FROM python:2.7

# Updating packages and installing basic ones
RUN apt-get update -y
RUN apt-get install -y wget build-essential checkinstall libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev

RUN apt-get install -y python-pip python-dev
RUN pip install --upgrade pip

COPY install_develop/dependencies.sh /install_develop/dependencies.sh
# Installing dependencies for OpenCV
RUN cd /install_develop && bash dependencies.sh

# Installing OpenCV
RUN mkdir /opencv && cd /opencv && wget -O OpenCV-3.1.0.zip http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/3.1.0/opencv-3.1.0.zip/download && \
    unzip OpenCV-3.1.0.zip && cd opencv-3.1.0 && mkdir build && cd build && cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D WITH_TBB=ON -D BUILD_NEW_PYTHON_SUPPORT=ON \
     -D WITH_V4L=ON -D INSTALL_C_EXAMPLES=ON -D INSTALL_PYTHON_EXAMPLES=ON -D BUILD_EXAMPLES=ON -D WITH_QT=ON -D WITH_OPENGL=ON .. && make -j2 && checkinstall -y && \
     sh -c 'echo "/usr/local/lib" > /etc/ld.so.conf.d/opencv.conf' && ldconfig

#Adding software and installing pip requirements
#COPY vader /vader
#RUN cd /vader && pip install -r requirements.txt

#CMD "python /vader/app.py"

