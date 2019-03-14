@echo off
wmic process where "COMMANDLINE LIKE '%%UnifiedMonitoringAgent.jar%%'" get Processid^,Commandline^ | findstr /c:"%cd%\jre\bin\java"
