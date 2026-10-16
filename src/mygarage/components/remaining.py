"""Every catalog part that is not hand-written in its own module.

Each row is a real component: nominal readings, one fault that changes those
readings, and optional parameters the system model already knows how to read
(timing belt, fuel filter, vacuum hose, coolant leaks, and so on).
"""

from typing import Any, Dict, List

from mygarage.component import CatalogPart, FaultMode


def _parse(text: str) -> Any:
    if text == '':
        return ''
    if text == 'true':
        return True
    if text == 'false':
        return False
    try:
        if '.' in text:
            return float(text)
        return int(text)
    except ValueError:
        return text


# id|name|subsystem|cost|reading|nominal|fault|fault_value|finding|symptom|dtc|param|param_nominal|param_fault
_ROWS = """
battery_pos_terminal|蓄电池正极桩头 Positive Terminal|starting|15|voltage_drop_v|0.03|corroded_terminal|3.0|White corrosion on the positive post|Slow crank and a large voltage drop at the positive post||resistance_ohm|0.0002|0.02
battery_neg_terminal|蓄电池负极桩头 Negative Terminal|starting|15|voltage_drop_v|0.02|corroded_terminal|2.8|Powdery corrosion on the negative clamp|Dim lights and a voltage drop on the ground side||resistance_ohm|0.0002|0.018
engine|发动机总成 Engine|engine|3500|compression_psi|170|low_compression|95|Compression is low on multiple cylinders|Long crank and low power||compression_ok|true|false
engine_block|气缸体 Engine Block|engine|1800|crack|none|cracked_block|visible|Coolant weeps from a crack in the block|External coolant leak low on the block|||
cylinder_head|气缸盖 Cylinder Head|engine|900|deck|flat|warped_head|warped|Head deck is warped beyond spec|Overheat history and combustion leakage into the coolant|||
head_gasket|气缸垫 Head Gasket|engine|400|combustion_leak|none|breached_gasket|coolant|Exhaust gas in the coolant and oil looks milky|Overheats and loses coolant with no external puddle||breached|false|true
piston|活塞 Piston|engine|250|skirt|smooth|scuffed_piston|scuffed|Piston skirt is scuffed|Knock when cold|||
piston_rings|活塞环 Piston Rings|engine|180|leakdown_pct|8|worn_rings|45|Leakdown is high and the oil is low|Blue smoke on startup and low compression|||
connecting_rod|连杆 Connecting Rod|engine|220|bearing_clearance_mm|0.04|spun_bearing|0.4|Rod bearing material is in the oil|Deep knock that rises with rpm|||
crankshaft|曲轴 Crankshaft|engine|700|journal|smooth|worn_journal|scored|Crank journal is scored|Low oil pressure at hot idle|||
camshaft|凸轮轴 Camshaft|engine|450|lobe_lift_mm|9.5|worn_lobe|6.0|One cam lobe is worn flat|Misfire on one cylinder and a ticking lifter|||
timing_belt|正时皮带 Timing Belt|engine|280|condition|intact|broken_belt|broken|Belt is off the sprockets|Cranks but will not start||broken|false|true
valve|气门 Valve|engine|40|seat|seated|burnt_valve|burnt|Exhaust valve face is burnt|Popping in the exhaust and low compression on one cylinder|||
valve_stem_seal|气门油封 Valve Stem Seal|engine|60|seal|pliable|hardened_seal|hard|Valve stem seals are hard and cracked|Blue smoke just after idle|||
flywheel|飞轮 Flywheel|engine|320|ring_gear|intact|damaged_ring_gear|missing teeth|Several ring-gear teeth are smashed|Grinds when the starter engages||teeth_ok|true|false
cmp_sensor|凸轮轴位置传感器 CMP Sensor|engine|85|signal|present|no_signal|none|No camshaft-position signal|Cranks but will not start||signal_present|true|false
spark_plug_wire|高压线 Spark Plug Wire|ignition|30|resistance_ohm|8000|open_wire|open|Plug wire is open|Misfire that moves when the wire is moved||open_circuit|false|true
distributor|分电器 Distributor|ignition|140|cap|clean|cracked_cap|carbon track|Carbon track inside the distributor cap|Misfire under load||cracked|false|true
knock_sensor|爆震传感器 Knock Sensor|ignition|75|signal|present|open_sensor|none|Knock sensor circuit is open|Pinging under load and no knock correction|P0325||
fuel_tank|燃油箱 Fuel Tank|fuel|450|leak|none|leaking_tank|weeping|Fuel smell and a wet tank seam|Fuel odor and a puddle under the tank|||
fuel_filter|燃油滤清器 Fuel Filter|fuel|20|flow|normal|clogged_filter|restricted|Filter is dark and restricted|Long crank and low rail pressure||clogged|false|true
fuel_pressure_regulator|燃油压力调节器 Fuel Pressure Regulator|fuel|90|mode|normal|stuck_low|low|Regulator vacuum diaphragm is ruptured|Low rail pressure and fuel in the vacuum hose||mode|normal|low
fuel_rail|油轨 Fuel Rail|fuel|160|leak|none|leaking_rail|wet|Fuel seeps at a rail fitting|Fuel smell in the engine bay|||
fuel_cap|油箱盖 Fuel Cap|fuel|18|seal|tight|loose_cap|loose|Cap clicks but does not seal|EVAP large-leak code after refueling|P0455||
evap_canister|活性炭罐 EVAP Canister|fuel|120|canister|dry|saturated_canister|fuel-logged|Canister is heavy and smells of raw fuel|Fuel smell and rich spikes|P0442||
purge_valve|碳罐电磁阀 Purge Valve|fuel|55|state|closed|stuck_open|open|Purge valve flows when it should be shut|Slightly high idle and a fuel trim shift|P0441|stuck_open|false|true
iac_valve|怠速控制阀 IAC Valve|intake|110|idle_air|normal|stuck_closed|closed|Idle air passage is carboned shut|Idle drops and the engine stalls|P0505|idle_air|normal|low
intake_manifold|进气歧管 Intake Manifold|intake|280|crack|none|cracked_runner|crack|Crack at a runner|Whistle and a lean code on one bank|||
iat_sensor|进气温度传感器 IAT Sensor|intake|35|reported_c|25|biased_hot|80|Sensor reads hot while the intake is cool|Slightly lean calculation and a temperature code|P0113||
tps_sensor|节气门位置传感器 TPS|intake|65|sweep|smooth|dead_spot|drop-out|Voltage drops out partway through the sweep|Hesitation at one throttle angle|P0121||
exhaust_manifold|排气歧管 Exhaust Manifold|exhaust|260|gasket|sealed|cracked_manifold|tick|Tick from a cracked manifold when cold|Exhaust tick and a lean shift at idle|||
muffler|消声器 Muffler|exhaust|180|flow|open|clogged_muffler|restricted|Muffler baffles are collapsed|Loss of power and high exhaust backpressure||clogged|false|true
radiator_cap|散热器盖 Radiator Cap|cooling|15|pressure_hold|ok|failed_cap|will not hold|Cap does not hold pressure|Coolant boils and the upper hose collapses||holds_pressure|true|false
fan_relay|风扇继电器 Fan Relay|cooling|25|contacts|closed|failed_open|open|Relay contacts do not close|Fan never runs and the engine overheats at idle||contacts_ok|true|false
coolant_reservoir|膨胀水箱 Coolant Reservoir|cooling|40|tank|intact|cracked_tank|crack|Crack at the reservoir seam|Coolant level falls with a visible leak||cracked|false|true
heater_core|暖风水箱 Heater Core|cooling|220|core|dry|leaking_core|wet|Sweet smell and a wet passenger carpet|Heater output with coolant inside the car||leaking|false|true
coolant_hose|冷却液软管 Coolant Hose|cooling|30|hose|firm|burst_hose|split|Upper hose is split|Sudden coolant loss and overheat||burst|false|true
oil_pump|机油泵 Oil Pump|lubrication|350|pressure_psi|40|failed_pump|0|Pump relief valve is stuck or the gears are worn|Oil light on as soon as the engine starts||pumping|true|false
oil_filter|机油滤清器 Oil Filter|lubrication|12|bypass|closed|clogged_filter|bypassing|Filter is swollen and the bypass is open|Oil pressure warning after a cold start|||
oil_pan|油底壳 Oil Pan|lubrication|140|level|full|leaking_pan|low|Wet seam at the oil pan|Oil puddle and a low dipstick reading||level|1.0|0.2
oil_pressure_sensor|机油压力传感器 Oil Pressure Sensor|lubrication|25|indicated_psi|40|false_low|0|Gauge reads zero while a mechanical gauge shows pressure|Oil light on but the engine is quiet|P0522||
dipstick|机油尺 Dipstick|lubrication|10|reading|full|blocked_tube|unreadable|Dipstick tube is crushed|Oil level cannot be checked and the tube leaks air|||
clutch_disc|离合器片 Clutch Disc|drivetrain|180|friction|good|slipping_disc|glazed|Disc is glazed and thin|Rpm rises without road speed under load|||
pressure_plate|离合器压盘 Pressure Plate|drivetrain|160|fingers|even|weak_plate|uneven|Pressure-plate fingers are uneven|Clutch slip and a heavy or shuddering pedal|||
release_bearing|分离轴承 Release Bearing|drivetrain|45|noise|quiet|noisy_bearing|growl|Bearing growls with the pedal down|Noise only while the clutch pedal is pressed|||
manual_transmission|手动变速器 Manual Transmission|drivetrain|1400|gears|all|worn_synchro|grinds|Second-gear synchro grinds|Grind going into second|||
automatic_transmission|自动变速器 Automatic Transmission|drivetrain|2200|shift|firm|slipping_clutch|flare|Shift flare between gears|Engine races during a shift|||
torque_converter|变矩器 Torque Converter|drivetrain|450|lockup|holds|shudder|shudder|Lockup clutch shudders|Vibration at steady cruise|P0741||
tcm|变速器控制模块 TCM|drivetrain|500|communication|online|no_communication|offline|No communication with the transmission module|Transmission stays in limp mode|U0101||
shift_solenoid|换挡电磁阀 Shift Solenoid|drivetrain|80|resistance_ohm|12|failed_solenoid|open|Shift solenoid is electrically open|Missing one gear|P0750||
driveshaft|传动轴 Driveshaft|drivetrain|320|ujoint|tight|failed_ujoint|play|U-joint has play and a dry cap|Clunk on takeoff and vibration with speed|||
cv_joint|等速万向节 CV Joint|drivetrain|160|boot|intact|torn_boot|click|Boot is torn and the joint clicks on turns|Clicking while turning under power|||
axle_shaft|半轴 Axle Shaft|drivetrain|210|shaft|straight|twisted_shaft|twisted|Axle shaft is twisted|No drive on one side after a hard launch|||
differential|差速器 Differential|drivetrain|800|noise|quiet|worn_gears|howl|Howl that changes with throttle|Howl on cruise that changes when you lift|||
wheel_bearing|车轮轴承 Wheel Bearing|drivetrain|120|play_mm|0.02|worn_bearing|0.6|Growl that changes when the wheel is steered|Growl that gets louder with speed|||
brake_pedal|制动踏板 Brake Pedal|brakes|40|travel|normal|soft_pedal|sinks|Pedal sinks slowly at a stop|Pedal sinks while holding at a light|||
master_cylinder|制动总泵 Brake Master Cylinder|brakes|160|seals|hold|bypassing_seals|bypass|Fluid bypasses the master-cylinder seals|Pedal sinks with no external leak|||
brake_booster|制动助力器 Brake Booster|brakes|220|vacuum|holds|leaking_booster|leak|Booster does not hold vacuum|Hard pedal and a hiss with the pedal pressed|||
brake_fluid_reservoir|制动液储液罐 Brake Fluid Reservoir|brakes|30|level|full|leaking_reservoir|low|Wet reservoir and a low fluid level|Brake warning light and a low pedal|||
brake_line|制动管路 Brake Line|brakes|50|line|dry|rusted_through|wet|Steel line is rusted through|Pedal goes to the floor and a fluid trail|||
brake_caliper|制动钳 Brake Caliper|brakes|140|piston|free|seized_caliper|seized|Caliper piston is seized|Car pulls and that wheel runs hot|||
brake_drum|制动鼓 Brake Drum|brakes|90|surface|smooth|scored_drum|scored|Drum surface is deeply scored|Grab or pulsation from the rear brakes|||
brake_shoes|制动蹄 Brake Shoes|brakes|70|lining_mm|5.0|worn_shoes|1.0|Shoe lining is at the rivets|Rear brake noise and a long pedal|||
wheel_cylinder|轮缸 Wheel Cylinder|brakes|35|seal|dry|leaking_cylinder|wet|Wheel cylinder is wet behind the drum|Pull to one side and fluid on the shoes|||
abs_module|ABS 控制模块 ABS Module|brakes|600|communication|online|internal_fault|offline|ABS module reports an internal fault|ABS light stays on|C1095||
brake_switch|制动灯开关 Brake Light Switch|brakes|20|signal|tracks pedal|failed_switch|always open|Brake lights stay off when the pedal is pressed|No brake lights and cruise will not set|||
steering_wheel|方向盘 Steering Wheel|steering|150|clockspring|intact|broken_clockspring|open|Clockspring is open|Horn and airbag light after the wheel is turned|B1000||
steering_column|转向柱 Steering Column|steering|400|ujoint|tight|loose_ujoint|play|Column U-joint is loose|Clunk in the column over bumps|||
steering_rack|转向机 Steering Rack|steering|550|boots|dry|leaking_rack|wet|Rack boot is full of fluid|Heavy steering and a wet subframe|||
power_steering_pump|转向助力泵 Power Steering Pump|steering|210|pressure|normal|failed_pump|low|Pump whines and pressure is low|Heavy steering and a whine at full lock|||
eps_module|电动助力模块 EPS Module|steering|700|assist|normal|no_assist|none|Electric power steering is offline|Steering is suddenly heavy|C1511||
tie_rod|横拉杆 Tie Rod|steering|45|play_mm|0.1|worn_tie_rod|3.0|Inner or outer tie rod has play|Wandering and tire wear on the edges|||
steering_knuckle|转向节 Steering Knuckle|steering|180|bend|none|bent_knuckle|bent|Knuckle is bent|Steering wheel off center after an impact|||
coil_spring|螺旋弹簧 Coil Spring|suspension|120|height_mm|equal|sagged_spring|low|One spring has sagged|Car sits low at one corner|||
control_arm|控制臂 Control Arm|suspension|140|bushings|tight|bent_arm|bent|Control arm is bent|Pull and an alignment that will not hold|||
ball_joint|球头 Ball Joint|suspension|55|play_mm|0.05|worn_joint|2.5|Ball joint has vertical play|Clunk over bumps and uneven tire wear|||
sway_bar|稳定杆 Sway Bar|suspension|160|bar|mounted|broken_bar|broken|Sway bar is broken at a bend|Body rolls more in corners|||
sway_bar_link|稳定杆连杆 Sway Bar Link|suspension|25|link|tight|broken_link|separated|Link is separated|Rattle over small bumps|||
suspension_bushing|衬套 Suspension Bushing|suspension|30|rubber|intact|torn_bushing|torn|Bushing is torn|Clunk on takeoff and a shifted wheel|||
strut|麦弗逊支柱 Strut|suspension|180|damping|firm|blown_strut|oil-soaked|Strut cartridge is oil-soaked|Bounce and a knock at that corner|||
tire|轮胎 Tire|wheels|140|pressure_psi|34|punctured|12|Nail in the tread|Pull and a low-pressure warning|||
wheel_rim|轮辋 Wheel Rim|wheels|160|bead|seated|bent_rim|bent|Rim is bent at the bead|Vibration and a slow leak|||
tire_valve|气门嘴 Tire Valve|wheels|8|core|seals|leaking_core|leak|Valve core leaks|Slow leak at the valve stem|||
tpms_sensor|胎压传感器 TPMS Sensor|wheels|45|signal|present|dead_battery|none|Sensor battery is dead|TPMS light with one sensor missing|C0750||
ac_compressor|空调压缩机 A/C Compressor|hvac|420|pump|pumps|seized_compressor|locked|Compressor shaft will not turn|Belt scream and no cold air|||
ac_clutch|压缩机离合器 A/C Clutch|hvac|90|gap_mm|0.4|open_coil|no engage|Clutch coil is open|Compressor never engages|P0645||
condenser|冷凝器 Condenser|hvac|180|fins|clear|blocked_condenser|matted|Fins are packed with debris|High discharge pressure and warm air|||
expansion_valve|膨胀阀 Expansion Valve|hvac|70|orifice|meters|stuck_closed|closed|Expansion valve is stuck closed|Low side in a vacuum and no cooling|||
evaporator|蒸发器 Evaporator|hvac|300|core|dry|leaking_evaporator|oily|Oily dust at the evaporator case|Sweet chemical smell and no cold air|||
blower_motor|鼓风机 Blower Motor|hvac|110|speed|varies|seized_blower|no spin|Blower wheel does not turn|No airflow at any speed|||
blower_resistor|鼓风机电阻 Blower Resistor|hvac|35|speeds|all|open_resistor|high only|Resistor is open|Only the highest fan speed works|||
ac_pressure_switch|空调压力开关 A/C Pressure Switch|hvac|40|circuit|closed|failed_open|open|Pressure switch is open with a full charge|Compressor will not engage even though the charge is correct|||
ecu|发动机控制单元 ECU|electrical|800|communication|online|failed_driver|offline|ECU injector driver has failed|No start or a dead cylinder with power and grounds good|P0601||
bcm|车身控制模块 BCM|electrical|450|communication|online|no_communication|offline|No communication with the body module|Lights locks and wipers act on their own|U0140||
instrument_cluster|仪表板 Instrument Cluster|electrical|350|gauges|track|dead_cluster|dark|Cluster has no power or no network|No gauges and no warning lamps|U0155||
obd_port|OBD 诊断接口 OBD Port|electrical|25|pin16_v|12.4|no_power|0|Pin 16 has no battery voltage|Scan tool will not power up|||
headlight|前大灯 Headlight|electrical|40|beam|bright|failed_bulb|out|Low-beam bulb is open|One headlight is out|||
tail_light|尾灯 Tail Light|electrical|20|lamp|on|failed_bulb|out|Tail or brake filament is open|One side stays dark|||
turn_signal|转向灯 Turn Signal|electrical|15|lamp|flashes|failed_bulb|out|One corner does not flash|Fast flash on that side|||
flasher_relay|闪光继电器 Flasher Relay|electrical|18|relay|clicks|failed_flasher|dead|Flasher does not click|No turn signals on either side|||
horn|喇叭 Horn|electrical|25|sound|loud|failed_horn|silent|Horn element is open|No horn with the relay clicking|||
horn_relay|喇叭继电器 Horn Relay|electrical|15|contacts|close|failed_relay|open|Horn relay does not close|No horn and no click|||
wiper_motor|雨刮电机 Wiper Motor|electrical|120|park|parks|seized_motor|stuck|Motor does not move|Wipers dead in every position|||
wiper_blade|雨刮片 Wiper Blade|electrical|20|edge|sharp|torn_blade|streaks|Blade edge is torn|Streaks across the glass|||
window_motor|电动窗电机 Window Motor|electrical|90|travel|smooth|failed_motor|dead|Motor draws nothing|One window does not move|||
door_lock_actuator|门锁执行器 Door Lock Actuator|electrical|55|action|locks|stripped_actuator|free|Actuator motor runs but the lock does not move|One door will not lock|||
fuse_box|熔断丝盒 Fuse Box|electrical|80|power|present|corroded_bus|voltage drop|Bus bar is corroded|Several circuits drop out together|||
relay_box|继电器盒 Relay Box|electrical|70|sockets|tight|melted_socket|melted|One relay socket is melted|That relay loses power when warm|||
vss|车速传感器 Vehicle Speed Sensor|electrical|60|signal|tracks speed|no_signal|none|No vehicle-speed signal|Speedometer stays at zero|P0500||
app_sensor|加速踏板位置传感器 APP Sensor|electrical|140|tracks|agree|mismatch|disagree|The two pedal tracks do not agree|Throttle is forced to idle|P2138||
vacuum_hose|真空管 Vacuum Hose|intake|12|hose|sealed|split_hose|split|Vacuum hose is split|High idle and a hiss under the hood||leak|false|true
""".strip().splitlines()


