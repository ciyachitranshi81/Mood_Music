from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import base64
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="MoodMusic API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CLIENT_ID = os.getenv("client_id")
CLIENT_SECRET = os.getenv("client_secret")

# Mood → Spotify audio feature targets
MOOD_PARAMS = {
    "happy": {
        "target_valence": 0.85,
        "target_energy": 0.80,
        "target_danceability": 0.75,
        "seed_genres": "pop,happy,dance",
    },
    "sad": {
        "target_valence": 0.15,
        "target_energy": 0.25,
        "target_danceability": 0.30,
        "seed_genres": "sad,acoustic,indie",
    },
    "chill": {
        "target_valence": 0.55,
        "target_energy": 0.30,
        "target_danceability": 0.45,
        "seed_genres": "chill,lofi,ambient",
    },
    "energetic": {
        "target_valence": 0.70,
        "target_energy": 0.95,
        "target_danceability": 0.85,
        "seed_genres": "work-out,edm,power-pop",
    },
    "focus": {
        "target_valence": 0.50,
        "target_energy": 0.45,
        "target_danceability": 0.30,
        "seed_genres": "study,classical,instrumental",
    },
    "melancholy": {
        "target_valence": 0.25,
        "target_energy": 0.35,
        "target_danceability": 0.25,
        "seed_genres": "indie,emo,singer-songwriter",
    },
}


async def get_spotify_token() -> str:
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": f"Basic {encoded}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={"grant_type": "client_credentials"},
        )

    print("TOKEN STATUS:", response.status_code)
    print("TOKEN BODY:", response.text)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to get Spotify token")

    return response.json()["access_token"]

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to get Spotify token")

    return response.json()["access_token"]


@app.get("/")
def root():
    return {"message": "MoodMusic API is running"}


@app.get("/recommend/{mood}")
async def recommend(mood: str, limit: int = 10):
    mood = mood.lower()
    if mood not in MOOD_PARAMS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown mood. Choose from: {', '.join(MOOD_PARAMS.keys())}",
        )

    token = await get_spotify_token()
    params = MOOD_PARAMS[mood]

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            "https://api.spotify.com/v1/recommendations",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "limit": limit,
                "seed_genres": params["seed_genres"],
                "target_valence": params["target_valence"],
                "target_energy": params["target_energy"],
                "target_danceability": params["target_danceability"],
            },
        )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Spotify API error")

    tracks = response.json().get("tracks", [])

    return {
        "mood": mood,
        "tracks": [
            {
                "id": t["id"],
                "name": t["name"],
                "artist": t["artists"][0]["name"],
                "album": t["album"]["name"],
                "duration_ms": t["duration_ms"],
                "preview_url": t.get("preview_url"),
                "spotify_url": t["external_urls"]["spotify"],
                "album_art": t["album"]["images"][0]["url"] if t["album"]["images"] else None,
                "popularity": t["popularity"],
            }
            for t in tracks
        ],
    }


@app.get("/moods")
def get_moods():
    return {
        "moods": list(MOOD_PARAMS.keys()),
        "descriptions": {
            "happy": "Upbeat, positive, feel-good energy",
            "sad": "Slow, emotional, reflective",
            "chill": "Relaxed, mellow, easygoing",
            "energetic": "High energy, pumped up, workout vibes",
            "focus": "Calm, instrumental, concentration",
            "melancholy": "Bittersweet, introspective, indie",
        },
    }
