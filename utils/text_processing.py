import docx
import re
from typing import List
import os
from io import BytesIO

# PDF 文档提取依赖库
import fitz  # PyMuPDF

def extract_text_from_docx(docx_file: BytesIO) -> str:
    """
    提取 docx 文件中的文本内容
    :param docx_file: 上传的 .docx 文件对象
    :return: 提取的文本内容
    """
    try:
        # 打开 .docx 文件
        doc = docx.Document(docx_file)
        text = "\n".join([para.text for para in doc.paragraphs])  # 合并所有段落的文本
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from docx file: {str(e)}")


def extract_text_from_pdf(pdf_file: BytesIO) -> str:
    """
    提取 PDF 文件中的文本内容
    :param pdf_file: 上传的 .pdf 文件对象
    :return: 提取的文本内容
    """
    try:
        # 使用 BytesIO 将上传的文件对象转为二进制流，并传递给 fitz
        doc = fitz.open(pdf_file)
        text = ""
        for page in doc:
            text += page.get_text()  # 提取文本
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF file: {str(e)}")


def extract_text_from_file(upload_file) -> str:
    """
    根据上传的文件对象类型识别文件并提取文本。
    :param upload_file: 上传的文件对象 (UploadFile)
    :return: 提取的文本内容
    """
    file_extension = os.path.splitext(upload_file.filename)[1].lower()  # 获取文件扩展名并转换为小写
    file_content = upload_file.file  # 获取文件的二进制内容

    if file_extension == '.docx':
        return extract_text_from_docx(file_content)
    elif file_extension == '.pdf':
        return extract_text_from_pdf(file_content)
    else:
        return f"Unsupported file type: {file_extension}"  # 对于其他文件类型，返回提示


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