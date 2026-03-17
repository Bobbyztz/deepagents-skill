# Enable Planning (TODO Lists)

> **📋 Prerequisites:** `01_create_orchestrator.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## ⚡ Quick Answer

Planning is **enabled by default** in Deep Agents!

```python
agent = create_deep_agent(model=model, system_prompt="...")

# Agent automatically has write_todos tool
```

To encourage planning, add to system prompt:

```python
system_prompt = """
## Workflow
1. First, create a plan using write_todos
2. Execute each step
3. Update TODO status as you progress
"""
```

---

## 📖 The write_todos Tool

### Basic Usage

Agent calls:

```python
write_todos([
    {"task": "Research topic A", "status": "in_progress"},
    {"task": "Research topic B", "status": "pending"},
    {"task": "Write summary", "status": "pending"}
])
```

### Status Values

- `pending` - Not started
- `in_progress` - Currently working on
- `completed` - Done
- `blocked` - Waiting on something

### Updating Status

```python
# Later in the workflow:
write_todos([
    {"task": "Research topic A", "status": "completed"},
    {"task": "Research topic B", "status": "in_progress"},
    {"task": "Write summary", "status": "pending"}
])
```

---

## 🎯 Prompting for Planning

### Minimal

```python
system_prompt = "Always create a plan with write_todos before starting complex tasks."
```

### Structured

```python
system_prompt = """# Research Assistant

## Workflow

1. **Plan** (REQUIRED)
   - Use write_todos to break down the task
   - Each TODO should be specific and actionable

2. **Execute**
   - Work through TODOs in order
   - Update status as you progress

3. **Verify**
   - Review completed TODOs
   - Ensure all requirements are met
"""
```

### With Limits

```python
system_prompt = """
## Planning Rules
- Create 3-5 TODOs per task
- Each TODO should take 1-2 tool calls
- Don't over-plan simple tasks
"""
```

---

## 📊 Accessing TODOs

```python
result = agent.invoke({"messages": [...]})

# Access TODO list
todos = result.get("todos", [])
for todo in todos:
    print(f"[{todo['status']}] {todo['task']}")
```

---

## 🔄 Planning Pattern in Deep Research

```python
INSTRUCTIONS = """
1. **Plan**: Create TODO list with write_todos
   - Break query into research topics
   - Include synthesis step

2. **Execute**: Work through each TODO
   - Delegate research to sub-agents
   - Update status after each step

3. **Synthesize**: Combine findings
   - Mark all research TODOs complete
   - Create final TODO: "Write report"
"""
```

---

## 🐛 Troubleshooting

### Agent doesn't plan

1. **Be explicit**: "ALWAYS start by creating a plan with write_todos"
2. **Give complex task**: Simple questions don't need plans
3. **Check model**: Some models follow instructions better

### Too many TODOs

Add constraint:

```python
"Create no more than 5 TODOs for any task"
```

---

## 🔗 Next Steps

**Add human approval:**
→ `06_add_human_in_loop.md`

**Understand planning workflow:**
→ `02_patterns/planning_workflow/README.md`

---

## 💡 Key Takeaways

1. **write_todos** is enabled by default
2. **Prompt engineering** encourages planning
3. **Update status** as work progresses
4. TODOs accessible in **result["todos"]**
