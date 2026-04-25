# Autonomous AI Task Execution Agent (AATEA) - Project Overview

This is a living document that tracks the core concepts, architecture, and progress of the AATEA project. It is designed to help you understand the workflow and serve as a foundation for your hackathon presentation.

## 🎯 The Problem We Are Solving

Knowledge workers spend roughly 40% of their time on repetitive, multi-step digital tasks (e.g., pulling data from one system, transforming it, and pushing it to another). 

Current AI solutions (like ChatGPT) are just chatbots — they can *tell* you how to do a task, but they cannot *execute* it autonomously. They lack the ability to orchestrate tools, handle failures, and string together complex workflows without constant human hand-holding. 

**The Execution Gap:** Users are still forced to copy-paste outputs between tools manually. AATEA closes this gap.

## 🚀 The Solution: AATEA Workflow

AATEA is not a chatbot; it is a **runtime execution engine**. Here is how the workflow operates:

1. **Natural Language Input:** The user types a plain-English request (e.g., *"Fetch the latest GitHub issues and send a summary to Slack"*).
2. **Intent Parsing:** A specialized AI model (`gemini-2.5-flash`) parses the unstructured text into a highly structured JSON intent, ensuring the goal is clear.
3. **DAG Planning:** A reasoning model (`gemini-2.5-flash`/`pro`) breaks the goal down into atomic steps, creating a Directed Acyclic Graph (DAG). This defines which steps can run in parallel and which depend on the outputs of previous steps.
4. **Execution Engine:** The Python-based asynchronous executor dynamically routes the steps to registered Tool Adapters, managing the flow of data between them.
5. **Real-time Observability:** Every step is logged and auditable, bringing full transparency to AI actions.

## 💻 Tech Stack

- **Backend Logic & Orchestration:** Python, FastAPI, Asyncio, NetworkX (for DAG resolution)
- **AI / LLM Integration:** Google Gemini API (using the modern `google-genai` SDK)
## 🎭 The "Undeniable Proof" Demo Strategy

To guarantee the judges are blown away and know this isn't just a mock interface, use this specific demonstration strategy:

**1. The Real-World Output (Webhook.site)**
Judges need to see the AI actually send data across the internet. 
- Go to [webhook.site](https://webhook.site/) (it instantly generates a free, temporary URL that listens for data).
- Copy "Your unique URL".
- Open your `backend/.env` file and paste that URL as your `SLACK_WEBHOOK_URL=https://webhook.site/...`
- Keep the webhook.site tab open on half your screen, and the AATEA frontend on the other half.

**2. The Prompt**
Type: *"Fetch the 5 latest issues from the facebook/react github repo, summarize them, and send them to slack"*

**3. The "Wow" Moment**
- **Action:** Click "Approve & Execute"
- **See:** The UI will stream live logs fetching real issues from GitHub. 
- **Verify:** The raw output in the UI will beautifully display the actual open issues from the React repository.
- **The Kicker:** On the other half of the screen, the judges will see the summary magically pop up live on the `webhook.site` dashboard. Undeniable proof that your AI agent reached out, grabbed data, and autonomously pushed it to a third-party service!

## 🌐 Deployment Strategy (Zero-Friction for Judges)

We have optimized the project so judges can run it without needing pendrives, cloning repos, or installing python packages.

**Option 1: Live Cloud Deployment (Recommended)**
- **Frontend (Vite/React):** Deployed on Vercel with a single click from the GitHub repository.
- **Backend (FastAPI):** Deployed on Render.com as a Web Service. The `GEMINI_API_KEY` and `SLACK_WEBHOOK_URL` are set as environment variables in the Render dashboard.

**Option 2: 1-Click Local Execution (Docker)**
If judges want to run the code locally, they don't need to install Python or Node.js. We have included a `docker-compose.yml` file. They simply run:
```bash
docker-compose up --build
```
And the entire stack (Frontend + Backend) boots up on `http://localhost:5173`.

## 📊 MVP Scope Completion

Every feature required for the MVP has been successfully implemented!

| Feature | Status | Description |
| :--- | :--- | :--- |
| **NL Task Parsing** | ✅ Done | Translates English to structured JSON intent. |
| **DAG Generation** | ✅ Done | AI successfully builds multi-step execution graphs. |
| **Execution Engine** | ✅ Done | Asynchronous routing of steps based on dependencies. |
| **Premium Web UI** | ✅ Done | Glassmorphism React interface for task submission. |
| **Real Tool Adapters** | ✅ Done | Zero-config GitHub (public APIs) & Slack Webhook adapters built. |
| **Plan Review Screen** | ✅ Done | UI pauses for human-in-the-loop approval before executing. |
| **WebSocket Streaming**| ✅ Done | Premium animated terminal streams logs in real-time. |
| **Retry Logic** | ✅ Done | Built-in exponential backoff (Tenacity) for failed API calls. |

> [!NOTE]
> **Living Document**
> I will update this document automatically whenever we add new features or change the architecture.
