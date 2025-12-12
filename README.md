# Kasparro AI — Multi-Agent Content Generation System

A LangGraph-powered multi-agent system that generates structured content pages from product data using LLM-powered autonomous agents.

## Overview

This system demonstrates how multiple specialized AI agents can collaborate to produce rich content. Given product information, the pipeline generates:

- **FAQ Pages** — 15 categorized Q&As addressing common customer concerns
- **Product Pages** — Compelling descriptions with benefits, usage, and safety information
- **Comparison Pages** — Competitive analysis with auto-generated competitor benchmarking

The architecture emphasizes **agent autonomy**, **modular design**, and **clean dependency management** through LangGraph-based orchestration.

---

## Key Features

| Feature | Description |
|---------|-------------|
| LangGraph Orchestration | StateGraph-based workflow with typed state management and declarative edges |
| Autonomous Agents | Each agent independently determines when to execute based on dependency satisfaction |
| LLM Integration | Powered by Groq's Llama 3.3 70B for fast, high-quality content generation |
| Comprehensive Tests | 50 pytest tests covering agents, generators, and integration workflows |
| Modular Architecture | Easily swap agents, templates, or LLM providers without system-wide changes |
| Production-Ready | Built-in rate limiting, retry logic, and graceful error handling |

---

## Project Structure

```
├── main.py                     # Application entry point
├── src/
│   ├── orchestrator.py         # LangGraph workflow wrapper
│   ├── llm_client.py           # Groq API integration
│   ├── utils.py                # Utility functions
│   ├── graph/                  # LangGraph workflow
│   │   ├── state.py            # TypedDict state schema
│   │   └── workflow.py         # StateGraph definition
│   ├── agents/                 # Agent implementations
│   │   ├── base_agent.py       # Abstract base class
│   │   ├── parser_agent.py     # Data validation agent
│   │   ├── question_agent.py   # Question generation agent
│   │   ├── faq_agent.py        # FAQ generation agent
│   │   ├── product_agent.py    # Product page agent
│   │   └── comparison_agent.py # Comparison agent
│   ├── models/                 # Pydantic data schemas
│   ├── templates/              # Output structure templates
│   └── content_blocks/         # Utility generators
├── tests/                      # Test suite
│   ├── test_agents.py          # Agent unit tests
│   ├── test_content_blocks.py  # Generator function tests
│   └── test_integration.py     # End-to-end workflow tests
├── output/                     # Generated JSON files
└── docs/                       # Documentation
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- Groq API key ([Get one free](https://console.groq.com/))

### Installation

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
echo "GROQ_API_KEY=your_api_key_here" > .env

# Run the pipeline
python main.py
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test module
pytest tests/test_agents.py -v
```

### Output

After execution, check the `output/` directory for:

| File | Contents |
|------|----------|
| `faq.json` | 15 Q&As across 5 categories (Informational, Safety, Usage, Purchase, Comparison) |
| `product_page.json` | Complete product page with all content sections |
| `comparison_page.json` | Side-by-side comparison with generated competitor analysis |

---

## Architecture

### LangGraph Workflow

The system uses LangGraph's StateGraph to orchestrate agent execution. Each node in the graph represents an agent, and edges define the dependency structure.

```
         ┌─────────┐
         │ Parser  │  ← START node (no dependencies)
         └────┬────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
┌─────────┐ ┌─────────┐ ┌────────────┐
│Questions│ │ Product │ │ Comparison │  ← Depend on Parser
└────┬────┘ └────┬────┘ └─────┬──────┘
     │           │            │
     ▼           └──────┬─────┘
 ┌───────┐              │
 │  FAQ  │              │
 └───┬───┘              │
     └────────┬─────────┘
              ▼
            [END]
```

### State Management

The workflow uses a `ContentGenerationState` TypedDict to share data between nodes:

```python
class ContentGenerationState(TypedDict, total=False):
    raw_input: Dict[str, Any]
    parsed_product: Optional[Product]
    questions: Optional[List[Question]]
    faq_output: Optional[Dict[str, Any]]
    product_output: Optional[Dict[str, Any]]
    comparison_output: Optional[Dict[str, Any]]
```

### Agent Summary

| Agent | Dependencies | Purpose | Uses LLM |
|-------|--------------|---------|----------|
| DataParserAgent | None | Validates product data into Pydantic model | No |
| QuestionGenerationAgent | Parser | Generates 15 diverse user questions | Yes |
| ProductPageAgent | Parser | Creates marketing copy and product descriptions | Yes |
| ComparisonAgent | Parser | Generates competitor product and analysis | Yes |
| FAQGenerationAgent | Parser, Questions | Produces answers for generated questions | Yes |

---

## Test Coverage

The project includes a comprehensive test suite:

| Test Module | Tests | Coverage |
|-------------|-------|----------|
| `test_agents.py` | 18 | Agent initialization, dependencies, can_execute logic |
| `test_content_blocks.py` | 15 | Generator functions, price calculations |
| `test_integration.py` | 17 | Templates, orchestrator, LangGraph workflow |

---

## Documentation

For detailed architecture documentation, design decisions, and implementation details, see:

**[docs/projectdocumentation.md](docs/projectdocumentation.md)**

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.10+ |
| Orchestration | LangGraph |
| LLM Provider | Groq Cloud |
| Model | Llama 3.3 70B Versatile |
| Data Validation | Pydantic |
| Testing | pytest |
| Environment Management | python-dotenv |

---

## Notes

- **Rate Limits**: The system includes automatic retry with exponential backoff for API rate limits
- **Customization**: Modify product data in `main.py` to generate content for different products
- **Extensibility**: The modular design supports adding new agents with minimal changes to existing code
- **Configuration**: Rate limiting delay is configurable via `AGENT_DELAY` environment variable (default: 5 seconds)
