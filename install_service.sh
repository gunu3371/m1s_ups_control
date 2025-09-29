#!/bin/bash
set -e

systemctl disable --now m1s_ups
apt update
apt install python3-pip python3-venv python3-dev
mkdir /etc/m1s_ups/
mkdir /var/log/m1s_ups/

rm -r /etc/m1s_ups/*

cp kill.sh /etc/m1s_ups/
cp service.py /etc/m1s_ups/
cp m1s_ups.service /etc/systemd/system/

cd /etc/m1s_ups/
python -m venv venv
venv/bin/python3 -m pip install -r requirements.txt --break-system-packages
systemctl daemon-reload

systemctl enable --now m1s_ups

echo 'install sucess'
