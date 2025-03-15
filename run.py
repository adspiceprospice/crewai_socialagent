#!/usr/bin/env python
"""
Main script to run the CrewAI Social Media Agent system.
This script starts all components including the web UI, scheduler, and monitor.
"""

import os
import sys
import signal
import atexit
import subprocess
import time
from typing import List
import multiprocessing

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the web UI app factory
from src.web_ui import create_app

# Global list to track all running processes
processes: List[subprocess.Popen] = []

def cleanup():
    """Clean up function to terminate all running processes."""
    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=5)  # Wait for process to terminate
        except Exception as e:
            print(f"Error terminating process: {e}")
            try:
                process.kill()  # Force kill if termination fails
            except Exception as e:
                print(f"Error killing process: {e}")

def signal_handler(signum, frame):
    """Handle termination signals by cleaning up processes."""
    print("\nReceived termination signal. Cleaning up...")
    cleanup()
    sys.exit(0)

def start_process(cmd: List[str], name: str) -> subprocess.Popen:
    """
    Start a new process with the given command.
    
    Args:
        cmd: Command to run as a list of strings
        name: Name of the process for logging
    
    Returns:
        The started process
    """
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        processes.append(process)
        print(f"Started {name} (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"Error starting {name}: {e}")
        return None

def monitor_processes():
    """Monitor running processes and restart them if they crash."""
    restart_delays = {}  # Track restart attempts for each process
    
    while True:
        for process in processes[:]:  # Create a copy of the list to iterate over
            if process.poll() is not None:  # Process has terminated
                cmd = process.args
                cmd_str = " ".join(cmd)
                processes.remove(process)
                
                # Implement exponential backoff for restarts
                if cmd_str in restart_delays:
                    # Increase delay up to a maximum of 60 seconds
                    restart_delays[cmd_str] = min(restart_delays[cmd_str] * 2, 60)
                else:
                    restart_delays[cmd_str] = 1  # Start with 1 second delay
                
                delay = restart_delays[cmd_str]
                print(f"Process {process.pid} terminated. Waiting {delay}s before restarting...")
                
                # Wait before restarting
                time.sleep(delay)
                
                new_process = start_process(cmd, f"Process {cmd}")
                if new_process is None:
                    print(f"Failed to restart process: {cmd}")
        
        # Sleep to avoid high CPU usage
        time.sleep(1)

def run_web_ui():
    """Run the Flask web UI."""
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=False)

def main():
    """Main function to run the entire system."""
    # Register signal handlers and cleanup function
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(cleanup)
    
    try:
        # Verify setup first
        verify_process = subprocess.run(
            [sys.executable, 'verify_setup.py'],
            check=True,
            capture_output=True,
            text=True
        )
        print("Setup verification completed successfully.")
        
        # Start the web UI in a separate process
        web_ui_process = multiprocessing.Process(target=run_web_ui)
        web_ui_process.start()
        print("Web UI started on http://localhost:5001")
        
        # Start the scheduler
        scheduler_process = start_process(
            [sys.executable, 'src/scheduler.py'],
            "Scheduler"
        )
        
        # Start the monitor
        monitor_process = start_process(
            [sys.executable, 'src/monitor.py'],
            "Monitor"
        )
        
        # Monitor processes and restart them if they crash
        monitor_processes()
        
    except subprocess.CalledProcessError as e:
        print(f"Setup verification failed: {e.stdout}\n{e.stderr}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt. Shutting down...")
    except Exception as e:
        print(f"Error running the system: {e}")
    finally:
        cleanup()

if __name__ == '__main__':
    main() 