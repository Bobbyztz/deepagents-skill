# Deep Research: Tool Implementation Deep Dive

> **📋 Prerequisites:** Read `04_prompt_system.md`

---

## 🛠️ Two Tools, Different Philosophies

Deep Research uses exactly **2 tools**, each demonstrating a different design philosophy:

1. **tavily_search**: Complex implementation, critical functionality
2. **think_tool**: Trivial implementation, powerful behavioral effect

---

## 🌐 Tool 1: tavily_search

**Location:** `tools.py` lines 38-88  
**Philosophy:** **Maximize information preservation**

### Design Decision: Tavily as URL Discovery Only

**What Tavily provides:**

```python
{
    "results": [
        {
            "title": "...",
            "url": "https://...",
            "content": "... (Summary, ~500 tokens) ...",  # We ignore this
            "score": 0.95
        }
    ]
}
```

**Deep Research's approach:**

```python
# ❌ Don't use Tavily's content summary
# ✅ Use only the URL, then fetch full content ourselves
```

### Implementation Flow

```python
@tool
def tavily_search(query: str, max_results: int = 1, topic: str = "general") -> str:
    # Step 1: Tavily discovers URLs
    search_results = tavily_client.search(
        query,
        max_results=max_results,
        topic=topic,
    )

    # Step 2: For each URL, fetch FULL content
    result_texts = []
    for result in search_results.get("results", []):
        url = result["url"]
        title = result["title"]

        # Step 3: HTTP request to get complete webpage
        content = fetch_webpage_content(url)  # Helper function

        # Step 4: Format as Markdown
        result_text = f"""## {title}
**URL:** {url}

{content}

---
"""
        result_texts.append(result_text)

    # Step 5: Return all results
    return f"🔍 Found {len(result_texts)} result(s) for '{query}':\n\n{chr(10).join(result_texts)}"
```

### Helper: fetch_webpage_content

```python
def fetch_webpage_content(url: str, timeout: float = 10.0) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = httpx.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return markdownify(response.text)  # HTML → Markdown
    except Exception as e:
        return f"Error fetching content from {url}: {str(e)}"
```

### Key Design Choices

**1. User-Agent Header**

```python
"User-Agent": "Mozilla/5.0 ..."  # Pretend to be a browser
```

**Why?** Some sites block requests without User-Agent (403 Forbidden).

**2. Markdown Conversion**

```python
markdownify(response.text)
```

**Why?**

- LLMs work better with Markdown than HTML
- More token-efficient (no HTML tags)
- Preserves structure (headings, lists, links)

**3. Full Content vs Summaries**

```python
content = fetch_webpage_content(url)  # Full content
# NOT: content = result["content"]    # Tavily's summary
```

**Why?**

- Preserves all information
- LLM decides what's important
- Avoids Tavily's summarization bias
- Better for nuanced questions

**4. Error Handling**

```python
try:
    response = httpx.get(...)
except Exception as e:
    return f"Error fetching..."  # Graceful failure
```

**Why?** Don't crash on 404, timeouts, etc. Return error as text for LLM to see.

### Result Format

```
🔍 Found 1 result(s) for 'Python web development frameworks':

## Django: The Web Framework for perfectionists with deadlines
**URL:** https://www.djangoproject.com/

# Django
Django is a high-level Python web framework that encourages rapid development...

## Features
- Object-relational mapper (ORM)
- Automatic admin interface
- Elegant URL design
...
[Full webpage content in Markdown, potentially 10,000+ tokens]

---
```

**Effect:** LLM gets complete information, can extract exactly what it needs.

---

## 💭 Tool 2: think_tool

**Location:** `tools.py` lines 91-116  
**Philosophy:** **Simplicity that shapes behavior**

### The "Magic" Implementation

