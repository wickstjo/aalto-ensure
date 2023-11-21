import concurrent.futures
import time

def worker_function(task):
    print(f"Working on task {task}")
    # Simulate some work
    time.sleep(2)
    print(f"Task {task} completed")

def main():
    # Number of tasks
    num_tasks = 5

    # Create a thread pool with 3 worker threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # Submit tasks to the thread pool
        tasks = [executor.submit(worker_function, i) for i in range(num_tasks)]

        # Wait for all tasks to complete
        concurrent.futures.wait(tasks)

if __name__ == "__main__":
    main()
