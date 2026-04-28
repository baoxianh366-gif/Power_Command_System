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
    
    st.info("💡 **指挥官的算盘**：在这里，我们将用户的【负荷向量】与市场的【价格向量】进行矩阵内积。系统将瞬间计算出这几十万行数据在不同策略下的真实采购成本。")
    
    st.divider()

    # ==========================================
    # ⚙️ 核心参数指挥台
    # ==========================================
    st.markdown("#### ⚙️ 第一步：设定战场基准 (Price Vectors)")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        contract_price = st.number_input("📜 模拟长协锁定均价 (元/MWh)", value=390.0, step=5.0)
    with col_p2:
        base_spot_price = st.number_input("📉 模拟现货均价基准 (元/MWh)", value=420.0, step=5.0)
    with col_p3:
        duck_curve_depth = st.slider("🦆 午间光伏塌陷深度 (元/MWh)", min_value=0, max_value=300, value=150, help="模拟中午光伏大发导致现货价格跳水的程度")

    # ==========================================
    # 🧬 向量引擎：生成动态价格向量
    # ==========================================
    # 构造 48 点的现货价格向量 (模拟真实市场的双峰一谷)
    x_axis = [f"{str(i//2).zfill(2)}:{'30' if i%2!=0 else '00'}" for i in range(48)]
    
    # 基础正弦波形，模拟日夜交替
    price_vector = np.sin(np.linspace(0, 2*np.pi, 48) - np.pi/2) * 80 + base_spot_price 
    # 模拟午间深谷 (光伏冲击)
    price_vector[22:28] -= duck_curve_depth 
    # 模拟晚峰飙升 (失去光伏+负荷高峰)
    price_vector[34:40] += 120 
    
    # 长协价格向量 (一条直线)
    lta_vector = np.full(48, contract_price)

    # ==========================================
    # 🧮 矩阵内积与财务核算
    # ==========================================
    # 1. 提取所有用户的总负荷向量 (48个点)
    total_load_vector = df[time_cols].sum(axis=0).values
    
    # 2. 💥 核心：向量内积 (Cost = L · P) 💥
    # 假设策略 1：全裸奔，全部在现货市场买电
    cost_all_spot = np.dot(total_load_vector, price_vector)
    
    # 假设策略 2：全长协，全部以固定价格买电
    cost_all_lta = np.dot(total_load_vector, lta_vector)
    
    # 假设策略 3：完美对冲 (谷电买现货，峰电用长协)
    # 取现货和长协中每个时段较便宜的那个价格！(这就是交易员的终极梦想)
    hedged_price_vector = np.minimum(price_vector, lta_vector)
    cost_hedged = np.dot(total_load_vector, hedged_price_vector)

    # ==========================================
    # 📊 战术看板展示
    # ==========================================
    st.markdown("#### 💰 第二步：资产池对冲结算报告")
    
    # 计算节省的资金
    savings = cost_all_spot - cost_hedged
    
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("⚡ 资产池单日总需量", f"{total_load_vector.sum():,.0f} MWh")
    mc2.metric("裸现货结算成本 (极高风险)", f"¥ {cost_all_spot:,.0f}", delta="全敞口基准", delta_color="off")
    mc3.metric("全长协结算成本 (利润微薄)", f"¥ {cost_all_lta:,.0f}", delta=f"对比现货 {cost_all_lta - cost_all_spot:,.0f}", delta_color="inverse")
    mc4.metric("🏆 完美对冲结算成本 (最优)", f"¥ {cost_hedged:,.0f}", delta=f"斩获超额利润 ¥ {savings:,.0f}")

    # ==========================================
    # 🗺️ 第三步：价格与负荷的空间碰撞图
    # ==========================================
    st.markdown("#### 🗺️ 第三步：波形碰撞雷达")
    st.caption("指挥官，请观察您的总负荷曲线是否不幸地踩在了现货价格的尖峰上。")
    
    # 使用多轴图表同时显示“钱”和“电”
    fig = go.Figure()
    
    # 添加电量条形图 (背景)
    fig.add_trace(go.Bar(x=x_axis, y=total_load_vector, name='聚合负荷 (MWh)', opacity=0.3, yaxis='y1', marker_color='cyan'))
    
    # 添加价格折线图 (前景)
    fig.add_trace(go.Scatter(x=x_axis, y=price_vector, mode='lines', name='现货 LMP (元/MWh)', line=dict(color='#FF0055', width=3), yaxis='y2'))
    fig.add_trace(go.Scatter(x=x_axis, y=lta_vector, mode='lines', name='长协防线 (元/MWh)', line=dict(color='#FFCC00', width=2, dash='dash'), yaxis='y2'))

    # 设置双 Y 轴布局
    fig.update_layout(
        template='plotly_dark',
        height=450, margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(title='时段 (48点)'),
        yaxis=dict(title='负荷 (MWh)', side='left', showgrid=False),
        yaxis2=dict(title='电价 (元/MWh)', side='right', overlaying='y', showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 战术解读
    st.success(f"💡 **AI 参谋复盘**：在当前的负荷形态与价格预设下，如果您能精准调度，让用户在价格超过 {contract_price} 元时切回长协通道，在跌破时吃进现货，您单日可比纯现货模式**净赚 ¥ {savings:,.0f} 元**的套利差价。")