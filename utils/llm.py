from openai import OpenAI
from config import OPENAI_API_KEY


def call_llm(question, context):
    """调用 OpenAI LLM 处理查询"""
    try:
        client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://api.deepseek.com")

        prompt = f"Based on the following context, answer the question: \nContext: {context}\nQuestion: {question}"
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error calling LLM: {str(e)}"