import streamlit as st
import pandas as pd
import io

# ページ設定
st.set_page_config(page_title="Excel/CSV 比較アプリ v4.3.6.1", layout="wide")

st.title("📊 Excel / CSV 比較アプリ（v4.3.6.1 空欄なし対応）")

# ファイルアップロード
file1 = st.file_uploader("ファイル①をアップロード", type=["csv", "xlsx"])
file2 = st.file_uploader("ファイル②をアップロード", type=["csv", "xlsx"])

# ファイル読み込み関数
def read_file(uploaded_file):
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    else:
        return pd.read_excel(uploaded_file)

if file1 and file2:
    df1 = read_file(file1)
    df2 = read_file(file2)

    # 列選択
    col1 = st.selectbox("ファイル①の比較列を選択", df1.columns)
    col2 = st.selectbox("ファイル②の比較列を選択", df2.columns)

    # ファイル①の値をリスト化
    file1_values = df1[col1].astype(str).tolist()

    # ファイル②の値をリスト化
    file2_values = df2[col2].astype(str).tolist()

    # マッチング処理
    matched_file1_values = []
    match_results = []

    for val in file2_values:
        if val in file1_values:
            matched_file1_values.append(val)
            file1_values.remove(val)
            match_results.append("✅")
        else:
            matched_file1_values.append(val)  # ←空欄にせず、そのまま出す
            match_results.append("❌")

    # 結果のデータフレーム作成
    result_df = pd.DataFrame({
        f"ファイル②（{col2}）": file2_values,
        f"ファイル①（{col1}）": matched_file1_values,
        "判定": match_results
    })

    # 結果表示
    st.subheader("📋 比較結果")
    st.dataframe(result_df)

    # CSVダウンロード
    csv = result_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 結果をCSVでダウンロード",
        data=csv,
        file_name="比較結果.csv",
        mime="text/csv"
    )
