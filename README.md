# Financial Counseling Platform

An AI-powered case management system that helps financial counselors match people with the right assistance programs. Built with FastAPI, React, and ChromaDB for semantic search.

## What It Does

This platform helps case workers manage people who are struggling financially. Instead of manually searching through dozens of assistance programs, the AI recommends the best matches based on someone's financial situation, uploaded documents, and urgency level.

Key features:
- Recommends financial assistance programs using vector search
- Analyzes incoming messages for urgency and sentiment
- Extracts text from uploaded documents (PDFs, Word docs) to improve recommendations
- Provides real-time writing suggestions for case workers
- Shows analytics and patterns across all cases

## Tech Stack

Backend:
- FastAPI for the API
- ChromaDB as the vector database
- Sentence Transformers for text embeddings
- Server-Sent Events for streaming responses

Frontend:
- React with TypeScript
- Vite for build tooling
- Standard fetch API for requests

## How to Run It

### Backend Setup
```bash
cd backend

# Create environment
conda create -n finance python=3.11 -y
conda activate finance

# Install dependencies
pip install fastapi uvicorn python-multipart pydantic chromadb PyPDF2 python-docx pillow pytesseract sentence-transformers python-dotenv pdf2image

# You also need poppler for PDF processing
brew install poppler

# Create .env file with your API key
echo 'GROQ_API_KEY=your_key_here' > .env

# Run the server
python3 main.py
```

Backend runs on http://localhost:8000

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

Frontend runs on http://localhost:5173

## How It Works

The recommendation system uses RAG (Retrieval Augmented Generation). Here's the basic flow:

1. When the server starts, it converts all financial assistance programs into vector embeddings using Sentence Transformers
2. These vectors get stored in ChromaDB
3. When you need recommendations for a case, the system builds a query from their financial data (income, credit score, debt, etc.) plus any uploaded documents
4. ChromaDB does semantic search to find the most similar programs using cosine similarity
5. The system calculates two scores: relevance (how well it matches) and estimated success (combines program approval rate with credit score)
6. Results stream back to the frontend with explanation text

The streaming uses Server-Sent Events so you see the "thinking" steps instead of just waiting for results.

## API Endpoints

Main endpoints:
- GET /api/cases - List all cases
- POST /api/cases - Create new case
- POST /api/recommend/stream - Get recommendations (streaming)
- POST /api/triage/stream - Analyze message urgency (streaming)
- POST /api/upload - Upload and process documents
- GET /api/analytics - Get dashboard stats
- POST /api/conversation/assist - Get writing suggestions

## Current Limitations

This is a prototype. Some things that would need work for production:
- Everything stores in memory right now (cases, documents, notes). Would need PostgreSQL or similar.
- No authentication or user accounts
- Triage uses simple keyword matching instead of a real NLP model
- Error handling is basic
- No rate limiting
- Groq API key is required but only used for potential future features

The core architecture is solid though. The RAG system works, streaming works, file upload and processing works. Just needs production polish.

## Project Structure
```
FinancePlatform/
├── backend/
│   ├── main.py              # FastAPI app and endpoints
│   ├── rag_system.py        # Vector search logic
│   ├── file_handler.py      # Document upload and text extraction
│   ├── .env                 # API keys (not in git)
│   └── uploads/             # Uploaded files (not in git)
└── frontend/
    ├── src/
    │   ├── components/      # React components
    │   ├── App.tsx          # Main app
    │   └── main.tsx         # Entry point
    └── package.json
```

## Why I Built This

I wanted to learn how to build a real RAG system and see if I could make something actually useful. The idea came from thinking about how case workers probably spend tons of time manually matching people to programs. Semantic search seemed like a good fit for that problem.

Also wanted to practice with:
- Vector databases (ChromaDB)
- Streaming responses (SSE)
- File processing and text extraction
- Combining multiple data sources (financial data plus documents) for better AI results

## License

MIT