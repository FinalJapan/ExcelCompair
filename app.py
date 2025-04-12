import streamlit as st
import pandas as pd
import io

# ✅ ページ設定（一番上に）
st.set_page_config(page_title="Excel/CSV 比較アプリ v3.5", layout="wide")

# ✅ チェックボックス対策CSS（常に黒文字）
st.markdown("""
<style>
div[class*="stCheckbox"] > label {
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Excel / CSV ファイル 比較アプリ（v3.5 表示数改善）")
st.caption("✔ 最大100行まで表示｜✔ ✅/❌で見やすい｜✔ 片方だけのデータもOK｜✔ 色付き｜✔ 安定した比較ロジック")

# ファイルアップロード
file1 = st.file_uploader("📄 ファイル①", type=["csv", "xlsx"])
file2 = st.file_uploader("📄 ファイル②", type=["csv", "xlsx"])

# A列B列表記変換
def num_to_col_letter(n):
    result = ''
    while n >= 0:
        result = chr(n % 26 + 65) + result
        n = n // 26 - 1
    return result

# ファイル読み込み用
def load_file(file):
    return io.BytesIO(file.read())

def read_file(file_data, filename, sheet_name=None):
    if filename.endswith(".csv"):
        return pd.read_csv(io.StringIO(file_data.getvalue().decode("cp932", errors="ignore")))
    else:
        return pd.read_excel(file_data, sheet_name=sheet_name)

def get_sheet_names(file_data):
    xls = pd.ExcelFile(file_data)
    return xls.sheet_names

# 比較処理スタート
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

    col_options1 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df1.columns)]
    selected1 = st.selectbox("ファイル①の列", col_options1, key="col_1")
    col1 = df1.columns[[i for i, s in enumerate(col_options1) if s == selected1][0]]

    col_options2 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df2.columns)]
    selected2 = st.selectbox("ファイル②の列", col_options2, key="col_2")
    col2 = df2.columns[[i for i, s in enumerate(col_options2) if s == selected2][0]]

    max_len = max(len(df1), len(df2))
    col1_data = df1[col1].reindex(range(max_len)).astype(str).fillna("")
    col2_data = df2[col2].reindex(range(max_len)).astype(str).fillna("")

    col_name1 = file1.name
    col_name2 = file2.name

    comparison_result = pd.DataFrame({
        col_name1: col1_data,
        col_name2: col2_data
    })

    comparison_result["一致しているか"] = comparison_result[col_name1] == comparison_result[col_name2]
    comparison_result["一致しているか"] = comparison_result["一致しているか"].map(lambda x: "✅" if x else "❌")

    # 並べ替え
    st.subheader("🔀 並べ替え設定")
    sort_column = st.selectbox("並べ替える列", comparison_result.columns)
    sort_order = st.radio("並び順", ["昇順", "降順"], horizontal=True)
    is_ascending = sort_order == "昇順"
    sorted_result = comparison_result.sort_values(by=sort_column, ascending=is_ascending)

    # ✅ 色付き（全列対応）
    def highlight_diff(row):
        if row["一致しているか"] == "✅":
            return ["background-color: #f2fdf2; color: black"] * len(row)
        else:
            return ["background-color: #fdf2f2; color: black"] * len(row)

    # ✅ 表示（最大100行まで表示）
    st.subheader("📋 比較結果（最大100行表示）")
    st.dataframe(
        sorted_result.head(100).style.apply(highlight_diff, axis=1),
        use_container_width=True,
        height=600
    )

    # ダウンロード
    csv = sorted_result.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 結果をCSVでダウンロード", data=csv, file_name="比較結果.csv", mime="text/csv")
