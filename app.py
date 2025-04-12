import streamlit as st
import pandas as pd
import io

# ページ設定
st.set_page_config(page_title="Excel/CSV 比較アプリ v4.3.1", layout="wide")

# カスタムCSS（ライトテーマ風、アップロードボックスも装飾）
st.markdown("""
<style>
body { background-color: white; color: black; }
div[class*="stCheckbox"] > label { color: black !important; }
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

st.title("📊 Excel/CSV 比較アプリ（v4.3.1 最終版）")

# アップロードボックス（見た目改善）
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

# A列、B列表示用関数
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

    # 列選択（編集不可のselectbox、初期値はindex=0）
    col_options1 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df1.columns)]
    col1 = df1.columns[col_options1.index(st.selectbox("ファイル①の列", col_options1, index=0))]

    col_options2 = [f"{num_to_col_letter(i)}列（{col}）" for i, col in enumerate(df2.columns)]
    col2 = df2.columns[col_options2.index(st.selectbox("ファイル②の列", col_options2, index=0))]

    # 並び替え方法選択（今回は「ファイル①の順に並べる」か「元のまま」か）
    st.subheader("🔀 並び替え方法を選んでください")
    sort_mode = st.radio(
        "ファイル①をマスターデータとして、ファイル②の順番をどうしますか？",
        options=[
            "元のまま表示（並び替えしない）",
            "ファイル①の順にファイル②を並び替える"
        ],
        index=0
    )

    # 比較対象データの準備（文字列に変換）
    col1_series = df1[col1].astype(str)
    col2_series = df2[col2].astype(str)

    # 並び替え処理：ファイル①の順にファイル②を並べ替え（全データ保持版）
    if sort_mode == "ファイル①の順にファイル②を並び替える":
        # マッチング用にファイル②の各行の使用フラグを作成
        used = [False] * len(col2_series)
        result_rows = []
        
        # ファイル①の各値について、最初の一致する（未使用の）ファイル②の値を探す
        for v in col1_series:
            found = False
            for i, w in enumerate(col2_series):
                if not used[i] and w == v:
                    used[i] = True
                    result_rows.append((v, w, "✅"))
                    found = True
                    break
            if not found:
                # ファイル①にはあるが、ファイル②にはない → ファイル②は空文字
                result_rows.append((v, "", "❌"))
        
        # 次に、ファイル②の中で未使用のデータ（＝ファイル①に存在しないもの）を追加
        for i, flag in enumerate(used):
            if not flag:
                result_rows.append(("", col2_series.iloc[i], "❌"))
        
        # ソート済みのデータフレーム作成（既にファイル①の順番で追加済み）
        sorted_result = pd.DataFrame(result_rows, columns=[f"ファイル①（{col1}）", f"ファイル②（{col2}）", "判定"])
    else:
        # 並び替えしない場合：単純に両ファイルのデータを表示
        sorted_result = pd.DataFrame({
            f"ファイル①（{col1}）": col1_series,
            f"ファイル②（{col2}）": col2_series
        })
        sorted_result["判定"] = sorted_result[f"ファイル①（{col1}）"] == sorted_result[f"ファイル②（{col2}）"]
        sorted_result["判定"] = sorted_result["判定"].map(lambda x: "✅" if x else "❌")

    # スタイリング：行全体に背景色＋太字
    def highlight_row(row):
        color = "#d4edda" if row["判定"] == "✅" else "#f8d7da"
        return [f"background-color: {color}; color: black; font-weight: bold;"] * len(row)

    styled_df = sorted_result.style.apply(highlight_row, axis=1)

    # 結果表示
    st.subheader("📋 比較結果")
    st.dataframe(styled_df, use_container_width=True)

    # ダウンロードボタン
    csv = sorted_result.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 結果をCSVでダウンロード",
        data=csv,
        file_name="比較結果.csv",
        mime="text/csv"
    )
