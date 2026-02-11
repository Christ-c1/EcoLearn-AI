# 🌱 EcoLearn AI - Plateforme d'apprentissage écologique

Une plateforme d'apprentissage écologique alimentée par l'IA qui calcule votre empreinte carbone et finance la plantation d'arbres.

## 🚀 Déploiement Docker

### Prérequis
- Docker et Docker Compose installés
- (Optionnel) Clés OAuth Google pour la connexion avec Google

### Démarrage rapide

1. **Cloner le projet et naviguer dans le dossier**
```bash
cd /chemin/vers/ecolearn
```

2. **Lancer les containers**
```bash
docker-compose up -d
```

3. **Accéder à l'application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Documentation API: http://localhost:8000/docs

### Configuration OAuth Google (Optionnel)

Pour activer la connexion avec Google:

1. Créez un projet sur [Google Cloud Console](https://console.cloud.google.com/)
2. Activez l'API Google+ et créez des identifiants OAuth 2.0
3. Ajoutez `http://localhost:8000/api/v1/auth/google/callback` comme URI de redirection autorisée
4. Créez un fichier `.env` à la racine:

```env
GOOGLE_CLIENT_ID=votre_client_id
GOOGLE_CLIENT_SECRET=votre_client_secret
```

5. Relancez les containers:
```bash
docker-compose down
docker-compose up -d
```

### Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│     Backend     │────▶│   PostgreSQL    │
│   (React/Vite)  │     │    (FastAPI)    │     │   (Database)    │
│   Port: 3000    │     │   Port: 8000    │     │   Port: 5432    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Fonctionnalités

#### 🔐 Authentification
- **Email/Mot de passe**: Inscription et connexion classique avec JWT
- **OAuth Google**: Connexion rapide avec compte Google (optionnel)

#### 📚 Apprentissage IA
- Génération de parcours personnalisés via IA
- Modules structurés avec quiz interactifs
- Suivi de progression

#### 🌍 Suivi Carbone
- Calcul automatique de l'empreinte carbone
- Graphiques D3.js interactifs
- Équivalences (km voiture, vols)

#### 🌳 Plantation d'arbres
- Compensation carbone via plantation virtuelle
- Certificats de plantation
- Historique des contributions

### Commandes utiles

```bash
# Démarrer les services
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Arrêter les services
docker-compose down

# Reconstruire les images
docker-compose build --no-cache

# Réinitialiser la base de données
docker-compose down -v
docker-compose up -d
```

### Variables d'environnement

#### Backend
| Variable | Description | Défaut |
|----------|-------------|--------|
| `DATABASE_URL` | URL de connexion PostgreSQL | `postgresql+asyncpg://ecolearn:ecolearn_secret_2024@postgres:5432/ecolearn_db` |
| `SECRET_KEY` | Clé secrète pour JWT | `ecolearn-secret-key-change-in-production-2024` |
| `GOOGLE_CLIENT_ID` | ID client OAuth Google | - |
| `GOOGLE_CLIENT_SECRET` | Secret client OAuth Google | - |
| `FRONTEND_URL` | URL du frontend | `http://localhost:3000` |

#### Frontend
| Variable | Description | Défaut |
|----------|-------------|--------|
| `VITE_API_URL` | URL de l'API backend | `http://localhost:8000` |

### Structure du projet

```
ecolearn/
├── docker-compose.yml          # Configuration Docker
├── README.md                   # Documentation
├── backend/
│   ├── Dockerfile              # Image Docker backend
│   ├── main.py                 # Point d'entrée FastAPI
│   ├── requirements.txt        # Dépendances Python
│   ├── init.sql                # Script d'initialisation DB
│   ├── core/                   # Configuration et DB
│   ├── models/                 # Modèles SQLAlchemy
│   ├── routers/                # Routes API
│   └── services/               # Logique métier
└── frontend/
    ├── Dockerfile              # Image Docker frontend
    ├── package.json            # Dépendances Node.js
    ├── src/
    │   ├── App.tsx             # Composant principal
    │   ├── lib/                # Services (auth, api)
    │   ├── pages/              # Pages de l'application
    │   └── components/         # Composants UI
    └── public/                 # Assets statiques
```

### API Endpoints

#### Authentification
- `POST /api/v1/auth/register` - Inscription
- `POST /api/v1/auth/login` - Connexion
- `POST /api/v1/auth/verify-token` - Vérifier le token JWT
- `GET /api/v1/auth/google` - Connexion OAuth Google
- `POST /api/v1/auth/logout` - Déconnexion

#### Apprentissage
- `GET /api/v1/learning_paths/` - Liste des parcours
- `GET /api/v1/learning_paths/{id}` - Détail d'un parcours
- `POST /api/v1/learning/generate-path` - Générer un parcours IA
- `POST /api/v1/learning/record-session` - Enregistrer une session

#### Carbone
- `GET /api/v1/carbon_metrics/` - Métriques carbone
- `GET /api/v1/learning/carbon-stats` - Statistiques carbone

#### Arbres
- `GET /api/v1/tree_plantations/` - Historique des plantations
- `POST /api/v1/learning/plant-tree` - Planter un arbre

### Sécurité

⚠️ **Important pour la production:**

1. Changez `SECRET_KEY` avec une clé sécurisée générée aléatoirement
2. Changez les mots de passe PostgreSQL
3. Utilisez HTTPS avec un certificat SSL
4. Configurez un reverse proxy (nginx, traefik)
5. Activez les CORS appropriés

### Licence

MIT License - Libre d'utilisation et de modification.

---

🌿 **EcoLearn AI** - Apprendre en préservant la planète