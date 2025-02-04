import streamlit as st
import openai
import pandas as pd
import fitz  # 解析 PDF
import docx  # 解析 Word

# 🔹 读取 API Key（优先从 Secrets 读取）
if "OPENAI_API_KEY" in st.secrets:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
else:
    import os
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-xxxx")  # 仅供本地测试

# 🔹 初始化会话存储
if "file_data" not in st.session_state:
    st.session_state.file_data = ""

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 🔹 调用 OpenAI 进行 AI 分析
def ask_chatgpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        api_key=OPENAI_API_KEY
    )
    return response["choices"][0]["message"]["content"]

# 🔹 解析 Excel
def read_excel(file):
    df = pd.read_excel(file)
    return df.to_string()

# 🔹 解析 Word
def read_word(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

# 🔹 解析 PDF
def read_pdf(file):
    doc = fitz.open(file)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# 🔹 Streamlit 界面
st.title("📊 AI 财务文件分析助手")
st.write("上传 **Excel、Word、PDF**，AI 自动解析内容，并可进行交互式分析！")

# 🔹 上传文件
uploaded_files = st.file_uploader("📂 上传文件（可选多个）", accept_multiple_files=True, type=["xlsx", "docx", "pdf"])

if uploaded_files:
    file_contents = ""
    
    for uploaded_file in uploaded_files:
        file_type = uploaded_file.name.split(".")[-1]
        
        if file_type == "xlsx":
            file_contents += read_excel(uploaded_file)
        elif file_type == "docx":
            file_contents += read_word(uploaded_file)
        elif file_type == "pdf":
            file_contents += read_pdf(uploaded_file)

    # 🔹 保存解析数据
    st.session_state.file_data = file_contents

    # 🔹 AI 生成初步分析
    if st.button("📊 生成 AI 分析"):
        with st.spinner("AI 正在分析文件，请稍候..."):
            analysis_result = ask_chatgpt(file_contents)
        st.success("✅ AI 分析完成！")
        st.session_state.chat_history.append(("AI", analysis_result))
        st.write(analysis_result)

# 🔹 AI 交互对话框（始终显示）
st.subheader("💬 AI 交互分析")

# 显示历史对话
if st.session_state.chat_history:
    for role, msg in st.session_state.chat_history:
        if role == "用户":
            st.markdown(f"👤 **用户**: {msg}")
        else:
            st.markdown(f"🤖 **AI**: {msg}")

# 用户输入问题
user_input = st.text_input("📝 请输入你的问题（基于已上传文件进行分析）", "")

# 处理 AI 回答
if user_input:
    chat_prompt = f"文件数据：\n{st.session_state.file_data}\n\n用户问题：{user_input}"
    response = ask_chatgpt(chat_prompt)
    st.session_state.chat_history.append(("用户", user_input))
    st.session_state.chat_history.append(("AI", response))
    st.experimental_rerun()  # 触发页面更新，防止刷新后历史消失