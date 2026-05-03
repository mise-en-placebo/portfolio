# My fork of sdorfehs

`sdorfehs` is a more modern implementation of the ratpoison
X11 window manager for Linux (and BSD). It matches nearly
all of my wants for a window manager: lightweight,
low-resource, keyboard-driven, and with advanced tagging for
windows, frames, and screens.

There were two features missing from `sdorfehs` that I
wished it had: the ability to (explicitly) move windows from
frame to frame, and for focus to follow the pointer on
click. (Yes, the latter goes against the whole spirit of the
project, but it's a feature that I've found to be
important.)

Instead of trying to find a different window manager that
fits my needs (which would likely be impossible as the niche
`sdorfehs` was already the best fit) I decided it would be
easier, and a good learning opportunity, to fork the project
and add the features myself.

Note that there is a minor bug with the fork: if a window
spawns a child/transient window which would normally hold
focus away from the parent until the child window was
terminated, clicking the parent window will crash the window
manager. I'm looking into fixes for this.

Also note that to build the project you'll need various X11
(C) headers; these are typically easily installed through
your package manager.

You can find the original project repository at
[https://github.com/jcs/sdorfehs](https://github.com/jcs/sdorfehs). 

You can find the actual repository of my fork at
[https://github.com/mise-en-placebo/sdorfehs](https://github.com/mise-en-placebo/sdorfehs).

---

## sdorfehs
<img src="https://jcs.org/images/sdorfehs-300.jpg" align="right">

#### (pronounced "starfish")

sdorfehs is a tiling window manager descended from
[ratpoison](https://www.nongnu.org/ratpoison/)
(which itself is modeled after
[GNU Screen](https://www.gnu.org/software/screen/)).

sdorfehs divides the screen into one or more frames, each only displaying
one window at a time but can cycle through all available windows (those
which are not being shown in another frame).

Like Screen, sdorfehs primarily uses prefixed/modal key bindings for most
actions.
sdorfehs's command mode is entered with a configurable keystroke
(`Control+a` by default) which then allows a number of bindings accessible
with just a single keystroke or any other combination.
For example, to cycle through available windows in a frame, press
`Control+a` then `n`.

### License

sdorfehs retains ratpoison's GPL2 license.

### Compiling

Run `make` to compile, and `make install` to install to `/usr/local` by
default.

### Wiki

The
[sdorfehs Wiki](https://github.com/jcs/sdorfehs/wiki)
has tips and tricks, and information on troubleshooting problems.

## Features

sdorfehs retains most of ratpoison's features while adding some more modern
touches.

![Screenshot](https://jcs.org/images/sdorfehs-20190826.png)

### EWMH

sdorfehs strives to be a bit more
[EWMH](https://specifications.freedesktop.org/wm-spec/wm-spec-latest.html)
compliant, supporting Atoms such as `_NET_ACTIVE_WINDOW` for compositors
to dim unfocused windows, and `_NET_WM_STATE_FULLSCREEN` to allow full-screen
programs like VLC and Firefox to take over the entire screen when requested
(though still allowing the standard key bindings to switch windows or kill
the program).

### Virtual Screens

sdorfehs adds virtual screens which each have their own frame configuration
and set of windows.
Windows can be moved between virtual screens with `vmove`.
By default, virtual screens can be selected (via the `vselect` command)
with `Control+a, F1` through `Control+a, F12`.

### Bar

sdorfehs has a bar window which displays status messages or the output of
certain commands.
By default, this bar is made sticky with the `barsticky` setting which
forces the bar to be permanently affixed to the top or bottom (configurable
with the `bargravity` setting) of every virtual screen displaying the
currently-focused window's title on the left side.

When the bar is sticky, it also enables a mechanism to display arbitrary
text on the right side, similar to bar programs for other window managers like
i3bar, dzen2, etc.
sdorfehs creates a
[named pipe](https://en.wikipedia.org/wiki/Named_pipe)
at `~/.config/sdorfehs/bar` and any text input into the pipe shows up on
the bar, making it easy to integrate with standard utilities which can just
echo into the pipe.
For an extremely simple example, a shell script can just echo the output of
`date` into the pipe once a second.

    while true; do
      date > ~/.config/sdorfehs/bar
      sleep 1
    done

Bar input supports some markup commands from dzen2 in the format
`^command(details)` which affect the text following the command until the
command is reset with `^command()`.
Currently supported commands:

- `^ca(btn,cmd,btn2,cmd2)`: execute `cmd` when mouse button `btn` is clicked on
this area of text, or `cmd2` if button `btn2` is clicked.
Closing the area of clickable text can be done with `^ca()`.

- `^fg(color)`: color the text following until the next `^fg()` command.
A line of text such as `hello ^fg(green)world^fg()!` will color `hello` with
the default foreground color (`set fgcolor`), then `world` in green, and the
exclamation point with the default color.
Colors can be specified as their common name (`blue`) or as a hex code
(`#0000ff`).

- `^fn(font)`: change the font of the following text.
Fonts must be specified in Xft format like `set font` such as
`^fn(noto emoji:size=13)`.
Resetting to the default font can be done with `^fn()`.

### Focus on click

This fork also enables 'focus follows click'
functionality. There are many instances in modern programs
where the interface is not designed for keyboard-driven
input, e.g., web browsers. It's rare in such programs that
you would wish to interact with the program solely with the
mouse. For example, if your browser is not focused, you
would rarely want to click 'new tab' and then not want to
input the URL.

To keep with the ratpoison spirit of the project, 'focus
follows click' functionality is **disabled** by default. You
can enable it by changing `FOCUS_FOLLOWS_CLICK` to `1` in
`config.h` when compiling, _or_ executing `set focusonclick
1` (either from a running sdorfehs instance or via the
configuration file).

Note that focus will follow _any_ pointer button, with any
modifiers applied.

### Gaps

sdorfehs enables a configurable gap (with `set gap`) between frames by
default to look a bit nicer on larger displays.

### Secure Remote Control

sdorfehs's `-c` command line option uses a more secure IPC mechanism
than Ratpoison for sending commands to a running sdorfehs process,
such as a script controlling sdorfehs to restore a particular layout.

Ratpoison's IPC only requires that a process create a new X11 window
and set an Atom on it, which the parent Ratpoison process reads and
executes the value of that Atom.
An unprivileged application that only has an X11 connection (say a
sandboxed Firefox child process) could set the `RP_COMMAND_REQUEST`
Atom property on its existing window with a value of `0exec
something` to cause Ratpoison to read it and execute that shell
command as the user id running Ratpoison.

sdorfehs's IPC mechanism switches to a Unix socket in the
`~/.config/sdorfehs` directory which ensures the requesting process
has the ability to make socket connections and can write to that
path.
