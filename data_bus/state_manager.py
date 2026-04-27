import streamlit as st
import time
from .loaders import parse_and_clean_data
from math_engine import fft_processor
from math_engine import clustering 

def init_system(uploaded_file):
    """带实时雷达侦察的数据初始化引擎"""
    if st.session_state.get('system_status') == 'ready':
        st.toast("系统已就绪。")
        return

    with st.spinner("⚙️ 正在执行侦察模式...请同时观察您的终端(黑框框)里的日志输出！"):
        print("\n" + "="*40)
        print("🚀 [雷达日志] 1. 开始解析 Excel/CSV 文件...")
        
        df_clean, time_cols = parse_and_clean_data(uploaded_file)
        if df_clean is None:
            print("❌ [雷达日志] 数据加载失败，已终止。")
            return 
            
        print(f"✅ [雷达日志] 2. 文件解析成功，总数据量: {len(df_clean)} 行。")
        st.write(f"📊 成功读取装载: 总计 {len(df_clean)} 条日运行记录。")
        
        # ---------------------------------------------------------
        # 💥 核心战术：截断防线 💥
        # 我们强行只派前 1000 个士兵去冲锋，测试引擎是否通畅！
        # ---------------------------------------------------------
        #df_test = df_clean.head(1000).copy()
        #print("⚔️ [雷达日志] 3. 已截取前 1000 条数据作为侦察小队，准备送入数学引擎。")
        
        try:
            print("⚡ [雷达日志] 4. 正在呼叫 FFT 频域扫描引擎...")
            st.write("⚡ 正在启动 FFT 频域扫描 (侦察小队1000条)...")
            df_features = fft_processor.extract_features(df_clean, time_cols)
            print("✅ [雷达日志] 5. FFT 扫描完成！")
            
            print("🌌 [雷达日志] 6. 正在呼叫 PCA 与高维聚类引擎...")
            st.write("🌌 正在进行高维空间聚类与 PCA 降维...")
            df_portfolio = clustering.run_model(df_features, time_cols)
            print("✅ [雷达日志] 7. 聚类引擎运行完成！")
            
        except Exception as e:
            print(f"❌ [雷达日志] 引擎遭遇致命错误: {str(e)}")
            st.error(f"引擎运行报错: {str(e)}")
            return

        print("💾 [雷达日志] 8. 计算完毕，准备将数据锁入 Streamlit 内存...")
        # 存入内存
        st.session_state['raw_data'] = df_clean
        st.session_state['time_cols'] = time_cols
        st.session_state['portfolio_data'] = df_portfolio 
        st.session_state['system_status'] = 'ready'
        print("✅ [雷达日志] 9. 内存锁定成功！系统准备重新加载网页。")
        print("="*40 + "\n")
        
    st.rerun() 

def clear_system():
    """一键清空协议：释放内存，抹除特征"""
    st.session_state['system_status'] = 'standby'
    
    # 清理所有挂载的内存字典
    keys_to_clear = ['raw_data', 'time_cols', 'portfolio_data', 'global_portfolio_data', 'current_tou_vector']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
            
    st.rerun()