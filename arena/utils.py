# simple general purpose functions
import random

def random_client_id():
    """Returns a random 6 digit id"""
    return str(random.randrange(100000, 999999))

def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])

def tuple_to_string(tup, sep=" "):
    """Turns a tuple into a string"""
    s = ""
    for val in tup:
        s += str(val) + sep
    return s.strip()

def agran(float_num):
    """Reduces floating point numbers to ARENA granularity."""
    return round(float_num, 3)

def santize_data(d):
    """replace underscores in data with dashes for aframe attributes"""
    underscore_words = []
    for k,v in d.items():
        if k == "dynamic_body" or k == "click_listener" or k == "goto_url":
            underscore_words += [k]
    for w in underscore_words:
        v = d[w]
        d[w.replace("_", "-").replace("--", "__")] = v
        del d[w]
