# MyGarage

[English](#english) | [中文](#中文)

---

## English

**MyGarage** is a game-like simulator where you practice car diagnosis and repair in a virtual environment. Investigate customer complaints, use diagnostic tools, identify faulty components, and submit your diagnosis for scoring.

### Features

- **Component-Based Architecture**: Modular car parts with realistic fault modes
- **Physics Simulation**: MuJoCo-based 3D visualization (optional)
- **Data-Driven Faults**: YAML-based fault catalog for easy extension
- **Diagnostic Tools**: Visual inspection, multimeter, load tests, crank tests
- **Scoring System**: Evaluates correctness, efficiency, and cost
- **Headless Mode**: Run without display for testing and automation
- **Extensible**: Add new components and faults with minimal code changes

### Quick Start

#### Installation

```bash
# Clone the repository
git clone <repository-url>
cd mygarage

# Install with pip
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

#### Run the Game

```bash
# Interactive mode (play the game)
mygarage --mode interactive

# Demo mode (automated demonstration)
mygarage --mode demo

# Test mode (verify installation)
mygarage --mode test
```

#### Example Gameplay

```bash
$ mygarage --mode interactive

============================================================
          MyGarage - Car Diagnosis Simulator
============================================================

Customer complaint:
- Car won't start
- Clicking sound when trying to start

Difficulty: easy

Your task: Diagnose the problem and identify the faulty component.

Available Actions:
  1. Visual inspection
  2. Measure voltage (resting)
  3. Measure voltage (while cranking)
  4. Battery load test
  5. Crank test
  6. Replace part
  7. Submit diagnosis
  9. Show components
  0. Quit

Choose action: 2
Component (battery_12v): battery_12v

Voltage Measurement (resting):
  11.5 V

Choose action: 4

Battery Load Test:
  Voltage before: 11.5 V
  Voltage during load: 8.0 V
  Voltage drop: 3.5 V
  Estimated CCA: 120
  Result: FAIL

Choose action: 7

Submit your diagnosis:
Faulty component ID: battery_12v
Fault name: discharged_battery

==================================================
DIAGNOSIS REPORT
==================================================

Diagnosis: CORRECT ✓
Base Points: 100
Tool Usage Penalty: -0
Parts Replaced: 0 ($0.00)
Efficiency Bonus: +20

TOTAL SCORE: 120
GRADE: A
==================================================
```

### Project Structure

```
mygarage/
├── src/mygarage/           # Main package
│   ├── component.py        # Base component class
│   ├── components/         # Car component implementations
│   │   ├── battery.py
│   │   └── starter_motor.py
│   ├── fault_engine.py     # Fault injection and catalog
│   ├── system_model.py     # System-wide state management
│   ├── diagnostic_tools.py # Diagnostic tool implementations
│   ├── scoring.py          # Scoring system
│   ├── simulation.py       # MuJoCo integration
│   ├── game.py             # Main game loop
│   ├── cli.py              # Command-line interface
│   └── mjcf/               # MuJoCo models
│       └── garage_scene.xml
├── data/
│   └── fault_catalog.yaml  # Fault definitions
├── tests/                  # Test suite
├── docs/                   # Documentation
│   └── architecture.md
├── pyproject.toml          # Package configuration
└── README.md               # This file
```

### Adding a New Component

1. **Create component class** in `src/mygarage/components/new_component.py`:

```python
from mygarage.component import Component, FaultMode

class NewComponent(Component):
    def __init__(self):
        super().__init__("new_component", "New Component")
        self.parameters = self.get_nominal_parameters()
        self._define_fault_modes()
    
    def get_nominal_parameters(self):
        return {'param1': 100.0, 'replacement_cost': 150.0}
    
    def _define_fault_modes(self):
        self.fault_modes = [
            FaultMode(
                name="fault_mode_1",
                description="Something broke",
                symptoms=["Symptom 1"],
                affected_parameters={'param1': 50.0}
            )
        ]
    
    def get_diagnostic_readings(self, tool, context):
        if tool == 'visual':
            return {'findings': ['Looks okay']}
        return {}
```

2. **Add to component registry** in `src/mygarage/components/__init__.py`

3. **Add faults** to `data/fault_catalog.yaml`:

```yaml
faults:
  - fault_id: "F999"
    component_id: "new_component"
    fault_name: "fault_mode_1"
    description: "Something broke"
    root_cause: "Wear and tear"
    symptoms: ["Symptom 1"]
    difficulty: "medium"
    points: 100
```

4. **Register in SystemModel** in `system_model.py`:

```python
def _initialize_default_components(self):
    self.add_component(Battery())
    self.add_component(StarterMotor())
    self.add_component(NewComponent())  # Add this
```

5. **Write tests** in `tests/test_components.py`

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mygarage

# Run specific test file
pytest tests/test_components.py

# Run in verbose mode
pytest -v
```

### Documentation

- **Architecture Overview**: See `docs/architecture.md` for detailed system design
- **Parts Catalog**: See `docs/parts_catalog.md` for common car parts grouped by system
- **Component API**: See `src/mygarage/component.py` for base class documentation
- **Fault Catalog Format**: See `data/fault_catalog.yaml` for examples

### Current Components

The playable car covers five subsystems. See `docs/parts_catalog.md` for the full list and which rows are implemented.

- **Starting**: battery, starter, ground strap, ignition switch, starter relay, starter fuse, solenoid
- **Charging**: alternator, serpentine belt, voltage regulator
- **Combustion**: spark plug, ignition coil, fuel injector, fuel pump, crankshaft position sensor
- **Cooling**: thermostat, water pump, cooling fan, coolant temperature sensor, radiator
- **Chassis**: brake pads, brake disc, wheel speed sensor, shock absorber

### License

MIT

---

## 中文

**MyGarage** 是一个类似游戏的模拟器，您可以在虚拟环境中练习汽车诊断和维修。调查客户投诉，使用诊断工具，识别故障组件，并提交您的诊断以获得评分。

### 功能特点

- **基于组件的架构**：模块化汽车零件，具有真实的故障模式
- **物理仿真**：基于 MuJoCo 的 3D 可视化（可选）
- **数据驱动的故障**：基于 YAML 的故障目录，易于扩展
- **诊断工具**：目视检查、万用表、负载测试、启动测试
- **评分系统**：评估正确性、效率和成本
- **无头模式**：无需显示器即可运行，用于测试和自动化
- **可扩展**：添加新组件和故障，代码更改最少

### 快速开始

#### 安装

```bash
# 克隆仓库
git clone <repository-url>
cd mygarage

# 使用 pip 安装
pip install -e .

# 或安装开发依赖
pip install -e ".[dev]"
```

#### 运行游戏

```bash
# 交互模式（玩游戏）
mygarage --mode interactive

# 演示模式（自动演示）
mygarage --mode demo

# 测试模式（验证安装）
mygarage --mode test
```

#### 游戏示例

```bash
$ mygarage --mode interactive

============================================================
          MyGarage - 汽车诊断模拟器
============================================================

客户投诉：
- 汽车无法启动
- 尝试启动时有咔嗒声

难度：简单

您的任务：诊断问题并识别故障组件。

可用操作：
  1. 目视检查
  2. 测量电压（静态）
  3. 测量电压（启动时）
  4. 电池负载测试
  5. 启动测试
  6. 更换零件
  7. 提交诊断
  9. 显示组件
  0. 退出

选择操作：2
组件 (battery_12v): battery_12v

电压测量（静态）：
  11.5 V

选择操作：4

电池负载测试：
  测试前电压：11.5 V
  负载时电压：8.0 V
  电压降：3.5 V
  估计冷启动电流：120
  结果：失败

选择操作：7

提交您的诊断：
故障组件 ID：battery_12v
故障名称：discharged_battery

==================================================
诊断报告
==================================================

诊断：正确 ✓
基础分数：100
工具使用扣分：-0
更换零件：0 ($0.00)
效率奖励：+20

总分：120
等级：A
==================================================
```

### 项目结构

```
mygarage/
├── src/mygarage/           # 主包
│   ├── component.py        # 基础组件类
│   ├── components/         # 汽车组件实现
│   │   ├── battery.py
│   │   └── starter_motor.py
│   ├── fault_engine.py     # 故障注入和目录
│   ├── system_model.py     # 系统级状态管理
│   ├── diagnostic_tools.py # 诊断工具实现
│   ├── scoring.py          # 评分系统
│   ├── simulation.py       # MuJoCo 集成
│   ├── game.py             # 主游戏循环
│   ├── cli.py              # 命令行界面
│   └── mjcf/               # MuJoCo 模型
│       └── garage_scene.xml
├── data/
│   └── fault_catalog.yaml  # 故障定义
├── tests/                  # 测试套件
├── docs/                   # 文档
│   └── architecture.md
├── pyproject.toml          # 包配置
└── README.md               # 本文件
```

### 添加新组件

1. **创建组件类** 在 `src/mygarage/components/new_component.py`：

```python
from mygarage.component import Component, FaultMode

class NewComponent(Component):
    def __init__(self):
        super().__init__("new_component", "新组件")
        self.parameters = self.get_nominal_parameters()
        self._define_fault_modes()
    
    def get_nominal_parameters(self):
        return {'param1': 100.0, 'replacement_cost': 150.0}
    
    def _define_fault_modes(self):
        self.fault_modes = [
            FaultMode(
                name="fault_mode_1",
                description="某物损坏",
                symptoms=["症状 1"],
                affected_parameters={'param1': 50.0}
            )
        ]
    
    def get_diagnostic_readings(self, tool, context):
        if tool == 'visual':
            return {'findings': ['看起来还好']}
        return {}
```

2. **添加到组件注册表** 在 `src/mygarage/components/__init__.py`

3. **添加故障** 到 `data/fault_catalog.yaml`：

```yaml
faults:
  - fault_id: "F999"
    component_id: "new_component"
    fault_name: "fault_mode_1"
    description: "某物损坏"
    root_cause: "磨损"
    symptoms: ["症状 1"]
    difficulty: "medium"
    points: 100
```

4. **在 SystemModel 中注册** 在 `system_model.py`：

```python
def _initialize_default_components(self):
    self.add_component(Battery())
    self.add_component(StarterMotor())
    self.add_component(NewComponent())  # 添加这个
```

5. **编写测试** 在 `tests/test_components.py`

### 运行测试

```bash
# 运行所有测试
pytest

# 运行带覆盖率的测试
pytest --cov=mygarage

# 运行特定测试文件
pytest tests/test_components.py

# 详细模式运行
pytest -v
```

### 文档

- **架构概述**：详细系统设计请参阅 `docs/architecture.md`
- **零件清单**：常见汽车零件按系统分组，见 `docs/parts_catalog.md`
- **组件 API**：基类文档请参阅 `src/mygarage/component.py`
- **故障目录格式**：示例请参阅 `data/fault_catalog.yaml`

### 当前组件

目前可以诊断的零件覆盖五个系统，完整对照见 `docs/parts_catalog.md`。

- **起动**：蓄电池、起动机、搭铁带、点火开关、起动继电器、起动熔断丝、电磁开关
- **充电**：发电机、皮带、电压调节器
- **燃烧**：火花塞、点火线圈、喷油器、燃油泵、曲轴位置传感器
- **冷却**：节温器、水泵、冷却风扇、水温传感器、散热器
- **底盘**：制动片、制动盘、轮速传感器、减振器

### 许可证

MIT

---

For detailed architecture documentation, see `docs/architecture.md`.

关于详细的架构文档，请参阅 `docs/architecture.md`。
