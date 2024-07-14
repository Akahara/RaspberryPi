#!/usr/bin/env bash

SCRIPT_DIR=$( dirname -- "$( readlink -f -- "$0"; )"; )
echo "Installing in $SCRIPT_DIR"

function pi_rootsetup()
{
  echo "postfix postfix/main_mailer_type select Local Only" | sudo debconf-set-selections
  echo "postfix postfix/mailname string wonderpi" | sudo debconf-set-selections
  echo "postfix postfix/destinations string localhost" | sudo debconf-set-selections
  apt-get install -y postfix
  echo "WONDER_PI=1" >> /etc/environment
}

echo | crontab -
#(crontab -l ; echo 'MAILTO=""') | crontab -
(crontab -l ; echo "@reboot cd $SCRIPT_DIR && ./exec_with_logs.sh ./photo.py") | crontab -
(crontab -l ; echo "@reboot cd $SCRIPT_DIR && ./exec_with_logs.sh ./interface.py") | crontab -
chmod a+x *.py *.sh

sudo bash -c "$(declare -f pi_rootsetup); pi_rootsetup"
git config --global user.email "albincalais@gmail.com"
git config --global user.name "Akahara"

if ! grep -q ".rpirc" ~/.bashrc; then
  echo "source $SCRIPT_DIR/.rpirc" >> ~/.bashrc
fi

[ -d "LCD-show" ] || git clone https://github.com/goodtft/LCD-show
chmod -R 755 LCD-show

echo "LCD-show messes up with the camera module (memory issues? see dtoverlay in /boot/config.txt)"
echo "Please reboot and run 'grep Cma /proc/meminfo', if available memory is too low, edit /boot/config.txt and add 'dtoverlay=vc4-kms-v3d,cma-512'"

if [ "$1" = "full" ]; then
  echo "LCD-show disabled"
#  cd LCD-show
#  echo "Running LCD-show, device will reboot"
#  sudo ./LCD35-show
else
  echo "LCD-show was not run, if its the first time you run this script run with 'full' or run ./LCD-show/LCD35-show"
  echo "Setup complete, run 'source .rpirc && restartcron' too simulate a reboot"
fi
