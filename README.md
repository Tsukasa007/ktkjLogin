##快速开始
```shell script
yum install https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
wget https://npm.taobao.org/mirrors/chromedriver/2.40/chromedriver_linux64.zip


修改 conf/login.json
 "chrome_driver_dir": "C:\\chromedriver.exe" 为chromedriver_linux64.zip解压文件路径

pip3 install -r requirements.txt

自己设置任务
python3 auto_login.py
```