def _class_name(component_id: str) -> str:
    return ''.join(part.capitalize() for part in component_id.split('_'))


def _specs() -> List[Dict[str, Any]]:
    specs = []
    for line in _ROWS:
        fields = line.split('|')
        if len(fields) == 13:
            fields.append('')
        (
            component_id, name, subsystem, cost, reading, nominal, fault_name,
            fault_value, finding, symptom, dtc, param, param_nominal, param_fault,
        ) = fields
        nominal_value = _parse(nominal)
        fault_reading = _parse(fault_value)
        params = {}
        fault_params = {}
        if param:
            params[param] = _parse(param_nominal)
            fault_params[param] = _parse(param_fault)
        if component_id == 'fuel_filter':
            params['restricted_pressure_psi'] = 12.0
        specs.append({
            'id': component_id,
            'name': name,
            'subsystem': subsystem,
            'cost': float(cost),
            'reading': reading,
            'nominal': nominal_value,
            'fault_name': fault_name,
            'fault_value': fault_reading,
            'finding': finding,
            'symptom': symptom,
            'dtc': dtc,
            'params': params,
            'fault_params': fault_params,
        })
    return specs


def iter_catalog_faults():
    """Yield fault-catalog dicts for every generated part."""
    for spec in _specs():
        yield {
            'component_id': spec['id'],
            'fault_name': spec['fault_name'],
            'description': spec['finding'],
            'root_cause': spec['symptom'],
            'symptoms': [spec['symptom']],
            'dtc': spec['dtc'],
        }


