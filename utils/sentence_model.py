from sentence_transformers import SentenceTransformer

# 本地模型路径
LOCAL_MODEL_PATH = './local_model'
MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'  # 更新为你想使用的多语言模型

# 加载模型并缓存到本地
def load_model(local_model_path=LOCAL_MODEL_PATH):
    """
    加载本地或远程 Sentence-BERT 模型。
    如果模型在本地已下载，则加载本地模型，否则从 Hugging Face 下载模型。
    """
    try:
        # 尝试加载本地模型
        model = SentenceTransformer(local_model_path)
        print(f"Loaded model from local path: {local_model_path}")
    except Exception as e:
        # 如果加载本地模型失败，则从远程下载模型
        print(f"Loading model from remote. Error: {e}")
        model = SentenceTransformer(MODEL_NAME)  # 使用指定的模型
        model.save(local_model_path)  # 将模型缓存到本地
        print(f"Model downloaded and cached to: {local_model_path}")

    return model

# 生成文本向量
def encode_text(model, text: str):
    """
    将文本转化为向量。
    :param model: 加载的 Sentence-BERT 模型
    :param text: 要转化的文本
    :return: 文本的向量表示
    """
    vector = model.encode([text])[0]
    return vector

# 支持批量文本编码
def encode_texts(model, texts: list):
    """
    将多个文本转化为向量。
    :param model: 加载的 Sentence-BERT 模型
    :param texts: 要转化的文本列表
    :return: 文本的向量表示列表
    """
    vectors = model.encode(texts)
    return vectors

# 获取已加载的模型
def get_model():
    """
    获取已加载的模型实例（如果没有加载，则进行加载）
    """
    model = load_model()  # 使用默认本地路径加载
    return model