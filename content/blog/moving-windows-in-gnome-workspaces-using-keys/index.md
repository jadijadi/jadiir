+++
title = "Moving windows in GNOME workspaces using keys"
description = "I always prefer to have my workspaces in a grid (using the extention). Unfortunately there is no keybinding configuration in the GNOME’s…"
date = 2023-07-11T05:48:33.313Z
tags = ["gnome", "keyboard", "linux", "tips", "tricks"]
medium = "https://medium.com/@jadi/moving-windows-in-gnome-workspaces-using-keys-971cc90bbe70"
+++

I always prefer to have my workspaces in a grid (using the extention). Unfortunately there is no keybinding configuration in the GNOME’s GUI to configure moving windows to “one workspace up” and “one workspace down”; but the configuration presents in GNOME itself and can be configured using these commands. This is how I like it:

```
➜  ~ gsettings set org.gnome.desktop.wm.keybindings  move-to-workspace-right "['<Control><Shift>Right']"
➜  ~ gsettings set org.gnome.desktop.wm.keybindings  move-to-workspace-left "['<Control><Shift>Left']"
➜  ~ gsettings set org.gnome.desktop.wm.keybindings  move-to-workspace-up "['<Control><Shift>Up']"
➜  ~ gsettings set org.gnome.desktop.wm.keybindings  move-to-workspace-down "['<Control><Shift>Down']"
```

---
*Originally published on [Medium](https://medium.com/@jadi/moving-windows-in-gnome-workspaces-using-keys-971cc90bbe70).*
