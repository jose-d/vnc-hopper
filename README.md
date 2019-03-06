# vnc-hopper

Wrapper script for TigerVNC.

Vnc-hopper script automatically connects to remote ssh server, possibly via jumphosts specified in `.ssh/config`, checks if there is any vncserver running - if no, starts new one and start vncviewer locally with arguments needed for tunnelled VNC session.

So far extra-early version.

## howto

1) configure your jumphosts in `.ssh/config` - and make sure you can connect directly with your ssh keys using the aliases from `.config`
2) update the `servers` variable in script with list of your vnc servers

