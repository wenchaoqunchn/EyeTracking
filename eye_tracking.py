import clr  # 导入 CLR（Common Language Runtime），用于与 .NET 交互
from time import time, sleep  # 导入时间处理函数
from multiprocessing import Process, Value, Lock  # 导入多进程相关的模块

# 添加 Tobii SDK 依赖
clr.AddReference("./dlls/tobii_interaction_lib_cs")  # 引用 Tobii 交互库
import Tobii.InteractionLib as tobii  # type: ignore # 导入 Tobii 交互库，type: ignore 表示忽略类型检查


class EyeTracker:
    def __init__(self, save_path, resolution):
        self.process = None  # 初始化进程变量
        self.running = Value(
            "b", False
        )  # 使用 multiprocessing.Value 共享状态，初始化为 False
        self.lock = Lock()  # 创建锁以确保文件访问的线程安全
        self.width, self.height = resolution  # 获取显示分辨率
        self.rounding = 2  # 设置坐标四舍五入精度
        self.save_path = save_path  # 设置数据保存路径

    def event_handler(self, event: tobii.GazePointData):
        # 处理眼动数据事件
        x = round(event.x, self.rounding)  # 四舍五入 x 坐标
        y = round(event.y, self.rounding)  # 四舍五入 y 坐标
        is_valid = event.validity == tobii.Validity.Valid  # 检查数据有效性
        if is_valid and x > 0 and y > 0:  # 仅处理有效且在有效范围内的坐标
            t = round(time() * 1000, self.rounding)  # 获取当前时间戳（毫秒）
            data = "{},{},{}\n".format(t, x, y)  # 格式化数据字符串
            with self.lock:  # 确保文件写入线程安全
                with open(self.save_path, "a+") as f:  # 以追加模式打开文件
                    f.write(data)  # 写入数据
                    print("{},{},{}\n".format(t, x, y))  # 打印数据到控制台

    def start_process(self):
        # 启动眼动追踪进程
        if not self.running.value:  # 检查眼动追踪是否已经在运行
            self.running.value = True  # 设置状态为运行
            self.process = Process(target=self.track)  # 创建新的进程以执行 track 方法
            self.process.start()  # 启动进程
            print("Eye tracking started.")  # 打印启动信息

    def track(self):
        # 眼动追踪的实际过程
        lib = tobii.InteractionLibFactory.CreateInteractionLib(
            tobii.FieldOfUse.Interactive
        )  # 创建交互库实例
        lib.CoordinateTransformAddOrUpdateDisplayArea(
            self.width, self.height
        )  # 设置显示区域
        lib.CoordinateTransformSetOriginOffset(0, 0)  # 设置坐标原点偏移
        lib.GazePointDataEvent += lambda event: self.event_handler(
            event
        )  # 绑定事件处理器

        while self.running.value:  # 当状态为运行时，持续监控眼动数据
            lib.WaitAndUpdate()  # 等待并更新数据

    def stop_process(self):
        # 停止眼动追踪进程
        if self.running and self.process is not None:  # 检查眼动追踪是否在运行
            self.running.value = False  # 设置状态为不运行
            self.process.join()  # 等待进程结束
            print("Eye tracking stopped.")  # 打印停止信息

    def is_running(self):
        return self.running.value


if __name__ == "__main__":
    # 测试代码
    eye_tracker = EyeTracker("test_data.csv", (2560, 1600))  # 创建眼动追踪实例
    eye_tracker.start_process()  # 启动眼动追踪
    sleep(5)  # 运行 60 秒
    eye_tracker.stop_process()  # 停止眼动追踪
