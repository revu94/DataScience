import whisper
import yt_dlp
import os
from utils.regex_utils import search_pattern


def download_audio(youtube_url:str, audio_path:str):
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': audio_path,  
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    audio_file = audio_path + ".mp3"
    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"Audio not downloaded: {audio_file}")

    return audio_file

def transcribe_audio(audio_path:str, model_size:str="base")->str:
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path)
    return result["text"]

def get_transcripts(youtube_urls:list[str],transcripts_path:str)->None:
    for idx, url in enumerate(youtube_urls, start=1):
        match=search_pattern(pattern=r"(?:shorts/|watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})",text=url)
        if not match:continue
        video_id=match.group(1) 
        if os.path.exists(f"{transcripts_path}/{video_id}.txt"):
            print(f"The file {video_id}.txt exists in folder {transcripts_path}")
            continue
        print(f"\n Processing URL {idx}/{len(youtube_urls)}: {url}")
        audios_path = f"audios/audio_{video_id}"

        print("Downloading audio...")
        audio_path = download_audio(url, audios_path)

        print("Transcribing audio...")
        transcript = transcribe_audio(audio_path, model_size="base")

        # Save transcript to file
        os.makedirs(f"{transcripts_path}", exist_ok=True)
        transcript_file = f"{transcripts_path}/{video_id}.txt"
        
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(transcript)

        print(f"Transcript saved: {transcript_file}")
        os.remove(audio_path)
    print("All URLs processed!")
