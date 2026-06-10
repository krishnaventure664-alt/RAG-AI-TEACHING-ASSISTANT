# Converts the video to mp3.
import os
import re
import subprocess


files = os.listdir("VIDEOS")
for file in files:
    print(file)
    number_match = re.search(r"Tutorial\s+#(\d+)", file)
    if not number_match:
        print(f"Skipping {file}: tutorial number not found")
        continue

    tutorial_number = number_match.group(1)
    title_part = file.split("[", 1)[0].strip()
    file_name = re.split(r"\s+[\u007c\uff5c]\s+|\s+-\s+Tutorial\s+#", title_part)[0].strip()
    output_path = f"AUDIOS/{tutorial_number}_{file_name}.mp3"

    print(tutorial_number, file_name)
    subprocess.run(["ffmpeg", "-i", f"VIDEOS/{file}", output_path], check=True)
