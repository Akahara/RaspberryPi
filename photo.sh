mkdir -p logs
printf -v logfile '%(logs/%Y-%m-%d-%H-%M-%S.txt)T\n' -1
./photo.py 2>&1 | tee $logfile
