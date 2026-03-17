# Minimal Example: Your First Deep Agent in 15 Lines

> **📋 Prerequisites:**
>
> - Read `what_is_deep_agents.md`
> - Have API keys for Anthropic (or OpenAI/Google)
>
> **LangGraph Version**: `>=0.2.0`

---

## ⚡ The Complete Code

```python
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model

# 1. Choose a model
model = init_chat_model("anthropic:claude-sonnet-4-5-20250929")

# 2. Create the agent
agent = create_deep_agent(
    model=model,
    system_prompt="You are a helpful research assistant."
)

# 3. Run it
result = agent.invoke({
    "messages": [{"role": "user", "content": "What is LangGraph?"}]
})

# 4. See the response
print(result["messages"][-1].content)
```

**That's it!** 15 lines, and you have an agent with:

- ✅ Planning (write_todos)
- ✅ File system (ls, read_file, write_file, edit_file)
- ✅ Sub-agent spawning (task)

---

## 🔬 What Happens Under the Hood?

When you run the code above, here's what automatically happens:

### Step 1: Model Receives Enhanced System Prompt

Your prompt (`"You are a helpful research assistant."`) is **augmented** by middleware:

```
Your prompt: "You are a helpful research assistant."

+

Middleware instructions:
  - TodoListMiddleware: "You have access to write_todos tool for planning..."
  - FilesystemMiddleware: "You can use ls, read_file, write_file..."
  - SubAgentMiddleware: "You can delegate tasks using the task() tool..."
```

### Step 2: Agent Gets Built-in Tools

Without you providing any tools, the agent has:

| Tool                                                         | From                 | Purpose            |
| ------------------------------------------------------------ | -------------------- | ------------------ |
| `write_todos`                                                | TodoListMiddleware   | Create task plans  |
| `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep` | FilesystemMiddleware | Context management |
| `task`                                                       | SubAgentMiddleware   | Spawn sub-agents   |

### Step 3: Agent Plans and Acts

For the query "What is LangGraph?", the agent might:

1. **Plan** (optional):

   ```python
   write_todos([
       {"task": "Search for LangGraph information", "status": "in_progress"},
       {"task": "Synthesize findings", "status": "pending"}
   ])
   ```

2. **No tools needed** for this simple question, so it responds directly

3. **Return**: Explanation of LangGraph

---

## 🛠️ Installation

### Option 1: pip

```bash
pip install deepagents langgraph>=0.2.0
```

### Option 2: uv (recommended for projects)

```bash
uv add deepagents "langgraph>=0.2.0"
```

### Option 3: poetry

```bash
poetry add deepagents "langgraph>=0.2.0"
```

---

## 🔑 Setting Up API Keys

### For Anthropic (Claude):

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### For OpenAI (GPT):

```bash
export OPENAI_API_KEY="sk-..."
```

### For Google (Gemini):

```bash
export GOOGLE_API_KEY="..."
```

---

## 🎨 Variations

### Variation 1: Different Model

```python
# Use GPT-4
model = init_chat_model("openai:gpt-4o")

# Use Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
model = ChatGoogleGenerativeAI(model="gemini-3-pro-preview")
```

### Variation 2: Add Custom Tools

```python
from langchain_core.tools import tool

@tool
def calculator(expression: str) -> str:
    """Evaluate a math expression"""
    return str(eval(expression))

agent = create_deep_agent(
    model=model,
    tools=[calculator],  # Your tool + built-in tools
    system_prompt="You are a math tutor."
)
```

### Variation 3: Disable Temperature for Determinism

```python
model = init_chat_model(
    "anthropic:claude-sonnet-4-5-20250929",
    temperature=0.0  # Fully deterministic
)
```

---

## 📂 File System Demo

Let's see the file system in action:

```python
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Research quantum computing and save your findings to /research.md"
    }]
})

# Check what files were created
files = result["files"]
print(files.keys())  # ['/research.md']

# Read the file content
print(files["/research.md"])
```

The agent will:

1. Research quantum computing (using your tools or knowledge)
2. Call `write_file("/research.md", content)`
3. File is stored in LangGraph state
4. Accessible via `result["files"]`

---

## 🔍 Inspecting the Result

The `invoke()` returns a dictionary with:

```python
{
    "messages": [
        {"role": "user", "content": "..."},
        AIMessage(...),  # Agent's thoughts
        ToolMessage(...),  # Tool results
        AIMessage(content="Final response")  # Last message
    ],
    "files": {
        "/research.md": "content...",
        # Other files created
    },
    "todos": [
        {"task": "...", "status": "completed"}
    ]
}
```

**Get the final response:**

```python
final_answer = result["messages"][-1].content
```

**Get files:**

```python
research_content = result["files"].get("/research.md", "")
```

---

## 🐛 Troubleshooting

### Error: "No API key found"

```bash
# Make sure you exported your key
export ANTHROPIC_API_KEY="..."

# Or set in code (not recommended for production)
import os
os.environ["ANTHROPIC_API_KEY"] = "..."
```

### Error: "Model not found"

```python
# Check the model string format:
"provider:model-name"

# Examples:
"anthropic:claude-sonnet-4-5-20250929"  ✅
"openai:gpt-4o"  ✅
"gpt-4o"  ❌ (missing provider)
```

### Agent doesn't use tools

- Normal for simple questions—agents only use tools when needed
- Try a task that requires tools: "Research X and write a report"

---

## 🔗 Next Steps

**Add custom tools:**
→ `01_atomic/02_add_tool.md`

**Configure sub-agents:**
→ `01_atomic/03_configure_subagent.md`

**Use project templates:**
→ `00_quickstart/templates/basic_agent/` or `research_agent/`

**Understand how it works:**
→ `01_atomic/01_create_orchestrator.md`

**Learn hybrid architecture:**
→ `deep_agent_as_node.md` - Deep Agent 作为 LangGraph 节点

**Compare with pure LangGraph:**
→ `langgraph_quickstart.md`

---

## 💡 Key Takeaway

With just `create_deep_agent()`, you get a **fully-featured agent** without manual setup of:

- Planning logic
- File system abstraction
- Sub-agent infrastructure
- Context management

This lets you focus on **what your agent should do**, not **how to build agent infrastructure**.
