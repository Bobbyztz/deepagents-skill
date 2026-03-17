# Hybrid Architecture Patterns

> **📋 Prerequisites:**
>
> - `00_quickstart/deep_agent_as_node.md`
> - `00_quickstart/architecture_comparison.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## ⚡ Quick Answer

**Hybrid = LangGraph 主图（编排） + Deep Agent 节点（执行）**

```python
from langgraph.graph import StateGraph, START, END
from deepagents import create_deep_agent

# Deep Agents for complex sub-tasks
research_agent = create_deep_agent(model, tools, "Research expert")
analysis_agent = create_deep_agent(model, tools, "Analysis expert")

# Wrap as LangGraph nodes
def research_node(state):
    result = research_agent.invoke({"messages": [{"role": "user", "content": state["query"]}]})
    return {"research": result["messages"][-1].content}

def analysis_node(state):
    result = analysis_agent.invoke({"messages": [{"role": "user", "content": state["research"]}]})
    return {"analysis": result["messages"][-1].content}

# LangGraph for orchestration
builder = StateGraph(State)
builder.add_node("research", research_node)
builder.add_node("analysis", analysis_node)
builder.add_edge(START, "research")
builder.add_edge("research", "analysis")
builder.add_edge("analysis", END)

graph = builder.compile()
```

---

## 📖 Why Hybrid?

| Aspect             | Pure Deep Agents | Pure LangGraph | Hybrid |
| ------------------ | ---------------- | -------------- | ------ |
| Planning           | ✅ Built-in      | ❌ Manual      | ✅     |
| File System        | ✅ Built-in      | ❌ Manual      | ✅     |
| Complex Topology   | ❌ Limited       | ✅ Full        | ✅     |
| Parallel Execution | ❌ Limited       | ✅ Full        | ✅     |
| Code Complexity    | Low              | Medium         | Medium |

---

## 🎯 Pattern 1: Sequential Pipeline

```python
# Three-stage pipeline: Research → Analyze → Write
research_agent = create_deep_agent(model, [search_tool, think_tool], "Researcher")
analysis_agent = create_deep_agent(model, [analyze_tool], "Analyst")
writing_agent = create_deep_agent(model, [grammar_tool], "Writer")

class State(TypedDict):
    topic: str
    research: str
    analysis: str
    report: str

def research_node(state):
    result = research_agent.invoke({"messages": [{"role": "user", "content": f"Research: {state['topic']}"}]})
    return {"research": result["messages"][-1].content}

def analysis_node(state):
    result = analysis_agent.invoke({"messages": [{"role": "user", "content": f"Analyze:\n{state['research']}"}]})
    return {"analysis": result["messages"][-1].content}

def writing_node(state):
    result = writing_agent.invoke({"messages": [{"role": "user", "content": f"Write report:\n{state['analysis']}"}]})
    return {"report": result["messages"][-1].content}

# Pipeline
builder.add_edge(START, "research")
builder.add_edge("research", "analysis")
builder.add_edge("analysis", "writing")
builder.add_edge("writing", END)
```

---

## 🎯 Pattern 2: Expert Router

```python
from typing import Literal

# Specialized agents
code_agent = create_deep_agent(model, [code_tools], "Code expert")
research_agent = create_deep_agent(model, [search_tools], "Research expert")
general_agent = create_deep_agent(model, [], "General assistant")

def classify(state) -> Literal["code", "research", "general"]:
    query = state["query"].lower()
    if any(kw in query for kw in ["code", "program", "function"]):
        return "code"
    elif any(kw in query for kw in ["research", "find", "search"]):
        return "research"
    return "general"

def code_node(state):
    return wrap_agent_call(code_agent, state)

def research_node(state):
    return wrap_agent_call(research_agent, state)

def general_node(state):
    return wrap_agent_call(general_agent, state)

def wrap_agent_call(agent, state):
    result = agent.invoke({"messages": [{"role": "user", "content": state["query"]}]})
    return {"result": result["messages"][-1].content}

