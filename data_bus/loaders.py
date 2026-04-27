# data_bus/loaders.py
import pandas as pd
import numpy as np
import streamlit as st
import gc

def parse_and_clean_data(uploaded_file):
    """
    终极防爆免疫版数据洗滤器 (流式分块 + 脏数据自动剔除)
    """
    try:
        time_cols = []
        
        if uploaded_file.name.endswith('.csv'):
            # 💥 核心升级：加入 on_bad_lines='skip'，直接无视并丢弃那几行破损的脏数据！
            chunk_iter = pd.read_csv(
                uploaded_file, 
                chunksize=50000, 
                on_bad_lines='skip',  # 踢除坏死数据行
                low_memory=False      # 防止类型推断警告
            )
            chunks = []
            
            for i, chunk in enumerate(chunk_iter):
                if i == 0:
                    time_cols = [col for col in chunk.columns if str(col).startswith('v') and len(str(col)) == 5]
                    if len(time_cols) != 48:
                        st.error(f"❌ 挂载失败：时空矩阵校验未通过！检测到 {len(time_cols)} 个时段。")
                        return None, None
                
                # 降维压缩
                chunk[time_cols] = chunk[time_cols].astype(np.float32)
                # 填补断点
                chunk[time_cols] = chunk[time_cols].ffill(axis=1).bfill(axis=1).fillna(0)
                
                chunks.append(chunk)
                gc.collect() 
            
            df = pd.concat(chunks, ignore_index=True)
            
        else: # Excel 处理
            df = pd.read_excel(uploaded_file)
            time_cols = [col for col in df.columns if str(col).startswith('v') and len(str(col)) == 5]
            if len(time_cols) != 48:
                st.error(f"❌ 挂载失败：检测到 {len(time_cols)} 个时段。")
                return None, None
                
            df[time_cols] = df[time_cols].astype(np.float32)
            df[time_cols] = df[time_cols].ffill(axis=1).bfill(axis=1).fillna(0)

        gc.collect()
        
        return df, time_cols
        
    except Exception as e:
        st.error(f"❌ 数据装载遭遇致命错误: {str(e)}")
        return None, None