# MoodMusic 🎵

AI-powered mood-based music recommendations using the Spotify Web API.

## Project Structure

```
moodmusic/
├── backend/
│   ├── main.py          ← FastAPI server
│   ├── requirements.txt
│   └── .env             ← your Spotify credentials (create this)
└── frontend/
    └── index.html       ← open this in browser
```

## Setup (5 minutes)

### Step 1: Get Spotify API Keys
1. Go to https://developer.spotify.com/dashboard
2. Log in with your Spotify account
3. Click **"Create app"**
4. Fill in: App name = "MoodMusic", Redirect URI = `http://localhost:8000`
5. Copy your **Client ID** and **Client Secret**

### Step 2: Set up the backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate       # Mac/Linux
# venv\Scripts\activate        # Windows

# Install dependencies
pip install -r requirements.txt

# Create your .env file
cp .env.example .env
# Open .env and paste your Client ID and Client Secret
```

### Step 3: Run the backend

```bash
uvicorn main:app --reload
```

You should see: `Uvicorn running on http://127.0.0.1:8000`

Test it: open http://localhost:8000/recommend/happy in your browser.

### Step 4: Open the frontend

Just open `frontend/index.html` in your browser. No build step needed!

Make sure the API URL in the config box says `http://localhost:8000`.

## How it works

The app maps each mood to Spotify audio features:
- **Valence** — how positive/happy the song sounds (0.0–1.0)
- **Energy** — intensity and activity level (0.0–1.0)
- **Danceability** — rhythmic regularity (0.0–1.0)

These are passed to Spotify's `/recommendations` endpoint to get real, matching songs.

## Moods supported
| Mood | Valence | Energy | Danceability |
|------|---------|--------|--------------|
| Happy | 0.85 | 0.80 | 0.75 |
| Sad | 0.15 | 0.25 | 0.30 |
| Chill | 0.55 | 0.30 | 0.45 |
| Energetic | 0.70 | 0.95 | 0.85 |
| Focus | 0.50 | 0.45 | 0.30 |
| Melancholy | 0.25 | 0.35 | 0.25 |

## Deploy (optional)
- Backend: deploy to **Render** (free tier) → https://render.com
- Frontend: deploy to **Vercel** or **GitHub Pages**
- Update the API URL in `index.html` to your Render URL

## API Endpoints
- `GET /recommend/{mood}?limit=10` — get track recommendations
- `GET /moods` — list all supported moods
