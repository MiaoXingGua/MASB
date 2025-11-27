from maa.custom_action import CustomAction

from typing import Dict, Any
import os
import json
import re


# 解析查询字符串
def parse_query_args(argv: CustomAction.RunArg) -> dict[str, Any]:
    if not argv.custom_action_param:
        return {}

    # 预处理参数：去除首尾引号并按'&'分割参数列表
    args: list[str] = argv.custom_action_param.strip("\"'").split("&")

    # 解析键值对到字典
    params: Dict[str, Any] = {}
    for arg in args:
        # 分割键值
        parts = arg.split("=")
        if len(parts) >= 2:
            params[parts[0]] = parts[1]

    return params


# 解析列表输入
def parse_list_input(input: str) -> list[str]:
    if not input:
        return []

    list_split_regex = r",\s*|，\s*|、\s*|\s+"

    items = re.split(list_split_regex, input)
    items = [item for item in items if item]

    return items


# 提示
class Prompt:
    @staticmethod
    def error(str: str, e: Exception = None):
        print(f"{str}失败，请立即停止运行程序！")
        if e is not None:
            print(e)
        return CustomAction.RunResult(success=False)


# 本地存储
class LocalStorage:
    # 存储文件路径
    agent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_dir = os.path.join(agent_dir, "..", "config")
    storage_path = os.path.join(config_dir, "mnma_storage.json")

    # 检查并确保存储文件存在
    @classmethod
    def ensure_storage_file(cls):
        # 确保配置目录存在
        if not os.path.exists(cls.config_dir):
            os.makedirs(cls.config_dir)

        # 确保存储文件存在
        if not os.path.exists(cls.storage_path):
            with open(cls.storage_path, "w") as f:
                json.dump({}, f)

    # 读取存储数据
    @classmethod
    def read(cls) -> dict:
        cls.ensure_storage_file()
        try:
            with open(cls.storage_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # 存储文件格式错误时重置为空对象
            with open(cls.storage_path, "w") as f:
                json.dump({}, f)
            return {}

    # 获取存储值
    @classmethod
    def get(cls, task: str, key: str) -> str | bool | int | None:
        storage = cls.read()
        task_storage = storage.get(task)
        if task_storage is None:
            return None
        return task_storage.get(key)

    # 写入存储数据到文件
    @classmethod
    def write(cls, storage: dict) -> bool:
        try:
            with open(cls.storage_path, "w") as f:
                json.dump(storage, f)
            return True
        except Exception as e:
            print(f"存储数据时出错: {e}")
            return False

    # 设置存储值
    @classmethod
    def set(cls, task: str, key: str, value: str | bool | int) -> bool:
        storage = cls.read()
        if task not in storage:
            storage[task] = {}
        storage[task][key] = value

        return cls.write(storage)
