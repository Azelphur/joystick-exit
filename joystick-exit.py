#!/usr/bin/python

import pygame
import argparse
import time
import subprocess
import psutil
import logging
import shlex

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

def kill_proc_tree(pid, including_parent=True):    
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    for child in children:
        logging.info('Killing child pid %d', child.pid)
        child.kill()
    psutil.wait_procs(children, timeout=5)
    if including_parent:
        parent.kill()

def kill_process():
    if args.kill_children:
        kill_proc_tree(PROCESS.pid)
    else:
        PROCESS.kill()

PROCESS = None

if args.program:
    p = subprocess.Popen(shlex.split(args.program), shell=False).pid
    PROCESS = psutil.Process(pid=p)
    logging.info('Spawned process %d', PROCESS.pid)
elif args.existing_program:
    for i in range(args.wait_for_start):
        for proc in psutil.process_iter():
            if proc.name() == args.existing_program:
                PROCESS = proc
                break
        if PROCESS:
            logging.info('Found process %d', PROCESS.pid)
            break
        logging.info('Process not found, retrying')
        time.sleep(1)

if not PROCESS:
    logging.error('Process not found, you must specify either --program or --existing-program')
    exit()

while True:
    try:
        if PROCESS.status() == 'zombie':
            logging.info('Process is a zombie, exiting.')
            break
    except psutil.NoSuchProcess:
        logging.info('Process no longer exists, exiting.')
        break

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
            BUTTONS.remove(event.button)
            if set(BUTTONS) != set(args.buttons):
                logging.info('Buttons are up at %d', time.time())
                DOWN_AT = None
    if DOWN_AT and time.time() - DOWN_AT >= args.hold:
        logging.info('Buttons have been held down for %d seconds, killing process', args.hold)
        kill_process()
        break
    clock.tick(2)
