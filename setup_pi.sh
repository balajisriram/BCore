#!/bin/bash

# adapted from https://github.com/wehr-lab/autopilot/blob/2to3/autopilot/setup/presetup_pilot.sh

# colors
RED='\033[0;31m'
NC='\033[0m'

# set date
read -p "Enter current date (mm/dd/yyyy hh:mi): " DATE
sudo date -s $DATE


############
# user args

read -p "If you haven't changed it, you should change the default raspberry pi password. Change it now? (y/n): " changepw
if [ "$changepw" == "y" ]; then
    passwd
else
    echo -e "${RED}    not changing password\n${NC}"
fi

read -p "Would you like to set your locale? Use the space bar to select/deselect items on the screen (y/n): " changelocale

if [ "$changelocale" == "y" ]; then
    sudo dpkg-reconfigure locales
    sudo dpkg-reconfigure keyboard-configuration
else
    echo -e "${RED}    not changing locale\n${NC}"
fi

read -p "Install jack audio? (y/n): " installjack

read -p "Setup hifiberry dac/amp? (y/n): " setuphifi

read -p "Setup X11 server and psychopy for visual stimuli? (y/n): " visualstim

read -p "Disable bluetooth? (y/n): " disablebt
###########
# prelims

# create git folder if it don't already exist
TEMPDIR=$HOME/temp
if [ ! -d "$TEMPDIR" ]; then
    echo -e "\n${RED}making git directory at $HOME/temp ${NC}"
    mkdir $TEMPDIR
fi

################
# update and install packages

echo -e "\n\n${RED}Installing necessary packages...\n\n ${NC}"

sudo apt update
sudo apt -y upgrade
sudo apt-get install -y \
    build-essential \
    cmake \
    git \
    python3-pip \
    python3-dev \
    python3-distutils \
    python3-setuptools
    libsamplerate0-dev \
    libsndfile1-dev \
    libreadline-dev \
    libasound-dev \
    i2c-tools \
    libportmidi-dev \
    liblo-dev \
    libhdf5-dev \
    python3-numpy \
    python3-pandas \
    python3-tables \
    libzmq-dev \
    libffi-dev \
    blosc
    
sudo -H pip3 install -U pyzmq npyscreen tornado inputs requests blosc

sudo systemctl disable raspi-config
    
# install pigpio
cd $TEMPDIR
git clone https://github.com/joan2937/pigpio.git
cd pigpio
make -j6
sudo -H make install

#############
# performance

echo -e "\n\n${RED}Doing performance enhancements\n\n ${NC}"

echo -e "\n${RED}Changing CPU governor to performance ${NC}"

# disable startup script that changes cpu governor
# note that this is not the same raspi-config as you're thinking
sudo systemctl disable raspi-config

sudo sed -i '/^exit 0/i echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor' /etc/rc.local

if [ "$disablebt" == "y" ]; then
    echo -e "\n${RED}Disabling bluetooth.. ${NC}"
    sudo sed -i '$s/$/\ndtoverlay=pi3-disable-bt/' /boot/config.txt
    sudo systemctl disable hciuart.service
    sudo systemctl disable bluealsa.service
    sudo systemctl disable bluetooth.service
else
    echo -e "\n${RED}Not disabling bluetooth ${NC}"
fi

############
# audio

if [ "$installjack" == "y" ]; then
    echo "\nInstalling jack audio"
    cd $TEMPDIR
    git clone git://github.com/jackaudio/jack2 --depth 1
    cd jack2
    ./waf configure --alsa=yes --libdir=/usr/lib/arm-linux-gnueabihf/
    ./waf build -j6
    sudo ./waf install
    sudo ldconfig

    # giving jack more juice
    sudo sh -c "echo @audio - memlock 256000 >> /etc/security/limits.conf"
    sudo sh -c "echo @audio - rtprio 75 >> /etc/security/limits.conf"

    # installing jack python packages
    sudo apt-get install -y python-cffi
    sudo -H pip install JACK-Client
fi

#######
# setup visual stim
if [ "$visualstim" == "y" ]; then
    echo -e "\n${RED}Installing X11 Server.. ${NC}"
    sudo apt-get install -y xserver-xorg xorg-dev xinit xserver-xorg-video-fbdev python-opencv mesa-utils

    echo -e "\n${RED}Installing Psychopy dependencies.. ${NC}"
    pip3 install \
        pyopengl \
        pyglet \
        pillow \
        moviepy \
        configobj \
        json_tricks \
        arabic-reshaper \
        astunparse \
        esprima \
        freetype-py \
        gevent \
        gitpython \
        msgpack-numpy \
        msgpack-python \
        pyparallel \
        pyserial \
        python-bidi \
        python-gitlab \
        pyyaml \
        sounddevice \
        soundfile

    echo -e "\n${RED}Compiling glfw... ${NC}"
    cd $TEMPDIR
    git clone https://github.com/glfw/glfw
    cd glfw
    cmake .
    make -j7
    sudo -H make install

    echo -e "\n${RED}Installing Psychopy... ${NC}"

    pip3 install psychopy --no-deps

    sudo sh -c "echo winType = \"glfw\" >> /home/pi/.psychopy3/userPrefs.cfg"
fi
