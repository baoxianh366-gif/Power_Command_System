# spaces/macro_sandbox.py
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

def render_sandbox():
    st.markdown("### 📈 宏观策略与博弈沙盘：高维内积与真金白银")
    if st.session_state.get('system_status') != 'ready':
        st.error("🚨 访问受阻：请先在 [空间一] 完成数据点火！")
        return
        
    df = st.session_state['portfolio_data']
    time_cols = st.session_state['time_cols']
    
    st.divider()

    st.markdown("#### ⚙️ 第一步：设定战场基准 (Price Vectors)")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        contract_price = st.number_input("📜 模拟长协锁定均价 (元/MWh)", value=390.0, step=5.0)
    with col_p2:
        base_spot_price = st.number_input("📉 模拟现货均价基准 (元/MWh)", value=420.0, step=5.0)
    with col_p3:
        duck_curve_depth = st.slider("🦆 午间光伏塌陷深度 (元/MWh)", min_value=0, max_value=300, value=150)

    # 💥 升级：96点向量引擎 💥
    x_axis = [f"{str(i//4).zfill(2)}:{str((i%4)*15).zfill(2)}" for i in range(96)]
    price_vector = np.sin(np.linspace(0, 2*np.pi, 96) - np.pi/2) * 80 + base_spot_price 
    price_vector[44:56] -= duck_curve_depth # 11点到14点
    price_vector[68:80] += 120 # 17点到20点
    lta_vector = np.full(96, contract_price)

    # 内积计算 (L·P)
    total_load_vector = df[time_cols].sum(axis=0).values
    cost_all_spot = np.dot(total_load_vector, price_vector)
    cost_all_lta = np.dot(total_load_vector, lta_vector)
    hedged_price_vector = np.minimum(price_vector, lta_vector)
    cost_hedged = np.dot(total_load_vector, hedged_price_vector)
    savings = cost_all_spot - cost_hedged

    st.markdown("#### 💰 第二步：资产池对冲结算报告")
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("⚡ 资产池总需量", f"{total_load_vector.sum():,.0f} MWh")
    mc2.metric("裸现货成本", f"¥ {cost_all_spot:,.0f}")
    mc3.metric("全长协成本", f"¥ {cost_all_lta:,.0f}")
    mc4.metric("🏆 完美对冲成本", f"¥ {cost_hedged:,.0f}", delta=f"净赚差价 ¥ {savings:,.0f}")

    st.markdown("#### 🗺️ 第三步：波形碰撞雷达 (96-Point)")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x_axis, y=total_load_vector, name='聚合负荷 (MWh)', opacity=0.3, yaxis='y1', marker_color='cyan'))
    fig.add_trace(go.Scatter(x=x_axis, y=price_vector, mode='lines', name='现货 LMP', line=dict(color='#FF0055', width=3), yaxis='y2'))
    fig.add_trace(go.Scatter(x=x_axis, y=lta_vector, mode='lines', name='长协防线', line=dict(color='#FFCC00', width=2, dash='dash'), yaxis='y2'))

    fig.update_layout(template='plotly_dark', height=450, margin=dict(l=0, r=0, t=10, b=0),
                      xaxis=dict(title='时段 (96点)'), yaxis=dict(title='负荷', side='left'),
                      yaxis2=dict(title='电价', side='right', overlaying='y', showgrid=False),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)