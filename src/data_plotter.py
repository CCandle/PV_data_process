import math
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


class DataPlotter:
    """数据绘图类"""

    def __init__(self, config_manager):
        self.config = config_manager
        self.cols_per_row = int(self.config.get_draw_config("cols_per_row", 2))
        self.xaxis_interval = self.config.get_draw_config("xaxis_interval", 5)
        self.column_groups = self.config.get_column_groups()
        self._setup_plot_style()
        self.linked_axes = None

    def _setup_plot_style(self):
        plt.rc("font", size=9)
        plt.rc("axes", titlesize=9)
        plt.rc("axes", labelsize=8)
        plt.rc("xtick", labelsize=7)
        plt.rc("ytick", labelsize=7)
        plt.rc("legend", fontsize=7)

    def plot(self, df):
        self._validate_columns(df)
        n_plots = len(self.column_groups)

        # 计算网格布局
        cols = min(self.cols_per_row, n_plots)
        rows = math.ceil(n_plots / cols)

        # 创建子图网格
        fig, axes = plt.subplots(
            rows, cols, squeeze=False, figsize=(6 * cols, 3 * rows)
        )

        time_range = df["Time(s)"].max() - df["Time(s)"].min()
        self.linked_axes = self.LinkedAxes(df, self.xaxis_interval)

        # 按列优先顺序填充子图
        for i, group_config in enumerate(self.column_groups):
            # 计算子图位置（列优先）
            row_idx = i % rows
            col_idx = i // rows

            # 如果列数超过实际需要的列数，跳过多余位置
            if col_idx >= cols:
                continue

            ax = axes[row_idx, col_idx]
            self._plot_group(ax, group_config, df, time_range)

        self._finalize_plot(fig, axes, n_plots, cols, rows)

    def _validate_columns(self, df):
        all_plot_cols = [
            col for group in self.column_groups for col in group["columns"]
        ]
        missing_cols = [col for col in all_plot_cols if col not in df.columns]
        if missing_cols:
            print(f"警告: 以下配置的列名在数据中不存在: {missing_cols}")
            raise ValueError("配置列名不存在")

    def _plot_group(self, ax, group_config, df, time_range):
        col_names = group_config["columns"]
        title = group_config.get("title", ", ".join(col_names))
        yaxis_range = group_config.get("yaxis")
        for col in col_names:
            ax.plot(df["Time(s)"], df[col], label=col, lw=1)

        # 修改标题设置：增加与纵坐标的间距，设置固定位置对齐
        ax.set_ylabel(title, fontsize=9, rotation=90, ha="center", va="center")
        # 设置标题位置，使其对齐
        ax.yaxis.set_label_coords(-0.053, 0.5)  # 调整x坐标增加间距，y坐标居中

        self._setup_xaxis_ticks(ax, time_range)

        # 设置纵坐标数值逆时针旋转45度
        ax.tick_params(axis="y", rotation=45)

        if len(col_names) > 1:
            ax.legend(fontsize=7)
        self.linked_axes.add_axis(ax, col_names, yaxis_range)
        ax.callbacks.connect("xlim_changed", self.linked_axes.on_xlims_change)

    def _setup_xaxis_ticks(self, ax, time_range):
        major_interval = (
            float(self.xaxis_interval)
            if self.xaxis_interval != "auto"
            else self._calculate_optimal_interval(time_range)
        )
        minor_interval = self._get_minor_interval(major_interval)
        ax.xaxis.set_major_locator(MultipleLocator(major_interval))
        ax.xaxis.set_minor_locator(MultipleLocator(minor_interval))
        ax.grid(True, which="major", linestyle="-", alpha=0.7)
        ax.grid(True, which="minor", linestyle="--", alpha=0.4)

    def _calculate_optimal_interval(self, time_range):
        intervals = [
            (0.01, 0.001),
            (0.05, 0.005),
            (0.1, 0.01),
            (0.5, 0.05),
            (1, 0.1),
            (5, 0.5),
            (10, 1),
            (50, 5),
            (100, 10),
        ]
        for threshold, interval in intervals:
            if time_range <= threshold:
                return interval
        return 20

    def _get_minor_interval(self, major_interval):
        if major_interval >= 10:
            return 2
        if major_interval >= 5:
            return 1
        if major_interval >= 1:
            return 0.5
        if major_interval >= 0.1:
            return 0.05
        if major_interval >= 0.01:
            return 0.005
        return major_interval / 5

    def _finalize_plot(self, fig, axes, n_plots, cols, rows):
        # 为每列的最后一个子图设置x轴标签
        for col_idx in range(cols):
            # 找到该列的最后一个非空子图
            for row_idx in range(rows - 1, -1, -1):
                if row_idx * cols + col_idx < n_plots:
                    axes[row_idx, col_idx].set_xlabel("Time (s)", fontsize=8)
                    break

        # 删除多余的空子图
        for i in range(n_plots, rows * cols):
            row_idx = i % rows
            col_idx = i // rows
            if col_idx < cols:  # 确保不超出列范围
                fig.delaxes(axes[row_idx, col_idx])

        # 调整布局
        plt.subplots_adjust(
            left=0.033, right=0.99, bottom=0.05, top=0.98, wspace=0.07, hspace=0.15
        )
        plt.show()

    class LinkedAxes:
        """联动坐标轴"""

        def __init__(self, df, xaxis_interval):
            self.axes, self.lines, self.fixed_yaxis = [], {}, {}
            self.df, self.updating, self.xaxis_interval = df, False, xaxis_interval

        def add_axis(self, ax, col_names, yaxis_range=None):
            self.axes.append(ax)
            self.lines[ax] = col_names
            if yaxis_range:
                self.fixed_yaxis[ax] = yaxis_range
                ax.set_ylim(yaxis_range)
            # 确保新添加的轴也有旋转的纵坐标数值
            ax.tick_params(axis="y", rotation=45)

        def on_xlims_change(self, event_ax):
            if self.updating:
                return
            new_xlim, self.updating = event_ax.get_xlim(), True
            try:
                for ax in self.axes:
                    if ax is event_ax:
                        continue
                    ax.callbacks.disconnect("xlim_changed")
                    ax.set_xlim(new_xlim)
                    ax.callbacks.connect("xlim_changed", self.on_xlims_change)
                    self._update_xaxis_ticks(ax, new_xlim)
                    self._auto_adjust_yaxis(ax, new_xlim)
                    ax.figure.canvas.draw_idle()
                self._update_xaxis_ticks(event_ax, new_xlim)
                event_ax.figure.canvas.draw_idle()
            finally:
                self.updating = False

        def _update_xaxis_ticks(self, ax, x_range):
            time_range = x_range[1] - x_range[0]
            major_interval = (
                float(self.xaxis_interval)
                if self.xaxis_interval != "auto"
                else self._calculate_optimal_interval(time_range)
            )
            minor_interval = self._get_minor_interval(major_interval)
            ax.xaxis.set_major_locator(MultipleLocator(major_interval))
            ax.xaxis.set_minor_locator(MultipleLocator(minor_interval))

        def _auto_adjust_yaxis(self, ax, x_range):
            if ax in self.fixed_yaxis:
                return
            col_names, time_col = self.lines[ax], self.df["Time(s)"]
            mask = (time_col >= x_range[0]) & (time_col <= x_range[1])
            if not mask.any():
                return
            y_min, y_max = float("inf"), float("-inf")
            for col in col_names:
                if col in self.df.columns:
                    vals = self.df.loc[mask, col]
                    if len(vals) > 0:
                        y_min, y_max = min(y_min, vals.min()), max(y_max, vals.max())
            if y_min != float("inf") and y_max != float("-inf"):
                y_range = y_max - y_min or abs(y_min) * 0.1 or 1
                ax.set_ylim(y_min - y_range * 0.1, y_max + y_range * 0.1)

        def _calculate_optimal_interval(self, time_range):
            intervals = [
                (0.01, 0.001),
                (0.05, 0.005),
                (0.1, 0.01),
                (0.5, 0.05),
                (1, 0.1),
                (5, 0.5),
                (10, 1),
                (50, 5),
                (100, 10),
            ]
            for threshold, interval in intervals:
                if time_range <= threshold:
                    return interval
            return 20

        def _get_minor_interval(self, major_interval):
            if major_interval >= 10:
                return 2
            if major_interval >= 5:
                return 1
            if major_interval >= 1:
                return 0.5
            if major_interval >= 0.1:
                return 0.05
            if major_interval >= 0.01:
                return 0.005
            return major_interval / 5
