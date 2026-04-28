# spaces/dimensions/dim4_synergy.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def render(df_view, df_global, time_cols):
    x_axis = [f"{str(i//4).zfill(2)}:{str((i%4)*15).zfill(2)}" for i in range(96)]
    
    # ==========================================
    # 🗺️ 上半部分：规律扫描与对冲
    # ==========================================
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🕒 时间指纹：周频段节律热力图")
        df_heat = df_view.copy()
        df_heat['星期'] = pd.to_datetime(df_heat['日期']).dt.dayofweek
        heatmap_data = df_heat.groupby('星期')[time_cols].mean()
        heatmap_data.index = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][:len(heatmap_data)]
        fig_heat = px.imshow(heatmap_data.values, x=x_axis, y=heatmap_data.index, color_continuous_scale="Viridis", aspect="auto")
        fig_heat.update_layout(template='plotly_dark', margin=dict(l=0, r=0, t=10, b=0), height=300)
        st.plotly_chart(fig_heat, use_container_width=True)
        
    with c2:
        st.subheader("⚙️ 对冲矩阵：互补特征分析")
        cluster_means = df_global.groupby('阵营标签')[time_cols].mean().T
        corr_matrix = cluster_means.corr()
        fig_corr = px.imshow(corr_matrix, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1, aspect="auto")
        fig_corr.update_layout(template='plotly_dark', margin=dict(l=0, r=0, t=10, b=0), height=300)
        fig_corr.update_xaxes(showticklabels=False)
        st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown("---")

    # ==========================================
    # 🚨 下半部分：洛伦兹集中度警报系统
    # ==========================================
    st.markdown("### 🚨 资产集中度与违约风险防线")
    
    # 1. 核心计算：按用户聚合总电量
    user_energy = df_view.groupby('用户编号')[time_cols].sum().sum(axis=1).sort_values(ascending=False)
    total_energy_pool = user_energy.sum()
    
    # 2. 帕累托指标计算 (Top 5% 用户)
    top_5_percent_count = max(1, int(len(user_energy) * 0.05))
    top_5_percent_energy = user_energy.iloc[:top_5_percent_count].sum()
    energy_ratio = top_5_percent_energy / (total_energy_pool + 1e-6)
    
    # 计算基尼系数 (简易梯形法)
    cum_energy = np.cumsum(user_energy.values) / total_energy_pool
    # 计算基尼系数 (兼容 NumPy 1.x 和 2.0+ 双版本)
    try:
        # 尝试使用 NumPy 2.0+ 的新语法
        gini = 1 - 2 * np.trapezoid(cum_energy, dx=1/len(user_energy))
    except AttributeError:
        # 如果报错，退回使用 NumPy 1.x 的旧语法
        gini = 1 - 2 * np.trapz(cum_energy, dx=1/len(user_energy))

    # 3. 渲染警报雷达看板
    ac1, ac2, ac3 = st.columns([1, 1, 1])
    with ac1:
        st.metric("核心基尼系数", f"{gini:.3f}", help="0=绝对平均, 1=绝对集中。超过 0.4 为警戒区，0.6 以上为极度危险。")
    with ac2:
        status_color = "normal" if energy_ratio < 0.5 else "inverse"
        st.metric("5% 头部集中度", f"{energy_ratio:.1%}", delta="帕累托警戒" if energy_ratio > 0.5 else "安全区间", delta_color=status_color)
    with ac3:
        top_user_id = user_energy.index[0]
        st.metric("头号资产占比", f"{user_energy.iloc[0]/total_energy_pool:.1%}", help=f"最大用户编号: {top_user_id}")

    # 4. 左右排布：曲线图与大户清单
    lc1, lc2 = st.columns([1.5, 1])
    
    with lc1:
        st.markdown("#### 💹 洛伦兹风险收益曲线")
        cum_users = np.linspace(0, 1, len(user_energy))
        # 翻转曲线使其符合传统习惯 (从小到大累加)
        user_energy_asc = user_energy.sort_values(ascending=True)
        cum_energy_asc = np.cumsum(user_energy_asc.values) / total_energy_pool
        
        fig_lorenz = go.Figure()
        fig_lorenz.add_trace(go.Scatter(x=cum_users, y=cum_users, mode='lines', line=dict(color='gray', dash='dash'), name='绝对平均线'))
        fig_lorenz.add_trace(go.Scatter(x=cum_users, y=cum_energy_asc, mode='lines', fill='tonexty', 
                                         line=dict(color='#FFCC00', width=4), name='当前资产分布'))
        
        # 风险阴影区
        if gini > 0.5:
            st.warning(f"🚨 **系统风险提示**：当前基尼系数 ({gini:.2f}) 极高！资产池过度依赖少数大客户。")

        fig_lorenz.update_layout(template='plotly_dark', height=400, margin=dict(l=0, r=0, t=10, b=0),
                                 xaxis_title="用户累计占比", yaxis_title="电量累计占比")
        st.plotly_chart(fig_lorenz, use_container_width=True)

    with lc2:
        st.markdown("#### 🏆 头部大户“哨兵”名单")
        st.caption("该阵营中贡献度前 10 的核心资产及其风险权重")
        
        # 构建大户列表 DataFrame
        top_10_df = pd.DataFrame({
            "用户编号": user_energy.index[:10],
            "总贡献电量": user_energy.values[:10],
            "资产权重": (user_energy.values[:10] / total_energy_pool)
        })
        
        st.table(top_10_df.style.format({
            "总贡献电量": "{:,.0f}",
            "资产权重": "{:.2%}"
        }))
        
        st.info("💡 **战术建议**：针对权重超过 10% 的单一用户，建议签署带违约补偿的“双向锁定合同”。")