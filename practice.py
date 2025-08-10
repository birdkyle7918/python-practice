import logging
from birdkyle_asyncio import birdkyle_asyncio_demo
from birdkyle_exception.birdkyle_custom_exception import MyCustomException
import numpy as np
import numpy.typing as npt
import typing
from typing import Annotated, AnyStr, Any
from numpy.typing import NDArray

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

# 为坐标创建一个类型别名，增强代码可读性
Coord: TypeAlias = tuple[int, int]
Grid: TypeAlias = list[list[int]]

# 二维astar算法
def astar_2d(grid: Grid, start: Coord, end: Coord) -> list[Coord]:
    """
    使用 A* 算法在二维网格中寻找最短路径。

    :param grid: 一个二维列表，0 代表可通行，1 代表障碍物。
    :param start: 起点坐标 (row, col)。
    :param end: 终点坐标 (row, col)。
    :return: 一个包含路径坐标的列表，若无路径则返回空列表。
    """
    rows: int = len(grid)
    cols: int = len(grid[0])

    # 定义启发函数：曼哈顿距离
    def heuristic(coord_a: Coord, coord_b: Coord) -> int:
        return abs(coord_a[0] - coord_b[0]) + abs(coord_a[1] - coord_b[1])

    # 优先队列（小顶堆），存储 (f_score, node)
    # f_score 是 g_score + h_score
    open_set: list[tuple[float, Coord]] = [(float(heuristic(start, end)), start)]

    # came_from 字典用于回溯路径，key 为节点，value 为其前驱节点
    came_from: dict[Coord, Coord] = {}

    # g_score 存储从起点到各节点的实际代价
    # 使用字典并设置默认值为无穷大
    g_score: dict[Coord, float] = {(r, c): float('inf') for r in range(rows) for c in range(cols)}
    g_score[start] = 0.0

    while open_set:

        # 每次都是从优先队列中弹出 f_score 最小的节点
        _, current_node = heapq.heappop(open_set)

        # 如果到达终点，则重建路径并返回（这个好理解）
        if current_node == end:
            path: list[Coord] = []
            while current_node in came_from:
                path.append(current_node)
                current_node = came_from[current_node]
            path.append(start)
            return path[::-1]  # 翻转列表得到从起点到终点的路径

        # 循环，分别探索当前节点的邻居（上、下、左、右）
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            # 邻居节点的坐标
            neighbor: Coord = (current_node[0] + dr, current_node[1] + dc)

            # 如果邻居超出网格，或者邻居是障碍物，则continue，探索下一个邻居
            if not (0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols and grid[neighbor[0]][neighbor[1]] == 0):
                continue

            # 计算经由当前节点到达邻居节点的 g_score
            # 此处每一步的代价为 1.0
            tentative_g_score: float = g_score[current_node] + 1.0

            # 如果这条新路径不是更优，则不管
            if tentative_g_score > g_score[neighbor]:
                continue

            # 更新邻居节点的来源节点
            came_from[neighbor] = current_node

            # 更新邻居节点的已知代价
            g_score[neighbor] = tentative_g_score

            # 更新邻居节点的总代价
            f_score: float = tentative_g_score + heuristic(neighbor, end)

            # 放入总代价队列
            heapq.heappush(open_set, (f_score, neighbor))


    # 如果 open_set 为空仍未找到终点，则说明没有路径
    return []

# 测试二维Astar算法
def test_astar_2d():
    # 定义一个 5x5 的网格
    # 0 = 可走, 1 = 障碍
    grid_map: Grid = [
        [0, 0, 0, 1, 0],
        [1, 1, 0, 1, 0],
        [0, 0, 0, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0]
    ]

    start_point: Coord = (0, 0)
    end_point: Coord = (4, 4)

    print(f"网格地图 (1代表障碍):")
    for row in grid_map:
        print(row)
    print(f"\n起点: {start_point}")
    print(f"终点: {end_point}")

    path: list[Coord] = astar_2d(grid_map, start_point, end_point)

    if path:
        print("\n找到路径:")
        print(path)

        # 可视化路径
        # 注意：path_grid 的类型是 int 和 str 的联合
        path_grid: list[list[int | str]] = [row[:] for row in grid_map]
        for r, c in path:
            if (r, c) == start_point:
                path_grid[r][c] = 'S'  # Start
            elif (r, c) == end_point:
                path_grid[r][c] = 'E'  # End
            else:
                path_grid[r][c] = '*'  # Path

        print("\n路径可视化 (S=起点, E=终点, *=路径):")
        for visual_row in path_grid:
            print(" ".join([str(item) for item in visual_row]))

    else:
        print("\n未找到路径。")





if __name__ == '__main__':
    test_astar_2d()
    pass


