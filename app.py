import streamlit as st
import pandas as pd
import io

# ページ設定
st.set_page_config(page_title="Excel/CSV 比較アプリ v4.1", layout="wide")

st.title("📊 Excel / CSV 比較アプリ（v4.1）")

# アップロード
file1 = st.file_uploader("📄 ファイル①", type=["csv", "xlsx"])
file2 = st.file_uploader("📄 ファイル②", type=["csv", "xlsx"])

# ファイル読み込み関数
def read_file(uploaded_file):
    uploaded_file.seek(0)
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(io.StringIO(uploaded_file.read().decode("cp932", errors="ignore")))
    else:
        return pd.read_excel(io.BytesIO(uploaded_file.read()))

# メイン処理
if file1 and file2:
    df1 = read_file(file1).reset_index(drop=True)
    df2 = read_file(file2).reset_index(drop=True)
    st.success("✅ ファイル読み込み完了！")

    # 比較列選択
    col1 = st.selectbox("ファイル①の比較列を選択", df1.columns)
    col2 = st.selectbox("ファイル②の比較列を選択", df2.columns)

    # 比較対象列の抽出と整形
    col1_data = df1[col1].astype(str).fillna("")
    col2_data = df2[col2].astype(str).fillna("")

    # 初期比較結果作成
    comparison_result = pd.DataFrame({
        f"ファイル①（{col1}）": col1_data,
        f"ファイル②（{col2}）": col2_data
    })
    comparison_result["一致しているか"] = comparison_result[f"ファイル①（{col1}）"] == comparison_result[f"ファイル②（{col2}）"]
    comparison_result["一致しているか"] = comparison_result["一致しているか"].map(lambda x: "✅" if x else "❌")

    # 並び替え設定
    st.subheader("🔀 並び替え設定")
    sort_mode = st.radio(
        "並び替え方法を選んでください",
        options=[
            "Excelの入力順（A2から順番）",
            "ファイル①の順にファイル②を並べる",
            "❌を上に表示（不一致優先）",
            "比較列の昇順",
            "比較列の降順"
        ],
        index=0
    )

    # 並び替え処理
    if sort_mode == "Excelの入力順（A2から順番）":
        sorted_result = comparison_result

    elif sort_mode == "ファイル①の順にファイル②を並べる":
        df2_indexed = df2.set_index(col2).astype(str)
        col1_series = df1[col1].astype(str)
    
        # reindexして index から値を取得
        col2_sorted_index = df2_indexed.reindex(col1_series).index.to_series().fillna("")
    
        sorted_result = pd.DataFrame({
            f"ファイル①（{col1}）": col1_series,
            f"ファイル②（{col2}）": col2_sorted_index
        })
        sorted_result["一致しているか"] = sorted_result[f"ファイル①（{col1}）"] == sorted_result[f"ファイル②（{col2}）"]
        sorted_result["一致しているか"] = sorted_result["一致しているか"].map(lambda x: "✅" if x else "❌")


    elif sort_mode == "❌を上に表示（不一致優先）":
        sorted_result = comparison_result.sort_values(by="一致しているか")

    elif sort_mode == "比較列の昇順":
        sorted_result = comparison_result.sort_values(by=f"ファイル①（{col1}）", ascending=True)

    elif sort_mode == "比較列の降順":
        sorted_result = comparison_result.sort_values(by=f"ファイル①（{col1}）", ascending=False)

    # 結果表示
    st.subheader("📋 比較結果")
    st.dataframe(sorted_result, use_container_width=True)

    # ダウンロードボタン
    csv = sorted_result.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 結果をCSVでダウンロード",
        data=csv,
        file_name="比較結果.csv",
        mime="text/csv"
    )
