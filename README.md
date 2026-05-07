# AI Interior Design Copilot

An AI-powered interior design web application that generates room designs from text descriptions, recommends matching furniture products, and provides budget-optimized shopping recommendations - all in a single Streamlit app.

## Features

- **AI Design Generation**: Describe any room and get photorealistic AI-generated interior designs using Stable Diffusion XL
- **Smart Prompt Optimization**: Groq LLM enhances vague descriptions into detailed image generation prompts
- **Visual Product Matching**: CLIP-powered similarity search finds furniture that matches your generated design
- **Budget Optimization**: Smart allocation algorithm fits recommendations within budget
- **RAG-Powered Design Advice**: Get expert interior design explanations based on 40+ design principles
- **Conversational Refinement**: Chat with AI to refine your design (make it brighter, reduce cost, etc.)
- **Save & Export**: Save designs locally with SQLite and export as reports

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| Image Generation | HuggingFace Inference API (SDXL) |
| LLM | Groq (llama-3.1-8b-instant) |
| Text Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Image Embeddings | open_clip_torch (ViT-B-32) |
| Vector DB | ChromaDB |
| Knowledge Base | FAISS |
| Database | SQLite (via SQLAlchemy) |
| Storage | Local filesystem |

## Setup Instructions

### 1. Clone and Install

```bash
# Navigate to project directory
cd ai-interior-copilot

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

You need:
- **GROQ_API_KEY**: Get free from [Groq Console](https://console.groq.com)
- **HF_TOKEN**: Get free from [HuggingFace Settings](https://huggingface.co/settings/tokens)

### 3. Seed Data

```bash
python data/seed_products.py
```

This creates:
- ChromaDB vector index with 60 furniture products
- FAISS index with 40 interior design principles

### 4. Run the App

```bash
streamlit run app.py
```

## Usage

1. **Generate**: Describe your room (e.g., "cozy living room with plants and natural light")
2. **Results**: View AI-generated design and product recommendations
3. **Refine**: Chat with AI to adjust the design
4. **Save**: Save designs for later

## Project Structure

```
ai-interior-copilot/
├── app.py                    # Main entry point
├── config.py                # Configuration
├── requirements.txt        # Dependencies
├── core/                  # Core modules
│   ├── clip_embedder.py    # CLIP embeddings
│   ├── prompt_optimizer.py # Groq prompt optimization
│   ├── image_generator.py # HuggingFace SDXL
│   ├── product_retriever.py # ChromaDB search
│   ├── budget_optimizer.py # Budget allocation
│   └── rag_assistant.py   # FAISS RAG
├── data/                  # Data files
│   ├── products.json       # 60 products
│   ├── design_knowledge.json # 40 principles
│   └── seed_products.py  # Seeding script
├── db/                   # Database
│   ├── models.py
│   └── database.py
└── pages/                 # Streamlit pages
    ├── 1_Generate.py
    ├── 2_Results.py
    └── 3_Saved_Designs.py
```

## Screenshots

[Add screenshots here]

## API Requirements

| Service | Cost | Notes |
| --- | --- | --- |
| Groq | Free | Get key at console.groq.com |
| HuggingFace Inference API | Free | Get token at huggingface.co/settings/tokens |
| ChromaDB | Free | Local only |
| FAISS | Free | Local only |

## Troubleshooting

- **No images generate**: Check HF_TOKEN in .env
- **No products found**: Run `python data/seed_products.py`
- **No design explanations**: Check GROQ_API_KEY in .env
- **Slow embedding**: Requires GPU for best performance

## License

MIT