# m1s_ups_control
## KR
ODROID-M1S 용 UPS모듈용 파이썬 스크립트
+ ### 기능
  + 자동 종료
  + UPS/전원상태를 로그에 저장
  + BE400같은 통신기능이 없는 UPS를 대신하여 다른 서버/컴퓨터에 종료신호 뿌리기(작업중)
+ ### 설치방법
  + 1.https://wiki.odroid.com/odroid-m1s/application_note/circuitpython#set_environment 이링크를 따라서 /boot/config.ini 수정후 재부팅
  + 2.```bash git clone https://github.com/gunu3371/m1s_ups_control.git``` 실행
  + 3.```bash sh install_service.sh``` 실행
+ ### 사용방법
  + ```bash systemctl status m1s_ups``` 로 상태확인
  + ```/etc/m1s_ups/log/``` 에서 로그확인
## EN
Python script for UPS module for ODROID-M1S
+ ### Features
  + Automatic shutdown
  + Save UPS/power status in log
  + Providing a shutdown signal to other servers/computers in place of a UPS that does not have a communication function such as BE400 (work in progress)
+ ### Installation method
  + 1. https://wiki.odroid.com/odroid-m1s/application_note/circuitpython#set_environment Follow this link, edit /boot/config.ini and reboot.
  + 2. Run ```bash git clone https://github.com/gunu3371/m1s_ups_control.git```
  + 3. Run ```bash sh install_service.sh```
+ ### How to use
  + Check status with ```systemctl status m1s_ups```
  + Check log in ```/etc/m1s_ups/log/```
