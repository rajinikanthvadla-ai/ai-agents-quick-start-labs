from bedrock_client import ask_bedrock


def main():
    user_question = input("Ask something: ")

    response = ask_bedrock(
        prompt=user_question,
        system_prompt="You are a helpful AI assistant. Explain clearly for beginners.",
    )

    print("\nAI Response:")
    print(response)


if __name__ == "__main__":
    main()
