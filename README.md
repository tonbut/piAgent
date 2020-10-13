# piAgent
A simple python3 agent which monitors many OS operating parameters and presents them as resource on HTTP

Install on Rasberry Pi with
- crontab -e
- @reboot python3 [file location]/piAgent.py

Then when running request state periodically from monitoring infrastructure such as [Polestar](https://github.com/tonbut/Polestar) by requesting 

curl http://localhost:8099/agent

will return
```xml
<agent hostname='BlackPi' rssi='85' diskAvailableMb='3507' freeMemMb='379' loadAverage='1.05' cpuTempC='40.1' uptimeHours='271' updatesAvailable='26' os='Raspbian GNU/Linux 7 (wheezy)'/>
```
