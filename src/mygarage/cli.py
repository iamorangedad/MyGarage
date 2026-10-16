"""Command-line interface for MyGarage."""

import sys
import argparse
from typing import Optional
from mygarage.game import Game


def print_header():
    """Print game header."""
    print("\n" + "="*60)
    print("MyGarage - Car Diagnosis Simulator".center(60))
    print("="*60 + "\n")


def print_menu():
    """Print diagnostic menu."""
    print("\nAvailable Actions:")
    print("  1. Visual inspection")
    print("  2. Multimeter (key as it is)")
    print("  3. Multimeter while cranking")
    print("  4. Battery load test")
    print("  5. Crank and try to start")
    print("  6. OBD scan")
    print("  7. Fuel pressure (turns key to RUN)")
    print("  8. Temperature")
    print("  9. Voltage drop while cranking")
    print("  10. Spark test")
    print("  11. Bounce test")
    print("  12. Key off / key run")
    print("  13. Replace part")
    print("  14. Submit diagnosis")
    print("  15. Show components")
    print("  16. Service manual (fault names for a part)")
    print("  0. Quit")
    print()


def format_readings(readings: dict) -> str:
    """Render a tool payload without knowing which tool produced it."""
    lines = []
    for key, value in readings.items():
        if isinstance(value, list):
            lines.append(f"  {key}:")
            for item in value:
                lines.append(f"    - {item}")
        else:
            lines.append(f"  {key}: {value}")
    return "\n".join(lines)


def prompt_component(game: Game, label: str) -> str:
    """Ask for a component id. An empty answer prints the catalog."""
    comp = input(f"{label}: ").strip()
    if not comp:
        print_components(game)
    return comp


def print_components(game: Game):
    """Print parts grouped by subsystem."""
    grouped = {}
    for comp in game.get_available_components():
        grouped.setdefault(comp.get('subsystem') or 'other', []).append(comp)
    print("\nComponents:")
    for subsystem, parts in grouped.items():
        print(f"  [{subsystem}]")
        for comp in parts:
            print(f"    {comp['id']}: {comp['name']}")


def show_result(result: dict):
    """Print a diagnostic result or its error."""
    if 'error' in result and 'readings' not in result:
        print(f"Error: {result['error']}")
        return
    readings = result.get('readings', {})
    if isinstance(readings, dict) and 'error' in readings and len(readings) == 1:
        print(f"Error: {readings['error']}")
        return
    print(format_readings(readings))


def interactive_mode(game: Game):
    """Run the game in interactive mode."""
    print_header()
    
    # Start a new scenario
    result = game.start_new_scenario()
    if not result['success']:
        print(f"Error: {result.get('error')}")
        return
    
    print(result['complaint'])
    print(f"\nDifficulty: {result['difficulty']}")
    print("\nYour task: Diagnose the problem and identify the faulty component.")
    
    while game.active_scenario:
        print_menu()
        choice = input("Choose action: ").strip()
        
        if choice == '0':
            print("Exiting without diagnosis...")
            break

        elif choice == '1':
            comp = prompt_component(game, "Component to inspect")
            if comp:
                print(f"\nVisual inspection of {comp}:")
                show_result(game.perform_diagnostic('visual', comp))

        elif choice == '2':
            comp = prompt_component(game, "Component to measure")
            if comp:
                print(f"\nMultimeter on {comp}:")
                show_result(game.perform_diagnostic('multimeter', comp))

        elif choice == '3':
            comp = prompt_component(game, "Component to measure while cranking")
            if comp:
                print(f"\nMultimeter on {comp} while cranking:")
                show_result(game.diagnostic_tools.measure_voltage(comp, cranking=True))

        elif choice == '4':
            print("\nBattery load test:")
            show_result(game.perform_diagnostic('load_test', 'battery_12v'))

        elif choice == '5':
            print("\nCrank and start attempt:")
            show_result(game.perform_diagnostic('crank_test', 'starter_motor'))

        elif choice == '6':
            print("\nOBD scan:")
            show_result(game.perform_diagnostic('obd', 'all'))

        elif choice == '7':
            game.set_ignition('run')
            print("\nFuel pressure with the key in RUN:")
            show_result(game.perform_diagnostic('fuel_pressure', 'fuel_pump'))

        elif choice == '8':
            comp = prompt_component(game, "Component (thermostat, ect_sensor, radiator, ...)")
            if comp:
                print(f"\nTemperature at {comp}:")
                show_result(game.perform_diagnostic('temperature', comp))

        elif choice == '9':
            comp = input("Connection to measure [ground_strap]: ").strip() or "ground_strap"
            print(f"\nVoltage drop across {comp}:")
            show_result(game.diagnostic_tools.measure_voltage(comp, cranking=True))

        elif choice == '10':
            comp = prompt_component(game, "Component (ignition_coil or spark_plug)")
            if comp:
                print(f"\nSpark test on {comp}:")
                show_result(game.perform_diagnostic('spark_test', comp))

        elif choice == '11':
            print("\nBounce test:")
            show_result(game.perform_diagnostic('bounce_test', 'shock_absorber'))

        elif choice == '12':
            position = input("Position (off/run): ").strip() or "run"
            result = game.set_ignition(position)
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                print(
                    f"Key is {result['ignition_position']}. "
                    f"Engine running: {result['engine_running']}. "
                    f"Charging voltage: {result['charging_voltage']} V"
                )

        elif choice == '13':
            comp = prompt_component(game, "Component to replace")
            if comp:
                result = game.replace_part(comp)
                if 'error' in result:
                    print(f"Error: {result['error']}")
                else:
                    print(f"\nReplaced {comp}")
                    print(f"Cost: ${result['cost']:.2f}")
                    print(f"Total parts replaced: {result['total_parts_replaced']}")

        elif choice == '14':
            print("\nSubmit your diagnosis:")
            comp = input("Faulty component ID: ").strip()
            fault = input("Fault name: ").strip()
            result = game.submit_diagnosis(comp, fault)
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                print(result['score_summary'])
                print(f"\n{result['diagnosis']['message']}")
                break

        elif choice == '15':
            print_components(game)

        elif choice == '16':
            comp = prompt_component(game, "Component ID")
            if comp:
                manual = game.get_fault_modes(comp)
                if 'error' in manual:
                    print(f"Error: {manual['error']}")
                else:
                    print(f"\nKnown faults for {comp}:")
                    for fault in manual['faults']:
                        print(f"  - {fault['name']}: {fault['description']}")

        else:
            print("Invalid choice. Try again.")
    
    game.close()


