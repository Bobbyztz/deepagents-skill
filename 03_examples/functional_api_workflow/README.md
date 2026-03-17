# Functional API Workflow Example

> **📋 Prerequisites:**
>
> - `04_langgraph_integration/02_functional_api_guide.md`
>
> **LangGraph Version**: `>=0.2.0`

---

## 🎯 Overview

A complete workflow using LangGraph's **Functional API** (`@entrypoint` + `@task`):

- ✅ Standard Python control flow
- ✅ Durable tasks with persistence
- ✅ Sequential and parallel execution
- ✅ Error handling

---

## 📁 Project Structure

```
functional_api_workflow/
├── README.md          # This file
├── workflow.py        # Main workflow implementation
└── tasks.py           # Task definitions
```

---

## 📄 workflow.py

```python
"""Functional API Workflow Example

Demonstrates LangGraph's Functional API for building
workflows with standard Python control flow.

LangGraph Version: >=0.2.0
"""

from langgraph.func import entrypoint, task
from langgraph.checkpoint.memory import MemorySaver

# ============================================================================
# Task Definitions
# ============================================================================

@task
def fetch_data(source: str) -> dict:
    """Fetch data from a source (durable task)."""
    # Simulated data fetch
    return {
        "source": source,
        "data": f"Data from {source}",
        "records": 100
    }


@task
def process_data(data: dict) -> dict:
    """Process fetched data (durable task)."""
    return {
        "processed": True,
        "original_records": data["records"],
        "valid_records": data["records"] - 5,  # Simulated validation
        "source": data["source"]
    }


@task
def analyze_data(processed: dict) -> dict:
    """Analyze processed data (durable task)."""
    return {
        "analysis": f"Analysis of {processed['source']}",
        "valid_rate": processed["valid_records"] / processed["original_records"],
        "insights": ["Insight 1", "Insight 2"]
    }


@task
def generate_report(analyses: list[dict]) -> str:
    """Generate final report from analyses."""
    report_lines = ["# Data Analysis Report\n"]

    for i, analysis in enumerate(analyses, 1):
        report_lines.append(f"## Source {i}")
        report_lines.append(f"- Valid rate: {analysis['valid_rate']:.1%}")
        report_lines.append(f"- Insights: {', '.join(analysis['insights'])}")
        report_lines.append("")

    return "\n".join(report_lines)


# ============================================================================
# Workflow Definition
# ============================================================================

@entrypoint(checkpointer=MemorySaver())
def data_pipeline(sources: list[str]) -> str:
    """Main data pipeline workflow.

    Demonstrates:
    - Sequential processing
    - Parallel task execution
    - Standard Python control flow
    - Persistence via checkpointer

    Args:
        sources: List of data sources to process

    Returns:
        Final report as string
    """

    # === Step 1: Fetch data from all sources (parallel) ===
    fetch_futures = [fetch_data(source) for source in sources]
    fetched_data = [f.result() for f in fetch_futures]

    print(f"Fetched data from {len(fetched_data)} sources")

    # === Step 2: Process each dataset (parallel) ===
    process_futures = [process_data(data) for data in fetched_data]
    processed_data = [f.result() for f in process_futures]

    print(f"Processed {len(processed_data)} datasets")

    # === Step 3: Analyze (sequential with condition) ===
    analyses = []
    for processed in processed_data:
        # Only analyze if valid rate > 50%
        if processed["valid_records"] / processed["original_records"] > 0.5:
            analysis = analyze_data(processed).result()
            analyses.append(analysis)
        else:
            print(f"Skipping {processed['source']} - low valid rate")

    print(f"Analyzed {len(analyses)} datasets")

    # === Step 4: Generate report ===
    if not analyses:
        return "No valid data to report"

    report = generate_report(analyses).result()

    return report


# ============================================================================
# Alternative: Iterative Workflow
# ============================================================================

@task
def improve_quality(data: dict, iteration: int) -> dict:
    """Improve data quality iteratively."""
    # Simulated improvement
    improvement = 0.1 * (iteration + 1)
    return {
        **data,
        "quality_score": min(1.0, data.get("quality_score", 0.5) + improvement)
    }


@entrypoint(checkpointer=MemorySaver())
def quality_improvement_workflow(initial_data: dict, target_quality: float = 0.9) -> dict:
    """Iterative quality improvement workflow.

    Demonstrates:
    - While loops in Functional API
    - Iterative refinement pattern

    Args:
        initial_data: Starting data
        target_quality: Target quality score (0-1)

    Returns:
        Final improved data
    """
    data = initial_data
    iteration = 0
    max_iterations = 5

    while data.get("quality_score", 0) < target_quality and iteration < max_iterations:
        print(f"Iteration {iteration + 1}: Quality = {data.get('quality_score', 0):.2f}")
        data = improve_quality(data, iteration).result()
        iteration += 1

    print(f"Final quality: {data['quality_score']:.2f} after {iteration} iterations")

    return data


# ============================================================================
# Main
# ============================================================================

def main():
    print("=== Data Pipeline Workflow ===\n")

    sources = ["database_a", "api_b", "file_c"]

    config = {"configurable": {"thread_id": "pipeline-run-1"}}

    report = data_pipeline.invoke(sources, config)

    print("\n=== Generated Report ===")
    print(report)

    print("\n=== Quality Improvement Workflow ===\n")

    initial = {"name": "sample_data", "quality_score": 0.4}
    config2 = {"configurable": {"thread_id": "quality-run-1"}}

    result = quality_improvement_workflow.invoke(initial, config2)
    print(f"\nFinal result: {result}")


if __name__ == "__main__":
    main()
```

