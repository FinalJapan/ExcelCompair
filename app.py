import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="VLOOKUP比較アプリ", layout="wide")
st.title("📊 Excel / CSV ファイル比較アプリ（VLOOKUP対応・エラーハンドリング付き）")

# ファイルアップロード
file1 = st.file_uploader("📄 ファイル①（基準になるデータ）", type=["csv", "xlsx"], key="file1")
file2 = st.file_uploader("📄 ファイル②（比較対象データ）", type=["csv", "xlsx"], key="file2")

# シート名取得（Excel）
def get_sheet_names(uploaded_file):
    xls = pd.ExcelFile(io.BytesIO(uploaded_file.read()))
    return xls.sheet_names

# ファイル読み込み関数（日本語CSV・Excel対応）
def read_file(uploaded_file, sheet_name=None):
    uploaded_file.seek(0)
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(io.StringIO(uploaded_file.read().decode("cp932", errors="ignore")))
    else:
        return pd.read_excel(io.BytesIO(uploaded_file.read()), sheet_name=sheet_name)

# シート選択（必要な場合）
sheet1 = sheet2 = None
if file1 and file1.name.endswith(".xlsx"):
    sheet1 = st.selectbox("📑 ファイル①のシートを選択", get_sheet_names(file1), key="sheet1")
if file2 and file2.name.endswith(".xlsx"):
    sheet2 = st.selectbox("📑 ファイル②のシートを選択", get_sheet_names(file2), key="sheet2")

# 両ファイルアップロード後
if file1 and file2:
    df1 = read_file(file1, sheet1)
    df2 = read_file(file2, sheet2)

    st.success("✅ ファイル読み込み成功！")

    st.subheader("🔍 比較したい列を選んでください（照合キーと比較対象）")

    st.write("🧪 ファイル①の列:", df1.columns.tolist())
    st.write("🧪 ファイル②の列:", df2.columns.tolist())

    key1 = st.selectbox("🔑 ファイル①の照合キー（例：商品名）", df1.columns, key="key1")
    key2 = st.selectbox("🔑 ファイル②の照合キー", df2.columns, key="key2")

    col1 = st.selectbox("📌 ファイル①の比較対象列（例：価格）", df1.columns, key="col1")
    col2 = st.selectbox("📌 ファイル②の比較対象列", df2.columns, key="col2")

    if not key1 or not key2 or not col1 or not col2:
        st.warning("⚠️ すべての列を選択してください。")
        st.stop()

    # エラーハンドリング付きマージ
    try:
        merged = pd.merge(
            df1[[key1, col1]],
            df2[[key2, col2]],
            left_on=key1,
            right_on=key2,
            how="left"  # ファイル①を基準にする
        )
    except ValueError as e:
        st.error(f"❌ マージに失敗しました：{e}")
        st.stop()

    # 列名をわかりやすく変更
    merged.rename(columns={
        key1: "照合キー",
        col1: f"{file1.name} の {col1}",
        col2: f"{file2.name} の {col2}"
    }, inplace=True)

    # 比較結果の列を追加
    merged["一致しているか"] = merged[f"{file1.name} の {col1}"].astype(str) == merged[f"{file2.name} の {col2}"].astype(str)

    st.subheader("📋 比較結果")

    def highlight_result(row):
        return ["background-color: #d4edda" if row["一致しているか"] else "background-color: #f8d7da"] * len(row)

    st.dataframe(merged.style.apply(highlight_result, axis=1), use_container_width=True)

    # CSVとして保存
    csv = merged.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 比較結果をCSVでダウンロード",
        data=csv,
        file_name="比較結果_vlookup.csv",
        mime="text/csv"
    )
