# Deep Research: Complete Execution Flow

> **📋 Prerequisites:** Read `02_file_walkthrough.md`

---

## 🎯 Example Query

```
User: "Compare Python vs JavaScript for web development"
```

Let's trace **every state change** from start to finish.

---

## 📍 Phase 1: Invocation

```python
result = agent.invoke({
    "messages": [{"role": "user", "content": "Compare Python vs JavaScript for web development"}]
})
```

**Initial State:**

```python
{
    "messages": [
        HumanMessage(content="Compare Python vs JavaScript for web development")
    ],
    "files": {},
    "todos": []
}
```

---

## 📍 Phase 2: Planning (Iteration 1)

**Main Agent (Orchestrator) LLM Call:**

```
System Prompt: RESEARCH_WORKFLOW_INSTRUCTIONS + SUBAGENT_DELEGATION_INSTRUCTIONS
Input Messages: [HumanMessage("Compare Python vs JavaScript...")]
```

**Agent Decision:**

```
"This is an explicit comparison query. Per delegation instructions:
'Compare A vs B' → 2 parallel sub-agents.
First, I'll create a plan."
```

**Tool Calls:**

```python
[
    {
        "name": "write_todos",
        "args": {
            "todos": [
                {"task": "Save research request to file", "status": "in_progress"},
                {"task": "Research Python for web development", "status": "pending"},
                {"task": "Research JavaScript for web development", "status": "pending"},
                {"task": "Synthesize findings and write report", "status": "pending"}
            ]
        }
    }
]
```

**State After:**

```python
{
    "messages": [...previous, AIMessage(tool_calls=[...]), ToolMessage(...)],
    "todos": [
        {"task": "Save research request", "status": "in_progress"},
        {"task": "Research Python", "status": "pending"},
        {"task": "Research JavaScript", "status": "pending"},
        {"task": "Synthesize", "status": "pending"}
    ]
}
```

---

## 📍 Phase 3: Save Request (Iteration 2)

**Main Agent LLM Call:**

**Tool Call:**

```python
{
    "name": "write_file",
    "args": {
        "path": "/research_request.md",
        "content": "Compare Python vs JavaScript for web development"
    }
}
```

**State After:**

```python
{
    "files": {
        "/research_request.md": "Compare Python vs JavaScript for web development"
    }
}
```

---

## 📍 Phase 4: Parallel Delegation (Iteration 3)

**Main Agent LLM Call:**

**Decision:**

```
"Comparison query → 2 parallel sub-agents.
I'll delegate both simultaneously for speed."
```

**Tool Calls (in SAME response):**

```python
[
    {
        "name": "task",
        "args": {
            "subagent_type": "research-agent",
            "description": "Research Python for web development. Focus on frameworks, performance, and use cases."
        }
    },
    {
        "name": "task",
        "args": {
            "subagent_type": "research-agent",
            "description": "Research JavaScript for web development. Focus on frameworks, performance, and use cases."
        }
    }
]
```

**LangGraph detects 2 task() calls → Executes in parallel**

---

## 📍 Phase 5: Sub-agent 1 Execution (Python) [Parallel]

**Sub-agent Isolated State:**

```python
{
    "messages": [
        HumanMessage(content="Research Python for web development. Focus on frameworks, performance, and use cases.")
    ],
    "files": {},  # Shared with main via state merging
    "todos": []
}
```

### Sub-agent Iteration 1

**LLM Call:**

```
System Prompt: RESEARCHER_INSTRUCTIONS (with date injected)
```

**Decision:** "I'll start with a broad search on Python frameworks"

**Tool Call:**

```python
{
    "name": "tavily_search",
    "args": {"query": "Python web development frameworks Django Flask"}
}
```

**Tool Result:**

```
🔍 Found 1 result(s) for 'Python web development frameworks Django Flask':

## Django: The Web Framework for perfectionists with deadlines
**URL:** https://www.djangoproject.com/

Django is a high-level Python web framework...
[10,000 tokens of full webpage content in Markdown]
---
```

