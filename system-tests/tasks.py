from arena import *

# start ARENA client
scene = Scene(host="arenaxr.org", realm="realm", scene="test")

@scene.run_once
def f1():
    print("f1")

@scene.run_after_interval(interval_ms=3000)
def f2():
    print("f2")

@scene.run_async
async def f3():
    print("f3 1")
    await scene.sleep(5000)
    print("f3 2")

@scene.run_forever(interval_ms=10000)
def f4():
    print("f4")

def f5():
    print("f5")

scene.run_forever(f5)

scene.run_tasks()
