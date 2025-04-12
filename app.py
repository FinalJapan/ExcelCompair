import streamlit as st
import pandas as pd
import io

# ページ設定
st.set_page_config(page_title="Excel/CSV 比較アプリ v4.3.5", layout="wide")

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

st.title("📊 Excel / CSV 比較アプリ（v4.3.5）")

# アップロードボックス
with st.container():
    file1 = st.file_uploader("", type=["csv", "xlsx"], key="file1", help="ファイル①を選択")
with st.container():
    file2 = st.file_uploader("", type=["csv", "xlsx"], key="file2", help="ファイル②を選択")

# ファイル読み込み関数
def read_file(uploaded_file):
    uploaded_file.seek(0)
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(io.StringIO(uploaded_file.read().decode("cp932", errors="ignore")))
    else:
        return pd.read_excel(io.BytesIO(uploaded_file.read()))

# A列B列表記関数
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

    st.subheader("🔍 比較結果（ファイル①基準）")

    # マスターデータの順に、ファイル②の値を1対1でマッチング
    col1_series = df1[col1].astype(str)
    col2_series = df2[col2].astype(str)

    used = [False] * len(col2_series)
    result_rows = []

    for v in col1_series:
        matched = False
        for i, w in enumerate(col2_series):
            if not used[i] and w == v:
                used[i] = True
                result_rows.append((v, w, "✅"))
                matched = True
                break
        if not matched:
            result_rows.append((v, "", "❌"))

    result_df = pd.DataFrame(result_rows, columns=[
        f"ファイル①（{col1}）",
        f"ファイル②（{col2}）",
        "判定"
    ])

    # スタイリング
    def highlight_row(row):
        color = "#d4edda" if row["判定"] == "✅" else "#f8d7da"
        return [f"background-color: {color}; color: black; font-weight: bold;"] * len(row)

    styled_df = result_df.style.apply(highlight_row, axis=1)

    st.dataframe(styled_df, use_container_width=True)

    # ダウンロード
    csv = result_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 結果をCSVでダウンロード",
        data=csv,
        file_name="比較結果.csv",
        mime="text/csv"
    )
