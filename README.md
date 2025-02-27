# CogniSync - 基于RAG增强智能文档问答系统

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68.0-green)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

基于RAG的增强文档理解与智能问答系统，实现跨文档语义检索和自然语言交互。
可用于搭建完全属于你个人的本地知识库！！！！

## ✨ 核心功能

- **多格式解析**：支持 PDF/DOCX/TXT 等常见文档格式
- **语义检索**：基于FAISS 向量数据库实现关键词搜索，能够智能检索最贴合你的问题的文档
- **智能问答**：DeepSeek 大模型驱动上下文感知问答
- **增量学习**：动态更新知识库无需全量重建
- **中文优化**：专为中文场景设计的文本预处理流程

## 🛠️ 技术栈

| 类别              | 技术组件                                                                 |
|-------------------|--------------------------------------------------------------------------|
| **后端框架**      | FastAPI                                                                 |
| **向量搜索**      | FAISS                                                                   |
| **NLP 模型**      | Sentence-BERT (paraphrase-multilingual-MiniLM-L12-v2)                   |
| **LLM 集成**      | DeepSeek API                                                            |
| **文本预处理**    | jieba / PDFMiner / python-docx                                          |
| **数据处理**      | numpy / pandas                                                          |
| **部署运维**      | Uvicorn / dotenv                                                        |

## 🚀 快速开始

### 环境准备

```bash
# 克隆项目
git clone https://github.com/yourusername/cognisync.git

# 安装依赖
推荐使用conda 创建虚拟环境
