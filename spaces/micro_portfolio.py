# spaces/micro_portfolio.py
import streamlit as st
import pandas as pd

from spaces.dimensions import dim0_macro_health
from spaces.dimensions import dim1_physical
from spaces.dimensions import dim2_ai_tags
from spaces.dimensions import dim3_spatial
from spaces.dimensions import dim4_synergy

def render_dashboard():
    """微观资产池：航母主框架 (防重叠版)"""
    
    if 'portfolio_data' not in st.session_state:
        st.warning("⚠️ 资产数据遗失，请返回 [数据总线] 重新点火！")
        return
        
    df = st.session_state['portfolio_data']
    time_cols = st.session_state['time_cols']
    
    # 💥 核心修复：为全军 1643 户企业，计算并确立唯一的“年度主导阵营” 💥
    if '主导阵营' not in df.columns and '用户编号' in df.columns:
        with st.spinner("⚙️ 正在为全军计算唯一主导阵营，消除跨界重叠..."):
            user_main_camp = df.groupby('用户编号')['阵营标签'].agg(lambda x: x.mode().iloc[0]).reset_index()
            user_main_camp.rename(columns={'阵营标签': '主导阵营'}, inplace=True)
            df = df.merge(user_main_camp, on='用户编号', how='left')
            st.session_state['portfolio_data'] = df # 将主导阵营锁入内存
    
    # --- 🎯 顶层雷达：全局阵营筛选 ---
    st.markdown("### 🔬 微观资产池：高维全景扫描")
    
    col_filter, col_metrics1, col_metrics2 = st.columns([2, 1, 1])
    with col_filter:
        # 🛑 改用『主导阵营』进行下拉框过滤！
        clusters = df['主导阵营'].unique().tolist() if '主导阵营' in df.columns else df['阵营标签'].unique().tolist()
        clusters.sort()
        selected_cluster = st.selectbox(
            "🎯 战术视角：选择要透视的军团阵营", 
            ["大盘全览 (All)"] + clusters,
            help="系统已强制将用户归入其全年中出现频率最高的【主导阵营】，彻底杜绝兵力重复计算。"
        )
        
    # 🛑 根据唯一的『主导阵营』分发兵力
    if selected_cluster == "大盘全览 (All)":
        df_view = df
    else:
        df_view = df[df['主导阵营'] == selected_cluster] if '主导阵营' in df.columns else df[df['阵营标签'] == selected_cluster]
    
    total_records = len(df_view)
    unique_users = df_view['用户编号'].nunique() if '用户编号' in df_view.columns else total_records
    mean_load_rate = df_view['负荷率'].mean() if '负荷率' in df_view.columns else 0
    
    with col_metrics1:
        st.metric("📡 视角兵力 (独立企业)", f"{unique_users:,} 户")
    with col_metrics2:
        st.metric("⚡ 平均负荷率", f"{mean_load_rate:.1%}")

    st.divider()

    # --- 🚀 停机坪：呼叫底层分析插件 ---
    tab0, tab1, tab2, tab3, tab4 = st.tabs([
        "📊 维度零：全局大盘与极限探测",
        "🌊 维度一：物理与频域双重测序", 
        "🏷️ 维度二：AI 标签与人工闭环", 
        "🌌 维度三：高维空间身位", 
        "⚙️ 维度四：时空节律与系统组合"
    ])
    
    with tab0:
        dim0_macro_health.render(df_view, time_cols, unique_users)
    with tab1:
        dim1_physical.render(df_view, time_cols)
    with tab2:
        dim2_ai_tags.render(df_view, unique_users)
    with tab3:
        dim3_spatial.render(df_view, total_records, unique_users)
    with tab4:
        dim4_synergy.render(df_view, df, time_cols)