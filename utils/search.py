import os
import whoosh.index as index
from whoosh.fields import Schema, TEXT
from whoosh.qparser import QueryParser

# 创建索引目录
def create_index(index_dir):
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)
        schema = Schema(content=TEXT(stored=True))
        idx = index.create_in(index_dir, schema)
        return idx
    else:
        return index.open_dir(index_dir)

# 索引数据
def index_data(index_dir, text):
    idx = create_index(index_dir)
    writer = idx.writer()
    writer.add_document(content=text)
    writer.commit()

# 搜索相关文件
def search_related_files(query_text, index_dir):
    idx = create_index(index_dir)
    with idx.searcher() as searcher:
        query = QueryParser("content", idx.schema).parse(query_text)
        results = searcher.search(query, limit=5)
        return [hit["content"] for hit in results]