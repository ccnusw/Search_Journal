import streamlit as st
import pandas as pd
import os

# 设置页面配置必须是第一行执行的Streamlit命令
st.set_page_config(page_title="《澳门语言学刊》检索系统", layout="wide")

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
    raise ValueError(f"无法读取文件 {file_path}，请检查文件编码和列名")

# 检索函数
def search_data(data, keyword, year, article_type, author):
    if keyword:
        data = data[data['标题'].str.contains(keyword.strip(), na=False)]
    if year:
        data = data[data['年份'] == year]
    if article_type:
        data = data[data['文章类型'].apply(lambda x: x.strip()) == article_type.strip()]
    if author:
        data = data[data['作者'].str.contains(author.strip(), na=False)]
    return data

# 主标题和简介
st.markdown("<h3 style='text-align: center;'>🔎《澳门语言学刊》检索系统</h3>", unsafe_allow_html=True)
st.write("")  # 空行

# 加载数据
data = load_data(csv_file_path)

# 初始化分页状态
if 'page_number' not in st.session_state:
    st.session_state.page_number = 1

# 初始化检索状态
if 'search' not in st.session_state:
    st.session_state.search = False

# 获取年份选项和文章类型选项
year_options = [""] + list(range(1995, 2025))
article_types = [""] + list(data['文章类型'].unique())

# 设置检索条件布局
search_cols = st.columns([3, 2, 3, 3, 3])
with search_cols[0]:
    keyword = st.text_input("关键词", value=st.session_state.get('keyword', ""))
with search_cols[1]:
    year = st.selectbox("年份", options=year_options, index=year_options.index(st.session_state.get('year', "")))
with search_cols[2]:
    article_type = st.selectbox("文章类型", options=article_types, index=article_types.index(st.session_state.get('article_type', "")))
with search_cols[3]:
    author = st.text_input("作者", value=st.session_state.get('author', ""))
with search_cols[4]:
    st.write("")  # 空行
    st.write("")  # 空行
    search_reset_cols = st.columns([1, 1])
    with search_reset_cols[0]:
        if st.button("检索", key='search_button', help="点击进行检索", use_container_width=True):
            if keyword.strip() or year or article_type.strip() or author.strip():
                st.session_state.keyword = keyword
                st.session_state.year = year
                st.session_state.article_type = article_type
                st.session_state.author = author
                st.session_state.search = True
                st.session_state.page_number = 1  # 每次新检索时重置页码
            else:
                st.error("至少填写一个搜索条件。")
    with search_reset_cols[1]:
        if st.button("重置", key='reset_button', help="点击重置检索条件", use_container_width=True):
            st.session_state.keyword = ""
            st.session_state.year = ""
            st.session_state.article_type = ""
            st.session_state.author = ""
            st.session_state.search = False
            st.session_state.page_number = 1
            st.experimental_rerun()

# 只有在用户输入检索条件后并点击检索按钮后才进行检索和显示结果
if st.session_state.search:
    # 检索数据
    filtered_data = search_data(data, st.session_state.keyword, st.session_state.year, st.session_state.article_type, st.session_state.author)

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

    # 使用 HTML 和 CSS 居中表格并调整列宽
    st.markdown("""
    <style>
    .center-table {
        margin-left: auto;
        margin-right: auto;
        width: 90%; /* 调整表格宽度 */
        border-collapse: collapse;
    }
    .center-table th, .center-table td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center; /* 将文本居中显示 */
        white-space: normal; /* 允许文本换行 */
        vertical-align: middle; /* 确保垂直居中 */
    }
    .center-table th {
        background-color: #f2f2f2;
    }
    .center-table th:nth-child(1), .center-table th:nth-child(4), .center-table th:nth-child(5) { /* 序号、年份、期数列宽调整 */
        white-space: nowrap; /* 防止这些列的头部分行显示 */
        width: 80px; /* 调整宽度 */
    }
    .center-table td:nth-child(1), .center-table td:nth-child(4), .center-table td:nth-child(5) { /* 序号、年份、期数内容调整 */
        white-space: nowrap; /* 防止内容分行显示 */
        width: 80px; /* 调整宽度 */
    }
    .center-table td:nth-child(2) { /* 标题列宽调整 */
        width: 20%; /* 减小宽度 */
    }
    .center-table td:nth-child(5) { /* 期数列宽调整 */
        width: 80px; /* 增大宽度以适应内容 */
    }
    .center-table td:nth-child(6) { /* 引用格式列特殊处理 */
        text-align: left; /* 引用格式内容靠左显示 */
    }
    </style>
    """, unsafe_allow_html=True)

    table_data = filtered_data.iloc[start_idx:end_idx][['新序号', '标题', '作者', '年份', '期数', '引用格式']].rename(columns={'新序号': '序号'})
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
    Copyright © 2024-长期 版权所有：《澳门语言学刊》编辑部
    本检索系统由澳门大学人文学院访问学者沈威制作，在使用中如果有任何问题可以发邮件至：sw@ccnu.edu.cn
</div>
""", unsafe_allow_html=True)
