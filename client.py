import requests

HOST_AGENT_URL = "http://127.0.0.1:8000/message"
SESSION_ID = "test_session_1"

def main():
    print("Welcome to the Host Agent CLI client!")
    print("Type 'exit' to quit.")
    user_input = input("You: ")

    while user_input.lower() != "exit":
        payload = {
            "session_id": SESSION_ID,
            "message": user_input
        }
        resp = requests.post(HOST_AGENT_URL, json=payload)
        if resp.status_code != 200:
            print(f"Error: {resp.status_code} {resp.text}")
            break
        data = resp.json()
        print(f"HostAgent: {data.get('response')}")
        if data.get("awaiting_param"):
            # HostAgent is asking for param value, prompt user
            user_input = input(f"Provide value for '{data['awaiting_param']}': ")
        else:
            # Normal prompt for next user input
            user_input = input("You: ")

    print("Goodbye!")

if __name__ == "__main__":
    main()
