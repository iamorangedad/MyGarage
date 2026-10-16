# 常见汽车零件清单 / Common Car Parts Catalog

面向乘用车（汽油发动机）诊断练习。零件按系统分组，并给出建议的组件 ID，方便以后做成 MyGarage 的组件模块。

图例：

- **已实现**：当前代码里已有组件和故障
- **规划**：清单里列出，尚未做成组件

v0 已实现的只有起动电路：`battery_12v`、`starter_motor`，以及场景里的点火开关/搭铁/曲轴这些最小配套件。

---

## 1. 起动与充电 / Starting & Charging

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 12V 蓄电池 | 12V battery | `battery_12v` | 已实现 | 提供起动和熄火时的电能 |
| 蓄电池正极桩头 | Positive battery terminal | `battery_pos_terminal` | 规划 | 主电源连接点，腐蚀会增大压降 |
| 蓄电池负极桩头 | Negative battery terminal | `battery_neg_terminal` | 规划 | 回路连接点 |
| 发动机搭铁带 | Engine ground strap | `ground_strap` | 规划 | 发动机到车身的搭铁，松动会导致起动无力 |
| 起动机 | Starter motor | `starter_motor` | 已实现 | 带动曲轴转动 |
| 起动机电磁开关 | Starter solenoid | `starter_solenoid` | 规划 | 吸合驱动齿轮并接通大电流 |
| 起动继电器 | Starter relay | `starter_relay` | 规划 | 用小电流控制起动机电路 |
| 主熔断丝 / 起动熔断丝 | Main / starter fuse | `starter_fuse` | 规划 | 过流保护，熔断则完全无起动 |
| 点火开关 | Ignition switch | `ignition_switch` | 规划 | ACC / ON / START 档位 |
| 发电机（交流发电机） | Alternator | `alternator` | 规划 | 发动机运转时给蓄电池充电 |
| 发电机皮带 | Alternator belt / serpentine belt | `serpentine_belt` | 规划 | 带动发电机、水泵等 |
| 电压调节器 | Voltage regulator | `voltage_regulator` | 规划 | 把充电电压稳定在约 13.5–14.5 V |

## 2. 发动机本体 / Engine

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 发动机总成 | Engine assembly | `engine` | 规划 | 把燃料化学能转成机械能 |
| 气缸体 | Engine block | `engine_block` | 规划 | 气缸、曲轴的承载体 |
| 气缸盖 | Cylinder head | `cylinder_head` | 规划 | 气门、火花塞、燃烧室 |
| 气缸垫 | Head gasket | `head_gasket` | 规划 | 密封燃烧室、油道、水道 |
| 活塞 | Piston | `piston` | 规划 | 承受燃烧压力并传给连杆 |
| 活塞环 | Piston rings | `piston_rings` | 规划 | 密封气缸、刮油 |
| 连杆 | Connecting rod | `connecting_rod` | 规划 | 连接活塞和曲轴 |
| 曲轴 | Crankshaft | `crankshaft` | 规划 | 把往复运动变成旋转 |
| 凸轮轴 | Camshaft | `camshaft` | 规划 | 按正时开闭气门 |
| 正时皮带 / 正时链条 | Timing belt / timing chain | `timing_belt` | 规划 | 保证曲轴与凸轮轴同步 |
| 气门 | Valve | `valve` | 规划 | 控制进气和排气 |
| 气门油封 | Valve stem seal | `valve_stem_seal` | 规划 | 防止机油进入燃烧室 |
| 飞轮 | Flywheel | `flywheel` | 规划 | 储存转动惯量，与起动机啮合 |
| 曲轴位置传感器 | Crankshaft position sensor (CKP) | `ckp_sensor` | 规划 | 告诉 ECU 转速和上止点 |
| 凸轮轴位置传感器 | Camshaft position sensor (CMP) | `cmp_sensor` | 规划 | 判断哪一缸在做功 |

## 3. 点火系统 / Ignition

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 火花塞 | Spark plug | `spark_plug` | 规划 | 点燃混合气 |
| 点火线圈 | Ignition coil | `ignition_coil` | 规划 | 把 12 V 升到点火高压 |
| 高压线 | Spark plug wire | `spark_plug_wire` | 规划 | 把高压送到火花塞（老车） |
| 分电器 | Distributor | `distributor` | 规划 | 老式点火的分电与触发 |
| 爆震传感器 | Knock sensor | `knock_sensor` | 规划 | 检测爆震，ECU 据此推迟点火 |

