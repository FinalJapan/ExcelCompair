import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="ファイル比較アプリ", layout="wide")
st.title("📊 Excel / CSV ファイル 比較アプリ（ローカル完結）")
st.caption("アップロードした2つのファイルを、指定した列で比較します（ローカル実行・情報流出なし）")

# ✅ ファイルアップロード
file1 = st.file_uploader("🔼 比較対象ファイル①（CSV or Excel）", type=["xlsx", "csv"], key="file1")
file2 = st.file_uploader("🔼 比較対象ファイル②（CSV or Excel）", type=["xlsx", "csv"], key="file2")

# ✅ 読み込み関数（日本語対応）
def read_file(uploaded_file):
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(io.StringIO(uploaded_file.read().decode("cp932", errors="ignore")))
    else:
        return pd.read_excel(io.BytesIO(uploaded_file.read()))

# ✅ アップロード後に処理開始
if file1 and file2:
    # 読み込み
    df1 = read_file(file1)
    df2 = read_file(file2)

    # 列の選択
    st.subheader("🔍 比較したい列を選んでください")
    col1 = st.selectbox("ファイル①の列", df1.columns, key="col1")
    col2 = st.selectbox("ファイル②の列", df2.columns, key="col2")

    # 比較処理（短い方に合わせる）
    compare_len = min(len(df1), len(df2))

    # 列名にファイル名（拡張子付き）を使用
    col_name1 = file1.name
    col_name2 = file2.name

    comparison_result = pd.DataFrame({
        col_name1: df1[col1].iloc[:compare_len].astype(str),
        col_name2: df2[col2].iloc[:compare_len].astype(str),
    })

    comparison_result["一致しているか"] = comparison_result[col_name1] == comparison_result[col_name2]

    # 比較結果を表示（色つき）
    st.subheader("📋 比較結果")

    def highlight_diff(row):
        if row["一致しているか"]:
            return ["background-color: #d4edda"] * len(row)  # 緑
        else:
            return ["background-color: #f8d7da"] * len(row)  # 赤

    st.dataframe(comparison_result.style.apply(highlight_diff, axis=1), use_container_width=True)

    # CSVダウンロード
    csv = comparison_result.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 結果をCSVでダウンロード",
        data=csv,
        file_name="比較結果.csv",
        mime="text/csv"
    )
