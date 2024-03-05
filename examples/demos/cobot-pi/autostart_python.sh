#!/bin/bash

'''
echo "waiting 10 seconds to warm up..."
sleep 1
echo "waiting 9 seconds to warm up..."
sleep 1
echo "waiting 8 seconds to warm up..."
sleep 1
echo "waiting 7 seconds to warm up..."
sleep 1
echo "waiting 6 seconds to warm up..."
sleep 1
'''
echo "waiting 5 seconds to warm up..."
sleep 1
echo "waiting 4 seconds to warm up..."
sleep 1
echo "waiting 3 seconds to warm up..."
sleep 1
echo "waiting 2 seconds to warm up..."
sleep 1
echo "waiting 1 seconds to warm up..."
sleep 1

x-terminal-emulator -e "pwd &&
			cd /home/ubuntu/Desktop/SteveLu-ARENA-py-Scripts/examples/MyCobotPi/ &&
			pwd &&
			python3 Arena320Pi.py"
