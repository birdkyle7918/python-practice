import json
import re
from datetime import datetime, timedelta

import requests


class ChineseTimeParser:
    def __init__(self):
        """
        中文时间解析器
        支持多种时间表达方式的解析
        """
        # 时间关键词映射
        self.time_keywords = {
            # 相对时间
            "今天": 0,
            "明天": 1,
            "后天": 2,
            "昨天": -1,
            "前天": -2,
            "今日": 0,
            "明日": 1,
            # 星期
            "这周": 0,
            "下周": 7,
            "上周": -7,
            "周一": 1,
            "周二": 2,
            "周三": 3,
            "周四": 4,
            "周五": 5,
            "周六": 6,
            "周日": 0,
            "星期一": 1,
            "星期二": 2,
            "星期三": 3,
            "星期四": 4,
            "星期五": 5,
            "星期六": 6,
            "星期日": 0,
            "礼拜一": 1,
            "礼拜二": 2,
            "礼拜三": 3,
            "礼拜四": 4,
            "礼拜五": 5,
            "礼拜六": 6,
            "礼拜日": 0,
            # 时间段
            "早上": 8,
            "上午": 10,
            "中午": 12,
            "下午": 14,
            "晚上": 19,
            "夜里": 22,
            "深夜": 23,
            "凌晨": 2,
            "清晨": 6,
            "傍晚": 18,
            "午夜": 0,
            # 数字映射
            "一": 1,
            "二": 2,
            "三": 3,
            "四": 4,
            "五": 5,
            "六": 6,
            "七": 7,
            "八": 8,
            "九": 9,
            "十": 10,
            "十一": 11,
            "十二": 12,
            "零": 0,
        }

        # 百度API配置（需要申请）
        self.baidu_api_key = "YOUR_BAIDU_API_KEY"
        self.baidu_secret_key = "YOUR_BAIDU_SECRET_KEY"
        self.access_token = None

    def get_baidu_access_token(self):
        """获取百度API访问令牌"""
        if self.access_token:
            return self.access_token

        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.baidu_api_key,
            "client_secret": self.baidu_secret_key,
        }

        try:
            response = requests.post(url, params=params)
            result = response.json()
            self.access_token = result.get("access_token")
            return self.access_token
        except Exception as e:
            print(f"获取百度API令牌失败: {e}")
            return None

    def parse_with_baidu_api(self, text):
        """使用百度NLP API解析时间"""
        access_token = self.get_baidu_access_token()
        if not access_token:
            return None

        url = (
            f"https://aip.baidubce.com/rpc/2.0/nlp/v1/lexer?access_token={access_token}"
        )

        headers = {"Content-Type": "application/json", "charset": "UTF-8"}

        data = {"text": text}

        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            result = response.json()

            # 解析API返回的时间信息
            if "items" in result:
                for item in result["items"]:
                    if item.get("pos") == "TIME":
                        return self.normalize_time_from_api(item.get("item", ""))

        except Exception as e:
            print(f"百度API调用失败: {e}")

        return None

    def parse_local(self, text):
        """本地解析时间表达式"""
        now = datetime.now()
        result_time = now

        # 提取日期信息
        date_info = self.extract_date_info(text, now)
        if date_info:
            result_time = date_info

        # 提取时间信息
        time_info = self.extract_time_info(text)
        if time_info:
            result_time = result_time.replace(
                hour=time_info.get("hour", result_time.hour),
                minute=time_info.get("minute", result_time.minute),
                second=0,
                microsecond=0,
            )

        return result_time

    def extract_date_info(self, text, base_time):
        """提取日期信息"""
        # 处理相对日期
        for keyword, offset in self.time_keywords.items():
            if keyword in text and keyword in [
                "今天",
                "明天",
                "后天",
                "昨天",
                "前天",
                "今日",
                "明日",
            ]:
                return base_time + timedelta(days=offset)

        # 处理星期
        for keyword, weekday in self.time_keywords.items():
            if (
                keyword in text
                and "周" in keyword
                or "星期" in keyword
                or "礼拜" in keyword
            ):
                days_until = (weekday - base_time.weekday()) % 7
                if days_until == 0 and "下" in text:
                    days_until = 7
                return base_time + timedelta(days=days_until)

        # 处理具体日期（如：8月10日）
        date_pattern = r"(\d{1,2})月(\d{1,2})日?"
        match = re.search(date_pattern, text)
        if match:
            month, day = int(match.group(1)), int(match.group(2))
            try:
                result = base_time.replace(month=month, day=day)
                # 如果日期已过，则为明年
                if result < base_time:
                    result = result.replace(year=base_time.year + 1)
                return result
            except ValueError:
                pass

        return None

    def extract_time_info(self, text):
        """提取时间信息"""
        time_info = {}

        # 处理标准时间格式（如：9点30分、21:30）
        time_patterns = [
            r"(\d{1,2})[：:](\d{2})",  # 21:30 或 21：30
            r"(\d{1,2})点(\d{1,2})分?",  # 9点30分
            r"(\d{1,2})点(?!.*分)",  # 9点（没有分钟）
        ]

        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                hour = int(match.group(1))
                minute = (
                    int(match.group(2))
                    if len(match.groups()) > 1 and match.group(2)
                    else 0
                )

                # 处理12小时制
                if hour <= 12 and ("下午" in text or "晚上" in text or "夜里" in text):
                    if hour != 12:
                        hour += 12
                elif hour == 12 and ("上午" in text or "早上" in text):
                    hour = 0

                time_info["hour"] = hour
                time_info["minute"] = minute
                return time_info

        # 处理时间段关键词
        for keyword, default_hour in self.time_keywords.items():
            if keyword in text and keyword in [
                "早上",
                "上午",
                "中午",
                "下午",
                "晚上",
                "夜里",
                "深夜",
                "凌晨",
                "清晨",
                "傍晚",
                "午夜",
            ]:
                time_info["hour"] = default_hour
                time_info["minute"] = 0
                return time_info

        # 处理中文数字
        chinese_num_pattern = r"([一二三四五六七八九十]+)点"
        match = re.search(chinese_num_pattern, text)
        if match:
            chinese_hour = match.group(1)
            hour = self.chinese_to_number(chinese_hour)
            if hour is not None:
                # 处理下午/晚上的时间
                if hour <= 12 and ("下午" in text or "晚上" in text):
                    if hour != 12:
                        hour += 12
                time_info["hour"] = hour
                time_info["minute"] = 0
                return time_info

        return time_info if time_info else None

    def chinese_to_number(self, chinese_str):
        """将中文数字转换为阿拉伯数字"""
        if chinese_str in self.time_keywords:
            return self.time_keywords[chinese_str]

        # 处理复合中文数字（如：十一、十二等）
        if "十" in chinese_str:
            if chinese_str == "十":
                return 10
            elif chinese_str.startswith("十"):
                return 10 + self.time_keywords.get(chinese_str[1:], 0)
            elif chinese_str.endswith("十"):
                return self.time_keywords.get(chinese_str[0], 0) * 10

        return None

    def normalize_time_from_api(self, api_time_str):
        """标准化API返回的时间字符串"""
        # 这里需要根据具体API返回格式进行处理
        # 百度API返回的时间格式可能需要进一步解析
        return datetime.now()  # 占位符

    def parse_time(self, text, use_api=True):
        """
        解析中文时间表达式

        Args:
            text (str): 中文时间表达式
            use_api (bool): 是否优先使用API

        Returns:
            str: 标准时间戳格式 "YYYY-MM-DD HH:MM:SS"
        """
        # 预处理文本
        text = text.strip().replace(" ", "")

        # 优先使用API解析
        if use_api:
            api_result = self.parse_with_baidu_api(text)
            if api_result:
                return api_result.strftime("%Y-%m-%d %H:%M:%S")

        # 使用本地解析作为备选
        local_result = self.parse_local(text)
        return local_result.strftime("%Y-%m-%d %H:%M:%S")


