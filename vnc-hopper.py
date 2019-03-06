#!/usr/bin/env python3

import subprocess
import random
import re
import sys
import os
from threading import Thread

# settings

# jumpserver aliases:
servers = [
    'koios1-limba',
    'koios2-limba',
]

start_vnc_timeout = 10

# classes:

class VncClientRunner():

    def run_vnc_client(self, vnc_server_host, display_id):

        # smth like this: vncviewer -via koios1-limba localhost:2
        passwd_file = str(local_home) + "/.vnc/passwd"
        if os.path.isfile(passwd_file):     # if there is password file, let's use it:
            command_array = [
                'vncviewer', '-via', vnc_server_host, 'localhost:' + str(display_id),
                "-passwd="+passwd_file
            ]
        else:
            command_array = [
                'vncviewer', '-via', vnc_server_host, 'localhost:' + str(display_id)
            ]
        print(str(command_array))
        try:
            vnc_subprocess = subprocess.Popen(
                command_array,  # try to run well-known command
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE
            )
        except:
            print("Exception in run_vnc_client, let's end this.")
            dump_buffer(vnc_subprocess.stdout)
            dump_buffer(vnc_subprocess.stderr)
            sys.exit(1)
        else:
            dump_buffer(vnc_subprocess.stdout)
            dump_buffer(vnc_subprocess.stderr)
            sys.exit(0)


# functions

def dump_buffer(buffer):
    lines = buffer.readlines()
    for line in lines:
        print(str(line.decode('utf-8')).strip())


def start_vnc(server):
    # start vnc
    try:
        start_vnc_output = subprocess.Popen(
            ['ssh', server, "vncserver","-localhost" ],  # try to run vncserver, localhost only.
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        dump_buffer(start_vnc_output.stdout)
        dump_buffer(start_vnc_output.stderr)
    except:
        print("Exception in run_vnc_client")
        return False
    else:
        if start_vnc_output.wait(start_vnc_timeout) != 0:
            print("Non-zero RC code in start_vnc_output.wait command vncserver...")
            return False
        if start_vnc_output.returncode != 0:
            print("Non-zero RC code for command vncserver...")
            return False
        # ok, not bad:
        return True


def try_ssh(server):
    # first check ssh connectivity:
    try:
        ssh_try_output = subprocess.Popen(
            ['ssh', server, "uname"],  # try to run well-known command
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
    except:
        print("Exception in try_ssh")
        return False
    else:
        uname_string = str(ssh_try_output.stdout.readlines()[0].decode('utf-8')).strip()
        if uname_string == 'Linux':
            return True

    return False


def download_vnc_pass(server):
    # first check ssh connectivity:
    try:
        cmd_string_list = ['scp', "'" + server + ":$HOME/.vnc/passwd'", local_home+"/.vnc/"]
        print(cmd_string_list)
        ssh_try_output = subprocess.Popen(
            cmd_string_list,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        print("download_vnc_pass")
        dump_buffer(ssh_try_output.stdout)
        dump_buffer(ssh_try_output.stderr)
        print("download_vnc_pass_end")
    except:
        print("Exception in download_vnc_pass")
        return False
    else:
        if ssh_try_output.returncode == 0: return True

    return False


def discovery_servers(servers):
    # collect info about servers: (buffers)

    discovery_outputs = {}  # array of buffers
    for server in servers:
        try:
            discovery_output = subprocess.Popen(
                ["ssh", server, "vncserver", "-list"],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE
            )
        except:
            print("Problem occurred when trying to connect to server " + server + ", skipping.")
        else:
            discovery_outputs[server] = discovery_output

    # compile RE to match lines like:
    # :3		135784 - 3 is display number, the second number is PID

    pattern = re.compile("^:\d+\s+\d+$")
    server_list = []

    # find running sessions and ports:
    for host in discovery_outputs:
        lines = discovery_outputs[host].stdout.readlines()
        for line in lines:
            decoded_line = str(line.decode("utf-8")).strip()
            if decoded_line == '':  # we skip empty lines
                continue
            if "TigerVNC" in decoded_line:  # we skip title line
                continue
            if "PROCESS" in decoded_line:  # we skip headers
                continue
            if pattern.match(decoded_line):  # parse port and pid
                display_id, vnc_pid = decoded_line.split()
                display_id = str(display_id).replace(':', '')
                server_list.append((str(host), int(display_id), int(vnc_pid)))

    if len(server_list) == 0:  # no server
        return None
    else:  # return first server: :)
        return server_list[0]  # take the first one :))


# main
if __name__ == '__main__':

    local_home = os.getenv("HOME")

    # check if there is any server running, if not, start one:

    ds = discovery_servers(servers)
    if not ds or ds == 0:
        print("There is no running VNC server, let's start one..")
        servers_shuffled = random.sample(servers, len(servers))
        for server in servers_shuffled:
            print("trying ssh to server " + str(server) + "...")
            if not try_ssh(server):
                continue

            print("server with ssh:" + server)
            print("starting vnc on server " + str(server) + "...")
            if not start_vnc(server):
                continue

            print("we started vnc server on " + str(server))
            break

    # now one should be running. if not, then there's something wrong.

    ds = discovery_servers(servers)
    if not ds or ds == 0:
        print("There is no running VNC server and the attempts to start it failed. Contact support.")
        sys.exit(1)

    host, display_id, pid = discovery_servers(servers)

    # download vnc password from server:

    #download_vnc_pass(host) #notworking

    # let's start vnc client with tunnel:

    sshR = VncClientRunner()
    ssh_tunnel_thread = Thread(target=sshR.run_vnc_client, args=(host, display_id))
    ssh_tunnel_thread.start()

    # let's wait for the thread with vncviewer to finish (or to fail..)

    ssh_tunnel_thread.join()
