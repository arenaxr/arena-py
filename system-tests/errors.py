# errors.py
#
# test printing tracebacks from exceptions when an error occurs
# should continue running mqtt loop, but print traceback

from arena import Scene


scene = Scene(host="arena.andrew.cmu.edu", realm="realm", scene="example")


@scene.run_once
def main():
    print("hello")
    print(1/0)      # should print traceback here!
    print("world")

@scene.run_forever
def forever():
    print("goodbye")
    print(iDontExist())     # should print traceback here and stop running this task!
    print("planet")


scene.run_tasks()
