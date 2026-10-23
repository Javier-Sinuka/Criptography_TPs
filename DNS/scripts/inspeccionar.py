#!/usr/bin/env python3
from registrar import run

commands = [
    ['date', '--iso-8601=seconds'], ['cat', '/etc/os-release'], ['uname', '-a'], ['id'],
    ['ip', '-br', 'addr'], ['ip', 'route'], ['ip', 'neigh'],
    ['cat', '/etc/resolv.conf'], ['resolvectl', 'status'],
    ['systemctl', 'is-active', 'systemd-resolved', 'dnsmasq', 'nscd'],
    ['VBoxManage', 'list', 'vms'], ['VBoxManage', 'list', 'runningvms'],
    ['docker', 'ps', '--format', '{{.Names}}\t{{.Image}}\t{{.Status}}'],
    ['docker', 'images', '--format', '{{.Repository}}:{{.Tag}}'],
    ['sudo', '-n', 'true'], ['tcpdump', '--version'],
    ['python3', '--version'], ['pdflatex', '--version'],
    ['dpkg-query', '-W', 'wireshark*', 'tshark', 'tcpdump', '*qemu*', '*virtualbox*', '*vmware*', 'docker*', 'podman', '*screenshot*', 'python3-pil', 'python3-gi', 'x11-utils'],
    ['apt-cache', 'policy', 'wireshark', 'tshark'],
]
for command in commands:
    run(command, timeout=20)
