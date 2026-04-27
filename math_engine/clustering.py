# math_engine/clustering.py
import os
# 强行关闭底层 C 库的多线程死锁
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import pandas as pd
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import streamlit as st

def run_model(df_features, time_cols):
    try:
        # 1. 提取参与聚类的特征
        feature_cols = time_cols + ['负荷率', '基荷占比', '柔性深度']
        
        # 2. 战术防跌倒：清洗可能在 FFT 中产生的任何 NaN/Inf (完美无警告版)
        df_features = df_features.replace([np.inf, -np.inf], np.nan)
        df_features = df_features.fillna(0).infer_objects(copy=False)
        
        X = df_features[feature_cols].values
        
        # 3. 特征标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 4. PCA 降维
        pca = PCA(n_components=2)
        coords = pca.fit_transform(X_scaled)
        df_features['PCA_X'] = coords[:, 0]
        df_features['PCA_Y'] = coords[:, 1]
        
        # 5. K-Means 极速微批处理聚类 (打赢 57 万大军的关键)
        kmeans = MiniBatchKMeans(n_clusters=5, random_state=42, batch_size=10000, n_init="auto")
        clusters = kmeans.fit_predict(X_scaled)
        df_features['cluster_id'] = clusters
        
        # 6. 阵营打标 (前端报错就是因为缺这个！)
        rename_dict = {
            0: "1-基荷压舱石",
            1: "2-稳定中坚群",
            2: "3-常规作息群",
            3: "0-柔性调节营",
            4: "-1-夜间异质军"
        }
        df_features['阵营标签'] = df_features['cluster_id'].map(rename_dict)
        
        return df_features

    except Exception as e:
        st.error(f"🚨 聚类引擎遭遇数学异常: {str(e)}")
        return df_features