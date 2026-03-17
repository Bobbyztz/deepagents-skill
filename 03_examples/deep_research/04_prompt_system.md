# Deep Research: Prompt System Deep Dive

> **📋 Prerequisites:** Read `03_execution_flow.md`

---

## 🎯 Three-Tier Prompt Architecture

Deep Research uses **3 distinct prompts** for different roles:

```
1. RESEARCH_WORKFLOW_INSTRUCTIONS → Main agent (workflow)
2. SUBAGENT_DELEGATION_INSTRUCTIONS → Main agent (delegation logic)
3. RESEARCHER_INSTRUCTIONS → Sub-agent (execution)
```

---

## 📝 Prompt 1: RESEARCH_WORKFLOW_INSTRUCTIONS

**Target:** Main agent (orchestrator)  
**Purpose:** Define 6-step workflow  
**Location:** `prompts.py` lines 3-65

### Key Sections

**1. Workflow Steps:**

```markdown
1. **Plan**: Create todo list with write_todos
2. **Save Request**: write_file("/research_request.md", query)
3. **Research**: Delegate to sub-agents - ALWAYS use sub-agents, never research yourself
4. **Synthesize**: Consolidate citations (each URL = one number)
5. **Write Report**: write_file("/final_report.md", formatted_report)
6. **Verify**: read("/research_request.md"), confirm coverage
```

**Design insight:** Hard rule "NEVER research yourself" prevents orchestrator from using tools directly.

**2. Report Structure Templates:**

```markdown
For comparisons:

1. Introduction
2. Overview of topic A
3. Overview of topic B
4. Detailed comparison
5. Conclusion

For lists/rankings:

1. Item 1 with details
2. Item 2 with details
   ...

For summaries:

1. Overview
2. Key concept 1
3. Key concept 2
   ...
4. Conclusion
```

**Design insight:** Explicit templates reduce output variance.

**3. Citation Rules:**

```markdown
- Cite inline: [1], [2], [3]
- Each unique URL gets ONE number across ALL sub-agent findings
- End with ### Sources section
- Format: [1] Title: URL (separate lines)
- No gaps in numbering
```

**Design insight:** Prevents duplicate citations from multiple sub-agents.

---

## 📝 Prompt 2: SUBAGENT_DELEGATION_INSTRUCTIONS

**Target:** Main agent (orchestrator)  
**Purpose:** When to use 1 vs multiple sub-agents  
**Location:** `prompts.py` lines 138-173

### Core Strategy

**DEFAULT: 1 sub-agent**

```markdown
Start with 1 sub-agent for most queries:

- "What is quantum computing?" → 1 (comprehensive)
- "List top 10 coffee shops" → 1
- "Research AI agents" → 1 (covers all aspects)
```

**ONLY parallelize for explicit comparisons:**

```markdown
Explicit comparisons:

- "Compare OpenAI vs Anthropic vs DeepMind" → 3 parallel
- "Compare Python vs JavaScript" → 2 parallel

Clearly separated aspects:

- "Research renewable energy in Europe, Asia, North America" → 3 parallel
```

### Key Principles

```markdown
- **Bias towards single sub-agent**: One comprehensive task > multiple narrow ones
- **Avoid premature decomposition**: Don't split "research X" into "X overview", "X tech", "X apps"
- **Parallelize only for clear comparisons**: Different entities or geographic separation
```

**Design insight:** Prevents unnecessary parallelization → saves costs.

### Limits (Injected via .format())

```python
- Max {max_concurrent_research_units} parallel sub-agents per iteration
- Max {max_researcher_iterations} delegation rounds
```

**Becomes:**

```
- Max 3 parallel sub-agents per iteration
- Max 3 delegation rounds
```

---

## 📝 Prompt 3: RESEARCHER_INSTRUCTIONS

**Target:** Research sub-agent (worker)  
**Purpose:** Execution guidelines  
**Location:** `prompts.py` lines 67-132

### Tool Instructions

```markdown
Available Research Tools:

1. **tavily_search**: Web search
2. **think_tool**: Reflection and planning
   **CRITICAL: Use think_tool after EACH search**
```

**Design insight:** "CRITICAL" + "EACH" enforces reflection loop.

### Execution Steps

```markdown
1. Read the question carefully - What specific information needed?
2. Start with broader searches - Comprehensive queries first
3. After each search, pause and assess - Enough? What's missing?
4. Execute narrower searches - Fill gaps
5. Stop when confident - Don't search for perfection
```

**Design insight:** Step 3 ties to think_tool usage.

### Hard Limits

```markdown
**Tool Call Budgets**:

- Simple queries: 2-3 search tool calls maximum
- Complex queries: 5 search tool calls maximum
- Always stop after 5 if can't find right sources

**Stop Immediately When**:

- Can answer comprehensively
- Have 3+ relevant examples/sources
- Last 2 searches returned similar information
```

**Design insight:** Prevents infinite search loops.

### Reflection Guidance

```markdown
After each search, use think_tool to analyze:

- What key information did I find?
- What's missing?
- Do I have enough to answer comprehensively?
- Should I search more or provide my answer?
```

**Design insight:** Structures the reflection content.

### Output Format

```markdown
## Key Findings

Context engineering is critical [1]. Studies show 40% improvement [2].

### Sources

[1] Context Guide: https://example.com/context
[2] Performance Study: https://example.com/study

NOTE: Orchestrator will consolidate citations from all sub-agents.
```

**Design insight:** Sub-agent numbers citations independently; orchestrator renumbers.

---

## 🎨 Prompt Engineering Techniques Used

### 1. Explicit Workflows

**Bad:**

```
"Research the topic and write a report"
```

**Good (Deep Research):**

```
"Follow this workflow:
1. Plan (write_todos)
2. Save Request (write_file)
3. Research (delegate)
4. Synthesize
5. Write Report
6. Verify"
```

### 2. Hard Constraints

**Bad:**

```
"Don't search too much"
```

**Good:**

```
"Simple queries: 2-3 searches maximum
Complex queries: 5 searches maximum"
```

### 3. Decision Criteria

**Bad:**

```
"Use multiple sub-agents when appropriate"
```

**Good:**

```
"Use 1 sub-agent for most queries.
ONLY use multiple for:
- Explicit comparisons (A vs B)
- Geographic separation (Europe vs Asia)"
```

### 4. Examples

```markdown
DEFAULT: 1 sub-agent

- "What is X?" → 1
- "List top 10 Y" → 1

PARALLELIZE:

- "Compare A vs B vs C" → 3
```

**Design insight:** Examples help LLM pattern-match.

### 5. Output Templates

```markdown
For comparisons:

1. Introduction
2. Overview A
3. Overview B
4. Comparison
5. Conclusion
```

**Design insight:** Reduces variance in output structure.

---

## 💡 Key Takeaways

1. **Three-tier separation**: Workflow → Delegation → Execution
2. **Explicit > Implicit**: Hard rules, templates, examples
3. **Constraints prevent loops**: Search budgets, stop conditions
4. **Reflection enforced**: "CRITICAL: Use after EACH search"
5. **Defaults matter**: "Start with 1 sub-agent" prevents over-parallelization
6. **Format control**: Output templates ensure consistency

---

## 🔗 Final Step

**Tool implementation details:**
→ `05_tool_implementation.md`
