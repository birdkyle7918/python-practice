import numpy as np
import random
import os
from tqdm import tqdm

# --- 参数设置 ---
GRID_SIZE = 8000
TARGET_OBSTACLE_RATIO = 0.30
# 您可以调整圆形的最小和最大半径来改变障碍物的形态
MIN_RADIUS = 30
MAX_RADIUS = 250
OUTPUT_FILENAME = 'obstacle_grid_8000x8000.npz'


def create_grid_with_circular_obstacles():
    """
    生成一个带有圆形障碍物的大型二进制网格。

    Returns:
        np.ndarray: 生成的二进制网格。
    """
    print(f"开始创建 {GRID_SIZE}x{GRID_SIZE} 的网格...")
    # 使用 uint8 类型以节省内存，0 代表可通行，1 代表障碍物
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)

    total_points = GRID_SIZE * GRID_SIZE
    target_obstacle_points = int(total_points * TARGET_OBSTACLE_RATIO)
    current_obstacle_points = 0

    # 使用 tqdm 创建一个进度条
    with tqdm(total=target_obstacle_points, desc="正在生成障碍物") as pbar:
        while current_obstacle_points < target_obstacle_points:
            # 1. 随机选择圆心和半径
            center_x = random.randint(0, GRID_SIZE - 1)
            center_y = random.randint(0, GRID_SIZE - 1)
            radius = random.randint(MIN_RADIUS, MAX_RADIUS)

            # 2. 计算圆形的边界框（优化计算）
            x_start = max(0, center_x - radius)
            x_end = min(GRID_SIZE, center_x + radius + 1)
            y_start = max(0, center_y - radius)
            y_end = min(GRID_SIZE, center_y + radius + 1)

            # 3. 在边界框内生成坐标网格
            sub_yy, sub_xx = np.mgrid[y_start:y_end, x_start:x_end]

            # 4. 计算到圆心的距离并创建掩码
            dist_sq = (sub_yy - center_y) ** 2 + (sub_xx - center_x) ** 2
            mask = dist_sq <= radius ** 2

            # 5. 将圆形区域设置为障碍物 (1)
            grid[y_start:y_end, x_start:x_end][mask] = 1

            # 6. 更新当前障碍物点数和进度条
            new_obstacle_points = np.sum(grid)
            # 更新进度条的增量
            pbar.update(new_obstacle_points - current_obstacle_points)
            current_obstacle_points = new_obstacle_points

    return grid


def main():
    """
    主函数：生成网格、验证并保存。
    """
    # 生成网格
    obstacle_grid = create_grid_with_circular_obstacles()

    # 验证最终结果
    print("\n--- 生成完毕 ---")
    final_obstacle_count = np.sum(obstacle_grid)
    total_points = obstacle_grid.size
    final_ratio = final_obstacle_count / total_points

    print(f"网格尺寸: {obstacle_grid.shape}")
    print(f"总计点数: {total_points:,}")
    print(f"障碍物点数: {final_obstacle_count:,}")
    print(f"最终障碍物比例: {final_ratio:.4f}")

    # 保存为压缩的 .npz 文件
    print(f"\n正在将网格保存到 '{OUTPUT_FILENAME}'...")
    # 使用 savez_compressed 可以显著减小文件大小
    # 将数组命名为 'grid' 以便后续加载
    np.savez_compressed(OUTPUT_FILENAME, grid=obstacle_grid)

    # 检查文件大小
    file_size_mb = os.path.getsize(OUTPUT_FILENAME) / (1024 * 1024)
    print(f"文件保存成功！ 文件大小: {file_size_mb:.2f} MB")


if __name__ == '__main__':
    # 确保在运行前已安装必要的库
    main()