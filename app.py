import streamlit as st
import pandas as pd
import io

# ページ設定
st.set_page_config(page_title="Excel/CSV 比較アプリ v4.3.4", layout="wide")

# カスタムCSS（見た目調整）
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

st.title("📊 Excel / CSV 比較アプリ（v4.3.4 全データ表示版）")

# アップロード（ラベルなし・プレースホルダー風）
with st.container():
    file1 = st.file_uploader("", type=["csv", "xlsx"], key="file1",
        help="ファイル①をここにドラッグ＆ドロップするか、クリックで選択")
with st.container():
    file2 = st.file_uploader("", type=["csv", "xlsx"], key="file2",
        help="ファイル②をここにドラッグ＆ドロップするか、クリックで選択")

# ファイル読み込み関数
def read_file(uploaded_file):
    uploaded_file.seek(0)
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(io.StringIO(uploaded_file.read().decode("cp932", errors="ignore")))
    else:
        return pd.read_excel(io.BytesIO(uploaded_file.read()))

# 列名をA列B列表示に変換
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
        "ファイル①をマスターデータとして、ファイル②の順番をどうしますか？",
        options=[
            "元のまま表示（並び替えしない）",
            "ファイル①の順にファイル②を並び替える（全データ表示）"
        ],
        index=0
    )

    col1_series = df1[col1].astype(str)
    col2_series = df2[col2].astype(str)

    if sort_mode == "ファイル①の順にファイル②を並び替える（全データ表示）":
        used = [False] * len(col2_series)
        result_rows = []

        # マッチ済みにする処理
        for v in col1_series:
            found = False
            for i, w in enumerate(col2_series):
                if not used[i] and w == v:
                    used[i] = True
                    result_rows.append((v, w, "✅"))
                    found = True
                    break
            if not found:
                result_rows.append((v, "", "❌"))

        # マッチされなかったファイル②の残りを後ろに追加
        for i, used_flag in enumerate(used):
            if not used_flag:
                result_rows.append(("", col2_series.iloc[i], "❌"))

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

    # 見た目：背景色・太字
    def highlight_row(row):
        color = "#d4edda" if row["ステータス"] == "✅" else "#f8d7da"
        return [f"background-color: {color}; color: black; font-weight: bold;"] * len(row)

    styled_df = sorted_result.style.apply(highlight_row, axis=1)

    # 表示
    st.subheader("📋 比較結果")
    st.dataframe(styled_df, use_container_width=True)

    # ダウンロード
    csv = sorted_result.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 結果をCSVでダウンロード",
        data=csv,
        file_name="比較結果.csv",
        mime="text/csv"
    )
