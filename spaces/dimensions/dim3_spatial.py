# spaces/dimensions/dim3_spatial.py
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA  # 💥 新增终极数学武器：PCA 主成分分析引擎

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

    df_space = df_view.copy()
    
    # ==========================================
    # 🧠 实时降维引擎：如果没有现成坐标，当场执行矩阵坍缩！
    # ==========================================
    if 'PCA_X' not in df_space.columns or 'PCA_Y' not in df_space.columns:
        with st.spinner("🌌 侦测到原始高维空间，正在启动 PCA 主成分分析引擎进行 96 维至 2 维的坍缩..."):
            # 抓取所有 96 个时间切片的列 (例如 v0000 到 v2345)
            time_cols = [c for c in df_space.columns if str(c).startswith('v') and len(str(c)) == 5]
            
            if not time_cols:
                st.error("🚨 未找到时序高频数据，无法进行降维。")
                return
            
            try:
                # 提取纯数字负荷矩阵并用 0 填补可能的空值
                matrix = df_space[time_cols].fillna(0).values
                
                # 启动主成分分析，将 96 维降到 2 维
                pca = PCA(n_components=2)
                coords = pca.fit_transform(matrix)
                
                # 将降维后的坐标赋予 DataFrame
                df_space['PCA_X'] = coords[:, 0]
                df_space['PCA_Y'] = coords[:, 1]
            except Exception as e:
                st.error(f"💥 PCA 降维引擎故障: {e}")
                return

    # ==========================================
    # 🧬 核心特征工程：计算空间距离
    # ==========================================
    # 1. 强制类型转换，确保坐标纯净
    for col in ['PCA_X', 'PCA_Y']:
        df_space[col] = pd.to_numeric(df_space[col], errors='coerce')
    
    # 2. 剔除坐标缺失的脏数据
    df_space = df_space.dropna(subset=['PCA_X', 'PCA_Y'])
    
    if df_space.empty:
        st.error("🚨 基础坐标计算失败，请检查原始数据。")
        return

    # 3. 动态计算引力中心与偏离度
    try:
        if '阵营标签' not in df_space.columns:
            df_space['阵营标签'] = '未分类资产'
            
        centroids = df_space.groupby('阵营标签')[['PCA_X', 'PCA_Y']].transform('mean')
        
        dx = (df_space['PCA_X'].values - centroids['PCA_X'].values)
        dy = (df_space['PCA_Y'].values - centroids['PCA_Y'].values)
        
        # 💥 计算欧氏距离偏离度
        df_space['偏离度'] = np.sqrt(dx**2 + dy**2)
        df_space['偏离度'] = pd.to_numeric(df_space['偏离度'], errors='coerce').fillna(0)
    except Exception as e:
        st.error(f"💥 空间引力场计算故障: {e}")
        df_space['偏离度'] = 0

    # ==========================================
    # 🌌 上半场：绘图
    # ==========================================
    c1, c2 = st.columns([3, 1])
    with c1:
        # 为了防止浏览器卡死，星空图最多只抽样 3000 颗星星展示
        sample_size = min(3000, len(df_space))
        df_scatter = df_space.sample(sample_size, random_state=42)
        
        hover_cols = ['偏离度']
        if '用户编号' in df_scatter.columns:
            hover_cols.insert(0, '用户编号')
            
        fig_pca = px.scatter(
            df_scatter, x='PCA_X', y='PCA_Y', color='阵营标签', 
            hover_data=hover_cols, opacity=0.7,
            marginal_x="violin", marginal_y="violin",
            title=f"高维引力场：资产星空图 (抽样展示: {sample_size} 户)"
        )
        fig_pca.update_layout(template='plotly_dark', margin=dict(l=0, r=0, t=30, b=0), height=450)
        st.plotly_chart(fig_pca, use_container_width=True)
        
    with c2:
        st.subheader("阵营企业分布")
        if '主导阵营' in df_view.columns:
            df_unique = df_view.drop_duplicates(subset=['用户编号']) if '用户编号' in df_view.columns else df_view
            cluster_counts = df_unique['主导阵营'].value_counts().reset_index()
        else:
            cluster_counts = df_view['阵营标签'].value_counts().reset_index()
            
        cluster_counts.columns = ['阵营', '户数']
        fig_pie = px.pie(cluster_counts, values='户数', names='阵营', hole=0.5)
        fig_pie.update_layout(template='plotly_dark', margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    
    # ==========================================
    # 🔭 下半场：探测
    # ==========================================
    st.markdown("### 🔭 空间引力场：边缘刺头与阵营标兵提取")
    
    # 构建绝对安全的子集以防排序崩溃
    subset_cols = ['偏离度', '阵营标签']
    if '用户编号' in df_space.columns:
        subset_cols.append('用户编号')
        
    df_safe = df_space.dropna(subset=subset_cols).copy()
    
    rc1, rc2 = st.columns(2)
    with rc1:
        st.markdown("#### 🚨 边缘游离态预警 (Top 5)")
        try:
            if '用户编号' in df_safe.columns:
                outliers = df_safe.sort_values(by='偏离度', ascending=False).drop_duplicates(subset=['用户编号']).head(5)
                st.dataframe(outliers[['用户编号', '阵营标签', '偏离度']], hide_index=True, use_container_width=True)
            else:
                outliers = df_safe.sort_values(by='偏离度', ascending=False).head(5)
                st.dataframe(outliers[['阵营标签', '偏离度']], hide_index=True, use_container_width=True)
        except Exception as e:
            st.error(f"排序受阻: {e}")

    with rc2:
        st.markdown("#### 🏆 阵营纯血标兵 (Top 5)")
        try:
            if '用户编号' in df_safe.columns:
                standards = df_safe.sort_values(by='偏离度', ascending=True).drop_duplicates(subset=['用户编号']).head(5)
                st.dataframe(standards[['用户编号', '阵营标签', '偏离度']], hide_index=True, use_container_width=True)
            else:
                standards = df_safe.sort_values(by='偏离度', ascending=True).head(5)
                st.dataframe(standards[['阵营标签', '偏离度']], hide_index=True, use_container_width=True)
        except Exception as e:
            st.error(f"排序受阻: {e}")