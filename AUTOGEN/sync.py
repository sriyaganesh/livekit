import time

def task1():
    print("Task 1 started")
    time.sleep(2)   # waits for 2 seconds
    print("Task 1 finished")

def task2():
    print("Task 2 started")
    time.sleep(1)   # waits for 1 second
    print("Task 2 finished")

# Run tasks
start=time.time()

task1()
task2()
end=time.time()

print(f"Total time taken: {end-start:.2f} seconds")