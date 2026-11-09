from typing import List, Dict, Any
from DataProcess.config import CHUNK_SIZE, OVERLAP_SIZE
from langchain_text_splitters import RecursiveCharacterTextSplitter

MAX_LENGTH_PER_FIELD = {
    "name": 40,
    "full_description": 100,
    "price": 30,
    "tags": 40,
    "user_reviews": 250,
    "review": 50,
}
DEFAULT_MAX_LENGTH = 80
MAX_DOC_CONTENT_LENGTH = 800



def truncate_text(text: str, max_length: int) -> str:
    if not text:
        return ""
    text = text.strip()
    return text if len(text) <= max_length else text[:max_length] + "..."

def format_reviews(reviews: List[Dict[str, Any]], max_length_per_review: int, max_reviews: int = 5) -> str:
    review_texts = []
    for review in reviews[:max_reviews]:
        content = review.get("review", "")
        truncated = truncate_text(content, max_length_per_review)
        review_texts.append(f"- {truncated}")
    return "\n".join(review_texts)

def json_to_docs(json_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    docs = []
    for item in json_data:
        steamid = str(item.get('steamid', 'unknown'))
        info = item.get('info', {})

        content_parts = []
        for field, value in info.items():
            # 取默认长度
            max_len = MAX_LENGTH_PER_FIELD.get(field, DEFAULT_MAX_LENGTH)

            if field == "user_reviews" and isinstance(value, list):
                # 这里用 review 字段的限制长度截断每条评论
                max_len_review = MAX_LENGTH_PER_FIELD.get("review", 30)
                value_str = format_reviews(value, max_len_review, max_reviews=5)
            elif isinstance(value, list):
                value_str = "\n".join(str(v).strip() for v in value if v is not None)
            elif value is None:
                value_str = ""
            else:
                value_str = str(value).strip()

            truncated_text = truncate_text(value_str, max_len)
            content_parts.append(f"{field}:\n{truncated_text}")

        # 拼接后保险截断
        full_content = truncate_text("\n\n".join(content_parts), MAX_DOC_CONTENT_LENGTH)
        docs.append({
            "id": steamid,
            "content": full_content
        })

    docs = [doc for doc in docs if doc.get("content", "").strip()]

    return docs


"""
def json_to_docs(json_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    
    将 JSON 数据转为分块文本文档。
    针对每个字段做长度限制后拼接，再用 RecursiveCharacterTextSplitter 分块。

    :param json_data: 加载后的 JSON 数据列表
    :return: [{'id': str, 'content': str}, ...] 文档列表
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=OVERLAP_SIZE
    )
    docs = []

    for item in json_data:
        steamid = str(item.get('steamid', 'unknown'))
        info = item.get('info', {})

        content_parts = []
        for field, value in info.items():
            max_len = MAX_LENGTH_PER_FIELD.get(field, DEFAULT_MAX_LENGTH)

            # 统一转换为字符串并处理列表类型
            if isinstance(value, list):
                # 过滤 None 值，转为字符串，拼接换行
                value_str = "\n".join(str(v).strip() for v in value if v is not None)
            elif value is None:
                value_str = ""
            else:
                value_str = str(value).strip()

            truncated_text = truncate_text(value_str, max_len)
            content_parts.append(f"{field}:\n{truncated_text}")

        full_content = "\n\n".join(content_parts)
        chunks = text_splitter.split_text(full_content)

        for idx, chunk in enumerate(chunks):
            docs.append({
                "id": f"{steamid}_{idx}",
                "content": chunk
            })

    return docs

"""