# Add Human-in-the-Loop

> **📋 Prerequisites:**
>
> - `01_create_orchestrator.md`
> - `08_add_persistence.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## ⚡ Quick Answer

### LangGraph: Using interrupt()

```python
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver

def approval_node(state):
    # Pause and ask human
    response = interrupt({"question": "Approve this action?", "data": state["proposed_action"]})

    if response == "approved":
        return {"status": "approved"}
    else:
        return {"status": "rejected"}

builder = StateGraph(State)
builder.add_node("propose", propose_node)
builder.add_node("approve", approval_node)
builder.add_node("execute", execute_node)
# ...

checkpointer = MemorySaver()  # Required!
graph = builder.compile(checkpointer=checkpointer)

# First run - pauses at interrupt
config = {"configurable": {"thread_id": "user-123"}}
result = graph.invoke(input, config)

# Resume with human response
result = graph.invoke(Command(resume="approved"), config)
```

---

## 📖 Why Human-in-the-Loop?

- ✅ **Approval workflows**: Human approves before execution
- ✅ **Feedback collection**: Get human input mid-process
- ✅ **Error correction**: Human fixes mistakes
- ✅ **Safety**: Critical actions require approval

---

## 🎯 LangGraph interrupt() Pattern

### Step 1: Add Persistence

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()  # Required for interrupt()
graph = builder.compile(checkpointer=checkpointer)
```

### Step 2: Use interrupt() in Node

```python
from langgraph.types import interrupt

def human_review_node(state):
    # Pause execution and send data to human
    human_response = interrupt({
        "type": "approval_request",
        "message": "Please review the following action:",
        "data": state["proposed_action"]
    })

    # Execution resumes here after human responds
    return {"human_feedback": human_response}
```

### Step 3: Resume with Command

```python
from langgraph.types import Command

# First invocation - pauses at interrupt
config = {"configurable": {"thread_id": "user-123"}}
result = graph.invoke({"input": "do something"}, config)

# result contains the interrupt data
# Human reviews...

# Resume with human's response
result = graph.invoke(Command(resume="approved"), config)
```

---

## 🔄 Complete Example

```python
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Literal

class State(TypedDict):
    task: str
    plan: str
    approved: bool
    result: str

def create_plan(state):
    # Agent creates a plan
    return {"plan": f"Plan for: {state['task']}"}

def get_approval(state):
    # Pause for human approval
    response = interrupt({
        "message": "Please approve this plan:",
        "plan": state["plan"]
    })
    return {"approved": response == "approved"}

def execute_or_revise(state) -> Literal["execute", "revise"]:
    if state["approved"]:
        return "execute"
    return "revise"

def execute_plan(state):
    return {"result": f"Executed: {state['plan']}"}

def revise_plan(state):
    return {"plan": f"Revised: {state['plan']}"}

# Build graph
builder = StateGraph(State)
builder.add_node("plan", create_plan)
builder.add_node("approve", get_approval)
builder.add_node("execute", execute_plan)
builder.add_node("revise", revise_plan)

builder.add_edge(START, "plan")
builder.add_edge("plan", "approve")
builder.add_conditional_edges("approve", execute_or_revise)
builder.add_edge("execute", END)
builder.add_edge("revise", "plan")  # Loop back

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

# Usage
config = {"configurable": {"thread_id": "task-1"}}

# Start - will pause at approval
result = graph.invoke({"task": "Write report"}, config)
print("Waiting for approval:", result)

# Human approves
result = graph.invoke(Command(resume="approved"), config)
print("Final result:", result)
```

---

## 🤝 With Deep Agents

Deep Agents can use interrupt_on configuration:

```python
agent = create_deep_agent(
    model=model,
    tools=[dangerous_tool],
    system_prompt="...",
    interrupt_on={"tools": ["dangerous_tool"]},  # Pause before this tool
    checkpointer=checkpointer
)
```

---

## 🐛 Troubleshooting

### interrupt() not working

1. **Add checkpointer**: Required for persistence
2. **Use thread_id**: Required for state retrieval
3. **Use Command(resume=...)**: Proper way to resume

### State lost after interrupt

- Ensure same `thread_id` is used for resume
- Check checkpointer is properly configured

---

## 🔗 Next Steps

**Learn interrupt patterns:**
→ `02_patterns/human_in_loop/README.md`

**Add persistence:**
→ `08_add_persistence.md`

---

## 💡 Key Takeaways

1. **interrupt()** pauses graph execution
2. **Checkpointer required** for state persistence
3. **Command(resume=...)** to continue
4. Great for **approval workflows** and **feedback collection**
