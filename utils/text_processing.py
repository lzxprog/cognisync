import re
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

# 加载停用词表
stop_words = set(stopwords.words('english'))


def clean_text(text):
    """清理文本，去除特殊字符、标点和停用词"""
    text = re.sub(r'[^\w\s]', '', text)  # 移除特殊字符和标点
    text = text.lower()  # 转换为小写
    words = text.split()
    text = ' '.join([word for word in words if word not in stop_words])
    return text


def split_text(text, max_length=512):
    """拆分长文本为小块，适用于LLM处理"""
    sentences = re.split(r'(?<=[.!?]) +', text)  # 按句号、问号、感叹号拆分
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        if current_length + len(sentence) > max_length:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_length = 0
        current_chunk.append(sentence)
        current_length += len(sentence)

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks
