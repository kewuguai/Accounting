import streamlit as st
import openai
import pandas as pd
import fitz  # 解析 PDF
import docx  # 解析 Word

# 🔹 读取 API Key（先留空，后面会在 Streamlit Secrets 里配置）
OPENAI_API_KEY = ""

def ask_chatgpt(prompt):
    """调用 OpenAI API 进行 AI 分析"""
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        api_key=OPENAI_API_KEY
    )
    return response["choices"][0]["message"]["content"]

# 读取 Excel 文件
def read_excel(file):
    df = pd.read_excel(file)
    return df.to_string()

# 读取 Word 文件
def read_word(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

# 读取 PDF 文件
def read_pdf(file):
    doc = fitz.open(file)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Streamlit 界面
st.title("📊 AI 文件分析助手")
st.write("上传你的 **Excel、Word、PDF**，AI 将自动解析内容，找出规律！")

# 文件上传
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

    # AI 分析
    if st.button("📊 生成 AI 分析"):
        with st.spinner("AI 正在分析文件，请稍候..."):
            analysis_result = ask_chatgpt(file_contents)
        st.success("✅ AI 分析完成！")
        st.write(analysis_result)