import asyncio
from fastapi import FastAPI, Request
from pydantic import BaseModel
from orchestrator_agent import get_orchestrator_agent, build_orchestrator_workflow

app = FastAPI()

# Conversation state storage (in-memory for demo)
# Keyed by session_id or user_id in real use
conversation_context = {}

class UserMessage(BaseModel):
    session_id: str  # to identify multi-turn session
    message: str

@app.on_event("startup")
async def startup_event():
    global orchestrator_agent, workflow
    orchestrator_agent = get_orchestrator_agent()
    workflow = build_orchestrator_workflow(orchestrator_agent)

@app.post("/message")
async def message_endpoint(user_msg: UserMessage):
    session_id = user_msg.session_id
    message = user_msg.message.strip()

    # Retrieve or initialize context
    context = conversation_context.get(session_id, {
        "user_input": message,
        "provided_params": {},
        "all_params_collected": False,
        "step_index": 0,
        "template_name": None,
        "template_yaml": None,
        "parameters": None,
        "error": None,
        "response": None,
    })

    # Update user_input for first step (only on first turn)
    if context["step_index"] == 0:
        context["user_input"] = message

    # Run workflow steps until waiting for user input or done
    steps = workflow.steps
    while context["step_index"] < len(steps):
        step = steps[context["step_index"]]

        # For multi-turn step prompt_for_missing_params, if waiting for user input, break and wait
        if step.__name__ == "prompt_for_missing_params":
            # If all params collected or error, proceed to next step
            if context.get("all_params_collected", False) or context.get("error"):
                context["step_index"] += 1
                continue
            # We are expecting user input for param value in this step
            # If this is the first call, prompt user for missing param
            required = [p.strip() for p in context.get("parameters", "").split(",")]
            provided = context.get("provided_params", {})
            missing = [p for p in required if p not in provided]

            if missing:
                param_to_ask = missing[0]
                # If this message is user providing param value for this field, store it
                # We'll assume client sends param value after prompt
                # So on first call to this step, just send prompt back to user
                # On next calls, store the param value
                if "awaiting_param" not in context or context["awaiting_param"] != param_to_ask:
                    context["awaiting_param"] = param_to_ask
                    response = f"Please provide value for parameter '{param_to_ask}':"
                    context["response"] = response
                    # Save context and break to wait user input
                    conversation_context[session_id] = context
                    return {"response": response, "awaiting_param": param_to_ask}
                else:
                    # Store user provided value as param
                    provided[param_to_ask] = message
                    context["provided_params"] = provided
                    context["awaiting_param"] = None
                    # Check if more missing params
                    missing = [p for p in required if p not in provided]
                    if not missing:
                        context["all_params_collected"] = True
                    context["response"] = f"Received '{param_to_ask}': {message}"
                    conversation_context[session_id] = context
                    return {"response": context["response"], "awaiting_param": None}

        # Normal step execution
        await step(context)

        if context.get("error"):
            context["response"] = f"Error: {context['error']}"
            conversation_context[session_id] = context
            return {"response": context["response"]}

        context["step_index"] += 1

        # If response is ready in context and we're past param prompts, return it
        if step.__name__ == "present_parameters":
            conversation_context[session_id] = context
            return {"response": context["response"]}

    # Workflow finished
    conversation_context[session_id] = context
    return {"response": "All done!", "params_collected": context.get("provided_params", {})}