# 不使用API的简化版本（推荐用于快速测试）
class SimpleChineseTimeParser:
    def __init__(self):
        self.time_keywords = {
            "今天": 0,
            "明天": 1,
            "后天": 2,
            "昨天": -1,
            "前天": -2,
            "早上": 8,
            "上午": 10,
            "中午": 12,
            "下午": 14,
            "晚上": 19,
            "夜里": 22,
            "凌晨": 2,
            "傍晚": 18,
            "午夜": 0,
            "一": 1,
            "二": 2,
            "三": 3,
            "四": 4,
            "五": 5,
            "六": 6,
            "七": 7,
            "八": 8,
            "九": 9,
            "十": 10,
            "十一": 11,
            "十二": 12,
        }

    def parse_time(self, text):
        """解析中文时间表达式"""
        now = datetime.now()
        result_time = now

        # 处理日期
        for keyword, offset in self.time_keywords.items():
            if keyword in text and keyword in ["今天", "明天", "后天", "昨天", "前天"]:
                result_time = now + timedelta(days=offset)
                break

        # 处理具体时间
        # 匹配 "X点Y分" 或 "X点" 格式
        time_pattern = r"(\d{1,2}|[一二三四五六七八九十]+)点(\d{1,2}分?)?"
        match = re.search(time_pattern, text)

        if match:
            hour_str = match.group(1)
            minute_str = match.group(2)

            # 转换小时
            if hour_str.isdigit():
                hour = int(hour_str)
            else:
                hour = self.chinese_to_number(hour_str)

            # 转换分钟
            minute = 0
            if minute_str:
                minute_num = re.search(r"\d+", minute_str)
                if minute_num:
                    minute = int(minute_num.group())

            # 处理12小时制
            if hour <= 12:
                if "下午" in text or "晚上" in text or "夜里" in text:
                    if hour != 12:
                        hour += 12
                elif hour == 12 and ("上午" in text or "早上" in text):
                    hour = 0

            result_time = result_time.replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )

        # 处理时间段关键词
        else:
            for keyword, default_hour in self.time_keywords.items():
                if keyword in text and keyword in [
                    "早上",
                    "上午",
                    "中午",
                    "下午",
                    "晚上",
                    "夜里",
                    "凌晨",
                    "傍晚",
                    "午夜",
                ]:
                    result_time = result_time.replace(
                        hour=default_hour, minute=0, second=0, microsecond=0
                    )
                    break

        return result_time.strftime("%Y-%m-%d %H:%M:%S")

    def chinese_to_number(self, chinese_str):
        """转换中文数字"""
        if chinese_str in self.time_keywords:
            return self.time_keywords[chinese_str]

        # 处理十几的情况
        if "十" in chinese_str:
            if chinese_str == "十":
                return 10
            elif chinese_str.startswith("十"):
                return 10 + self.time_keywords.get(chinese_str[1:], 0)
            elif len(chinese_str) == 2 and chinese_str[1] == "十":
                return self.time_keywords.get(chinese_str[0], 0) * 10

        return int(chinese_str) if chinese_str.isdigit() else 0


