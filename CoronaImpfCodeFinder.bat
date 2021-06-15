:loop 
set VAR_0=0
set VAR_1=1

start /min python Y:\CoronaImpfTermin\repo\CoronaTermin_Auto.py %1 %VAR_0%
timeout /t 60 /nobreak 
goto :loop 