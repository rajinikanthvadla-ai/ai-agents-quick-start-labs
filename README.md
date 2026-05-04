# Quick Start AI Agent Labs with AWS Bedrock

Beginner-friendly Python labs for learning how real AI agents work using Amazon Bedrock.

Main idea:

```text
Normal AI app = Answer only
AI Agent = Think + Use Tool + Take Action + Verify
```

## Lab Flow

Run the labs in this order:

1. `lab1_simple_chat.py` - Simple LLM chatbot
2. `lab2_tool_agent.py` - Agent with calculator tool
3. `lab3_memory_agent.py` - Agent with short-term memory
4. `lab4_log_rca_agent.py` - Agent that reads logs and gives RCA
5. `lab5_devops_agent.py` - Mini DevOps incident agent
6. `lab6_langgraph_workflow_agent.py` - LangGraph workflow agent

## What This Project Uses

This project does not use Google Gemini API.

It uses:

- AWS Bedrock for LLM responses
- `boto3` for calling Bedrock from Python
- `python-dotenv` for local environment values
- `langgraph` for the workflow agent in Lab 6

## Setup

Create and activate a virtual environment:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

Install packages:

```bash
pip install -r requirements.txt
```

Create your `.env` file:

```bash
copy .env.example .env
```

Update `.env` if needed:

```text
AWS_REGION=us-east-1
AWS_PROFILE=default
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
ALLOW_CLUSTER_CREATE=false
KIND_CLUSTER_NAME=ai-agent-lab
```

Before running the labs, make sure:

- AWS CLI is configured with valid credentials.
- Your AWS user or role has permission to call Amazon Bedrock.
- The selected Bedrock model is enabled in your AWS account and region.

Example AWS CLI setup:

```bash
aws configure
```

## Lab 1: Simple AI Chatbot

Run:

```bash
python lab1_simple_chat.py
```

Example input:

```text
Explain Docker in simple words.
```

What happens:

- User enters a question.
- Python sends the question to AWS Bedrock.
- Bedrock returns an answer.

This is a normal AI app. It answers, but it does not use tools or take action.

## Lab 2: Agent with Tool Calling

Run:

```bash
python lab2_tool_agent.py
```

Example inputs:

```text
calculate 25 * 40
check docker
docker ps
docker images
check kubectl
kubectl get nodes
create kind cluster
```

What happens:

- The script checks the user request.
- It selects one matching tool from the tool registry.
- It runs the selected Python function.
- The Python function may call a local command like `docker` or `kubectl`.
- It sends the tool output to Bedrock.
- Bedrock explains what happened and what to do next.

Available tools:

```text
calculator             Simple arithmetic
docker_status          Checks if Docker engine is running
docker_containers      Lists running Docker containers
docker_images          Lists local Docker images
kubectl_client         Checks kubectl client installation
kubernetes_nodes       Lists Kubernetes cluster nodes
kind_cluster_create    Creates a local Kubernetes cluster using Kind
```

This is the first agent step: the AI does not only answer, it selects a tool, runs it, reads the result, and explains the next step.

Important:

`create kind cluster` is dry-run by default. To allow real cluster creation, install Docker and Kind, then set this in `.env`:

```text
ALLOW_CLUSTER_CREATE=true
KIND_CLUSTER_NAME=ai-agent-lab
```

Then run:

```bash
python lab2_tool_agent.py
```

And ask:

```text
create kind cluster
```

## Lab 3: Agent with Memory

Run:

```bash
python lab3_memory_agent.py
```

Example conversation:

```text
You: My name is Rajini.
You: I teach DevOps.
You: What do I teach?
```

What happens:

- The script stores conversation history in a Python list.
- Each new question is sent with previous context.
- Bedrock answers using that memory.

This is short-term memory. It works only while the program is running.

## Lab 4: Log RCA Agent

Run:

```bash
python lab4_log_rca_agent.py
```

What happens:

- The agent reads `app.log`.
- It sends the logs to Bedrock.
- Bedrock creates a root cause analysis.

The sample logs show database latency, payment-service timeout, and checkout failures.

This is a simple AIOps agent.

## Lab 5: Mini DevOps Agent

Run:

```bash
python lab5_devops_agent.py
```

What happens:

- The agent reads `service_status.txt`.
- The agent reads `app.log`.
- The agent reads `deployment_info.txt`.
- Bedrock combines all inputs and recommends action.

This is closer to a real incident assistant because it combines health, logs, and deployment context.

## Lab 6: LangGraph Workflow Agent

Run:

```bash
python lab6_langgraph_workflow_agent.py
```

What happens:

```text
Issue
  -> Analyze Issue
  -> Recommend Action
  -> Verify Action
```

LangGraph makes the agent flow controlled and easy to understand.

Each node has one job:

- `analyze_issue` understands the problem.
- `recommend_action` gives the next action.
- `verify_action` explains how to confirm recovery.

## Simple Architecture

```text
User Goal
   |
Agent Brain / Bedrock LLM
   |
Tools + Memory + Files
   |
Action / Recommendation
   |
Verification
```

## Files

```text
bedrock_client.py                  Shared AWS Bedrock helper
lab1_simple_chat.py                Basic chatbot
lab2_tool_agent.py                 Tool-calling agent
lab3_memory_agent.py               Memory agent
lab4_log_rca_agent.py              Log RCA agent
lab5_devops_agent.py               Mini DevOps agent
lab6_langgraph_workflow_agent.py   LangGraph workflow agent
app.log                            Sample application logs
service_status.txt                 Sample service health data
deployment_info.txt                Sample deployment data
```