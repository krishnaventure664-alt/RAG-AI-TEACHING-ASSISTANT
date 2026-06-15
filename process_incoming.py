import json
import time
from urllib import request, error
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import requests

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

        if status_code != 200:
            print("Status_code:", status_code)

        data = json.loads(response_text)
        if "embeddings" in data:
            return data["embeddings"]

        print("Ollama error:", data)
        time.sleep(2)

    raise Exception("No embeddings returned after 3 tries")

def inference(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model":"llama3.2",
            # "model":"deepseek-r1",
            "prompt":prompt,
            "stream":False
        },
        timeout=300
    )
    response.raise_for_status()
    data = response.json()
    return data["response"]

df = joblib.load('embeddings.joblib')

incoming_query = input("Ask a Questions :")
question_embedding = create_embedding([incoming_query])[0]


#Find similarities of question_embedding with other embeddings

similarities = cosine_similarity(np.vstack(df['embedding']),[question_embedding]).flatten()
# print(similarities)
top_results = 5
max_indices = similarities.argsort()[-top_results:][::-1]
# print(max_indices)
new_df = df.iloc[max_indices]
# print(new_df[["title","number","text"]])

prompt = f''' I am teaching web-development in my sigma-web development course. Here are video subtitle chunks containing video title,video number,start time in seconds,end time in seconds,the text at that time :

{new_df[["title","number","start","end","text"]].to_json(orient="records")}

----------------------------------------------------

"{incoming_query}"
User asked this question related to the video chunks,you have to answer in human way(don't mention the above format,it is just for you) where and how much content is taught in which video (in which video at what timestamp) and guide user to go to that particular video . If user ask unrelated question ,tell him that you can only answer questions related to the course 
'''

with open("prompt.txt","w") as f:
    f.write(prompt)

# answer = inference(prompt)
# print(answer)

answer = inference(prompt)
print(answer)

with open("answer.txt","w",encoding="utf-8") as f:
    f.write(answer)

# for index,item in new_df.iterrows():
#     print(index, item["title"], item["number"], item["text"], item["start"], item["end"])
