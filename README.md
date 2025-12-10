# 🚀 Kasparro AI - Multi-Agent Content Generation System

> *"Let intelligent agents do the heavy lifting."*

Ever wondered what happens when you let AI agents work together like a team? This project is exactly that — a **smart, collaborative system** where 5 specialized AI agents generate rich content pages from simple product data.

Give it a product, and it'll create:
- 📋 **FAQ pages** with 15 thoughtful Q&As
- 📦 **Product pages** with compelling descriptions
- ⚖️ **Comparison pages** with competitor analysis

All powered by **Groq's blazing-fast LLM** (Llama 3.3 70B) and orchestrated through a clean DAG pipeline.

---

## ✨ What Makes This Special?

| Feature | Why It Matters |
|---------|---------------|
| **Autonomous Agents** | Each agent thinks for itself — knows when to run based on what others have done |
| **DAG Orchestration** | No tangled dependencies. Clean, predictable execution order |
| **LLM-Powered** | Groq's Llama 3.3 70B generates human-quality content in seconds |
| **Modular Design** | Swap out agents, templates, or the LLM provider without breaking anything |
| **Production-Ready** | Rate limiting, retries, error handling — it's all built in |

---

## 📁 Project Structure

```
📦 kasparro-ai-content-generation/
├── 🎯 main.py                    # Start here — runs the whole pipeline
├── 📂 src/
│   ├── 🎭 orchestrator.py        # The conductor — coordinates all agents
│   ├── 🤖 llm_client.py          # Talks to Groq's API
│   ├── 🛠️ utils.py               # Helper functions
│   ├── 📂 agents/                # The team of 5 specialists
│   │   ├── base_agent.py         # What every agent inherits
│   │   ├── parser_agent.py       # Validates & structures data
│   │   ├── question_agent.py     # Generates smart questions
│   │   ├── faq_agent.py          # Answers those questions
│   │   ├── product_agent.py      # Creates product copy
│   │   └── comparison_agent.py   # Builds competitor comparisons
│   ├── 📂 models/                # Pydantic schemas
│   ├── 📂 templates/             # Output formatters
│   └── 📂 content_blocks/        # Utility generators
├── 📂 output/                    # Where the magic lands
└── 📂 docs/                      # You're reading part of this!
```

---

## 🏃 Quick Start

### 1️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Add your Groq API key
Create a `.env` file:
```
GROQ_API_KEY=your_api_key_here
```
👉 Get one free at [console.groq.com](https://console.groq.com/)

### 3️⃣ Run it!
```bash
python main.py
```

That's it! Check the `output/` folder for your generated content.

---

## 🔄 How It Works (The Agent DAG)

Think of it like a relay race — each agent waits for the right moment to run:

```
     🏁 START
         │
    ┌────▼────┐
    │ Parser  │  ← First up: validates the product data
    └────┬────┘
         │
    ┌────┴────┬─────────────┐
    ▼         ▼             ▼
┌─────────┐ ┌─────────┐ ┌────────────┐
│Questions│ │ Product │ │ Comparison │  ← These three can run together
└────┬────┘ └─────────┘ └────────────┘
     │
     ▼
 ┌───────┐
 │  FAQ  │  ← Waits for Questions to finish first
 └───────┘
     │
     ▼
   🏆 DONE
```

| Agent | Waits For | What It Does |
|-------|-----------|--------------|
| **Parser** | Nothing | Validates product data into a clean model |
| **Questions** | Parser | Generates 15 diverse user questions |
| **Product** | Parser | Creates compelling product page copy |
| **Comparison** | Parser | Builds a competitor product + analysis |
| **FAQ** | Parser + Questions | Answers all those questions |

---

## 📄 What You Get

Three beautifully structured JSON files in `output/`:

| File | What's Inside |
|------|---------------|
| `faq.json` | 15 Q&As covering safety, usage, benefits, and more |
| `product_page.json` | Full product page with descriptions, benefits, usage tips |
| `comparison_page.json` | Side-by-side comparison with a generated competitor |

---

## 📚 Learn More

Curious about the architecture? Check out the full documentation:
- 📖 [`docs/projectdocumentation.md`](docs/projectdocumentation.md)

---

## 🛠️ Tech Stack

- **Python 3.8+** — the foundation
- **Groq Cloud** — for lightning-fast LLM inference
- **Llama 3.3 70B** — the brain behind the content
- **Pydantic** — keeping data clean and validated
- **python-dotenv** — for safe API key management

---

## 💡 Pro Tips

1. **Rate limits got you down?** The system automatically waits and retries. Just be patient.
2. **Want different content?** Edit the product data in `main.py` and run again.
3. **Building on this?** The modular design makes it easy to add new agents!

---
