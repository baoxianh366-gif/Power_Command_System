# ⚡ 电力交易策略指挥官 (Power Command System)

基于 Streamlit 的电力现货交易资产池分析与策略推演驾驶舱。面向售电公司、虚拟电厂 (VPP) 运营商及电力交易员，提供从数据接入到战术决策的全链路分析能力。

---

## 功能架构

系统由五大战略空间组成：

| 空间 | 模块 | 功能描述 |
|------|------|----------|
| 🛰️ 空间一 | 数据总线 | CSV/Excel 数据接入、48点负荷矩阵校验与初始化 |
| 🔬 空间二 | 微观资产池 | 企业级用电画像：FFT频域分析、AI标签侦测、PCA聚类、对冲矩阵 |
| 🌍 空间三 | 宏观情报局 | 现货电价走势、气象与新能源出力、政策事件日历 |
| 📈 空间四 | 策略博弈沙盘 | 头寸推演、盈亏测算、CVaR 风险预演 (预留扩展) |
| 📖 空间五 | 战术白皮书 | 核心指标术语与实战交易应用指南 |

---

## 技术栈

- **前端界面**: [Streamlit](https://streamlit.io/)
- **数据处理**: Pandas, NumPy
- **机器学习**: scikit-learn (MiniBatchKMeans, PCA)
- **可视化**: Plotly
- **频域分析**: NumPy FFT

---

## 快速启动

### 1. 克隆仓库

```bash
git clone https://github.com/<your-username>/Power_Command_System.git
cd Power_Command_System
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动应用

```bash
streamlit run app.py
```

---

## 数据格式要求

系统唯一的输入数据源为包含 **用户ID、日期和48个时段电量** 的宽表：

| 用户编号 | 日期 | v0030 | v0100 | v0130 | ... | v0000 |
|----------|------|-------|-------|-------|-----|-------|
| U001 | 2025-01-01 | 12.5 | 11.3 | ... | ... | 10.2 |

- 时间列以 `v` 开头，共 **48列**，代表每日 48 个半点时段
- 支持 `.csv` 和 `.xlsx` 格式

---

## 项目结构

```
Power_Command_System/
├── app.py                      # Streamlit 入口
├── requirements.txt            # Python 依赖
├── config/                     # 省份电价规则配置 (预留)
├── data_bus/                   # 数据总线
│   ├── state_manager.py        # 系统状态与生命周期管理
│   ├── loaders.py              # 数据清洗与加载
│   └── tou_manager.py          # 分时电价引擎 (浙江2025)
├── math_engine/                # 高维数学引擎
│   ├── fft_processor.py        # FFT 频域特征提取
│   └── clustering.py           # PCA 降维与 K-Means 聚类
└── spaces/                     # 前端作战空间
    ├── dimensions/             # 微观资产池四大维度
    ├── micro_portfolio.py
    ├── macro_intelligence.py
    ├── macro_sandbox.py
    └── tactical_manual.py
```

---

## 核心设计准则

1. **单一事实来源**: 唯一输入为 48 点负荷宽表，杜绝多数据源冲突
2. **状态机管理**: 明确的生命周期 `[待机] → [装载] → [运行] → [清空]`
3. **算法与业务解耦**: 数学引擎纯物理计算，业务规则由独立配置文件驱动

---

## 许可证

MIT License
