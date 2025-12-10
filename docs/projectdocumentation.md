# Multi-Agent Content Generation System

## Problem Statement

Traditional content generation systems often rely on monolithic scripts that tightly couple data processing, content logic, and output formatting. This approach becomes difficult to maintain, extend, and test as complexity grows.

**The Challenge:** Generate structured content pages (FAQ, Product, Comparison) from product data using an autonomous multi-agent system that allows for parallel execution, clear separation of concerns, and scalable architecture.

---

## Solution Overview

We built a **DAG-based multi-agent system** where 5 specialized agents autonomously execute based on dependency satisfaction. Each agent has a single responsibility and communicates with others via shared state.

**Key Characteristics:**
- Autonomous execution based on dependency graph
- Parallel processing where dependencies allow
- Shared data state for inter-agent communication
- Reusable content logic blocks
- Template-based output generation
- Deterministic, reproducible outputs

---

## Scopes & Assumptions

| Scope | Description |
|-------|-------------|
| **Input** | Single product (GlowBoost Vitamin C Serum) |
| **Data Sources** | No external APIs or databases |
| **Content Generation** | Deterministic (no LLMs, no randomness) |
| **Output Format** | Machine-readable JSON files |
| **Execution Model** | Autonomous DAG-based agent orchestration |

---

## System Design

### Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                   AgentOrchestrator                      │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Shared Data State                      │ │
│  │   raw_input → parser → questions → faq/product     │ │
│  └─────────────────────────────────────────────────────┘ │
│                          │                               │
│    ┌─────────────────────┼─────────────────────┐        │
│    │                     │                     │        │
│    ▼                     ▼                     ▼        │
│ ┌────────┐  ┌────────────────┐  ┌──────────────────┐   │
│ │ Agents │  │ Content Blocks │  │    Templates     │   │
│ └────────┘  └────────────────┘  └──────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

**Core Components:**
- **5 Autonomous Agents** - Each with clear, single responsibility
- **DAG Executor** - Orchestrates based on declared dependencies
- **Shared Data State** - Enables inter-agent communication
- **Content Logic Blocks** - Reusable content generation functions
- **Templates** - Standardized output structure generation

---

### Agent Specifications

#### 1. Data Parser Agent
| Property | Value |
|----------|-------|
| **ID** | `parser` |
| **Dependencies** | None |
| **Input** | Raw product JSON |
| **Output** | Validated Product model |
| **Executes** | Immediately (first agent) |

#### 2. Question Generation Agent
| Property | Value |
|----------|-------|
| **ID** | `questions` |
| **Dependencies** | `[parser]` |
| **Input** | Product model |
| **Output** | 15+ categorized questions |
| **Executes** | After parser completes |

#### 3. FAQ Generation Agent
| Property | Value |
|----------|-------|
| **ID** | `faq` |
| **Dependencies** | `[parser, questions]` |
| **Input** | Product + Questions |
| **Output** | FAQ page JSON |
| **Executes** | After parser AND questions |

#### 4. Product Page Agent
| Property | Value |
|----------|-------|
| **ID** | `product` |
| **Dependencies** | `[parser]` |
| **Input** | Product model |
| **Output** | Product page JSON |
| **Executes** | After parser (parallel with questions) |

#### 5. Comparison Agent
| Property | Value |
|----------|-------|
| **ID** | `comparison` |
| **Dependencies** | `[parser]` |
| **Input** | Product model |
| **Output** | Comparison page JSON |
| **Executes** | After parser (parallel with others) |

---

### DAG Structure

```
         ┌─────────┐
         │ Parser  │  ← No dependencies, runs first
         └────┬────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
┌─────────┐ ┌─────────┐ ┌────────────┐
│Questions│ │ Product │ │ Comparison │  ← All depend on Parser
└────┬────┘ └─────────┘ └────────────┘    (can run in parallel)
     │
     ▼
 ┌───────┐
 │  FAQ  │  ← Depends on Parser + Questions
 └───────┘
```

**Execution Order:**
1. Parser executes (no dependencies)
2. Questions, Product, Comparison execute in parallel
3. FAQ executes after Questions completes

---

### Content Logic Blocks

Seven reusable, pure functions that take structured data and return formatted content:

| Block | Input | Output |
|-------|-------|--------|
| `generate_benefits_block` | Product | Benefits description string |
| `generate_usage_block` | Product | Usage instructions string |
| `generate_safety_block` | Product | Safety/side effects string |
| `generate_ingredients_block` | Product | Ingredients description string |
| `compare_ingredients_block` | Product A, B | Ingredients comparison dict |
| `compare_price_block` | Product A, B | Price/value comparison dict |
| `generate_answer_block` | Question, Product | Context-aware answer string |

---

### Template System

Three template classes that structure final output:

| Template | Purpose | Output Structure |
|----------|---------|------------------|
| **FAQTemplate** | Structures Q&A pairs | `{page_type, faqs: [{question, answer}]}` |
| **ProductTemplate** | Structures product sections | `{page_type, sections: {name, benefits, usage...}}` |
| **ComparisonTemplate** | Structures comparisons | `{page_type, products: [], comparison_metrics: []}` |

---

### Orchestration Flow

```
1. Initialize    → Create all 5 agent instances
                 → Initialize shared_data dictionary

2. Load Data     → Add raw_product_data to shared_data["raw_input"]

3. Execute DAG   → While not all agents completed:
                    → Find agents with satisfied dependencies
                    → Execute those agents
                    → Store outputs in shared_data[agent_id]
                    → Mark agents as completed

4. Collect       → Gather outputs: faq, product, comparison

5. Output        → Write JSON files to output/ directory
```

---

## Output Files

| File | Content |
|------|---------|
| `output/faq.json` | FAQ page with 5 Q&A pairs |
| `output/product_page.json` | Complete product information |
| `output/comparison_page.json` | Product comparison data |

---

## Running the System

```bash
# Install dependencies
pip install -r requirements.txt

# Run the pipeline
python main.py
```

**Expected Console Output:**
```
============================================================
Kasparro AI - Agentic Content Generation System
============================================================
Starting multi-agent content generation pipeline...
Agent execution order based on DAG dependencies...
All pages generated successfully!
Outputs saved to: output/
============================================================
```
