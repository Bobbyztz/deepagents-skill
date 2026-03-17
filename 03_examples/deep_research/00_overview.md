# Deep Research: Complete Example Overview

> **📋 Prerequisites:** Read `00_quickstart/what_is_deep_agents.md`

---

## 🎯 What is Deep Research?

**Deep Research** is the official LangChain example showcasing Deep Agents capabilities. It's a **production-ready research agent** that:

- 📊 Conducts multi-source research
- 🤖 Uses sub-agents for context isolation
- 💭 Employs reflection-driven search (think_tool)
- 📝 Generates professional reports with inline citations
- ⚡ Handles parallel research for comparisons

**User query:**

```
"Compare Python vs JavaScript for web development"
```

**Agent output:**

```markdown
# Python vs JavaScript for Web Development

## Introduction

This report compares Python and JavaScript...

## Python Overview

Python offers Django [1] and Flask [2] frameworks...

## JavaScript Overview

JavaScript excels with Node.js [3]...

## Detailed Comparison

| Aspect | Python | JavaScript |
...

### Sources

[1] Django Documentation: https://djangoproject.com/
[2] Flask Guide: https://flask.palletsprojects.com/
[3] Node.js Official: https://nodejs.org/
```

---

## 🏗️ Architecture at a Glance

```
User: "Compare Python vs JavaScript"
   ↓
Main Orchestrator
   ├─ Plan: write_todos([...])
   ├─ Save: write_file("/research_request.md", query)
   ├─ Delegate (parallel):
   │    ├─ Sub-agent 1: Research Python
   │    │    ↳ Search → Think → Search → Think → Return findings [1],[2]
   │    └─ Sub-agent 2: Research JavaScript
   │         ↳ Search → Think → Search → Return findings [1],[2]
   ├─ Synthesize: Merge citations [1],[2],[3],[4]
   ├─ Write: write_file("/final_report.md", report)
   └─ Verify: ead("/research_request.md"), confirm coverage
```

---

## 📂 File Structure

```
deep_research/
├── agent.py              # Main entry: creates orchestrator + sub-agent
├── research_agent/
│   ├── prompts.py        # 3-tier prompt system
│   └── tools.py          # tavily_search + think_tool
└── langgraph.json        # Deployment config
```

**Just 3 core files!**

---

## 🧩 Key Components

### 1. Main Orchestrator (agent.py)

**Responsibilities:**

- Plans research strategy
- Delegates to sub-agents
- Synthesizes results
- Writes final report
- **Never researches directly**

**Tools**: Has `tavily_search` and `think_tool` but **instructed not to use them**

### 2. Research Sub-agent (agent.py)

**Responsibilities:**

- Executes web searches
- Reflects after each search (think_tool)
- Returns findings with citations

**Tools**: Actually uses `tavily_search` and `think_tool`

### 3. Two Tools (tools.py)

**tavily_search:**

- Uses Tavily for URL discovery
- Fetches full webpage content (HTTP)
- Converts to Markdown
- Returns complete text (not summaries)

**think_tool:**

- Forces reflection after each search
- Simple implementation (just returns input)
- Powerful behavioral effect

### 4. Three-tier Prompts (prompts.py)

**RESEARCH_WORKFLOW_INSTRUCTIONS:**

- 6-step workflow for orchestrator
- Report writing guidelines
- Citation format rules

**SUBAGENT_DELEGATION_INSTRUCTIONS:**

- When to use 1 vs multiple sub-agents
- Parallelization strategy
- Limits (3 parallel max, 3 iterations max)

**RESEARCHER_INSTRUCTIONS:**

- Sub-agent's execution guidelines
- Search budgets (2-3 for simple, 5 for complex)
- Stop conditions
- Citation format

---

## 🎯 Design Patterns Used

| Pattern                 | Where                 | Why                              |
| ----------------------- | --------------------- | -------------------------------- |
| **Context Isolation**   | Sub-agents            | Keep orchestrator context clean  |
| **Reflection Loop**     | think_tool            | Quality-driven search, not blind |
| **Planning Workflow**   | 6-step process        | Consistent, verifiable execution |
| **Parallel Delegation** | Multiple task() calls | Fast comparison queries          |

