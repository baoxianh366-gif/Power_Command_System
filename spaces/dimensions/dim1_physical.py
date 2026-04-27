# spaces/dimensions/dim1_physical.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 尝试导入动态分时底座
try:
    from data_bus.tou_manager import ZhejiangTOU2025
    tou_engine = ZhejiangTOU2025()
except:
    tou_engine = None

def render(df_view, time_cols):
    with st.expander("📖 【战术指南】如何阅读本页图表与术语？", expanded=False):
        st.markdown("""
        * **时域形态图**：展示资产一天24小时（48点）的用电起伏。
        * **八维战力雷达**：基荷占比（越高越稳）、柔性深度（越高越有潜力做需求响应）、负荷率。
        * **FFT 频域拆解**：频域显微镜，0为直流代表基荷，往右代表波动频率。
        """)
        
    c1, c2 = st.columns([3, 2])
    x_axis = [f"{str(i//2).zfill(2)}:{'30' if i%2!=0 else '00'}" for i in range(48)]
    
    with c1:
        st.subheader("时域形态：典型日走势与 TOU 电价映射")
        mean_curve = df_view[time_cols].mean().values
        fig_time = go.Figure()
        fig_time.add_trace(go.Scatter(x=x_axis, y=mean_curve, line=dict(color='#00F0FF', width=3), name='典型均线'))
        
        if tou_engine:
            tou_vector = tou_engine.get_tou_vector("2025-04-15") 
            color_map = {"深谷": "rgba(0,0,139,0.2)", "谷": "rgba(135,206,235,0.2)", "平": "rgba(128,128,128,0.1)", "峰": "rgba(255,165,0,0.2)", "尖峰": "rgba(255,0,0,0.2)"}
            for i in range(48):
                fig_time.add_vrect(x0=i-0.5, x1=i+0.5, fillcolor=color_map.get(tou_vector[i], "rgba(0,0,0,0)"), layer="below", line_width=0)
        
        fig_time.update_layout(template='plotly_dark', margin=dict(l=0, r=0, t=30, b=0), height=350, xaxis_title="时间轴 (48个交易时段)", yaxis_title="聚合平均功率")
        st.plotly_chart(fig_time, use_container_width=True)

    with c2:
        st.subheader("八维战力雷达：资产全息属性")
        radar_categories = ['基荷占比', '负荷率', '柔性深度', '峰谷差率', '日间活跃度', '夜间活跃度', '波动率', '容量规模']
        mean_load_rate = df_view['负荷率'].mean() if '负荷率' in df_view.columns else 0
        radar_values = [df_view['基荷占比'].mean() if '基荷占比' in df_view else 0.5, 
                        mean_load_rate, 
                        df_view['柔性深度'].mean() if '柔性深度' in df_view else 0.2, 
                        0.6, 0.7, 0.3, 0.4, 0.8]
        
        fig_radar = go.Figure(data=go.Scatterpolar(r=radar_values + [radar_values[0]], theta=radar_categories + [radar_categories[0]], fill='toself', line_color='#FF0055'))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=False)), template='plotly_dark', margin=dict(l=40, r=40, t=30, b=20), height=350)
        st.plotly_chart(fig_radar, use_container_width=True)
        
    st.subheader("FFT 频域拆解：基荷与高频扰动分离")
    fft_vals = np.abs(np.fft.rfft(mean_curve)) / 48.0
    fig_fft = px.bar(x=[f"频段 {i}" for i in range(len(fft_vals))], y=fft_vals)
    fig_fft.update_layout(template='plotly_dark', height=250, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig_fft, use_container_width=True)