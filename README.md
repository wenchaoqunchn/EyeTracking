# EyeTracking

## 项目简介

此项目基于 Python、Tobii 和 PythonNet 实现了眼动追踪功能。通过使用 Tobii SDK 和相关 DLL 文件，您可以监测用户的眼动数据。项目包含核心的 `eye_tracking.py` 文件，其中构造了一个 `EyeTracker` 类，负责实现眼动监测的所有功能。

## 目录结构

```bash
├── dlls/
│   ├── tobii_interaction_lib.dll
│   ├── tobii_interaction_lib_c.dll
│   ├── tobii_interaction_lib_cs.dll
│   └── tobii_stream_engine.dll
├── eye_tracking.py
├── PyGazeAnalyser/
│   ├── __init__.py
│   ├── detectors.py
│   └── gazeplotter.py
├── sample_data.csv
└── 参考文献/

```

- `dlls/`：包含四个不可或缺的 DLL 文件，分别是：
  - `tobii_interaction_lib.dll`：基础交互库。
  - `tobii_interaction_lib_c.dll`：C 语言接口库。
  - `tobii_interaction_lib_cs.dll`：C# 接口库（供 PythonNet 调用）。
  - `tobii_stream_engine.dll`：流引擎库。

- `eye_tracking.py`：核心文件，包含 `EyeTracker` 类的实现。

- `PyGazeAnalyser/`：一个经过微调的第三方库，用于数据分析。

- `sample_data.csv`：示例输出的原始数据。

- `参考文献/`：几篇可能对你有帮助的综述和前樊院学长李镕辰的小论文。

## 使用说明

### 环境要求

- Python 3
- 安装 PythonNet：`pip install pythonnet`
- 安装其他依赖库（后续眼动分析视情况安装）

### 运行示例

1. 确保所有 DLL 文件位于 `dlls/` 文件夹中。
2. 运行 `eye_tracking.py` 文件。
3. 程序将开始监测5s的眼动数据。

### EyeTracker 类

- `__init__(self, save_path, resolution)`：初始化眼动追踪实例。
  - `save_path`：数据保存路径。
  - `resolution`：显示分辨率（如 `(2560, 1600)`）。
- `start_process(self)`：启动眼动追踪进程。
- `track(self)`：眼动追踪的实际过程，持续监控眼动数据。
- `stop_process(self)`：停止眼动追踪进程。
- `is_running(self)`：检查眼动追踪是否在运行。

### 数据处理

