# Production Deployment Guide

> **📋 Prerequisites:**
>
> - `03_persistence_guide.md`
> - `05_streaming_guide.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## 🎯 Overview

Production deployment checklist:

- ✅ Persistent checkpointer (PostgreSQL)
- ✅ Error handling & retry
- ✅ Logging & monitoring
- ✅ Rate limiting
- ✅ Security considerations
- ✅ Scaling strategies

---

## 📦 Production Checkpointer

### PostgreSQL Setup

```python
# pip install langgraph-checkpoint-postgres

from langgraph.checkpoint.postgres import PostgresSaver

# From connection string
checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:password@localhost:5432/langgraph_db"
)

# Initialize tables
checkpointer.setup()

# Compile with checkpointer
graph = builder.compile(checkpointer=checkpointer)
```

### Async PostgreSQL

```python
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

checkpointer = await AsyncPostgresSaver.from_conn_string(
    "postgresql://user:password@localhost:5432/langgraph_db"
)
await checkpointer.setup()

graph = builder.compile(checkpointer=checkpointer)

# Use async
result = await graph.ainvoke(input, config)
```

### Connection Pooling

```python
import asyncpg

# Create connection pool
pool = await asyncpg.create_pool(
    "postgresql://user:password@localhost:5432/langgraph_db",
    min_size=5,
    max_size=20
)

checkpointer = AsyncPostgresSaver(pool)
```

---

## 🔒 Security

### Encryption at Rest

```python
from langgraph.checkpoint.serde.encrypted import EncryptedSerializer

# Set environment variable: LANGGRAPH_AES_KEY
serde = EncryptedSerializer.from_pycryptodome_aes()

checkpointer = PostgresSaver.from_conn_string(
    "postgresql://...",
    serde=serde
)
```

### Input Validation

```python
from pydantic import BaseModel, validator

class UserInput(BaseModel):
    query: str
    user_id: str

    @validator("query")
    def validate_query(cls, v):
        if len(v) > 10000:
            raise ValueError("Query too long")
        return v

def validated_invoke(graph, input_data: dict, config: dict):
    # Validate input
    validated = UserInput(**input_data)

    return graph.invoke(
        {"messages": [HumanMessage(content=validated.query)]},
        config
    )
```

### API Key Management

```python
import os
from functools import lru_cache

@lru_cache()
def get_model():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")

    return init_chat_model(
        "anthropic:claude-sonnet-4-5-20250929",
        api_key=api_key
    )
```

---

## 🔄 Error Handling & Retry

### Retry Policy

```python
from langgraph.types import RetryPolicy

# Node with retry
builder.add_node(
    "api_call",
    api_call_node,
    retry=RetryPolicy(
        max_attempts=3,
        initial_interval=1.0,
        backoff_multiplier=2.0,
        max_interval=10.0
    )
)
```

### Global Error Handling

```python
def safe_invoke(graph, input_data, config, max_retries=3):
    """Invoke with retry and error handling."""
    import time

    for attempt in range(max_retries):
        try:
            return graph.invoke(input_data, config)
        except Exception as e:
            if attempt == max_retries - 1:
                raise

            wait_time = 2 ** attempt
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
            time.sleep(wait_time)
```

### Graceful Degradation

```python
def node_with_fallback(state):
    try:
        # Primary path
        result = expensive_operation(state)
    except Exception as e:
        # Fallback path
        logger.error(f"Primary failed: {e}, using fallback")
        result = fallback_operation(state)

    return {"result": result}
```

---

## 📊 Logging & Monitoring

### Structured Logging

```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)

    def log(self, level, message, **kwargs):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            **kwargs
        }
        getattr(self.logger, level)(json.dumps(log_data))

logger = StructuredLogger("langgraph_app")

def monitored_node(state, config):
    start_time = time.time()
    thread_id = config["configurable"]["thread_id"]

    try:
        result = process(state)

        logger.log("info", "Node completed",
            node="monitored_node",
            thread_id=thread_id,
            duration_ms=(time.time() - start_time) * 1000
        )

        return result
    except Exception as e:
        logger.log("error", "Node failed",
            node="monitored_node",
            thread_id=thread_id,
            error=str(e)
        )
        raise
```

### Metrics

```python
from prometheus_client import Counter, Histogram

# Metrics
invocations = Counter("graph_invocations_total", "Total invocations", ["graph_name"])
duration = Histogram("graph_duration_seconds", "Invocation duration", ["graph_name"])
errors = Counter("graph_errors_total", "Total errors", ["graph_name", "error_type"])

def instrumented_invoke(graph, graph_name, input_data, config):
    invocations.labels(graph_name=graph_name).inc()

    with duration.labels(graph_name=graph_name).time():
        try:
            return graph.invoke(input_data, config)
        except Exception as e:
            errors.labels(graph_name=graph_name, error_type=type(e).__name__).inc()
            raise
```

---

## ⚡ Performance

### Recursion Limits

```python
# Set sensible limits
result = graph.invoke(
    input_data,
    {
        **config,
        "recursion_limit": 25  # Prevent infinite loops
    }
)
```

### Timeout

```python
import asyncio

async def invoke_with_timeout(graph, input_data, config, timeout=60):
    try:
        return await asyncio.wait_for(
            graph.ainvoke(input_data, config),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        raise TimeoutError(f"Graph execution exceeded {timeout}s")
```

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_embedding(text: str) -> list[float]:
    return embedder.embed(text)
```

---

## 🌐 Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  langgraph-worker:
    image: your-app:latest
    deploy:
      replicas: 4
    environment:
      - DATABASE_URL=postgresql://...
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
```

### Queue-based Processing

```python
import redis
import json

redis_client = redis.Redis()

def enqueue_task(task_data):
    redis_client.lpush("langgraph_tasks", json.dumps(task_data))

def worker():
    while True:
        _, task_json = redis_client.brpop("langgraph_tasks")
        task = json.loads(task_json)

        result = graph.invoke(
            task["input"],
            {"configurable": {"thread_id": task["thread_id"]}}
        )

        # Store result
        redis_client.set(f"result:{task['task_id']}", json.dumps(result))
```

---

## 🧪 Testing

### Unit Tests

```python
import pytest
from unittest.mock import patch

def test_node_function():
    state = {"query": "test"}
    result = my_node(state)
    assert "result" in result

@patch("myapp.model.invoke")
def test_with_mocked_llm(mock_invoke):
    mock_invoke.return_value = AIMessage(content="Mocked response")

    result = graph.invoke({"messages": [HumanMessage("Hi")]}, config)

    assert "Mocked" in result["messages"][-1].content
```

### Integration Tests

```python
def test_full_workflow():
    # Use in-memory checkpointer for tests
    checkpointer = MemorySaver()
    test_graph = builder.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "test-123"}}

    result = test_graph.invoke({"query": "test"}, config)

    assert result["status"] == "completed"
```

---

## 🔗 Next Steps

**Memory management:**
→ `04_memory_guide.md`

**Migration from V1:**
→ `07_migration_guide.md`

---

## 💡 Production Checklist

- [ ] PostgreSQL checkpointer configured
- [ ] Encryption enabled (LANGGRAPH_AES_KEY)
- [ ] Input validation implemented
- [ ] Retry policies on external calls
- [ ] Structured logging enabled
- [ ] Metrics collection configured
- [ ] Recursion limits set
- [ ] Timeouts configured
- [ ] Tests passing
- [ ] Monitoring dashboards ready
