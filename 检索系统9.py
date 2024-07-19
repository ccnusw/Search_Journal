import streamlit as st
import pandas as pd
import os

# 确保当前工作目录是脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.join(current_dir, "journals.csv")

# 加载数据
@st.cache_data
def load_data(file_path):
    # 尝试多种编码读取文件
    encodings = ['utf-8', 'ISO-8859-1', 'gbk']
    for encoding in encodings:
        try:
            data = pd.read_csv(file_path, encoding=encoding, usecols=['序号', '标题', '作者', '文章类型', '年份', '期数', '引用格式'])
            return data
        except (UnicodeDecodeError, ValueError):
            continue
    # 如果所有尝试都失败，抛出错误
    raise ValueError(f"无法读取文件 {file_path}，请检查文件编码和列名")

# 检索函数
def search_data(data, keyword, year, article_type, author):
    if keyword:
        data = data[data['标题'].str.contains(keyword, na=False)]
    if year:
        data = data[data['年份'] == year]
    if article_type:
        data = data[data['文章类型'] == article_type]
    if author:
        data = data[data['作者'].str.contains(author, na=False)]
    return data

# 设置页面配置
st.set_page_config(page_title="《澳门语言学刊》检索系统", layout="wide")

# 主标题和简介
st.markdown("<h3 style='text-align: center;'>🔎《澳门语言学刊》检索系统</h3>", unsafe_allow_html=True)
st.write("")  # 空行
st.write("")  # 空行
st.write("")  # 空行

# 加载数据
data = load_data(csv_file_path)

# 初始化分页状态
if 'page_number' not in st.session_state:
    st.session_state.page_number = 1

# 初始化检索状态
if 'search' not in st.session_state:
    st.session_state.search = False

# 设置检索条件布局
search_cols = st.columns([3, 2, 3, 3, 1.5])
with search_cols[0]:
    keyword = st.text_input("关键词")
with search_cols[1]:
    year = st.selectbox("年份", options=[""] + list(range(1995, 2025)))
with search_cols[2]:
    article_type = st.selectbox("文章类型", options=["", "句法学与语义学", "语音学与音系学", "词汇学与辞书学", "修辞学与语用学", "语言接触与语言变异", "汉语史", "文字学", "应用语言学", "其他"])
with search_cols[3]:
    author = st.text_input("作者")
with search_cols[4]:
    st.write("")  # 空行，用于调整按钮位置
    st.write("")  # 空行，用于调整按钮位置
    search_button = st.button("检索")

# 检索按钮触发
if search_button:
    st.session_state.page_number = 1  # 每次新检索时重置页码
    st.session_state.search = True  # 更新检索状态

# 只有在用户输入检索条件后并点击检索按钮后才进行检索和显示结果
if st.session_state.search:
    # 检索数据
    filtered_data = search_data(data, keyword, year, article_type, author)

    # 显示结果
    total_results = len(filtered_data)
    st.write(f"检索结果总数: {total_results}")

    # 分页展示
    page_size = 15
    total_pages = (total_results // page_size) + 1
    page_number = st.session_state.page_number

    start_idx = (page_number - 1) * page_size
    end_idx = start_idx + page_size

    # 对检索结果重新编号
    filtered_data = filtered_data.reset_index(drop=True)
    filtered_data.index += 1
    filtered_data['新序号'] = filtered_data.index

    # 显示数据表
    table_data = filtered_data.iloc[start_idx:end_idx][['新序号', '引用格式']].rename(columns={'新序号': '序号'})

    # 使用 HTML 和 CSS 居中表格并调整列宽
    st.markdown("""
    <style>
    .center-table {
        margin-left: auto;
        margin-right: auto;
        width: 80%;
        border-collapse: collapse;
    }
    .center-table th, .center-table td {
        border: 1px solid #ddd;
        padding: 8px;
    }
    .center-table th {
        text-align: center;
        background-color: #f2f2f2;
    }
    .center-table td {
        text-align: left;
    }
    .center-table td:nth-child(1) {
        width: 60px;
        text-align: center;
    }
    .center-table td:nth-child(2) {
        width: 500px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(table_data.to_html(index=False, classes='center-table'), unsafe_allow_html=True)

    # 分页按钮显示在文件详细信息上方
    button_cols = st.columns([1, 1, 1, 1, 1, 1, 1, 1], gap="small")
    with button_cols[2]:
        if page_number > 1:
            if st.button("首页"):
                st.session_state.page_number = 1
                st.experimental_rerun()
    with button_cols[3]:
        if page_number > 1:
            if st.button("上一页"):
                st.session_state.page_number -= 1
                st.experimental_rerun()
    with button_cols[4]:
        if page_number < total_pages:
            if st.button("下一页"):
                st.session_state.page_number += 1
                st.experimental_rerun()
    with button_cols[5]:
        if page_number < total_pages:
            if st.button("末页"):
                st.session_state.page_number = total_pages
                st.experimental_rerun()

    # 显示引用格式
    if not filtered_data.empty:
        st.write('<div style="font-size:12px;">文章详细信息:</div>', unsafe_allow_html=True)
        for i in range(start_idx, min(end_idx, total_results)):
            row = filtered_data.iloc[i]
            st.write(f'<div style="font-size:14px;">({i+1}) 标题: {row["标题"]}</div>', unsafe_allow_html=True)
            st.write(f'<div style="font-size:14px;">作者: {row["作者"]}</div>', unsafe_allow_html=True)
            st.write(f'<div style="font-size:14px;">文章类型: {row["文章类型"]}</div>', unsafe_allow_html=True)
            st.write(f'<div style="font-size:14px;">年份: {row["年份"]}</div>', unsafe_allow_html=True)
            st.write(f'<div style="font-size:14px;">期数: {row["期数"]}</div>', unsafe_allow_html=True)
            st.write(f'<div style="font-size:14px;">引用格式: {row["引用格式"]}</div>', unsafe_allow_html=True)
            st.write('<hr>', unsafe_allow_html=True)

# 添加分割线和版权信息，固定在页面底部
st.markdown("""
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: white;
    text-align: center;
    padding: 10px 0;
    border-top: 1px solid #ddd;
    font-family: KaiTi;
}
.email {
    font-family: KaiTi,Times New Roman;
}
</style>
<div class="footer">
    <div>Copyright © 2024-长期 版权所有：《澳门语言学刊》编辑部</div>
    <div>本检索系统由澳门大学人文学院访问学者沈威制作，在使用中如果有任何问题可以发邮件至：sw@ccnu.edu.cn</div>
</div>
""", unsafe_allow_html=True)
