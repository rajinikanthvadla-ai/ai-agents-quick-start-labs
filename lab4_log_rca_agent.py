from pathlib import Path

from bedrock_client import ask_bedrock


def read_logs():
    return Path("app.log").read_text(encoding="utf-8")


def main():
    logs = read_logs()

    prompt = f"""
You are an AIOps root cause analysis agent.

Read the production logs and produce a practical RCA.

Return:
1. What happened
2. Probable root cause
3. Business impact
4. Immediate fix
5. Simple explanation for a junior engineer

Logs:
{logs}
"""

    response = ask_bedrock(
        prompt=prompt,
        system_prompt="You are a practical DevOps incident analysis agent.",
        max_tokens=900,
    )

    print(response)


if __name__ == "__main__":
    main()
