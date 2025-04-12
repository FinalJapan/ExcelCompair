import streamlit as st
import pandas as pd
import io

# ✅ ✅ ✅ 必ずこの位置に！
st.set_page_config(page_title="Excel/CSV 比較アプリ v3.2", layout="wide")

# ✅ UIカスタムCSS（その後でOK）
st.markdown("""
<style>
div[class*="stCheckbox"] > label {
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Excel / CSV ファイル 比較アプリ（v3.2 最終版）")
st.caption("✔ 複数シート対応｜✔ 並べ替え｜✔ アルファベット列名｜✔ UI見やすさ改善")

# ファイルアップロード
file1 = st.file_uploader("📄 ファイル①", type=["csv", "xlsx"], key="file1")
file2 = st.file_uploader("📄 ファイル②", type=["csv", "xlsx"], key="file2")

# 列番号 → A列B列変換
def num_to_col_letter(n):
    result = ''
    while n >= 0:
        result = chr(n % 26 + 65) + result
        n = n // 26 - 1
    return result

# シート名取得
def get_sheet_names(uploaded_file):
    xls = pd.ExcelFile(io.BytesIO(uploaded_file.read()))
    return xls.sheet_names

# ファイル読み込み
def read_file(uploaded_file, sheet_name=None):
    uploaded_file.seek(0)
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(io.StringIO(uploaded_file.read().decode("cp932", errors="ignore")))
    else:
        return pd.read_excel(io.BytesIO(uploaded_file.read()), sheet_name=sheet_name)

# シート選択
sheet1 = None
sheet2 = None
if file1 and file1.name.endswith(".xlsx"):
    sheet_names1 = get_sheet_names(file1)
    sheet1 = st.selectbox("🗂 ファイル①のシート", sheet_names1, key="sheet1")
if file2 and file2.name.endswith(".xlsx"):
    sheet_names2 = get_sheet_names(file2)
    sheet2 = st.selectbox("🗂 ファイル②のシート", sheet_names2, key="sheet2")

# 両ファイルあり → メイン処理
if file1 and file2:
    df1 = read_file(file1, sheet1)
    df2 = read_file(file2, sheet2)

    st.success("✅ ファイル読み込み成功！")

    st.subheader("🔍 比較する列を選んでください")

    # 比較列選択（A列表示）
    col_options1 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df1.columns)]
    selected1 = st.selectbox("ファイル①の列", options=col_options1, key="col_1")
    col1 = df1.columns[[i for i, s in enumerate(col_options1) if s == selected1][0]]

    col_options2 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df2.columns)]
    selected2 = st.selectbox("ファイル②の列", options=col_options2, key="col_2")
    col2 = df2.columns[[i for i, s in enumerate(col_options2) if s == selected2][0]]

    # 比較処理
    compare_len = min(len(df1), len(df2))
    col_name1 = file1.name
    col_name2 = file2.name

    comparison_result = pd.DataFrame({
        col_name1: df1[col1].iloc[:compare_len].astype(str),
        col_name2: df2[col2].iloc[:compare_len].astype(str)
    })
    comparison_result["一致しているか"] = comparison_result[col_name1] == comparison_result[col_name2]

    # 並べ替え
    st.subheader("🔀 並べ替え設定")
    sort_column = st.selectbox("並べ替える列", comparison_result.columns, key="sort_column")
    sort_order = st.radio("並び順", ["昇順", "降順"], horizontal=True, key="sort_order")
    is_ascending = sort_order == "昇順"
    sorted_result = comparison_result.sort_values(by=sort_column, ascending=is_ascending)

    # 色つき表示（淡くて文字は黒）
    def highlight_diff(row):
    styles = []
    for col in row.index:
        if col == "一致しているか":
            styles.append("")  # デフォルトのまま（背景色なし）
        elif row["一致しているか"]:
            styles.append("background-color: #f2fdf2; color: black")  # 淡い緑
        else:
            styles.append("background-color: #fdf2f2; color: black")  # 淡い赤
    return styles


    st.subheader("📋 比較結果")
    st.dataframe(sorted_result.style.apply(highlight_diff, axis=1), use_container_width=True)

    # ダウンロード
    csv = sorted_result.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 結果をCSVでダウンロード",
        data=csv,
        file_name="比較結果.csv",
        mime="text/csv"
    )
