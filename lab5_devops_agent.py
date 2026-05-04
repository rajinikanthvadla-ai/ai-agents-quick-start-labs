from pathlib import Path

from bedrock_client import ask_bedrock


def read_service_status():
    return Path("service_status.txt").read_text(encoding="utf-8")


def read_logs():
    return Path("app.log").read_text(encoding="utf-8")


def read_deployment_info():
    return Path("deployment_info.txt").read_text(encoding="utf-8")


def main():
    service_status = read_service_status()
    logs = read_logs()
    deployment_info = read_deployment_info()

    prompt = f"""
You are a Mini DevOps AI Agent.

The agent used three tools:
- read_service_status()
- read_logs()
- read_deployment_info()

Service status:
{service_status}

Application logs:
{logs}

Deployment information:
{deployment_info}

Analyze the incident and return:
1. Current service health
2. Is this CPU, application, database, or deployment issue?
3. Most probable root cause
4. Immediate action for the on-call engineer
5. Long-term fix
6. Slack incident update message

Keep the answer practical and production-style.
"""

    response = ask_bedrock(
        prompt=prompt,
        system_prompt="You are a senior DevOps agent helping during a production incident.",
        max_tokens=1000,
    )

    print(response)


if __name__ == "__main__":
    main()
