def tuple_to_string(tup):
    s = ""
    for val in tup:
        s += str(val) + " "
    return s.strip()

def agran(float_num):
    """Reduces floating point numbers to ARENA granularity."""
    return round(float_num, 3)