def demo_mode(game: Game):
    """Run a quick demonstration of the game."""
    print_header()
    print("DEMO MODE - Automated gameplay demonstration\n")
    
    # Start scenario
    result = game.start_new_scenario()
    print(f"Scenario: {result['complaint']}")
    
    # Get fault info (cheating for demo purposes)
    fault_info = game.fault_engine.get_active_fault_info()
    print(f"\n[DEBUG] Actual fault: {fault_info['component_id']} - {fault_info['fault_name']}")
    
    # Run some diagnostics
    print("\n--- Running diagnostics ---")
    
    print("\n1. Visual inspection of battery:")
    result = game.perform_diagnostic('visual', 'battery_12v')
    for finding in result['readings'].get('findings', []):
        print(f"   {finding}")
    
    print("\n2. Battery voltage (resting):")
    result = game.perform_diagnostic('multimeter', 'battery_12v')
    print(f"   {result['readings']['voltage']} V")
    
    print("\n3. Crank test:")
    result = game.perform_diagnostic('crank_test', 'starter_motor')
    print(f"   {result['readings']['description']}")
    
    # Submit correct diagnosis
    print("\n--- Submitting diagnosis ---")
    result = game.submit_diagnosis(fault_info['component_id'], fault_info['fault_name'])
    print(result['score_summary'])
    
    game.close()


def headless_test(game: Game):
    """Run headless test to verify functionality."""
    print("Running headless test...")
    
    # Test scenario creation
    result = game.start_new_scenario()
    assert result['success'], "Failed to start scenario"
    print("✓ Scenario started")
    
    # Test diagnostics
    result = game.perform_diagnostic('visual', 'battery_12v')
    assert 'error' not in result, "Visual inspection failed"
    print("✓ Visual inspection works")
    
    result = game.perform_diagnostic('multimeter', 'battery_12v')
    assert 'error' not in result, "Multimeter failed"
    print("✓ Multimeter works")
    
    # Test simulation stepping
    if game.simulation and game.simulation.is_loaded():
        game.step_simulation(10)
        print("✓ MuJoCo simulation stepping works")
    else:
        print("⚠ MuJoCo simulation not available")
    
    # Test diagnosis submission
    fault_info = game.fault_engine.get_active_fault_info()
    result = game.submit_diagnosis(fault_info['component_id'], fault_info['fault_name'])
    assert result['diagnosis']['correct'], "Diagnosis check failed"
    print("✓ Diagnosis submission works")
    
    print("\nAll tests passed! ✓")
    game.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="MyGarage - Car Diagnosis Simulator"
    )
    parser.add_argument(
        '--mode',
        choices=['interactive', 'demo', 'test'],
        default='interactive',
        help='Game mode (default: interactive)'
    )
    parser.add_argument(
        '--difficulty',
        choices=['easy', 'medium', 'hard'],
        help='Difficulty level'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        default=True,
        help='Run in headless mode (no 3D viewer)'
    )
    
    args = parser.parse_args()
    
    try:
        game = Game(headless=args.headless, difficulty=args.difficulty)
        
        if args.mode == 'interactive':
            interactive_mode(game)
        elif args.mode == 'demo':
            demo_mode(game)
        elif args.mode == 'test':
            headless_test(game)
            
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
