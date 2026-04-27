# math_engine/fft_processor.py
import numpy as np
import pandas as pd

def extract_features(df_clean, time_cols):
    """
    FFT 频域特征提取引擎
    """
    # 提取纯粹的 48 维负荷张量矩阵 (N x 48)
    load_matrix = df_clean[time_cols].values
    
    # 1. 计算时域基础物理量
    max_load = load_matrix.max(axis=1) + 1e-6 # 加 1e-6 防止除以 0
    mean_load = load_matrix.mean(axis=1)
    load_rate = mean_load / max_load # 负荷率
    
    # 2. 启动 FFT 频域分解 (核心矩阵运算，极速)
    # 将实数序列转换为复数频域序列
    fft_result = np.fft.rfft(load_matrix, axis=1)
    amplitudes = np.abs(fft_result) / 48.0 # 提取振幅
    
    # 3. 剥离特征波段
    # A0 (零频) 代表直流分量，即绝对基荷
    base_load_amp = amplitudes[:, 0]
    # 其余波段代表所有的波动能量
    total_ac_energy = np.sum(amplitudes[:, 1:], axis=1)
    
    # 【战术指标 1】基荷占比 (Base Ratio)：值越大，越像压舱石
    base_ratio = base_load_amp / (base_load_amp + total_ac_energy + 1e-6)
    
    # 【战术指标 2】高频柔性深度 (Flex Depth)
    # 选取高频段 (例如周期<6小时的波动) 计算其在均值中的占比
    high_freq_energy = np.sum(amplitudes[:, 4:], axis=1)
    flex_depth = high_freq_energy / (mean_load + 1e-6)
    
    # 4. 组装并返回带高维特征的新矩阵
    df_features = df_clean.copy()
    df_features['负荷率'] = load_rate
    df_features['基荷占比'] = base_ratio
    df_features['柔性深度'] = flex_depth
    
    return df_features