```python
@tool(parse_docstring=True)
def think_tool(reflection: str) -> str:
    """Strategic reflection tool for research progress and decision-making.

    Use this tool after each search to analyze results and plan next steps systematically.
    This creates a deliberate pause in the research workflow for quality decision-making.

    When to use:
    - After receiving search results: What key information did I find?
    - Before deciding next steps: Do I have enough to answer comprehensively?
    - When assessing research gaps: What specific information am I still missing?
    - Before concluding research: Can I provide a complete answer now?

    Reflection should address:
    1. Analysis of current findings - What concrete information have I gathered?
    2. Gap assessment - What crucial information is still missing?
    3. Quality evaluation - Do I have sufficient evidence/examples for a good answer?
    4. Strategic decision - Should I continue searching or provide my answer?

    Args:
        reflection: Your detailed reflection on research progress, findings, gaps, and next steps

    Returns:
        Confirmation that reflection was recorded for decision-making
    """
    return f"Reflection recorded: {reflection}"
```

**Implementation:** Just 1 line!  
**Power:** Everything is in the docstring and system prompt.

### Why It Works

**1. Docstring as Instruction Manual**

The docstring tells the LLM:

- **When** to use it ("after each search")
- **What** to reflect on (4-point structure)
- **Why** it matters ("deliberate pause", "quality decision-making")

**2. System Prompt Reinforcement**

From `RESEARCHER_INSTRUCTIONS`:

```
**CRITICAL: Use think_tool after EACH search to reflect on results and plan next steps**
```

**3. Forced Pause**

To call think_tool, LLM must:

1. Formulate a reflection (think explicitly)
2. Address the 4 points (structured thinking)
3. Make a decision (continue or stop)

**This pause prevents blind searching.**

### Actual Usage Example

**Sub-agent after first search:**

```python
think_tool("""
I found detailed information about Django and Flask frameworks:
- Django: Full-stack, MTV architecture, built-in ORM and admin
- Flask: Lightweight micro-framework, flexible

Gap assessment:
- Still missing: Performance comparisons, production use cases
- Need: Real-world examples of Python web apps at scale

Quality evaluation:
- Have 1 solid source with framework details
- Not enough for comprehensive answer yet

Strategic decision:
- Continue searching
- Next query: 'Python web development performance production examples'
""")
```

**Effect:** LLM explicitly reasons about next steps.

### Comparison: With vs Without think_tool

**Without think_tool:**

```
1. Search "Python web frameworks"
2. Search "Python performance"
3. Search "Python use cases"
4. Search "Python vs other languages"
5. Search "Python production deployments"
... keeps searching without evaluating
```

**With think_tool:**

```
1. Search "Python web frameworks"
2. think_tool("Found Django/Flask. Missing: performance, use cases. Next: search performance")
3. Search "Python performance use cases"
4. think_tool("Have frameworks + performance. 2 sources. Enough to answer. Stop")
5. Return findings
```

**Difference:** Quality-driven (2 searches) vs quantity-driven (5+ searches)

---

## 🎯 Tool Design Lessons

### From tavily_search:

1. **Preserve information**: Full content > summaries
2. **Handle edge cases**: User-Agent, error handling
3. **Format for LLMs**: Markdown > HTML
4. **Document clearly**: Docstring explains purpose and usage

### From think_tool:

1. **Simple can be powerful**: 1-line implementation, huge impact
2. **Docstring is prompt**: LLM reads it to understand usage
3. **System prompt reinforces**: "CRITICAL: Use after EACH..."
4. **Behavioral shaping**: Tool existence changes agent behavior

---

## 💡 Key Takeaways

1. **tavily_search shows**: Complex tools need thoughtful implementation
2. **think_tool shows**: Simple tools can have profound effects
3. **Both show**: Docstrings are critical (LLM reads them)
4. **Design philosophy**: Full info + structured reflection = quality output
5. **Real-world ready**: Error handling, graceful failures, production considerations

---

## 🎉 End of Deep Research Deep Dive

You've now learned:

- ✅ Architecture (3 layers)
- ✅ File structure (3 files, 350 lines)
- ✅ Execution flow (complete trace)
- ✅ Prompt system (3-tier design)
- ✅ Tool implementation (2 tools, 2 philosophies)

**You can now:**

- Build similar research agents
- Extract patterns for other domains
- Customize Deep Research for your use case
- Understand Deep Agents design principles

**Next steps:**

- Apply patterns to your projects
- Explore `deepagents_skills_v2/02_patterns/` for extractable patterns
- Use `deepagents_skills_v2/00_quickstart/templates/` as starting points
