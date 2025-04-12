import streamlit as st
import pandas as pd
import io

# ✅ ページ設定（必ず最初）
st.set_page_config(page_title="Excel/CSV 比較アプリ v3.4", layout="wide")

# ✅ 強制ライトテーマ風CSS（チェックボックス黒文字）
st.markdown("""
<style>
body {
    background-color: white !important;
    color: black !important;
}
div[class*="stCheckbox"] > label {
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Excel / CSV 比較アプリ（v3.4 最終版）")
st.caption("✔ ✅も色つき表示｜✔ テーマをライトに固定｜✔ 片方だけのデータも比較OK")

# アップロード
file1 = st.file_uploader("📄 ファイル①", type=["csv", "xlsx"], key="file1")
file2 = st.file_uploader("📄 ファイル②", type=["csv", "xlsx"], key="file2")

# A列B列表示用関数
def num_to_col_letter(n):
    result = ''
    while n >= 0:
        result = chr(n % 26 + 65) + result
        n = n // 26 - 1
    return result

# シート取得関数
def get_sheet_names(uploaded_file):
    xls = pd.ExcelFile(io.BytesIO(uploaded_file.read()))
    return xls.sheet_names

# ファイル読み込み関数
def read
