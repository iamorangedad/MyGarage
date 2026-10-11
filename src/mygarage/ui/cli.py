"""Command-line interface for MyGarage"""

import sys
from pathlib import Path
from typing import Optional

from ..game import MyGarageGame


def print_banner():
    """Print game banner"""
    print("=" * 60)
    print("   MyGarage - 汽车维修模拟器")
    print("   Car Repair Simulator")
    print("=" * 60)
    print()


def print_help():
    """Print help text"""
    print("Available commands:")
    print("  help                    - Show this help")
    print("  new [difficulty]        - Start new case (easy/medium/hard)")
    print("  measure <tool> <target> <measurement> - Use diagnostic tool")
    print("  replace <component> <cost> - Replace a part")
    print("  diagnose <fault_id>     - Submit diagnosis")
    print("  list                    - List all faults (reference)")
    print("  info <fault_id>         - Get fault details (reference)")
    print("  quit                    - Exit")
    print()
    print("Examples:")
    print("  measure multimeter battery resting_voltage")
    print("  measure multimeter battery loaded_voltage")
    print("  measure visual battery general")
    print("  measure crank_test starter attempt_start")
    print("  replace battery 120.00")
    print("  diagnose F001")
    print()


def main():
    """Main CLI entry point"""
    print_banner()
    
    data_dir = Path(__file__).parent.parent.parent.parent / "data"
    
    try:
        game = MyGarageGame(data_dir)
    except Exception as e:
        print(f"Error initializing game: {e}")
        print(f"Make sure fault data exists in: {data_dir / 'faults'}")
        return 1
        
    print("Type 'help' for commands or 'new' to start a case.")
    print()
    
    current_symptoms: Optional[str] = None
    
    while True:
        try:
            command = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break
            
        if not command:
            continue
            
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd in ["quit", "exit", "q"]:
            print("Thanks for playing!")
            break
            
        elif cmd == "help":
            print_help()
            
        elif cmd == "new":
            difficulty = parts[1] if len(parts) > 1 else None
            try:
                symptoms = game.start_new_case(difficulty)
                current_symptoms = symptoms
                print("\n" + "="*60)
                print("NEW CASE")
                print("="*60)
                print(f"Customer complaint: {symptoms}")
                print("="*60)
                print("\nBegin diagnosis. Use 'measure' to investigate.")
                print()
            except Exception as e:
                print(f"Error starting case: {e}")
                
        elif cmd == "measure":
            if len(parts) < 4:
                print("Usage: measure <tool> <target> <measurement>")
                print("Example: measure multimeter battery resting_voltage")
                continue
                
            tool_name = parts[1]
            target = parts[2]
            measurement = parts[3]
            
            result = game.use_tool(tool_name, target, measurement)
            print()
            print(result)
            print()
            
        elif cmd == "replace":
            if len(parts) < 3:
                print("Usage: replace <component> <cost>")
                print("Example: replace battery 120.00")
                continue
                
            component = parts[1]
            try:
                cost = float(parts[2])
            except ValueError:
                print("Cost must be a number")
                continue
                
            result = game.replace_part(component, cost)
            print()
            print(result)
            print()
            
        elif cmd == "diagnose":
            if len(parts) < 2:
                print("Usage: diagnose <fault_id>")
                print("Example: diagnose F001")
                continue
                
            fault_id = parts[1].upper()
            
            try:
                score = game.submit_diagnosis(fault_id)
                print()
                print("="*60)
                print("DIAGNOSIS RESULT")
                print("="*60)
                print(score)
                print("="*60)
                print()
            except Exception as e:
                print(f"Error: {e}")
                
        elif cmd == "list":
            print("\nAvailable faults (for reference):")
            for fault_info in game.list_available_faults():
                print(f"  {fault_info}")
            print()
            
        elif cmd == "info":
            if len(parts) < 2:
                print("Usage: info <fault_id>")
                continue
                
            fault_id = parts[1].upper()
            details = game.get_fault_details(fault_id)
            if details:
                print()
                print(details)
                print()
            else:
                print(f"Fault {fault_id} not found")
                
        else:
            print(f"Unknown command: {cmd}. Type 'help' for commands.")
            
    return 0


if __name__ == "__main__":
    sys.exit(main())
