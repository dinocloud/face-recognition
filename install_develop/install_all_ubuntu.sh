#!/bin/bash

command_exists () {
    type "$1" &> /dev/null ;
}

check() {
  if [ $1 -ne 0 ]; then
    print 'Last command failed'
    exit $1
fi
}

#First of all, install python
if command_exists python ; then
    echo "Python already exists, skipping"
else
    echo "Installing dependencies for Python..."
    sudo apt-get install -y wget build-essential checkinstall
    sudo apt-get install -y libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
    echo "Downloading python"
    wget https://www.python.org/ftp/python/2.7.12/Python-2.7.12.tgz
    check $?
    tar -xvf Python-2.7.12.tgz
    cd Python-2.7.12
    echo "Installing python"
    ./configure
    make
    check $?
    sudo checkinstall -y
    check $?
    cd -
fi

#Install pip
if command_exists pip ; then
    echo "Pip already exists, skipping"
else
    echo "Installing pip"
    sudo apt-get install python-pip python-dev build-essential
    check $?
    sudo pip install --upgrade pip
    check $?
fi

#Install OpenCV
echo "Checking if OpenCV is installed"
python -c "import cv2"
if [ $? -ne 0 ]; then
    echo "OpenCV not installed"
    echo "Installing OpenCV dependencies"
    ./dependencies.sh
    check $?
    echo "Downloading and installing OpenCV"
    ./opencv.sh
    check $?
else
    echo "OpenCV already installed... skipping"
fi

#Install numpy
echo "Checking if numpy is installed"
pip freeze | grep "numpy==1.11.2"
if [ $? -ne 0 ]; then
    echo "Installing numpy"
    sudo pip install numpy==1.11.2
    check $?
else
    echo "Numpy already installed... exiting"
fi

echo "All steps were successful.. environment ready"

