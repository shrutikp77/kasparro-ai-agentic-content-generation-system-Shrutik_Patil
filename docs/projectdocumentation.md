# Multi-Agent Content Generation System — Technical Documentation

This document provides a comprehensive overview of the system architecture, design decisions, and implementation details.

---

## Problem Statement

Traditional content generation approaches often suffer from:

- **Monolithic design** — Data processing, content logic, and formatting tightly coupled in single scripts
- **Poor maintainability** — Changes in one area cascade unpredictably to others
- **Limited reusability** — Adding new content types requires significant rework

Our goal was to build a system where specialized agents work autonomously, coordinated through a clean dependency graph, producing structured content that's easy to extend and maintain.

---

## Solution Approach

We implemented a **LangGraph-based multi-agent system** with the following characteristics:

| Principle | Implementation |
|-----------|----------------|
| Agent Autonomy | Each agent determines its own readiness based on dependency satisfaction |
| Single Responsibility | One agent, one job — no overlap in responsibilities |
| LangGraph Orchestration | StateGraph-based workflow with typed state management |
| Template-Based Output | Standardized output structures with validation |
| LLM-Powered Generation | Groq API for intelligent, context-aware content creation |

---

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   LANGGRAPH ORCHESTRATOR                    │
│   StateGraph-based workflow with typed state management     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │            CONTENT GENERATION STATE                 │   │
│   │   TypedDict shared across all workflow nodes        │   │
│   └─────────────────────────────────────────────────────┘   │
│                            │                                │
│          ┌─────────────────┼─────────────────┐              │
│          ▼                 ▼                 ▼              │
│     ┌─────────┐      ┌──────────┐      ┌──────────┐        │
│     │  Nodes  │      │   LLM    │      │Templates │        │
│     │  (5x)   │      │  Client  │      │   (3x)   │        │
│     └─────────┘      └──────────┘      └──────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Purpose |
|-----------|---------|
| **LangGraph Workflow** | Defines node functions and edges for DAG-based execution |
| **State Schema** | TypedDict defining shared state across all workflow nodes |
| **Orchestrator** | High-level interface wrapping LangGraph workflow execution |
| **Node Functions** | Execute specific content generation tasks (5 nodes) |
| **LLM Client** | Handles API communication, retries, and JSON parsing |
| **Templates** | Validate and structure final outputs |
| **Models** | Pydantic schemas for data validation |

---

## LangGraph Workflow

### State Definition

The workflow uses a typed state schema (`ContentGenerationState`) that flows through all nodes:

```python
class ContentGenerationState(TypedDict, total=False):
    raw_input: Dict[str, Any]           # Input product data
    parsed_product: Optional[Product]    # Parser output
    questions: Optional[List[Question]]  # Question agent output
    faq_output: Optional[Dict[str, Any]]         # FAQ page
    product_output: Optional[Dict[str, Any]]     # Product page
    comparison_output: Optional[Dict[str, Any]]  # Comparison page
```

### Node Functions

Each node wraps agent logic and reads/writes to the shared state:

| Node | Input State Keys | Output State Keys |
|------|------------------|-------------------|
| `parse_product` | `raw_input` | `parsed_product` |
| `generate_questions` | `parsed_product` | `questions` |
| `generate_product_page` | `parsed_product` | `product_output` |
| `generate_comparison_page` | `parsed_product` | `comparison_output` |
| `generate_faq_page` | `parsed_product`, `questions` | `faq_output` |

### Graph Edges

```python
# DAG Structure defined in workflow.py
workflow.add_edge(START, "parse_product")
workflow.add_edge("parse_product", "generate_questions")
workflow.add_edge("parse_product", "generate_product_page")
workflow.add_edge("parse_product", "generate_comparison_page")
workflow.add_edge("generate_questions", "generate_faq_page")
workflow.add_edge("generate_product_page", END)
workflow.add_edge("generate_comparison_page", END)
workflow.add_edge("generate_faq_page", END)
```

---

## Agent Specifications

### 1. Data Parser Node

| Property | Value |
|----------|-------|
| Node Name | `parse_product` |
| Dependencies | None (START node) |
| Input | Raw product JSON from `state["raw_input"]` |
| Output | Validated `Product` Pydantic model |
| LLM Usage | None — performs validation only |

**Purpose**: Serves as the entry point, ensuring all downstream nodes receive clean, validated data. Runs first as it connects directly from START.

---

### 2. Question Generation Node

| Property | Value |
|----------|-------|
| Node Name | `generate_questions` |
| Dependencies | `parse_product` |
| Input | `Product` model from state |
| Output | List of 15 `Question` objects across 5 categories |
| LLM Usage | Generates diverse, natural user questions |

**Purpose**: Creates realistic questions a user might ask about the product. Categories include Informational, Safety, Usage, Purchase, and Comparison.