def _build(spec: Dict[str, Any]) -> type:
    reading = spec['reading']
    nominal_value = spec['nominal']
    fault_value = spec['fault_value']
    params = dict(spec['params'])
    fault_params = dict(spec['fault_params'])
    finding = spec['finding']
    dtc = [spec['dtc']] if spec['dtc'] else []
    cost = spec['cost']
    fault_name = spec['fault_name']
    symptom = spec['symptom']
    title = spec['name']
    component_id = spec['id']

    class Part(CatalogPart):
        subsystem = spec['subsystem']

        def __init__(self, component_id: str = component_id):
            super().__init__(component_id, title, component_id + '.xml')

        def get_nominal_parameters(self) -> Dict[str, Any]:
            nominal = {
                'visual_findings': ['Appears serviceable'],
                'active_dtcs': [],
                'readings': {reading: nominal_value},
                'replacement_cost': cost,
            }
            nominal.update(params)
            return nominal

        def _define_fault_modes(self) -> None:
            affected = {
                'visual_findings': [finding],
                'active_dtcs': list(dtc),
                'readings': {reading: fault_value},
            }
            affected.update(fault_params)
            self.fault_modes = [
                FaultMode(
                    name=fault_name,
                    description=finding,
                    symptoms=[symptom],
                    affected_parameters=affected,
                )
            ]

        def get_diagnostic_readings(self, tool: str, context: Dict[str, Any]) -> Dict[str, Any]:
            if tool in ('visual', 'measure'):
                payload = {'findings': list(self.parameters.get('visual_findings', []))}
                payload.update(self.parameters.get('readings', {}))
                return payload
            return super().get_diagnostic_readings(tool, context)

    Part.__name__ = _class_name(component_id)
    Part.__qualname__ = Part.__name__
    return Part


def remaining_classes() -> List[type]:
    """One component class per remaining catalog row."""
    return [_build(spec) for spec in _specs()]
