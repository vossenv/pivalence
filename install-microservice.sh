#!/usr/bin/env bash
dir="/home/kloud/.piveilance"
name="piveilance"

echo ""
echo "Initiating install with the parameters:"
echo " - Directory = $dir"
echo ""


echo "Installing the $name service..."


sudo tee /etc/systemd/system/$name.service <<-EOF > /dev/null
#!/usr/bin/env bash
[Unit]
Description=$name Service
[Service]
User=kloud
WorkingDirectory=$dir
ExecStart=/bin/bash $dir/startup.sh
SuccessExitStatus=143
TimeoutStopSec=10
[Install]
WantedBy=multi-user.target
EOF

sudo tee $dir/startup.sh <<-EOF > /dev/null
#!/usr/bin/env bash
sleep 10
export DISPLAY=:0
source venv/bin/activate
piveilance
EOF

sudo systemctl daemon-reload
sudo systemctl enable $name.service
echo ""

echo "----------------------------"
[ ! -d /etc/systemd/system/$name.service ] && echo "Service verified" || echo "Service failed to install"
[ ! -d $dir/startup.sh ] && echo "Startup file verified" || echo "Startup file failed to install"
echo "----------------------------"


sudo chmod 777 -R $dir

echo ""
echo "Attempting to start service"
sudo service $name stop
sudo service $name start

sleep 5
state=$(sudo systemctl is-active $name)

[ "$state" = "active" ] && echo "Service is running, install complete!" || echo "Service not running, attention needed"

echo ""