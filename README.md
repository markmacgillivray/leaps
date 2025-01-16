LEAPS
=====

Lothians Equal Access Programme for Schools 

Online questionnaire management software.

Not something that is of any use to anyone else.


Installing the leaps VM
=======================

configure the network host in /etc/network/interfaces, add the following (find the right hardware name if reconfiguring on new vm):
auto ens160
iface ens160 inet static
address 129.215.10.235
netmask 255.255.254.0
gateway 129.215.11.254
dns-nameservers 8.8.8.8 8.8.4.4

sudo apt-get install openssh-server
sudo apt-get install htop

cd
mkdir .ssh
chmod 700 .ssh
mv /root/.ssh/authorized_keys .ssh/
touch .ssh/authorized_keys
chmod 600 .ssh/authorized_keys

Copy any necessary public keys into the authorized_keys file

sudo visudo, and add the following:
leaps ALL=(ALL) NOPASSWD: ALL

sudo vim /etc/ssh/sshd_config and edit:
PermitRootLogin no
PasswordAuthentication no
PubkeyAcceptedKeyTypes=+ssh-dss

sudo service ssh restart

sudo apt-get install nginx

sudo apt-get -q -y install bpython screen git-core python-pip python-dev python-setuptools build-essential python-software-properties

sudo pip install --upgrade pip
sudo pip install --upgrade virtualenv
sudo pip install gunicorn
sudo pip install requests
sudo pip install supervisor

cd /etc/init.d
copied supervisord from my test machine
sudo chmod a+x /etc/init.d/supervisord
sudo chown root:root supervisord
sudo service supervisord stop
sudo update-rc.d supervisord defaults
sudo mkdir /var/log/supervisor
sudo ln -s /usr/local/bin/supervisord /usr/bin/supervisord
cd /etc
sudo mkdir supervisor
cd supervisor
sudo mkdir conf.d
copied supervisord.conf from my test machine
sudo chown root:root supervisord.conf
sudo service supervisord start


Install opensearch
==================



Clone and install LEAPS
=======================

sudo apt-get install libxml2-dev libxslt1-dev libffi-dev weasyprint
# libpango-1.0-0 also required or is weasyprint enough? NOTE apt install weasyprint is necessary even though included in the setup
git clone https://github.com/markmacgillivray/leaps.git
cd leaps
python3 -m venv .venv
cd leaps
source .venv/bin/activate
pip install gunicorn
pip install eventlet
pip install lxml
pip install -e .

# copy the app.cfg from the live service to the new service


Symlink LEAPS nginx and supervisor configs
==========================================

cd /etc/nginx/sites-enabled
sudo ln -s ~/leaps/config/nginx/leaps .
sudo nginx -t
sudo service nginx restart
cd /etc/supervisor/conf.d
sudo ln -s ~/leaps/config/supervisor/leaps.conf .
sudo supervisorctl update


Setup certbot SSL
=================

sudo apt-get update
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
sudo apt-get install python-certbot-nginx
sudo certbot --nginx




