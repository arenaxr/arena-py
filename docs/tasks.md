# Tasks in ARENA-py

Tasks are ways you can run programs in the ARENA.

You can run a task once at startup:
```python
@arena.run_once
def f():
    print("here on startup")

# or do this:
arena.run_once(f)
```

You can run a task after a specified period of time (in milliseconds):
```python
@arena.run_after_interval(interval_ms=1000)
def f():
    print("here, but after 1 second")

# or do this:
arena.run_after_interval(f, 1000)
```

You can run a task every [interval_ms] milliseconds:
```python
@arena.run_forever(interval_ms=10000)
def f():
    print("here, but after 10 seconds")

# or do this:
arena.run_forever(f, 10000)
```

You can run an async task (for advanced users who know asyncio):
```python
@arena.run_async
def f():
    print("here")
    await arena.sleep(5000)
    print("here, but after 5 seconds")

# or do this:
arena.run_async(f, 1000)
```

## Arguments
You can add arguments to tasks like so:
```python
@arena.run_once(text="arena-py 2.0!", parent="sphere")
def make_text(text, parent):
    text_obj = Text(text=text, position=Position(0,1.5,0), parent=parent)
    arena.add_object(text_obj)

# you can also do this
arena.run_once(make_text, text="arena-py 2.0!", parent="sphere")
```

```python
@arena.run_forever(interval_ms=1234, arg="hello world")
def forever(arg):
    print(arg)

# you can also do this
arena.run_forever(forever, 1234, arg="hello world")
```