## 4. 燃油系统 / Fuel

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 燃油箱 | Fuel tank | `fuel_tank` | 规划 | 储存汽油 |
| 燃油泵 | Fuel pump | `fuel_pump` | 规划 | 建立油轨压力 |
| 燃油滤清器 | Fuel filter | `fuel_filter` | 规划 | 过滤杂质 |
| 燃油压力调节器 | Fuel pressure regulator | `fuel_pressure_regulator` | 规划 | 维持油轨压力 |
| 喷油器 | Fuel injector | `fuel_injector` | 规划 | 按 ECU 指令喷油 |
| 油轨 | Fuel rail | `fuel_rail` | 规划 | 向各缸喷油器供油 |
| 油箱盖 | Fuel cap | `fuel_cap` | 规划 | 密封蒸发系统，松开会报蒸发故障 |
| 活性炭罐 | EVAP canister | `evap_canister` | 规划 | 吸附燃油蒸气 |
| 碳罐电磁阀 | Purge valve | `purge_valve` | 规划 | 把蒸气导入进气 |

## 5. 进气与排气 / Intake & Exhaust

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 空气滤清器 | Air filter | `air_filter` | 规划 | 过滤进气 |
| 节气门体 | Throttle body | `throttle_body` | 规划 | 控制进气量 |
| 怠速控制阀 | Idle air control valve | `iac_valve` | 规划 | 调节怠速空气（老车） |
| 进气歧管 | Intake manifold | `intake_manifold` | 规划 | 把空气分配到各缸 |
| 进气歧管垫 | Intake manifold gasket | `intake_gasket` | 规划 | 密封进气，漏气会导致怠速不稳 |
| 质量空气流量传感器 | MAF sensor | `maf_sensor` | 规划 | 测量进气质量 |
| 进气压力传感器 | MAP sensor | `map_sensor` | 规划 | 测量进气歧管压力 |
| 进气温度传感器 | IAT sensor | `iat_sensor` | 规划 | 测量进气温度 |
| 节气门位置传感器 | TPS | `tps_sensor` | 规划 | 测量油门开度 |
| 排气歧管 | Exhaust manifold | `exhaust_manifold` | 规划 | 汇集各缸废气 |
| 氧传感器（前） | Upstream O2 sensor | `o2_sensor_upstream` | 规划 | 反馈空燃比，供闭环喷油 |
| 氧传感器（后） | Downstream O2 sensor | `o2_sensor_downstream` | 规划 | 监测三元催化效率 |
| 三元催化器 | Catalytic converter | `catalytic_converter` | 规划 | 转化 CO、HC、NOx |
| 排气管 / 消声器 | Exhaust pipe / muffler | `muffler` | 规划 | 导出并降低排气噪声 |
| EGR 阀 | EGR valve | `egr_valve` | 规划 | 引入废气降低燃烧温度 |
| PCV 阀 | PCV valve | `pcv_valve` | 规划 | 把曲轴箱蒸气导入进气 |

## 6. 冷却系统 / Cooling

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 散热器 | Radiator | `radiator` | 规划 | 把冷却液热量散到空气 |
| 散热器盖 | Radiator cap | `radiator_cap` | 规划 | 保持系统压力，提高沸点 |
| 水泵 | Water pump | `water_pump` | 规划 | 循环冷却液 |
| 节温器 | Thermostat | `thermostat` | 规划 | 控制大循环开启温度 |
| 冷却风扇 | Cooling fan | `cooling_fan` | 规划 | 低速或怠速时强制散热 |
| 风扇继电器 | Fan relay | `fan_relay` | 规划 | 控制风扇电机通断 |
| 冷却液温度传感器 | Coolant temperature sensor (ECT) | `ect_sensor` | 规划 | 告诉 ECU 和仪表水温 |
| 膨胀水箱 | Coolant reservoir | `coolant_reservoir` | 规划 | 储存热胀冷缩的冷却液 |
| 暖风水箱 | Heater core | `heater_core` | 规划 | 用冷却液给驾驶室加热 |
| 冷却液软管 | Coolant hose | `coolant_hose` | 规划 | 连接散热器、发动机、暖风 |

## 7. 润滑系统 / Lubrication

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 机油泵 | Oil pump | `oil_pump` | 规划 | 建立机油压力 |
| 机油滤清器 | Oil filter | `oil_filter` | 规划 | 过滤机油杂质 |
| 油底壳 | Oil pan | `oil_pan` | 规划 | 储存机油 |
| 机油压力传感器 | Oil pressure sensor | `oil_pressure_sensor` | 规划 | 监测油压并驱动报警灯 |
| 机油尺 | Dipstick | `dipstick` | 规划 | 检查机油液位 |

