# errors.py
#
# test printing tracebacks from exceptions when an error occurs
# should continue running mqtt loop, but print traceback

from arena import Arena


arena = Arena(host="arena.andrew.cmu.edu", realm="realm", scene="example")


@arena.run_once
def main():
    print("hello")
    print(1/0)      # should print traceback here!
    print("world")

@arena.run_forever
def forever():
    print("goodbye")
    print(iDontExist())     # should print traceback here and stop running this task!
    print("planet")


arena.run_tasks()
