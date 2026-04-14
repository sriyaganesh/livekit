import asyncio
import time

async def task1():
    print("Task 1 started")
    await asyncio.sleep(2)   # waits for 2 seconds
    print("Task 1.1 started")
    await asyncio.sleep(5)   # waits for 2 seconds
    print("Task 1 and 1.1 Finished")
    

async def task2():
    print("Task 2 started")
    await asyncio.sleep(2)   # waits for 2 seconds
    print("Task 2.1 started")
    await asyncio.sleep(5)   # waits for 2 seconds
    print("Task 2 and 2.1 Finished")
    


# Run tasks
async def main():
    start=time.time()
    await asyncio.gather(task1(), task2())
    end=time.time()
    print(f"Total time taken: {end-start:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())