---

## 🔍 Execution Flow Example

**Query:** "Compare Python vs JavaScript for web development"

### Phase 1: Planning

```
Orchestrator: write_todos([
    {"task": "Save request", "status": "in_progress"},
    {"task": "Research Python", "status": "pending"},
    {"task": "Research JavaScript", "status": "pending"},
    {"task": "Synthesize and write report", "status": "pending"}
])
```

### Phase 2: Save Request

```
Orchestrator: write_file("/research_request.md", "Compare Python vs JavaScript...")
```

### Phase 3: Parallel Delegation

```
Orchestrator calls:
  task(subagent_type="research-agent", description="Research Python for web development")
  task(subagent_type="research-agent", description="Research JavaScript for web development")

Both execute in parallel ⚡
```

### Phase 4: Sub-agent 1 Execution (Python)

```
Sub-agent 1 (isolated context):
  1. tavily_search("Python web development frameworks")
  2. think_tool("Found Django/Flask. Missing: performance, use cases")
  3. tavily_search("Python web performance use cases")
  4. think_tool("Enough info. Have 2 sources. Returning findings")
  5. Return: "## Python\nDjango [1]... Flask [2]...\n### Sources\n[1] ...\n[2] ..."
```

### Phase 5: Sub-agent 2 Execution (JavaScript)

```
Sub-agent 2 (isolated, parallel):
  Similar flow...
  Return: "## JavaScript\nNode.js [1]... Express [2]..."
```

### Phase 6: Synthesis

```
Orchestrator receives both results:
  - Python findings use [1], [2]
  - JavaScript findings also use [1], [2]

Merge citations:
  - Python [1] → Report [1]
  - Python [2] → Report [2]
  - JavaScript [1] → Report [3]
  - JavaScript [2] → Report [4]
```

### Phase 7: Write Report

```
Orchestrator: write_file("/final_report.md", """
# Python vs JavaScript...
Python has Django [1]...
JavaScript has Node.js [3]...

### Sources
[1] Django: https://...
[2] Flask: https://...
[3] Node.js: https://...
[4] Express: https://...
""")
```

### Phase 8: Verification

```
Orchestrator: read_file("/research_request.md")
Orchestrator: ✅ Confirmed coverage of Python, JavaScript, comparison, citations
```

---

## 📊 Why This Example Matters

### 1. Production-Ready

- Handles real-world research tasks
- Robust error handling (search budgets, stop conditions)
- Professional output (citations, structured reports)

### 2. Showcases All Core Capabilities

- ✅ Planning (write_todos)
- ✅ File system (/research_request.md, /final_report.md)
- ✅ Sub-agents (research-agent)
- ✅ Context isolation (messy searches contained)
- ✅ Parallel execution (comparison queries)

### 3. Reusable Patterns

- Reflection loop extractable to other domains
- Parallel delegation strategy applicable broadly
- Citation management system reusable
- 6-step workflow template

---

## 🔗 Deep Dive Navigation

Continue learning in order:

1. **Architecture Deep Dive**
   → `01_architecture.md` (3-layer system explained)

2. **File-by-File Walkthrough**
   → `02_file_walkthrough.md` (agent.py, tools.py, prompts.py)

3. **Complete Execution Flow**
   → `03_execution_flow.md` (Step-by-step trace)

4. **Prompt Engineering**
   → `04_prompt_system.md` (3-tier prompt design)

5. **Tool Implementation**
   → `05_tool_implementation.md` (tavily_search + think_tool deep dive)

---

## 💡 Key Takeaways

1. **Simplicity**: Only 3 core files, ~200 lines total
2. **Powerful patterns**: Context isolation + reflection = high quality
3. **Extractable**: Each pattern can be used independently
4. **Production-tested**: Based on Claude Code design
5. **Extensible**: Easy to add more tools, sub-agents, or prompts
