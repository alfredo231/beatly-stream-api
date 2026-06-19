from fastapi import FastAPI, HTTPException
import requests

app = FastAPI(title="Beatly Premium Stream API")

@app.get("/")
def get_stream(id: str = None):
    if not id:
        return {"status": "Beatly Stream API is online. Pass an ?id="}
        
    # Ask a decentralized instance for the stream manifest instead of scraping it ourselves.
    # This completely bypasses YouTube's bot wall.
    piped_url = f"https://pipedapi.kavin.rocks/streams/{id}"
    
    try:
        # Fetch the metadata from the proxy
        response = requests.get(piped_url, timeout=8)
        response.raise_for_status()
        data = response.json()
        
        # Extract the audio-only streams
        audio_streams = data.get("audioStreams", [])
        
        if not audio_streams:
            raise HTTPException(status_code=404, detail="Could not extract direct stream URL.")
            
        # Grab the highest quality m4a/webm audio URL available
        stream_url = audio_streams[-1].get("url")
        
        return {"stream_url": stream_url}
        
    except requests.exceptions.RequestException as e:
        # Fallback to an alternate proxy instance if the main one is busy
        try:
            backup_url = f"https://pipedapi.lunar.icu/streams/{id}"
            backup_resp = requests.get(backup_url, timeout=8)
            backup_resp.raise_for_status()
            backup_data = backup_resp.json()
            
            stream_url = backup_data.get("audioStreams", [])[-1].get("url")
            return {"stream_url": stream_url}
            
        except Exception as backup_error:
            raise HTTPException(status_code=500, detail="All proxy routes blocked or timed out.")
