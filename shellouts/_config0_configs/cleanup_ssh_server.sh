#!/bin/bash

# clean up ssh keys
cd /etc/ssh/
rm -rf ssh_host_dsa_key*
rm -rf ssh_host_rsa_key*
rm -rf ssh_host_e*

# clean up ubuntu
rm -rf /home/ubuntu/.bash_history
rm -rf /home/ubuntu/.ssh

# clean up root
rm -rf /root/.bash_history
rm -rf /root/.ssh
