# BASE

sudo apt update
sudo apt install -y \
  build-essential cmake pkg-config git curl wget gnupg lsb-release \
  software-properties-common

sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

sudo apt update
sudo apt install -y python3-pip python3-venv python3-colcon-common-extensions python3-rosdep gnome-terminal



# ROS / GZ
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8

sudo apt install -y software-properties-common
sudo add-apt-repository universe

sudo apt update
sudo apt install -y ros-humble-desktop-full || sudo apt install -y ros-jazzy-desktop-full

echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc

sudo rosdep init
rosdep update

# QGC
sudo usermod -a -G dialout $USER
sudo apt-get remove modemmanager -y
sudo apt install gstreamer1.0-plugins-bad gstreamer1.0-libav gstreamer1.0-gl -y
sudo apt install libfuse2 -y
sudo apt install libxcb-xinerama0 libxkbcommon-x11-0 libxcb-cursor-dev -y

wget https://github.com/mavlink/qgroundcontrol/releases/download/v5.1.0/QGroundControl-x86_64.AppImage
chmod +x ./QGroundControl-x86_64.AppImage
./QGroundControl-x86_64.AppImage


# Plotting Related tools
## Install plotjuggler from source
### deps 
sudo apt -y install qtbase5-dev libqt5svg5-dev libqt5websockets5-dev \
      libqt5serialport5-dev libqt5opengl5-dev libqt5x11extras5-dev libprotoc-dev libzmq3-dev \
      liblz4-dev libzstd-dev python3-dev

wget https://packages.apache.org/artifactory/arrow/$(lsb_release --id --short | tr 'A-Z' 'a-z')/apache-arrow-apt-source-latest-$(lsb_release --codename --short).deb
sudo apt install -y -V ./apache-arrow-apt-source-latest-$(lsb_release --codename --short).deb
sudo apt update
sudo apt install -y -V libarrow-dev libarrow-flight-dev libparquet-dev
