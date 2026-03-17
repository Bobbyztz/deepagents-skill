# Deep Research: File-by-File Walkthrough

> **📋 Prerequisites:** Read `01_architecture.md`

---

## 📂 Project Structure Reminder

```
deep_research/
├── agent.py              ← Entry point (60 lines)
└── research_agent/
    ├── prompts.py        ← 3 prompts (173 lines)
    └── tools.py          ← 2 tools (117 lines)
```

**Total: ~350 lines** for a production research agent!

---

## 📄 File 1: agent.py

**Location:** `deep_research/agent.py`

### Imports (Lines 1-18)

```python
from datetime import datetime
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent

from research_agent.prompts import (
    RESEARCHER_INSTRUCTIONS,           # Sub-agent prompt
    RESEARCH_WORKFLOW_INSTRUCTIONS,    # Main agent workflow
    SUBAGENT_DELEGATION_INSTRUCTIONS,  # Delegation strategy
)
from research_agent.tools import tavily_search, think_tool
```

**Key**: Separates prompts and tools into dedicated files.

### Configuration (Lines 20-25)

```python
max_concurrent_research_units = 3  # Max parallel sub-agents
max_researcher_iterations = 3      # Max delegation rounds

current_date = datetime.now().strftime("%Y-%m-%d")
```

**Why these limits?**

- 3 parallel: Balance speed vs API rate limits
- 3 iterations: Prevent infinite delegation loops
- Date injection: Give sub-agent temporal context

### Main Agent Prompt (Lines 27-37)

```python
INSTRUCTIONS = (
    RESEARCH_WORKFLOW_INSTRUCTIONS                  # Part 1: 6-step workflow
    + "\n\n"
    + "=" * 80
    + "\n\n"
    + SUBAGENT_DELEGATION_INSTRUCTIONS.format(      # Part 2: Delegation rules
        max_concurrent_research_units=max_concurrent_research_units,
        max_researcher_iterations=max_researcher_iterations,
    )
)
```

**Design**: 2-part prompt composition

1. **RESEARCH_WORKFLOW_INSTRUCTIONS**: What to do (6 steps)
2. **SUBAGENT_DELEGATION_INSTRUCTIONS**: How to delegate (when to parallelize)

### Sub-agent Definition (Lines 39-45)

```python
research_sub_agent = {
    "name": "research-agent",
    "description": "Delegate research to the sub-agent researcher. Only give this researcher one topic at a time.",
    "system_prompt": RESEARCHER_INSTRUCTIONS.format(date=current_date),
    "tools": [tavily_search, think_tool]
}
```

**Key fields:**

- `name`: Identifier for task() calls
- `description`: LLM reads this to decide when to use
- `system_prompt`: Sub-agent's instructions (separate from main!)
- `tools`: Same tools as main, but sub actually uses them

### Model Selection (Lines 47-51)

```python
# Option 1: Gemini 3 (commented out)
# model = ChatGoogleGenerativeAI(model="gemini-3-pro-preview", temperature=0.0)

# Option 2: Claude 4.5 (active)
model = init_chat_model(model="anthropic:claude-sonnet-4-5-20250929", temperature=0.0)
```

**Why temperature=0.0?** Deterministic output for production.

### Agent Creation (Lines 53-59)

```python
agent = create_deep_agent(
    model=model,
    tools=[tavily_search, think_tool],  # Main has tools...
    system_prompt=INSTRUCTIONS,         # ...but told not to use for research
    subagents=[research_sub_agent],     # Delegates instead
)
```

**Result**: `agent` is a runnable LangGraph compiled graph.

---

## 📄 File 2: research_agent/prompts.py

**Location:** `deep_research/research_agent/prompts.py`

### Prompt 1: RESEARCH_WORKFLOW_INSTRUCTIONS (Lines 3-65)

**Purpose:** Main agent's 6-step workflow

**Structure:**

```markdown
# Research Workflow

1. **Plan**: Create todos
2. **Save Request**: write_file("/research_request.md")
3. **Research**: Delegate with task()
4. **Synthesize**: Consolidate citations
5. **Write Report**: write_file("/final_report.md")
6. **Verify**: Confirm coverage

## Report Writing Guidelines

- For comparisons: Intro → A → B → Comparison → Conclusion
- For lists: Item 1 → Item 2 → ...
- Citations: [1], [2], [3] inline

**Key Rules**:

- Each unique URL gets ONE citation number
- Use paragraph form (text-heavy)
- No self-referential language ("I found...")
```

**Design insight**: Explicit output format reduces variance.

### Prompt 2: SUBAGENT_DELEGATION_INSTRUCTIONS (Lines 138-173)

**Purpose:** When to use 1 vs multiple sub-agents

**Key sections:**

**Default Rule:**

```
Start with 1 sub-agent for most queries:
- "What is X?" → 1 sub-agent
- "Research Y" → 1 sub-agent
```

**Parallel only for explicit comparisons:**

```
"Compare A vs B vs C" → 3 parallel
"Research X in Europe, Asia, America" → 3 parallel
```

