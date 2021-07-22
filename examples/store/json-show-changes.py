#!/usr/bin/env python
from arena import *

scene = Scene(host="arenaxr.org", scene="example")

@scene.run_forever(interval_ms=1000)
def print_store():
    print(Store.all_stores)

scene.run_tasks()
