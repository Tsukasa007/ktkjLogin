FROM markadams/chromium-xvfb-py3
ADD . /ktkjLogin
WORKDIR /ktkjLogin
VOLUME /ktkjLogin
#ENV  LANG "en_US.UTF-8"
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt && mkdir /ktkjLogin/tmpImage
ENTRYPOINT [ "python3", "auto_login.py"]
