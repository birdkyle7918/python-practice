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
