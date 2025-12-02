import requests

url = "http://127.0.0.1:8000/v1/analyzeResume"

files = {
    "file": open("Saqlin Mustaq Resume (July).pdf", "rb")
}

data = {
    "user_id": "saqlin"
}

response = requests.post(url, data=data, files=files)

print(response.json())