**Limits:**

```
- Max {max_concurrent_research_units} parallel
- Max {max_researcher_iterations} rounds
```

**Design insight**: Default to single comprehensive, parallelize only when clear benefit.

### Prompt 3: RESEARCHER_INSTRUCTIONS (Lines 67-132)

**Purpose:** Sub-agent's execution guidelines

**Key sections:**

**Tools:**

```
1. tavily_search: Web search
2. think_tool: Reflection
   **CRITICAL: Use after EACH search**
```

**Hard Limits:**

```
Tool Call Budgets:
- Simple: 2-3 searches max
- Complex: 5 searches max

Stop Immediately When:
- Can answer comprehensively
- Have 3+ sources
- Last 2 searches similar
```

**Output Format:**

```markdown
## Key Findings

Finding A [1]. Finding B [2].

### Sources

[1] Source Title: URL
[2] Another Title: URL
```

**Design insight**: Explicit stop conditions prevent endless searching.

---

## 📄 File 3: research_agent/tools.py

**Location:** `deep_research/research_agent/tools.py`

### Helper Function: fetch_webpage_content (Lines 16-35)

```python
def fetch_webpage_content(url: str, timeout: float = 10.0) -> str:
    """Fetch and convert webpage to markdown."""
    headers = {
        "User-Agent": "Mozilla/5.0 ..."  # Bypass anti-scraping
    }

    try:
        response = httpx.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return markdownify(response.text)  # HTML → Markdown
    except Exception as e:
        return f"Error fetching {url}: {str(e)}"
```

**Design decisions:**

1. User-Agent header (avoid 403 errors)
2. Timeout (prevent hanging)
3. Markdown conversion (LLM-friendly)
4. Error handling (graceful failure)

### Tool 1: tavily_search (Lines 38-88)

```python
@tool(parse_docstring=True)
def tavily_search(
    query: str,
    max_results: Annotated[int, InjectedToolArg] = 1,
    topic: Annotated[Literal["general", "news", "finance"], InjectedToolArg] = "general",
) -> str:
    """Search the web for information.

    Uses Tavily to discover URLs, then fetches full content as markdown.
    """
    # 1. Use Tavily for URL discovery
    search_results = tavily_client.search(query, max_results=max_results, topic=topic)

    # 2. Fetch full content for each URL
    result_texts = []
    for result in search_results.get("results", []):
        url = result["url"]
        title = result["title"]
        content = fetch_webpage_content(url)  # Full content!

        result_texts.append(f"## {title}\n**URL:** {url}\n\n{content}\n---")

    # 3. Format response
    return f"🔍 Found {len(result_texts)} result(s) for '{query}':\n\n{chr(10).join(result_texts)}"
```

**Key design: Full content vs summaries**

- Tavily provides summaries in `result["content"]`
- **Ignored** in favor of full HTML fetch
- **Why?** Preserve all information, let LLM decide what's important

### Tool 2: think_tool (Lines 91-116)

```python
@tool(parse_docstring=True)
def think_tool(reflection: str) -> str:
    """Strategic reflection tool for decision-making.

    Use after each search to analyze results and plan next steps.

    Reflection should address:
    1. Analysis of current findings
    2. Gap assessment
    3. Quality evaluation
    4. Strategic decision (continue or stop?)
    """
    return f"Reflection recorded: {reflection}"
```

**Magic: 1-line implementation, huge impact**

- Implementation trivial (echo input)
- Docstring powerful (guides LLM usage)
- System prompt reinforces ("Use after EACH search")
- **Result**: Forces deliberate pauses, quality-driven search

---

## 🔗 How Files Work Together

```
agent.py (Entry)
   ├─ Imports prompts from prompts.py
   ├─ Imports tools from tools.py
   ├─ Assembles INSTRUCTIONS from 2 prompts
   ├─ Defines research_sub_agent with RESEARCHER_INSTRUCTIONS
   ├─ Calls create_deep_agent()
   └─ Returns compiled agent

When agent runs:
   Main agent → Uses INSTRUCTIONS (workflow + delegation)
      ↓
   Calls task() → Invokes research_sub_agent
      ↓
   Sub-agent → Uses RESEARCHER_INSTRUCTIONS
      ↓
   Calls tavily_search (from tools.py)
      ↓
   Calls think_tool (from tools.py)
      ↓
   Returns summary to main
      ↓
   Main synthesizes and writes report
```

---

## 💡 Key Takeaways

1. **Modularity**: Prompts, tools, agent config all separated
2. **Prompt composition**: Main = Workflow + Delegation
3. **Same tools, different usage**: Main has tools but doesn't use; sub uses them
4. **Full content philosophy**: Fetch everything, let LLM filter
5. **Simple is powerful**: think_tool is 1 line but critical

---

## 🔗 Next Steps

**See execution flow:**
→ `03_execution_flow.md`

**Deep dive on prompts:**
→ `04_prompt_system.md`

**Tool implementation details:**
→ `05_tool_implementation.md`
