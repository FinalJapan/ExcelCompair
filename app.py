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
        try:
            return pd.read_csv(io.StringIO(uploaded_file.read().decode("utf-8")))
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            return pd.read_csv(io.StringIO(uploaded_file.read().decode("cp932", errors="ignore")))
    else:
        if sheet_name:
            return pd.read_excel(io.BytesIO(uploaded_file.read()), sheet_name=sheet_name)
        else:
            return pd.read_excel(io.BytesIO(uploaded_file.read()))

# 列名変換（A列、B列 表記）
def num_to_col_letter(n):
    result = ''
    while n >= 0:
        result = chr(n % 26 + 65) + result
        n = n // 26 - 1
    return result

# アプリ本体
if file1 and file2:
    # ファイル①のシート選択
    if file1.name.endswith(".xlsx"):
        excel1 = pd.ExcelFile(io.BytesIO(file1.read()))
        sheet_options1 = excel1.sheet_names
        sheet1 = st.selectbox("ファイル①のシートを選んでください", sheet_options1)
    else:
        sheet1 = None

    # ファイル②のシート選択
    if file2.name.endswith(".xlsx"):
        excel2 = pd.ExcelFile(io.BytesIO(file2.read()))
        sheet_options2 = excel2.sheet_names
        sheet2 = st.selectbox("ファイル②のシートを選んでください", sheet_options2)
    else:
        sheet2 = None

    # ファイル読み込み
    df1 = read_file(file1, sheet_name=sheet1).reset_index(drop=True)
    df2 = read_file(file2, sheet_name=sheet2).reset_index(drop=True)
    st.success("✅ ファイル読み込み成功！")

    # 行数チェック
    if len(df1) != len(df2) and sort_mode == "元のまま表示（並び替えしない）":
        st.warning("⚠️ 行数が一致していないため、正確な比較ができない可能性があります。")

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

    # 結果件数の表示
    matched = (sorted_result["ステータス"] == "✅").sum()
    unmatched = (sorted_result["ステータス"] == "❌").sum()
    st.markdown(f"**✅ 一致: {matched} 件　❌ 不一致: {unmatched} 件**")

    # 背景色・太字スタイル
    def highlight_row(row):
        color = "#e6f4ea" if row["ステータス"] == "✅" else "#fde0dc"
        return [f"background-color: {color}; color: black; font-weight: bold;"] * len(row)

    styled_df = sorted_result.style.apply(highlight_row, axis=1)

    # 表示
    st.subheader("📋 比較結果")
    if len(sorted_result) > 1000:
        st.info("表示数が多いため最初の1000行のみ表示しています")
        st.dataframe(styled_df.head(1000), use_container_width=True)
    else:
        st.dataframe(styled_df, use_container_width=True)

    # CSV出力
    csv = sorted_result.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 結果をCSVでダウンロード",
        data=csv,
        file_name="比較結果.csv",
        mime="text/csv"
    )
    
    # Excel出力
    try:
        import openpyxl
        excel = sorted_result.to_excel(index=False, engine='openpyxl')
        st.download_button(
            label="📥 結果をExcelでダウンロード",
            data=excel,
            file_name="比較結果.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except ImportError:
        st.warning("Excel出力には`openpyxl`ライブラリが必要です。")
