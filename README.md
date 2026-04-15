# MoodMusic

> Spotify-powered mood-based music recommendations.

Pick a mood -> we map it to Spotify's audio features (valence, energy, danceability) -> get a curated playlist of real tracks.

---

## Stack

| Layer    | Tech                          |
|----------|-------------------------------|
| Backend  | FastAPI (Python)              |
| API      | Spotify Web API               |
| Frontend | Vanilla HTML/CSS/JS           |
| Hosting  | Render (backend) · GitHub Pages (frontend) |

---

## Setup

### 1. Get Spotify credentials

1. Go to [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Log in → **Create app**
3. Name it anything. Set Redirect URI to `http://127.0.0.1:8000`
4. Go to **Settings** → copy **Client ID** and **Client Secret**

---

### 2. Backend (Python 3.9+)

```bash
# clone the repo
git clone https://github.com/YOUR_USERNAME/moodmusic.git
cd moodmusic

# create virtual environment
python -m venv venv

# activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# install dependencies
pip install -r requirements.txt

# create your .env file
copy .env.example .env     # Windows
# OR
cp .env.example .env       # Mac/Linux
```

Open `.env` and paste your credentials:

```
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

Start the server:

```bash
uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Test it: open `http://127.0.0.1:8000/recommend/happy` in your browser. You should see JSON with tracks.

---

### 3. Frontend

Just open `index.html` in your browser. That's it.

Make sure the **API Endpoint** field in the bottom left of the sidebar says `http://127.0.0.1:8000`.

---

## How it works

Each mood maps to target values for Spotify's audio features:

| Mood       | Valence | Energy | Danceability |
|------------|---------|--------|--------------|
| Happy      | 0.85    | 0.75   | 0.70         |
| Sad        | 0.15    | 0.30   | 0.35         |
| Energetic  | 0.70    | 0.95   | 0.80         |
| Chill      | 0.55    | 0.35   | 0.45         |
| Focus      | 0.50    | 0.45   | 0.30         |
| Angry      | 0.20    | 0.90   | 0.60         |
| Romantic   | 0.75    | 0.40   | 0.55         |
| Melancholic| 0.25    | 0.38   | 0.38         |

These are sent to Spotify's `/v1/recommendations` endpoint which returns tracks matching those audio profiles.

---

## API Endpoints

| Endpoint                        | Description                     |
|---------------------------------|---------------------------------|
| `GET /`                         | Health check                    |
| `GET /moods`                    | List available moods            |
| `GET /recommend/{mood}`         | Get tracks for a mood           |
| `GET /recommend/{mood}?limit=N` | Control number of tracks (max 20) |

---

## Project Structure

```
moodmusic/
├── main.py            # FastAPI backend
├── requirements.txt   # Python dependencies
├── .env.example       # Credential template
├── index.html         # Frontend (single file)
└── README.md
```

---

## Contributors

- [Chitranshi Singh](https://github.com/ciyachitranshi81)
- [Syed Mohammad Fawaz](https://github.com/SMFawaz24)
