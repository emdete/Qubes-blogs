Qubes
=====

Errors & Bugs
-------------

- GUI error with debian-9

- rfkill problem

- usb problem

- acpi (?) problem (battery control, XF86Launch1, brightness stops working after suspend/resume)

- qubes vm manager does not provide scrollbars

- sound / pulse audio for 9, actual version is 10 FIXED: move the .so to the proper places fixes this

- umlaut does not work in VMs (dom0 works) FIXED: run xmodmap

- no dvd video ([lavf] av_find_stream_info() failed, Error cracking CSS key for /VIDEO_TS/VTS_02_0.VOB), libdvdcss installed

- templates do not shut down

Ugliness
--------

- how to change pwd (account, crypt fs)

- use nodm

- use tk instead of qt

- separate packing for distributions from code

- reduce installed packages (all xorg drivers, wpa.., firmware.., ...)

- reconsider systemd use (runit)

- reconsider installation of dhcpcd&dnsmasq in favour of network manager

- debian should switch off apt install-recommends, install-suggests

- are the dependencies correct?

- isc-dhcp is a nightmare

- switch from exim to opensmtp

- take a look at voidlinux

- traces left from dispvm

- sudo-install into /usr/local/bin could overwrite programs permanently if that's first in $PATH

- no proper backup concept (raw blobs just take too long to be regulary made (once a day?))

