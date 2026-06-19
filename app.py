from fastapi import FastAPI, HTTPException
import yt_dlp

app = FastAPI(title="Beatly Ultimate Speed API")

@app.get("/")
def get_stream(id: str = None):
    if not id:
        return {"status": "Beatly API Active. Pass ?id="}
        
    video_url = f"https://www.youtube.com/watch?v={id}"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
        
        # SPEED CRITICAL OPTIMIZATIONS:
        'process': False,                     # Don't resolve playlists or extra deep formats
        'extract_flat': True,                 # Scrape fast metadata blocks only
        'force_generic_extractor': False,
        
        # Bypass webpage scraper downloads to jump straight to the streaming API manifest
        'extractor_args': {
            'youtube': {
                'player_client': ['android_vr', 'ios'], # Ultra-fast internal light signatures
                'skip': ['webpage', 'configs', 'js']    # Completely skip downloading 3MB+ of HTML/JS
            }
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Instant flat metadata lookup
            info = ydl.extract_info(video_url, download=False, process=False)
            formats = info.get('formats', [])
            
            # Instantly filter for direct raw audio formats in memory
            audio_formats = [f for f in formats if f.get('vcodec') == 'none' and f.get('url')]
            
            if audio_formats:
                # Grab the top optimized direct streaming link
                stream_url = audio_formats[-1].get('url')
            else:
                stream_url = info.get('url') or (formats[0].get('url') if formats else None)
                
            if not stream_url:
                raise HTTPException(status_code=404, detail="Stream URL could not be unpacked rapidly.")
                
            return {"stream_url": stream_url}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
