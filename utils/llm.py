import openai
from config import OPENAI_API_KEY  # 从配置文件中导入 API 密钥

# 设置 OpenAI API 密钥和 base_url
BASE_URL = "https://api.deepseek.com"  # 可以设置为自定义的 URL

# 创建 OpenAI 客户端
openai.api_key = OPENAI_API_KEY
openai.api_base = BASE_URL  # 设置 base_url

def call_llm(query: str, relevant_doc_content: str, model_name="deepseek-chat", system_message="You are a helpful assistant.", custom_messages=None) -> str:
    """调用 OpenAI LLM 处理查询，支持自定义消息"""
    try:
        # 如果没有提供自定义的 messages，就使用默认的
        if custom_messages is None:
            custom_messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Document: {relevant_doc_content}"},
                {"role": "user", "content": f"Question: {query}"}
            ]

        # 调用 OpenAI API 生成回答
        response = openai.ChatCompletion.create(
            model=model_name,  # 使用传入的模型名称
            messages=custom_messages,  # 使用自定义的消息
            temperature=0.7,  # 设置生成文本的随机性
            max_tokens=100  # 设置回答的最大长度
        )

        # 检查响应
        if 'choices' not in response or len(response['choices']) == 0:
            raise Exception("No response choices returned from LLM API")

        # 返回模型生成的答案
        return response['choices'][0]['message']['content'].strip()

    except Exception as e:
        # 改进错误处理，捕获并返回详细的错误信息
        return f"Error calling LLM: {str(e)}"
