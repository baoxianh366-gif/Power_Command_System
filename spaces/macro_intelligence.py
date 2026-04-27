# spaces/macro_intelligence.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def render_intelligence():
    st.markdown("### 🌍 宏观情报局：外部环境与市场基准")
    st.caption("情报决定战局！这里汇聚了现货电价、气象数据、新能源出力等所有左右市场走向的外部核心要素，是沙盘推演的先决条件。")
    
    st.divider()

    # 划分三大情报分局
    tab1, tab2, tab3 = st.tabs([
        "📉 现货电价基准 (Prices)", 
        "🌤️ 气象与新能源 (Weather & RES)", 
        "📰 政策与基本面 (Fundamentals)"
    ])

    # ---------------------------------------------------------
    # 📉 情报一：现货价格体系
    # ---------------------------------------------------------
    with tab1:
        st.subheader("省级节点边际电价 (LMP) 走势侦测")
        st.caption("当前接入：模拟/历史典型日现货电价矩阵（后续可接驳真实数据源）")
        
        # 模拟生成具有物理意义的现货电价（双峰特性，中午光伏塌陷导致价格极低）
        x_axis = [f"{str(i//2).zfill(2)}:{'30' if i%2!=0 else '00'}" for i in range(48)]
        # 模拟基础日内走势 (带午间深谷和晚间高峰)
        base_curve = np.sin(np.linspace(0, 2*np.pi, 48) - np.pi/2) * 150 + 350 
        base_curve[20:28] -= 150 # 午间光伏大发，价格砸穿
        base_curve[34:40] += 200 # 晚峰价格飙升
        
        # 模拟日前(DA)与实时(RT)
        da_price = base_curve + np.random.normal(0, 20, 48)
        rt_price = base_curve + np.random.normal(0, 60, 48) # 实时波动更大
        
        fig_price = go.Figure()
        fig_price.add_trace(go.Scatter(x=x_axis, y=da_price, line=dict(color='#FFCC00', width=2), name='日前均价 (DA)'))
        fig_price.add_trace(go.Scatter(x=x_axis, y=rt_price, line=dict(color='#FF0055', width=2, dash='dot'), name='实时均价 (RT)'))
        
        fig_price.update_layout(
            template='plotly_dark', height=400, margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="时段 (48点)", yaxis_title="电价 (元/MWh)", hovermode="x unified"
        )
        st.plotly_chart(fig_price, use_container_width=True)
        
        st.info("💡 **战术指引**：在沙盘推演中，我们将把资产池的【负荷向量】与此处的【价格向量】进行内积碰撞，计算真实头寸。")

    # ---------------------------------------------------------
    # 🌤️ 情报二：气象与大盘出力
    # ---------------------------------------------------------
    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🌡️ 气温敏感度雷达")
            st.markdown("等待气象局 API 接入...")
            st.caption("计划功能：追踪极端高温（>30°C）/寒潮对商业与居民负荷的非线性抬升效应。")
        with c2:
            st.subheader("☀️ 风光出力预测")
            st.markdown("等待省调调度数据接入...")
            st.caption("计划功能：追踪全省新能源出力，预判午间鸭子曲线的深度（决定价格谷底）。")

    # ---------------------------------------------------------
    # 📰 情报三：基本面事件
    # ---------------------------------------------------------
    with tab3:
        st.subheader("📅 关键事件日历 (Event Driven)")
        events = pd.DataFrame({
            "日期": ["2026-05-15", "2026-06-01", "2026-07-20"],
            "事件类型": ["政策变更", "检修计划", "气象预警"],
            "情报内容": ["省发改委：迎峰度夏开启，尖峰电价时段延长1小时。", "某特高压直流跨区送电检修，预计晚峰供应吃紧。", "厄尔尼诺现象加剧，预计7月下旬出现连续极端高温日。"],
            "影响判定": ["🚨 现货均价看涨", "⚠️ 晚峰价差拉大", "🔥 容量危机预警"]
        })
        st.table(events)