# 示例使用代码
def demo_usage():
    """演示如何使用时间解析器"""

    # 使用简化版本（推荐）
    parser = SimpleChineseTimeParser()

    test_cases = ["晚上23点"]

    print("=== 中文时间解析演示 ===")
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    for text in test_cases:
        result = parser.parse_time(text)
        print(f"输入: {text:<15} -> 输出: {result}")


# 增强版本，支持更复杂的时间表达
class AdvancedChineseTimeParser(SimpleChineseTimeParser):
    def __init__(self):
        super().__init__()
        # 扩展更多时间表达
        self.relative_time_patterns = {
            r"(\d+)个?小时[后之]后": lambda x: datetime.now() + timedelta(hours=int(x)),
            r"(\d+)分钟[后之]后": lambda x: datetime.now() + timedelta(minutes=int(x)),
            r"(\d+)天[后之]后": lambda x: datetime.now() + timedelta(days=int(x)),
            r"半小时[后之]后": lambda x: datetime.now() + timedelta(minutes=30),
            r"一刻钟[后之]后": lambda x: datetime.now() + timedelta(minutes=15),
        }

    def parse_time(self, text):
        """增强版时间解析"""
        # 首先尝试相对时间模式
        for pattern, func in self.relative_time_patterns.items():
            match = re.search(pattern, text)
            if match:
                if match.groups():
                    result = func(match.group(1))
                else:
                    result = func(None)
                return result.strftime("%Y-%m-%d %H:%M:%S")

        # 处理"半"的情况
        if "半" in text:
            text = text.replace("半", "30分")

        # 回退到基础解析
        return super().parse_time(text)


if __name__ == "__main__":
    # 运行演示
    demo_usage()
