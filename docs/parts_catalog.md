# 常见汽车零件清单 / Common Car Parts Catalog

面向乘用车（汽油发动机）诊断练习。零件按系统分组，并给出建议的组件 ID，方便以后做成 MyGarage 的组件模块。

图例：

- **已实现**：当前代码里已有组件和故障

表里的零件都已经做成组件，并且写进了故障目录。都可以在游戏里目视检查、读取故障码、更换和提交诊断。

会改变车子运行的零件接在系统模型里：

1. 起动电路：搭铁带、点火开关、起动继电器、起动熔断丝、电磁开关、蓄电池桩头、飞轮齿圈（另有蓄电池和起动机）
2. 充电：发电机、皮带、电压调节器
3. 着车与缺火：火花塞、点火线圈、高压线、分电器、喷油器、燃油泵、燃油滤清器、燃油压力调节器、曲轴位置传感器、凸轮轴位置传感器、正时皮带
4. 过热：节温器、水泵、冷却风扇、风扇继电器、水温传感器、散热器、散热器盖、气缸垫、冷却液软管、暖风水箱、膨胀水箱
5. 机油压力：机油泵、油底壳
6. 进气与排气：空气滤清器、节气门、怠速控制阀、进气歧管垫、真空管、碳罐电磁阀、空气流量传感器、进气压力传感器、前后氧传感器、三元催化器、消声器、EGR 阀、PCV 阀

制动、转向、悬架、传动、空调和车身电器只出现在各自的目视检查、测量读数和故障码里。MuJoCo 场景仍然只带动曲轴。

---

## 1. 起动与充电 / Starting & Charging

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 12V 蓄电池 | 12V battery | `battery_12v` | 已实现 | 提供起动和熄火时的电能 |
| 蓄电池正极桩头 | Positive battery terminal | `battery_pos_terminal` | 已实现 | 主电源连接点，腐蚀会增大压降 |
| 蓄电池负极桩头 | Negative battery terminal | `battery_neg_terminal` | 已实现 | 回路连接点 |
| 发动机搭铁带 | Engine ground strap | `ground_strap` | 已实现 | 发动机到车身的搭铁，松动会导致起动无力 |
| 起动机 | Starter motor | `starter_motor` | 已实现 | 带动曲轴转动 |
| 起动机电磁开关 | Starter solenoid | `starter_solenoid` | 已实现 | 吸合驱动齿轮并接通大电流 |
| 起动继电器 | Starter relay | `starter_relay` | 已实现 | 用小电流控制起动机电路 |
| 主熔断丝 / 起动熔断丝 | Main / starter fuse | `starter_fuse` | 已实现 | 过流保护，熔断则完全无起动 |
| 点火开关 | Ignition switch | `ignition_switch` | 已实现 | ACC / ON / START 档位 |
| 发电机（交流发电机） | Alternator | `alternator` | 已实现 | 发动机运转时给蓄电池充电 |
| 发电机皮带 | Alternator belt / serpentine belt | `serpentine_belt` | 已实现 | 带动发电机、水泵等 |
| 电压调节器 | Voltage regulator | `voltage_regulator` | 已实现 | 把充电电压稳定在约 13.5–14.5 V |