builder.add_edge(START, "classify")
builder.add_conditional_edges("classify", classify)
builder.add_edge("code", END)
builder.add_edge("research", END)
builder.add_edge("general", END)
```

---

## 🎯 Pattern 3: Parallel Analysis

```python
import operator
from typing import Annotated

class ParallelState(TypedDict):
    topic: str
    perspectives: Annotated[list[str], operator.add]
    synthesis: str

tech_agent = create_deep_agent(model, tools, "Tech perspective")
business_agent = create_deep_agent(model, tools, "Business perspective")
social_agent = create_deep_agent(model, tools, "Social perspective")

def tech_node(state):
    result = tech_agent.invoke(...)
    return {"perspectives": [f"Tech: {result['messages'][-1].content}"]}

def business_node(state):
    result = business_agent.invoke(...)
    return {"perspectives": [f"Business: {result['messages'][-1].content}"]}

def social_node(state):
    result = social_agent.invoke(...)
    return {"perspectives": [f"Social: {result['messages'][-1].content}"]}

def synthesize(state):
    all_perspectives = "\n\n".join(state["perspectives"])
    return {"synthesis": f"Combined analysis:\n{all_perspectives}"}

# Parallel execution
builder.add_edge(START, "tech")
builder.add_edge(START, "business")
builder.add_edge(START, "social")

# Convergence
builder.add_edge("tech", "synthesize")
builder.add_edge("business", "synthesize")
builder.add_edge("social", "synthesize")
builder.add_edge("synthesize", END)
```

---

## 🎯 Pattern 4: Iterative Refinement

```python
def should_refine(state) -> Literal["refine", "__end__"]:
    if state["quality_score"] < 0.8 and state["iterations"] < 3:
        return "refine"
    return END

def evaluate_node(state):
    # Simple evaluation (could use LLM)
    score = len(state["draft"]) / 1000  # Simple heuristic
    return {"quality_score": min(score, 1.0)}

def refine_node(state):
    result = writing_agent.invoke({
        "messages": [{"role": "user", "content": f"Improve this:\n{state['draft']}"}]
    })
    return {
        "draft": result["messages"][-1].content,
        "iterations": state["iterations"] + 1
    }

builder.add_edge(START, "draft")
builder.add_edge("draft", "evaluate")
builder.add_conditional_edges("evaluate", should_refine, {
    "refine": "refine",
    END: END
})
builder.add_edge("refine", "evaluate")  # Loop back
```

---

## ⚠️ Anti-Patterns

### ❌ Deep Nesting

```python
# BAD: Agent calling agent calling agent
agent_a = create_deep_agent(subagents=[agent_b])  # Don't nest!

# GOOD: Flat structure
builder.add_node("a", agent_a_node)
builder.add_node("b", agent_b_node)
```

### ❌ State Pollution

```python
# BAD: Leaking internal state
def node(state):
    result = agent.invoke(...)
    return result  # Leaks messages, files, todos!

# GOOD: Extract only what you need
def node(state):
    result = agent.invoke(...)
    return {"summary": result["messages"][-1].content}
```

---

## 📊 When to Use Hybrid

| Situation                         | Recommendation             |
| --------------------------------- | -------------------------- |
| Simple task                       | Pure Deep Agent            |
| Complex topology needed           | LangGraph                  |
| Complex topology + planning/files | **Hybrid**                 |
| Multiple specialized agents       | **Hybrid**                 |
| Production system                 | **Hybrid** (most flexible) |

---

## 🔗 Next Steps

**Core concept:**
→ `00_quickstart/deep_agent_as_node.md`

**Complex topology:**
→ `../complex_topology/README.md`

**Complete example:**
→ `03_examples/hybrid_multi_agent/README.md`

---

## 💡 Key Takeaways

1. **LangGraph for orchestration** (what, when)
2. **Deep Agents for execution** (how)
3. **State mapping** is the bridge
4. **Flat structure** over deep nesting
5. **Best of both worlds** for production systems
