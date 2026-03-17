# Reflection Loop Pattern (think_tool)

> **📋 Prerequisites:** `01_atomic/02_add_tool.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## ⚡ Quick Answer

```python
from langchain_core.tools import tool

@tool
def think_tool(reflection: str) -> str:
    """Reflect on your progress and plan next steps.

    Use this AFTER each action to analyze:
    - What did I find?
    - What's still missing?
    - Should I continue or stop?

    Args:
        reflection: Your detailed analysis and plan

    Returns:
        Acknowledgment
    """
    return f"Reflection recorded: {reflection}"
```

---

## 📖 Why Reflection?

### Without think_tool

```
Search → Search → Search → Search → Search
(Agent keeps searching without evaluating)
```

### With think_tool

```
Search → think_tool → Search → think_tool → STOP
(Agent evaluates after each action, stops when done)
```

---

## 🎯 The Pattern

### System Prompt

```python
system_prompt = """## Instructions

1. Start with a broad search
2. After EACH search, use think_tool to:
   - Analyze what you found
   - Identify what's missing
   - Decide: search more or stop?
3. Stop when you can answer confidently

## Hard Limits
- Maximum 5 searches
- Stop immediately when you have 3+ good sources
"""
```

### How It Works

```
1. web_search("quantum computing basics")
   ↓
2. think_tool("Found: overview of QC. Missing: practical applications. Continue: yes")
   ↓
3. web_search("quantum computing applications")
   ↓
4. think_tool("Found: applications. Have enough to answer. Continue: no")
   ↓
5. Return answer with citations
```

---

## 📊 Benefits

| Without Reflection | With Reflection     |
| ------------------ | ------------------- |
| Over-searches      | Efficient searching |
| No quality control | Self-assessment     |
| May miss gaps      | Identifies gaps     |
| Random stopping    | Strategic stopping  |

---

## 🔧 Implementation Tips

1. **Clear prompting**: Tell agent when to use think_tool
2. **After each action**: Not just searches—any significant step
3. **Structured reflection**: Guide what to think about
4. **Stop conditions**: Define when to stop clearly

---

## 🎯 Advanced: With Confidence Score

```python
@tool
def think_tool(reflection: str, confidence: int) -> str:
    """Reflect with confidence score.

    Args:
        reflection: Your analysis
        confidence: 1-10 score of answer confidence
    """
    return f"Confidence: {confidence}/10. {reflection}"
```

Prompt:

```
Stop searching when confidence >= 8
```

---

## 🔗 Next Steps

**Context isolation:**
→ `../context_isolation/README.md`

**Planning workflow:**
→ `../planning_workflow/README.md`

---

## 💡 Key Takeaways

1. **think_tool** enables quality-driven search
2. Use **after each action** for evaluation
3. Define **clear stop conditions**
4. Results in **more efficient**, higher-quality outputs
