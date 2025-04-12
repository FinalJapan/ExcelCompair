import streamlit as st
import pandas as pd
import io

# ページ設定
st.set_page_config(page_title="Excel/CSV 比較アプリ v4.3", layout="wide")

# カスタムCSS（アップロードボックス）
st.markdown("""
<style>
body { background-color: white; color: black; }
div[class*="stCheckbox"] > label { color: black !important; }

/* アップロードボックス */
#file1-box .stFileUploader {
    padding: 40px 20px;
    background-color: #d1ecf1;
    border: 2px solid #0c5460;
    border-radius: 10px;
    min-height: 100px;
}
#file2-box .stFileUploader {
    padding: 40px 20px;
    background-color: #fff3cd;
    border: 2px solid #856404;
    border-radius: 10px;
    min-height: 100px;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Excel / CSV 比較アプリ（v4.3 全データ＋並び順維持対応）")

# アップロードボックス
with st.container():
    st.markdown('<div id="file1-box"><h4>📁 ファイル① をアップロード</h4></div>', unsafe_allow_html=True)
    file1 = st.file_uploader("", type=["csv", "xlsx"], key="file1")

with st.container():
    st.markdown('<div id="file2-box"><h4>📁 ファイル② をアップロード</h4></div>', unsafe_allow_html=True)
    file2 = st.file_uploader("", type=["csv", "xlsx"], key="file2")

# ファイル読み込み関数
def read_file(uploaded_file):
    uploaded_file.seek(0)
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(io.StringIO(uploaded_file.read().decode("cp932", errors="ignore")))
    else:
        return pd.read_excel(io.BytesIO(uploaded_file.read()))

# A列形式表示関数
def num_to_col_letter(n):
    result = ''
    while n >= 0:
        result = chr(n % 26 + 65) + result
        n = n // 26 - 1
    return result

if file1 and file2:
    df1 = read_file(file1).reset_index(drop=True)
    df2 = read_file(file2).reset_index(drop=True)
    st.success("✅ ファイル読み込み成功！")

    # 列選択
    col_options1 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df1.columns)]
    col1 = df1.columns[col_options1.index(st.selectbox("ファイル①の列", col_options1, index=0))]

    col_options2 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df2.columns)]
    col2 = df2.columns[col_options2.index(st.selectbox("ファイル②の列", col_options2, index=0))]

    # 並び替え方法選択
    st.subheader("🔀 並び替え方法を選んでください")
    sort_mode = st.radio(
        "比較列に基づいて、ファイル②の順番をどう並べますか？",
        options=[
            "元のまま表示（並び替えしない）",
            "ファイル①の順にファイル②を並び替える"
        ],
        index=0
    )

    # 比較対象データ
    col1_series = df1[col1].astype(str)
    col2_series = df2[col2].astype(str)

    if sort_mode == "ファイル①の順にファイル②を並び替える":
        # 順番指定
        unique_order = pd.Series(col1_series.unique())
        df2["_sort_order"] = pd.Categorical(df2[col2].astype(str), categories=unique_order, ordered=True)
        df2 = df2.sort_values("_sort_order").drop(columns=["_sort_order"]).reset_index(drop=True)
        file2_aligned = df2[col2].astype(str)

        # ファイル①の値をreindexで合わせて取得（Noneにならないよう注意）
        file1_map = pd.Series(col1_series.values, index=col1_series)
        file1_for_display = file2_aligned.map(file1_map).fillna("")
    else:
        file2_aligned = col2_series
        file1_for_display = col1_series.reindex_like(col2_series).fillna("")

    # 比較結果作成
    result_df = pd.DataFrame({
        f"ファイル①（{col1}）": file1_for_display,
        f"ファイル②（{col2}）": file2_aligned
    })
    result_df["判定"] = result_df[f"ファイル①（{col1}）"] == result_df[f"ファイル②（{col2}）"]
    result_df["判定"] = result_df["判定"].map(lambda x: "✅" if x else "❌")

    # 色付きスタイル関数
    def highlight_row(row):
        color = "#d0f0fd" if row["判定"] == "✅" else "#ffd6e0"
        return [f"background-color: {color}; color: black; font-weight: bold;"] * len(row)

    styled_df = result_df.style.apply(highlight_row, axis=1)

    # 結果表示
    st.subheader("📋 比較結果")
    st.dataframe(styled_df, use_container_width=True)

    # ダウンロード
    csv = result_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 結果をCSVでダウンロード",
        data=csv,
        file_name="比較結果.csv",
        mime="text/csv"
    )
