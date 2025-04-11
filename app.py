import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("🎓 生徒の点数分析アプリ（クラウド版）")

names = ['あかり', 'たけし', 'ゆうこ', 'けんじ', 'さくら', 'だいご', 'まい', 'しんじ', 'はなこ', 'ゆうた']
scores = np.random.randint(0, 101, size=10)

df = pd.DataFrame({'名前': names, '点数': scores})
st.dataframe(df)

sorted_df = df.sort_values(by='点数', ascending=False)
st.subheader("🏆 上位3人")
st.write(sorted_df.head(3))

st.subheader("📊 点数グラフ")
st.bar_chart(df.set_index('名前'))
