import time
import psutil
import os
import threading
import platform
import socket

iterations = 420000
current_iteration = 0
stop_loading = False

def simulate_hash_work():
    time.sleep(0.000001)  # Simulate hash calculation time

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
    battery = safe_call(lambda: psutil.sensors_battery())
    cpu_temp = safe_call(lambda: psutil.sensors_temperatures()['coretemp'][0].current if 'coretemp' in psutil.sensors_temperatures() else 'N/A')
    uptime = safe_call(lambda: time.time() - psutil.boot_time())
    processes = len(psutil.pids())
    top_mem_procs = safe_call(lambda: sorted(psutil.process_iter(attrs=['pid', 'name', 'memory_info']), key=lambda p: p.info['memory_info'].rss, reverse=True)[:5])
    top_cpu_procs = safe_call(lambda: sorted(psutil.process_iter(attrs=['pid', 'name', 'cpu_percent']), key=lambda p: p.info['cpu_percent'], reverse=True)[:5])
    load_avg = safe_call(lambda: os.getloadavg() if hasattr(os, 'getloadavg') else "Not available", "Not available")
    fs_type = safe_call(lambda: [partition.fstype for partition in psutil.disk_partitions()])
    total_threads = sum(p.num_threads() for p in psutil.process_iter())
    context_switches = safe_call(lambda: psutil.cpu_stats().ctx_switches)
    interrupts = safe_call(lambda: psutil.cpu_stats().interrupts)
    boot_time = safe_call(lambda: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(psutil.boot_time())))
    hostname = socket.gethostname()
    public_ip = "Not retrieved"  # This would need an external API call, but we'll leave it as a placeholder

    # Display additional information
    additional_info = [
        f"CPU Usage: {cpu_usage}",
        f"Disk Usage: {disk_usage}",
        f"Network I/O: {network_io}",
        f"Swap Memory: {swap_memory}",
        f"CPU Temperature: {cpu_temp} °C",
        f"System Uptime: {uptime if isinstance(uptime, str) else f'{uptime / 3600:.2f} hours'}",
        f"Number of Processes: {processes}",
        f"Top Memory Consuming Processes: {top_mem_procs}",
        f"Top CPU Consuming Processes: {top_cpu_procs}",
        f"Load Average: {load_avg}",
        f"Filesystem Type: {fs_type}",
        f"Total Number of Threads: {total_threads}",
        f"Context Switches: {context_switches}",
        f"Interrupts: {interrupts}",
        f"Boot Time: {boot_time}",
        f"Hostname: {hostname}",
        f"Public IP Address: {public_ip}"
    ]

    # Clear console
    print("\n" * 10)

    # Print final organized log
    print(f"Running hash rate test with {iterations} iterations...")
    print(f"Iterations: {iterations}")
    print(f"Number of threads used: {os.cpu_count()}")
    print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
    print(f"End time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
    print(f"Total time taken: {total_time_taken:.6f} seconds")
    print(f"Hash rate: {hash_rate:.2f} hashes/second")
    print(f"Average time per hash: {average_time_per_hash:.10f} seconds")
    print(f"Min time for a single hash: {min_time_per_hash:.10f} seconds")
    print(f"Max time for a single hash: {max_time_per_hash:.10f} seconds")
    print(f"Average hash time: {average_hash_time:.10f} seconds")
    print("\nMemory Usage:")
    print(f"Memory usage before test: {memory_before:.2f} MB")
    print(f"Memory usage after test: {memory_after:.2f} MB")
    print("\nSystem Information:")
    print(f"Platform: {platform.system()}")
    print(f"Release: {platform.release()}")
    print(f"Version: {platform.version()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    print(f"CPU Count: {os.cpu_count()} logical cores")
    print(f"Physical Memory: {psutil.virtual_memory().total / 1024 / 1024:.2f} MB")
    print(f"Python version: {platform.python_version()}")
    print("\nAdditional Information:")
    print("please submit info here -link to gfourms-")
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
