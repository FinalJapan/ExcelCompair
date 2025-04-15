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

st.title("📊 Excel / CSV 比較アプリ（3列比較・横並びUI）")

# アップロードUI
file1 = st.file_uploader("ファイル①をアップロード", type=["csv", "xlsx"])
file2 = st.file_uploader("ファイル②をアップロード", type=["csv", "xlsx"])

# ファイル読み込み関数
def read_file(uploaded_file, sheet_name=None):
    uploaded_file.seek(0)
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(io.StringIO(uploaded_file.read().decode("cp932", errors="ignore")))
    else:
        return pd.read_excel(io.BytesIO(uploaded_file.read()), sheet_name=sheet_name)

# A列, B列...に変換
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

    # 列名リスト作成
    col_options1 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df1.columns)]
    col_options2 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df2.columns)]

    # ファイル① 列選択（横並び）
    st.markdown("### 📌 ファイル①の比較列を選んでください")
    col1_a, col1_b, col1_c = st.columns(3)
    with col1_a:
        col1_1 = st.selectbox("列①", col_options1, key="col1_1")
    with col1_b:
        col1_2 = st.selectbox("列②", col_options1, key="col1_2")
    with col1_c:
        col1_3 = st.selectbox("列③", col_options1, key="col1_3")

    selected_cols1 = [
        df1.columns[col_options1.index(col1_1)],
        df1.columns[col_options1.index(col1_2)],
        df1.columns[col_options1.index(col1_3)],
    ]

    # ファイル② 列選択（横並び）
    st.markdown("### 📌 ファイル②の比較列を選んでください")
    col2_a, col2_b, col2_c = st.columns(3)
    with col2_a:
        col2_1 = st.selectbox("列①", col_options2, key="col2_1")
    with col2_b:
        col2_2 = st.selectbox("列②", col_options2, key="col2_2")
    with col2_c:
        col2_3 = st.selectbox("列③", col_options2, key="col2_3")

    selected_cols2 = [
        df2.columns[col_options2.index(col2_1)],
        df2.columns[col_options2.index(col2_2)],
        df2.columns[col_options2.index(col2_3)],
    ]

    # 並び替えモード
    st.subheader("🔀 並び替え方法を選んでください")
    sort_mode = st.radio(
        "",
        options=[
            "元のまま表示（並び替えしない）",
            "ファイル①の順にファイル②を並び替える"
        ],
        index=0
    )

    # 選んだ列のデータを取得（文字列化）
    df1_selected = df1[selected_cols1].astype(str)
    df2_selected = df2[selected_cols2].astype(str)

    # 比較用の連結文字列作成（status判定用）
    col1_series = df1_selected.agg(" | ".join, axis=1)
    col2_series = df2_selected.agg(" | ".join, axis=1)

    # 行数を揃える
    min_len = min(len(col1_series), len(col2_series))
    if len(col1_series) != len(col2_series):
        st.warning(f"⚠ 行数が一致していません（ファイル①: {len(col1_series)}行、ファイル②: {len(col2_series)}行）。短い方に合わせて比較します。")
    col1_series = col1_series.iloc[:min_len]
    col2_series = col2_series.iloc[:min_len]
    df1_selected = df1_selected.iloc[:min_len]
    df2_selected = df2_selected.iloc[:min_len]

    # 比較ロジック
    if sort_mode == "ファイル①の順にファイル②を並び替える":
        used = [False] * len(col2_series)
        result_rows = []

        for i in range(len(col1_series)):
            row1 = df1_selected.iloc[i]
            found = False
            for j in range(len(col2_series)):
                if not used[j] and col1_series[i] == col2_series[j]:
                    used[j] = True
                    row2 = df2_selected.iloc[j]
                    result_rows.append((row1.tolist(), row2.tolist(), "✅"))
                    found = True
                    break
            if not found:
                result_rows.append((row1.tolist(), [None]*3, "❌"))

        # データフレーム作成
        col_names = [f"ファイル①_{col}" for col in selected_cols1] + [f"ファイル②_{col}" for col in selected_cols2] + ["ステータス"]
        sorted_result = pd.DataFrame([r1 + r2 + [status] for r1, r2, status in result_rows], columns=col_names)

    else:
        # 同じ行同士を比較（そのまま表示）
        status_col = (col1_series == col2_series).map(lambda x: "✅" if x else "❌")
        df1_selected.columns = [f"ファイル①_{col}" for col in selected_cols1]
        df2_selected.columns = [f"ファイル②_{col}" for col in selected_cols2]
        sorted_result = pd.concat([df1_selected.reset_index(drop=True), df2_selected.reset_index(drop=True)], axis=1)
        sorted_result["ステータス"] = status_col

    # ハイライト関数
    def highlight_row(row):
        color = "#e6f4ea" if row["ステータス"] == "✅" else "#fde0dc"
        return [f"background-color: {color}; color: black; font-weight: bold;"] * len(row)

    styled_df = sorted_result.style.apply(highlight_row, axis=1)

    # 結果表示
    st.subheader("📋 比較結果")
    st.dataframe(styled_df, use_container_width=True)

    # ダウンロードボタン
    csv = sorted_result.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 結果をCSVでダウンロード",
        data=csv,
        file_name="比較結果_3列.csv",
        mime="text/csv"
    )