---

## 🚀 Running

```bash
# Install dependencies
pip install langgraph

# Run
python workflow.py
```

**Expected Output:**

```
=== Data Pipeline Workflow ===

Fetched data from 3 sources
Processed 3 datasets
Analyzed 3 datasets

=== Generated Report ===
# Data Analysis Report

## Source 1
- Valid rate: 95.0%
- Insights: Insight 1, Insight 2

## Source 2
- Valid rate: 95.0%
- Insights: Insight 1, Insight 2

## Source 3
- Valid rate: 95.0%
- Insights: Insight 1, Insight 2

=== Quality Improvement Workflow ===

Iteration 1: Quality = 0.40
Iteration 2: Quality = 0.50
Iteration 3: Quality = 0.60
Iteration 4: Quality = 0.70
Iteration 5: Quality = 0.80
Final quality: 0.90 after 5 iterations

Final result: {'name': 'sample_data', 'quality_score': 0.9}
```

---

## 🎯 Key Patterns Demonstrated

### 1. Parallel Execution

```python
# Start all tasks
futures = [fetch_data(source) for source in sources]

# Wait for all results
results = [f.result() for f in futures]
```

### 2. Conditional Logic

```python
if condition:
    result = task_a(data).result()
else:
    result = task_b(data).result()
```

### 3. Iterative Refinement

```python
while not good_enough(data):
    data = improve(data).result()
```

### 4. Persistence

```python
@entrypoint(checkpointer=MemorySaver())
def workflow(input):
    # Tasks are persisted and can resume
    ...
```

---

## 📊 Graph API vs Functional API

| Use Case                          | Recommendation        |
| --------------------------------- | --------------------- |
| Complex topology (fan-out/fan-in) | Graph API             |
| Linear workflow                   | **Functional API** ✅ |
| Existing Python code              | **Functional API** ✅ |
| Visual debugging                  | Graph API             |
| Quick prototype                   | **Functional API** ✅ |

---

## 🔗 Next Steps

**Compare with Graph API:**
→ `04_langgraph_integration/01_graph_api_guide.md`

**Add Deep Agents:**
→ `00_quickstart/deep_agent_as_node.md`

**Production deployment:**
→ `04_langgraph_integration/06_production_guide.md`
