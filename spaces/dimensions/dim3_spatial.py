# spaces/dimensions/dim3_spatial.py
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

def render(df_view, total_records, unique_users):
    # 💥 战术前置：数据有效性判定
    if df_view is None or df_view.empty:
        st.warning("⚠️ 空间视图数据为空，无法进行引力场分析。")
        return

    with st.expander("📖 【战术指南】如何利用空间身位进行风控与寻优？", expanded=False):
        st.markdown("""
        * **🚨 边缘刺头 (Outliers)**：距离中心最远的资产，通常代表高风险。
        * **🏆 阵营标兵 (Centroids)**：最接近中心的标准资产。
        """)

    # ==========================================
    # 🧬 核心特征工程：计算空间距离 (加装防护)
    # ==========================================
    df_space = df_view.copy()
    
    # 1. 强制类型转换，确保坐标纯净
    for col in ['PCA_X', 'PCA_Y']:
        if col in df_space.columns:
            df_space[col] = pd.to_numeric(df_space[col], errors='coerce')
    
    # 2. 剔除坐标缺失的脏数据
    df_space = df_space.dropna(subset=['PCA_X', 'PCA_Y'])
    
    if df_space.empty:
        st.error("🚨 基础坐标缺失，请重新在空间一加载数据。")
        return

    # 3. 动态计算引力中心与偏离度
    try:
        centroids = df_space.groupby('阵营标签')[['PCA_X', 'PCA_Y']].transform('mean')
        
        dx = (df_space['PCA_X'].values - centroids['PCA_X'].values)
        dy = (df_space['PCA_Y'].values - centroids['PCA_Y'].values)
        
        # 💥 战术清理：计算并把可能导致排序崩溃的所有特殊值全部抹平
        df_space['偏离度'] = np.sqrt(dx**2 + dy**2)
        df_space['偏离度'] = pd.to_numeric(df_space['偏离度'], errors='coerce').fillna(0)
    except Exception as e:
        st.error(f"💥 空间算法引擎故障: {e}")
        df_space['偏离度'] = 0

    # ==========================================
    # 🌌 上半场：绘图
    # ==========================================
    c1, c2 = st.columns([3, 1])
    with c1:
        sample_size = min(3000, len(df_space))
        df_scatter = df_space.sample(sample_size, random_state=42)
        fig_pca = px.scatter(
            df_scatter, x='PCA_X', y='PCA_Y', color='阵营标签', 
            hover_data=['用户编号', '偏离度'], opacity=0.7,
            marginal_x="violin", marginal_y="violin",
            title=f"高维引力场：资产星空图 (样本量: {sample_size})"
        )
        fig_pca.update_layout(template='plotly_dark', margin=dict(l=0, r=0, t=30, b=0), height=450)
        st.plotly_chart(fig_pca, use_container_width=True)
        
    with c2:
        st.subheader("阵营企业分布")
        if '主导阵营' in df_view.columns:
            df_unique = df_view.drop_duplicates(subset=['用户编号'])
            cluster_counts = df_unique['主导阵营'].value_counts().reset_index()
        else:
            cluster_counts = df_view['阵营标签'].value_counts().reset_index()
        cluster_counts.columns = ['阵营', '户数']
        fig_pie = px.pie(cluster_counts, values='户数', names='阵营', hole=0.5)
        fig_pie.update_layout(template='plotly_dark', margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    
    # ==========================================
    # 🔭 下半场：探测 (终极防线)
    # ==========================================
    st.markdown("### 🔭 空间引力场：边缘刺头与阵营标兵提取")
    
    # 💥 排序前强行剔除所有可能作妖的 NaN，构建绝对安全的子集
    df_safe = df_space.dropna(subset=['用户编号', '偏离度', '阵营标签']).copy()
    
    rc1, rc2 = st.columns(2)
    with rc1:
        st.markdown("#### 🚨 边缘游离态预警 (Top 5)")
        try:
            # 在绝对安全的子集上进行排序
            outliers = df_safe.sort_values(by='偏离度', ascending=False).drop_duplicates(subset=['用户编号']).head(5)
            st.dataframe(outliers[['用户编号', '阵营标签', '偏离度']], hide_index=True, use_container_width=True)
        except Exception as e:
            st.error(f"排序受阻: {e}")

    with rc2:
        st.markdown("#### 🏆 阵营纯血标兵 (Top 5)")
        try:
            standards = df_safe.sort_values(by='偏离度', ascending=True).drop_duplicates(subset=['用户编号']).head(5)
            st.dataframe(standards[['用户编号', '阵营标签', '偏离度']], hide_index=True, use_container_width=True)
        except Exception as e:
            st.error(f"排序受阻: {e}")