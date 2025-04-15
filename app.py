import streamlit as st
import pandas as pd
import io

# ページ設定
st.set_page_config(page_title="Excel/CSV 比較アプリ", layout="wide")

# カスタムCSS
st.markdown("""
<style>
body { background-color: white; color: black; }
div[class*="stCheckbox"] > label { color: black !important; }
.stFileUploader {
    padding: 40px 20px;
    border: 2px dashed #999;
    border-radius: 10px;
    background-color: #f9f9f9;
    min-height: 100px;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Excel / CSV 比較アプリ（3列比較対応）")

# ファイルアップロードUI
file1 = st.file_uploader("ファイル①をアップロード", type=["csv", "xlsx"])
file2 = st.file_uploader("ファイル②をアップロード", type=["csv", "xlsx"])

# ファイル読み込み関数
def read_file(uploaded_file, sheet_name=None):
    uploaded_file.seek(0)
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(io.StringIO(uploaded_file.read().decode("cp932", errors="ignore")))
    else:
        return pd.read_excel(io.BytesIO(uploaded_file.read()), sheet_name=sheet_name)

# 列番号をA列、B列のように変換
def num_to_col_letter(n):
    result = ''
    while n >= 0:
        result = chr(n % 26 + 65) + result
        n = n // 26 - 1
    return result

if file1 and file2:
    # シート名の取得（Excelのみ）
    if file1.name.endswith(".xlsx"):
        with io.BytesIO(file1.read()) as buffer:
            sheet_names1 = pd.ExcelFile(buffer).sheet_names
    else:
        sheet_names1 = []

    if file2.name.endswith(".xlsx"):
        with io.BytesIO(file2.read()) as buffer:
            sheet_names2 = pd.ExcelFile(buffer).sheet_names
    else:
        sheet_names2 = []

    # シート選択
    sheet_name1 = st.selectbox("ファイル①のシートを選択", sheet_names1) if sheet_names1 else None
    sheet_name2 = st.selectbox("ファイル②のシートを選択", sheet_names2) if sheet_names2 else None

    # ファイルの読み込み
    df1 = read_file(file1, sheet_name=sheet_name1).reset_index(drop=True)
    df2 = read_file(file2, sheet_name=sheet_name2).reset_index(drop=True)
    st.success("✅ ファイル読み込み成功！")

    # 比較列の選択（固定で3列）
    col_options1 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df1.columns)]
    col_options2 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df2.columns)]

    st.markdown("### 📌 ファイル①の比較列")
    col1_1 = st.selectbox("列①", col_options1, key="col1_1")
    col1_2 = st.selectbox("列②", col_options1, key="col1_2")
    col1_3 = st.selectbox("列③", col_options1, key="col1_3")
    selected_cols1 = [
        df1.columns[col_options1.index(col1_1)],
        df1.columns[col_options1.index(col1_2)],
        df1.columns[col_options1.index(col1_3)],
    ]

    st.markdown("### 📌 ファイル②の比較列")
    col2_1 = st.selectbox("列①", col_options2, key="col2_1")
    col2_2 = st.selectbox("列②", col_options2, key="col2_2")
    col2_3 = st.selectbox("列③", col_options2, key="col2_3")
    selected_cols2 = [
        df2.columns[col_options2.index(col2_1)],
        df2.columns[col_options2.index(col2_2)],
        df2.columns[col_options2.index(col2_3)],
    ]

    # 並び順選択
    st.subheader("🔀 並び替え方法を選んでください")
    sort_mode = st.radio(
        "",
        options=[
            "元のまま表示（並び替えしない）",
            "ファイル①の順にファイル②を並び替える"
        ],
        index=0
    )
    
    # 比較用に連結文字列を作成
    col1_series = df1[selected_cols1].astype(str).agg(" | ".join, axis=1)
    col2_series = df2[selected_cols2].astype(str).agg(" | ".join, axis=1)

    # 👇 これを追加！
    if len(col1_series) != len(col2_series):
        st.warning(f"⚠ 行数が一致していません（ファイル①: {len(col1_series)}行、ファイル②: {len(col2_series)}行）。短い方に合わせて比較します。")

    min_len = min(len(col1_series), len(col2_series))
    col1_series = col1_series.iloc[:min_len]
    col2_series = col2_series.iloc[:min_len]

    # 比較処理
    if sort_mode == "ファイル①の順にファイル②を並び替える":
        used = [False] * len(col2_series)
        result_rows = []

        for v in col1_series:
            found = False
            for i, w in enumerate(col2_series):
                if not used[i] and w == v:
                    used[i] = True
                    result_rows.append((v, w, "✅"))
                    found = True
                    break
            if not found:
                result_rows.append((v, None, "❌"))

        sorted_result = pd.DataFrame(result_rows, columns=[
            "ファイル①（3列）", "ファイル②（3列）", "ステータス"
        ])
    else:
        sorted_result = pd.DataFrame({
            "ファイル①（3列）": col1_series,
            "ファイル②（3列）": col2_series
        })
        sorted_result["ステータス"] = col1_series == col2_series
        sorted_result["ステータス"] = sorted_result["ステータス"].map(lambda x: "✅" if x else "❌")

    # 行ごとに色をつける関数
    def highlight_row(row):
        color = "#e6f4ea" if row["ステータス"] == "✅" else "#fde0dc"
        return [f"background-color: {color}; color: black; font-weight: bold;"] * len(row)

    styled_df = sorted_result.style.apply(highlight_row, axis=1)

    # 表示
    st.subheader("📋 比較結果")
    st.dataframe(styled_df, use_container_width=True)

    # CSV出力
    csv = sorted_result.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 結果をCSVでダウンロード",
        data=csv,
        file_name="比較結果_3列.csv",
        mime="text/csv"
    )
