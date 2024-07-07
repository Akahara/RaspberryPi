mkdir -p logs
printf -v logfile "%(logs/$1-%Y-%m-%d-%H-%M-%S.txt)T\n" -1
$@ 2>&1 | tee $logfile
