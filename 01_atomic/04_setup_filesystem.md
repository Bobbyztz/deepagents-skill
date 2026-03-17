# Setup File System

> **📋 Prerequisites:** `01_create_orchestrator.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## ⚡ Quick Answer

File system is **enabled by default** in Deep Agents!

```python
agent = create_deep_agent(model=model, system_prompt="...")

# Agent automatically has these tools:
# - ls(path)
# - read_file(path)
# - write_file(path, content)
# - edit_file(path, old, new)
# - glob(pattern)
# - grep(pattern, path)
```

---

## 📖 Why File System?

### Use Cases

1. **Large Results**: Save web search results instead of keeping in context
2. **Communication**: Share data between orchestrator and sub-agents
3. **Persistence**: Keep important outputs for verification
4. **Templates**: Store reusable prompts or formats

### Example Flow

```
User: "Research quantum computing and write a report"

Agent:
1. write_file("/user_request.md", original_query)
2. web_search → large results
3. write_file("/raw_research.md", search_results)
4. Process results
5. write_file("/final_report.md", polished_report)
6. read_file("/user_request.md") to verify coverage
```

---

## 🛠️ Built-in File Tools

### ls(path)

```python
# List directory contents
ls("/")           # Root
ls("/research")   # Subdirectory
```

### read_file(path)

```python
# Read file contents
content = read_file("/notes.md")
```

### write_file(path, content)

```python
# Create or overwrite file
write_file("/report.md", "# My Report\n\nContent here...")
```

### edit_file(path, old, new)

```python
# Replace text in file
edit_file("/report.md", "PLACEHOLDER", "Actual content")
```

### glob(pattern)

```python
# Find files matching pattern
glob("*.md")           # All markdown files
glob("/research/*.md") # Markdown in specific dir
```

### grep(pattern, path)

```python
# Search for text in files
grep("quantum", "/research")  # Find "quantum" in /research
```

---

## 📁 Virtual File System

Files are stored in **LangGraph state**, not on disk:

```python
result = agent.invoke({"messages": [...]})

# Access files from result
files = result["files"]
print(files.keys())        # ['/report.md', '/data.json']
print(files["/report.md"]) # File contents
```

### Custom Backend

For real disk persistence:

```python
from deepagents.backend import FilesystemBackend

backend = FilesystemBackend(root_dir="./workspace")

agent = create_deep_agent(
    model=model,
    backend=backend  # Now writes to ./workspace/
)
```

---

## 🔗 Sharing Files Between Agents

### Option 1: State Passing

```python
def agent_a_node(state):
    result = agent_a.invoke(...)
    return {
        "a_files": result.get("files", {}),
        "a_output": result["messages"][-1].content
    }

def agent_b_node(state):
    # Reference files from state
    files_content = state["a_files"]
    # ...
```

### Option 2: Shared Backend

```python
shared = FilesystemBackend(root_dir="./shared")

agent_a = create_deep_agent(model, backend=shared)
agent_b = create_deep_agent(model, backend=shared)
# Both can read/write to same files
```

---

## 🎯 Best Practices

1. **Organize with directories**: `/research/`, `/drafts/`, `/final/`
2. **Save large results**: Don't keep 10KB search results in messages
3. **Use for verification**: Save request, compare with output
4. **Clear naming**: `/research_quantum_2024.md` not `/temp1.md`

---

## 🔗 Next Steps

**Add planning:**
→ `05_enable_planning.md`

**Long-term memory:**
→ `07_add_long_term_memory.md`

---

## 💡 Key Takeaways

1. File system is **enabled by default**
2. Files are in **LangGraph state** (virtual)
3. Use `backend` for **real disk** persistence
4. Great for **large results** and **cross-agent communication**
