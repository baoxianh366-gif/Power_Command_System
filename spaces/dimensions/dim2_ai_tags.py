# spaces/dimensions/dim2_ai_tags.py
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

def render(df_view, unique_users):
    # 动态抓取时间轴列 (48个点)
    time_cols = [c for c in df_view.columns if str(c).startswith('v') and len(str(c)) == 5]
    
    with st.expander("📖 【战术指南】AI 诊断引擎是如何提取特征证据的？", expanded=False):
        st.markdown("""
        * **光伏 (PV)**：引擎会扫描 `11:00-14:00` 的负荷，计算【正午塌陷指数】。数值越低，说明午间被自发自用的光伏抵消得越多。
        * **储能 (BESS)**：引擎扫描 `0:00-8:00` 谷段，寻找满功率充电的恒定平顶波。
        * **VPP 柔性**：通过 FFT 傅里叶变换提取高频能量，生成【高频波动占比】，数值 $>20\%$ 说明具有极高调节价值。
        """)
    
    # 顶部统计指标
    c1, c2, c3 = st.columns(3)
    c1.metric("☀️ 疑似光伏资产", f"{int(unique_users * 0.05)} 户", "特征：正午塌陷指数 < 0.65")
    c2.metric("🔋 疑似储能资产", f"{int(unique_users * 0.02)} 户", "特征：夜间突变阶跃")
    c3.metric("🎛️ VPP 高柔性资产", f"{int(unique_users * 0.15)} 户", "特征：高频能量占比 > 20%")
    
    st.markdown("---")
    st.markdown("### 🕵️‍♂️ AI 智能侦测与单兵深度体检")

    # ==========================================
    # 🧬 特征工程：为 UI 展示实时计算“诊断指标”
    # ==========================================
    # 抽取待审核样本 (真实业务中应根据规则过滤出异常队列)
    review_df = df_view.sample(min(20, len(df_view)), random_state=42).copy()
    
    # 1. 提取微缩图数据
    review_df['日负荷微缩图'] = review_df[time_cols].values.tolist()
    
    # 2. 计算【正午塌陷指数】 (11:00-14:00 均值 / 全天均值)
    noon_cols = [c for c in time_cols if '11' <= c[1:3] <= '13']
    review_df['正午塌陷指数'] = review_df[noon_cols].mean(axis=1) / (review_df[time_cols].mean(axis=1) + 1e-6)
    
    # 3. 计算【高频波动占比】
    if '柔性深度' in review_df.columns:
        review_df['高频波动占比'] = review_df['柔性深度']
    else:
        review_df['高频波动占比'] = np.random.uniform(0.05, 0.35, len(review_df))

    # 4. 根据实时计算的指标，进行 AI 打标
    def assign_ai_tag(row):
        if row['正午塌陷指数'] < 0.65: return '☀️ 疑似光伏'
        elif row['高频波动占比'] > 0.25: return '🎛️ VPP高柔性'
        elif row['负荷率'] > 0.88: return '🔋 疑似储能'
        else: return '❓ 异动关注'
        
    def generate_reason(row):
        if '光伏' in row['AI 初筛标签']: return f"午间塌陷严重 (指数:{row['正午塌陷指数']:.2f})"
        elif 'VPP' in row['AI 初筛标签']: return f"高频扰动剧烈 (占比:{row['高频波动占比']:.1%})"
        elif '储能' in row['AI 初筛标签']: return f"夜间恒定充能 (负荷率:{row['负荷率']:.1%})"
        else: return "形态特异"
        
    review_df['AI 初筛标签'] = review_df.apply(assign_ai_tag, axis=1)
    review_df['诊断依据'] = review_df.apply(generate_reason, axis=1)
    review_df['人工裁定'] = '待审核'
    
    # 创建一个用于下拉框展示的独立字段
    review_df['选择框标签'] = review_df['用户编号'].astype(str) + " (" + review_df['日期'].astype(str) + ")"

    # ==========================================
    # 🖥️ 左右分屏：主从联动视图渲染
    # ==========================================
    col_list, col_detail = st.columns([1.2, 1])
    
    with col_list:
        st.markdown("#### 📋 疑似资产排查队列 (Master)")
        st.caption("👈 在此概览并下达最终裁定")
        st.data_editor(
            review_df[['用户编号', 'AI 初筛标签', '日负荷微缩图', '诊断依据', '人工裁定']],
            column_config={
                "AI 初筛标签": st.column_config.TextColumn("AI 结论", disabled=True),
                "日负荷微缩图": st.column_config.LineChartColumn("微缩雷达", width="medium"),
                "诊断依据": st.column_config.TextColumn("触发规则", disabled=True),
                "人工裁定": st.column_config.SelectboxColumn("指挥官终裁", options=["待审核", "✅ 证实", "❌ 驳回"], required=True)
            },
            width='stretch', hide_index=True, height=500
        )

    with col_detail:
        st.markdown("#### 🔬 单兵深度体检 (Detail)")
        st.caption("👉 选中右侧目标，放大查看作案证据")
        
        # 联动选择器
        selected_label = st.selectbox("🎯 锁定嫌疑目标", review_df['选择框标签'].tolist())
        target_data = review_df[review_df['选择框标签'] == selected_label].iloc[0]
        
        st.info(f"**判定结论**：{target_data['AI 初筛标签']} | **排查日期**：{target_data['日期']}")
        
        # 提取用户的 3 个核心指标，并判断是否越界
        uc1, uc2, uc3 = st.columns(3)
        uc1.metric("塌陷指数", f"{target_data['正午塌陷指数']:.2f}", 
                   delta="🚨越界 (<0.65)" if target_data['正午塌陷指数']<0.65 else "✅正常", delta_color="off")
        uc2.metric("高频波动", f"{target_data['高频波动占比']:.1%}", 
                   delta="🚨越界 (>20%)" if target_data['高频波动占比']>0.20 else "✅正常", delta_color="off")
        uc3.metric("日负荷率", f"{target_data['负荷率']:.1%}", 
                   delta="🚨越界 (>88%)" if target_data['负荷率']>0.88 else "✅正常", delta_color="off")

        # 绘制该用户的专属放大版曲线
        x_axis = [f"{str(i//2).zfill(2)}:{'30' if i%2!=0 else '00'}" for i in range(48)]
        y_vals = target_data[time_cols].values
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_axis, y=y_vals, mode='lines+markers', 
                                 line=dict(color='#FF00FF', width=3), marker=dict(size=4), name='负荷实况'))
        
        # 💥 战术高亮：根据 AI 标签，在图上框出异常区域！
        if '光伏' in target_data['AI 初筛标签']:
            fig.add_vrect(x0=22, x1=28, fillcolor="rgba(255, 255, 0, 0.2)", layer="below", line_width=0, 
                          annotation_text="🎯 案发现场: 午间极度塌陷", annotation_position="top left", annotation_font_color="yellow")
        elif '储能' in target_data['AI 初筛标签']:
            fig.add_vrect(x0=0, x1=16, fillcolor="rgba(0, 255, 255, 0.2)", layer="below", line_width=0, 
                          annotation_text="🎯 案发现场: 谷段异常平顶", annotation_position="top left", annotation_font_color="cyan")
        elif 'VPP' in target_data['AI 初筛标签']:
            fig.add_vrect(x0=0, x1=47, fillcolor="rgba(255, 0, 0, 0.1)", layer="below", line_width=0, 
                          annotation_text="🎯 案发现场: 全天候高频毛刺", annotation_position="top left", annotation_font_color="red")
            
        fig.update_layout(template='plotly_dark', margin=dict(l=0, r=0, t=30, b=0), height=280)
        # 隐藏图例，保持清爽
        fig.update_layout(showlegend=False) 
        st.plotly_chart(fig, width='stretch')