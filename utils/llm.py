import logging
import openai

# 设置 OpenAI API 密钥和 base_url
BASE_URL = "https://api.deepseek.com"  # 可以设置为自定义的 URL

openai.api_base = BASE_URL  # 设置 base_url

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def call_llm_query(query: str, openApiKey:str) -> str:
    # 创建 OpenAI 客户端
    openai.api_key = openApiKey
    """调用 OpenAI LLM 处理查询，支持自定义消息"""
    logging.info(f"Calling LLM with query: {query}")
    try:
        custom_messages = [
            {
                "role": "system",
                "content": (
                    "你是一名电力系统、电力市场研究专家，请将我提出的问题解析为二十个关键词。"
                    "遵循以下规则：\n"
                    "1. 专业\n"
                    "2. 简洁\n"
                    "3. 用，分割\n"
                    "4. 仅返回关键词"
                )
            },
            {"role": "user", "content": f"Question: {query}"}
        ]

        # 调用 OpenAI API 生成回答
        response = openai.ChatCompletion.create(
            model="deepseek-chat",  # 使用传入的模型名称
            messages=custom_messages,  # 使用自定义的消息
            temperature=0.6,  # 设置生成文本的随机性
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

def call_llm(query: str, relevant_doc_content: str,openApiKey:str) -> str:
    # 创建 OpenAI 客户端
    openai.api_key = openApiKey
    """调用 OpenAI LLM 处理查询，支持自定义消息"""
    logging.info(f"Calling LLM with query: {query}")
    logging.info(f"Relevant document content: {relevant_doc_content}")
    try:
        custom_messages = [
            {
                "role": "system",
                "content": (
                    "你是一名电力系统、电力市场研究专家，请严格根据提供的文档内容回答问题。"
                    "遵循以下规则：\n"
                    "1. 回答需基于文档事实，优先使用列表和结构化格式\n"
                    "2. 如果文档信息不足，明确说明缺失信息\n"
                    "3. 对不确定的内容标注置信度\n"
                    "4. 保持回答简洁专业，避免冗余解释\n"
                    "5. 保持保证学术、专业、数据支撑"
                )
            },
            {"role": "user", "content": f"Document: {relevant_doc_content}"},
            {"role": "user", "content": f"Question: {query}"}
        ]

        # 调用 OpenAI API 生成回答
        response = openai.ChatCompletion.create(
            model="deepseek-chat",  # 使用传入的模型名称
            messages=custom_messages,  # 使用自定义的消息
            temperature=0.6,  # 设置生成文本的随机性
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
