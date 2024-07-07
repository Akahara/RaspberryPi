SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

function pi_rootsetup()
{
  echo | crontab -
  (crontab -l ; echo "@reboot cd $SCRIPT_DIR && ./exec_with_logs.sh ./photo.py") | crontab -
  (crontab -l ; echo "@reboot cd $SCRIPT_DIR && ./exec_with_logs.sh ./interface.py") | crontab -
  chmod a+x *.py *.sh
  echo "WONDER_PI=1" >> /etc/environment
}

export WONDER_PI=1
sudo bash -c "$(declare -f pi_rootsetup); pi_rootsetup"
git config --global user.email "albincalais@gmail.com"
git config --global user.name "Albin"

echo 'alias restartcron="rm /var/run/crond.reboot && systemctl restart cron && sleep .5 && journalctl -u cron.service -n 50 -e"'

echo "Setup complete, run 'restartcron' too simulate a reboot"
