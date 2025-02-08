#!/bin/bash

openssl enc -d -pbkdf2 -aes-256-cbc -in $1 -out $2 -k $3
