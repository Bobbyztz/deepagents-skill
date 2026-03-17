# Human-in-the-Loop Patterns

> **📋 Prerequisites:**
>
> - `01_atomic/08_add_persistence.md`
> - `01_atomic/06_add_human_in_loop.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## ⚡ Quick Answer

```python
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver

def approval_node(state):
    # Pause for human
    response = interrupt({
        "question": "Approve this action?",
        "proposed_action": state["action"]
    })
    return {"approved": response == "yes"}

# Must have checkpointer!
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

# Start - pauses at interrupt
config = {"configurable": {"thread_id": "123"}}
result = graph.invoke(input, config)

# Resume with human response
result = graph.invoke(Command(resume="yes"), config)
```

---

## 📖 Three HIL Patterns

| Pattern      | Use Case              | Example             |
| ------------ | --------------------- | ------------------- |
| **Approval** | Gate critical actions | Delete confirmation |
| **Feedback** | Collect human input   | Review draft        |
| **Edit**     | Modify state directly | Fix agent mistake   |

---

## 🎯 Pattern 1: Approval Gate

```python
from langgraph.types import interrupt, Command
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal

class ApprovalState(TypedDict):
    action: str
    approved: bool | None
    result: str

def propose_action(state):
    return {"action": "Send email to all users"}

def get_approval(state):
    response = interrupt({
        "type": "approval",
        "message": f"Approve action: {state['action']}?",
        "options": ["approve", "reject"]
    })
    return {"approved": response == "approve"}

def route_by_approval(state) -> Literal["execute", "cancel"]:
    return "execute" if state["approved"] else "cancel"

def execute_action(state):
    return {"result": f"Executed: {state['action']}"}

def cancel_action(state):
    return {"result": "Action cancelled by user"}

builder = StateGraph(ApprovalState)
builder.add_node("propose", propose_action)
builder.add_node("approve", get_approval)
builder.add_node("execute", execute_action)
builder.add_node("cancel", cancel_action)

builder.add_edge(START, "propose")
builder.add_edge("propose", "approve")
builder.add_conditional_edges("approve", route_by_approval)
builder.add_edge("execute", END)
builder.add_edge("cancel", END)

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)
```

**Usage:**

```python
config = {"configurable": {"thread_id": "user-session"}}

# Start - pauses at approval
result = graph.invoke({"action": "", "approved": None, "result": ""}, config)
# Returns interrupt data

# Human decides...
result = graph.invoke(Command(resume="approve"), config)
print(result["result"])  # "Executed: Send email to all users"
```

---

## 🎯 Pattern 2: Feedback Collection

```python
def generate_draft(state):
    return {"draft": "Here is a draft report..."}

def get_feedback(state):
    feedback = interrupt({
        "type": "feedback",
        "message": "Please review this draft:",
        "draft": state["draft"],
        "prompt": "Enter your feedback or 'approve' to finalize"
    })

    if feedback.lower() == "approve":
        return {"feedback": None, "approved": True}
    return {"feedback": feedback, "approved": False}

def route_feedback(state) -> Literal["revise", "finalize"]:
    return "finalize" if state["approved"] else "revise"

def revise_draft(state):
    # Incorporate feedback
    return {"draft": f"{state['draft']}\n[Revised based on: {state['feedback']}]"}

def finalize(state):
    return {"final": state["draft"]}
```

**Flow:**

```
generate → get_feedback → [human] → revise → get_feedback → [human] → finalize
                             ↑______________________________|
```

---

## 🎯 Pattern 3: Direct State Edit

```python
# Get current state
config = {"configurable": {"thread_id": "123"}}
snapshot = graph.get_state(config)

# Human modifies state
graph.update_state(
    config,
    {"draft": "Human-edited version of the draft"},
    as_node="generate_draft"  # Pretend this came from the node
)

# Resume from the modified state
result = graph.invoke(None, config)
```

---

## 🔄 Multiple Interrupts

```python
def multi_step_approval(state):
    # First interrupt
    step1 = interrupt({"step": 1, "question": "First approval?"})
    if step1 != "approve":
        return {"status": "rejected_step1"}

    # Second interrupt
    step2 = interrupt({"step": 2, "question": "Second approval?"})
    if step2 != "approve":
        return {"status": "rejected_step2"}

    return {"status": "fully_approved"}
```

**Resume:**

```python
# First invoke - pauses at step1
result = graph.invoke(input, config)

# Resume step1
result = graph.invoke(Command(resume="approve"), config)
# Pauses at step2

# Resume step2
result = graph.invoke(Command(resume="approve"), config)
# Completes
```

---

## 🤝 With Deep Agents

```python
agent = create_deep_agent(
    model=model,
    tools=[dangerous_tool],
    system_prompt="...",
    interrupt_on={"tools": ["dangerous_tool"]},
    checkpointer=checkpointer
)

# Agent pauses when it tries to use dangerous_tool
config = {"configurable": {"thread_id": "123"}}
result = agent.invoke({"messages": [...]}, config)

# Review the proposed tool call, then resume
result = agent.invoke(Command(resume=True), config)
```

---

## ⚠️ Requirements

1. **Checkpointer is mandatory** for interrupt() to work
2. **Same thread_id** must be used for resume
3. **Command(resume=...)** to continue execution

---

## 🔗 Next Steps

**Add persistence:**
→ `01_atomic/08_add_persistence.md`

**Complex workflows:**
→ `../complex_topology/README.md`

---

## 💡 Key Takeaways

1. **interrupt()** pauses for human input
2. **Command(resume=...)** continues execution
3. **Checkpointer required** - no persistence, no HIL
4. Can have **multiple interrupts** in one node
