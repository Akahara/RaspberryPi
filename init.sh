
crontab -l > crons
echo "@reboot cd /home/albin/Dev && ./photo.sh" >> crons
crontab crons
rm crons
git config --global user.email "albincalais@gmail.com"
git config --global user.name "Albin"
