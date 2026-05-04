import ast
import os
import operator
import re
import subprocess

from bedrock_client import ask_bedrock

ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def run_command(command, timeout=30):
    """Run a local DevOps command and return output for the agent."""
    print(f"\nRunning local command: {' '.join(command)}")

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return f"Command not found: {command[0]}"
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout} seconds: {' '.join(command)}"

    output = completed.stdout.strip()
    error = completed.stderr.strip()

    if completed.returncode != 0:
        return f"Command failed: {' '.join(command)}\nError:\n{error}"

    return output or "Command completed successfully with no output."


def safe_calculator(expression):
    """Calculator tool for simple arithmetic expressions."""
    node = ast.parse(expression, mode="eval").body
    return str(_evaluate_math_node(node))


def _evaluate_math_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPERATORS:
        left = _evaluate_math_node(node.left)
        right = _evaluate_math_node(node.right)
        return ALLOWED_OPERATORS[type(node.op)](left, right)

    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPERATORS:
        value = _evaluate_math_node(node.operand)
        return ALLOWED_OPERATORS[type(node.op)](value)

    raise ValueError("Only simple arithmetic is supported.")


def extract_expression(user_input):
    cleaned = user_input.lower().replace("calculate", "").strip()
    match = re.search(r"[-+*/().\d\s]+", cleaned)
    return match.group(0).strip() if match else ""


def check_docker_status(_user_input):
    return run_command(["docker", "info", "--format", "Docker server version: {{.ServerVersion}}"])


def list_docker_containers(_user_input):
    return run_command(["docker", "ps", "--format", "name={{.Names}} status={{.Status}} image={{.Image}}"])


def list_docker_images(_user_input):
    return run_command(["docker", "images", "--format", "repository={{.Repository}} tag={{.Tag}} size={{.Size}}"])


def check_kubectl_client(_user_input):
    return run_command(["kubectl", "version", "--client=true"])


def get_kubernetes_nodes(_user_input):
    return run_command(["kubectl", "get", "nodes", "-o", "wide"])


def create_kind_cluster(_user_input):
    cluster_name = os.getenv("KIND_CLUSTER_NAME", "ai-agent-lab")

    if os.getenv("ALLOW_CLUSTER_CREATE", "false").lower() != "true":
        return f"""
Dry run only. Cluster was not created.

To allow real cluster creation, add this to .env:
ALLOW_CLUSTER_CREATE=true
KIND_CLUSTER_NAME={cluster_name}

Then ask again: create kind cluster

Real command that will run:
kind create cluster --name {cluster_name} --wait 120s
"""

    return run_command(
        ["kind", "create", "cluster", "--name", cluster_name, "--wait", "120s"],
        timeout=180,
    )


def calculate(user_input):
    expression = extract_expression(user_input)
    if not expression:
        return "No arithmetic expression found."

    return safe_calculator(expression)


TOOLS = {
    "calculator": {
        "description": "Use for arithmetic questions like calculate 25 * 40.",
        "function": calculate,
        "keywords": ["calculate", "+", "-", "*", "/"],
    },
    "docker_status": {
        "description": "Use to check if Docker engine is running.",
        "function": check_docker_status,
        "keywords": ["docker", "docker status", "docker running", "check docker", "run docker"],
    },
    "docker_containers": {
        "description": "Use to list running Docker containers.",
        "function": list_docker_containers,
        "keywords": ["docker ps", "list containers", "running containers"],
    },
    "docker_images": {
        "description": "Use to list local Docker images.",
        "function": list_docker_images,
        "keywords": ["docker images", "list images", "check images", "show images", "images docker"],
    },
    "kubectl_client": {
        "description": "Use to check kubectl installation.",
        "function": check_kubectl_client,
        "keywords": ["kubectl", "kubectl version", "check kubectl", "kubectl client", "run kubectl"],
    },
    "kubernetes_nodes": {
        "description": "Use to list Kubernetes cluster nodes.",
        "function": get_kubernetes_nodes,
        "keywords": ["kubectl get nodes", "kubernetes nodes", "cluster nodes"],
    },
    "kind_cluster_create": {
        "description": "Use to create a local Kubernetes cluster with Kind.",
        "function": create_kind_cluster,
        "keywords": ["kind cluster", "create kind cluster", "create kubernetes cluster", "create cluster"],
    },
}


def choose_tool(user_input):
    text = user_input.lower()
    matches = []

    for tool_name, tool_config in TOOLS.items():
        for keyword in tool_config["keywords"]:
            if keyword in text:
                matches.append((len(keyword), tool_name, tool_config))

    if not matches:
        return None, None

    _keyword_length, tool_name, tool_config = max(matches, key=lambda item: item[0])
    return tool_name, tool_config


def build_tool_prompt(user_input, tool_name, tool_description, tool_result):
    return f"""
The user asked:
{user_input}

The agent selected this tool:
{tool_name}

Why this tool was selected:
{tool_description}

Tool output:
{tool_result}

Explain:
1. What the agent understood
2. Which tool it used
3. What the tool result means
4. What the user should do next

Keep it simple for students.
"""


def main():
    user_input = input("Ask agent: ")

    tool_name, tool_config = choose_tool(user_input)

    if tool_config:
        print(f"\nTool selected: {tool_name}")
        tool_result = tool_config["function"](user_input)
        print("\nTool output:")
        print(tool_result)

        final_prompt = build_tool_prompt(
            user_input=user_input,
            tool_name=tool_name,
            tool_description=tool_config["description"],
            tool_result=tool_result,
        )
    else:
        final_prompt = f"""
The user asked:
{user_input}

No local tool was needed. Answer normally in simple words.
"""

    response = ask_bedrock(
        prompt=final_prompt,
        system_prompt="You are a beginner-friendly AI agent.",
    )

    print("\nAgent Response:")
    print(response)


if __name__ == "__main__":
    main()
