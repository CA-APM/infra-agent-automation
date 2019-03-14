@echo off
wmic process where "COMMANDLINE LIKE '%%PerfMonCollectorAgent.exe%%'" get Processid^,Commandline^
