from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

from .utils import parse_query_args, Prompt


class Counter:
    def __init__(self, max_count: int = 0, exceed: bool = True):
        self.count = 0
        self.max = max_count
        self.exceed = exceed

    def init(self, max_count: int = 0, exceed: bool = True):
        self.count = 0
        self.max = max_count
        self.exceed = exceed

    def increment(self):
        self.count += 1
        return self.count

    def is_max(self):
        if self.max <= 0:
            return False
        if self.exceed:
            return self.count > self.max
        else:
            return self.count >= self.max

    def get_count(self):
        return self.count

    def set_max(self, max_count: int, exceed: bool = True):
        self.max = max_count
        self.exceed = exceed


class CounterManager:
    def __init__(self):
        self.counters = {}

    def get(self, key: str) -> Counter:
        if key not in self.counters:
            self.counters[key] = Counter()
        return self.counters[key]

    def remove(self, key: str):
        if key in self.counters:
            del self.counters[key]

    def reset(self, key: str, max_count: int = 0, exceed: bool = True):
        self.counters[key] = Counter(max_count, exceed)


counter_manager = CounterManager()


@AgentServer.custom_action("init_counter")
class InitCounter(CustomAction):
    def run(
        self, context: Context, argv: CustomAction.RunArg
    ) -> CustomAction.RunResult | bool:
        try:
            print("InitCounter")
            args = parse_query_args(argv)
            key = args.get("key", "default")
            maxCount = args.get("max")
            exceed = args.get("exceed")
            maxCount = int(maxCount) if maxCount is not None else 0
            exceed = str(exceed).lower() != "false" if exceed is not None else True
            counter_manager.reset(key, maxCount, exceed)
            counter = counter_manager.get(key)
            print(f"初始化计数: {counter.get_count()}")
            return CustomAction.RunResult(success=True)
        except Exception as e:
            return Prompt.error("初始化计数", e)


@AgentServer.custom_action("count")
class Count(CustomAction):
    def run(
        self, context: Context, argv: CustomAction.RunArg
    ) -> CustomAction.RunResult | bool:
        print("Count")
        try:
            args = parse_query_args(argv)
            key = args.get("key", "default")
            text = args.get("t", "")
            counter = counter_manager.get(key)
            counter.increment()
            if text:
                print(f"> 第{counter.get_count()}次{text}")
            if counter.is_max():
                return CustomAction.RunResult(success=False)
            return CustomAction.RunResult(success=True)
        except Exception as e:
            return Prompt.error("计数", e)


# Counter.py（只改这部分）
from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
from .utils import parse_query_args, Prompt

# 全局计数器管理器（内存单例）
counter_manager = CounterManager()


@AgentServer.custom_action("init_counters")
class InitCounters(CustomAction):
    def run(self, context: Context, argv: CustomAction.RunArg):
        print("批量初始化计数器 (原生数组模式)")
        try:
            # 直接接收 list！
            items = argv.custom_action_param
            if not isinstance(items, list):
                return Prompt.error("counters 必须是数组")

            results = []
            for item in items:
                if not isinstance(item, dict):
                    print(f"  跳过无效项: {item}")
                    continue

                key = item.get("key")
                if not key:
                    continue

                max_val = int(item.get("max", 0))
                exceed = item.get("exceed", True) in (True, "true", "True")

                # 复用 InitCounter 逻辑
                fake_argv = CustomAction.RunArg(
                    custom_action="init_counter",
                    custom_action_param=f"key={key}&max={max_val}&exceed={exceed}",
                )
                result = InitCounter.run(self, context, fake_argv)
                success = result.success if hasattr(result, "success") else bool(result)
                results.append(success)

                print(
                    f"  → 初始化 {key}: max={max_val}, exceed={exceed} -> {'OK' if success else 'Failed'}"
                )

            return CustomAction.RunResult(success=all(results))

        except Exception as e:
            return Prompt.error("批量初始化失败", e)
