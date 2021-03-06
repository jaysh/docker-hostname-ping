docker-hostname-ping
====================

On a stock installation of Ubuntu based distributions comes with dnsmasq via NetworkManager. We can take advantage of this to generate a new file like `/etc/hosts` called `/etc/hosts.docker` which is read by `dnsmasq` for instant DNS updates on containers statuses.

In action:

    $ docker start stupefied_pare
    stupefied_pare
    $ docker ps
    CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS               NAMES
    fa5a5785d4ea        example:latest   /bin/bash           3 weeks ago         Up About a minute                       stupefied_pare      
    $ cat /etc/hosts.docker 
    # Docker hosts. This file is auto-generated by /home/jay/bin/rebuild_docker_hosts.py on each docker
    # invocation.
    #
    # Last updated: Sat Aug 30 18:41:23 2014 with 1 running containers

    172.17.0.4  example.com
    $ ping -c1 example.com
    PING example.com (172.17.0.4) 56(84) bytes of data.
    64 bytes from example.com (172.17.0.4): icmp_seq=1 ttl=64 time=0.085 ms

    --- example.com ping statistics ---
    1 packets transmitted, 1 received, 0% packet loss, time 0ms
    rtt min/avg/max/mdev = 0.085/0.085/0.085/0.000 ms

## Installation

There are few parts that need to be installed.

* copy `additional-dnsmasq.conf` to `/etc/NetworkManager/dnsmasq.d/docker`
* add the contents of docker-bashrc.sh to your `.bashrc`
* copy `rebuild_docker_hosts.py` to your `bin` (e.g. `$HOME/bin` or `/usr/local/bin`)
* enable your user to sudo to `nobody` without a password (I have a docker group, so I use `%docker ALL=(nobody) NOPASSWD: ALL`)
* create `/etc/hosts.docker` and ensure that it's writable by your user (e.g. `sudo chown root.docker /etc/hosts.docker && chmod 0775 /etc/hosts.docker`)
