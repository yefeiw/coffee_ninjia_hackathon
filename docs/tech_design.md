# Tech Design

## Stack
- FastAPI backend
- Static frontend
- OpenAI API for generation/embeddings
- Qdrant in-memory vector retrieval

## Key Services
- `ProfileService`: profile normalization and indexing
- `MatchingService`: retrieval and ranking (LLM + fallback)
- `ChatService`: local conversation persistence
- `VectorStore`: Qdrant collection management and search

## Data Flow
1. Onboarding input -> structured profile
2. Profile -> embedding -> vector index
3. Match request -> query embedding -> candidate retrieval
4. Ranking -> explainable match cards
5. Conversation APIs for follow-up
