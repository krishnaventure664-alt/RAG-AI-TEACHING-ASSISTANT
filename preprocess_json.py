import os
import json
import re
import time
from urllib import request, error
import pandas as pd
import joblib

BATCH_SIZE = 32

def create_embedding(text_list):
    for attempt in range(3): 
        body = json.dumps({
            "model": "bge-m3",
            "input": text_list
        }).encode("utf-8")

        req = request.Request(
            "http://localhost:11434/api/embed",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with request.urlopen(req, timeout=120) as r:
                status_code = r.status
                response_text = r.read().decode("utf-8")
        except error.HTTPError as e:
            status_code = e.code
            response_text = e.read().decode("utf-8")

        print("Status_code:", status_code)

        data = json.loads(response_text)
        if "embeddings" in data:
            return data["embeddings"]

        print("Ollama error:", data)
        time.sleep(2)

    raise Exception("No embeddings returned after 3 tries")

def create_embeddings_in_batches(text_list, batch_size=BATCH_SIZE):
    all_embeddings = []

    for start in range(0, len(text_list), batch_size):
        batch = text_list[start:start + batch_size]
        print(f"Embedding batch {start // batch_size + 1}: {len(batch)} chunks")
        all_embeddings.extend(create_embedding(batch))

    return all_embeddings


def tutorial_number(filename):
    match = re.match(r"\s*(\d+)", filename)
    if not match:
        raise ValueError(f"Cannot read tutorial number from {filename}")
    return int(match.group(1))


jsons = os.listdir("jsons") #list all the jsons
jsons.sort(key=tutorial_number)
my_dicts = []
chunk_id = 0
for json_file in jsons:
    with open(f"jsons/{json_file}") as f:
        content = json.load(f)
    print(f"Creating embeddings for {json_file} ")
    
    embeddings = create_embeddings_in_batches([c['text'] for c in content['chunks']])

    for i,chunk in enumerate(content['chunks']):
        chunk['chunk_id'] = chunk_id
        chunk['embedding'] = embeddings[i]
        chunk_id +=1
        my_dicts.append(chunk)
    
    
# print(my_dicts)
# print("Total chunks with embeddings:", len(my_dicts))
df = pd.DataFrame.from_records(my_dicts)
#Save this Dataframe
joblib.dump(df,'embeddings.joblib')
