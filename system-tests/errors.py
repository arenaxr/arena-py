# errors.py
#
# test printing tracebacks from exceptions when an error occurs
# should continue running mqtt loop, but print traceback

from arena import Arena

arena = Arena("arena.andrew.cmu.edu", "realm", "example")

@arena.run_once
def main():
    print("hello")
    print(1/0) # should print traceback here!
    print("world")

arena.run_tasks()
