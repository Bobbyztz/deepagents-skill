# Planning Workflow Pattern

> **📋 Prerequisites:** `01_atomic/05_enable_planning.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## ⚡ Quick Answer

**6-Step Workflow** (from Deep Research):

```
1. Plan      → write_todos
2. Save      → write_file("/request.md", query)
3. Execute   → task() or tools
4. Synthesize → combine findings
5. Write     → write_file("/report.md", report)
6. Verify    → read_file("/request.md"), confirm coverage
```

---

## 📖 System Prompt Template

```python
system_prompt = """# Research Orchestrator

## Workflow (MUST follow in order)

### 1. PLAN
Create a TODO list using write_todos:
- Break the task into 3-5 specific steps
- Each TODO should be actionable

### 2. SAVE REQUEST
Save the user's original request:
```

write_file("/user_request.md", <original query>)

```

### 3. EXECUTE
Work through each TODO:
- Delegate research to sub-agents using task()
- Update TODO status as you progress

### 4. SYNTHESIZE
Combine all findings:
- Consolidate citations
- Identify any gaps

### 5. WRITE REPORT
Write final output:
```

write_file("/final_report.md", <report>)

```

### 6. VERIFY
Read the original request and confirm:
- All points addressed
- No missing information
"""
```

---

## 🎯 Why This Pattern?

| Without Planning      | With Planning              |
| --------------------- | -------------------------- |
| Jumps into action     | Thinks first               |
| May miss requirements | Systematic coverage        |
| No progress tracking  | TODO status tracking       |
| Hard to verify        | Explicit verification step |

---

## 📊 Example Execution

**User**: "Compare Python vs JavaScript for web development"

**Agent**:

```
1. write_todos([
     {"task": "Research Python strengths", "status": "pending"},
     {"task": "Research JavaScript strengths", "status": "pending"},
     {"task": "Write comparison", "status": "pending"}
   ])

2. write_file("/user_request.md", "Compare Python vs JavaScript...")

3. task("researcher", "Research Python web development")
   → Update TODO 1 to "completed"

   task("researcher", "Research JavaScript web development")
   → Update TODO 2 to "completed"

4. Synthesize: Combine Python and JavaScript findings

5. write_file("/final_report.md", "## Comparison\n...")
   → Update TODO 3 to "completed"

6. read_file("/user_request.md")
   → Verify: "Does report address 'Compare Python vs JavaScript'? ✓"
```

---

## 🔧 Tips

1. **Be explicit**: Tell agent to follow steps "in order"
2. **Save early**: User request saved before any work
3. **Update TODOs**: Track progress visibly
4. **Verify last**: Always check against original request

---

## 🔗 Next Steps

**Enable planning:**
→ `01_atomic/05_enable_planning.md`

**Context isolation:**
→ `../context_isolation/README.md`

---

## 💡 Key Takeaways

1. **Plan before acting** - write_todos first
2. **Save original request** - for verification
3. **Update progress** - TODO status tracking
4. **Verify at end** - compare output to request
