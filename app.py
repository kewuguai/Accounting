import streamlit as st   # 1️⃣ Streamlit UI 框架
import openai            # 2️⃣ OpenAI API
import pandas as pd      # 3️⃣ Excel 数据处理
import fitz              # 4️⃣ 解析 PDF
import docx              # 5️⃣ 解析 Word

# 6️⃣ 版本信息
VERSION = "1.6"

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
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "uploaded_files_count" not in st.session_state:
    st.session_state["uploaded_files_count"] = 0  

if "last_user_input" not in st.session_state:
    st.session_state["last_user_input"] = None  # ✅ 记录上次输入，防止重复提交

# 1️⃣0️⃣ 解析 Excel
def read_excel(file):
    df = pd.read_excel(file)
    return df.to_string()

# 1️⃣1️⃣ 解析 Word
def read_word(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

# 1️⃣2️⃣ 解析 PDF
def read_pdf(file):
    doc = fitz.open(file)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# 1️⃣3️⃣ 调用 OpenAI 进行 AI 分析
def ask_chatgpt(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "你是一个财务分析专家，请根据用户提供的文件数据进行分析。"},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except openai.OpenAIError as e:
        return f"⚠️ OpenAI API 请求失败: {e}"

# 1️⃣4️⃣ Streamlit UI 界面
st.title("📊 AI 财务文件分析助手")
st.write(f"📌 **版本 {VERSION}**")
st.write("上传 **Excel、Word、PDF**，AI 自动解析内容，并可进行交互式分析！")

# 1️⃣5️⃣ 上传文件
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

    # 1️⃣6️⃣ 保存解析数据
    st.session_state["file_data"] = file_contents
    st.session_state["uploaded_files_count"] = len(uploaded_files)

    # 1️⃣7️⃣ AI 生成初步分析
    if st.button("📊 生成 AI 分析"):
        with st.spinner("AI 正在分析文件，请稍候..."):
            analysis_result = ask_chatgpt(file_contents)
        st.success("✅ AI 分析完成！")
        st.session_state["chat_history"].append(("AI", analysis_result))
        st.write(analysis_result)

# 1️⃣8️⃣ AI 交互对话框（始终显示）
st.subheader("💬 AI 交互分析")

# 1️⃣9️⃣ 显示历史对话
if st.session_state["chat_history"]:
    for role, msg in st.session_state["chat_history"]:
        if role == "用户":
            st.markdown(f"👤 **用户**: {msg}")
        else:
            st.markdown(f"🤖 **AI**: {msg}")

# 2️⃣0️⃣ 用户输入问题
user_input = st.text_input("📝 请输入你的问题（基于已上传文件进行分析）", "")

# 2️⃣1️⃣ 处理 AI 回答
if user_input and user_input != st.session_state["last_user_input"]:
    st.session_state["last_user_input"] = user_input  # ✅ 记录输入，防止重复提交

    # 2️⃣2️⃣ 处理 "我上传了多少份文件？" 问题
    if user_input.lower() in ["我上传了多少份文件？", "我上传了几份文件？"]:
        response = f"✅ 您已上传 {st.session_state['uploaded_files_count']} 份文件。"
    else:
        chat_prompt = f"文件数据：\n{st.session_state['file_data']}\n\n用户问题：{user_input}"
        response = ask_chatgpt(chat_prompt)

    st.session_state["chat_history"].append(("用户", user_input))
    st.session_state["chat_history"].append(("AI", response))
    
    # ✅ 只在用户输入新问题后触发 `rerun`
    st.experimental_set_query_params(refresh="true")