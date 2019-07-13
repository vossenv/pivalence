#!/usr/bin/env bash

ipaddresses=(
    "192.168.50.58:pifeed"
)

function deployBash() {


    local username="pi"
    local dir="/home/pi/.pifeed"
    local script='sleep\ 10\;export\ DISPLAY=:0\;/usr/bin/python\ feed.py'

    
    ssh $username@$1 "sudo rm -rf $dir; echo "Creating directory $dir";  sudo mkdir $dir; sudo chmod 777 $dir;"
    printf "\nSending files:\n\n"
    scp ./feed.py ./datasource.py $username@$1:$dir
    ssh $username@$1 'bash -s' < ./install-microservice.sh "$dir" "$script" "$2"


}


for i in ${ipaddresses[@]}; do  

    IFS=':' tokens=(${i});

    host=${tokens[0]}
    nickname=${tokens[1]}

    printf "\n===== Begin deployBash: $nickname / $host =====\n\n"
    deployBash $host $nickname
    printf "===== End deployBash: $nickname / $host =====\n"

done




