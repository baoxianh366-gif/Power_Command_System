# app.py
import streamlit as st
import pandas as pd

# 1. 导入各功能空间模块
from data_bus import state_manager
from spaces import micro_portfolio
from spaces import macro_intelligence
from spaces import macro_sandbox
from spaces import tactical_manual

# --- 页面全局配置 ---
st.set_page_config(
    page_title="电力交易策略指挥官 - 驾驶舱",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 初始化全局系统状态 ---
if 'system_status' not in st.session_state:
    st.session_state['system_status'] = 'standby' # standby (待机) | ready (就绪)

# ==========================================
# 🗺️ 侧边栏：核心战略导航 (请核对这里的文字)
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/radar.png", width=80)
    st.title("战术指挥部")
    st.markdown("---")
    
    # 💥 定义 5 大战略空间 💥
    page = st.radio(
        "🚀 战略空间切换",
        [
            "🛰️ 空间一：数据总线 (接入)", 
            "🔬 空间二：微观资产池 (画像)", 
            "🌍 空间三：宏观情报局 (市场)", 
            "📈 空间四：策略博弈沙盘 (对冲)", 
            "📖 空间五：战术白皮书 (术语)"
        ],
        index=0
    )
    
    st.markdown("---")
    st.caption("系统版本: V3.5 Total Integration")
    
    if st.button("🗑️ 强行清空系统内存"):
        state_manager.clear_system()

# ==========================================
# 🛰️ 空间一：数据总线与底层洗滤
# ==========================================
if page == "🛰️ 空间一：数据总线 (接入)":
    st.title("🛰️ 空间一：数据总线与底层洗滤中心")
    st.info("💡 指挥官，请在此上传原始负荷 Q 矩阵，启动系统核心。")
    
    with st.expander("📥 弹药挂载口：上传负荷数据 (CSV/Excel)", expanded=(st.session_state['system_status'] == 'standby')):
        uploaded_file = st.file_uploader("选择 1600 户级全样本数据文件", type=['csv', 'xlsx'])
        if uploaded_file:
            if st.button("🚀 确认点火：启动高维解析引擎"):
                state_manager.init_system(uploaded_file)

    if st.session_state['system_status'] == 'ready':
        st.success("✅ 系统状态：高维矩阵已锁入内存，随时可进行战术推演。")
        # 简单预览
        if 'portfolio_data' in st.session_state:
            st.write("数据预览（前5行）：")
            st.dataframe(st.session_state['portfolio_data'].head(5), use_container_width=True)
    else:
        st.warning("⚠️ 系统状态：待机中。请上传数据以激活高维空间。")

# ==========================================
# 🔬 空间二：微观资产池
# ==========================================
elif page == "🔬 空间二：微观资产池 (画像)":
    if st.session_state['system_status'] != 'ready':
        st.error("🚨 访问受阻：请先在 [空间一：数据总线] 完成数据点火！")
    else:
        micro_portfolio.render_dashboard()

# ==========================================
# 🌍 空间三：宏观情报局
# ==========================================
elif page == "🌍 空间三：宏观情报局 (市场)":
    macro_intelligence.render_intelligence()

# ==========================================
# 📈 空间四：策略博弈沙盘
# ==========================================
elif page == "📈 空间四：策略博弈沙盘 (对冲)":
    if st.session_state['system_status'] != 'ready':
        st.error("🚨 访问受阻：资产池数据为空，无法进行沙盘推演。")
    else:
        macro_sandbox.render_sandbox()

# ==========================================
# 📖 空间五：战术白皮书
# ==========================================
elif page == "📖 空间五：战术白皮书 (术语)":
    tactical_manual.render_manual()