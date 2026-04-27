# spaces/macro_sandbox.py
import streamlit as st

def render_sandbox():
    st.markdown("### 📈 宏观策略与博弈沙盘 (Macro Strategy Sandbox)")
    
    if st.session_state.get('system_status') != 'ready':
        st.error("🚨 访问受阻：请先在 [数据总线] 空间完成数据初始化点火！")
        return
        
    df = st.session_state['portfolio_data']
    time_cols = st.session_state['time_cols']
    
    st.info("💡 **指挥官，终极战场已为您敞开。** 我们将在这里引入 LMP（节点边际电价）向量，将其与资产池的负荷向量进行矩阵内积运算，推演各种组合下的真实盈亏与 CVaR 风险。")
    
    st.divider()
    
    # 预留沙盘推演控制台
    st.subheader("⚙️ 推演控制台 (Deploying...)")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("模拟长协基准价", "390.00 元/MWh")
    c2.metric("模拟现货均价", "425.50 元/MWh")
    c3.metric("当前资产池总规模", f"{df[time_cols].sum().sum():,.0f} MWh")
    c4.metric("暴露敞口风险", "待推演")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.caption("🚀 正在等待指挥官下达具体的定价模型与策略指令...")