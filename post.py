import requests
import json

url = "https://windbornesystems.com/career_applications.json"

data = {
  "career_application": {
    "name": "GOUTHAM CHANDRAPPA",
    "email": "chandrappagoutham52@gmail.com",
    "role": "LLM Tooling Intern",
    "notes": """Key Technical Skills : Python, data visualization, Machine Learning, and Generative AI application development, Natural language processing, C++, MATLAB. for more technical skills please refer to my linkedin account and the Resume
                What I bring to table :) = I'm good to work with because I blend technical expertise with strong communication and a collaborative approach to solving complex problems.""",
    "submission_url": "https://github.com/GouthamChandrappa/balloon_constellation",
    "portfolio_url": "https://github.com/GouthamChandrappa/RAG_AGENTIC_CHATBOT",
    "resume_url": "https://drive.google.com/file/d/1yB9_4mA_9yffWy3X_aCqoPPsFrXya9OC/view?usp=sharing"
  }
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, data=json.dumps(data), headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")