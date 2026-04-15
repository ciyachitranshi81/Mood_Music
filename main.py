import os
import base64
import random
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="MoodMusic API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

CLIENT_ID     = os.getenv("SPOTIFY_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")

MOODS: dict[str, dict] = {
    "happy": {
        "queries": ["feel good hits", "happy upbeat", "good vibes pop", "sunshine pop", "feel good dance"],
        "meta":    {"valence": 0.85, "energy": 0.75, "danceability": 0.70},
    },
    "sad": {
        "queries": ["sad songs", "heartbreak acoustic", "emotional ballad", "sad indie", "crying playlist"],
        "meta":    {"valence": 0.15, "energy": 0.30, "danceability": 0.35},
    },
    "energetic": {
        "queries": ["workout hits", "high energy electronic", "pump up songs", "gym motivation", "high bpm dance"],
        "meta":    {"valence": 0.70, "energy": 0.95, "danceability": 0.80},
    },
    "chill": {
        "queries": ["chill vibes", "lo-fi chill", "relaxing indie", "afternoon chill", "mellow beats"],
        "meta":    {"valence": 0.55, "energy": 0.35, "danceability": 0.45},
    },
    "focus": {
        "queries": ["study music", "deep focus instrumental", "concentration music", "focus beats", "background study"],
        "meta":    {"valence": 0.50, "energy": 0.45, "danceability": 0.30},
    },
    "angry": {
        "queries": ["metal rage", "hard rock intense", "anger release music", "heavy metal", "punk rock aggressive"],
        "meta":    {"valence": 0.20, "energy": 0.90, "danceability": 0.60},
    },
    "romantic": {
        "queries": ["love songs", "romantic r&b", "slow dance songs", "date night music", "romantic pop"],
        "meta":    {"valence": 0.75, "energy": 0.40, "danceability": 0.55},
    },
    "melancholic": {
        "queries": ["melancholic indie", "bittersweet songs", "nostalgic music", "sad beautiful songs", "melancholy folk"],
        "meta":    {"valence": 0.25, "energy": 0.38, "danceability": 0.38},
    },
}


async def get_token() -> str:
    if not CLIENT_ID or not CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Spotify credentials not set. Add SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET to your .env file.",
        )
    encoded = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": f"Basic {encoded}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={"grant_type": "client_credentials"},
        )
    if r.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Spotify token error: {r.text}")
    return r.json()["access_token"]


def parse_track(t: dict) -> dict:
    return {
        "id":          t["id"],
        "name":        t["name"],
        "artists":     [a["name"] for a in t["artists"]],
        "album":       t["album"]["name"],
        "album_art":   t["album"]["images"][0]["url"] if t["album"]["images"] else None,
        "preview_url": t.get("preview_url"),
        "spotify_url": t["external_urls"]["spotify"],
        "duration_ms": t["duration_ms"],
    }


@app.get("/")
async def root():
    return {"status": "ok", "message": "MoodMusic API is running"}


@app.get("/moods")
async def list_moods():
    return {"moods": list(MOODS.keys())}


@app.get("/recommend/{mood}")
async def recommend(mood: str, limit: int = 12):
    if mood not in MOODS:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown mood '{mood}'. Valid: {list(MOODS.keys())}",
        )

    token  = await get_token()
    config = MOODS[mood]
    limit  = min(limit, 20)

    queries  = random.sample(config["queries"], k=min(2, len(config["queries"])))
    seen_ids = set()
    tracks   = []

    async with httpx.AsyncClient(timeout=20.0) as client:
        for query in queries:
            needed = limit - len(tracks)
            if needed <= 0:
                break

            r = await client.get(
                "https://api.spotify.com/v1/search",
                headers={"Authorization": f"Bearer {token}"},
                params={
                    "q":     query,
                    "type":  "track",
                    "limit": min(needed + 5, 10),
                },
            )

            if r.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Spotify search error: {r.text}",
                )

            for item in r.json().get("tracks", {}).get("items", []):
                if item["id"] not in seen_ids and len(tracks) < limit:
                    seen_ids.add(item["id"])
                    tracks.append(parse_track(item))

    random.shuffle(tracks)

    return {
        "mood":          mood,
        "count":         len(tracks),
        "audio_targets": config["meta"],
        "tracks":        tracks,
    }
