#!/usr/bin/python

import sys
import pygame
import argparse
import time
import subprocess
import psutil
import logging
import shlex
import os
import re
from subprocess import PIPE, Popen

parser = argparse.ArgumentParser(description='Joystick exit')
parser.add_argument('--joysticks', type=int, help='Joystick numbers to listen for, omit to listen to all joysticks', nargs='+')
parser.add_argument('--buttons', type=int, help='Button(s) to listen for, if multiple are specified, all must be pressed at the same time', nargs='+')
parser.add_argument('--hold', type=int, help='Number of seconds buttons must be held for to trigger exit')
parser.add_argument('--program', help='Program to execute')
parser.add_argument('--existing-program', help='Hook onto an existing program')
parser.add_argument('--wait-for-start', help="For hooking to existing programs, wait this amount of seconds to start", default=20, type=int)
parser.add_argument('--kill-children', help="Enable this if your game/emulator doesn't exit. Some things launch", action='store_const', const=True)
parser.add_argument('--log-level', help="Logging level, set to DEBUG if you're having problems.", default='ERROR')

args = parser.parse_args()

logging.basicConfig(level=getattr(logging, args.log_level.upper()))

pygame.init()

if args.joysticks:
    for x in args.joysticks:
        pygame.joystick.Joystick(x).init() 
        logging.info('Hooked joystick %d', x)
else:
    for x in range(pygame.joystick.get_count()):
        pygame.joystick.Joystick(x).init()
        logging.info('Hooked joystick %d', x)

pygame.joystick.init()

BUTTONS = []
DOWN_AT = None

clock = pygame.time.Clock()

def kill_process():
    title = get_active_window_title()
    print("Killing", title)
    if title != "EmulationStation":
        os.system("wmctrl -c :ACTIVE:")

def get_active_window_title():
    root = subprocess.Popen(['xprop', '-root', '_NET_ACTIVE_WINDOW'], stdout=subprocess.PIPE)
    stdout, stderr = root.communicate()

    m = re.search(b'^_NET_ACTIVE_WINDOW.* ([\w]+)$', stdout)
    if m != None:
        window_id = m.group(1)
        window = subprocess.Popen(['xprop', '-id', window_id, 'WM_NAME'], stdout=subprocess.PIPE)
        stdout, stderr = window.communicate()
    else:
        return None

    match = re.match(b"WM_NAME\(\w+\) = (?P<name>.+)$", stdout)
    if match != None:
        return match.group("name").decode('utf-8').strip('"')
        #return match.group("name").decode('utf-8')

    return None

while True:
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            logging.info('Joystick %d Button %d is down', event.joy, event.button)
            BUTTONS.append(event.button)
            if set(BUTTONS) == set(args.buttons):
                logging.info('Buttons are down at %d', time.time())
                if args.hold:
                    DOWN_AT = time.time()
                else:
                    kill_process()
        if event.type == pygame.JOYBUTTONUP:
            logging.info('Joystick %d Button %d is up', event.joy, event.button)
            try:
                BUTTONS.remove(event.button)
            except ValueError:
                pass
            if set(BUTTONS) != set(args.buttons):
                logging.info('Buttons are up at %d', time.time())
                DOWN_AT = None
    if DOWN_AT and time.time() - DOWN_AT >= args.hold:
        logging.info('Buttons have been held down for %d seconds, killing process', args.hold)
        kill_process()
        DOWN_AT = None
    clock.tick(2)
