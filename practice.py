import logging
from birdkyle_asyncio import birdkyle_asyncio_demo
from birdkyle_exception.birdkyle_custom_exception import MyCustomException
import numpy as np

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
    one_dimension_list = [x for x in range(5)]
    one_dimension_array = np.array(one_dimension_list)
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


def practice_numpy_three_dimension():
    grid_shape = (5, 5, 5)
    three_dimension_grid = np.zeros(grid_shape, dtype=int)
    print(f"这是一个全是0的三维格子\n{three_dimension_grid}")


    pass


if __name__ == '__main__':
    practice_numpy_three_dimension()
    pass


