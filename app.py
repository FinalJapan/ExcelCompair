import streamlit as st
import pandas as pd
import io

# ページ設定
st.set_page_config(page_title="Excel/CSV 比較アプリ", layout="wide")

# カスタムCSS（少し見やすくする）
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

st.title("📊 Excel / CSV 比較アプリ（3列比較・列ごと表示・使いやすいUI）")

# ファイルアップロード
file1 = st.file_uploader("📂 ファイル①をアップロード", type=["csv", "xlsx"])
file2 = st.file_uploader("📂 ファイル②をアップロード", type=["csv", "xlsx"])

# ファイル読み込み関数
def read_file(uploaded_file, sheet_name=None):
    uploaded_file.seek(0)
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(io.StringIO(uploaded_file.read().decode("cp932", errors="ignore")))
    else:
        return pd.read_excel(io.BytesIO(uploaded_file.read()), sheet_name=sheet_name)

# A列, B列... の表示用
def num_to_col_letter(n):
    result = ''
    while n >= 0:
        result = chr(n % 26 + 65) + result
        n = n // 26 - 1
    return result

if file1 and file2:
    # Excelのシート選択
    sheet_names1 = pd.ExcelFile(file1).sheet_names if file1.name.endswith(".xlsx") else []
    sheet_names2 = pd.ExcelFile(file2).sheet_names if file2.name.endswith(".xlsx") else []

    sheet_name1 = st.selectbox("🗂 ファイル①のシートを選択", sheet_names1) if sheet_names1 else None
    sheet_name2 = st.selectbox("🗂 ファイル②のシートを選択", sheet_names2) if sheet_names2 else None

    # ファイル読み込み
    df1 = read_file(file1, sheet_name1).reset_index(drop=True)
    df2 = read_file(file2, sheet_name2).reset_index(drop=True)
    st.success("✅ ファイル読み込み成功！")

    # 列名リスト作成
    col_options1 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df1.columns)]
    col_options2 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df2.columns)]

    # ファイル①の比較列（横並び）
    st.markdown("### 🔸 ファイル①の比較列を選択")
    c1_1, c1_2, c1_3 = st.columns(3)
    with c1_1:
        col1_1 = st.selectbox("列①", col_options1, key="col1_1")
    with c1_2:
        col1_2 = st.selectbox("列②", col_options1, key="col1_2")
    with c1_3:
        col1_3 = st.selectbox("列③", col_options1, key="col1_3")

    selected_cols1 = [
        df1.columns[col_options1.index(col1_1)],
        df1.columns[col_options1.index(col1_2)],
        df1.columns[col_options1.index(col1_3)],
    ]

    # ファイル②の比較列（横並び）
    st.markdown("### 🔸 ファイル②の比較列を選択")
    c2_1, c2_2, c2_3 = st.columns(3)
    with c2_1:
        col2_1 = st.selectbox("列①", col_options2, key="col2_1")
    with c2_2:
        col2_2 = st.selectbox("列②", col_options2, key="col2_2")
    with c2_3:
        col2_3 = st.selectbox("列③", col_options2, key="col2_3")

    selected_cols2 = [
        df2.columns[col_options2.index(col2_1)],
        df2.columns[col_options2.index(col2_2)],
        df2.columns[col_options2.index(col2_3)],
    ]

    # 並び順モード
    st.subheader("🔁 並び替えモードを選んでください")
    sort_mode = st.radio(
        "表示順の指定",
        ["元のまま表示（並び替えなし）", "ファイル①の順にファイル②を並び替える"]
    )

    # 比較用のSeriesと、表示用DataFrameを作成
    df1_selected = df1[selected_cols1].astype(str)
    df2_selected = df2[selected_cols2].astype(str)
    col1_series = df1_selected.agg(" | ".join, axis=1)
    col2_series = df2_selected.agg(" | ".join, axis=1)

    # 長さを揃える
    min_len = min(len(col1_series), len(col2_series))
    if len(col1_series) != len(col2_series):
        st.warning(f"⚠ 行数が異なるため、{min_len}行に揃えて比較します。")
    df1_selected = df1_selected.iloc[:min_len]
    df2_selected = df2_selected.iloc[:min_len]
    col1_series = col1_series.iloc[:min_len]
    col2_series = col2_series.iloc[:min_len]

    # 比較結果生成
    if sort_mode == "ファイル①の順にファイル②を並び替える":
        used = [False] * len(col2_series)
        result_rows = []

        for i in range(len(col1_series)):
            row1 = df1_selected.iloc[i]
            found = False
            for j in range(len(col2_series)):
                if not used[j] and col1_series[i] == col2_series[j]:
                    row2 = df2_selected.iloc[j]
                    result_rows.append((row1.tolist(), row2.tolist(), "✅"))
                    used[j] = True
                    found = True
                    break
            if not found:
                result_rows.append((row1.tolist(), [None]*3, "❌"))

        col_names = [f"ファイル①_{col}" for col in selected_cols1] + [f"ファイル②_{col}" for col in selected_cols2] + ["ステータス"]
        sorted_result = pd.DataFrame([r1 + r2 + [status] for r1, r2, status in result_rows], columns=col_names)
    else:
        status_col = (col1_series == col2_series).map(lambda x: "✅" if x else "❌")
        df1_selected.columns = [f"ファイル①_{col}" for col in selected_cols1]
        df2_selected.columns = [f"ファイル②_{col}" for col in selected_cols2]
        sorted_result = pd.concat([df1_selected.reset_index(drop=True), df2_selected.reset_index(drop=True)], axis=1)
        sorted_result["ステータス"] = status_col

    # ステータス列だけ色をつける関数
    def highlight_status(val):
        if val == "✅":
            return "background-color: #e6f4ea; color: black; font-weight: bold;"
        else:
            return "background-color: #fde0dc; color: black; font-weight: bold;"

    # "ステータス"列にだけスタイルを適用
    styled_df = sorted_result.style.applymap(highlight_status, subset=["ステータス"])


    # 表示
    st.subheader("📋 比較結果")
    st.dataframe(styled_df, use_container_width=True)

    # ダウンロード
    csv = sorted_result.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 結果をCSVでダウンロード",
        data=csv,
        file_name="比較結果_3列.csv",
        mime="text/csv"
    )
