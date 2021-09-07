import getpass
import os

import logging
from selenium.webdriver.remote.remote_connection import LOGGER

from selenium import webdriver
import time

from tkinter import messagebox

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def main():
    global driver
    print("长安大学自动选课助手 V1.0 by 在西安财经大学上学的 HikariLan 贺兰星辰")
    print("本助手基于 Python 3.9 以及 Selenium")
    print("悄咪咪的说，本来我是想用 Java/Kotlin 写的，但是怕人不会运行 Java 应用程序，所以还是用 Python 吧")

    username = input('输入用户名：')
    password = getpass.getpass('输入密码：')

    ke = input("请告诉我们您需要选择的课程序号，使用空格作为分隔符，例如TX110101.04 TX110101.05：").split()

    select_browser = input("请告诉我们您正在使用的浏览器名称，目前可选的值有：Firefox,Chrome,Edge：")

    LOGGER.setLevel(logging.FATAL)

    if select_browser == "Firefox":
        print("选择的浏览器：" + select_browser)
        driver = webdriver.Firefox("drivers/chromedriver.exe")
    elif select_browser == "Chrome":
        print("选择的浏览器：" + select_browser)
        driver = webdriver.Chrome("drivers/geckodriver.exe")
    elif select_browser == "Edge":
        print("选择的浏览器：" + select_browser)
        driver = webdriver.Edge("drivers/MicrosoftWebDriver.exe")
    else:
        print("所选浏览器不存在，请重试！")
        driver.quit()
        exit(0)

    def login():
        driver.find_element_by_id(id_="username").send_keys(username)
        driver.find_element_by_id(id_="password").send_keys(password)

        captcha = driver.find_element_by_id(id_="captchaDiv")
        captcha_class = captcha.get_attribute("class")
        captcha_style = captcha.get_attribute("style")

        if "display: none;" not in captcha_style and "hide" not in captcha_class:
            captcha = input("检测到了需要提供验证码，请输入正确的验证码，然后在这里按回车键继续：")
            driver.find_element_by_id(id_="captcha").send_keys(captcha)

        driver.find_element_by_id(id_="login_submit").click()

    print("加载页面中...")

    driver.get(
        url="http://bkjw.chd.edu.cn/eams/stdElectCourse.action")

    print("页面加载完成")

    login()

    try:
        if "您提供的用户名或者密码有误" in driver.find_element_by_id("showErrorTip").text:
            print("用户名或密码错误，停止程序...")
            driver.quit()
            exit(0)
    except NoSuchElementException:
        print("校验通过")

    try:
        WebDriverWait(driver, 1).until_not(
            EC.presence_of_element_located((By.ID, "login_submit"))
        )
    except TimeoutException:
        print("登陆出错，重试中")
        login()

    print("已完成登录")

    driver.find_element_by_link_text("进入选课>>>>").click()

    original_window = driver.current_window_handle

    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

    for window_handle in driver.window_handles:
        if window_handle != original_window:
            driver.switch_to.window(window_handle)
            break

    xuan_ke_window = driver.current_window_handle

    result = dict()

    def xuan_ke(selected_ke):
        driver.switch_to.window(xuan_ke_window)
        selector = driver.find_element_by_xpath('/html/body/div[10]/div[2]/div[1]/table/thead/tr[1]/th[2]/div/input')
        selector.send_keys(selected_ke)
        selector.send_keys(Keys.ENTER)
        try:
            driver.find_element_by_xpath('/html/body/div[10]/div[2]/div[1]/table/tbody/tr[1]/td[12]/a').click()
            WebDriverWait(driver, 10).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            if "已满" in alert.text:
                print("课程 " + selected_ke + " " + alert.text)
                result[selected_ke] = alert.text
                alert.dismiss()
            elif "冲突" in alert.text:
                print(alert.text)
                result[selected_ke] = alert.text
                alert.dismiss()
            elif "提交" in alert.text:
                print("课程 " + selected_ke + " 已提交")
                result[selected_ke] = "已提交"
                alert.accept()
            elif "重试" in alert.text:
                driver.switch_to.window(xuan_ke_window)
                print("网络出现问题，正在重新选课中...")
                driver.refresh()
                xuan_ke(selected_ke)
            time.sleep(1)
        except NoSuchElementException:
            print("找不到课程" + selected_ke)
            result[selected_ke] = "找不到课程"

    driver.switch_to.window(xuan_ke_window)

    time.sleep(1)

    while True:
        driver.refresh()
        try:
            driver.find_element_by_xpath('/html/body/div[10]/div[2]/div[1]/table/tbody/tr[1]/td[12]/a')
            print("处于选课时间，开始选课")
            break
        except NoSuchElementException:
            print("未到选课时间，持续监听中...")
            time.sleep(5)
            continue

    for item in ke:
        xuan_ke(item)

    driver.quit()

    result_str = ""

    for num in range(len(result.items())):
        k, v = result.popitem()
        result_str += k + ": " + v + "\n"

    messagebox.showinfo("选课结果", result_str)


if __name__ == '__main__':
    main()
    os.system('pause')
