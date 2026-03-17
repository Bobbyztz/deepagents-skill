# Complex Topology Patterns【核心】

> **📋 Prerequisites:**
>
> - `00_quickstart/deep_agent_as_node.md`
> - `01_atomic/10_graph_api_basics.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## ⚡ Quick Answer: Three Core Topologies

### 1. Sequential Pipeline

```
START → A → B → C → END
```

### 2. Fan-out / Fan-in (Parallel)

```
       ┌→ B ─┐
START → A ─┼→ C ─┼→ D → END
       └→ E ─┘
```

### 3. Conditional Routing

```
         ┌→ B → END
START → A ─┼→ C → END
         └→ D → END
```

---

## 📖 Why Complex Topology?

| Pure Deep Agents               | LangGraph Complex Topology           |
| ------------------------------ | ------------------------------------ |
| One parent → multiple children | Multiple parents → multiple children |
| No inter-child communication   | Children can communicate             |
| Fixed delegation               | Dynamic branching                    |
| Simple control                 | Full graph control                   |

---

## 🎯 Pattern 1: Sequential Pipeline

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class State(TypedDict):
    input: str
    step1_result: str
    step2_result: str
    final_result: str

def step_1(state):
    return {"step1_result": f"Processed by step 1: {state['input']}"}

def step_2(state):
    return {"step2_result": f"Step 2 on: {state['step1_result']}"}

def step_3(state):
    return {"final_result": f"Final: {state['step2_result']}"}

builder = StateGraph(State)
builder.add_node("step1", step_1)
builder.add_node("step2", step_2)
builder.add_node("step3", step_3)

builder.add_edge(START, "step1")
builder.add_edge("step1", "step2")
builder.add_edge("step2", "step3")
builder.add_edge("step3", END)

graph = builder.compile()
```

---

## 🎯 Pattern 2: Fan-out / Fan-in

Parallel execution with result aggregation.

```python
import operator
from typing import Annotated

class ParallelState(TypedDict):
    topic: str
    results: Annotated[list[str], operator.add]  # Reducer for merging
    summary: str

def research_tech(state):
    return {"results": [f"Tech analysis of {state['topic']}"]}

def research_market(state):
    return {"results": [f"Market analysis of {state['topic']}"]}

def research_legal(state):
    return {"results": [f"Legal analysis of {state['topic']}"]}

def summarize(state):
    combined = "\n".join(state["results"])
    return {"summary": f"Summary:\n{combined}"}

builder = StateGraph(ParallelState)
builder.add_node("tech", research_tech)
builder.add_node("market", research_market)
builder.add_node("legal", research_legal)
builder.add_node("summarize", summarize)

# Fan-out: Multiple edges from START
builder.add_edge(START, "tech")
builder.add_edge(START, "market")
builder.add_edge(START, "legal")

# Fan-in: Multiple edges to summarize
builder.add_edge("tech", "summarize")
builder.add_edge("market", "summarize")
builder.add_edge("legal", "summarize")

builder.add_edge("summarize", END)

graph = builder.compile()
```

**Key**: Use `Annotated[list, operator.add]` reducer to merge parallel results.

---

## 🎯 Pattern 3: Conditional Routing

```python
from typing import Literal

class RoutingState(TypedDict):
    query: str
    category: str
    result: str

def classify(state):
    query = state["query"].lower()
    if "code" in query:
        return {"category": "code"}
    elif "research" in query:
        return {"category": "research"}
    return {"category": "general"}

def route(state) -> Literal["code_handler", "research_handler", "general_handler"]:
    return f"{state['category']}_handler"

def code_handler(state):
    return {"result": "Handled as code request"}

def research_handler(state):
    return {"result": "Handled as research request"}

def general_handler(state):
    return {"result": "Handled as general request"}

builder = StateGraph(RoutingState)
builder.add_node("classify", classify)
builder.add_node("code_handler", code_handler)
builder.add_node("research_handler", research_handler)
builder.add_node("general_handler", general_handler)

builder.add_edge(START, "classify")
builder.add_conditional_edges("classify", route)
builder.add_edge("code_handler", END)
builder.add_edge("research_handler", END)
builder.add_edge("general_handler", END)

graph = builder.compile()
```

---

## 🎯 Pattern 4: Loop with Exit Condition

```python
def should_continue(state) -> Literal["process", "__end__"]:
    if state["iterations"] >= 3:
        return END
    return "process"

def process(state):
    return {"iterations": state["iterations"] + 1}

builder = StateGraph(State)
builder.add_node("process", process)
builder.add_edge(START, "process")
builder.add_conditional_edges("process", should_continue, {
    "process": "process",  # Loop back
    END: END
})

graph = builder.compile()
```

---

## 🔄 Pattern 5: Inter-Child Communication

Children communicate through shared state:

```python
class CollaborativeState(TypedDict):
    task: str
    agent_a_result: str
    agent_b_result: str
    final: str

def agent_a(state):
    # A does initial work
    return {"agent_a_result": "A's findings"}

def agent_b(state):
    # B uses A's result
    a_work = state.get("agent_a_result", "")
    return {"agent_b_result": f"B building on: {a_work}"}

def combine(state):
    return {"final": f"{state['agent_a_result']} + {state['agent_b_result']}"}

# A → B → combine (sequential with data dependency)
builder.add_edge(START, "agent_a")
builder.add_edge("agent_a", "agent_b")
builder.add_edge("agent_b", "combine")
builder.add_edge("combine", END)
```

---

## 🤝 With Deep Agents as Nodes

Combine complex topology with Deep Agent power:

```python
from deepagents import create_deep_agent

# Create specialized Deep Agents
tech_agent = create_deep_agent(model, [code_tools], "Tech expert")
market_agent = create_deep_agent(model, [search_tools], "Market analyst")

# Wrap as nodes
def tech_node(state):
    result = tech_agent.invoke({"messages": [{"role": "user", "content": state["query"]}]})
    return {"results": [result["messages"][-1].content]}

def market_node(state):
    result = market_agent.invoke({"messages": [{"role": "user", "content": state["query"]}]})
    return {"results": [result["messages"][-1].content]}

# Use in complex topology
builder.add_edge(START, "tech")    # Parallel
builder.add_edge(START, "market")  # Parallel
builder.add_edge("tech", "summarize")
builder.add_edge("market", "summarize")
```

---

## 📊 Topology Decision Guide

| Need                    | Pattern        | Example                |
| ----------------------- | -------------- | ---------------------- |
| Step-by-step processing | Sequential     | ETL pipeline           |
| Multiple perspectives   | Fan-out/Fan-in | Multi-source research  |
| Different handlers      | Conditional    | Expert routing         |
| Iterative refinement    | Loop           | Quality improvement    |
| Data dependencies       | Inter-child    | Build on previous work |

---

## 🔗 Next Steps

**Dynamic branching:**
→ `../send_api_patterns/README.md`

**Deep Agent as node:**
→ `00_quickstart/deep_agent_as_node.md`

**Complete hybrid example:**
→ `03_examples/hybrid_multi_agent/README.md`

---

## 💡 Key Takeaways

1. **Fan-out/Fan-in** for parallel execution
2. **Reducers** merge parallel results
3. **Conditional edges** for dynamic routing
4. **Deep Agents as nodes** for best of both worlds
