# 方便延时加载
import time
from selenium import webdriver
from PIL import Image, ImageEnhance
import requests
from selenium.webdriver.support.select import Select
import sys
import codecs
import json
import logging


def isElementExist(browser, element):
    flag = True
    try:
        browser.find_element_by_link_text(element)
        return flag

    except:
        flag = False
        return flag


def saveImg(browser, imgPath):
    browser.get_screenshot_as_file(imgPath)

    location = browser.find_element_by_xpath("//*[@id='imgId']").location
    size = browser.find_element_by_xpath("//*[@id='imgId']").size
    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']
    img = Image.open(imgPath).crop((left, top, right, bottom))
    img.save(imgPath)


def get_browser(chrome_driver_dir):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')  # 解决DevToolsActivePort文件不存在的报错
    chrome_options.add_argument('window-size=1280x720')  # 指定浏览器分辨率
    chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
    chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
    # chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
    # chrome_options.add_argument('--headless')  # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
    # 模拟浏览器打开网站
    # browser = webdriver.Chrome(chrome_options=chrome_options)
    browser = webdriver.Chrome(executable_path=chrome_driver_dir, chrome_options=chrome_options)
    browser.set_window_size(1280, 720)
    browser.get('https://ktyw.gdcattsoft.com:8081/ktyw/login.jsp')
    return browser


def start(username, password, check_code_url, chrome_driver_dir, save_img_dir, login_success_url, attendance_url,
          sleep_tiem):
    browser = get_browser(chrome_driver_dir)

    isLogin = False
    isSuccess = False

    while not isLogin:
        logging.info(browser.title)
        # 将窗口最大化
        # browser.maximize_window()

        # 根据路径找到按钮,并模拟进行点击
        # browser.find_element_by_xpath('/html/body/div[1]/div/div[4]/span/a[1]').click()
        # 延时2秒，以便网页加载所有元素，避免之后找不到对应的元素
        time.sleep(sleep_tiem * 5)

        logging.info("输入账号: " + username)
        u = browser.find_element_by_xpath(
            "//*[@id='sAccount']")
        time.sleep(sleep_tiem)
        u.send_keys(username)
        logging.info('输入密码: ' + password)
        time.sleep(sleep_tiem)

        browser.find_element_by_xpath(
            "//*[@id='sPasswd']").send_keys(password)
        time.sleep(sleep_tiem)

        saveImg(browser, save_img_dir)
        logging.info("保存图片")
        # 识别验证码
        files = {'image_file': ("screenImg.png", open(save_img_dir, 'rb'), 'application')}
        r = requests.post(url=check_code_url, files=files)
        verify_code = json.loads(r.text)['value']
        logging.info("识别出验证码: " + verify_code)
        logging.info("填写验证码: " + verify_code)
        time.sleep(sleep_tiem)
        browser.find_element_by_xpath(
            "//*[@id='sValidataCode']").send_keys(verify_code)

        time.sleep(sleep_tiem)

        # 在输入用户名和密码之后,点击登陆按钮
        logging.info("点击登录")
        browser.find_element_by_xpath("//*[@id='LoginButton']").click()
        time.sleep(sleep_tiem)

        if isElementExist(browser, '确定'):
            logging.info("顶人下号")
            browser.find_element_by_link_text('确定').click()
        time.sleep(sleep_tiem)

        if login_success_url in browser.current_url:
            isLogin = True
            logging.info("登录成功!")
            browser.find_element_by_id("tab_content_todoNone")

        else:
            browser.get('https://ktyw.gdcattsoft.com:8081/ktyw/login.jsp')
        time.sleep(sleep_tiem)

    while not isSuccess:
        logging.info("转到签到页面: " + attendance_url)
        browser.get(attendance_url)
        time.sleep(sleep_tiem)
        logging.info("全部打钩")
        browser.find_element_by_class_name("datagrid-header-check").click()
        time.sleep(sleep_tiem)

        logging.info("点击批量签到")
        browser.find_element_by_class_name("edit").click()
        time.sleep(sleep_tiem)

        browser.switch_to.frame(browser.find_element_by_xpath("//iframe[contains(@src,'editAttendanceSign.jsp')]"))
        time.sleep(sleep_tiem)

        # browser.find_element_by_class_name('panel-tool-close').click()
        Select(browser.find_element_by_id('IREASON')).select_by_value("99")
        logging.info("选择其他99")
        time.sleep(sleep_tiem)
        browser.find_element_by_name("SREMARK").send_keys("其他其他!213")
        time.sleep(sleep_tiem * 2)
        browser.find_element_by_css_selector("[class='z-btn-text icon-sub']").click()
        if isElementExist(browser, '操作成功!'):
            browser.close()
            logging.info("签到成功")
            isSuccess = True
        else:
            browser.switch_to.parent_frame()


def main():
    with open("conf/login.json", "r") as f:
        login_conf = json.load(f)
        username = login_conf["username"]
        password = login_conf["password"]
        check_code_url = login_conf["check_code_url"]
        save_img_dir = login_conf["save_img_dir"]
        chrome_driver_dir = login_conf["chrome_driver_dir"]
        login_success_url = login_conf["login_success_url"]
        attendance_url = login_conf["attendance_url"]
        sleep_time = login_conf["sleep_time"]

    start(username, password, check_code_url, chrome_driver_dir, save_img_dir, login_success_url, attendance_url,
          sleep_time)


if __name__ == '__main__':
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    fmt = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s'
    logging.FileHandler(filename='./logs.txt', encoding='utf-8')
    logging.basicConfig(level=logging.INFO,
                        format=fmt,
                        datefmt='%a, %d %b %Y %H:%M:%S')

    main()
