#!/usr/bin/env python
"""Rebuild /etc/hosts.docker with an IP to FQDN map.

Interates all of the running containers, and creates /etc/hosts.docker, with
one line per container: the primary IP address of the container and the FQDN
(hostname plus domain name)."""

import json
import os
import os.path
import subprocess
import time

DNSMASQ_USER = 'nobody'
DOCKER_HOSTS_BANNER = """\
# Docker hosts. This file is auto-generated by {filename} on each docker
# invocation.
#
# Last updated: {last_updated} with {container_count} running containers

"""

def generate_docker_hosts_contents():
    """Creates the content for the docker hosts.

    For example, if you have these containers running:
        - ID: 5ab8ff1a30ac, IP: 1.2.3.4, Hostname: foo.example.com
        - ID: 9a29f2d34ef1, IP: 5.6.7.8, Hostname: example

    Then this will return (where <...> is generated dynamically):
        <DOCKER_HOSTS_BANNER with the values filled in>

        1.2.3.4     foo.example.com
        5.6.7.8     example

    """

    docker_hosts_lines = []

    docker_ps_output = subprocess.check_output(['docker', 'ps', '-q']).strip()
    if docker_ps_output:
        running_containers = docker_ps_output.split("\n")
        for container in running_containers:
            status = json.loads(
                subprocess.check_output(['docker', 'inspect', container])
            )[0]

            hostname = status['Config']['Hostname']
            domain = status['Config']['Domainname']

            fqdn = hostname
            if domain:
                fqdn += '.' + domain

            docker_hosts_lines.append('{ip}\t{fqdn}'.format(
                ip=status['NetworkSettings']['IPAddress'],
                fqdn=fqdn,
            ))

    return DOCKER_HOSTS_BANNER.format(
        filename=os.path.abspath(__file__),
        last_updated=time.strftime('%c'),
        container_count=len(docker_hosts_lines),
    ) + '\n'.join(docker_hosts_lines)

def reload_dnsmasq():
    """Attempts to reload dnsmasq by sending it SIGHUP."""

    reload_dnsmasq_exit_code = subprocess.call([
        'sudo', '-n', # Run sudo non-interactively, and switch to
        '-u', DNSMASQ_USER, 'pkill', # the dnsmasq user to try to signal
        '-HUP', # (by sending SIGHUP)
        '-u', DNSMASQ_USER, # any processes owned by it and
        '-f', '/usr/sbin/dnsmasq' # that appear to be a dnsmasq process.
    ])
    if reload_dnsmasq_exit_code != 0:
        print "Failed to reload dnsmasq (exit code {exit_code})".format(
            exit_code=reload_dnsmasq_exit_code
        )

def main():
    """Main entry point for this module."""

    try:
        with open('/etc/hosts.docker', 'w') as docker_hosts:
            docker_hosts.write(generate_docker_hosts_contents())

            # Having a terminating new-line makes the easier to read (e.g.
            # when printed via `cat`).
            docker_hosts.write('\n')
    except IOError:
        print "Cannot write docker hosts file. Please check the permissions."
        raise

    reload_dnsmasq()

if __name__ == '__main__':
    main()
