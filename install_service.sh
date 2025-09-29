#!/bin/bash

systemctl disable --now m1s_ups
rm -rf /etc/m1s_ups/
mkdir /etc/m1s_ups/
mkdir /var/log/m1s_ups/
set -e

apt update
apt install python3-pip python3-venv python3-dev
cp requirements.txt /etc/m1s_ups/
cp kill.sh /etc/m1s_ups/
cp service.py /etc/m1s_ups/
cp m1s_ups.service /etc/systemd/system/

cd /etc/m1s_ups/
python3 -m venv venv
venv/bin/python3 -m pip install -r requirements.txt --break-system-packages
systemctl daemon-reload

systemctl enable --now m1s_ups

echo 'install sucess'