## 2. 发动机本体 / Engine

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 发动机总成 | Engine assembly | `engine` | 已实现 | 把燃料化学能转成机械能 |
| 气缸体 | Engine block | `engine_block` | 已实现 | 气缸、曲轴的承载体 |
| 气缸盖 | Cylinder head | `cylinder_head` | 已实现 | 气门、火花塞、燃烧室 |
| 气缸垫 | Head gasket | `head_gasket` | 已实现 | 密封燃烧室、油道、水道 |
| 活塞 | Piston | `piston` | 已实现 | 承受燃烧压力并传给连杆 |
| 活塞环 | Piston rings | `piston_rings` | 已实现 | 密封气缸、刮油 |
| 连杆 | Connecting rod | `connecting_rod` | 已实现 | 连接活塞和曲轴 |
| 曲轴 | Crankshaft | `crankshaft` | 已实现 | 把往复运动变成旋转 |
| 凸轮轴 | Camshaft | `camshaft` | 已实现 | 按正时开闭气门 |
| 正时皮带 / 正时链条 | Timing belt / timing chain | `timing_belt` | 已实现 | 保证曲轴与凸轮轴同步 |
| 气门 | Valve | `valve` | 已实现 | 控制进气和排气 |
| 气门油封 | Valve stem seal | `valve_stem_seal` | 已实现 | 防止机油进入燃烧室 |
| 飞轮 | Flywheel | `flywheel` | 已实现 | 储存转动惯量，与起动机啮合 |
| 曲轴位置传感器 | Crankshaft position sensor (CKP) | `ckp_sensor` | 已实现 | 告诉 ECU 转速和上止点 |
| 凸轮轴位置传感器 | Camshaft position sensor (CMP) | `cmp_sensor` | 已实现 | 判断哪一缸在做功 |

## 3. 点火系统 / Ignition

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 火花塞 | Spark plug | `spark_plug` | 已实现 | 点燃混合气 |
| 点火线圈 | Ignition coil | `ignition_coil` | 已实现 | 把 12 V 升到点火高压 |
| 高压线 | Spark plug wire | `spark_plug_wire` | 已实现 | 把高压送到火花塞（老车） |
| 分电器 | Distributor | `distributor` | 已实现 | 老式点火的分电与触发 |
| 爆震传感器 | Knock sensor | `knock_sensor` | 已实现 | 检测爆震，ECU 据此推迟点火 |

## 4. 燃油系统 / Fuel

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 燃油箱 | Fuel tank | `fuel_tank` | 已实现 | 储存汽油 |
| 燃油泵 | Fuel pump | `fuel_pump` | 已实现 | 建立油轨压力 |
| 燃油滤清器 | Fuel filter | `fuel_filter` | 已实现 | 过滤杂质 |
| 燃油压力调节器 | Fuel pressure regulator | `fuel_pressure_regulator` | 已实现 | 维持油轨压力 |
| 喷油器 | Fuel injector | `fuel_injector` | 已实现 | 按 ECU 指令喷油 |
| 油轨 | Fuel rail | `fuel_rail` | 已实现 | 向各缸喷油器供油 |
| 油箱盖 | Fuel cap | `fuel_cap` | 已实现 | 密封蒸发系统，松开会报蒸发故障 |
| 活性炭罐 | EVAP canister | `evap_canister` | 已实现 | 吸附燃油蒸气 |
| 碳罐电磁阀 | Purge valve | `purge_valve` | 已实现 | 把蒸气导入进气 |

## 5. 进气与排气 / Intake & Exhaust

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 空气滤清器 | Air filter | `air_filter` | 已实现 | 过滤进气 |
| 节气门体 | Throttle body | `throttle_body` | 已实现 | 控制进气量 |
| 怠速控制阀 | Idle air control valve | `iac_valve` | 已实现 | 调节怠速空气（老车） |
| 进气歧管 | Intake manifold | `intake_manifold` | 已实现 | 把空气分配到各缸 |
| 进气歧管垫 | Intake manifold gasket | `intake_gasket` | 已实现 | 密封进气，漏气会导致怠速不稳 |
| 质量空气流量传感器 | MAF sensor | `maf_sensor` | 已实现 | 测量进气质量 |
| 进气压力传感器 | MAP sensor | `map_sensor` | 已实现 | 测量进气歧管压力 |
| 进气温度传感器 | IAT sensor | `iat_sensor` | 已实现 | 测量进气温度 |
| 节气门位置传感器 | TPS | `tps_sensor` | 已实现 | 测量油门开度 |
| 排气歧管 | Exhaust manifold | `exhaust_manifold` | 已实现 | 汇集各缸废气 |
| 氧传感器（前） | Upstream O2 sensor | `o2_sensor_upstream` | 已实现 | 反馈空燃比，供闭环喷油 |
| 氧传感器（后） | Downstream O2 sensor | `o2_sensor_downstream` | 已实现 | 监测三元催化效率 |
| 三元催化器 | Catalytic converter | `catalytic_converter` | 已实现 | 转化 CO、HC、NOx |
| 排气管 / 消声器 | Exhaust pipe / muffler | `muffler` | 已实现 | 导出并降低排气噪声 |
| EGR 阀 | EGR valve | `egr_valve` | 已实现 | 引入废气降低燃烧温度 |
| PCV 阀 | PCV valve | `pcv_valve` | 已实现 | 把曲轴箱蒸气导入进气 |

