import streamlit as st
import pandas as pd
import io
import math

# ✅ ページ設定（最初に）
st.set_page_config(page_title="Excel/CSV 比較アプリ v3.7", layout="wide")

# ✅ チェックボックス文字色（黒固定）
st.markdown("""
<style>
div[class*="stCheckbox"] > label {
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Excel / CSV ファイル 比較アプリ（v3.7 完全版）")
st.caption("✔ ✅/❌で比較結果表示｜✔ ページ分割｜✔ りゅうじ追跡機能つき！")

file1 = st.file_uploader("📄 ファイル①", type=["csv", "xlsx"])
file2 = st.file_uploader("📄 ファイル②", type=["csv", "xlsx"])

def num_to_col_letter(n):
    result = ''
    while n >= 0:
        result = chr(n % 26 + 65) + result
        n = n // 26 - 1
    return result

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

    # 🔍 データ確認
    st.subheader("🔍 ファイル①のプレビュー")
    st.write(df1.head(10))
    st.subheader("🔍 ファイル②のプレビュー")
    st.write(df2.head(10))

    col_options1 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df1.columns)]
    selected1 = st.selectbox("ファイル①の列", col_options1, key="col_1")
    col1 = df1.columns[[i for i, s in enumerate(col_options1) if s == selected1][0]]

    col_options2 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df2.columns)]
    selected2 = st.selectbox("ファイル②の列", col_options2, key="col_2")
    col2 = df2.columns[[i for i, s in enumerate(col_options2) if s == selected2][0]]

    max_len = max(len(df1), len(df2))
    col1_data = df1[col1].reindex(range(max_len)).astype(str).fillna("").str.strip()
    col2_data = df2[col2].reindex(range(max_len)).astype(str).fillna("").str.strip()

    col_name1 = file1.name
    col_name2 = file2.name

    comparison_result = pd.DataFrame({
        col_name1: col1_data,
        col_name2: col2_data
    })

    comparison_result["一致しているか"] = comparison_result[col_name1] == comparison_result[col_name2]
    comparison_result["一致しているか"] = comparison_result["一致しているか"].map(lambda x: "✅" if x else "❌")

    # 🔍 りゅうじチェック機能
    if "りゅうじ" in comparison_result[col_name1].values:
        st.success("🎉 『りゅうじ』はファイル①にいます！")
    else:
        st.warning("😢 『りゅうじ』がファイル①に見つかりませんでした。")

    # 並べ替え
    st.subheader("🔀 並べ替え設定")
    sort_column = st.selectbox("並べ替える列", comparison_result.columns)
    sort_order = st.radio("並び順", ["昇順", "降順"], horizontal=True)
    is_ascending = sort_order == "昇順"
    sorted_result = comparison_result.sort_values(by=sort_column, ascending=is_ascending)

    # ✅ ページネーション
    rows_per_page = 20
    total_rows = len(sorted_result)
    total_pages = math.ceil(total_rows / rows_per_page)

    st.subheader("📑 表示ページ")
    page = st.number_input("ページ番号を選んでください", min_value=1, max_value=total_pages, step=1)
    start_idx = (page - 1) * rows_per_page
    end_idx = start_idx + rows_per_page
    paginated_result = sorted_result.iloc[start_idx:end_idx]

    # ✅ 色付き表示
    def highlight_diff(row):
        if row["一致しているか"] == "✅":
            return ["background-color: #f2fdf2; color: black"] * len(row)
        else:
            return ["background-color: #fdf2f2; color: black"] * len(row)

    st.subheader(f"📋 比較結果（{rows_per_page}件 × {total_pages}ページ中 {page}ページ目）")
    st.dataframe(
        paginated_result.style.apply(highlight_diff, axis=1),
        use_container_width=True,
        height=600
    )

    csv = sorted_result.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 全データをCSVでダウンロード", data=csv, file_name="比較結果.csv", mime="text/csv")
