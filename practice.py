import logging
import typing

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from matplotlib.colors import ListedColormap
from numpy.typing import NDArray

from birdkyle_exception.birdkyle_custom_exception import MyCustomException
from typing import Annotated # Python 3.9+
from collections import defaultdict
from scipy.ndimage import binary_dilation # <--- 导入膨胀函数


"""
个人练习 Python 语法

"""

# 打印非转义字符
def print_no_escape():
    print(r"打印一个非转义\n")

# 打印转义字符
def print_yes_escape():
    print("打印一个转义\n我换行啦")

# 字符串练习，练习截取子字符串
def print_str_1():
    my_str = "abcde"
    print(my_str[1:3])

# 字符串练习，练习截取子字符串
def print_str_2():
    my_str = "abcde"
    print(my_str[:3])

# 字符串练习，练习截取子字符串
def print_str_3():
    my_str = "abcde"
    print(my_str[-2:])

# 练习类型
def practice_type():
    # 变量定义
    x = 10  # 整数
    y = 3.14  # 浮点数
    name = "Alice"  # 字符串
    is_active = True  # 布尔值

    # 查看数据类型
    print(type(x))  # <class 'int'>
    print(type(y))  # <class 'float'>
    print(type(name))  # <class 'str'>
    print(type(is_active))  # <class 'bool'>

# 练习类型转换，隐式
def practice_trans_type_implicit():
    num_int = 123
    num_flo = 1.23

    num_new = num_int + num_flo

    print("num_int 数据类型为:", type(num_int))
    print("num_flo 数据类型为:", type(num_flo))

    print("num_new 值为:", num_new)
    print("num_new 数据类型为:", type(num_new))

# 练习类型转换，显式
def practice_trans_type_explicit():
    num_int = 100
    num_str = "200"

    print("类型转换前，num_str 数据类型为:", type(num_str))
    num_str = int(num_str)  # 强制转换为整型
    print("类型转换后，num_str 数据类型为:", type(num_str))

    num_sum = num_int + num_str

    print("num_int 与 num_str 相加结果为:", num_sum)
    print("sum 数据类型为:", type(num_sum))