## 6. 冷却系统 / Cooling

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 散热器 | Radiator | `radiator` | 已实现 | 把冷却液热量散到空气 |
| 散热器盖 | Radiator cap | `radiator_cap` | 已实现 | 保持系统压力，提高沸点 |
| 水泵 | Water pump | `water_pump` | 已实现 | 循环冷却液 |
| 节温器 | Thermostat | `thermostat` | 已实现 | 控制大循环开启温度 |
| 冷却风扇 | Cooling fan | `cooling_fan` | 已实现 | 低速或怠速时强制散热 |
| 风扇继电器 | Fan relay | `fan_relay` | 已实现 | 控制风扇电机通断 |
| 冷却液温度传感器 | Coolant temperature sensor (ECT) | `ect_sensor` | 已实现 | 告诉 ECU 和仪表水温 |
| 膨胀水箱 | Coolant reservoir | `coolant_reservoir` | 已实现 | 储存热胀冷缩的冷却液 |
| 暖风水箱 | Heater core | `heater_core` | 已实现 | 用冷却液给驾驶室加热 |
| 冷却液软管 | Coolant hose | `coolant_hose` | 已实现 | 连接散热器、发动机、暖风 |

## 7. 润滑系统 / Lubrication

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 机油泵 | Oil pump | `oil_pump` | 已实现 | 建立机油压力 |
| 机油滤清器 | Oil filter | `oil_filter` | 已实现 | 过滤机油杂质 |
| 油底壳 | Oil pan | `oil_pan` | 已实现 | 储存机油 |
| 机油压力传感器 | Oil pressure sensor | `oil_pressure_sensor` | 已实现 | 监测油压并驱动报警灯 |
| 机油尺 | Dipstick | `dipstick` | 已实现 | 检查机油液位 |

## 8. 传动系统 / Drivetrain

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 离合器片 | Clutch disc | `clutch_disc` | 已实现 | 手动挡传递或切断动力 |
| 离合器压盘 | Pressure plate | `pressure_plate` | 已实现 | 压紧离合器片 |
| 分离轴承 | Release bearing | `release_bearing` | 已实现 | 分离离合器 |
| 手动变速器 | Manual transmission | `manual_transmission` | 已实现 | 改变传动比 |
| 自动变速器 | Automatic transmission | `automatic_transmission` | 已实现 | 自动换挡 |
| 变矩器 | Torque converter | `torque_converter` | 已实现 | 自动挡的液力耦合 |
| 变速器控制模块 | TCM | `tcm` | 已实现 | 控制换挡和锁止 |
| 换挡电磁阀 | Shift solenoid | `shift_solenoid` | 已实现 | 控制油路实现换挡 |
| 传动轴 | Driveshaft | `driveshaft` | 已实现 | 后驱/四驱传递动力 |
| 等速万向节 | CV joint | `cv_joint` | 已实现 | 前驱半轴在转向时仍能传力 |
| 半轴 | Axle shaft / half shaft | `axle_shaft` | 已实现 | 差速器到车轮 |
| 差速器 | Differential | `differential` | 已实现 | 允许左右轮转速不同 |
| 车轮轴承 | Wheel bearing | `wheel_bearing` | 已实现 | 支承车轮旋转 |

