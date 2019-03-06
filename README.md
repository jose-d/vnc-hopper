# vnc-hopper

Wrapper script for TigerVNC.

Vnc-hopper script automatically connects to remote ssh server, possibly via jumphosts specified in `.ssh/config`, checks if there is any vncserver running - if no, starts new one and start vncviewer locally with arguments needed for tunnelled VNC session.

So far extra-early version.
