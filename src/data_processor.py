import os
import numpy as np
import pandas as pd
from pathlib import Path


class DataProcessor:
    """数据处理类"""

    def __init__(self, config_manager):
        self.config = config_manager
        self.fs = float(self.config.get_setting("fs"))
        self.header_val = self.config.parse_hex_value(self.config.get_setting("header"))
        self.tail_val = self.config.parse_hex_value(self.config.get_setting("tail"))
        self.start_time = float(self.config.get_draw_config("start_time", 0))
        self.end_time = float(self.config.get_draw_config("end_time", 150))

    def process(self, input_file):
        self._validate_input_file(input_file)
        frames = self._read_and_validate_data(input_file)
        df = self._extract_valid_data(frames)
        # self._save_csv(df, input_file)
        return df

    def _validate_input_file(self, input_file):
        if not os.path.isfile(input_file):
            raise FileNotFoundError(f"文件 '{input_file}' 不存在")

    def _read_and_validate_data(self, input_file):
        data = np.fromfile(input_file, dtype=np.int16)
        num_frames = len(data) // self.config.frame_size
        data = data[: num_frames * self.config.frame_size]
        frames = data.reshape(num_frames, self.config.frame_size)

        print(f"原始数据点数: {len(data)}, 总帧数: {num_frames}")

        mask = (frames[:, self.config.header_idx] == self.header_val) & (
            frames[:, self.config.tail_idx] == self.tail_val
        )
        valid_frames = frames[mask]
        print(f"帧头帧尾筛选: {frames.shape[0]} -> {valid_frames.shape[0]} 帧")

        if valid_frames.shape[0] == 0:
            raise ValueError("所有帧均未通过校验")

        return valid_frames

    def _extract_valid_data(self, frames):
        time = np.arange(frames.shape[0]) / self.fs
        mask_time_range = (time >= self.start_time) & (time <= self.end_time)
        valid_frames = frames[mask_time_range]
        time = time[mask_time_range]

        print(f"时间范围筛选: {frames.shape[0]} -> {len(time)} 帧")

        raw_columns = [
            ch["source"]
            for ch in self.config.get_channels_config()
            if isinstance(ch["source"], str)
        ]
        valid_data = valid_frames[:, 1:-1]
        df = pd.DataFrame(valid_data, columns=raw_columns)
        df.insert(0, "Time(s)", time)

        df = self._apply_column_config(df)
        df = self._filter_outliers(df)
        return df

    def _apply_column_config(self, df):
        result_df = pd.DataFrame()
        result_df["Time(s)"] = df["Time(s)"]

        for channel_config in self.config.get_channels_config():
            col_name = self._get_column_name(channel_config)
            source = channel_config["source"]

            if isinstance(source, str):
                transform_func_str = channel_config.get("transform")
                result_df[col_name] = self._apply_transform(
                    df[source], transform_func_str
                )
            elif isinstance(source, dict) and "expression" in source:
                result_df[col_name] = self._apply_expression(df, source["expression"])

        return result_df

    def _get_column_name(self, channel_config):
        if "name" in channel_config:
            return channel_config["name"]
        elif isinstance(channel_config["source"], str):
            return channel_config["source"]
        elif (
            isinstance(channel_config["source"], dict)
            and "name" in channel_config["source"]
        ):
            return channel_config["source"]["name"]
        else:
            raise ValueError(f"配置中缺少列名: {channel_config}")

    def _apply_transform(self, data, transform_func_str):
        if not transform_func_str:
            return data
        try:
            transform_func = eval(transform_func_str)
            return transform_func(data)
        except Exception as e:
            print(f"警告: 无法解析转换函数 '{transform_func_str}'，使用原始数据")
            return data

    def _apply_expression(self, df, expression):
        try:
            return df.eval(expression)
        except Exception as e:
            print(f"警告: 无法计算表达式 '{expression}': {e}")
            return 0

    def _filter_outliers(self, df):
        before_len = len(df)
        for channel_config in self.config.get_channels_config():
            col_name = self._get_column_name(channel_config)
            filter_vals = channel_config.get("filter_vals", [])
            if filter_vals and col_name in df.columns:
                for val in filter_vals:
                    df = df[df[col_name] != val]
        after_len = len(df)
        if after_len < before_len:
            print(f"异常值过滤: {before_len} -> {after_len} 行")
        return df

    def save_csv(self, df, csv_path):
        df.to_csv(csv_path, index=False)
        print(f"已保存到 {csv_path}, 最终数据点数: {len(df)}")
        print("可用数据列:")
        for col in df.columns:
            print(f"  - {col}")