## 8. 传动系统 / Drivetrain

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 离合器片 | Clutch disc | `clutch_disc` | 规划 | 手动挡传递或切断动力 |
| 离合器压盘 | Pressure plate | `pressure_plate` | 规划 | 压紧离合器片 |
| 分离轴承 | Release bearing | `release_bearing` | 规划 | 分离离合器 |
| 手动变速器 | Manual transmission | `manual_transmission` | 规划 | 改变传动比 |
| 自动变速器 | Automatic transmission | `automatic_transmission` | 规划 | 自动换挡 |
| 变矩器 | Torque converter | `torque_converter` | 规划 | 自动挡的液力耦合 |
| 变速器控制模块 | TCM | `tcm` | 规划 | 控制换挡和锁止 |
| 换挡电磁阀 | Shift solenoid | `shift_solenoid` | 规划 | 控制油路实现换挡 |
| 传动轴 | Driveshaft | `driveshaft` | 规划 | 后驱/四驱传递动力 |
| 等速万向节 | CV joint | `cv_joint` | 规划 | 前驱半轴在转向时仍能传力 |
| 半轴 | Axle shaft / half shaft | `axle_shaft` | 规划 | 差速器到车轮 |
| 差速器 | Differential | `differential` | 规划 | 允许左右轮转速不同 |
| 车轮轴承 | Wheel bearing | `wheel_bearing` | 规划 | 支承车轮旋转 |

## 9. 制动系统 / Brakes

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 制动踏板 | Brake pedal | `brake_pedal` | 规划 | 驾驶员输入 |
| 制动总泵 | Brake master cylinder | `master_cylinder` | 规划 | 把踏板力变成液压 |
| 制动助力器 | Brake booster | `brake_booster` | 规划 | 利用真空放大踏板力 |
| 制动液储液罐 | Brake fluid reservoir | `brake_fluid_reservoir` | 规划 | 储存制动液 |
| 制动硬管 / 软管 | Brake line / hose | `brake_line` | 规划 | 传递液压 |
| 制动钳 | Brake caliper | `brake_caliper` | 规划 | 夹紧制动盘 |
| 制动片 | Brake pads | `brake_pads` | 规划 | 摩擦材料 |
| 制动盘 | Brake disc / rotor | `brake_disc` | 规划 | 与制动片摩擦减速 |
| 制动鼓 | Brake drum | `brake_drum` | 规划 | 鼓式制动的旋转件 |
| 制动蹄 | Brake shoes | `brake_shoes` | 规划 | 鼓式制动摩擦件 |
| 轮缸 | Wheel cylinder | `wheel_cylinder` | 规划 | 鼓刹中把液压变成推力 |
| ABS 控制模块 | ABS module | `abs_module` | 规划 | 防抱死控制 |
| 轮速传感器 | Wheel speed sensor | `wheel_speed_sensor` | 规划 | 测量各轮转速，供 ABS/ESP |
| 制动灯开关 | Brake light switch | `brake_switch` | 规划 | 点亮制动灯，并通知 ECU |

## 10. 转向系统 / Steering

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 方向盘 | Steering wheel | `steering_wheel` | 规划 | 驾驶员输入 |
| 转向柱 | Steering column | `steering_column` | 规划 | 连接方向盘和转向机 |
| 转向机（齿轮齿条） | Steering rack | `steering_rack` | 规划 | 把转动变成横拉杆位移 |
| 转向助力泵 | Power steering pump | `power_steering_pump` | 规划 | 液压助力（液压转向） |
| 电动助力转向模块 | EPS module | `eps_module` | 规划 | 电机助力转向 |
| 横拉杆 | Tie rod | `tie_rod` | 规划 | 带动转向节 |
| 转向节 | Steering knuckle | `steering_knuckle` | 规划 | 连接拉杆、轴承和悬架 |

## 11. 悬架 / Suspension

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 减振器 | Shock absorber | `shock_absorber` | 规划 | 衰减弹簧振动 |
| 螺旋弹簧 | Coil spring | `coil_spring` | 规划 | 承受车身重量 |
| 控制臂 | Control arm | `control_arm` | 规划 | 定位车轮相对车身 |
| 球头 | Ball joint | `ball_joint` | 规划 | 控制臂与转向节的活动连接 |
| 稳定杆 | Sway bar | `sway_bar` | 规划 | 减小侧倾 |
| 稳定杆连杆 | Sway bar link | `sway_bar_link` | 规划 | 连接稳定杆和悬架 |
| 衬套 | Bushing | `suspension_bushing` | 规划 | 橡胶减振连接 |
| 麦弗逊支柱 | MacPherson strut | `strut` | 规划 | 减振器与弹簧一体的前悬架 |