## 9. 制动系统 / Brakes

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 制动踏板 | Brake pedal | `brake_pedal` | 已实现 | 驾驶员输入 |
| 制动总泵 | Brake master cylinder | `master_cylinder` | 已实现 | 把踏板力变成液压 |
| 制动助力器 | Brake booster | `brake_booster` | 已实现 | 利用真空放大踏板力 |
| 制动液储液罐 | Brake fluid reservoir | `brake_fluid_reservoir` | 已实现 | 储存制动液 |
| 制动硬管 / 软管 | Brake line / hose | `brake_line` | 已实现 | 传递液压 |
| 制动钳 | Brake caliper | `brake_caliper` | 已实现 | 夹紧制动盘 |
| 制动片 | Brake pads | `brake_pads` | 已实现 | 摩擦材料 |
| 制动盘 | Brake disc / rotor | `brake_disc` | 已实现 | 与制动片摩擦减速 |
| 制动鼓 | Brake drum | `brake_drum` | 已实现 | 鼓式制动的旋转件 |
| 制动蹄 | Brake shoes | `brake_shoes` | 已实现 | 鼓式制动摩擦件 |
| 轮缸 | Wheel cylinder | `wheel_cylinder` | 已实现 | 鼓刹中把液压变成推力 |
| ABS 控制模块 | ABS module | `abs_module` | 已实现 | 防抱死控制 |
| 轮速传感器 | Wheel speed sensor | `wheel_speed_sensor` | 已实现 | 测量各轮转速，供 ABS/ESP |
| 制动灯开关 | Brake light switch | `brake_switch` | 已实现 | 点亮制动灯，并通知 ECU |

## 10. 转向系统 / Steering

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 方向盘 | Steering wheel | `steering_wheel` | 已实现 | 驾驶员输入 |
| 转向柱 | Steering column | `steering_column` | 已实现 | 连接方向盘和转向机 |
| 转向机（齿轮齿条） | Steering rack | `steering_rack` | 已实现 | 把转动变成横拉杆位移 |
| 转向助力泵 | Power steering pump | `power_steering_pump` | 已实现 | 液压助力（液压转向） |
| 电动助力转向模块 | EPS module | `eps_module` | 已实现 | 电机助力转向 |
| 横拉杆 | Tie rod | `tie_rod` | 已实现 | 带动转向节 |
| 转向节 | Steering knuckle | `steering_knuckle` | 已实现 | 连接拉杆、轴承和悬架 |

## 11. 悬架 / Suspension

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 减振器 | Shock absorber | `shock_absorber` | 已实现 | 衰减弹簧振动 |
| 螺旋弹簧 | Coil spring | `coil_spring` | 已实现 | 承受车身重量 |
| 控制臂 | Control arm | `control_arm` | 已实现 | 定位车轮相对车身 |
| 球头 | Ball joint | `ball_joint` | 已实现 | 控制臂与转向节的活动连接 |
| 稳定杆 | Sway bar | `sway_bar` | 已实现 | 减小侧倾 |
| 稳定杆连杆 | Sway bar link | `sway_bar_link` | 已实现 | 连接稳定杆和悬架 |
| 衬套 | Bushing | `suspension_bushing` | 已实现 | 橡胶减振连接 |
| 麦弗逊支柱 | MacPherson strut | `strut` | 已实现 | 减振器与弹簧一体的前悬架 |

## 12. 车轮与轮胎 / Wheels & Tires

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 轮胎 | Tire | `tire` | 已实现 | 与地面接触，提供附着 |
| 轮辋 | Wheel rim | `wheel_rim` | 已实现 | 安装轮胎 |
| 气门嘴 | Valve stem | `tire_valve` | 已实现 | 充放气 |
| 胎压传感器 | TPMS sensor | `tpms_sensor` | 已实现 | 监测胎压 |

