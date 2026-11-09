import os
from typing import Generator, List, Dict, Any
from datetime import datetime

from agent.zhipuai_llm import ZhipuaiLLM
from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableBranch, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from DataProcess.zhipuai_embedding import ZhipuAIEmbeddings
from langchain_chroma import Chroma


def init_env(api_key: str):
    os.environ["ZHIPUAI_API_KEY"] = api_key


def get_zhipuai_llm(model_name: str = "glm-4-plus", temperature: float = 0.1, api_key: str = None) -> ZhipuaiLLM:
    if api_key is None:
        raise ValueError("API Key 未提供")
    return ZhipuaiLLM(model_name=model_name, temperature=temperature, api_key=api_key)

def get_retriever(persist_directory: str = r"data_base/vector_db/chroma") -> Any:
    embedding = ZhipuAIEmbeddings()
    vectordb = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding
    )
    return vectordb.as_retriever()

def combine_docs(docs: List[Any]) -> str:
    # 拼接多个文档内容
    return "\n\n".join(doc.page_content for doc in docs)

def get_qa_history_chain(api_key: str = None) -> RunnablePassthrough:
    if api_key is None:
        raise ValueError("API Key 未提供")
    init_env(api_key)
    llm = get_zhipuai_llm(api_key=api_key)
    retriever = get_retriever()

    condense_question_system_template = (
        "请根据聊天记录总结用户最近的问题，"
        "如果没有多余的聊天记录则返回用户的问题。"
    )
    condense_question_prompt = ChatPromptTemplate([
        ("system", condense_question_system_template),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
    ])

    # 检索逻辑
    retrieve_docs = RunnableBranch(
        (
            lambda x: not x.get("chat_history", False),
            (lambda x: x["input"]) | retriever,
        ),
        condense_question_prompt | llm | StrOutputParser() | retriever,
    )

    system_prompt = (
        "你是一个游戏信息问答任务的助手。"
        "请使用检索到的上下文片段回答这个问题。"
        "回答问题时以steam游戏小助手的身份可爱的回答。"
        "如果你不知道答案就说不知道。"
        "请确保回答是基于检索到的内容，而不是胡编乱造。"
        "并在回答末尾中给出多条给定数据中的内容作为依据，如游戏简介，玩家评价内容。\n\n"
        "{context}"
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
        ]
    )

    # 拼接上下文文档内容的辅助函数
    def assign_context(x):
        # x 是一个 dict，里面可能包含 context 和其它字段
        x["context"] = combine_docs(x.get("context", []))
        return x

    qa_chain = (
        RunnablePassthrough()
        .assign(context=retrieve_docs)
        | RunnableLambda(assign_context)
        | qa_prompt
        | llm
        | StrOutputParser()
    )

    # 组合一个可流式输出的链
    qa_history_chain = RunnablePassthrough().assign(
        context=retrieve_docs,
        answer=qa_chain
    )

    return qa_history_chain


def gen_response(chain: RunnablePassthrough, input: str, chat_history: List) -> Generator[str, None, None]:
    response_stream = chain.stream({
        "input": input,
        "chat_history": chat_history
    })
    for res in response_stream:
        answer = res.get("answer")
        if answer:
            yield answer


def retrieve_docs_for_question(question: str, persist_directory: str = r"data_base/vector_db/chroma") -> List[Any]:
    """
    根据用户问题，从向量数据库检索相关文档并返回。

    Args:
        question: 用户的查询问题字符串。
        persist_directory: 向量数据库持久化目录路径。

    Returns:
        List[Any]: 检索得到的文档列表，每个文档对象一般包含page_content属性。
    """
    retriever = get_retriever(persist_directory)
    docs = retriever.invoke(question)
    return docs