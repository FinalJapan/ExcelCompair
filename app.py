import streamlit as st
import pandas as pd
import io

# ページ設定
st.set_page_config(page_title="Excel/CSV 比較アプリ v3.7", layout="wide")

# テーマ調整（ライト風）
st.markdown("""
<style>
body { background-color: white; color: black; }
div[class*="stCheckbox"] > label { color: black !important; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Excel / CSV 比較アプリ（v3.7 完全版）")

# アップロード
file1 = st.file_uploader("📄 ファイル①", type=["csv", "xlsx"], key="file1")
file2 = st.file_uploader("📄 ファイル②", type=["csv", "xlsx"], key="file2")

# 列名を「A列（列名）」形式にする関数
def num_to_col_letter(n):
    result = ''
    while n >= 0:
        result = chr(n % 26 + 65) + result
        n = n // 26 - 1
    return result

# ファイル読み込み
def read_file(uploaded_file):
    uploaded_file.seek(0)
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(io.StringIO(uploaded_file.read().decode("cp932", errors="ignore")))
    else:
        return pd.read_excel(io.BytesIO(uploaded_file.read()))

if file1 and file2:
    df1 = read_file(file1).reset_index(drop=True)
    df2 = read_file(file2).reset_index(drop=True)
    st.success("✅ ファイル読み込み成功！")

    # 比較列の選択（A列付きで表示）
    col_options1 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df1.columns)]
    col_selected1 = st.selectbox("ファイル①の列", col_options1)
    col1 = df1.columns[col_options1.index(col_selected1)]

    col_options2 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df2.columns)]
    col_selected2 = st.selectbox("ファイル②の列", col_options2)
    col2 = df2.columns[col_options2.index(col_selected2)]

    # 比較結果の初期作成
    col1_data = df1[col1].astype(str).fillna("")
    col2_data = df2[col2].astype(str).fillna("")
    comparison_result = pd.DataFrame({
        f"ファイル①（{col1}）": col1_data,
        f"ファイル②（{col2}）": col2_data
    })
    comparison_result["一致しているか"] = comparison_result[f"ファイル①（{col1}）"] == comparison_result[f"ファイル②（{col2}）"]
    comparison_result["一致しているか"] = comparison_result["一致しているか"].map(lambda x: "✅" if x else "❌")

    # 並び替え選択
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

    # 並び替え処理
    if sort_mode == "ファイル①の順にファイル②を並び替える":
    if df1[col1].duplicated().any():
        st.warning("⚠ 並び替えできません：ファイル①の比較列に重複があります。")
        sorted_result = comparison_result
    else:
        # ファイル①とファイル②の比較列をstrで揃える
        col1_series = df1[col1].astype(str)
        col2_series = df2[col2].astype(str)

        # ファイル②のデータをSeries化してインデックスに値を使う
        file2_series = pd.Series(col2_series.values, index=col2_series)

        # reindexでファイル①の並び順にファイル②を合わせる（存在しない値はNaNになる）
        aligned_file2 = file2_series.reindex(col1_series).values

        sorted_result = pd.DataFrame({
            f"ファイル①（{col1}）": col1_series,
            f"ファイル②（{col2}）": aligned_file2
        })
        sorted_result["一致しているか"] = sorted_result[f"ファイル①（{col1}）"] == sorted_result[f"ファイル②（{col2}）"]
        sorted_result["一致しているか"] = sorted_result["一致しているか"].map(lambda x: "✅" if x else "❌")


    # 結果表示
    st.subheader("📋 比較結果")
    st.dataframe(sorted_result, use_container_width=True)

    # ダウンロード
    csv = sorted_result.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 結果をCSVでダウンロード",
        data=csv,
        file_name="比較結果.csv",
        mime="text/csv"
    )
