:loop 
set VAR_0=0
set VAR_1=1

start /min python Y:\CoronaImpfTermin\repo\CoronaTermin_Auto.py %1 %VAR_1%

timeout /t 300 /nobreak 
goto :loop 