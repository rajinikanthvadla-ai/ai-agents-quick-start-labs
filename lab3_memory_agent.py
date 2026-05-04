from bedrock_client import ask_bedrock


def format_memory(memory):
    return "\n".join(memory)


def main():
    memory = []

    print("Memory Agent started. Type 'exit' to stop.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        memory.append(f"User: {user_input}")

        prompt = f"""
Use the conversation memory to answer the latest user message.

Conversation memory:
{format_memory(memory)}

Latest user message:
{user_input}
"""

        ai_reply = ask_bedrock(
            prompt=prompt,
            system_prompt="You are a helpful AI agent with short-term memory.",
        )

        memory.append(f"Agent: {ai_reply}")

        print("\nAgent:", ai_reply)
        print("-" * 50)


if __name__ == "__main__":
    main()
