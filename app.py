import streamlit as st   # 1️⃣ Streamlit UI 框架
import openai            # 2️⃣ OpenAI API
import pandas as pd      # 3️⃣ Excel 数据处理
import fitz              # 4️⃣ 解析 PDF
import docx              # 5️⃣ 解析 Word

# 6️⃣ 版本信息
VERSION = "1.5"

# 7️⃣ 读取 OpenAI API Key（优先从 Secrets 读取）
if "OPENAI_API_KEY" in st.secrets:  
    openai_api_key = st.secrets["OPENAI_API_KEY"]
else:
    import os
    openai_api_key = os.getenv("OPENAI_API_KEY", "sk-xxxx")  # 仅供本地测试

# 8️⃣ 确保 API Key 正确
if not openai_api_key or "sk-" not in openai_api_key:
    st.error("⚠️ 未检测到有效的 OpenAI API Key，请检查 `secrets.toml` 配置！")
    st.stop()

# 9️⃣ 创建 OpenAI 客户端
client = openai.OpenAI(api_key=openai_api_key)

# 🔹 **初始化 `session_state` 避免 AI 交互异常**
for key in ["chat_history", "uploaded_files_count", "file_data"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "chat_history" else "" if key == "file_data" else 0

# 🎨 自定义 ChatGPT 风格的 UI
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

# 1️⃣4️⃣ Streamlit UI 界面
st.title("💬 ChatGPT 风格 AI 交互分析")
st.write(f"📌 **版本 {VERSION}**")
st.write("上传 **Excel、Word、PDF**，AI 自动解析内容，并可进行交互式分析！")

# 1️⃣5️⃣ 上传文件
uploaded_files = st.file_uploader("📂 上传文件（可选多个）", accept_multiple_files=True, type=["xlsx", "docx", "pdf"])

if uploaded_files:
    file_contents = ""
    
    for uploaded_file in uploaded_files:
        file_type = uploaded_file.name.split(".")[-1]
        
        if file_type == "xlsx":
            file_contents += pd.read_excel(uploaded_file).to_string()
        elif file_type == "docx":
            file_contents += "\n".join([para.text for para in docx.Document(uploaded_file).paragraphs])
        elif file_type == "pdf":
            doc = fitz.open(uploaded_file)
            file_contents += "".join([page.get_text() for page in doc])

    # 1️⃣6️⃣ 保存解析数据
    st.session_state["file_data"] = file_contents
    st.session_state["uploaded_files_count"] = len(uploaded_files)

    # 1️⃣7️⃣ AI 生成初步分析
    if st.button("📊 生成 AI 分析"):
        with st.spinner("AI 正在分析文件，请稍候..."):
            analysis_result = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "system", "content": "你是一个财务分析专家，请根据用户提供的文件数据进行分析。"},
                          {"role": "user", "content": file_contents}]
            ).choices[0].message.content
        st.success("✅ AI 分析完成！")
        st.session_state["chat_history"].append(("AI", analysis_result))
        st.write(analysis_result)

# 💬 ChatGPT 风格 AI 交互
st.subheader("💬 AI 交互分析")

# 📜 显示历史对话
if st.session_state["chat_history"]:
    for role, msg in st.session_state["chat_history"]:
        role_class = "stChatMessageUser" if role == "用户" else "stChatMessageAssistant"
        with st.container():
            st.markdown(f'<div class="stChatMessage {role_class}">{msg}</div>', unsafe_allow_html=True)

# 📝 用户输入问题
user_input = st.chat_input("请输入你的问题...")
if user_input:
    chat_prompt = f"文件数据：\n{st.session_state['file_data']}\n\n用户问题：{user_input}"
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "你是一个财务分析专家，请根据用户提供的文件数据进行分析。"},
                  {"role": "user", "content": chat_prompt}]
    ).choices[0].message.content
    
    st.session_state["chat_history"].append(("用户", user_input))
    st.session_state["chat_history"].append(("AI", response))
    st.rerun()  # ✅ 修复 `st.experimental_rerun()` 问题