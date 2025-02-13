from openai import OpenAI
from config import OPENAI_API_KEY  # 从配置文件中导入 API 密钥

# 设置 OpenAI API 密钥
client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://api.deepseek.com")

def call_llm(query: str, relevant_doc_content: str, model_name="gpt-3.5") -> str:
    """调用 OpenAI LLM 处理查询"""
    try:
        # 构建提示（prompt）
        prompt = f"Answer the following question based on the document:\n{relevant_doc_content}\n\nQuestion: {query}\nAnswer:"

        # 调用 ChatGPT 接口生成回答
        response = client.chat.completions.create(
            model=model_name,  # 允许传递不同的模型名称
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            stream=False  # 不使用流式输出
        )

        # 检查响应
        if 'choices' not in response or len(response['choices']) == 0:
            raise Exception("No response choices returned from LLM API")

        # 返回模型生成的答案
        return response['choices'][0]['message']['content'].strip()

    except Exception as e:
        # 改进错误处理，捕获并返回详细的错误信息
        return f"Error calling LLM: {str(e)}"
