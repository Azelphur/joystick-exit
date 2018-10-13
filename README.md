# joystick-exit
Exit games/emulators using a joystick. Works great with things like EmulationStation and Kodi/XBMC This is achieved by using `wmctrl -c :ACTIVE:` - so wmctrl is a dependency.

Joystick-exit will allow you to exit any process when
- A button on a joystick is pressed
- A combination of buttons on a joystick is pressed
- A combination of buttons on a joystick is held down

Now for some examples. All these examples are with XBox 360 wireless controllers, however any joystick will work.

Exit when the xbox button is held down for 2 seconds on the first joystick.

```joystick-exit.py --joysticks 0 --buttons 10 --hold 2```

Exit when A+B+X+Y are pressed on any joystick.

```joystick-exit.py --kill-children --buttons 0 1 2 3```
