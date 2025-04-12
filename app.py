import streamlit as st
import pandas as pd
import io
import math

# ✅ ページ設定（必ず一番上）
st.set_page_config(page_title="Excel/CSV 比較アプリ v3.6", layout="wide")

# ✅ チェックボックスの文字色を黒に固定（ダークテーマ対策）
st.markdown("""
<style>
div[class*="stCheckbox"] > label {
color: black !important;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Excel / CSV ファイル 比較アプリ（v3.6 ページネーション対応）")
st.caption("✔ ページ単位で表示切替｜✔ ✅/❌で比較明確｜✔ 色分けあり｜✔ 大量データも安心！")

# ファイルアップロード
file1 = st.file_uploader("📄 ファイル①", type=["csv", "xlsx"])
file2 = st.file_uploader("📄 ファイル②", type=["csv", "xlsx"])

# ヘルパー関数たち
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

# ファイル読み込み＆処理
if file1 and file2:
file1_data = load_file(file1)
file2_data = load_file(file2)

sheet1 = sheet2 = None
if file1.name.endswith(".xlsx"):
sheet1 = st.selectbox("🗂 ファイル①のシート", get_sheet_names(file1_data), key="sheet1")
if file2.name.endswith(".xlsx"):
sheet2 = st.selectbox("🗂 ファイル②のシート", get_sheet_names(file2_data), key="sheet2")

df1 = read_file(file1_data, file1.name, sheet1).reset_index(drop=True)
# ✅ りゅうじが含まれているか簡単にチェック
if 'りゅうじ' in df1[col1].astype(str).tolist():
st.success("🎉 ファイル①に『りゅうじ』はいます！")
else:
st.error("😢 ファイル①に『りゅうじ』はいません…（読み込みか列選択の問題）")

df2 = read_file(file2_data, file2.name, sheet2).reset_index(drop=True)

# ✅ データがちゃんと読み込まれてるか表示して確認！
st.subheader("🔍 ファイル①の読み込み内容プレビュー")
st.write(df1.head(10))

st.subheader("🔍 ファイル②の読み込み内容プレビュー")
st.write(df2.head(10))

st.success("✅ ファイル読み込み成功！")

col_options1 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df1.columns)]
selected1 = st.selectbox("ファイル①の列", col_options1, key="col_1")
col1 = df1.columns[[i for i, s in enumerate(col_options1) if s == selected1][0]]

# ✅ 選んだ列に「りゅうじ」がいるか確認！
st.subheader("🔍 選んだ列の上から10件（りゅうじ確認）")
st.write("ファイル①：" + col1)
st.write(df1[col1].head(10))

st.write("ファイル②：" + col2)
st.write(df2[col2].head(10))

col_options2 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df2.columns)]
selected2 = st.selectbox("ファイル②の列", col_options2, key="col_2")
col2 = df2.columns[[i for i, s in enumerate(col_options2) if s == selected2][0]]

# ✅ 選んだ列に「りゅうじ」がいるか確認！
st.subheader("🔍 選んだ列の上から10件（りゅうじ確認）")
st.write("ファイル①：" + col1)
st.write(df1[col1].head(10))

st.write("ファイル②：" + col2)
st.write(df2[col2].head(10))

max_len = max(len(df1), len(df2))
col1_data = df1[col1].reindex(range(max_len)).astype(str).fillna("")
col2_data = df2[col2].reindex(range(max_len)).astype(str).fillna("")

col_name1 = file1.name
col_name2 = file2.name

comparison_result = pd.DataFrame({
col_name1: col1_data,
col_name2: col2_data
})

# ✅ 比較結果全体を見て、りゅうじが含まれてるか確認！
st.subheader("🔍 比較結果全体（りゅうじチェック）")
st.write(comparison_result)

comparison_result["一致しているか"] = comparison_result[col_name1] == comparison_result[col_name2]
comparison_result["一致しているか"] = comparison_result["一致しているか"].map(lambda x: "✅" if x else "❌")

# 並べ替え
st.subheader("🔀 並べ替え設定")
sort_column = st.selectbox("並べ替える列", comparison_result.columns)
sort_order = st.radio("並び順", ["昇順", "降順"], horizontal=True)
is_ascending = sort_order == "昇順"
sorted_result = comparison_result.sort_values(by=sort_column, ascending=is_ascending)

# ✅ ページネーション設定
rows_per_page = 20  # ← 1ページに表示する行数（自由に変更OK！）
total_rows = len(sorted_result)
total_pages = math.ceil(total_rows / rows_per_page)

st.subheader("📑 表示ページ")
page = st.number_input("ページ番号を選んでください", min_value=1, max_value=total_pages, step=1)
start_idx = (page - 1) * rows_per_page
end_idx = start_idx + rows_per_page
paginated_result = sorted_result.iloc[start_idx:end_idx]

# ✅ 色付き表示（✅ / ❌ に応じて）
def highlight_diff(row):
if row["一致しているか"] == "✅":
    return ["background-color: #f2fdf2; color: black"] * len(row)
else:
    return ["background-color: #fdf2f2; color: black"] * len(row)

# ✅ 表示（ページごとの結果）
st.subheader(f"📋 比較結果（{rows_per_page}件 × {total_pages}ページ中 {page}ページ目）")
st.dataframe(
paginated_result.style.apply(highlight_diff, axis=1),
use_container_width=True,
height=600
)

# ✅ 全件ダウンロード
csv = sorted_result.to_csv(index=False).encode("utf-8-sig")
st.download_button("📥 全データをCSVでダウンロード", data=csv, file_name="比較結果.csv", mime="text/csv")
