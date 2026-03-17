# LangGraph Quickstart: Your First Agent in 10 Minutes

> **📋 Prerequisites:** None - Start here for pure LangGraph!
>
> **LangGraph Version**: `>=0.2.0`

---

## ⚡ Quick Answer: Complete Calculator Agent

```python
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated
from typing import Literal
import operator

# 1. Setup model and tools
model = init_chat_model("anthropic:claude-sonnet-4-5-20250929", temperature=0)

@tool
def add(a: int, b: int) -> int:
    """Adds a and b."""
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """Multiply a and b."""
    return a * b

tools = [add, multiply]
tools_by_name = {t.name: t for t in tools}
model_with_tools = model.bind_tools(tools)

# 2. Define state
class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

# 3. Define nodes
def llm_call(state: MessagesState):
    """LLM decides whether to call a tool or not"""
    return {
        "messages": [
            model_with_tools.invoke(
                [SystemMessage(content="You are a helpful calculator assistant.")]
                + state["messages"]
            )
        ]
    }

def tool_node(state: MessagesState):
    """Execute tool calls"""
    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=str(observation), tool_call_id=tool_call["id"]))
    return {"messages": result}

# 4. Define routing
def should_continue(state: MessagesState) -> Literal["tool_node", "__end__"]:
    """Route based on whether LLM made tool calls"""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tool_node"
    return END

# 5. Build graph
builder = StateGraph(MessagesState)
builder.add_node("llm_call", llm_call)
builder.add_node("tool_node", tool_node)
builder.add_edge(START, "llm_call")
builder.add_conditional_edges("llm_call", should_continue, ["tool_node", END])
builder.add_edge("tool_node", "llm_call")

agent = builder.compile()

# 6. Run it!
result = agent.invoke({"messages": [HumanMessage(content="What is 3 + 4?")]})
for m in result["messages"]:
    m.pretty_print()
```

---

## 📖 Step-by-Step Explanation

### Step 1: Setup Model and Tools

```python
from langchain.tools import tool
from langchain.chat_models import init_chat_model

model = init_chat_model("anthropic:claude-sonnet-4-5-20250929", temperature=0)

@tool
def add(a: int, b: int) -> int:
    """Adds a and b."""
    return a + b

tools = [add]
model_with_tools = model.bind_tools(tools)
```

**Key Points:**

- Use `@tool` decorator to create LangChain tools
- `bind_tools()` lets the LLM know what tools are available
- Docstrings are **critical** - LLM uses them to understand tools

### Step 2: Define State

```python
from typing_extensions import TypedDict, Annotated
import operator

class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
```

**Key Points:**

- State is a `TypedDict` that flows through the graph
- `Annotated[..., operator.add]` is a **reducer** - new messages are appended, not replaced
- This is the standard pattern for chat-based agents

### Step 3: Define Nodes

```python
def llm_call(state: MessagesState):
    """LLM node - decides what to do"""
    return {"messages": [model_with_tools.invoke(state["messages"])]}

def tool_node(state: MessagesState):
    """Tool node - executes tools"""
    results = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        result = tool.invoke(tool_call["args"])
        results.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
    return {"messages": results}
```

**Key Points:**

- Nodes are Python functions that take state and return state updates
- Return a dict with keys to update (reducer handles merging)
- Tool calls are in `message.tool_calls`

### Step 4: Define Routing

```python
def should_continue(state: MessagesState) -> Literal["tool_node", "__end__"]:
    if state["messages"][-1].tool_calls:
        return "tool_node"
    return END  # "__end__"
```

**Key Points:**

- Conditional edges route based on state
- Return node name as string
- `END` (or `"__end__"`) terminates the graph

### Step 5: Build Graph

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(MessagesState)
builder.add_node("llm_call", llm_call)
builder.add_node("tool_node", tool_node)
builder.add_edge(START, "llm_call")
builder.add_conditional_edges("llm_call", should_continue)
builder.add_edge("tool_node", "llm_call")

