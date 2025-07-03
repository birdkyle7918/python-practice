import asyncio
import logging
import random
import time
from typing import Dict

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
    my_dict = {"age": 25, "name": "bird"}
    my_dict["name"] = "kyle"
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
    a = 1
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
    for num in fibonacci_sequence(10):
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


# 练习继承
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
class MyCustomException(Exception):
    def __init__(self, message="这是一个自定义的错误信息"):
        self.message = message
        super().__init__(self.message)  # 调用父类的构造函数

    def __str__(self):
        """
        当异常被打印或转换为字符串时返回的信息。
        """
        return f"MyCustomException: {self.message}"

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
    multi_params_function("birdkyle", set)
    multi_params_function("birdkyle", tuple)
    multi_params_function("birdkyle", **dict)


# 练习并发协程
async def call_network(task_id):
    """
    一个模拟异步操作的函数，这里简单地等待一段时间并返回一个结果。
    """
    print(f"任务 {task_id}: 开始...")
    if task_id == "c":
        raise MyCustomException("自定义异常")

    # 模拟调用下游的网络延迟
    delay = random.uniform(1.0, 2.0)
    await asyncio.wait_for(asyncio.sleep(delay), 1.8)

    print(f"任务{task_id}完成，耗时{delay:.2f}")
    return f"任务{task_id}结果"


async def parallel_call_network() -> Dict:
    num_list = ["a", "b", "c", "d", "e"]

    # 创建一个空的列表来存储 task 对象
    task_map = dict()

    # 在循环中创建并启动多个 func 任务
    for num in num_list:
        # asyncio.ensure_future() 或 asyncio.create_task() 都可以将一个协程包装为一个 Task (它是一个 Future 的子类)
        # 这里使用 asyncio.create_task 是更现代和推荐的做法
        task = asyncio.create_task(call_network(num))
        task_map[num] = task

    print("\n【所有任务启动完成，正在执行中】")

    # 拿出所有的任务
    task_list = task_map.values()

    # 使用 asyncio.gather 等待所有 task 完成，并收集它们的结果
    # asyncio.gather 方法的参数要么是协程，要么是 task
    # 加上了 return_exceptions=True
    await asyncio.gather(*task_list, return_exceptions=True)

    return task_map

def practice_async():
    start = time.time()
    # 调用主逻辑
    task_map_result = asyncio.run(parallel_call_network())
    end = time.time()
    print(f"\n总耗时:{(end - start):.2f}")

    # 拿出 map 中的结果
    print("\n【所有任务完成，下面展示任务结果】")
    for num, task in task_map_result.items():
        # 获取任务的异常（如果有的话）
        ex = task.exception()
        if ex:
            if isinstance(ex, MyCustomException):
                print(f"任务{num}出现MyCustomException异常:{ex}")
            elif isinstance(ex, asyncio.TimeoutError):
                print(f"任务{num}出现TimeoutError异常:{ex}")
            else:
                print(f"任务{num}出现未知异常:{ex}")
        else:
            print(f"任务{num}的结果是：{task.result()}")


if __name__ == '__main__':
    practice_async()


