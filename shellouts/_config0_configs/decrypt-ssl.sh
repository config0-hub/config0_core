#!/bin/bash

openssl enc -d -pbkdf2 -a -salt -aes-256-cbc -in $1 -out $2 -k $3
