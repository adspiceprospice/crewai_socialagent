#!/usr/bin/env python
"""
Run the CrewAI Social Media Agent system.
This script starts all components of the system: web UI, scheduler, and monitor.
"""

import os
import sys
import subprocess
import time
import signal
import atexit

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Global list to keep track of all processes
processes = []

def start_process(script_path, name):
    """Start a subprocess and add it to the global processes list."""
    print(f"Starting {name}...")
    process = subprocess.Popen([sys.executable, script_path])
    processes.append((process, name))
    return process

def cleanup():
    """Terminate all running processes."""
    print("\nShutting down all processes...")
    for process, name in processes:
        print(f"Terminating {name}...")
        process.terminate()
    
    # Wait for all processes to terminate
    for process, name in processes:
        try:
            process.wait(timeout=5)
            print(f"{name} terminated successfully.")
        except subprocess.TimeoutExpired:
            print(f"{name} did not terminate gracefully, killing...")
            process.kill()

def signal_handler(sig, frame):
    """Handle termination signals."""
    print("\nReceived termination signal.")
    cleanup()
    sys.exit(0)

def main():
    """Run the entire social media agent system."""
    # Register cleanup function and signal handlers
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🚀 Starting CrewAI Social Media Agent system...")
    
    # First, verify the setup
    print("\n🔍 Verifying setup...")
    verify_result = subprocess.run([sys.executable, "verify_setup.py"], capture_output=True, text=True)
    if "All checks passed!" not in verify_result.stdout:
        print("\n❌ Setup verification failed. Please fix the issues before continuing.")
        print(verify_result.stdout)
        return
    
    # Start the web UI
    web_ui_process = start_process("web_ui.py", "Web UI")
    print("✅ Web UI started at http://localhost:5000")
    
    # Start the scheduler
    scheduler_process = start_process("src/scheduler.py", "Scheduler")
    print("✅ Scheduler started")
    
    # Start the monitor
    monitor_process = start_process("src/monitor.py", "Monitor")
    print("✅ Monitor started")
    
    print("\n🎉 All systems are running!")
    print("Access the web interface at: http://localhost:5000")
    print("Press Ctrl+C to stop all processes.")
    
    # Keep the main process running
    try:
        while True:
            # Check if any process has terminated unexpectedly
            for i, (process, name) in enumerate(processes):
                if process.poll() is not None:
                    print(f"\n⚠️ {name} has terminated unexpectedly (exit code: {process.returncode}).")
                    print(f"Restarting {name}...")
                    
                    # Determine which script to restart
                    script_path = "web_ui.py" if name == "Web UI" else f"src/{name.lower()}.py"
                    
                    # Restart the process
                    new_process = start_process(script_path, name)
                    
                    # Replace the old process in the list
                    processes[i] = (new_process, name)
            
            # Sleep to avoid high CPU usage
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt.")
        cleanup()

if __name__ == "__main__":
    main() 