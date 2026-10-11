# MyGarage

**MyGarage** 是一个基于 MuJoCo 物理引擎的汽车维修模拟器，用于练习汽车故障诊断和维修技能。

**MyGarage** is a car repair simulator using MuJoCo physics engine for practicing vehicle diagnostic and repair skills.

## 特性 Features

- 🔧 **真实物理仿真** - 使用 MuJoCo 模拟机械部件行为
- ⚡ **电气系统模型** - 完整的电瓶和起动机系统仿真
- 🔍 **诊断工具** - 万用表、目视检查、起动测试等
- 📊 **评分系统** - 根据诊断效率和成本评估表现
- 🎮 **游戏化学习** - 通过案例学习故障诊断流程
- 🧩 **模块化设计** - 易于添加新部件和故障

## 快速开始 Quick Start

### 安装 Installation

```bash
# 克隆仓库 Clone repository
git clone <repository-url>
cd mygarage

# 安装依赖 Install dependencies
pip install -e .

# 或使用 uv (推荐)
uv pip install -e .
```

### 运行 Run

```bash
# 启动命令行界面 Start CLI
mygarage

# 或直接运行 Or run directly
python -m mygarage.ui.cli
```

### 游戏流程 Game Flow

1. 输入 `new` 开始新案例
2. 系统显示客户抱怨（症状）
3. 使用诊断工具调查：
   - `measure multimeter battery resting_voltage` - 测电瓶静态电压
   - `measure multimeter battery loaded_voltage` - 测负载电压
   - `measure visual battery general` - 目视检查电瓶
   - `measure crank_test starter attempt_start` - 尝试起动
4. 可选：`replace <component> <cost>` 更换零件
5. `diagnose <fault_id>` 提交诊断
6. 系统评分并显示结果

## 示例 Example

```
> new
===========================================================
NEW CASE
===========================================================
Customer complaint: 车辆无法启动,起动机无反应或只有微弱的咔哒声
===========================================================

> measure multimeter battery resting_voltage
[Multimeter] battery - resting_voltage: 11.5V

> measure crank_test starter attempt_start
[Crank Test] starter - attempt_start: Single CLICK, no rotation

> diagnose F001
===========================================================
DIAGNOSIS RESULT
===========================================================
✓ CORRECT
Total Score: 100.0 / 100
  Base: 100.0
  Efficiency: 100.0 (2 steps, optimal 3)
  Cost: 100.0 ($0.00 spent)

Excellent! Perfect diagnosis with minimal steps and no wasted parts.
===========================================================
```

## 可用命令 Available Commands

| 命令 Command | 说明 Description |
|-------------|-----------------|
| `help` | 显示帮助信息 Show help |
| `new [difficulty]` | 开始新案例 Start new case (easy/medium/hard) |
| `measure <tool> <target> <measurement>` | 使用诊断工具 Use diagnostic tool |
| `replace <component> <cost>` | 更换零件 Replace part |
| `diagnose <fault_id>` | 提交诊断 Submit diagnosis |
| `list` | 列出所有故障（参考） List all faults (reference) |
| `info <fault_id>` | 查看故障详情 View fault details |
| `quit` | 退出 Exit |

## 当前故障库 Current Faults

### 电瓶相关 Battery Faults

- **F001** - 电瓶亏电 (Dead Battery)
- **F002** - 电瓶单格损坏 (Bad Cell)
- **F003** - 电瓶桩头腐蚀 (Corroded Terminal)
- **F004** - 接地线松动 (Loose Ground)

### 起动机相关 Starter Faults

- **F005** - 起动机电磁开关故障 (Failed Starter Solenoid)
- **F006** - 起动机磨损 (Worn Starter Motor)
- **F007** - 保险丝熔断 (Blown Fuse)
- **F008** - 继电器失效 (Failed Relay)

## 添加新部件 Adding New Components

1. 在 `src/mygarage/components/` 创建新组件文件
2. 继承 `Component` 基类并实现接口：
   - `get_mjcf()` - 返回 MJCF XML
   - `apply_fault()` - 应用故障
   - `get_reading()` - 返回诊断读数
3. 在 `data/faults/` 添加故障 YAML 文件
4. 无需修改核心代码

示例组件结构：

```python
from mygarage.components.base import Component

class NewComponent(Component):
    def __init__(self):
        super().__init__("Component Name", "component_id")
        
    def get_mjcf(self) -> str:
        return """<body>...</body>"""
        
    def apply_fault(self, fault_id: str, params: dict):
        self.state.fault_id = fault_id
        
    def get_reading(self, tool_name: str, measurement: str, params: dict) -> dict:
        return {"value": 0, "unit": ""}
```

## 测试 Testing

```bash
# 运行所有测试 Run all tests
pytest

# 运行特定测试 Run specific test
pytest tests/test_components.py

# 查看覆盖率 View coverage
pytest --cov=mygarage
```

所有测试均支持无头运行（无需显示）。

## 项目结构 Project Structure

```
mygarage/
├── pyproject.toml          # 项目配置
├── README.md               # 本文档
├── docs/
│   ├── design/
│   │   └── feasibility-and-plan.md  # 可行性分析与设计
│   └── architecture.md     # 架构文档
├── data/
│   └── faults/
│       └── battery_starter.yaml     # 故障库
├── src/mygarage/
│   ├── components/         # 部件层
│   │   ├── base.py
│   │   ├── battery.py
│   │   └── starter.py
│   ├── system_model/       # 系统模型层
│   │   └── electrical.py
│   ├── faults/             # 故障引擎
│   │   ├── catalog.py
│   │   └── injector.py
│   ├── diagnostics/        # 诊断工具
│   │   ├── base.py
│   │   ├── multimeter.py
│   │   ├── visual.py
│   │   └── crank_test.py
│   ├── scoring.py          # 评分系统
│   ├── game.py             # 游戏主逻辑
│   └── ui/
│       └── cli.py          # 命令行界面
└── tests/                  # 测试
    ├── test_components.py
    ├── test_faults.py
    ├── test_diagnostics.py
    ├── test_scoring.py
    └── test_integration.py
```

## 架构文档 Architecture

详细架构设计请参阅：

- [可行性分析与设计方案](docs/design/feasibility-and-plan.md) - 完整的可行性分析和架构设计
- [架构文档](docs/architecture.md) - 技术架构详解

## 开发计划 Roadmap

### v0.1 (当前 Current)
- ✅ 基础架构
- ✅ 电瓶 + 起动机系统
- ✅ 故障注入和诊断
- ✅ CLI 界面
- ✅ 评分系统

### v0.2 (规划中 Planned)
- 🔄 刹车系统组件
- 🔄 更多故障类型
- 🔄 ImGui 图形界面
- 🔄 更详细的 MuJoCo 模型

### 未来 Future
- 🌐 Web 界面 (MuJoCo WASM)
- 🚗 完整车辆模型
- 🎓 教学模式和提示系统
- 📈 进度追踪和成就系统

## 依赖 Dependencies

- Python >= 3.10
- MuJoCo >= 3.0.0
- NumPy >= 1.24.0
- PyYAML >= 6.0
- pytest >= 7.0.0 (开发)

## 许可 License

MIT License

## 贡献 Contributing

欢迎贡献！特别欢迎：

- 新的车辆部件
- 更多真实的故障案例
- 改进的物理模型
- UI/UX 改进
- 文档翻译

## 致谢 Acknowledgments

- [MuJoCo](https://mujoco.org/) - 物理仿真引擎
- [microduck](https://github.com/pollen-robotics/microduck) - 架构灵感来源
