# LLM Rating - Prédiction de notes via Claude

Application web permettant de prédire la note (1-5 étoiles) d'un avis client en utilisant Claude (Anthropic) via LangChain.

## Architecture

```
llm_rating/
├── docker-compose.yml
├── backend/          # Django + DRF + LangChain
│   ├── Dockerfile
│   ├── requirements.txt
│   └── rating_api/
└── frontend/         # React + Vite
    ├── Dockerfile
    └── src/
```

## Prérequis

- Docker & Docker Compose
- Clé API Anthropic

## Installation

1. **Configurer la clé API**
   ```bash
   cd llm_rating
   cp .env.example .env
   # Éditer .env et ajouter votre ANTHROPIC_API_KEY
   ```

2. **Lancer avec Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Accéder à l'application**
   - Frontend : http://localhost:5173
   - Backend API : http://localhost:8000

## Utilisation sans Docker

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### POST /api/predict/
Prédit la note d'un avis.

**Request:**
```json
{
  "review": "Produit de très bonne qualité, livraison rapide !"
}
```

**Response:**
```json
{
  "rating": 5,
  "explanation": "Avis très positif mentionnant qualité et rapidité",
  "review": "Produit de très bonne qualité, livraison rapide !"
}
```

### GET /api/health/
Vérifie l'état de l'API.

## Technologies

- **Backend**: Django 4.2, Django REST Framework, LangChain, Anthropic Claude
- **Frontend**: React 18, Vite
- **Containerisation**: Docker, Docker Compose
