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

st.title("📊 Excel / CSV 比較アプリ")

# アップロードUI（ラベルなし）
with st.container():
    file1 = st.file_uploader("", type=["csv", "xlsx"], key="file1",
        help="ファイル①をここにドラッグ＆ドロップするか、クリックで選択")
with st.container():
    file2 = st.file_uploader("", type=["csv", "xlsx"], key="file2",
        help="ファイル②をここにドラッグ＆ドロップするか、クリックで選択")

# ファイル読み込み
def read_file(uploaded_file, sheet_name=None):
    uploaded_file.seek(0)
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(io.StringIO(uploaded_file.read().decode("cp932", errors="ignore")))
    else:
        # シート名が指定されていればそのシートを読み込み、指定されていなければ全シートを読み込む
        return pd.read_excel(io.BytesIO(uploaded_file.read()), sheet_name=sheet_name)

# 列名変換（A列、B列 表記）
def num_to_col_letter(n):
    result = ''
    while n >= 0:
        result = chr(n % 26 + 65) + result
        n = n // 26 - 1
    return result

# アプリ本体
if file1 and file2:
    # Excelの場合、シート名を取得
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

    # シート選択（Excelの場合）
    if sheet_names1:
        sheet_name1 = st.selectbox("ファイル①のシートを選んでください", sheet_names1)
    else:
        sheet_name1 = None

    if sheet_names2:
        sheet_name2 = st.selectbox("ファイル②のシートを選んでください", sheet_names2)
    else:
        sheet_name2 = None

    # ファイルの読み込み
    df1 = read_file(file1, sheet_name=sheet_name1).reset_index(drop=True)
    df2 = read_file(file2, sheet_name=sheet_name2).reset_index(drop=True)
    st.success("✅ ファイル読み込み成功！")

    # 比較列選択
    col_options1 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df1.columns)]
    col1 = df1.columns[col_options1.index(st.selectbox("ファイル①の列", col_options1, index=0))]

    col_options2 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df2.columns)]
    col2 = df2.columns[col_options2.index(st.selectbox("ファイル②の列", col_options2, index=0))]

    # 比較モード
    st.subheader("🔀 並び替え方法を選んでください")
    sort_mode = st.radio(
        "",
        options=[
            "元のまま表示（並び替えしない）",
            "ファイル①の順にファイル②を並び替える"
        ],
        index=0
    )

    col1_series = df1[col1].astype(str)
    col2_series = df2[col2].astype(str)

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
            f"ファイル①（{col1}）",
            f"ファイル②（{col2}）",
            "ステータス"
        ])
    else:
        sorted_result = pd.DataFrame({
            f"ファイル①（{col1}）": col1_series,
            f"ファイル②（{col2}）": col2_series
        })
        sorted_result["ステータス"] = sorted_result[f"ファイル①（{col1}）"] == sorted_result[f"ファイル②（{col2}）"]
        sorted_result["ステータス"] = sorted_result["ステータス"].map(lambda x: "✅" if x else "❌")

    # 背景色・太字スタイル
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
        file_name="比較結果.csv",
        mime="text/csv"
    )
