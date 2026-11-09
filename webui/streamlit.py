import streamlit as st
from agent.zhipu_fuc import gen_response, get_qa_history_chain, retrieve_docs_for_question
from api_config.api import ZHIYUAI_API_KEY

st.set_page_config(page_title="Steam 小助手", layout="wide")

# 自定义样式
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .chat-message {
        padding: 0.5rem;
        border-radius: 1rem;
        margin-bottom: 0.5rem;
    }
    .chat-message.user {
        background-color: #DCF8C6;
        text-align: right;
    }
    .chat-message.ai {
        background-color: #F1F0F0;
        text-align: left;
    }
    [data-testid="stChatMessageAvatar"] img {
        width: 64px !important;
        height: 64px !important;
        border-radius: 50% !important;
        object-fit: cover;
    }
</style>
""", unsafe_allow_html=True)

USER_AVATAR = "👤"
AI_AVATAR = "🤖"

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            ("ai", "你好！我是Steam小助手，可以帮你找游戏、查折扣、回答各种Steam相关问题～🎮")
        ]
    if "qa_history_chain" not in st.session_state:
        st.session_state.qa_history_chain = get_qa_history_chain(api_key=ZHIYUAI_API_KEY)
    if "retrieved_docs_texts" not in st.session_state:
        st.session_state.retrieved_docs_texts = []

def render_messages(container):
    for role, content in st.session_state.messages:
        avatar = USER_AVATAR if role == "human" else AI_AVATAR
        with container.chat_message(role, avatar=avatar):
            st.markdown(content)

def render_docs():
    with right_col:
        with st.container(height=856):
            st.markdown("### 🔍 检索到的信息")
            if st.session_state.retrieved_docs_texts:
                for idx, doc_text in enumerate(st.session_state.retrieved_docs_texts, 1):
                    st.markdown(f"**信息 {idx}:**")
                    st.markdown(doc_text)
            else:
                st.markdown("_暂无检索信息_")

def main():
    st.markdown("### 🎮 Steam小助手")
    initialize_session_state()

    global left_col, right_col  # 为了 render_docs() 使用
    left_col, right_col = st.columns([3,1])

    prompt=0
    with left_col:
        prompt = st.chat_input("嗨！想问点什么？比如游戏推荐、折扣、攻略……")
        with st.container(height=800):
            messages_container = st.container()

            # 渲染欢迎语和历史消息
            render_messages(messages_container)


            if prompt:
                # 立即渲染用户输入
                with left_col:
                    with messages_container.chat_message("human", avatar=USER_AVATAR):
                        st.markdown(prompt)

                # 检索文档并保存
                docs = retrieve_docs_for_question(prompt)
                st.session_state.retrieved_docs_texts = [doc.page_content for doc in docs]

                # 右侧立即展示
                render_docs()

                # 流式生成 AI 回答
                with left_col:
                    with messages_container.chat_message("ai", avatar=AI_AVATAR):
                        response_placeholder = st.empty()
                        answer_chunks = []
                        for chunk in gen_response(st.session_state.qa_history_chain, prompt, st.session_state.messages):
                            answer_chunks.append(chunk)
                            response_placeholder.markdown("".join(answer_chunks))
                        full_answer = "".join(answer_chunks)

                # 最后保存到会话记录
                st.session_state.messages.append(("human", prompt))
                st.session_state.messages.append(("ai", full_answer))

            else:
                # 初始时展示右栏信息（如果前面有对话过）
                render_docs()

if __name__ == "__main__":
    main()
