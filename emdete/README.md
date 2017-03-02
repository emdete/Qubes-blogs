Qubes
=====

Starting
--------

When starting with qubes as a computer worked with a highly tuned setup for
personal preferences in usability installing Qubes is like droping anchor. The
cost of security is you can't do anymore simpliest things. Even if wanted.
Point is to find out how to tell the system the difference of wanted and not so
much wanted stuff without loosing the benefits of Qubes.

On top you loose performance. Qubes generates a stead cpu usage of 20-30% (of
400%) without anything important running (having a audio control like
pavucontrol running in dom0 adds another 20% or so).

Staying productive
------------------

The only way to keep going was a double boot with all data for me. This is not
a secure setup but a learning constelation.

Qubes has an single image for all persistent stuff of a VM called
"private". This one has to be avaiable in Qubes and pure Debian to have
a double boot with all data in $HOME. The layout is a bit different as
it contains other persistent data as well:

```
drwxr-xr-x  3 root root  4096 Dec  9 13:58 /rw/bind-dirs
drwxr-xr-x  2 root root  4096 Feb 17 19:17 /rw/config
drwxr-xr-x  5 root root  4096 Feb  8 15:28 /rw/home
drwx------  2 root root 16384 Oct  6 14:26 /rw/lost+found
drwxr-xr-x 12 root root  4096 Feb  8 15:28 /rw/usrlocal
```

The user in Qubes has to have uid 1000, gid 1000 and name user. The last
i did just with a symlink to have a `home/user`. Qubes does to a symlink
from /home but uses bind mount. I established the same in Debian with
this entry in `/etc/fstab`:

```
/rw/home        /home       none    noauto,bind,defaults 0 0
```

The Qubes Manage nicely shows where
the disk images for the VMs ended up so i created a debian AppVM, removed the
private raw image of it and symlinked the partition.

I added the part to boot Qubes from the original Qubes installtion into
the grub config of my bare metal installation to have a double boot.

Template usage
--------------

I played around with VMs alot. This is much fun, it just works. You can
clone, rename, delete VMs at will, the AppVMs depend on templates which
can even be changed easily. All installed software is in the template
and inherited by the AppVM.

This leads to several usability problems:

- if you need to install a missing program you do so in the template and
  have to restart both after that

- if you have several AppVMs with dedicated duties and thus different
  needs for different programs you end up either in a single template
  that has installed all the software for all duties or in several
  templates with alot additional administrative work

so my rules with VMs are as such:

- i do not touch the preinstalled templates but clone those before
  change and reduce the installed packages in that template to the bare
  minumum

- i cloned the minimal template into several templates with different
  purposes - in case i find a package missing in all templates i install
  it from dom0 via a script.

during minimize i found really weird packages installed in debian
templates (i did not check fedora):

- all xorg drivers while only 2 are needed

- wpa while there is no wlan in the AppVM

- firmware

- big fat NetworkManager, avahi, mdns (i replaced it succesfully by
  dhcpcd&dnsmasq)

USB
---

Some chips have a reset-bug. This was my major show stopper in using
USB. Next it was completly unclear to me what to expect from Qubes about
it. The sys-usb VM was not installed and when i did so it hang so i left
all USB in dom0 which is a bad idea.

The reset bug is bad but having USB in dom0 is worse i decided. So i
enabled to be not so strict in that VM and it works.

After that you can (via command line currently only) ex/import most of the
USB devices to VMs, device by device, not devices by bus anymore. Just
issue a

```
qvm-usb -l
qvm-usb -a <id> <vm>
```

to do so.

The mouse is automatically detected and grabbed by dom0 after i agreed
to it when logging in.

A webcam could be exported to an AppVM, next steps will be android &
adb.

Wireless
--------

My bluetooth was switched on all the time (led was lit). This wasn't the
case under Debian. i installed rfkill `qubes-dom0-update rfkill` in
dom0 which allowed to switch wwan & bluetooth off.

Voidlinux
---------

I recently discovered Voidlinux, a new distribution from scratch without
legacy issues. So i decided to try to build a Voidlinux based appvm.

A setup of an HVM was braindead simple. An AppVM (or PVM) would be
harder. All the Qubes programs have to be build. This is alot of trouble
because these are targeted for the support distributions only. The repos
contain a mix of building and packaging (for rpm & deb). I expect a
source tree to build with `make` and to install with `make install` -
plus maybe a configure step in the beginning. These repos don't behave
like that. Some just give a help when issueing a `make`, some have even
bugs in that help, some don't even have a generic Makefile and rely on
distro specific stuff.

On top the packages depend on systemd (which is not used by Voidlinux).
I doubt that systemd is a good choice for a system like Qubes but that's
another matter. Anyway the packages need some cleanup before being
generic enough and usabe.


Below this line is my _INTERNAL_, personal list of keywords:

VPNs
----

Clipboard
---------

xmodmap
-------

Outstanding problems
-------------

- xmodmap

- pavucontrol in dom0 takes 20% cpu

- GUI error with debian-9 (U2MFN_GET_MFN_FOR_PAGE: get_user_pages
  failed, ret=0xfffffffffffffff2)

- usb problem

- acpi (?) problem (battery control, XF86Launch1, brightness sometimes stop working after suspend/resume)

- qubes vm manager does not provide scrollbars

- sound / pulse audio for 9, actual version is 10 FIXED: move the .so to the proper places fixes this

- umlaut does not work in VMs (dom0 works) FIXED: run xmodmap

- no dvd video ([lavf] av_find_stream_info() failed, Error cracking CSS key for /VIDEO_TS/VTS_02_0.VOB), libdvdcss installed

- templates do not shut down

- how to change pwd (account, crypt fs)

- use nodm

- use tk instead of qt

- separate packing for distributions from code

- reconsider systemd use (runit)

- debian should switch off apt install-recommends, install-suggests

- are the dependencies correct?

- isc-dhcp is a nightmare

- switch from exim to opensmtp

- traces left from dispvm

- sudo-install into /usr/local/bin could overwrite programs permanently if that's first in $PATH

- no proper backup concept (raw blobs just take too long to be regulary made (once a day?))

