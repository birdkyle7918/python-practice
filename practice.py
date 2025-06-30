import logging
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


if __name__ == '__main__':
    practice_logging()


