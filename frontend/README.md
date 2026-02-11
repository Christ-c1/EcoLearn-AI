# EcoLearn - Plateforme d'Apprentissage Écologique

Une application web complète pour l'apprentissage écologique avec suivi de l'empreinte carbone et génération de contenu par IA.

## 🚀 Déploiement avec Docker

### Prérequis
- Docker et Docker Compose installés
- Port 3000 (frontend), 8000 (backend), et 5432 (PostgreSQL) disponibles

### Configuration

Le fichier `docker-compose.yml` contient toutes les configurations nécessaires :

#### Variables d'environnement Backend

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `DATABASE_URL` | URL de connexion PostgreSQL | `postgresql+asyncpg://ecolearn:ecolearn_secret_2024@postgres:5432/ecolearn_db` |
| `JWT_SECRET_KEY` | Clé secrète pour les tokens JWT | `ecolearn-secret-key-change-in-production-2024` |
| `JWT_ALGORITHM` | Algorithme JWT | `HS256` |
| `JWT_EXPIRE_MINUTES` | Durée de validité des tokens | `1440` (24 heures) |
| `APP_AI_BASE_URL` | URL de l'API AI (OpenRouter) | `https://openrouter.ai/api/v1` |
| `APP_AI_KEY` | Clé API OpenRouter | Configurée dans docker-compose.yml |

### Démarrage

```bash
# Depuis le dossier /workspace/app
cd /workspace/app

# Construire et démarrer tous les services
docker-compose up --build

# Ou en arrière-plan
docker-compose up --build -d
```

### Accès à l'application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentation API**: http://localhost:8000/docs

## 🔐 Authentification

L'application utilise une authentification JWT avec email/mot de passe :

1. **Inscription** : Créez un compte avec email et mot de passe
2. **Connexion** : Connectez-vous pour recevoir un token JWT
3. **Accès** : Le token est automatiquement inclus dans les requêtes API

### Endpoints d'authentification

- `POST /api/v1/auth/register` - Inscription
- `POST /api/v1/auth/login` - Connexion
- `GET /api/v1/user/me` - Profil utilisateur

## 🤖 Génération de Contenu par IA

L'application utilise OpenRouter pour générer des parcours d'apprentissage personnalisés.

### Configuration OpenRouter

1. Obtenez une clé API sur [OpenRouter](https://openrouter.ai/)
2. Configurez la clé dans `docker-compose.yml` :

```yaml
environment:
  APP_AI_BASE_URL: https://openrouter.ai/api/v1
  APP_AI_KEY: votre-clé-api-openrouter
```

### Modèle utilisé

- **google/gemini-flash-1.5** : Modèle rapide et économique pour la génération de contenu éducatif

### Fallback

Si l'API AI n'est pas disponible, l'application utilise un contenu statique prédéfini pour les sujets courants (recyclage, énergie, eau, biodiversité).

## 📊 Fonctionnalités

### Dashboard
- Vue d'ensemble des statistiques utilisateur
- Progression des parcours d'apprentissage
- Suivi de l'empreinte carbone

### Parcours d'Apprentissage
- Génération automatique par IA
- Modules progressifs avec quiz
- Suivi de la progression

### Suivi Carbone
- Calcul de l'empreinte carbone des sessions
- Statistiques de compensation
- Équivalents visuels (km en voiture, vols)

### Plantation d'Arbres
- Historique des contributions
- Impact environnemental calculé

## 🛠️ Structure du Projet

```
app/
├── backend/
│   ├── core/           # Configuration et base de données
│   ├── models/         # Modèles SQLAlchemy
│   ├── routers/        # Routes API FastAPI
│   ├── services/       # Logique métier
│   ├── schemas/        # Schémas Pydantic
│   ├── main.py         # Point d'entrée
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/ # Composants React
│   │   ├── pages/      # Pages de l'application
│   │   ├── lib/        # Utilitaires et API
│   │   └── App.tsx     # Routeur principal
│   └── public/
├── docker-compose.yml
└── README.md
```

## 🔧 Développement Local

### Backend (sans Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend (sans Docker)

```bash
cd frontend
pnpm install
pnpm run dev
```

## 📝 Notes de Production

⚠️ **Important** : Pour un déploiement en production, modifiez les valeurs suivantes :

1. `JWT_SECRET_KEY` : Utilisez une clé secrète forte et unique
2. `POSTGRES_PASSWORD` : Utilisez un mot de passe sécurisé
3. `APP_AI_KEY` : Utilisez votre propre clé API OpenRouter
4. Configurez HTTPS avec un reverse proxy (nginx, traefik)
5. Activez les logs de production

## 📄 Licence

MIT License