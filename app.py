from fastapi import FastAPI, HTTPException
import yt_dlp
import os

app = FastAPI(title="Beatly Premium Stream API")

@app.get("/")
def get_stream(id: str = None):
    if not id:
        return {"status": "Beatly Stream API is online. Pass an ?id="}
        
    video_url = f"https://www.youtube.com/watch?v={id}"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
    }
    
    # Locate the cookies file inside the deployment environment
    cookie_path = os.path.join(os.path.dirname(__file__), "..", "cookies.txt")
    if os.path.exists(cookie_path):
        ydl_opts['cookiefile'] = cookie_path
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            stream_url = info.get('url')
            
            if not stream_url:
                raise HTTPException(status_code=404, detail="Could not extract stream URL")
                
            return {"stream_url": stream_url}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
