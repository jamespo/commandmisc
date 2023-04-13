# check-systemd-socket

## Install

Copy service file to /etc/systemd/system/ & run systemctl daemon-reload

Copy shell script to /usr/local/bin

Enable & start the daemon (example given for dbus.socket):

       systemctl start check-systemd-socket@dbus
       systemctl enable check-systemd-socket@dbus
