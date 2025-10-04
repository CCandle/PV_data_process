# Data Processing and Visualization Project

本项目用于处理原始 `.dat` 格式的数据文件，自动完成数据解析、清洗、存储，并支持可视化绘制。  
项目支持通过 **YAML 配置文件** 定义数据列和处理规则，具有良好的可扩展性和灵活性。  

---

## ✨ 功能特性

- **数据读取**：自动从 `data/raw` 中读取最新的原始 `.dat` 文件。  
- **数据清洗**：支持根据配置过滤无效值、异常值。  
- **数据存储**：处理后的数据自动保存到 `data/processed` 文件夹。  
- **可视化绘制**：支持多列数据波形的绘制。  
- **配置化管理**：通过 `config/data_config.yml` 灵活定义列名、忽略值、新增计算列。  
- **命令行参数**：支持从命令行指定输入/输出路径。  

---

## 📂 项目结构
```
├── main.py # 主入口，运行程序
├── requirements.txt # 项目依赖
├── README.md # 使用文档
├── config/
│ └── data_config.yml # 数据列与处理规则配置文件
├── data/
│ ├── raw/ # 存放原始 .dat 数据文件
│ └── processed/ # 存放处理后的 .csv 文件
└── src/
  ├── data_processor.py # 数据读取与清洗逻辑
  ├── data_plotter.py # 数据可视化逻辑
  ├── config_manager.py # 配置文件解析与管理
  └── init.py
```
---

## 🛠️ 环境安装

### 1. 克隆项目
```bash
git clone https://github.com/yourname/yourproject.git
cd yourproject
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```
（推荐使用 conda 或 venv 创建虚拟环境）

---

## ⚙️ 配置文件说明
配置文件位于 config/data_config.yml，用于定义数据列及规则。
示例：
```yml
columns:
  BoostVolt1:
    ignore: []
  BoostVolt2:
    ignore: []
  BoostCurr1(A):
    ignore: [326.67, 204.79]   # 忽略异常值
  Vbalance.Uref(V):
    ignore: []
  Iboost_PICtl.Out:
    ignore: []
  d:
    ignore: []
  delta_D:
    ignore: []
  InvFault:
    ignore: []

derived_columns:
  Power: "lambda row: row['BoostVolt1'] * row['BoostCurr1(A)']"
```
+ columns：定义原始列及需要忽略的值。
+ derived_columns：定义新列（通过表达式计算）。

---

## 🚀 使用方法
运行主程序
默认会读取 `data/raw` 中最新的 `.dat` 文件，并输出到 `data/processed`：
```bash
python main.py
```
指定输入文件和输出路径
```bash
python main.py input.dat output.csv
```

---

## 📊 输出说明
+ 处理后数据：以 CSV 格式保存到 `data/processed/`
+ 可视化图像：运行时会弹出波形图窗口，绘制配置中指定的列。

---

## 📖 示例
输入文件：`data/raw/2025-10-03 20-56-44Detaildata.dat`
运行：
```bash
python main.py
```
输出：
+清洗后的数据保存为：
`data/processed/2025-10-03 20-56-44Detaildata.csv`
+终端打印：
```bash
原始数据点数: 13824000
总帧数: 864000
异常值过滤: 864000 -> 863668 行
已保存到 data/processed/2025-10-03 20-56-44Detaildata.csv
```
---
## 📜 许可证

本项目使用 MIT License，详情见 [LICENSE](LICENSE)。

---

## 👨‍💻 作者
开发者: [CCandle]()
联系方式: 2987794676@qq.com