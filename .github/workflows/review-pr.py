import os

import openai
from github import Github

g = Github(os.getenv("GITHUB_TOKEN"))
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_review_with_openai(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",  # use GPT-4 model
        messages=[
            {"role": "system", "content": "You are a helpful coding assistant. Your job is to review the following diff and spot any bugs. Leave review comments so the author can fix their bugs."},
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message['content']

def reviewPR():
    repo = g.get_repo(f"{os.getenv('GITHUB_REPOSITORY')}")
    try:
        pr_number = os.getenv('GITHUB_REF').split('/')[-1]
        pr = repo.get_pull(int(pr_number))

        feedback = get_review_with_openai(pr.body)

        pr.create_review(body=feedback.choices[0].text, event="COMMENT")
    except Exception as e:
        raise Exception(f"Failed to review PR {os.getenv('GITHUB_REF')}: {e}")

if __name__ == "__main__":
    reviewPR()