### Sub-agent Iteration 2

**LLM Call with updated context:**

```
Messages: [User message, AI search decision, ToolMessage(10k tokens)]
```

**Decision:** "Per instructions, use think_tool after each search"

**Tool Call:**

```python
{
    "name": "think_tool",
    "args": {
        "reflection": "I found detailed information about Django and Flask frameworks. Key points: Django is full-stack with ORM, Flask is lightweight and flexible. Still missing: performance data and production use cases. Need one more search focusing on performance and real-world applications."
    }
}
```

**Tool Result:**

```
Reflection recorded: I found detailed information...
```

### Sub-agent Iteration 3

**Tool Call:**

```python
{
    "name": "tavily_search",
    "args": {"query": "Python web development performance production use cases Instagram"}
}
```

**Tool Result:**

```
## Instagram Engineering: Web Service Efficiency at Instagram with Python
**URL:** https://instagram-engineering.com/...

Instagram's web service runs entirely on Python Django...
[12,000 tokens of content]
```

### Sub-agent Iteration 4

**Tool Call:**

```python
{
    "name": "think_tool",
    "args": {
        "reflection": "Now I have: 1) Framework details (Django/Flask), 2) Performance data (Instagram case study). I have 2 solid sources. This is enough to provide a comprehensive answer per the stop conditions (have 3+ sources OR can answer comprehensively). I'll return my findings."
    }
}
```

### Sub-agent Final Response

**AIMessage (returned to main agent):**

```markdown
## Python for Web Development

### Frameworks

Python offers two primary web frameworks: Django [1] and Flask [2]. Django is a high-level, full-stack framework with built-in ORM, admin interface, and authentication. Flask is a lightweight micro-framework providing flexibility for custom solutions.

### Performance & Use Cases

Python web frameworks are production-proven. Instagram's entire web service runs on Django, handling billions of requests [2]. While Python is single-threaded, it scales horizontally effectively.

### Sources

[1] Django Documentation:https://www.djangoproject.com/
[2] Instagram Engineering Blog: https://instagram-engineering.com/...
```

---

## 📍 Phase 6: Sub-agent 2 Execution (JavaScript) [Parallel]

**Executes same pattern simultaneously:**

1. Search "JavaScript web development Node.js Express"
2. think_tool reflection
3. Search "JavaScript web performance V8 engine"
4. think_tool decision to stop
5. Return findings with citations [1], [2]

**Final Response:**

```markdown
## JavaScript for Web Development

JavaScript dominates with Node.js [1] and Express [2]...

### Sources

[1] Node.js Official: https://nodejs.org/
[2] Express.js Guide: https://expressjs.com/
```

---

## 📍 Phase 7: Synthesis (Iteration 4)

**Main Agent Receives:**

```
ToolMessage 1 (from Sub-agent 1): "## Python...\n### Sources\n[1] Django...\n[2] Instagram..."
ToolMessage 2 (from Sub-agent 2): "## JavaScript...\n### Sources\n[1] Node.js...\n[2] Express..."
```

**Main Agent LLM Call:**

**Decision:**

```
"I have findings from both sub-agents. Now I need to:
1. Consolidate citations (each URL gets ONE number)
2. Synthesize into comparison format
3. Write to /final_report.md"
```

**Citation Consolidation Logic:**

```
Sub-agent 1 sources:
  [1] → Report [1]
  [2] → Report [2]

Sub-agent 2 sources:
  [1] → Report [3] (renumbered!)
  [2] → Report [4]
```

---

## 📍 Phase 8: Write Report (Iteration 5)

**Tool Call:**