---

### 3. Product Page Node

| Property | Value |
|----------|-------|
| Node Name | `generate_product_page` |
| Dependencies | `parse_product` |
| Input | `Product` model from state |
| Output | Structured product page dictionary |
| LLM Usage | Generates marketing copy and descriptions |

**Purpose**: Transforms raw product data into compelling marketing content including descriptions, benefits explanations, usage guidance, and safety information.

---

### 4. Comparison Node

| Property | Value |
|----------|-------|
| Node Name | `generate_comparison_page` |
| Dependencies | `parse_product` |
| Input | `Product` model from state |
| Output | Comparison page with two products and analysis |
| LLM Usage | Two calls — generates competitor, then comparative analysis |

**Purpose**: Creates a realistic competitive comparison by first generating a fictional competitor product, then analyzing differences in ingredients, pricing, and effectiveness.

---

### 5. FAQ Generation Node

| Property | Value |
|----------|-------|
| Node Name | `generate_faq_page` |
| Dependencies | `parse_product`, `generate_questions` |
| Input | `Product` model + list of `Question` objects |
| Output | FAQ page with Q&A pairs |
| LLM Usage | Generates helpful, accurate answers |

**Purpose**: Takes the generated questions and produces informative answers based on product data. Runs last due to its dependency on both parser and question node outputs.

---

## Execution Flow

### DAG Structure

```
         ┌─────────┐
         │ Parser  │
         └────┬────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
┌─────────┐ ┌─────────┐ ┌────────────┐
│Questions│ │ Product │ │ Comparison │
└────┬────┘ └────┬────┘ └─────┬──────┘
     │           │            │
     ▼           │            │
 ┌───────┐       │            │
 │  FAQ  │       │            │
 └───┬───┘       │            │
     │           │            │
     └─────────┬─┴────────────┘
               ▼
            [END]
```

### Execution Sequence

1. **Initialization**
   - Create LangGraph StateGraph with 5 nodes
   - Define edges matching dependency structure
   - Compile workflow for execution

2. **Workflow Invocation**
   - Call `workflow.invoke()` with initial state
   - LangGraph automatically handles node ordering
   - State flows through nodes based on edges

3. **Rate Limiting**
   - Each LLM-using node adds delay after execution
   - Configurable via `AGENT_DELAY` environment variable (default: 5s)

4. **Output Collection**
   - Extract outputs from final state
   - Write FAQ, product, and comparison to JSON files

---

## LLM Integration

### Configuration

| Setting | Value |
|---------|-------|
| Provider | Groq Cloud |
| Model | `llama-3.3-70b-versatile` |
| Output Mode | Structured JSON prompts |
| Max Retries | 3 |
| Backoff Strategy | Exponential (10s, 20s, 30s) |
| Inter-Node Delay | 5 seconds (configurable) |

### Error Handling

The LLM client implements several robustness features:

- **Rate limit detection** — Identifies 429 errors and rate-related messages
- **Automatic retry** — Exponential backoff with configurable max attempts
- **JSON extraction** — Regex-based parsing to handle markdown-wrapped responses
- **Response validation** — Ensures valid JSON before returning to nodes

---

## Template System

Templates provide structure and validation for node outputs:

| Template | Required Fields | Output Structure |
|----------|-----------------|------------------|
| FAQTemplate | question, answer for each item | `{page_type, faqs: [{question, answer}]}` |
| ProductTemplate | name, benefits, how_to_use, key_ingredients, price | `{page_type, sections: {...}}` |
| ComparisonTemplate | product_a, product_b, comparison_metrics | `{page_type, products: [], comparison_metrics: []}` |

Templates validate inputs and raise `ValueError` if required fields are missing, preventing malformed outputs.

---

## Test Suite

The system includes a comprehensive test suite using pytest:

| Test Module | Tests | Coverage |
|-------------|-------|----------|
| `test_agents.py` | 18 | Agent initialization, dependencies, can_execute logic |
| `test_content_blocks.py` | 15 | Generator functions, price calculations, ingredient extraction |
| `test_integration.py` | 17 | Templates, orchestrator, LangGraph workflow, schemas |

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_agents.py -v

# Run with coverage
pytest tests/ --cov=src
```

---

## Utility Functions

The `content_blocks/generators.py` module provides deterministic helper functions:

| Function | Purpose |
|----------|---------|
| `extract_product_summary` | Generate one-line product summary |
| `calculate_price_difference` | Compute price delta and percentage |
| `extract_common_ingredients` | Find shared ingredients between products |
| `extract_unique_ingredients` | Identify ingredients unique to one product |
| `generate_content_block` | Create structured content block wrapper |
| `merge_content_blocks` | Combine multiple blocks into single output |

These functions are pure (no LLM calls) and deterministic, suitable for operations where exact reproducibility is needed.

---

## Output Files

| File | Description |
|------|-------------|
| `output/faq.json` | 15 Q&A pairs organized by category |
| `output/product_page.json` | Complete product page with all sections |
| `output/comparison_page.json` | Two-product comparison with detailed metrics |

All outputs are machine-readable JSON, suitable for direct integration with CMS platforms, APIs, or frontend applications.

---

## Running the System

### Prerequisites

- Python 3.10 or higher
- Groq API key

### Setup and Execution

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure API key
echo "GROQ_API_KEY=your_key_here" > .env

# Execute pipeline
python main.py
```

