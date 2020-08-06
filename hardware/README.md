# Installing OpenCV, dlib and face_recognition on a Raspberry Pi

Instructions tested with a Raspberry Pi 2 Model B. Probably also works fine on other models.


### Step 0

Download the [latest Raspbian Jessie Light](https://www.raspberrypi.org/downloads/raspbian/) image. Earlier versions of Raspbian won't work.

Write it to a memory card using [Etcher](https://etcher.io/), put the memory card in the RPi and boot it up.

Log in. Default username / password is `pi` / `raspberry`.

Run sudo `raspi-config`, configure the basics, particularly:

- Enable the Raspberry Pi camera (if you have one attached)
- Configure gpu memory split under 'Advanced'. Set it up '16'.

Save changes and reboot.

Prepping the system for the installation.

```sh
sudo apt-get -y purge wolfram-engine
sudo apt-get -y purge libreoffice*
sudo apt-get -y clean
sudo apt-get -y autoremove

cvVersion="master"

# clean build directories
rm -rf opencv/build
rm -rf opencv_contrib/build

# create directory for installation
mkdir installation
mkdir installation/OpenCV-"$cvVersion"

# storing current working directory
cwd=$(pwd)

# update packages
sudo apt -y update
sudo apt -y upgrade

# installing OS dependencies
sudo apt-get -y remove x264 libx264-dev

sudo apt-get -y install build-essential checkinstall cmake pkg-config yasm
sudo apt-get -y install git gfortran
sudo apt-get -y install libjpeg8-dev libjasper-dev libpng12-dev
sudo apt-get -y install libtiff5-dev
sudo apt-get -y install libtiff-dev
sudo apt-get -y install libavcodec-dev libavformat-dev libswscale-dev libdc1394-22-dev
sudo apt-get -y install libxine2-dev libv4l-dev
cd /usr/include/linux
sudo ln -s -f ../libv4l1-videodev.h videodev.h
cd $cwd

sudo apt-get -y install libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev
sudo apt-get -y install libgtk2.0-dev libtbb-dev qt5-default
sudo apt-get -y install libatlas-base-dev
sudo apt-get -y install libmp3lame-dev libtheora-dev
sudo apt-get -y install libvorbis-dev libxvidcore-dev libx264-dev
sudo apt-get -y install libopencore-amrnb-dev libopencore-amrwb-dev
sudo apt-get -y install libavresample-dev
sudo apt-get -y install x264 v4l-utils

# optional dependencies
sudo apt-get -y install libprotobuf-dev protobuf-compiler
sudo apt-get -y install libgoogle-glog-dev libgflags-dev
sudo apt-get -y install libgphoto2-dev libeigen3-dev libhdf5-dev doxygen

# install python
sudo apt-get -y install python3-dev python3-pip
sudo -H pip3 install -U pip numpy
sudo apt-get -y install python3-testresources
```

Install `virtualenv` and `virtualenvwrapper`:

```sh
cd $cwd
python3 -m venv OpenCV-"$cvVersion"-py3
echo "# virtualenv wrapper" >> ~/.bashrc
echo "alias workoncv-$cvVersion=\"source $cwd/OpenCV-$cvVersion-py3/bin/activate\"" >> ~/.bashrc
source "$cwd"/OpenCV-"$cvVersion"-py3/bin/activate
```

Temporarily enable a larger swap file size (so the dlib compile won't fail due to limited memory):

```sh
sudo sed -i 's/CONF_SWAPSIZE=100/CONF_SWAPSIZE=1024/g' /etc/dphys-swapfile
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start
```

Finally, we are ready to install the libraries:

```sh
sudo pip3 install numpy dlib
# install the picamera python library with array support
sudo apt-get install python3-picamera
sudo pip3 install --upgrade picamera[array]
# installing face_recognition
sudo pip3 install face_recognition
deactivate
```

Cloning and compiling `opencv` and `opencv_contrib`:

```sh
git clone https://github.com/opencv/opencv.git
cd opencv
git checkout $cvVersion
cd ..

git clone https://github.com/opencv/opencv_contrib.git
cd opencv_contrib
git checkout $cvVersion
cd ..

cd opencv
mkdir build
cd build

cmake -D CMAKE_BUILD_TYPE=RELEASE \
            -D CMAKE_INSTALL_PREFIX=$cwd/installation/OpenCV-"$cvVersion" \
            -D INSTALL_C_EXAMPLES=ON \
            -D INSTALL_PYTHON_EXAMPLES=ON \
            -D WITH_TBB=ON \
            -D WITH_V4L=ON \
            -D OPENCV_PYTHON3_INSTALL_PATH=$cwd/OpenCV-$cvVersion-py3/lib/python3.5/site-packages \
            -D WITH_QT=ON \
            -D WITH_OPENGL=ON \
            -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules \
            -D BUILD_EXAMPLES=ON ..

make -j$(nproc)
make install
```

> Note: For system wide installation of OpenCV, change `CMAKE_INSTALL_PREFIX` to `CMAKE_INSTALL_PREFIX=/usr/local \.`

Once we are done installing, it's time to reset swap file,

```sh
sudo sed -i 's/CONF_SWAPSIZE=1024/CONF_SWAPSIZE=100/g' /etc/dphys-swapfile
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start
```

We also need to add a simple statement to make sure that VideoCapture(0) works on our Raspberry Pi,

```sh
echo "sudo modprobe bcm2835-v4l2" >> ~/.profile
```

> Note: Better way to do it would be to add the line to `/etc/modules` to get the kernel to insert the module on boot automatically: `bcm2835-v4l2" | tee -a /etc/modules`

Yahoo! Now you can use OpenCV without any hitch (hopefully) by hopping into the venv using `workon OpenCV-master-py3`,

```py
import cv2
print(cv2.__version__)
```

> For me, compiling dlib took about 8 hours, while OpenCV was completed in roughly 3 hours.

#### Performance optimization techniques

- Only detect faces in 1/4 frame of video
- Processing each video frame at 1/5 resolution (though still display it at full resolution)