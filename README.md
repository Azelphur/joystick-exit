# joystick-exit
Exit games/emulators using a joystick. Works great with things like EmulationStation and Kodi/XBMC

Joystick-exit will allow you to exit any process when
- A button on a joystick is pressed
- A combination of buttons on a joystick is pressed
- A combination of buttons on a joystick is held down

Now for some examples. All these examples are with XBox 360 wireless controllers, however any joystick will work.

Exit dolphin when the xbox button is held down for 2 seconds on the first joystick.

```joystick-exit.py --joysticks 0 --buttons 10 --hold 2 --program "dolphin-emu -b -e game.iso"```

Exit PCSX2 when A+B+X+Y are pressed on any joystick. Note that PCSX2 runs as a shell script so you must --kill-children.

```joystick-exit.py --kill-children --buttons 0 1 2 3 --program "/usr/games/PCSX2-linux.sh --fullscreen --nogui game.iso"```

This example shows working with a steam game. Steam games detach so we can't run them ourselves, this example shows attaching to an existing process. So you must run portal 2 before running this, then portal 2 will exit when start+select are held for 2 seconds on joystick 0 or 1.
```joystick-exit.py --joysticks 0 1 --buttons 8 9 --hold 2 --existing-program portal2_linux```
