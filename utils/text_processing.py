import docx
from sentence_transformers import SentenceTransformer
import numpy as np
import re
from typing import List


# 加载预训练的 Sentence-BERT 模型
model = SentenceTransformer('all-MiniLM-L6-v2')  # 可以选择其他预训练模型


def vectorize_text(text: str) -> np.ndarray:
    """
    使用 Sentence-BERT 将文本转化为向量
    :param text: 输入的文本（文档或查询）
    :return: 文本的向量表示
    """
    try:
        # 获取文本的向量表示
        vector = model.encode(text)
        return np.array(vector)  # 转化为 numpy 数组
    except Exception as e:
        raise Exception(f"Error vectorizing text: {str(e)}")


def extract_text_from_docx(docx_file: str) -> str:
    """
    提取 docx 文件中的文本内容
    :param docx_file: docx 文件路径
    :return: 提取的文本内容
    """
    try:
        # 打开 .docx 文件
        doc = docx.Document(docx_file)
        text = "\n".join([para.text for para in doc.paragraphs])  # 合并所有段落的文本
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from docx file: {str(e)}")


def extract_text_from_pdf(pdf_file: str) -> str:
    """
    提取 PDF 文件中的文本内容
    :param pdf_file: PDF 文件路径
    :return: 提取的文本内容
    """
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_file)
        text = ""
        for page in doc:
            text += page.get_text()  # 提取文本
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF file: {str(e)}")


def clean_text(text: str) -> str:
    """
    清理和预处理文本，移除无用字符、额外的空白等
    :param text: 原始文本
    :return: 清理后的文本
    """
    try:
        # 移除多余的空白字符、换行符等
        cleaned_text = " ".join(text.split())

        # 去除特殊字符、数字等
        cleaned_text = re.sub(r'[^\w\s]', '', cleaned_text)

        # 可以进一步去除停用词，扩展该函数
        # 例如：停用词移除（可以使用 nltk 或其他库）

        return cleaned_text
    except Exception as e:
        raise Exception(f"Error cleaning text: {str(e)}")


def extract_keywords(text: str) -> List[str]:
    """
    提取文本中的关键字。这里只是一个简单示例，你可以根据需要进行改进（例如使用 NLP 库提取关键词）
    :param text: 输入文本
    :return: 关键字列表
    """
    words = text.split()  # 简单的按空格分割为单词
    keywords = [word for word in words if len(word) > 4]  # 假设关键字长度大于4的单词为关键字
    return keywords