## 12. 车轮与轮胎 / Wheels & Tires

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 轮胎 | Tire | `tire` | 规划 | 与地面接触，提供附着 |
| 轮辋 | Wheel rim | `wheel_rim` | 规划 | 安装轮胎 |
| 气门嘴 | Valve stem | `tire_valve` | 规划 | 充放气 |
| 胎压传感器 | TPMS sensor | `tpms_sensor` | 规划 | 监测胎压 |

## 13. 空调与暖风 / HVAC

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 空调压缩机 | A/C compressor | `ac_compressor` | 规划 | 压缩制冷剂 |
| 压缩机离合器 | A/C clutch | `ac_clutch` | 规划 | 接合或断开压缩机 |
| 冷凝器 | Condenser | `condenser` | 规划 | 把高温高压气态制冷剂冷凝 |
| 膨胀阀 / 节流管 | Expansion valve / orifice tube | `expansion_valve` | 规划 | 降低制冷剂压力 |
| 蒸发器 | Evaporator | `evaporator` | 规划 | 吸收驾驶室热量 |
| 鼓风机 | Blower motor | `blower_motor` | 规划 | 把空气吹过蒸发器或暖风水箱 |
| 鼓风机电阻 / 模块 | Blower resistor | `blower_resistor` | 规划 | 控制风速档位 |
| 空调压力开关 | A/C pressure switch | `ac_pressure_switch` | 规划 | 压力异常时切断压缩机 |

## 14. 车身电器 / Body Electrical

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 发动机控制单元 | ECU / PCM | `ecu` | 规划 | 控制喷油、点火、怠速等 |
| 车身控制模块 | BCM | `bcm` | 规划 | 灯光、门锁、雨刮等 |
| 仪表板 | Instrument cluster | `instrument_cluster` | 规划 | 显示车速、转速、故障灯 |
| OBD 诊断接口 | OBD-II port | `obd_port` | 规划 | 读取故障码和数据流 |
| 前大灯 | Headlight | `headlight` | 规划 | 夜间照明 |
| 尾灯 / 制动灯 | Tail / brake light | `tail_light` | 规划 | 示廓与制动信号 |
| 转向灯 | Turn signal | `turn_signal` | 规划 | 转向提示 |
| 闪光继电器 | Flasher relay | `flasher_relay` | 规划 | 让转向灯闪烁 |
| 喇叭 | Horn | `horn` | 规划 | 警告声 |
| 喇叭继电器 | Horn relay | `horn_relay` | 规划 | 控制喇叭大电流 |
| 雨刮电机 | Wiper motor | `wiper_motor` | 规划 | 驱动雨刮 |
| 雨刮片 | Wiper blade | `wiper_blade` | 规划 | 刮除挡风玻璃水膜 |
| 电动窗电机 | Window motor | `window_motor` | 规划 | 升降车窗 |
| 中控锁执行器 | Door lock actuator | `door_lock_actuator` | 规划 | 锁止/解锁车门 |
| 熔断丝盒 | Fuse box | `fuse_box` | 规划 | 集中保护各电路 |
| 继电器盒 | Relay box | `relay_box` | 规划 | 集中安装继电器 |

## 15. 排放与其他传感器 / Emissions & Other Sensors

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 车速传感器 | Vehicle speed sensor (VSS) | `vss` | 规划 | 车速信号，供仪表和变速器 |
| 加速踏板位置传感器 | APP sensor | `app_sensor` | 规划 | 电子油门的踏板位置 |
| 空气流量相关真空管 | Vacuum hose | `vacuum_hose` | 规划 | 真空泄漏会导致怠速高、刹车助力差 |

---

## 建议的实现顺序

诊断游戏里，零件最好按「能互相解释症状」的子系统一批批加，而不是一次做完全部几何。

1. **起动电路补全**（紧接现有蓄电池和起动机）
   - 搭铁带、点火开关、起动继电器、起动熔断丝、电磁开关
2. **充电系统**
   - 发电机、皮带、电压调节器
3. **能着车之后的怠速/缺火**
   - 火花塞、点火线圈、喷油器、燃油泵、曲轴位置传感器
4. **过热**
   - 节温器、水泵、冷却风扇、水温传感器、散热器
5. **制动与底盘**
   - 制动片、制动盘、轮速传感器、减振器

每一批仍然遵循现有约定：新组件模块 + `data/fault_catalog.yaml` 里的故障条目，不改核心循环。