### Expected Output

```
============================================================
Kasparro AI - Agentic Content Generation System
============================================================
Starting multi-agent content generation pipeline...

Product: GlowBoost Vitamin C Serum
Price: ₹699

Agent execution order based on DAG dependencies...
  parser (no deps) → runs first
  questions, product, comparison (dep: parser) → run after parser
  faq (deps: parser, questions) → runs after questions

----------------------------------------
Executing agents...
----------------------------------------
Using model: llama-3.3-70b-versatile
Starting LangGraph workflow execution...
Executing node: parse_product...
Node parse_product completed.
Executing node: generate_questions...
Node generate_questions completed.
Waiting 5s to respect rate limits...
...

  [parser] completed
  [questions] completed
  [faq] completed
  [product] completed
  [comparison] completed

----------------------------------------
Saving outputs to JSON files...
----------------------------------------
  ✓ faq.json
  ✓ product_page.json
  ✓ comparison_page.json

============================================================
All pages generated successfully!
Outputs saved to: output/
============================================================
```

---

## Project Structure

```
kasparro-ai-agentic-content-generation-system/
├── src/
│   ├── __init__.py
│   ├── agents/                    # Agent implementations
│   │   ├── __init__.py
│   │   ├── base_agent.py          # Abstract base class
│   │   ├── parser_agent.py
│   │   ├── question_agent.py
│   │   ├── faq_agent.py
│   │   ├── product_agent.py
│   │   └── comparison_agent.py
│   ├── graph/                     # LangGraph workflow
│   │   ├── __init__.py
│   │   ├── state.py               # TypedDict state schema
│   │   └── workflow.py            # StateGraph definition
│   ├── content_blocks/
│   │   ├── __init__.py
│   │   └── generators.py          # Pure utility functions
│   ├── templates/
│   │   ├── __init__.py
│   │   └── template_definitions.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py             # Pydantic models
│   ├── llm_client.py              # Groq API client
│   ├── orchestrator.py            # LangGraph wrapper
│   └── utils.py
├── tests/
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_content_blocks.py
│   └── test_integration.py
├── output/                        # Generated JSON files
├── docs/
│   └── projectdocumentation.md
├── main.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

## Design Principles

### LangGraph-Based Orchestration

The system uses LangGraph's StateGraph for workflow management:

- **Typed State** — `ContentGenerationState` TypedDict ensures type safety
- **Declarative Edges** — DAG structure defined through `add_edge()` calls
- **Automatic Execution** — LangGraph handles node ordering and state propagation
- **Compiled Workflow** — Graph compiled once, invoked multiple times

### Agent Autonomy

Original agent classes remain for compatibility and implement:

- `can_execute(completed_agents)` — Returns `True` when all dependencies are satisfied
- `execute(shared_data)` — Performs the agent's work and returns output

### Modularity

The system is organized into independent modules:

| Module | Responsibility |
|--------|----------------|
| `src/graph/` | LangGraph state and workflow definitions |
| `src/agents/` | Individual agent implementations |
| `src/models/` | Data validation schemas |
| `src/templates/` | Output structure definitions |
| `src/content_blocks/` | Pure utility functions |
| `src/llm_client.py` | External API abstraction |
| `src/orchestrator.py` | High-level LangGraph wrapper |

This separation allows changes to one component without affecting others.

### Graceful Degradation

The system handles failures without crashing:

- Rate limits trigger automatic retry with backoff
- Missing LLM response fields fall back to defaults
- Template validation catches malformed outputs early

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.10+ |
| Orchestration | LangGraph |
| LLM Provider | Groq Cloud |
| Model | Llama 3.3 70B Versatile |
| Data Validation | Pydantic |
| Testing | pytest |
| Environment | python-dotenv |
| Output Format | JSON |

---

## Summary

This multi-agent system demonstrates how autonomous, specialized agents can collaborate through a LangGraph-orchestrated workflow to produce structured content. The modular design supports extensibility, the DAG structure ensures predictable execution, and the LLM integration enables high-quality content generation.

The architecture prioritizes:
- **Clarity** — Each component has a single, well-defined purpose
- **Reliability** — Error handling and validation at every layer
- **Extensibility** — New nodes can be added with minimal changes
- **Testability** — Comprehensive test suite with 50 tests
