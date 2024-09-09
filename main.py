import time
import psutil
import os
import threading
import platform
import socket
import sys
import hashlib

iterations = 6500


current_iteration = 0
stop_loading = False
commands = {"show_all": True}

def parse_args():
    global commands
    args = sys.argv[1:]
    for arg in args:
        if arg.startswith("--omit="):
            omit_sections = arg.split("=")[1].split(",")
            for section in omit_sections:
                commands[section.strip()] = False
        if arg.startswith("--iterations="):
            global iterations
            iterations = int(arg.split("=")[1])
    if "show_all" in commands:
        commands = {key: False for key in commands}
        commands["show_all"] = True

def simulate_hash_work(intensity="high"):
    """
    Simulates hash work by performing multiple hash calculations on the same data based on the specified intensity.

    Args:
        intensity (str): Can be 'low', 'medium', or 'high'. Determines the number of iterations and the level of hashing.
                         'low' = fewer iterations (e.g., simpler chains like Litecoin)
                         'medium' = standard iterations (e.g., Ethereum)
                         'high' = higher iterations (e.g., Bitcoin)
    """
    # Generate random data for hashing
    data = os.urandom(64)

    # Set the number of iterations based on the specified intensity
    if intensity == "low":       # Simulate a simpler blockchain (Litecoin-like)
        iterations = 100
    elif intensity == "high":    # Simulate a complex blockchain (Bitcoin-like)
        iterations = 10000
    else:                        # Default to medium complexity (Ethereum-like)
        iterations = 1000

    # Perform a variety of hash algorithms for diversity in complexity
    for _ in range(iterations):
        # Apply a mix of hashing algorithms
        data = hashlib.sha256(data).digest()  # SHA-256, typical for Bitcoin
        data = hashlib.md5(data).digest()     # MD5, faster and less secure
        data = hashlib.sha1(data).digest()    # SHA-1 for an additional round
        data = hashlib.blake2b(data).digest() # Blake2b for variety
        data = hashlib.sha3_256(data).digest()# SHA-3 variant

    return data

def safe_call(func, default="Permission Denied"):
    try:
        return func()
    except (PermissionError, RuntimeError, AttributeError):
        return default

def print_progress_bar(iteration, total, length=40):
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    print(f'\rProgress: |{bar}| {percent}% Complete', end='\r')
    if iteration == total:
        print()

