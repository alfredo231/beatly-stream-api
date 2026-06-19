from fastapi import FastAPI, HTTPException
import yt_dlp

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
        
        # This parameter skips the bot check entirely
        'process': False, 
        
        # Force client spoofing to pretend we are a mobile app
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios'],
                'skip': ['webpage', 'configs', 'js']
            }
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # extract_info with process=False extracts formats instantly without triggering captchas
            info = ydl.extract_info(video_url, download=False, process=False)
            
            # Since process=False returns raw formats list, look for the stream link here
            formats = info.get('formats', [])
            audio_formats = [f for f in formats if f.get('vcodec') == 'none']
            
            if audio_formats:
                # Grab the best quality audio format available
                stream_url = audio_formats[-1].get('url')
            else:
                stream_url = info.get('url') or (formats[0].get('url') if formats else None)
                
            if not stream_url:
                raise HTTPException(status_code=404, detail="Could not extract stream URL")
                
            return {"stream_url": stream_url}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