agent = builder.compile()
```

**Graph Structure:**

```
START → llm_call → (tool needed?) → tool_node → llm_call (loop)
                 → (no tools)    → END
```

### Step 6: Run

```python
result = agent.invoke({"messages": [HumanMessage(content="What is 3 + 4?")]})
print(result["messages"][-1].content)  # "7" or "The answer is 7"
```

---

## 🔄 The Two LangGraph APIs

LangGraph offers two ways to build agents:

### Graph API (shown above)

- Declarative graph structure
- Explicit state management
- Visual representation
- Best for: Complex workflows, team collaboration

### Functional API

```python
from langgraph.func import entrypoint, task

@task
def call_llm(messages):
    return model_with_tools.invoke(messages)

@task
def call_tool(tool_call):
    tool = tools_by_name[tool_call["name"]]
    return tool.invoke(tool_call["args"])

@entrypoint()
def agent(messages):
    while True:
        response = call_llm(messages).result()
        if not response.tool_calls:
            return messages + [response]

        tool_results = [call_tool(tc).result() for tc in response.tool_calls]
        messages = messages + [response] + tool_results
```

**Best for:** Linear workflows, rapid prototyping, existing Python code

→ See `architecture_comparison.md` for detailed comparison

---

## 🛠️ Installation

```bash
pip install langgraph langchain langchain-anthropic
```

Or with uv:

```bash
uv add langgraph langchain langchain-anthropic
```

---

## 🎨 Common Patterns

### Pattern 1: Add Persistence

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
agent = builder.compile(checkpointer=checkpointer)

# Use thread_id to maintain conversation
config = {"configurable": {"thread_id": "user-123"}}
result = agent.invoke({"messages": [HumanMessage("Hi")]}, config)
result = agent.invoke({"messages": [HumanMessage("What did I just say?")]}, config)
```

### Pattern 2: Stream Output

```python
# Stream state updates
for chunk in agent.stream({"messages": [HumanMessage("Calculate 5 * 7")]}):
    print(chunk)

# Stream LLM tokens
for msg, metadata in agent.stream(input, stream_mode="messages"):
    print(msg.content, end="")
```

### Pattern 3: Parallel Execution

```python
# Fan-out: multiple edges from START
builder.add_edge(START, "research_a")
builder.add_edge(START, "research_b")

# Fan-in: multiple edges to same node
builder.add_edge("research_a", "summarize")
builder.add_edge("research_b", "summarize")
```

---

## 🔍 Visualize Your Graph

```python
from IPython.display import Image, display

display(Image(agent.get_graph().draw_mermaid_png()))
```

Or get Mermaid syntax:

```python
print(agent.get_graph().draw_mermaid())
```

---

## 🐛 Troubleshooting

### Graph doesn't terminate

- Check your conditional edges return `END` in some cases
- Add recursion limit: `agent.invoke(input, {"recursion_limit": 10})`

### Tool not being called

- Verify tool docstring is clear
- Check `bind_tools()` was called
- Print `message.tool_calls` to debug

### State not updating correctly

- Ensure you're using reducers (`Annotated[list, operator.add]`)
- Return dict with correct keys from nodes

---

## 🔗 Next Steps

**Compare with Deep Agents:**
→ `architecture_comparison.md`

**Learn about state management:**
→ `04_langgraph_integration/01_graph_api_guide.md`

**Add persistence:**
→ `01_atomic/08_add_persistence.md`

**Use Deep Agent as a node:**
→ `deep_agent_as_node.md` 【核心】

**See complete examples:**
→ `03_examples/langgraph_chatbot/`

---

## 💡 Key Takeaways

1. **LangGraph = State + Nodes + Edges**
2. **Reducers** control how state updates merge
3. **Conditional edges** enable dynamic routing
4. **Graph API** for complex flows, **Functional API** for linear flows
5. **Deep Agents can be nodes** in your LangGraph!
