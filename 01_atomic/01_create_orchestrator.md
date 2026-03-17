# Create Orchestrator (Main Agent)

> **📋 Prerequisites:** Read `00_quickstart/minimal_example.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## ⚡ Quick Answer

```python
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model

model = init_chat_model("anthropic:claude-sonnet-4-5-20250929")

agent = create_deep_agent(
    model=model,
    system_prompt="You are a helpful assistant."
)
```

**That's it!** You now have an orchestrator with built-in capabilities.

---

## 📖 What is an Orchestrator?

The **orchestrator** (also called "main agent") is the **top-level coordinator**. It:

- ✅ Plans high-level strategy
- ✅ Delegates tasks to tools or sub-agents
- ✅ Synthesizes results
- ❌ Doesn't directly execute complex tasks (delegates instead)

**Analogy**: A project manager who assigns work to specialists.

---

## 🎯 Step-by-Step Guide

### Step 1: Import Dependencies

```python
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
```

### Step 2: Choose a Model

```python
# Option 1: Anthropic Claude (recommended for complex reasoning)
model = init_chat_model(
    "anthropic:claude-sonnet-4-5-20250929",
    temperature=0.0  # Deterministic
)

# Option 2: OpenAI GPT-4
model = init_chat_model("openai:gpt-4o")

# Option 3: Google Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
model = ChatGoogleGenerativeAI(
    model="gemini-3-pro-preview",
    temperature=0.0
)
```

**Why temperature=0.0?**

- Makes output deterministic (same input → same output)
- Important for testing and production
- Deep Research uses 0.0

### Step 3: Write System Prompt

The system prompt defines the orchestrator's **role and workflow**.

**Example 1: Simple Assistant**

```python
system_prompt = "You are a helpful research assistant."
```

**Example 2: Structured Workflow** (like Deep Research)

```python
system_prompt = """# Your Role

You are a research orchestrator.

## Workflow
1. Plan: Break down the task using write_todos
2. Execute: Use tools or delegate to sub-agents
3. Synthesize: Combine results
4. Verify: Check completeness

## Key Rules
- Always plan before executing
- Delegate complex tasks to sub-agents
- Save important results to files
"""
```

### Step 4: Create the Orchestrator

```python
agent = create_deep_agent(
    model=model,
    tools=[],  # Empty for now (added in next skill)
    system_prompt=system_prompt
)
```

### Step 5: Run It

```python
result = agent.invoke({
    "messages": [{"role": "user", "content": "Hello!"}]
})

print(result["messages"][-1].content)
```

---

## 🧩 What Happens Under the Hood?

When you call `create_deep_agent()`, it:

### 1. Creates Middleware Stack

```python
middleware = [
    TodoListMiddleware(),           # Provides write_todos
    FilesystemMiddleware(),         # Provides ls, read_file, write_file, etc.
    SubAgentMiddleware(),           # Provides task (if subagents configured)
    SummarizationMiddleware(),      # Auto-compresses long history
]
```

### 2. Returns a Compiled LangGraph

**Important**: `create_deep_agent()` returns a `CompiledStateGraph` - this means:

- It's a standard LangGraph Runnable
- It can be used as a node in another LangGraph! (See `11_use_deep_agent_as_node.md`)

---

## 🎨 Configuration Options

### Full Signature

```python
agent = create_deep_agent(
    model,                     # Required: LangChain chat model
    tools=[],                  # Optional: Your custom tools
    system_prompt="",          # Optional: Your instructions
    subagents=[],              # Optional: Sub-agent configs
    backend=None,              # Optional: File system backend
    store=None,                # Optional: Long-term memory store
    interrupt_on={},           # Optional: Human-in-the-loop config
    checkpointer=None,         # Optional: State persistence
    middleware=[]              # Optional: Additional middleware
)
```

---

## 🔗 Next Steps

**Add custom tools:**
→ `01_atomic/02_add_tool.md`

**Configure sub-agents:**
→ `01_atomic/03_configure_subagent.md`

**Use as LangGraph node:**
→ `01_atomic/11_use_deep_agent_as_node.md`

---

## 💡 Key Takeaways

1. **Orchestrator = Coordinator**, not executor
2. **System prompt defines workflow** - be explicit
3. **Built-in capabilities** (planning, files, sub-agents) work automatically
4. **Returns CompiledStateGraph** - can be used as LangGraph node