## 13. 空调与暖风 / HVAC

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 空调压缩机 | A/C compressor | `ac_compressor` | 已实现 | 压缩制冷剂 |
| 压缩机离合器 | A/C clutch | `ac_clutch` | 已实现 | 接合或断开压缩机 |
| 冷凝器 | Condenser | `condenser` | 已实现 | 把高温高压气态制冷剂冷凝 |
| 膨胀阀 / 节流管 | Expansion valve / orifice tube | `expansion_valve` | 已实现 | 降低制冷剂压力 |
| 蒸发器 | Evaporator | `evaporator` | 已实现 | 吸收驾驶室热量 |
| 鼓风机 | Blower motor | `blower_motor` | 已实现 | 把空气吹过蒸发器或暖风水箱 |
| 鼓风机电阻 / 模块 | Blower resistor | `blower_resistor` | 已实现 | 控制风速档位 |
| 空调压力开关 | A/C pressure switch | `ac_pressure_switch` | 已实现 | 压力异常时切断压缩机 |

## 14. 车身电器 / Body Electrical

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 发动机控制单元 | ECU / PCM | `ecu` | 已实现 | 控制喷油、点火、怠速等 |
| 车身控制模块 | BCM | `bcm` | 已实现 | 灯光、门锁、雨刮等 |
| 仪表板 | Instrument cluster | `instrument_cluster` | 已实现 | 显示车速、转速、故障灯 |
| OBD 诊断接口 | OBD-II port | `obd_port` | 已实现 | 读取故障码和数据流 |
| 前大灯 | Headlight | `headlight` | 已实现 | 夜间照明 |
| 尾灯 / 制动灯 | Tail / brake light | `tail_light` | 已实现 | 示廓与制动信号 |
| 转向灯 | Turn signal | `turn_signal` | 已实现 | 转向提示 |
| 闪光继电器 | Flasher relay | `flasher_relay` | 已实现 | 让转向灯闪烁 |
| 喇叭 | Horn | `horn` | 已实现 | 警告声 |
| 喇叭继电器 | Horn relay | `horn_relay` | 已实现 | 控制喇叭大电流 |
| 雨刮电机 | Wiper motor | `wiper_motor` | 已实现 | 驱动雨刮 |
| 雨刮片 | Wiper blade | `wiper_blade` | 已实现 | 刮除挡风玻璃水膜 |
| 电动窗电机 | Window motor | `window_motor` | 已实现 | 升降车窗 |
| 中控锁执行器 | Door lock actuator | `door_lock_actuator` | 已实现 | 锁止/解锁车门 |
| 熔断丝盒 | Fuse box | `fuse_box` | 已实现 | 集中保护各电路 |
| 继电器盒 | Relay box | `relay_box` | 已实现 | 集中安装继电器 |

## 15. 排放与其他传感器 / Emissions & Other Sensors

| 中文 | English | 建议 ID | 状态 | 作用 |
| --- | --- | --- | --- | --- |
| 车速传感器 | Vehicle speed sensor (VSS) | `vss` | 已实现 | 车速信号，供仪表和变速器 |
| 加速踏板位置传感器 | APP sensor | `app_sensor` | 已实现 | 电子油门的踏板位置 |
| 空气流量相关真空管 | Vacuum hose | `vacuum_hose` | 已实现 | 真空泄漏会导致怠速高、刹车助力差 |

---

## 整张清单都已实现

起动、充电、着车、冷却、机油压力、进气和排气接进了系统模型。其余零件在 `components/remaining.py` 里按同一套插件生成，用各自的测量读数和故障码区分。

结构上，气缸体和气缸盖不再是焊死的一块：缸盖由四颗螺母拧在双头螺栓上。拧紧才压住缸盖，拧松则缸盖可以离开缸体。以后的零件也按这个方式，用螺栓和螺母搭起来。详见 `docs/architecture.md` 的结构层。

再加零件仍然是：新组件模块（或 `components/remaining.py` 里的一行）+ `data/fault_catalog.yaml` 里的故障条目，并把它放进 `components/__init__.py` 的 `COMPONENT_CLASSES`。需要拆装时，再在 `fasteners/` 里用螺栓和螺母组成装配。
