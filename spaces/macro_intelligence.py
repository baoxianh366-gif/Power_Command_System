# spaces/macro_intelligence.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def render_intelligence():
    st.markdown("### 🌍 宏观情报局：外部环境与市场基准")
    st.caption("情报决定战局！这里汇聚了现货电价、气象数据等核心要素。当前全军雷达已切换至 **96点(15分钟级)** 现货高频模式。")
    st.divider()

    tab1, tab2, tab3 = st.tabs(["📉 现货电价基准", "🌤️ 气象与新能源", "📰 政策基本面"])

    with tab1:
        st.subheader("省级节点边际电价 (LMP) 走势侦测")
        
        # 💥 升级：96点现货价格模拟器 💥
        x_axis = [f"{str(i//4).zfill(2)}:{str((i%4)*15).zfill(2)}" for i in range(96)]
        
        # 基础日内走势 (拉伸到 96 点)
        base_curve = np.sin(np.linspace(0, 2*np.pi, 96) - np.pi/2) * 150 + 350 
        base_curve[44:56] -= 150 # 午间深谷 (11:00-14:00)
        base_curve[68:80] += 200 # 晚峰飙升 (17:00-20:00)
        
        da_price = base_curve + np.random.normal(0, 20, 96)
        rt_price = base_curve + np.random.normal(0, 60, 96)
        
        fig_price = go.Figure()
        fig_price.add_trace(go.Scatter(x=x_axis, y=da_price, line=dict(color='#FFCC00', width=2), name='日前均价 (DA)'))
        fig_price.add_trace(go.Scatter(x=x_axis, y=rt_price, line=dict(color='#FF0055', width=2, dash='dot'), name='实时均价 (RT)'))
        fig_price.update_layout(template='plotly_dark', height=400, margin=dict(l=0, r=0, t=10, b=0), xaxis_title="时段 (96点)", yaxis_title="电价 (元/MWh)", hovermode="x unified")
        st.plotly_chart(fig_price, use_container_width=True)

    with tab2:
        st.info("等待气象局API与省调96点高频风光数据接入...")
    with tab3:
        st.info("无重大基本面异动。")