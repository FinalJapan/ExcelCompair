import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Excel/CSV 比較アプリ", layout="wide")
st.title("📊 Excel / CSV ファイル比較アプリ（複数シート対応・ローカル完結）")

# 🔽 ファイルアップロード
file1 = st.file_uploader("📄 ファイル①をアップロード（CSV または Excel）", type=["csv", "xlsx"], key="file1")
file2 = st.file_uploader("📄 ファイル②をアップロード（CSV または Excel）", type=["csv", "xlsx"], key="file2")

# 🔽 シート名を取得（Excelファイル用）
def get_sheet_names(uploaded_file):
    xls = pd.ExcelFile(io.BytesIO(uploaded_file.read()))
    return xls.sheet_names

# 🔽 ファイル読み込み関数（シート指定可能）
def read_file(uploaded_file, sheet_name=None):
    uploaded_file.seek(0)  # ファイル読み直しのため位置リセット
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(io.StringIO(uploaded_file.read().decode("cp932", errors="ignore")))
    else:
        return pd.read_excel(io.BytesIO(uploaded_file.read()), sheet_name=sheet_name)

# 🔽 シート選択UI
sheet1 = None
sheet2 = None

if file1 and file1.name.endswith(".xlsx"):
    sheet_names1 = get_sheet_names(file1)
    sheet1 = st.selectbox("📑 ファイル①のシートを選択", sheet_names1, key="sheet1")

if file2 and file2.name.endswith(".xlsx"):
    sheet_names2 = get_sheet_names(file2)
    sheet2 = st.selectbox("📑 ファイル②のシートを選択", sheet_names2, key="sheet2")

# 🔽 両方のファイルがある場合のみ処理を実行
if file1 and file2:
    df1 = read_file(file1, sheet1)
    df2 = read_file(file2, sheet2)

    st.success("✅ ファイル読み込み成功！")

    st.subheader("🔍 比較する列を選んでください")
    col1 = st.selectbox("ファイル①の列", df1.columns, key="col_1")
    col2 = st.selectbox("ファイル②の列", df2.columns, key="col_2")

    # 比較処理（短い方に合わせる）
    compare_len = min(len(df1), len(df2))
    col_name1 = file1.name
    col_name2 = file2.name

    comparison_result = pd.DataFrame({
        col_name1: df1[col1].iloc[:compare_len].astype(str),
        col_name2: df2[col2].iloc[:compare_len].astype(str)
    })

    comparison_result["一致しているか"] = comparison_result[col_name1] == comparison_result[col_name2]

    # 色付き表示用関数
    def highlight_diff(row):
        if row["一致しているか"]:
            return ["background-color: #d4edda"] * len(row)  # 緑
        else:
            return ["background-color: #f8d7da"] * len(row)  # 赤

    st.subheader("📋 比較結果")
    st.dataframe(comparison_result.style.apply(highlight_diff, axis=1), use_container_width=True)

    # ダウンロードボタン
    csv = comparison_result.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 結果をCSVでダウンロード",
        data=csv,
        file_name="比較結果.csv",
        mime="text/csv"
    )
