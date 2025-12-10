# Multi-Agent Content Generation System

A DAG-based multi-agent system that generates structured content pages from product data.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Output

Three JSON files are generated in `output/`:

- `faq.json` - FAQ page with 5+ Q&As
- `product_page.json` - Complete product page  
- `comparison_page.json` - Product comparison

## Architecture

- 5 autonomous agents with DAG-based orchestration
- Reusable content logic blocks
- Template-based generation
- Machine-readable JSON output

## Documentation

See `docs/projectdocumentation.md` for complete system design.
