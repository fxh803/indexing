# Please install OpenAI SDK first: `pip3 install openai`

from openai import OpenAI

def ask_deepseek(question):
    client = OpenAI(api_key="sk-7907fe173aef4c74ad3c9b92107d38dd", base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            # {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": question},
        ],
        stream=False
    )

    return response.choices[0].message.content