# 练习除法取整数，往小了取
def practice_divide_1():
    print(5 // 2)
    print(-5 // 2)

# 练习除法，得出浮点数
def practice_divide_2():
    print(1 / 3)
    print(5 / 2)

# 练习集合
def practice_set():
    my_set = set()
    my_set.add(1)
    my_set.add("xbk")
    my_set.add("xbk")
    print(my_set)

# 练习字典
def practice_dict():
    my_dict = {"age": 25, "name": "kyle"}
    print(my_dict)

# 练习迭代器和生成器
def my_range(n):
    i = 0
    while i < n:
        yield i
        i += 1
def practice_yield_1():
    for num in my_range(10):
        print(num)
def practice_yield_2():
    my_iter = my_range(10)
    while True:
        try:
            print(next(my_iter))
        except StopIteration:
            break

# 斐波那契数列
def fibonacci_sequence(n):
    a = 0
    b = 1
    i = 0
    while True:
        if i == n:
            break
        yield a
        temp = b
        b = a + b
        a = temp
        i += 1
def print_fibonacci_sequence():
    for num in fibonacci_sequence(15):
        print(num)

# 练习面向对象
class MyClass:
    gender = 'female'
    def __init__(self, name, age):
        self.name = name
        self.age = age
    def __str__(self):
        return f'名字是:{self.name}\n年龄是:{self.age}'
def practice_class():
    my_class = MyClass('kyle', 18)
    my_class.name='bird'
    print(my_class)


# 练习类继承
class People:
    #定义基本属性
    name = ''
    age = 0
    #定义私有属性,私有属性在类外部无法直接进行访问
    __weight = 0
    #定义构造方法
    def __init__(self, name, age, weight):
        self.name = name
        self.age = age
        self.__weight = weight
    def speak(self):
        print(f"{self.name} 说: 我 {self.age} 岁。")
class Student(People):
    grade = ''
    def __init__(self, name, age, weight, grade):
        #调用父类的构造方法
        People.__init__(self, name, age, weight)
        self.grade = grade
    #覆写父类的方法
    def speak(self):
        print(f"{self.name} 说: 我 {self.age} 岁了，我在读 {self.grade} 年级")

# 练习打印日志
def practice_logging():
    # 创建记录器
    logger = logging.getLogger("practice_logging")
    logger.setLevel(logging.INFO)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 文件处理器
    file_handler = logging.FileHandler("practice_logging.log")
    file_handler.setLevel(logging.INFO)

    # 格式化
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # 这一条警告会输出到控制台以及文件
    logger.info("打印一条日志")
    logger.warning("警告")


# 练习异常处理
def example_exception_function(value):
    if value < 0:
        raise MyCustomException("输入值不能为负数！")
    elif value == 0:
        raise MyCustomException("输入值不能为零！请提供一个正数。")
    else:
        print(f"输入值为: {value}")
def practice_my_exception():
    try:
        example_exception_function(-5)
    except MyCustomException as e:
        print(f"捕获到自定义异常: {e}")
    except Exception as e:
        print(f"捕获到其他异常: {e}")

# 练习不定参数
def multi_params_function(name, *args, **kwargs):
    if name:
        print(f"名字是[{name}]")
    if args:
        print(f"args是[{args}]")
    if kwargs:
        print(f"kwargs是[{kwargs}]")
def practice_multi_params_function():
    set = {"apple", "banana", "cherry"}
    tuple = ("1", "2", "3")
    dict = {"age": 25, "gender": "male"}
    # multi_params_function("birdkyle", set)
    # multi_params_function("birdkyle", tuple)
    # multi_params_function("birdkyle", **dict)

    multi_params_function("n", x=1, y=2, z="3")

# 练习推导式
def practice_derivation():
    my_list1 = [x for x in range(10)]
    print(my_list1)

    my_list2 = [[x, x**2] for x in range(5) if x % 2 == 0]
    print(my_list2)

    my_set1 = {x for x in range(5) if x % 2 == 0}
    print(my_set1)


# 练习numpy处理一维度
def practice_numpy_one_dimension():

    one_dimension_list: list = [x for x in range(5)]
    one_dimension_array: typing.Annotated[npt.NDArray[np.float64], "1, 3"] = np.array(one_dimension_list)
    print(f"这是一个一维的数组\n{one_dimension_array}")

    bool_list = [True, False, True, False, True]
    print(f"根据布尔值列表快速筛选数组\n{one_dimension_array[bool_list]}")

    need_indices = [0,4]
    print(f"根据索引列表快速筛选数组\n{one_dimension_array[need_indices]}")

    even_numbers_indices = np.where(one_dimension_array % 2 == 0)[0]
    print(f"筛选出偶数的索引\n{even_numbers_indices}")


# 练习numpy处理二维
def practice_numpy_two_dimension():
    two_dimension_list = [[x, x, x] for x in range(5)]
    two_dimension_array = np.array(two_dimension_list)
    print(f"这是一个二维的数组\n{two_dimension_array}")

    bool_list = [True, False, True, False, True]
    print(f"根据布尔值列表快速筛选数组\n{two_dimension_array[bool_list]}")

    need_indices = [0,4]
    print(f"根据索引列表快速筛选数组\n{two_dimension_array[need_indices]}")

    even_numbers_indices = np.where(two_dimension_array[:,0] % 2 == 0)[0]
    print(f"筛选出偶数的索引\n{even_numbers_indices}")

# 练习numpy处理三维
def practice_numpy_three_dimension():
    grid_shape = (5, 5, 5)
    three_dimension_grid = np.ones(grid_shape, dtype=int)
    print(f"这是一个全是0的三维格子\n{three_dimension_grid}")




# 其他numpy的高级用法练习
def other_numpy_practice(one_dimension_array: NDArray[np.int64], two_dimension_array:NDArray[np.int64]):
    assert one_dimension_array.ndim == 1, "one_dimension_array 必须是一维"
    assert two_dimension_array.ndim == 2, "two_dimension_array 必须是二维"

    one_dimension_array = np.array([1,2,3,4,5])
    two_dimension_array = np.array([[1,2,3],[4,5,6]])


    # 1.广播机制
    after_broadcast_array = one_dimension_array + [2]
    print(f"广播后的\n{after_broadcast_array}")

    # 2.普通的数组相加
    origin_list = [1,2,3,4]
    after_plus_list = origin_list + [5]
    print(f"列表相加结果\n{after_plus_list}")

    # 3.创建一个数组，填充指定数字
    full_array = np.full((2,3), 5)
    print(f"full_array\n{full_array}")

    # 4.展平二维数组
    print(f"展平二维数组\n{full_array.flatten()}")

    # 6.转置二维数组
    print(f"转置二维数组\n{full_array.T}")

    # 沿着指定轴连接数组
    a = np.array([[1, 2, 3], [4, 5, 6]])
    b = np.array([[7, 8, 9], [10, 11, 12]])
    print(f"垂直连接\n {np.concatenate((a, b), axis=0)}")  # 垂直连接
    print(f"水平连接\n {np.concatenate((a, b), axis=1)}")  # 水平连接

    # 垂直连接就是把两个数组竖着一摞堆起来（要求列数必须一样）
    # 水平连接就是把两个数组横着焊接连起来（要求行数必须一样）
    print(f"垂直连接\n {np.vstack((a, b))}")  # 垂直连接
    print(f"水平连接\n {np.hstack((a, b))}")  # 水平连接


    e_arr = np.full((2,2,2), 5)
    e_arr[0][:][:] = 0
    print(f"<e_arr>\n{e_arr}")

    pass


# 二维astar算法
import heapq
from typing import TypeAlias

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
        return MOVE_COST_STRAIGHT * (dx + dy) + (MOVE_COST_DIAGONAL - 2 * MOVE_COST_STRAIGHT) * min(dx, dy)

    # 定义8个移动方向和对应的成本
    neighbors_moves = [
        ((0, 1), MOVE_COST_STRAIGHT), ((0, -1), MOVE_COST_STRAIGHT),
        ((1, 0), MOVE_COST_STRAIGHT), ((-1, 0), MOVE_COST_STRAIGHT),
        ((1, 1), MOVE_COST_DIAGONAL), ((-1, 1), MOVE_COST_DIAGONAL),
        ((-1, -1), MOVE_COST_DIAGONAL), ((1, -1), MOVE_COST_DIAGONAL)
    ]

    # 优先队列（小顶堆）
    open_set: list[tuple[float, Coord]] = [(heuristic(start, end), start)]

    # 优化点 2: 引入 closed_set，使用 set 以获得 O(1) 的查找效率
    closed_set: set[Coord] = set()

    # came_from 用于回溯路径
    came_from: dict[Coord, Coord] = {}

    # 优化点 3: 使用 defaultdict 避免低效的初始化
    g_score: dict[Coord, float] = defaultdict(lambda: float('inf'))
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
            if not (0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols and grid[neighbor[0]][neighbor[1]] == 0):
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


def show_grid_high_clarity_overview():
    # 1. 加载.npz文件 (您的原始逻辑)
    # 为了让代码可以运行，我们先创建一个模拟文件
    try:
        data = np.load('obstacles11.npz')
        print("已成功加载文件。")
    except FileNotFoundError:
        print("未找到，正在创建模拟数据文件...")
        grid_size = 10000
        mock_grid = np.zeros((grid_size, grid_size), dtype=int)
        num_obstacles = int(grid_size * grid_size * 0.6)
        obstacle_rows = np.random.randint(0, grid_size, num_obstacles)
        obstacle_cols = np.random.randint(0, grid_size, num_obstacles)
        mock_grid[obstacle_rows, obstacle_cols] = 1  # 1 代表障碍物
        np.savez_compressed('obstacles.npz', grid=mock_grid)
        data = np.load('obstacles.npz')
        print("模拟数据文件已创建并加载。")

    # 2. 提取网格并运行A*算法
    origin_grid = data['grid']
    print('正在执行Astar算法...')
    path_grid = get_astar_2d_result_grid(origin_grid, (9999, 5), (1500, 9999))

    # --- 路径加粗处理开始 ---
    print("正在加粗路径...")

    # 2. 创建一个只包含路径的布尔掩码 (True代表是路径)
    path_mask = (path_grid == 2)

    # 3. 对路径掩码进行膨胀操作
    # 'iterations' 参数控制加粗的程度，值越大，路径越粗。可以从 2 或 3 开始尝试。
    dilated_path_mask = binary_dilation(path_mask, iterations=6)

    # 4. 将加粗后的路径应用回网格
    # 在原有的 path_grid 上，所有被膨胀区域覆盖的地方，都赋值为 2
    path_grid[dilated_path_mask] = 2

    print("路径加粗完成。")
    # --- 路径加粗处理结束 ---



    # --- 图像清晰化处理开始 ---

    # 3. 定义一个高对比度的颜色映射来区分不同区域
    # 0: 可通行区域 (白色)
    # 1: 障碍物 (黑色)
    # 2: 路径 (红色) - 这是根据您之前代码逻辑推断的
    colors = ['white', 'black', 'red']
    cmap = ListedColormap(colors)
    # 创建一个归一化器，确保数值和颜色正确对应
    norm = plt.Normalize(vmin=0, vmax=2)

    # 4. 创建一个尺寸合适的图像画布
    # figsize 单位是英寸, 10x10英寸的画布可以容纳更多细节
    fig, ax = plt.subplots(figsize=(10, 10))

    # 5. 使用 imshow 显示网格
    # interpolation='none' 可以确保在放大时，单元格边缘保持清晰的方块状
    ax.imshow(path_grid, cmap=cmap, norm=norm, interpolation='none')

    # 6. 【核心改动】移除所有会造成混乱的细节元素
    # 不再绘制网格线和单元格文本，因为在3000x3000的尺度下它们只会变成一团乱麻
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("3000x3000 Grid - High Clarity Overview", fontsize=16)

    plt.show() # 用于快速预览



if __name__ == '__main__':
    show_grid_high_clarity_overview()
    pass