```python
{
    "name": "write_file",
    "args": {
        "path": "/final_report.md",
        "content": """# Python vs JavaScript for Web Development

## Introduction
This report compares Python and JavaScript...

## Python Overview
Python offers Django [1] and Flask [2]...
Instagram proves Python's scalability [3]...

## JavaScript Overview
JavaScript excels with Node.js [4] and Express [5]...

## Detailed Comparison
| Aspect | Python | JavaScript |
|--------|--------|------------|
| Primary Framework | Django [1], Flask [2] | Node.js [4], Express [5] |
| Performance | Single-threaded, horizontally scalable [3] | Event-driven, non-blocking [6] |

## Conclusion
...

### Sources
[1] Django Documentation: https://www.djangoproject.com/
[2] Flask Guide: https://flask.palletsprojects.com/
[3] Instagram Engineering: https://instagram-engineering.com/...
[4] Node.js Official: https://nodejs.org/
[5] Express.js Guide: https://expressjs.com/
[6] V8 Performance: https://v8.dev/
"""
    }
}
```

**State After:**

```python
{
    "files": {
        "/research_request.md": "Compare Python vs JavaScript...",
        "/final_report.md": "# Python vs JavaScript...\n..."
    }
}
```

---

## 📍 Phase 9: Verification (Iteration 6)

**Tool Call:**

```python
{
    "name": "read_file",
    "args": {"path": "/research_request.md"}
}
```

**Tool Result:**

```
Compare Python vs JavaScript for web development
```

**Main Agent Decision:**

```
"Checking coverage:
✅ Python frameworks covered (Django, Flask)
✅ JavaScript frameworks covered (Node.js, Express)
✅ Performance comparison included
✅ Use cases provided
✅ Citations properly formatted [1]-[6]
✅ Report structure follows comparison guidelines

All aspects of the request are addressed. Verification complete."
```

---

## 📍 Phase 10: Final Response

**AIMessage to User:**

```
I've completed a comprehensive comparison of Python vs JavaScript for web development. The research covered frameworks, performance characteristics, and production use cases from both ecosystems. You can find the detailed report in /final_report.md with inline citations.

Key takeaways:
- Python: Django/Flask, proven scalability (Instagram case)
- JavaScript: Node.js/Express, event-driven architecture
- Both are production-ready with different strengths

Would you like me to elaborate on any specific aspect?
```

**Final State Returned:**

```python
{
    "messages": [... all messages ...],
    "files": {
        "/research_request.md": "...",
        "/final_report.md": "# Python vs JavaScript...\n..."
    },
    "todos": [
        {"task": "Save research request", "status": "completed"},
        {"task": "Research Python", "status": "completed"},
        {"task": "Research JavaScript", "status": "completed"},
        {"task": "Synthesize", "status": "completed"}
    ]
}
```

---

## 📊 Final Statistics

**Main Agent:**

- Iterations: 6
- LLM calls: 6
- Context size per call: ~2-3k tokens (clean!)
- Tools called: `write_todos`, `write_file` (×2), `task` (×2), `read_file`

**Sub-agent 1 (Python):**

- Iterations: 5
- LLM calls: 5
- Context size: Grows from 100 → 25k tokens
- Tools called: `tavily_search` (×2), `think_tool` (×2)

**Sub-agent 2 (JavaScript):**

- Iterations: 5
- LLM calls: 5
- Context size: Similar to Sub-agent 1
- Tools called: `tavily_search` (×2), `think_tool` (×2)

**Total:**

- LLM calls: 16
- Web searches: 4
- Reflections: 4
- Files created: 2

---

## 💡 Key Observations

1. **Parallel execution worked**: Both sub-agents ran simultaneously
2. **Context isolation effective**: Main agent never saw 50k tokens of search results
3. **Reflection loop prevented over-searching**: Stopped at 2 searches each (not max 5)
4. **Citation consolidation**: 4 unique sources → numbered 1-4 (later became 1-6 in final)
5. **Verification caught completeness**: Final step confirmed all aspects covered

---

## 🔗 Next Steps

**Prompt engineering deep dive:**
→ `04_prompt_system.md`

**Tool implementation details:**
→ `05_tool_implementation.md`
