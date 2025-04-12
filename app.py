import streamlit as st
import pandas as pd
import io

# ✅ ページ設定（必ず最初）
st.set_page_config(page_title="Excel/CSV 比較アプリ v3.4", layout="wide")

# ✅ 強制ライトテーマ風CSS（チェックボックス黒文字）
st.markdown("""
<style>
body {
    background-color: white !important;
    color: black !important;
}
div[class*="stCheckbox"] > label {
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Excel / CSV 比較アプリ（v3.4 最終版）")
st.caption("✔ ✅も色つき表示｜✔ テーマをライトに固定｜✔ 片方だけのデータも比較OK")

# アップロード
file1 = st.file_uploader("📄 ファイル①", type=["csv", "xlsx"], key="file1")
file2 = st.file_uploader("📄 ファイル②", type=["csv", "xlsx"], key="file2")

# A列B列表示用関数
def num_to_col_letter(n):
    result = ''
    while n >= 0:
        result = chr(n % 26 + 65) + result
        n = n // 26 - 1
    return result

# シート取得関数
def get_sheet_names(uploaded_file):
    xls = pd.ExcelFile(io.BytesIO(uploaded_file.read()))
    return xls.sheet_names

# ファイル読み込み関数
def read_file(uploaded_file, sheet_name=None):
    uploaded_file.seek(0)
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(io.StringIO(uploaded_file.read().decode("cp932", errors="ignore")))
    else:
        return pd.read_excel(io.BytesIO(uploaded_file.read()), sheet_name=sheet_name)

# シート選択
sheet1 = None
sheet2 = None
if file1 and file1.name.endswith(".xlsx"):
    sheet1 = st.selectbox("🗂 ファイル①のシート", get_sheet_names(file1), key="sheet1")
if file2 and file2.name.endswith(".xlsx"):
    sheet2 = st.selectbox("🗂 ファイル②のシート", get_sheet_names(file2), key="sheet2")

# メイン処理
if file1 and file2:
    df1 = read_file(file1, sheet1).reset_index(drop=True)
    df2 = read_file(file2, sheet2).reset_index(drop=True)

    st.success("✅ ファイル読み込み成功！")

    col_options1 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df1.columns)]
    selected1 = st.selectbox("ファイル①の列", col_options1, key="col_1")
    col1 = df1.columns[[i for i, s in enumerate(col_options1) if s == selected1][0]]

    col_options2 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df2.columns)]
    selected2 = st.selectbox("ファイル②の列", col_options2, key="col_2")
    col2 = df2.columns[[i for i, s in enumerate(col_options2) if s == selected2][0]]

    max_len = max(len(df1), len(df2))
    col1_data = df1[col1].reindex(range(max_len)).astype(str).fillna("")
    col2_data = df2[col2].reindex(range(max_len)).astype(str).fillna("")

    # 比較列の選択
    col1 = st.selectbox("ファイル①の比較列を選択", df1.columns)
    col2 = st.selectbox("ファイル②の比較列を選択", df2.columns)
    
    # 比較結果の作成
    comparison_result = pd.DataFrame({
        f"ファイル①（{col1}）": df1[col1],
        f"ファイル②（{col2}）": df2[col2]
    })
    comparison_result["一致しているか"] = comparison_result[f"ファイル①（{col1}）"] == comparison_result[f"ファイル②（{col2}）"]
    comparison_result["一致しているか"] = comparison_result["一致しているか"].map(lambda x: "✅" if x else "❌")


    
    # 並び替え設定：ラジオボタン＋説明付き
    st.subheader("🔀 並び替え方法を選んでください")
    
    sort_mode = st.radio(
        "比較列に基づいて、ファイル②の順番をどう並べますか？",
        options=[
            "元のまま表示（並び替えしない）",
            "ファイル①の順にファイル②を並び替える"
        ],
        index=0,
        help="ファイル①の比較列の順番に合わせて、ファイル②の値を並び替えます。"
    )
    
    # 並び替えの実行
    if sort_mode == "ファイル①の順にファイル②を並び替える":
        if df1[col1].duplicated().any():
            st.warning("⚠ 並び替えできません：ファイル①の比較列に重複があります。")
            sorted_result = comparison_result
        else:
            merged_df = pd.merge(df1[[col1]], df2[[col2]], left_on=col1, right_on=col2, how='left')
            sorted_result = pd.DataFrame({
                f"ファイル①（{col1}）": merged_df[col1],
                f"ファイル②（{col2}）": merged_df[col2]
            })
            sorted_result["一致しているか"] = sorted_result[f"ファイル①（{col1}）"] == sorted_result[f"ファイル②（{col2}）"]
            sorted_result["一致しているか"] = sorted_result["一致しているか"].map(lambda x: "✅" if x else "❌")
    else:
        sorted_result = comparison_result
    
    # 結果の表示
    st.dataframe(sorted_result)
    
    # ✅ 背景色すべての列に適用（✅/❌列にも戻した）
    def highlight_diff(row):
        if row["一致しているか"] == "✅":
            return ["background-color: #f2fdf2; color: black"] * len(row)
        else:
            return ["background-color: #fdf2f2; color: black"] * len(row)

    st.subheader("📋 比較結果")
    st.dataframe(sorted_result.style.apply(highlight_diff, axis=1), use_container_width=True)

    csv = sorted_result.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 結果をCSVでダウンロード",
        data=csv,
        file_name="比較結果.csv",
        mime="text/csv"
    )