def hash_rate_test(iterations):
    global current_iteration
    print(f"Running hash rate test with {iterations} iterations...please wait")

    start_time = time.time()
    memory_before = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # in MB

    hash_times = []
    for i in range(iterations):
        start_hash_time = time.time()
        simulate_hash_work()
        end_hash_time = time.time()
        hash_times.append(end_hash_time - start_hash_time)
        current_iteration = i + 1

    end_time = time.time()
    memory_after = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # in MB

    total_time_taken = end_time - start_time
    hash_rate = iterations / total_time_taken
    average_time_per_hash = total_time_taken / iterations
    min_time_per_hash = min(hash_times)
    max_time_per_hash = max(hash_times)
    average_hash_time = sum(hash_times) / len(hash_times)

    # Display collected information
    if commands.get("time", True):
        print(f"\nTotal time taken: {total_time_taken:.6f} seconds")
        print(f"Hash rate: {hash_rate:.2f} hashes/second")
        print(f"Average time per hash: {average_time_per_hash:.10f} seconds")
        print(f"Min time for a single hash: {min_time_per_hash:.10f} seconds")
        print(f"Max time for a single hash: {max_time_per_hash:.10f} seconds")
        print(f"Average hash time: {average_hash_time:.10f} seconds")

    # Additional information with error handling
    cpu_usage = safe_call(lambda: f"{psutil.cpu_percent(interval=1)}%")
    disk_usage = safe_call(lambda: f"{psutil.disk_usage('/').percent}% used, {psutil.disk_usage('/').free / 1024 / 1024:.2f} MB free")
    network_io = safe_call(lambda: f"Sent = {psutil.net_io_counters().bytes_sent / 1024 / 1024:.2f} MB, Received = {psutil.net_io_counters().bytes_recv / 1024 / 1024:.2f} MB")
    swap_memory = safe_call(lambda: f"{psutil.swap_memory().percent}% used, {psutil.swap_memory().free / 1024 / 1024:.2f} MB free")
    cpu_temp = safe_call(lambda: psutil.sensors_temperatures()['coretemp'][0].current if 'coretemp' in psutil.sensors_temperatures() else 'N/A')
    uptime = safe_call(lambda: time.time() - psutil.boot_time())
    processes = len(psutil.pids())
    load_avg = safe_call(lambda: os.getloadavg() if hasattr(os, 'getloadavg') else "Not available")
    fs_type = safe_call(lambda: [partition.fstype for partition in psutil.disk_partitions()])
    total_threads = sum(p.num_threads() for p in psutil.process_iter())
    context_switches = safe_call(lambda: psutil.cpu_stats().ctx_switches)
    interrupts = safe_call(lambda: psutil.cpu_stats().interrupts)
    boot_time = safe_call(lambda: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(psutil.boot_time())))
    hostname = socket.gethostname()

    # Display additional information
    additional_info = [
        f"CPU Usage: {cpu_usage}",
        f"Disk Usage: {disk_usage}",
        f"Network I/O: {network_io}",
        f"Swap Memory: {swap_memory}",
        f"CPU Temperature: {cpu_temp} °C",
        f"System Uptime: {uptime if isinstance(uptime, str) else f'{uptime / 3600:.2f} hours'}",
        f"Number of Processes: {processes}",
        f"Load Average: {load_avg}",
        f"Filesystem Type: {fs_type}",
        f"Total Number of Threads: {total_threads}",
        f"Context Switches: {context_switches}",
        f"Interrupts: {interrupts}",
        f"Boot Time: {boot_time}",
        f"Hostname: {hostname}",
    ]

    # Clear console
    print("\n" * 10)

    # Print final organized log
    print(f"Running hash rate test with {iterations} iterations...")
    print(f"Iterations: {iterations}")
    print(f"Number of threads used: {os.cpu_count()}")
    print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
    print(f"End time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
    if commands.get("time", True):
        print(f"Total time taken: {total_time_taken:.6f} seconds")
        print(f"Hash rate: {hash_rate:.2f} hashes/second")
        print(f"Average time per hash: {average_time_per_hash:.10f} seconds")
        print(f"Min time for a single hash: {min_time_per_hash:.10f} seconds")
        print(f"Max time for a single hash: {max_time_per_hash:.10f} seconds")
        print(f"Average hash time: {average_hash_time:.10f} seconds")
    if commands.get("memory", True):
        print("\nMemory Usage:")
        print(f"Memory usage before test: {memory_before:.2f} MB")
        print(f"Memory usage after test: {memory_after:.2f} MB")
    if commands.get("system_info", True):
        print("\nSystem Information:")
        print(f"Platform: {platform.system()}")
        print(f"Release: {platform.release()}")
        print(f"Version: {platform.version()}")
        print(f"Machine: {platform.machine()}")
        print(f"Processor: {platform.processor()}")
        print(f"CPU Count: {os.cpu_count()} logical cores")
        print(f"Physical Memory: {psutil.virtual_memory().total / 1024 / 1024:.2f} MB")
        print(f"Python version: {platform.python_version()}")
    if commands.get("additional_info", True):
        print("\nAdditional Information:")
        for info in additional_info:
            print(info)

def loading_animation():
    frames = [
        "[      ]", "[*     ]", "[**    ]", "[***   ]", "[****  ]", "[***** ]", "[******]",
        "[ **** ]", "[  **  ]", "[      ]", "[  **  ]", "[ **** ]", "[******]",
        "[***** ]", "[****  ]", "[***   ]", "[**    ]", "[*     ]", "[      ]",
        "[     *]", "[    **]", "[   ***]", "[  ****]", "[ *****]", "[******]",
        "[ **** ]", "[  **  ]", "[      ]", "[  **  ]", "[ **** ]", "[******]",
        "[***** ]", "[****  ]", "[***   ]", "[**    ]", "[*     ]", "[      ]"
    ]
    while not stop_loading:
        for frame in frames:
            if stop_loading:
                break
            print(frame, end="\r")
            time.sleep(0.1)

def update_progress_bar():
    while not stop_loading:
        print_progress_bar(current_iteration, iterations)
        time.sleep(0.2)

if __name__ == "__main__":
    parse_args()
    
    # Create and start loading thread
    loading_thread = threading.Thread(target=loading_animation)
    progress_thread = threading.Thread(target=update_progress_bar)

    loading_thread.start()
    progress_thread.start()

    # Run the hash rate test while the loading animation is displayed
    try:
        hash_rate_test(iterations)
    finally:
        stop_loading = True

    # Wait for loading and progress threads to complete
    loading_thread.join()
    progress_thread.join()

p
