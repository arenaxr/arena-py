#!/usr/bin/env python3
"""
arena-py-sub: Helper script for ARENA MQTT CLI subscribe
"""
import json
import os
import sys

def main():
    sargs = sys.argv
    args = []
    for arg in sargs:
        try:
            json.loads(arg)
            # preserve shell-stripped quotes
            if "\"" in arg:
                args.append(f"'{arg}'")
            else:
                args.append(f"\"{arg}\"")
        except:
            args.append(arg)
    args[0] = "python3 -m arena -a sub"
    os.system(" ".join(args))

if __name__ == "__main__":
    main()
