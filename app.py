import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Excel/CSV 比較アプリ v4.2", layout="wide")

st.markdown("""
<style>
div[class*="stCheckbox"] > label {
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Excel / CSV 比較アプリ（v4.2 空欄削除対応）")
st.caption("✔ 空白行は非表示｜✔ ✅/❌比較｜✔ 最小構成の超安定版")

file1 = st.file_uploader("📄 ファイル①", type=["csv", "xlsx"])
file2 = st.file_uploader("📄 ファイル②", type=["csv", "xlsx"])

def load_file(file):
    return io.BytesIO(file.read())

def read_file(file_data, filename, sheet_name=None):
    if filename.endswith(".csv"):
        return pd.read_csv(io.StringIO(file_data.getvalue().decode("cp932", errors="ignore")))
    else:
        return pd.read_excel(file_data, sheet_name=sheet_name)

def get_sheet_names(file_data):
    return pd.ExcelFile(file_data).sheet_names

if file1 and file2:
    file1_data = load_file(file1)
    file2_data = load_file(file2)

    sheet1 = sheet2 = None
    if file1.name.endswith(".xlsx"):
        sheet1 = st.selectbox("🗂 ファイル①のシート", get_sheet_names(file1_data), key="sheet1")
    if file2.name.endswith(".xlsx"):
        sheet2 = st.selectbox("🗂 ファイル②のシート", get_sheet_names(file2_data), key="sheet2")

    df1 = read_file(file1_data, file1.name, sheet1).reset_index(drop=True)
    df2 = read_file(file2_data, file2.name, sheet2).reset_index(drop=True)

    st.success("✅ ファイル読み込み成功！")

    col1 = st.selectbox("ファイル①で比較する列を選択", df1.columns)
    col2 = st.selectbox("ファイル②で比較する列を選択", df2.columns)

    max_len = max(len(df1), len(df2))
    col1_data = df1[col1].reindex(range(max_len)).astype(str).fillna("").str.strip()
    col2_data = df2[col2].reindex(range(max_len)).astype(str).fillna("").str.strip()

    col_name1 = file1.name
    col_name2 = file2.name

    comparison_result = pd.DataFrame({
        col_name1: col1_data,
        col_name2: col2_data
    })

    # ✅ 空欄の行を除外
  comparison_result = comparison_result[
    (comparison_result[col_name1] != "") | (comparison_result[col_name2] != "")
]

    comparison_result["一致しているか"] = comparison_result[col_name1] == comparison_result[col_name2]
    comparison_result["一致しているか"] = comparison_result["一致しているか"].map(lambda x: "✅" if x else "❌")

    def highlight_diff(row):
        if row["一致しているか"] == "✅":
            return ["background-color: #f2fdf2; color: black"] * len(row)
        else:
            return ["background-color: #fdf2f2; color: black"] * len(row)

    st.subheader("📋 比較結果（空欄行は除外）")
    st.dataframe(
        comparison_result.style.apply(highlight_diff, axis=1),
        use_container_width=True,
        height=600
    )

    csv = comparison_result.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 結果をCSVでダウンロード", data=csv, file_name="比較結果.csv", mime="text/csv")
