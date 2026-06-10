import whisper
import json
import os
from pathlib import Path

model = whisper.load_model("large-v2")
audios = os.listdir("AUDIOS")
for audio in audios:
    if "_" in audio:
        audio_path = Path(audio)
        number, title = audio_path.stem.split("_", 1)
        number = number.strip()
        title = title.strip()
        print(number,title)
        result = model.transcribe(audio = f"AUDIOS/{audio}",
                                language = "hi",
                                task = "translate",
                                word_timestamps=False)
        chunks = []
        for segment in result["segments"]:
            chunks.append({"number":number,"title":title,"start":segment["start"],"end":segment["end"],"text":segment["text"]})
        chunks_with_metadata = {"chunks":chunks,"text":result["text"]}

        with open(f"jsons/{audio}.json","w") as f:
            json.dump(chunks_with_metadata,f)
