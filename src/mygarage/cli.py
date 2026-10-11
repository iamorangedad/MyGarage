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
    print("  2. Measure voltage (resting)")
    print("  3. Measure voltage (while cranking)")
    print("  4. Battery load test")
    print("  5. Crank test")
    print("  6. Replace part")
    print("  7. Submit diagnosis")
    print("  9. Show components")
    print("  0. Quit")
    print()


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
            # Visual inspection
            comp = input("Component to inspect (battery_12v/starter_motor): ").strip()
            result = game.perform_diagnostic('visual', comp)
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                print(f"\nVisual Inspection of {comp}:")
                for finding in result['readings'].get('findings', []):
                    print(f"  - {finding}")
        
        elif choice == '2':
            # Voltage measurement (resting)
            comp = input("Component (battery_12v): ").strip() or "battery_12v"
            result = game.perform_diagnostic('multimeter', comp)
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                readings = result['readings']
                print(f"\nVoltage Measurement ({readings.get('test_condition')}):")
                print(f"  {readings.get('voltage')} {readings.get('unit')}")
        
        elif choice == '3':
            # Voltage measurement (cranking)
            comp = input("Component (battery_12v): ").strip() or "battery_12v"
            result = game.diagnostic_tools.measure_voltage(comp, cranking=True)
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                readings = result['readings']
                crank_info = result.get('crank_info', {})
                print(f"\nVoltage Measurement (cranking):")
                print(f"  {readings.get('voltage')} {readings.get('unit')}")
                if crank_info:
                    print(f"  Crank sound: {crank_info.get('sound')}")
                    print(f"  RPM: {crank_info.get('rpm', 0)}")
        
        elif choice == '4':
            # Load test
            result = game.perform_diagnostic('load_test', 'battery_12v')
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                readings = result['readings']
                print(f"\nBattery Load Test:")
                print(f"  Voltage before: {readings.get('voltage_before')} V")
                print(f"  Voltage during load: {readings.get('voltage_during_load')} V")
                print(f"  Voltage drop: {readings.get('voltage_drop')} V")
                print(f"  Estimated CCA: {readings.get('estimated_cca')}")
                print(f"  Result: {'PASS' if readings.get('passed') else 'FAIL'}")
        
        elif choice == '5':
            # Crank test
            result = game.perform_diagnostic('crank_test', 'starter_motor')
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                readings = result['readings']
                print(f"\nCrank Test:")
                print(f"  Cranked: {readings.get('cranked')}")
                print(f"  Sound: {readings.get('sound')}")
                print(f"  Description: {readings.get('description')}")
                if 'rpm' in readings:
                    print(f"  RPM: {readings.get('rpm')}")
        
        elif choice == '6':
            # Replace part
            comp = input("Component to replace (battery_12v/starter_motor): ").strip()
            result = game.replace_part(comp)
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                print(f"\nReplaced {comp}")
                print(f"Cost: ${result['cost']:.2f}")
                print(f"Total parts replaced: {result['total_parts_replaced']}")
        
        elif choice == '7':
            # Submit diagnosis
            print("\nSubmit your diagnosis:")
            comp = input("Faulty component ID: ").strip()
            fault = input("Fault name: ").strip()
            
            result = game.submit_diagnosis(comp, fault)
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                print(result['score_summary'])
                
                # Show correct answer
                diagnosis = result['diagnosis']
                print(f"\n{diagnosis['message']}")
                
                break
        
        elif choice == '9':
            # Show components
            print("\nAvailable Components:")
            for comp in game.get_available_components():
                print(f"  - {comp['id']}: {comp['name']} ({comp['type']})")
        
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
