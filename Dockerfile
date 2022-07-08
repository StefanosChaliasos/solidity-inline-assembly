FROM ubuntu:18.04

ENV TZ=Europe/Athens
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt update -yq && apt upgrade -yq
RUN apt install -y vim software-properties-common git curl unzip zip sudo \
    sqlite3 wget unzip locales jq cloc texlive-latex-extra \
    dvipng texlive-latex-extra texlive-fonts-recommended cm-super
RUN sudo locale-gen "en_US.UTF-8"
RUN update-locale LC_ALL="en_US.UTF-8"
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt -yqq update && \
    apt -yqq install python3.9 python3-pip && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
RUN apt install -yq python3.9-distutils


# Install missing python packages
RUN pip3 install --upgrade setuptools
RUN pip3 install --upgrade setuptools
RUN pip3 install --upgrade distlib
RUN pip3 install --upgrade pip
RUN pip3 install seaborn pandas matplotlib

# Create the inline user.
RUN useradd -ms /bin/bash inline && \
    echo inline:inline | chpasswd && \
    cp /etc/sudoers /etc/sudoers.bak && \
    echo 'inline ALL=(ALL:ALL) NOPASSWD:ALL' >> /etc/sudoers
USER inline
ENV HOME /home/inline
WORKDIR ${HOME}

RUN touch ${HOME}/.bash_profile
RUN echo "source ${HOME}/.bash_profile" >> ${HOME}/.bashrc
RUN echo 'export LANG="en_US.UTF-8"' >> ${HOME}/.bashrc

# Add scripts and requirements.txt
ADD ./scripts ${HOME}/scripts
ADD ./requirements.txt ${HOME}/requirements.txt

RUN sudo chown -R inline:inline ${HOME}/scripts
RUN sudo chown -R inline:inline ${HOME}/requirements.txt

# Install Python dependencies
RUN pip3 install -r requirements.txt

WORKDIR ${HOME}
