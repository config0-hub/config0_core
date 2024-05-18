#!/bin/bash

# clean up misc
rm -rf /opt/shared
rm -rf /usr/src/tarballs
rm -rf /var/tmp/*

# clean up crontabs
rm -rf /var/spool/cron/crontabs/root
rm -rf /var/spool/cron/crontabs/ubuntu
