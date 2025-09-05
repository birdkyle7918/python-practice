"""
二维astar算法
"""
import heapq
from collections import defaultdict
from typing import TypeAlias, Annotated

import numpy as np
import numpy.typing as npt
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap
from scipy.ndimage import binary_dilation

# 类型别名
# 点坐标
Coord: TypeAlias = tuple[int, int]
# 路径
Path = Annotated[npt.NDArray[np.int64], ("N", 2)]
# 网格
Grid = Annotated[npt.NDArray[np.int64], ("N", "M")]

MOVE_COST_STRAIGHT: float = 1.0
MOVE_COST_DIAGONAL: float = np.sqrt(2)


# 二维astar算法
def get_path_astar_2d(grid: Grid, start: Coord, end: Coord) -> Path:
    """
    一个优化版本的二维A*寻路算法。
    """
    rows, cols = grid.shape

    # 优化点 1: 修正启发函数为八角距离 (Octile Distance)
    def heuristic(coord_a: Coord, coord_b: Coord) -> float:
        dx = abs(coord_a[0] - coord_b[0])
        dy = abs(coord_a[1] - coord_b[1])
        # 这是八角距离的精确计算公式
        return MOVE_COST_STRAIGHT * (dx + dy) + (
            MOVE_COST_DIAGONAL - 2 * MOVE_COST_STRAIGHT
        ) * min(dx, dy)

    # 定义8个移动方向和对应的成本
    neighbors_moves = [
        ((0, 1), MOVE_COST_STRAIGHT),
        ((0, -1), MOVE_COST_STRAIGHT),
        ((1, 0), MOVE_COST_STRAIGHT),
        ((-1, 0), MOVE_COST_STRAIGHT),
        ((1, 1), MOVE_COST_DIAGONAL),
        ((-1, 1), MOVE_COST_DIAGONAL),
        ((-1, -1), MOVE_COST_DIAGONAL),
        ((1, -1), MOVE_COST_DIAGONAL),
    ]

    # 优先队列（小顶堆）
    open_set: list[tuple[float, Coord]] = [(heuristic(start, end), start)]

    # 优化点 2: 引入 closed_set，使用 set 以获得 O(1) 的查找效率
    closed_set: set[Coord] = set()

    # came_from 用于回溯路径
    came_from: dict[Coord, Coord] = {}

    # 优化点 3: 使用 defaultdict 避免低效的初始化
    g_score: dict[Coord, float] = defaultdict(lambda: float("inf"))
    g_score[start] = 0.0

    while open_set:
        _, current_node = heapq.heappop(open_set)

        # 如果节点已处理过，则跳过（这是对同一节点在open_set中存在多个副本的防御）
        if current_node in closed_set:
            continue

        # 将当前节点加入关闭列表，表示它已被访问和处理
        closed_set.add(current_node)

        if current_node == end:
            path: list[Coord] = []
            # 注意：这里的回溯逻辑需要确保终点能被加入路径
            temp = current_node
            while temp in came_from:
                path.append(temp)
                temp = came_from[temp]
            path.append(start)
            return np.array(path[::-1])

        # 优化点 1: 邻居循环使用预定义的移动和代价
        for (dr, dc), move_cost in neighbors_moves:
            neighbor: Coord = (current_node[0] + dr, current_node[1] + dc)

            # 检查邻居是否有效（界内、非障碍物）
            if not (
                0 <= neighbor[0] < rows
                and 0 <= neighbor[1] < cols
                and grid[neighbor[0]][neighbor[1]] == 0
            ):
                continue

            # 检查邻居是否已在关闭列表中
            if neighbor in closed_set:
                continue

            tentative_g_score = g_score[current_node] + move_cost

            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current_node
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor, end)

                # 这里可以进一步优化：仅当邻居不在 open_set 中时才添加。
                # 但简单的重复添加，依赖于前面的 closed_set 检查来处理，通常也足够快。
                heapq.heappush(open_set, (f_score, neighbor))

    return np.array([])  # 未找到路径


# 测试二维Astar算法
def get_astar_2d_result_grid(grid_map: Grid, start: Coord, end: Coord) -> Grid:

    path: Path = get_path_astar_2d(grid_map, start, end)

    # 赋初值
    path_grid: Grid = grid_map

    if path is not None and len(path) > 0:
        # 把路径在网格上标出来
        for r, c in path:
            path_grid[r][c] = 2  # Path
    else:
        print("\n未找到路径。")

    return np.array(path_grid)

# 可视化展示
def show_grid_high_clarity_overview():
    # 1. 加载.npz文件 (您的原始逻辑)
    # 为了让代码可以运行，我们先创建一个模拟文件
    try:
        data = np.load("../algo/obstacle_grid_6000x6000.npz")
        print("已成功加载文件。")
    except FileNotFoundError:
        print("未找到，正在创建模拟数据文件...")
        grid_size = 10000
        mock_grid = np.zeros((grid_size, grid_size), dtype=int)
        num_obstacles = int(grid_size * grid_size * 0.6)
        obstacle_rows = np.random.randint(0, grid_size, num_obstacles)
        obstacle_cols = np.random.randint(0, grid_size, num_obstacles)
        mock_grid[obstacle_rows, obstacle_cols] = 1  # 1 代表障碍物
        np.savez_compressed("obstacles.npz", grid=mock_grid)
        data = np.load("obstacles.npz")
        print("模拟数据文件已创建并加载。")

    # 2. 提取网格并运行A*算法
    origin_grid = data["grid"]
    print("正在执行Astar算法...")
    path_grid = get_astar_2d_result_grid(origin_grid, (5900, 0), (0, 1200))

    # --- 路径加粗处理开始 ---
    print("正在加粗路径...")

    # 2. 创建一个只包含路径的布尔掩码 (True代表是路径)
    path_mask = path_grid == 2

    # 3. 对路径掩码进行膨胀操作
    # 'iterations' 参数控制加粗的程度，值越大，路径越粗。可以从 2 或 3 开始尝试。
    dilated_path_mask = binary_dilation(path_mask, iterations=5)

    # 4. 将加粗后的路径应用回网格
    # 在原有的 path_grid 上，所有被膨胀区域覆盖的地方，都赋值为 2
    path_grid[dilated_path_mask] = 2

    print("路径加粗完成。")
    # --- 路径加粗处理结束 ---

    # --- 图像清晰化处理开始 ---

    # 3. 定义一个高对比度的颜色映射来区分不同区域
    # 0: 可通行区域 (白色)
    # 1: 障碍物 (黑色)
    # 2: 路径 (红色)
    colors = ["white", "black", "red"]
    cmap = ListedColormap(colors)
    # 创建一个归一化器，确保数值和颜色正确对应
    norm = plt.Normalize(vmin=0, vmax=2)

    # 4. 创建一个尺寸合适的图像画布
    # figsize 单位是英寸, 10x10英寸的画布可以容纳更多细节
    fig, ax = plt.subplots(figsize=(10, 10))

    # 5. 使用 imshow 显示网格
    # interpolation='none' 可以确保在放大时，单元格边缘保持清晰的方块状
    ax.imshow(path_grid, cmap=cmap, norm=norm, interpolation="none")

    # 6. 【核心改动】移除所有会造成混乱的细节元素
    # 不再绘制网格线和单元格文本，因为在3000x3000的尺度下它们只会变成一团乱麻
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Grid - High Clarity Overview", fontsize=16)

    plt.show()  # 用于快速预览
