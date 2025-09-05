import asyncio
import random
import time
from typing import Dict
from src.birdkyle_exception.birdkyle_custom_exception import MyCustomException


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
    await asyncio.wait_for(asyncio.sleep(delay), 1.9)

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


if __name__ == "__main__":
    practice_async()
