import streamlit as st
import pandas as pd
import io
st.set_page_config(page_title="Excel比較アプリ", layout="wide")

st.title("📊 Excelファイル比較アプリ（ローカル完結）")
st.write("2つのExcelファイルを読み込んで、指定した列の値が一致しているかをチェックします。")

if file1 and file2:
    df1 = read_file(file1)
    df2 = read_file(file2)

    # ✅ ここで df1 / df2 があるからOK！
    compare_len = min(len(df1), len(df2))

    # 比較列の指定（前に作ったやつ）
    comparison_result = pd.DataFrame({
        file1.name: df1[col1].iloc[:compare_len].astype(str),
        file2.name: df2[col2].iloc[:compare_len].astype(str)
    })
    comparison_result["一致しているか"] = comparison_result[file1.name] == comparison_result[file2.name]



def read_file(uploaded_file):
    if uploaded_file.name.endswith(".csv"):
        # アップロードされたCSVファイルをバイナリから文字として読み込む
        return pd.read_csv(io.StringIO(uploaded_file.read().decode("cp932", errors="ignore")))
    else:
        # ExcelファイルはそのままBytesIOで読み込み
        return pd.read_excel(io.BytesIO(uploaded_file.read()))


# 比較実行
if file1 and file2:
    df1 = read_file(file1)
    df2 = read_file(file2)

    st.success("ファイルの読み込みに成功しました！")

    st.subheader("🔍 どの列を比較しますか？")
    col1 = st.selectbox("ファイル①の列を選択", df1.columns)
    col2 = st.selectbox("ファイル②の列を選択", df2.columns)

    # データの比較（短い方に合わせる）
    compare_len = min(len(df1), len(df2))
    comparison_result = pd.DataFrame({
        "ファイル①": df1[col1].iloc[:compare_len].astype(str),
        "ファイル②": df2[col2].iloc[:compare_len].astype(str)
    })
    comparison_result["一致しているか"] = comparison_result["ファイル①"] == comparison_result["ファイル②"]

    st.subheader("📋 比較結果")

    # 色分け表示（Streamlitでは表示だけ）
    def highlight_diff(row):
        if row["一致しているか"]:
            return ["background-color: #d4edda"] * 3  # 緑
        else:
            return ["background-color: #f8d7da"] * 3  # 赤

    st.dataframe(comparison_result.style.apply(highlight_diff, axis=1))

    # ダウンロード
    csv = comparison_result.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 結果をCSVでダウンロード",
        data=csv,
        file_name="比較結果.csv",
        mime="text/csv"
    )
