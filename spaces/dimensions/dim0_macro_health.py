# spaces/dimensions/dim0_macro_health.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def render(df_view, time_cols, unique_users):
    """插件 0：全局静态体检与极限探测 (配备多尺度时空切片器)"""
    
    st.caption("核心目标：摸清底牌。通过多尺度切片探测该阵营的规模基盘、热力节律与极值风险边界。")
    
    # ==========================================
    # 🕒 核心增强：时空切片雷达控制台
    # ==========================================
    st.markdown("### 🕒 时空探测雷达：多尺度切片")
    
    slice_mode = st.radio(
        "选择战术透视尺度", 
        ["全景 (Year)", "季度 (Quarter)", "月份 (Month)", "周次 (Week)", "单日定点 (Day)"], 
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # 将日期列标准化以便进行时序过滤
    df_sliced = df_view.copy()
    df_sliced['日期'] = pd.to_datetime(df_sliced['日期'])
    
    # 生成二级联动过滤选项
    col_ctrl1, col_ctrl2 = st.columns([1, 4])
    with col_ctrl1:
        if slice_mode == "季度 (Quarter)":
            quarter = st.selectbox("🎯 锁定目标季度", [1, 2, 3, 4], format_func=lambda x: f"Q{x} 季度")
            df_sliced = df_sliced[df_sliced['日期'].dt.quarter == quarter]
        elif slice_mode == "月份 (Month)":
            month = st.selectbox("🎯 锁定目标月份", list(range(1, 13)), format_func=lambda x: f"{x} 月")
            df_sliced = df_sliced[df_sliced['日期'].dt.month == month]
        elif slice_mode == "周次 (Week)":
            min_week = int(df_sliced['日期'].dt.isocalendar().week.min())
            max_week = int(df_sliced['日期'].dt.isocalendar().week.max())
            week = st.slider("🎯 拖动锁定周次", min_value=min_week, max_value=max_week, value=min_week)
            df_sliced = df_sliced[df_sliced['日期'].dt.isocalendar().week == week]
        elif slice_mode == "单日定点 (Day)":
            min_date = df_sliced['日期'].min().date()
            max_date = df_sliced['日期'].max().date()
            target_date = st.date_input("🎯 锁定具体日期", value=min_date, min_value=min_date, max_value=max_date)
            df_sliced = df_sliced[df_sliced['日期'].dt.date == target_date]
            
    st.divider()
    
    if len(df_sliced) == 0:
        st.warning("🚨 侦测失败：在您锁定的时间切片内，未扫描到有效负荷数据！")
        return
        
    # ==========================================
    # 📊 第一部分：基于切片的动态 KPIs
    # ==========================================
    c1, c2, c3, c4 = st.columns(4)
    
    # 1. 切片内总电量
    total_energy = df_sliced[time_cols].sum().sum()
    c1.metric(f"🔋 [{slice_mode.split()[0]}] 总电量 (MWh)", f"{total_energy:,.0f}")
    
    # 2. 动态同时率计算 (取切片内负荷最高的一天测算)
    daily_energy = df_sliced.groupby('日期')[time_cols].sum().sum(axis=1)
    max_day = daily_energy.idxmax()
    df_peak_day = df_sliced[df_sliced['日期'] == max_day]
    
    if len(df_peak_day) > 0:
        agg_peak = df_peak_day[time_cols].sum(axis=0).max()
        sum_of_peaks = df_peak_day[time_cols].max(axis=1).sum()
        coincidence_factor = agg_peak / (sum_of_peaks + 1e-6)
        c2.metric("🛡️ 切片内极值日同时率", f"{coincidence_factor:.1%}", help="值越大，说明该群体在切片内的叠加风险越高。")
    else:
        c2.metric("🛡️ 极值日同时率", "N/A")
        
    # 3. 极值定位
    min_day = daily_energy.idxmin()
    c3.metric("🔥 切片内最高负荷日", str(max_day)[:10])
    c4.metric("🧊 切片内最低负荷日", str(min_day)[:10])

    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==========================================
    # 🗺️ 第二部分：动态视觉图表
    # ==========================================
    col_left, col_right = st.columns([2, 1])
    y_times = [f"{str(i//2).zfill(2)}:{'30' if i%2!=0 else '00'}" for i in range(48)]
    
    with col_left:
        st.subheader("高维全景地毯图 (Carpet Plot)")
        st.caption("横轴：日期 | 纵轴：48个时段。颜色越亮代表负荷越重。")
        
        carpet_data = df_sliced.groupby('日期')[time_cols].mean().T
        x_dates = carpet_data.columns.astype(str).str[:10]
        
        fig_carpet = px.imshow(
            carpet_data.values, 
            x=x_dates, y=y_times,
            aspect="auto", color_continuous_scale="Inferno"
        )
        fig_carpet.update_layout(template='plotly_dark', margin=dict(l=0, r=0, t=10, b=0), height=350)
        fig_carpet.update_yaxes(showticklabels=False)
        st.plotly_chart(fig_carpet, width='stretch')

    with col_right:
        # 💥 智能判定：如果是单日切片，折线图自动变形为“48点日内巡航图”
        if slice_mode == "单日定点 (Day)":
            st.subheader("日内负荷巡航 (Intraday)")
            st.caption(f"聚焦目标日 {target_date} 全天48点走势")
            
            day_curve = df_sliced[time_cols].sum(axis=0)
            fig_trend = px.line(x=y_times, y=day_curve.values, labels={'x': '时段 (48点)', 'y': '聚合功率'})
            fig_trend.update_layout(template='plotly_dark', margin=dict(l=0, r=0, t=10, b=0), height=350)
            
        # 其他多日切片：正常显示切片期间的日极值走势
        else:
            st.subheader("切片极值巡航 (Trends)")
            st.caption(f"跟踪所选【{slice_mode.split()[0]}】时间跨度内的日均起伏")
            
            fig_trend = px.line(x=daily_energy.index, y=daily_energy.values, labels={'x': '日期', 'y': '日总电量'})
            fig_trend.update_layout(template='plotly_dark', margin=dict(l=0, r=0, t=10, b=0), height=350)
            # 打上战术标记
            fig_trend.add_scatter(x=[max_day], y=[daily_energy.max()], mode='markers', marker=dict(color='red', size=10), name='局部最高')
            fig_trend.add_scatter(x=[min_day], y=[daily_energy.min()], mode='markers', marker=dict(color='blue', size=10), name='局部最低')
            
        st.plotly_chart(fig_trend, width='stretch')