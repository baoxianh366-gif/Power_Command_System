# spaces/dimensions/dim3_spatial.py
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

def render(df_view, total_records, unique_users):
    with st.expander("📖 【战术指南】如何利用空间身位进行风控与寻优？", expanded=False):
        st.markdown("""
        * **星空图与边缘引力场**：主图展示分布，顶部和右侧的“小提琴图”展示了该维度的兵力厚度（越胖代表聚集的人越多）。
        * **🚨 边缘刺头 (Outliers)**：距离阵营中心最远的资产。它们虽然被强行分到了某个阵营，但行为极其怪异。在电力现货中，这类“变异用户”是导致整体预测偏差和现货爆仓的**核心风险源**，必须拉入黑名单或收取高额风险溢价！
        * **🏆 阵营标兵 (Centroids)**：距离阵营中心最近的资产。它们是该阵营的“绝对标准件”，可作为未来售电公司对外招揽新客户时的**画像模板**。
        """)

    # ==========================================
    # 🧬 核心特征工程：计算空间距离与引力中心
    # ==========================================
    # 为了不污染原数据，copy一份作图专用的
    df_space = df_view.copy()
    
    # 动态计算每个阵营的几何引力中心 (Centroid)
    centroids = df_space.groupby('阵营标签')[['PCA_X', 'PCA_Y']].transform('mean')
    
    # 计算每个点到其所属阵营中心的欧氏距离 (Euclidean Distance)
    df_space['偏离度'] = np.sqrt((df_space['PCA_X'] - centroids['PCA_X'])**2 + (df_space['PCA_Y'] - centroids['PCA_Y'])**2)
    
    # ==========================================
    # 🌌 上半场：宏观星空与兵力厚度
    # ==========================================
    c1, c2 = st.columns([3, 1])
    
    with c1:
        sample_size = min(3000, total_records)
        df_scatter = df_space.sample(sample_size, random_state=42)
        
        # 💥 升级：加入边缘小提琴图 (Marginal distributions) 增强高维感
        fig_pca = px.scatter(
            df_scatter, x='PCA_X', y='PCA_Y', color='阵营标签', 
            hover_data=['用户编号', '负荷率', '偏离度'], opacity=0.7,
            marginal_x="violin", marginal_y="violin", # 增加边缘分布，看透厚度
            title=f"高维引力场：资产星空图与边缘密度分布 (抽样展示 {sample_size} 个切片)"
        )
        fig_pca.update_layout(template='plotly_dark', margin=dict(l=0, r=0, t=30, b=0), height=450)
        fig_pca.update_xaxes(showticklabels=False); fig_pca.update_yaxes(showticklabels=False)
        st.plotly_chart(fig_pca, width='stretch')
        
    with c2:
        st.subheader("阵营企业数量分布")
        # 强制按“独立企业”去重
        if '主导阵营' in df_view.columns:
            df_unique = df_view.drop_duplicates(subset=['用户编号'])
            cluster_counts = df_unique['主导阵营'].value_counts().reset_index()
        else:
            cluster_counts = df_view['阵营标签'].value_counts().reset_index()
            
        cluster_counts.columns = ['阵营', '户数']
        
        fig_pie = px.pie(cluster_counts, values='户数', names='阵营', hole=0.5)
        fig_pie.update_layout(template='plotly_dark', margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label+value')
        st.plotly_chart(fig_pie, width='stretch')
        st.caption(f"🛡️ 兵力核对：共计 **{unique_users}** 户独立企业。")

    st.markdown("---")
    
    # ==========================================
    # 🔭 下半场：微观深度解析 (标兵与刺头探测)
    # ==========================================
    st.markdown("### 🔭 空间引力场：边缘刺头与阵营标兵提取")
    st.caption("基于高维欧氏距离测算。在风控逻辑中，距离中心越远代表异质性越强、偏差违约风险越高。")
    
    rc1, rc2 = st.columns(2)
    
    with rc1:
        st.markdown("#### 🚨 边缘游离态预警 (Top 5 刺头资产)")
        
        # 提取距离最大的 5 个用户（去重，找最极端的）
        outliers = df_space.sort_values(by='偏离度', ascending=False).drop_duplicates(subset=['用户编号']).head(5)
        outliers_df = outliers[['用户编号', '阵营标签', '偏离度', '负荷率']].copy()
        
        # 渲染刺头表格
        st.dataframe(
            outliers_df, 
            column_config={
                "偏离度": st.column_config.ProgressColumn(
                    "空间偏离度 (拉满为极度危险)", 
                    format="%.2f", 
                    min_value=0, 
                    max_value=float(df_space['偏离度'].max())
                ),
                "负荷率": st.column_config.NumberColumn("负荷率", format="%.1f%%")
            },
            hide_index=True, width='stretch'
        )
        
    with rc2:
        st.markdown("#### 🏆 阵营纯血标兵 (Top 5 标准件)")
        
        # 提取距离最小的 5 个用户 (纯度最高)
        standards = df_space.sort_values(by='偏离度', ascending=True).drop_duplicates(subset=['用户编号']).head(5)
        standards_df = standards[['用户编号', '阵营标签', '偏离度', '负荷率']].copy()
        
        # 渲染标兵表格
        st.dataframe(
            standards_df, 
            column_config={
                "偏离度": st.column_config.NumberColumn("中心贴合度 (越低代表越纯正)", format="%.3f"),
                "负荷率": st.column_config.NumberColumn("负荷率", format="%.1f%%")
            },
            hide_index=True, width='stretch'
        )