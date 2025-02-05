import streamlit as st
import requests

# 设置页面基本信息
st.set_page_config(page_title="AI Chat", layout="wide")

# 自定义 ChatGPT 网页版风格的界面样式
st.markdown(
    """
    <style>
        body {background-color: #F0F2F6; color: black;}
        .stTextInput > div > div > input {background-color: #FFFFFF; color: black; border: 1px solid #CCCCCC;}
        .stButton > button {background-color: #10A37F; color: white; border-radius: 5px; padding: 10px;}
        .stChatMessage {padding: 10px; margin: 5px 0; border-radius: 5px;}
        .stChatMessageUser {background-color: #E5E5EA; color: black;}
        .stChatMessageAssistant {background-color: #10A37F; color: white;}
    </style>
    """,
    unsafe_allow_html=True
)

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for message in st.session_state.messages:
    role_class = "stChatMessageUser" if message["role"] == "user" else "stChatMessageAssistant"
    with st.container():
        st.markdown(f'<div class="stChatMessage {role_class}">{message["content"]}</div>', unsafe_allow_html=True)

# 用户输入
user_input = st.chat_input("请输入你的问题...")
if user_input:
    # 记录用户消息
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.container():
        st.markdown(f'<div class="stChatMessage stChatMessageUser">{user_input}</div>', unsafe_allow_html=True)
    
    # 发送请求到 API
    response = requests.get(f"http://your-aws-ec2-ip:8000/ask/?question={user_input}")
    ai_response = response.json().get("answer", "AI 没有返回结果。")
    
    # 记录 AI 消息
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    with st.container():
        st.markdown(f'<div class="stChatMessage stChatMessageAssistant">{ai_response}</div>', unsafe_allow_html=True)
