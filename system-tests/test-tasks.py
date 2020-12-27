from arena import *

# start ARENA client
arena = Arena("arena.andrew.cmu.edu", "realm", "test")

@arena.run_once
def f1():
    print("f1")

@arena.run_after_interval(interval_ms=3000)
def f2():
    print("f2")

@arena.run_async
async def f3():
    print("f3 1")
    await arena.sleep(5000)
    print("f3 2")

@arena.run_forever(interval_ms=10000)
def f4():
    print("f4")

def f5():
    print("f5")

arena.run_forever(f5)

arena.start_tasks()
