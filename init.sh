#!/usr/bin/env bash

SCRIPT_DIR=$( dirname -- "$( readlink -f -- "$0"; )"; )
echo "Installing in $SCRIPT_DIR"

function pi_rootsetup()
{
  SCRIPT_DIR=$( dirname -- "$( readlink -f -- "$0"; )"; )
  echo "postfix postfix/main_mailer_type select Local Only" | sudo debconf-set-selections
  echo "postfix postfix/mailname string wonderpi" | sudo debconf-set-selections
  echo "postfix postfix/destinations string localhost" | sudo debconf-set-selections
  apt-get install -y postfix
  echo | crontab -
  (crontab -l ; echo 'MAILTO=""') | crontab -
  (crontab -l ; echo "@reboot cd $SCRIPT_DIR && ./exec_with_logs.sh ./photo.py") | crontab -
  (crontab -l ; echo "@reboot cd $SCRIPT_DIR && ./exec_with_logs.sh ./interface.py") | crontab -
  chmod a+x *.py *.sh
  echo "WONDER_PI=1" >> /etc/environment
}

sudo bash -c "$(declare -f pi_rootsetup); pi_rootsetup"
git config --global user.email "albincalais@gmail.com"
git config --global user.name "Akahara"

if ! grep -q ".rpirc" ~/.bashrc; then
  echo "source $SCRIPT_DIR/.rpirc" >> ~/.bashrc
fi

echo "Setup complete, run 'source .rpirc && restartcron' too simulate a reboot"
