#!/bin/bash
python3 -m pip install -r requirements.txt
mkdir -p /etc/m1s_ups/

cp kill.sh /etc/m1s_ups/
cp service.py /etc/m1s_ups/
cp m1s_ups.service /etc/systemd/system/

systemctl daemon-reload

systemctl enable --now m1s_ups

echo 'install sucess'
