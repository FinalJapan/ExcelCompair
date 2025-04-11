import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="VLOOKUP比較アプリ", layout="wide")
st.title("📊 Excel / CSV ファイル比較アプリ（VLOOKUP風結合）")

# ファイルアップロード
file1 = st.file_uploader("📄 ファイル①（基準になるデータ）", type=["csv", "xlsx"], key="file1")
file2 = st.file_uploader("📄 ファイル②（比較対象データ）", type=["csv", "xlsx"], key="file2")

# シート取得（Excelのみ）
def get_sheet_names(uploaded_file):
    xls = pd.ExcelFile(io.BytesIO(uploaded_file.read()))
    return xls.sheet_names

# ファイル読み込み関数
def read_file(uploaded_file, sheet_name=None):
    uploaded_file.seek(0)  # 読み込み位置をリセット
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(io.StringIO(uploaded_file.read().decode("cp932", errors="ignore")))
    else:
        return pd.read_excel(io.BytesIO(uploaded_file.read()), sheet_name=sheet_name)

# シート選択UI
sheet1 = sheet2 = None
if file1 and file1.name.endswith(".xlsx"):
    sheet1 = st.selectbox("📑 ファイル①のシートを選択", get_sheet_names(file1), key="sheet1")
if file2 and file2.name.endswith(".xlsx"):
    sheet2 = st.selectbox("📑 ファイル②のシートを選択", get_sheet_names(file2), key="sheet2")

# ファイルが両方そろったら処理開始
if file1 and file2:
    df1 = read_file(file1, sheet1)
    df2 = read_file(file2, sheet2)

    st.success("✅ ファイル読み込み成功！")

    st.subheader("🔍 照合キーと比較列を選んでください")

    key1 = st.selectbox("🔑 ファイル①の照合キー（例：商品名）", df1.columns, key="key1")
    key2 = st.selectbox("🔑 ファイル②の照合キー", df2.columns, key="key2")

    col1 = st.selectbox("📌 ファイル①の比較したい列（例：価格）", df1.columns, key="col1")
    col2 = st.selectbox("📌 ファイル②の照合先列", df2.columns, key="col2")

    # データをマージ（VLOOKUP的）
    merged = pd.merge(
        df1[[key1, col1]],
        df2[[key2, col2]],
        left_on=key1,
        right_on=key2,
        how="left"  # 基準ファイルを優先
    )

    # 列名調整
    merged.rename(columns={
        key1: "キー（商品名など）",
        col1: f"{file1.name} の {col1}",
        col2: f"{file2.name} の {col2}"
    }, inplace=True)

    # 比較結果カラム追加
    merged["一致しているか"] = merged[f"{file1.name} の {col1}"].astype(str) == merged[f"{file2.name} の {col2}"].astype(str)

    # 表示
    st.subheader("📋 比較結果")

    def highlight_diff(row):
        if row["一致しているか"]:
            return ["background-color: #d4edda"] * len(row)  # 緑
        else:
            return ["background-color: #f8d7da"] * len(row)  # 赤

    st.dataframe(merged.style.apply(highlight_diff, axis=1), use_container_width=True)

    # ダウンロード
    csv = merged.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 結果をCSVでダウンロード",
        data=csv,
        file_name="比較結果_vlookup.csv",
        mime="text/csv"
    )
