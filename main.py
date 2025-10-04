import sys
import os
import glob
from src.config_manager import ConfigManager
from src.data_processor import DataProcessor
from src.data_plotter import DataPlotter


def get_latest_dat_file(raw_dir="data/raw"):
    """获取 raw 目录下最新的 dat 文件"""
    files = glob.glob(os.path.join(raw_dir, "*.dat"))
    if not files:
        raise FileNotFoundError(f"目录 {raw_dir} 下没有找到任何 dat 文件")
    return max(files, key=os.path.getmtime)


def main():
    # ========== 输入文件 ==========
    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    else:
        input_file = get_latest_dat_file("data/raw")
        print(f"未指定输入文件，默认使用最新文件: {input_file}")

    # ========== 配置文件 ==========
    config_file = sys.argv[2] if len(sys.argv) >= 3 else "config/data_config.yml"

    # try:
    config_manager = ConfigManager(config_file)
    processor = DataProcessor(config_manager)

    # 处理数据
    df = processor.process(input_file)

    # 绘图
    if len(df) > 0:
        fig_out = os.path.splitext(os.path.basename(input_file))[0] + ".png"
        fig_out = os.path.join("data", "waves", fig_out)
        plotter = DataPlotter(config_manager, fig_out)
        plotter.plot(df)

    # except Exception as e:
    #     print(f"错误: {e}")
    #     sys.exit(1)


if __name__ == "__main__":
    main()
