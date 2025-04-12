import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Excel/CSV 比較アプリ v3.1", layout="wide")
st.title("📊 Excel / CSV ファイル 比較アプリ（v3.1 アルファベット列表示対応）")
st.caption("✔ 複数シート対応｜✔ 並べ替え対応｜✔ 完全ローカル実行｜✔ A列（列名）表示付き")

# 🔽 ファイルアップロード
file1 = st.file_uploader("📄 ファイル①（CSV または Excel）", type=["csv", "xlsx"], key="file1")
file2 = st.file_uploader("📄 ファイル②（CSV または Excel）", type=["csv", "xlsx"], key="file2")

# 🔠 列番号 → アルファベット変換関数
def num_to_col_letter(n):
    result = ''
    while n >= 0:
        result = chr(n % 26 + 65) + result
        n = n // 26 - 1
    return result

# 🔽 シート名取得（Excelのみ）
def get_sheet_names(uploaded_file):
    xls = pd.ExcelFile(io.BytesIO(uploaded_file.read()))
    return xls.sheet_names

# 🔽 ファイル読み込み関数（シート対応）
def read_file(uploaded_file, sheet_name=None):
    uploaded_file.seek(0)
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(io.StringIO(uploaded_file.read().decode("cp932", errors="ignore")))
    else:
        return pd.read_excel(io.BytesIO(uploaded_file.read()), sheet_name=sheet_name)

# 🔽 シート選択（Excelのみ）
sheet1 = None
sheet2 = None
if file1 and file1.name.endswith(".xlsx"):
    sheet_names1 = get_sheet_names(file1)
    sheet1 = st.selectbox("🗂 ファイル①のシート選択", sheet_names1, key="sheet1")
if file2 and file2.name.endswith(".xlsx"):
    sheet_names2 = get_sheet_names(file2)
    sheet2 = st.selectbox("🗂 ファイル②のシート選択", sheet_names2, key="sheet2")

# 🔽 比較処理
if file1 and file2:
    df1 = read_file(file1, sheet1)
    df2 = read_file(file2, sheet2)

    st.success("✅ ファイル読み込み成功！")

    st.subheader("🔍 比較する列を選んでください")

    # 🔠 ファイル①の列選択（A列表示付き）
    col_options1 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df1.columns)]
    selected1 = st.selectbox("ファイル①の列", options=col_options1, key="col_1")
    col1 = df1.columns[[i for i, s in enumerate(col_options1) if s == selected1][0]]

    # 🔠 ファイル②の列選択（A列表示付き）
    col_options2 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df2.columns)]
    selected2 = st.selectbox("ファイル②の列", options=col_options2, key="col_2")
    col2 = df2.columns[[i for i, s in enumerate(col_options2) if s == selected2][0]]

    # 🔄 比較処理
    compare_len = min(len(df1), len(df2))
    col_name1 = file1.name
    col_name2 = file2.name

    comparison_result = pd.DataFrame({
        col_name1: df1[col1].iloc[:compare_len].astype(str),
        col_name2: df2[col2].iloc[:compare_len].astype(str)
    })
    comparison_result["一致しているか"] = comparison_result[col_name1] == comparison_result[col_name2]

    # 🔁 並べ替え
    st.subheader("🔀 並べ替え設定")
    sort_column = st.selectbox("並べ替える列を選択", comparison_result.columns, key="sort_column")
    sort_order = st.radio("並び順", ["昇順", "降順"], horizontal=True, key="sort_order")
    is_ascending = True if sort_order == "昇順" else False
    sorted_result = comparison_result.sort_values(by=sort_column, ascending=is_ascending)

    # 🖍 色分け表示
    def highlight_diff(row):
   　　 if row["一致しているか"]:
       　  return ["background-color: #f2fdf2; color: black"] * len(row)
        else:
           return ["background-color: #fdf2f2; color: black"] * len(row)


    st.subheader("📋 比較結果（並び替え済み）")
    st.dataframe(sorted_result.style.apply(highlight_diff, axis=1), use_container_width=True)

    # 💾 ダウンロード
    csv = sorted_result.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 結果をCSVでダウンロード",
        data=csv,
        file_name="比較結果.csv",
        mime="text/csv"
    )
