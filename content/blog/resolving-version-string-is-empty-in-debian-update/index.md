+++
title = "Resolving “version string is empty” in debian update"
description = "From yesterday I had weird issues with a clean installation of debian. Each time I’ve updated my system it crashed with a strange message:"
date = 2016-12-19T07:07:03.551Z
tags = ["debian", "linux", "raspberry-pi"]
medium = "https://medium.com/@jadi/resolving-version-string-is-empty-in-debian-update-1edafc221f07"
+++

From yesterday I had weird issues with a clean installation of debian. Each time I’ve updated my system it crashed with a strange message:

```
Selecting previously unselected package dirmngr.
  Preparing to unpack .../48-dirmngr_2.1.16-3_i386.deb ...
  dpkg-maintscript-helper: error: dpkg: error: version '' has bad syntax: version string is empty
  dpkg: error processing archive /tmp/apt-dpkg-install-P10DjX/48-dirmngr_2.1.16-3_i386.deb (--unpack):
   subprocess new pre-installation script returned error exit status 1
  dpkg-maintscript-helper: error: dpkg: error: version '' has bad syntax: version string is empty
  dpkg: error while cleaning up:
   subprocess new post-removal script returned error exit status 1
```

The issue is simple. dpkg sees an empty version string and refuses to continue. This bug [is already fixed](https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=848511) but not pushed to the main ftp server yet so you may experience the same headache I had for hours to bring your server up and running. The solution is simple. Donwload the older version from [http://ftp.debian.org/debian/pool/main/d/dpkg/](http://ftp.debian.org/debian/pool/main/d/dpkg/) and install it. I used dpkg_1.17.27 ([amd64 version](http://ftp.debian.org/debian/pool/main/d/dpkg/dpkg_1.17.27_amd64.deb)) and installed it using:

```
sudo dpkg -i dpkg_1.17.27_amd64.deb
```

and everything worked fine.

Note: do not update dpkg unless it is equal or higher than 1.18.17

---
*Originally published on [Medium](https://medium.com/@jadi/resolving-version-string-is-empty-in-debian-update-1edafc221f07).*
