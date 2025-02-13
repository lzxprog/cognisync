import logging

import openai
from config import OPENAI_API_KEY  # 从配置文件中导入 API 密钥

# 设置 OpenAI API 密钥和 base_url
BASE_URL = "https://api.deepseek.com"  # 可以设置为自定义的 URL

# 创建 OpenAI 客户端
openai.api_key = OPENAI_API_KEY
openai.api_base = BASE_URL  # 设置 base_url

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def call_llm(query: str, relevant_doc_content: str) -> str:
    """调用 OpenAI LLM 处理查询，支持自定义消息"""
    logging.info(f"Calling LLM with query: {query}")
    logging.info(f"Relevant document content: {relevant_doc_content}")
    try:
        custom_messages = [
            {"role": "system", "content": "You are a helpful assistant who answers questions based on the content of the provided documents."},
            {"role": "user", "content": f"Document: {relevant_doc_content}"},
            {"role": "user", "content": f"Question: {query}"}
        ]

        # 调用 OpenAI API 生成回答
        response = openai.ChatCompletion.create(
            model="deepseek-chat",  # 使用传入的模型名称
            messages=custom_messages,  # 使用自定义的消息
            temperature=0.7,  # 设置生成文本的随机性
            max_tokens=512  # 设置回答的最大长度
        )

        # 检查响应
        if 'choices' not in response or len(response['choices']) == 0:
            raise Exception("No response choices returned from LLM API")

        # 返回模型生成的答案
        return response['choices'][0]['message']['content'].strip()

    except Exception as e:
        # 改进错误处理，捕获并返回详细的错误信息
        return f"Error calling LLM: {str(e)}"
