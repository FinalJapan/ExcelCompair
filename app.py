import streamlit as st
import pandas as pd
import io

# ページ設定
st.set_page_config(page_title="Excel/CSV 比較アプリ v4.1", layout="wide")

# テーマ調整（ライト風・黒文字）
st.markdown("""
<style>
body { background-color: white; color: black; }
div[class*="stCheckbox"] > label { color: black !important; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Excel / CSV 比較アプリ")

# ファイル読み込み関数
def read_file(uploaded_file):
    uploaded_file.seek(0)
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(io.StringIO(uploaded_file.read().decode("cp932", errors="ignore")))
    else:
        return pd.read_excel(io.BytesIO(uploaded_file.read()))

# A列、B列表記にする関数
def num_to_col_letter(n):
    result = ''
    while n >= 0:
        result = chr(n % 26 + 65) + result
        n = n // 26 - 1
    return result

# ファイルアップロード
file1 = st.file_uploader("📄 ファイル①", type=["csv", "xlsx"], key="file1")
file2 = st.file_uploader("📄 ファイル②", type=["csv", "xlsx"], key="file2")

if file1 and file2:
    df1 = read_file(file1).reset_index(drop=True)
    df2 = read_file(file2).reset_index(drop=True)
    st.success("✅ ファイル読み込み成功！")

    # 比較列選択（編集不可 selectbox）
    col_options1 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df1.columns)]
    col1 = df1.columns[col_options1.index(st.selectbox("ファイル①の列", col_options1, index=0))]

    col_options2 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df2.columns)]
    col2 = df2.columns[col_options2.index(st.selectbox("ファイル②の列", col_options2, index=0))]

    # 並び替え選択
    st.subheader("🔀 並び替え方法を選んでください")
    sort_mode = st.radio(
        "比較列に基づいて、ファイル②の順番をどう並べますか？",
        options=[
            "元のまま表示（並び替えしない）",
            "ファイル①の順にファイル②を並び替える"
        ],
        index=0
    )

    # データ取得と型変換
    col1_series = df1[col1].astype(str)
    col2_series = df2[col2].astype(str)

    # 並び替え処理
    if sort_mode == "ファイル①の順にファイル②を並び替える":
        if col2_series.duplicated().any():
            st.warning("⚠ ファイル②の比較列に重複があります。並び替えできません。")
            file2_aligned = col2_series
        else:
            file2_map = pd.Series(col2_series.values, index=col2_series)
            file2_aligned = file2_map.reindex(col1_series).values
    else:
        file2_aligned = col2_series

    # 比較結果作成
    result_df = pd.DataFrame({
        f"ファイル①（{col1}）": col1_series,
        f"ファイル②（{col2}）": file2_aligned
    })
    result_df["一致しているか"] = result_df[f"ファイル①（{col1}）"] == result_df[f"ファイル②（{col2}）"]
    result_df["一致しているか"] = result_df["一致しているか"].map(lambda x: "✅" if x else "❌")

    # スタイル設定：行全体に背景色 + 太字
    def highlight_row(row):
        color = "#d4edda" if row["True or False"] == "✅" else "#f8d7da"
        return [f"background-color: {color}; color: black; font-weight: bold;"] * len(row)

    styled_df = result_df.style.apply(highlight_row, axis=1)

    # 結果表示
    st.subheader("📋 比較結果")
    st.dataframe(styled_df, use_container_width=True)

    # CSV出力
    csv = result_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 結果をCSVでダウンロード",
        data=csv,
        file_name="比較結果.csv",
        mime="text/csv"
    )
