# File: video_processor.py
# Handles video processing and transcription

import whisper
from pytube import YouTube
import tempfile
import os

class VideoProcessor:
    def __init__(self):
        self.model = whisper.load_model("base")
        
    def transcribe_video(self, video_input):
        """Handle both YouTube URLs and file uploads"""
        try:
            if isinstance(video_input, str) and ("youtube.com" in video_input or "youtu.be" in video_input):
                return self._process_youtube(video_input)
            else:
                return self._process_file(video_input)
        except Exception as e:
            raise Exception(f"Video processing failed: {str(e)}")
    
    def _process_youtube(self, url):
        try:
            yt = YouTube(url)
            audio_stream = yt.streams.filter(only_audio=True).first()
            temp_dir = tempfile.gettempdir()
            temp_file = audio_stream.download(output_path=temp_dir)
            result = self.model.transcribe(temp_file)
            os.remove(temp_file)
            return result["text"]
        except Exception as e:
            raise Exception(f"YouTube processing error: {str(e)}")
    
    def _process_file(self, file):
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
                tmp.write(file.getbuffer())
                tmp_path = tmp.name
                
            result = self.model.transcribe(tmp_path)
            os.unlink(tmp_path)
            return result["text"]
        except Exception as e:
            raise Exception(f"File processing error: {str(e)}")