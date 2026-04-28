# data_bus/state_manager.py
import pandas as pd
import numpy as np
import streamlit as st

def _normalize_resolution(df, time_cols):
    """
    🎛️ 核心引擎：跨省数据分辨率统一适配器 (96点现货标准版)
    将 24点/48点 的异构数据，强制升采样为现货标准的 96点 (MW 功率)
    """
    n_points = len(time_cols)
    
    # 1. 生成标准的 96 点列名 (v0000, v0015, v0030, v0045 ... v2345)
    std_time_cols = []
    for h in range(24):
        for m in ['00', '15', '30', '45']:
            std_time_cols.append(f"v{h:02d}{m}")
            
    # 2. 如果已经是 96 点标准件，直接更换标准列名并放行
    if n_points == 96:
        df_meta = df.drop(columns=time_cols)
        df_load = pd.DataFrame(df[time_cols].values, columns=std_time_cols, index=df.index)
        return pd.concat([df_meta, df_load], axis=1), std_time_cols
        
    st.toast(f"🔄 侦测到 {n_points} 点陈旧格式，正在将其升采样对齐至 96 点现货标准...", icon="⚙️")
    
    load_matrix = df[time_cols].values
    n_samples = load_matrix.shape[0]
    
    # 构建 96 点标准容器
    standard_matrix = np.zeros((n_samples, 96))
    
    # 3. 升采样：24点 (小时级) -> 96点 (15分钟级，一分四)
    if n_points == 24:
        for i in range(24):
            standard_matrix[:, i*4] = load_matrix[:, i]
            standard_matrix[:, i*4 + 1] = load_matrix[:, i]
            standard_matrix[:, i*4 + 2] = load_matrix[:, i]
            standard_matrix[:, i*4 + 3] = load_matrix[:, i]
            
    # 4. 升采样：48点 (半小时级) -> 96点 (15分钟级，一分二)
    elif n_points == 48:
        for i in range(48):
            standard_matrix[:, i*2] = load_matrix[:, i]
            standard_matrix[:, i*2 + 1] = load_matrix[:, i]
            
    else:
        raise ValueError(f"🚨 无法识别的数据阵列格式：{n_points} 点。系统当前仅支持 24, 48, 96 点接入。")
        
    # 5. 组装新 DataFrame
    df_meta = df.drop(columns=time_cols)
    df_load = pd.DataFrame(standard_matrix, columns=std_time_cols, index=df.index)
    df_final = pd.concat([df_meta, df_load], axis=1)
    
    return df_final, std_time_cols

def init_system(uploaded_file):
    """系统点火：读取数据并执行高维洗滤"""
    try:
        with st.spinner("正在读取原始数据文件..."):
            if uploaded_file.name.endswith('.csv'):
                # 💥 升级容错装甲：遇到逗号错乱的脏数据直接跳过，绝不死机！
                df = pd.read_csv(uploaded_file, on_bad_lines='skip')
            elif uploaded_file.name.endswith('.parquet'):
                df = pd.read_parquet(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
        
        # 自动识别时间序列列
        time_cols = [c for c in df.columns if str(c).startswith('v') or str(c).replace('.','',1).isdigit()]
        
        if len(time_cols) not in [24, 48, 96]:
            st.error(f"🚨 数据格式错误：侦测到 {len(time_cols)} 个时段列。必须为 24, 48 或 96 点！")
            return
            
        with st.spinner("正在将全军坐标系强制对齐至 96 点现货标准..."):
            # 💥 调用适配器统一轨距为 96
            df, standard_time_cols = _normalize_resolution(df, time_cols)
            
        with st.spinner("正在执行降维初筛..."):
            df['日均负荷'] = df[standard_time_cols].mean(axis=1)
            df['日最大负荷'] = df[standard_time_cols].max(axis=1)
            df['负荷率'] = df['日均负荷'] / (df['日最大负荷'] + 1e-6)
            
            if '阵营标签' not in df.columns:
                df['阵营标签'] = np.random.choice(['A营-基荷压舱石', 'B营-柔性调节军', 'C营-高频异动团'], len(df))
                
        # 锁入系统内存
        st.session_state['portfolio_data'] = df
        st.session_state['time_cols'] = standard_time_cols
        st.session_state['system_status'] = 'ready'
        
        st.success("✅ 点火成功！数据轨距已全部锁定为 96 点。")
        
    except Exception as e:
        st.error(f"点火失败，请检查弹药库格式: {e}")

def clear_system():
    for key in ['portfolio_data', 'time_cols', 'system_status']:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state['system_status'] = 'standby'
    st.success("🗑️ 系统内存已清空，可挂载其他省份的数据。")