可以使用 `PyGazeAnalyser` 中的 `detectors.py` 提取注视和扫视等行为数据，使用 `gazeplotter.py` 进行可视化。（[PyGazeAnalyser参考链接](https://github.com/esdalmaijer/PyGazeAnalyser.git)）

## 注意事项

- 请确保您的系统中已安装 Tobii Experience。
- 由于 DLL 文件之间存在相互依赖关系，缺少任何一个文件将导致程序无法正常运行。

## EyeTracker类介绍

### 与 Tobii C# 库交互

在 `EyeTracker` 类中，通过 PythonNet 与 Tobii 的 C# 库进行交互，以下是与 Tobii C# 库交互的详细步骤和原理。

1. #### **引入 CLR**

首先，使用 PythonNet 的 CLR 模块来访问 .NET 组件：

```python
import clr
```

2. #### **添加 DLL 引用**

通过 `clr.AddReference` 方法加载 Tobii 的 C# DLL 文件：

```python
clr.AddReference("./dlls/tobii_interaction_lib_cs")
```

- 这里引用的是 `tobii_interaction_lib_cs.dll`，这是一个 C# 库，提供了与 Tobii 硬件的交互接口。

3. #### **导入 Tobii 命名空间**

在加载 DLL 后，导入相应的 Tobii 命名空间，以便调用其类和方法：

```python
import Tobii.InteractionLib as tobii
```

4. #### **创建 Tobii 交互库实例**

在 `track` 方法中，使用 `Tobii.InteractionLibFactory` 创建一个交互库实例：

```python
lib = tobii.InteractionLibFactory.CreateInteractionLib(tobii.FieldOfUse.Interactive)
```

- `CreateInteractionLib` 方法根据指定的使用场景（如 `Interactive`）创建一个交互库实例，允许我们进行眼动数据的捕获。

5. #### **设置显示区域**

使用交互库实例配置显示区域：

```python
lib.CoordinateTransformAddOrUpdateDisplayArea(self.width, self.height)
```

- 该方法设置眼动数据的坐标系统，使其与实际显示设备的分辨率相匹配。

6. #### **绑定眼动数据事件**

通过事件机制，将眼动数据事件与自定义的处理器进行绑定：

```python
lib.GazePointDataEvent += lambda event: self.event_handler(event)
```

- `GazePointDataEvent` 是一个事件，当 Tobii SDK 检测到新的眼动数据时，会触发该事件。
- 通过 lambda 表达式，将 `event_handler` 方法作为事件的回调函数，确保每次事件触发时都会调用该方法处理数据。

7. #### **等待和更新眼动数据**

在 `track` 方法的主循环中，使用 `WaitAndUpdate` 方法持续监控眼动数据：

```python
while self.running.value:
    lib.WaitAndUpdate()
```

- 该方法会阻塞当前线程，直到新的眼动数据可用。它确保程序能够实时接收和处理眼动信息。

8. #### **停止眼动追踪**

在停止眼动追踪时，不需要显式地调用 C# 库的方法来断开连接。通过设置状态变量来控制监测的停止：

```python
self.running.value = False
```

- 这使得 `track` 方法的循环结束，进而停止眼动数据的接收。

### 监测眼动事件

`EyeTracker` 类通过一系列步骤实现眼动数据的监测，以下是这些步骤的调用顺序和具体细节：

1. #### **启动眼动追踪**：

   - 调用 `start_process` 方法：

     ```python
     def start_process(self):
         if not self.running.value:
             self.running.value = True
             self.process = Process(target=self.track)
             self.process.start()
             print("Eye tracking started.")
     ```

   - 此方法检查眼动追踪是否已在运行，如果未运行，则创建一个新进程，并调用 `track` 方法以开始监测。

2. #### **进入眼动追踪过程**：

   - 在新进程中，调用 `track` 方法：

     ```python
     def track(self):
         lib = tobii.InteractionLibFactory.CreateInteractionLib(tobii.FieldOfUse.Interactive)
         lib.CoordinateTransformAddOrUpdateDisplayArea(self.width, self.height)
         lib.GazePointDataEvent += lambda event: self.event_handler(event)
     ```

   - 创建 Tobii 交互库实例，并设置显示区域的坐标转换。

   - 绑定 `GazePointDataEvent` 事件到 `event_handler` 方法，以便在眼动数据更新时自动调用该处理器。

3. #### **处理眼动数据事件**：

   - 当 Tobii SDK 检测到新眼动数据时，会触发 `GazePointDataEvent` 事件，调用 `event_handler` 方法：

     ```python
     def event_handler(self, event: tobii.GazePointData):
         x = round(event.x, self.rounding)
         y = round(event.y, self.rounding)
         is_valid = event.validity == tobii.Validity.Valid
         if is_valid and x > 0 and y > 0:
             t = round(time() * 1000, self.rounding)
             data = "{},{},{}\n".format(t, x, y)
             with self.lock:
                 with open(self.save_path, "a+") as f:
                     f.write(data)
                     print("{},{},{}\n".format(t, x, y))
     ```

   - 在处理器中，首先获取眼动坐标 `x` 和 `y`，并检查数据的有效性。

   - 仅当数据有效且坐标在合理范围内时，获取当前时间戳，并将数据格式化为字符串记录到文件中。

4. #### **持续监控**：

   - 在 `track` 方法的主循环中，使用 `WaitAndUpdate` 方法不断等待并更新眼动数据：

     ```python
     while self.running.value:
         lib.WaitAndUpdate()
     ```

   - 该循环会在 `self.running` 状态为 `True` 时持续运行，确保实时监测眼动数据。

5. #### **停止眼动追踪**：

   - 通过调用 `stop_process` 方法可以停止眼动追踪：

     ```python
     def stop_process(self):
         if self.running and self.process is not None:
             self.running.value = False
             self.process.join()
             print("Eye tracking stopped.")
     ```

   - 该方法设置 `running` 状态为 `False`，等待进程结束并打印停止信息。
