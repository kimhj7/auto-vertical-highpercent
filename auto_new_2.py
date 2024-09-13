import time
import subprocess
import tkinter.messagebox
import tkinter.scrolledtext as scrolledtext
import math
from tkinter.font import Font

import socketio

import os
import sys
import re

import requests
import uuid
import playsound

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox, Toplevel

from pathlib import Path

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r".\assets\frame0")

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException, StaleElementReferenceException, \
    WebDriverException
from screeninfo import get_monitors
from selenium_stealth import stealth
import threading
import random

options = ChromeOptions()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.183 Safari/537.36"
options.add_argument('user-agent=' + user_agent)
options.add_argument("lang=ko_KR")
options.add_argument('--window-size=1920,1020')

monitors = get_monitors()
if monitors[0].width < 1367:
    options.add_argument("force-device-scale-factor=0.45")
    options.add_argument("high-dpi-support=0.45")
elif monitors[0].width > 1367 and monitors[0].width < 1610:
    options.add_argument("force-device-scale-factor=0.6")
    options.add_argument("high-dpi-support=0.6")
elif monitors[0].width > 1610 and monitors[0].width < 1900:
    options.add_argument("force-device-scale-factor=0.63")
    options.add_argument("high-dpi-support=0.63")
elif monitors[0].width > 1900 and monitors[0].width < 2500:
    options.add_argument("force-device-scale-factor=0.65")
    options.add_argument("high-dpi-support=0.65")
elif monitors[0].width > 2500 and monitors[0].width < 3000:
    options.add_argument("force-device-scale-factor=0.9")
    options.add_argument("high-dpi-support=0.9")
elif monitors[0].width > 3000:
    options.add_argument("force-device-scale-factor=1.3")
    options.add_argument("high-dpi-support=1.3")

options.add_experimental_option("detach", True)


def resource_path(relative_path):
    """ 리소스의 절대 경로를 얻기 위한 함수 """
    try:
        # PyInstaller가 생성한 임시 폴더에서 실행 중일 때의 경로
        base_path = sys._MEIPASS
    except Exception:
        # 일반적인 Python 인터프리터에서 실행 중일 때의 경로
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# 크롬 드라이버 최신 버전 설정
driver_path = ChromeDriverManager().install()
if driver_path:
    driver_name = driver_path.split('/')[-1]
    if driver_name != "chromedriver":
        driver_path = "/".join(driver_path.split('/')[:-1] + ["chromedriver.exe"])
        if '/' in driver_path:
            driver_path = driver_path.replace('/', '\\')
        os.chmod(driver_path, 0o755)

# chrome driver
# driver = webdriver.Chrome(service=service, options=options)  # <- options로 변경
# driver2 = webdriver.Chrome(service=service, options=options)  # <- options로 변경


last_opened_window_handle = True

set_hours = 72
serial_number = 'DPAUTO1'


def recode_log(serial, type, start_price, current_price, bet_price, title, room, status, step, round, cal):
    url = "https://log2.pattern2024.com/log"
    datas = {
        'serial': serial,
        'type': type,
        'start_price': start_price,
        'current_price': current_price,
        'bet_price': bet_price,
        "title": title,
        "room": room,
        "status": status,
        "step": step,
        "round": round,
        "benefit": cal
    }

    requests.post(url, data=datas)


def pause_control(status):
    url = "https://patternlog.platform-dev.xyz/pause_control.php"
    datas = {
        'serial': serial_number,
        "status": status,
    }

    res = requests.post(url, data=datas)
    res1 = res.text
    return res1


def martin_set_zero():
    url = "https://patternlog.platform-dev.xyz/martin_set_zero.php"
    datas = {
        'serial': serial_number,
    }

    res = requests.post(url, data=datas)


def martin_set_load():
    url = "https://patternlog.platform-dev.xyz/martin_set_load.php"
    datas = {
        'serial': serial_number,
    }

    res = requests.post(url, data=datas)
    res2 = res.text
    return res2


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


def resource_path(relative_path):
    """ 리소스의 절대 경로를 얻기 위한 함수 """
    try:
        # PyInstaller가 생성한 임시 폴더에서 실행 중일 때의 경로
        base_path = sys._MEIPASS
    except Exception:
        # 일반적인 Python 인터프리터에서 실행 중일 때의 경로
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_current_drive_serial():
    try:
        # wmic 명령어 실행하여 시리얼 번호 가져옴
        result = subprocess.run(["wmic", "diskdrive", "get", "SerialNumber"], capture_output=True, text=True,
                                check=True)
        lines = result.stdout.strip().split('\n')

        # 지정한 시리얼 번호 확인
        specified_serial = "121220160204"  # 여기에 지정한 시리얼 번호를 추가하세요
        for line in lines:
            if specified_serial in line:
                return True

        return None
    except Exception as e:
        print("디스크 드라이브의 시리얼 번호를 가져오는 데 문제가 발생했습니다:", e)
        return None


def get_external_ip():
    response = requests.get('https://httpbin.org/ip')
    ip = response.json()['origin']
    return ip


def get_mac_address():
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2 * 6, 2)][::-1])
    return mac


def set_chrome_window_size(driver, width, height, x_offset=0, y_offset=0):
    driver.set_window_position(x_offset, y_offset)
    driver.set_window_size(width, height)


def reset(driver, driver2):
    last_window_handle = driver.current_window_handle
    update_completed = False
    while True:
        # 업데이트가 완료된 경우 루프 중지
        if update_completed:
            break

        try:
            # 현재 열려 있는 모든 창의 핸들 가져오기
            window_handles = driver.window_handles

            # 새 창이 열렸는지 확인
            for window_handle in window_handles:
                if window_handle != last_window_handle:
                    # 새로 열린 창으로 전환
                    driver.switch_to.window(window_handle)

                    # 새 창의 URL 확인
                    current_url = driver.current_url

                    # URL에 특정 파라미터가 포함되어 있는지 확인
                    if "game=baccarat" in current_url:
                        print("특정 파라미터가 포함된 새 창 URL:", current_url)
                        time.sleep(3)
                        driver.switch_to.frame(driver.find_element(By.TAG_NAME, "iframe"))
                        time.sleep(3)
                        elem = driver.find_element(By.CLASS_NAME, 'roadGrid--bd5fc')
                        # inputdoublex(elem, driver, driver2)
                        crawlresult(driver, driver2)

                        update_completed = True

            # 리소스 사용 최소화를 위해 잠시 대기
            time.sleep(1)
        except KeyboardInterrupt:
            # 사용자가 Ctrl+C를 누르면 루프 종료
            break


step = 0
step_order = []
price_number2 = 0
start_price = 0
current_price = 0
cal = 0
s_bet = False

selected_index = 0
selected_type = 1

lose = False
start = True
re_start = False

d_title = ""
r_title = ""

profit_stop2 = 0
loss_stop2 = 0

group_level = 1

group1_sum = 0
group2_get = 0
group2_get_sum = 0

stop_group_level = 1
stop_step = 1

betstop = False
tie_values = [1000, 1000, 1000, 1000, 1000, 1000, 1000, 2000, 2000, 2000, 3000, 3000, 3000, 4000, 4000, 5000, 6000,
              7000, 8000, 9000, 10000, 11000, 13000, 15000, 17000, 19000, 22000, 25000, 29000, 33000, 38000, 43000,
              49000, 56000, 65000, 74000, 84000, 97000, 110000, 126000]
tie_auto_value = False
tie_step = 0
long_stop_w = True
long_stop_w2 = True
long_stop_value = 3
long_stop_value2 = 3
pause_status = False
pause_status2 = False
pause_step = 0
check_type = ""
go_bonus = False
side_bet = True
vbet_amount = 0
vbet_data = []
order = []
order_index = 0
martin_kind = ""
element_length = 0

long_go_o = False
long_go_x = False

round = ""
change_on = False
change_no = 0
step_o = 0
vbet_key = ""
current_int = 0
bet_type = 0
stop_check = False
stop_check2 = False
next_value = 0
profit_stop = False

base_price = 0
sum_price = 0
betting_price = 0


def start_autobet():
    global lose, s_bet, betstop, step_order, next_value

    pause_control(0)

    martin_set_zero()

    print("오토시작")

    s_bet = True
    lose = False
    betstop = False
    step_order = [0] * len(vbet_data)
    next_value = 0

    s = "오토프로그램 시작"
    entry_25.insert(tk.END,
                    "==================================\n%s\n==================================\n\n" % s.center(
                        30))
    entry_25.see(tk.END)
    recode_log(serial_number, 'START', start_price, current_price, 0, d_title, r_title, "", "", "", cal)

    if re_start:
        entry_25.insert(tk.END, str(stop_step) + "마틴부터 다시 시작\n\n")
        entry_25.see(tk.END)


def stop_autobet():
    global check_type, cal

    print("오토정지")
    global s_bet, step, current_price, re_start, step_order, next_value

    re_start = True
    s_bet = False
    next_value = 0
    check_type = ""
    step_order = [0] * len(vbet_data)
    s = "패턴 오토프로그램 일시정지"
    entry_25.insert(tk.END,
                    "==================================\n%s\n==================================\n\n\n" % s.center(30))
    entry_25.see(tk.END)
    try:
        current_price = driver.find_element(By.CSS_SELECTOR, '.amount--bb99f span').get_attribute('innerText').strip()
        price_number = re.sub(r'[^0-9.]', '', current_price)
        cal = int(float(price_number)) - int(float(price_number2))
    except:
        print("오류")
    recode_log(serial_number, 'STOP', start_price, current_price, 0, d_title, r_title, "", "", round, cal)
    time.sleep(1)
    try:
        current_price = driver.find_element(By.CSS_SELECTOR, '.amount--bb99f span').get_attribute('innerText').strip()
        price_number = re.sub(r'[^0-9.]', '', current_price)
        cal = int(float(price_number)) - int(float(price_number2))
    except:
        print("오류")
    recode_log(serial_number, 'STOP_PRICE_CHECK', start_price, current_price, 0, d_title, r_title, "", "", round, cal)
    time.sleep(2)
    try:
        current_price = driver.find_element(By.CSS_SELECTOR, '.amount--bb99f span').get_attribute('innerText').strip()
        price_number = re.sub(r'[^0-9.]', '', current_price)
        cal = int(float(price_number)) - int(float(price_number2))
    except:
        print("오류")
    recode_log(serial_number, 'STOP_PRICE_CHECK', start_price, current_price, 0, d_title, r_title, "", "", round, cal)


profit_stop_count = 1


def profit_stop_func():
    print("수익으로 인한 1마틴 복귀")
    global step_order, profit_stop, profit_stop_count
    step_order = [0] * len(vbet_data)
    s = "수익으로 인한 전체 마틴단계 1단계 복귀"
    entry_25.insert(tk.END,
                    "==================================\n%s\n==================================\n\n\n" % s.center(30))
    entry_25.see(tk.END)
    profit_stop_count += 1


def loss_stop_func():
    print("손실로 인한 오토정지")
    global s_bet, step, start
    s_bet = False
    step = []
    start = True
    s = "손실로 인한 오토프로그램 정지"
    entry_25.insert(tk.END,
                    "========================================\n%s\n========================================\n\n\n" % s.center(
                        30))
    entry_25.see(tk.END)
    recode_log('LOSS_STOP', start_price, current_price, 0, d_title, r_title, "", "", round, cal)


x_stop = False
t_check = ""
tie_on = False
last_tie_step = 0


def chip_selection(price, c_res, step, round, bonus, vname):
    global current_price

    bet_price = int(price)
    price = int(price)
    print(price)
    # 칩 값과 이름을 튜플 리스트로 저장
    chips = [
        (500000, '6'),
        (100000, '5'),
        (25000, '4'),
        (5000, '3'),
        (2000, '2'),
        (1000, '1')
    ]

    # 결과를 저장할 문자열
    result = []

    for value, name in chips:
        if price >= value:
            count = price // value  # 해당 칩으로 몇 개 살 수 있는지 계산
            price %= value  # 남은 금액 계산
            if count > 0:
                result.append(f"{name}번칩 {int(count)}개")
                css_selector = f".expandedChipStack--0a379 > div:nth-child({name})"
                chip = driver.find_element(By.CSS_SELECTOR, css_selector)
                chip.click()
                for i in range(int(count)):
                    if betstop:
                        entry_25.insert(tk.END, ("실제 칩 배팅 정지중..\n\n"))
                        entry_25.see(tk.END)
                    else:
                        if bonus == "bonus":
                            click_chip2(c_res)
                        else:
                            click_chip(c_res)

    # 결과 출력
    if c_res == "T":
        entry_25.insert(tk.END, ("※※ " + ", ".join(result) + "🟢 TIE에 " + str(
            bet_price) + "원 배팅 ※※\n\n=================================\n\n"), "green")
        entry_25.see(tk.END)
    else:
        current_price = driver.find_element(By.CSS_SELECTOR, '.amount--bb99f span').get_attribute('innerText').strip()
        if bonus == "bonus":
            if c_res == "B":
                tx = "BANKER BONUS"
            elif c_res == "P":
                tx = "PLAYER BONUS"
            entry_25.insert(tk.END, (", ".join(result) + " " + tx + "" + vname + " 에 " + str(
                bet_price) + "원 배팅\n\n=================================\n\n"))
            entry_25.see(tk.END)
            recode_log(vname, 'RUNNING', start_price, current_price, bet_price, d_title, r_title, tx, step, round, cal)
        else:
            entry_25.insert(tk.END, (", ".join(result) + " " + c_res + " " + vname + " 에 " + str(
                bet_price) + "원 배팅\n\n=================================\n\n"))
            entry_25.see(tk.END)
            recode_log(vname, 'RUNNING', start_price, current_price, bet_price, d_title, r_title, c_res, step, round,
                       cal)


def click_chip(chip):
    # 'chip'의 값에 따라 특정 동작을 수행
    if chip == "P":
        player_area.click()  # 'P'일 경우, player_area를 클릭
    elif chip == "B":
        banker_area.click()  # 'B'일 경우, banker_area를 클릭
    elif chip == "T":
        tie_area.click()


def click_chip2(chip):
    # 'chip'의 값에 따라 특정 동작을 수행
    if chip == "P":
        player_bonus.click()  # 'P'일 경우, player_bonus를 클릭
    elif chip == "B":
        banker_bonus.click()  # 'B'일 경우, banker_bonus를 클릭


def confirm_action():
    messagebox.showinfo("결과", "마틴단계 계속진행")


def cancel_action():
    global step, start
    step = []
    start = True
    messagebox.showinfo("결과", "마틴단계 1단계로 복귀")


def stop_action():
    stop_autobet()
    messagebox.showinfo("결과", "프로그램 일시정지")


def stop_bet():
    global betstop
    betstop = True
    entry_25.insert(tk.END, (
        "=======================================\n실제 칩 배팅 정지\n=======================================\n\n"))
    entry_25.see(tk.END)


def random_choice():
    return random.choice([1, 3])


def autoBet(driver, driver2):
    martin_list = ['base', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th']

    if s_bet:

        global step, x_stop, lose, start, current_price, t_check, last_tie_step, group_level, player_area, banker_area, player_bonus, banker_bonus, group2_get, group2_get_sum, tie_on, re_start, win_stack, ask_dialog, tie_step, tie_area, stop_check, stop_check2, stop_check4, lose_stack, stop_step2, check_type, check_kind, compare_mybet, highest_variable, element_length, previously_selected, current_group, long_go_o, long_go_x, round, cal, change_on, change_no, order_index, martin_kind, step_o, vbet_key, current_int, next_value, step_order, order_index, betting_price, sum_price

        player_area = driver.find_element(By.CSS_SELECTOR, '.player--d9544')
        banker_area = driver.find_element(By.CSS_SELECTOR, '.banker--7e77b')
        tie_area = driver.find_element(By.CSS_SELECTOR, '.tie--a582d')
        current_price = driver.find_element(By.CSS_SELECTOR, '.amount--bb99f span').get_attribute('innerText').strip()
        round = driver2.find_element(By.CSS_SELECTOR, '.result1 .current_no').get_attribute('innerText').strip()

        price_number = re.sub(r'[^0-9.]', '', current_price)
        cal = int(float(price_number)) - int(float(price_number2))
        positive_cal = cal * -1
        if betting_price == 0:
            betting_price = base_price

        entry_1.config(state='normal')
        entry_2.config(state='normal')
        entry_2.delete(0, tkinter.END)
        entry_2.insert(0, price_number)
        entry_1.delete(0, tkinter.END)
        entry_1.insert(0, cal)
        entry_1.config(state='readonly')
        entry_2.config(state='readonly')
        try:
            check_ox = driver2.find_element(By.CSS_SELECTOR,
                                            '.result.active .pattern2 > ul:last-child > li:last-child p')
            ox = check_ox.get_attribute('innerHTML').strip()
            check_type = driver2.find_element(By.CSS_SELECTOR, '.result.active .tc.active').get_attribute('data-type')
            check_kind = driver2.find_element(By.CSS_SELECTOR, '.result.active').get_attribute('data-kind')
            if check_type == "O":
                current_res = driver2.find_element(By.CSS_SELECTOR, '.result.active .o-pattern .to-result')
            elif check_type == "X":
                current_res = driver2.find_element(By.CSS_SELECTOR, '.result.active .x-pattern .to-result')
            c_res = current_res.get_attribute('innerHTML').strip()
            tie_check = driver2.find_element(By.CSS_SELECTOR, '.result.active .current_res .ball')
            t_check = tie_check.get_attribute('innerHTML').strip()

            try:
                element_length = len(driver2.find_elements(By.CSS_SELECTOR, '.result1 .pattern2 > ul > li'))
                stop_check1 = driver2.find_element(By.CSS_SELECTOR,
                                                   '.result.active .pattern2 > ul:last-child > li:last-child p').get_attribute(
                    'innerHTML').strip()
            except NoSuchElementException:
                element_length = 0
                stop_check1 = False

            if check_type == "O":

                if (cal > 0) and (profit_stop2 != 0 and profit_stop2 * profit_stop_count < cal):
                    profit_stop_func()

                elif (stop_check1 and stop_check1 == "X") and bet_type == 1:
                    entry_25.insert(tk.END, ("역패턴 정지\n"))
                    entry_25.see(tk.END)
                    recode_log(vbet_key, 'LONG_STOP', start_price, current_price, 0, d_title, r_title, "", "", round,
                               cal)
                    stop_check = True
                else:
                    if lose:
                        next_value = next_value
                        step_order[next_value] = 0
                        lose = False
                        next_value = show_next_order()

                    else:
                        if bet_type != 2:
                            if t_check == "TIE":
                                next_value = next_value
                            else:
                                next_value = show_next_order()
                        if bet_type == 2 and ox == "X":
                            next_value = show_next_order()
                        elif bet_type == 2 and ox == "O":
                            if start:
                                next_value = show_next_order()
                            else:
                                next_value = next_value
                        if re_start or start:
                            next_value = 0
                            order_index = 1
                            step_order = [0] * len(vbet_data)

                    if not start:
                        print("합계를 비교하여 단계를 높힐지 1로 돌릴지")
                        print("합계 금액 : " + str(sum_price))
                        if next_value == 0:
                            if sum_price > 0:
                                next_value = 0
                                order_index = 1
                                step_order = [0] * len(vbet_data)
                                betting_price = base_price
                                sum_price = 0
                                entry_25.insert(tk.END,
                                                (
                                                        "=================================\n\n그룹 합계 수익, 전체 배팅 금액 " + str(
                                                    betting_price) + "원 배팅\n\n=================================\n\n"))
                                entry_25.see(tk.END)
                            elif sum_price < 0:
                                step_order = [x + 1 for x in step_order]
                                betting_price = abs(sum_price) + base_price
                                entry_25.insert(tk.END,
                                                (
                                                        "=================================\n\n그룹 합계 손실, 손실 긍액 : "+str(sum_price)+" 전체 배팅 금액 " + str(
                                                    betting_price) + "원 배팅(손실금+베이스)\n\n=================================\n\n"))
                                entry_25.see(tk.END)
                        elif next_value != 0 and step_order[0] > 0:
                            if sum_price > 0:
                                next_value = 0
                                order_index = 1
                                step_order = [0] * len(vbet_data)
                                betting_price = base_price
                                sum_price = 0
                                entry_25.insert(tk.END,
                                                (
                                                        "=================================\n\n그룹 합계 수익, 전체 배팅 금액 " + str(
                                                    betting_price) + "원 배팅\n\n=================================\n\n"))
                                entry_25.see(tk.END)

                    vbet_key = vbet_keys[next_value]
                    martin_kind = vbet_data[vbet_key]['martin_kind']
                    betting = vbet_data[vbet_key]['betting']
                    current_position = vbet_key[-1]
                    current_int = int(current_position)
                    step_o = step_order[next_value]
                    current_vmachine.delete(0, tkinter.END)
                    current_vmachine.insert(tk.END, vbet_key)
                    driver2.find_element(By.CSS_SELECTOR, f".{vbet_key} .vmachine-name").click()

                    # blink_text(vbet_key)
                    print(step_o, step_order)
                    if ox == "X":
                        if bet_type == 0 or bet_type == 2 or bet_type == 3:
                            if check_kind == "A":
                                driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                                time.sleep(0.2)
                                driver2.find_element(By.CSS_SELECTOR, '.result1 .tc2').click()
                            elif check_kind == "B":
                                driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                time.sleep(0.2)
                                driver2.find_element(By.CSS_SELECTOR, '.result2 .tc2').click()
                            elif check_kind == "C":
                                driver2.find_element(By.CSS_SELECTOR, '.result3').click()
                                time.sleep(0.2)
                                driver2.find_element(By.CSS_SELECTOR, '.result3 .tc2').click()
                            current_res = driver2.find_element(By.CSS_SELECTOR, '.result.active .x-pattern .to-result')
                            c_res = current_res.get_attribute('innerHTML').strip()
                            check_type = "X"

                        if t_check == "TIE":
                            if lose:
                                step_o = last_tie_step
                                last_tie_step = 0
                                lose = False
                            else:
                                step_o = step_o
                                tie_on = True
                                print("step유지")
                        else:
                            if lose:
                                step_o = 0

                            if start:
                                step_o = 0

                        if re_start:
                            re_start = False

                        entry_25.insert(tk.END, (str(step_o + 1) + "마틴 진행\n"))
                        entry_25.see(tk.END)

                        if bet_type == 3:
                            for i in range(10):
                                if step_o == i:
                                    if selected_index == i + 1:
                                        lose = True
                                        last_tie_step = step
                                        tie_on = True
                                    print("OO")
                                    chip_selection(betting_price, c_res, step_o, round, "", vbet_key)
                                    break  # 일치하는 조건을 찾으면 반복문을 종료
                        else:
                            for i in range(10):
                                if step_o == i:
                                    if selected_index == i + 1:
                                        lose = True
                                        last_tie_step = step
                                        tie_on = True
                                    print("OO")
                                    chip_selection(betting[martin_list[i]], c_res, step_o, round, "", vbet_key)
                                    break  # 일치하는 조건을 찾으면 반복문을 종료

                        start = False

                    if ox == "O":
                        if t_check == "TIE":
                            if lose:
                                step_o = last_tie_step
                                last_tie_step = 0
                                lose = False
                            else:
                                step_o = step_o
                                tie_on = True
                                print("step유지")

                        else:
                            if lose:
                                if t_check == "TIE":
                                    step_o = last_tie_step
                                else:
                                    step_o = 0
                                    # step_order[current_int] = 0
                                lose = False

                            if start:
                                step_o = 0

                        if re_start:
                            re_start = False

                        entry_25.insert(tk.END, (str(step_o + 1) + "마틴 진행\n"))
                        entry_25.see(tk.END)

                        if bet_type == 3:
                            for i in range(10):
                                if step_o == i:
                                    if selected_index == i + 1:
                                        lose = True
                                        last_tie_step = step
                                        tie_on = True
                                    print("OO")
                                    chip_selection(betting_price, c_res, step_o, round, "", vbet_key)
                                    break  # 일치하는 조건을 찾으면 반복문을 종료
                        else:
                            for i in range(10):
                                if step_o == i:
                                    if selected_index == i + 1:
                                        lose = True
                                        last_tie_step = step
                                        tie_on = True
                                    print("OO")
                                    chip_selection(betting[martin_list[i]], c_res, step_o, round, "", vbet_key)
                                    break  # 일치하는 조건을 찾으면 반복문을 종료

                        start = False
                        stop_check = False

            elif check_type == "X":
                if (cal > 0) and (profit_stop2 != 0 and profit_stop2 * profit_stop_count < cal):
                    profit_stop_func()
                    pass
                elif (stop_check1 and stop_check1 == "X") and bet_type == 1:
                    entry_25.insert(tk.END, ("역패턴 정지\n\n"))
                    entry_25.see(tk.END)
                    recode_log(vbet_key, 'LONG_STOP', start_price, current_price, 0, d_title, r_title, "", "", round,
                               cal)
                else:
                    if lose:
                        next_value = next_value
                        step_order[next_value] = 0
                        lose = False
                        next_value = show_next_order()
                    else:
                        if bet_type != 2:
                            if t_check == "TIE":
                                next_value = next_value
                            else:
                                next_value = show_next_order()
                        if bet_type == 2 and ox == "X":
                            next_value = show_next_order()
                        elif bet_type == 2 and ox == "O":
                            if start:
                                next_value = show_next_order()
                            else:
                                next_value = next_value
                        if re_start or start:
                            next_value = 0
                            order_index = 1
                            step_order = [0] * len(vbet_data)

                    if not start:
                        print("합계를 비교하여 단계를 높힐지 1로 돌릴지")
                        print("합계 금액 : " + str(sum_price))
                        if next_value == 0:
                            if sum_price > 0:
                                next_value = 0
                                order_index = 1
                                step_order = [0] * len(vbet_data)
                                betting_price = base_price
                                sum_price = 0
                                entry_25.insert(tk.END,
                                                (
                                                        "=================================\n\n그룹 합계 수익, 전체 배팅 금액 " + str(
                                                    betting_price) + "원 배팅\n\n=================================\n\n"))
                                entry_25.see(tk.END)
                            elif sum_price < 0:
                                step_order = [x + 1 for x in step_order]
                                betting_price = abs(sum_price) + base_price
                                entry_25.insert(tk.END,
                                                (
                                                        "=================================\n\n그룹 합계 손실, 손실 긍액 : " + str(
                                                    sum_price) + " 전체 배팅 금액 " + str(
                                                    betting_price) + "원 배팅(손실금+베이스)\n\n=================================\n\n"))
                        elif next_value != 0 and step_order[0] > 0:
                            if sum_price > 0:
                                next_value = 0
                                order_index = 1
                                step_order = [0] * len(vbet_data)
                                betting_price = base_price
                                sum_price = 0
                                entry_25.insert(tk.END,
                                                (
                                                        "=================================\n\n그룹 합계 수익, 전체 배팅 금액 " + str(
                                                    betting_price) + "원 배팅\n\n=================================\n\n"))
                                entry_25.see(tk.END)


                    vbet_key = vbet_keys[next_value]
                    martin_kind = vbet_data[vbet_key]['martin_kind']
                    betting = vbet_data[vbet_key]['betting']
                    current_position = vbet_key[-1]
                    current_int = int(current_position)
                    step_o = step_order[next_value]
                    current_vmachine.delete(0, tkinter.END)
                    current_vmachine.insert(tk.END, vbet_key)
                    driver2.find_element(By.CSS_SELECTOR, f".{vbet_key} .vmachine-name").click()
                    # blink_text(vbet_key)
                    print(step_o, step_order)
                    if ox == "O":

                        if bet_type == 0 or bet_type == 2 or bet_type == 3:
                            if check_kind == "A":
                                driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                            elif check_kind == "B":
                                driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                            elif check_kind == "C":
                                driver2.find_element(By.CSS_SELECTOR, '.result3').click()
                            current_res = driver2.find_element(By.CSS_SELECTOR, '.result.active .o-pattern .to-result')
                            c_res = current_res.get_attribute('innerHTML').strip()
                            check_type = "O"

                        if t_check == "TIE":
                            if lose:
                                step_o = last_tie_step
                                last_tie_step = 0
                                lose = False
                            else:
                                step_o = step_o
                                tie_on = True
                                print("step유지")
                        else:
                            if lose:
                                step_o = 0

                            if start:
                                step_o = 0

                        if re_start:
                            re_start = False

                        entry_25.insert(tk.END, (str(step_o + 1) + "마틴 진행\n"))
                        entry_25.see(tk.END)

                        if bet_type == 3:
                            for i in range(10):
                                if step_o == i:
                                    if selected_index == i + 1:
                                        lose = True
                                        last_tie_step = step
                                        tie_on = True
                                    print("OO")
                                    chip_selection(betting_price, c_res, step_o, round, "", vbet_key)
                                    break  # 일치하는 조건을 찾으면 반복문을 종료
                        else:
                            for i in range(10):
                                if step_o == i:
                                    if selected_index == i + 1:
                                        lose = True
                                        last_tie_step = step
                                        tie_on = True
                                    print("OO")
                                    chip_selection(betting[martin_list[i]], c_res, step_o, round, "", vbet_key)
                                    break  # 일치하는 조건을 찾으면 반복문을 종료

                        start = False
                    if ox == "X":
                        if t_check == "TIE":
                            if lose:
                                step_o = last_tie_step
                                last_tie_step = 0
                                lose = False
                            else:
                                step_o = step_o
                                tie_on = True
                                print("step유지")

                        else:
                            if lose:
                                if t_check == "TIE":
                                    step_o = last_tie_step
                                else:
                                    step_o = 0
                                    # step_order[current_int] = 0
                                lose = False

                            if start:
                                step_o = 0

                        if re_start:
                            re_start = False

                        entry_25.insert(tk.END, (str(step_o + 1) + "마틴 진행\n"))
                        entry_25.see(tk.END)

                        if bet_type == 3:
                            for i in range(10):
                                if step_o == i:
                                    if selected_index == i + 1:
                                        lose = True
                                        last_tie_step = step
                                        tie_on = True
                                    print("OO")
                                    chip_selection(betting_price, c_res, step_o, round, "", vbet_key)
                                    break  # 일치하는 조건을 찾으면 반복문을 종료
                        else:
                            for i in range(10):
                                if step_o == i:
                                    if selected_index == i + 1:
                                        lose = True
                                        last_tie_step = step
                                        tie_on = True
                                    print("OO")
                                    chip_selection(betting[martin_list[i]], c_res, step_o, round, "", vbet_key)
                                    break  # 일치하는 조건을 찾으면 반복문을 종료

                        start = False
                        stop_check = False

        except NoSuchElementException:
            # 요소가 발견되지 않으면 계속 반복
            print("요소없음")
            pass


def close_popup(driver):
    while True:
        try:
            no_money = driver.find_element(By.CSS_SELECTOR, '.buttonContainerItem--30865')
            no_money.click()
        except NoSuchElementException:
            # 요소가 발견되지 않으면 계속 반복
            pass
        time.sleep(10)


def crawlresult(driver, driver2, nowin):
    global current_price, previous_win, previous_lose, step_order, stop_check, sum_price, base_price
    if bet_type == 3:
        base_price = get_base_value()

    while True:

        try:
            # 특정 요소를 찾음
            session_pop = driver.find_element(By.CSS_SELECTOR,
                                              'div.content--82383 > div.popupContainer--53f29.blocking--88949.highestPriority--6e829 > div > div')

            # 요소가 발견되면 반복 중지
            break
        except NoSuchElementException:
            # 요소가 발견되지 않으면 계속 반복
            pass

        if not last_opened_window_handle:
            break

        try:
            current_url = driver.current_url

            # URL 변경 감지
            if nowin == "no":
                if "game=baccarat&table_id" not in current_url:
                    break
            try:
                if ("table_id=PTB" in current_url) or ("table_id=Lightning" in current_url):
                    element = driver.find_element(By.CSS_SELECTOR, '[class*="gameResult"]')
                else:
                    element = driver.find_element(By.CSS_SELECTOR, '[class*="gameResult"] > div')
                # 엘리먼트의 HTML 내용 가져오기

                element_html = element.get_attribute('innerHTML').strip()
            except NoSuchElementException:
                pass

            # HTML 내용이 비어있지 않은지 확인
            if element_html:
                # 주어진 함수 실행
                try:
                    number_player = driver.find_element(By.CSS_SELECTOR, '.player--d9544 .score--9b2dc')
                    number_banker = driver.find_element(By.CSS_SELECTOR, '.banker--7e77b .score--9b2dc')
                    player = number_player.get_attribute('innerText')
                    banker = number_banker.get_attribute('innerText')
                    p_input = driver2.find_element(By.CLASS_NAME, "player")
                    b_input = driver2.find_element(By.CLASS_NAME, "banker")
                    submit_button = driver2.find_element(By.CLASS_NAME, "submit")
                    p_input.click()
                    p_input.send_keys(player)
                    b_input.click()
                    b_input.send_keys(banker)
                    submit_button.click()
                    time.sleep(1)
                    try:
                        if not stop_check and s_bet and not (re_start or start):
                            stop_check = False
                            if element_length > 0:
                                check_type = driver2.find_element(By.CSS_SELECTOR,
                                                                  '.result.active .tc.active').get_attribute(
                                    'data-type')
                                check_ox = driver2.find_element(By.CSS_SELECTOR,
                                                                '.result.active .pattern2 > ul:last-child > li:last-child p').get_attribute(
                                    'innerHTML').strip()
                                tie_check = driver2.find_element(By.CSS_SELECTOR,
                                                                 '.result.active .current_res .ball').get_attribute(
                                    'innerHTML').strip()
                                current_price = driver.find_element(By.CSS_SELECTOR,
                                                                    '.amount--bb99f span').get_attribute(
                                    'innerText').strip()

                                if check_type == "O":
                                    if check_ox == "O":
                                        if tie_check == "TIE":
                                            entry_25.insert(tk.END, (
                                                "================================\n타이\n================================\n\n"))
                                            entry_25.see(tk.END)
                                            recode_log(vbet_key, 'TIE', start_price, current_price, 0, d_title, r_title,
                                                       "", "",
                                                       round, cal)
                                        else:
                                            entry_25.insert(tk.END, (
                                                "=================================\n승리\n=================================\n\n"))
                                            entry_25.see(tk.END)
                                            recode_log(vbet_key, 'WIN', start_price, current_price, 0, d_title, r_title,
                                                       "", "",
                                                       round, cal)
                                            previous_win = True
                                            previous_lose = False
                                            if bet_type != 3:
                                                step_order[current_int - 1] = 0
                                            if bet_type == 3:
                                                sum_price += betting_price
                                            bet_input = step_order[current_int - 1] + 1
                                            if lose:
                                                driver2.find_element(By.CSS_SELECTOR, f".{vbet_key} .lbet1").click()
                                            else:
                                                driver2.find_element(By.CSS_SELECTOR,
                                                                     f".{vbet_key} .lbet{bet_input}").click()

                                    elif check_ox == "X":
                                        print("틀림")
                                        if tie_check == "TIE":
                                            entry_25.insert(tk.END, (
                                                "================================\n타이\n================================\n\n"))
                                            entry_25.see(tk.END)
                                            recode_log('TIE', start_price, current_price, 0, d_title, r_title, "", "",
                                                       round, cal)
                                        else:
                                            entry_25.insert(tk.END, (
                                                "=================================\n패배\n=================================\n\n"))
                                            entry_25.see(tk.END)
                                            recode_log(vbet_key, 'LOSE', start_price, current_price, 0, d_title,
                                                       r_title, "", "",
                                                       round, cal)
                                            previous_win = False
                                            previous_lose = True
                                            if bet_type != 3:
                                                step_order[current_int - 1] += 1
                                            if bet_type == 3:
                                                sum_price -= betting_price
                                            bet_input = step_order[current_int - 1] + 1
                                            if lose:
                                                driver2.find_element(By.CSS_SELECTOR, f".{vbet_key} .lbet1").click()
                                            else:
                                                driver2.find_element(By.CSS_SELECTOR, f".{vbet_key} .lbet{bet_input}").click()


                                elif check_type == "X":
                                    if check_ox == "O":
                                        if tie_check == "TIE":
                                            entry_25.insert(tk.END, (
                                                "================================\n타이\n================================\n\n"))
                                            entry_25.see(tk.END)
                                            recode_log(vbet_key, 'TIE', start_price, current_price, 0, d_title, r_title,
                                                       "", "",
                                                       round, cal)
                                        else:
                                            entry_25.insert(tk.END, (
                                                "=================================\n패배\n=================================\n\n"))
                                            entry_25.see(tk.END)
                                            recode_log(vbet_key, 'LOSE', start_price, current_price, 0, d_title,
                                                       r_title, "", "",
                                                       round, cal)
                                            previous_win = False
                                            previous_lose = True
                                            if bet_type != 3:
                                                step_order[current_int - 1] += 1
                                            if bet_type == 3:
                                                sum_price -= betting_price
                                            bet_input = step_order[current_int - 1] + 1
                                            if lose:
                                                driver2.find_element(By.CSS_SELECTOR, f".{vbet_key} .lbet1").click()
                                            else:
                                                driver2.find_element(By.CSS_SELECTOR,
                                                                     f".{vbet_key} .lbet{bet_input}").click()

                                    elif check_ox == "X":
                                        if tie_check == "TIE":
                                            entry_25.insert(tk.END, (
                                                "================================\n타이\n================================\n\n"))
                                            entry_25.see(tk.END)
                                            recode_log(vbet_key, 'TIE', start_price, current_price, 0, d_title, r_title,
                                                       "", "",
                                                       round, cal)
                                        else:
                                            entry_25.insert(tk.END, (
                                                "=================================\n승리\n=================================\n\n"))
                                            entry_25.see(tk.END)
                                            recode_log(vbet_key, 'WIN', start_price, current_price, 0, d_title, r_title,
                                                       "", "",
                                                       round, cal)
                                            previous_win = True
                                            previous_lose = False
                                            if bet_type != 3:
                                                step_order[current_int - 1] = 0
                                            if bet_type == 3:
                                                sum_price += betting_price
                                            bet_input = step_order[current_int - 1] + 1
                                            if lose:
                                                driver2.find_element(By.CSS_SELECTOR, f".{vbet_key} .lbet1").click()
                                            else:
                                                driver2.find_element(By.CSS_SELECTOR,
                                                                     f".{vbet_key} .lbet{bet_input}").click()

                    except NoSuchElementException:
                        # 요소가 발견되지 않으면 계속 반복
                        print("요소없음")
                        pass

                    time.sleep(6)
                    startThread6(driver, driver2)
                except NoSuchElementException:
                    pass

            else:
                time.sleep(1)

        except NoSuchWindowException:
            print("마지막 창이 닫혔습니다. 새 창을 확인합니다.")
            reset(driver, driver2)
            break

        except KeyboardInterrupt:
            # 사용자가 Ctrl+C를 누르면 루프 종료
            break
        except Exception as e:
            print(f"오류 발생: {e}")
            break


def inputdoublex(arg2, driver, driver2):
    global price_number2, start_price
    start_price = driver.find_element(By.CSS_SELECTOR, '.amount--bb99f span').get_attribute('innerText').strip()
    price_number2 = re.sub(r'[^0-9.]', '', start_price)
    entry_3.config(state='normal')
    entry_3.delete(0, tkinter.END)
    entry_3.insert(0, price_number2)
    entry_3.config(state='readonly')
    recode_log(serial_number, 'OPEN_ROOM', start_price, start_price, 0, d_title, r_title, "", "", "", cal)


def findurl(driver, driver2):
    last_opened_window_handle = None
    last_checked_url = ""
    room_search = True

    global docrawl, d_title, r_title, start

    d_title = driver.title
    entry_25.insert(tk.END, "\n%s사이트 접속\n\n" % d_title)
    entry_25.see(tk.END)

    parse_betdata()

    while True:

        current_window_handles = driver.window_handles

        if not current_window_handles:
            print("열린 창이 없습니다. 새 창을 기다립니다.")
            time.sleep(1)
            continue

        # 현재 열려 있는 창 중 마지막 창을 선택
        # 마지막에 열린 새 창이 항상 선택되도록 last_opened_window_handle 업데이트
        new_last_opened_window_handle = current_window_handles[-1]
        if new_last_opened_window_handle != last_opened_window_handle:
            last_opened_window_handle = new_last_opened_window_handle
            driver.switch_to.window(last_opened_window_handle)
            driver.set_window_size(width - 120, height)
            last_checked_url = ""  # URL 체크 리셋

        try:
            current_url = driver.current_url

            # URL 변경 감지
            if current_url != last_checked_url:
                print("URL 변경 감지:", current_url)
                if room_search:
                    entry_25.insert(tk.END, "방 찾는중...\n\n")

                    entry_25.see(tk.END)
                    room_search = False

                last_checked_url = current_url

                if "game=baccarat&table_id" in current_url:
                    print("필요한 URL 변경을 감지했습니다. 작업을 수행합니다.")
                    entry_25.insert(tk.END, "방 접속완료. 마틴단계와 금액 설정 후 오토프로그램을 시작하세요.\n\n")
                    entry_25.see(tk.END)
                    driver2.refresh()
                    start = True
                    time.sleep(5)
                    driver.switch_to.default_content()
                    iframes = driver.find_elements(By.TAG_NAME, "iframe")
                    # iframe이 하나 이상 있을 경우 첫 번째 iframe으로 이동
                    if len(iframes) > 0:
                        driver.switch_to.frame(iframes[0])
                    try:
                        elem = driver.find_element(By.CLASS_NAME, 'roadGrid--bd5fc')
                        r_title = driver.find_element(By.CLASS_NAME, 'tableName--a9bc5').get_attribute(
                            'innerText').strip()
                    except NoSuchElementException:
                        print("지정된 요소를 찾을 수 없습니다.")
                        continue

                    startThread4(elem, driver, driver2)
                    time.sleep(5)

                    startThread5(driver, driver2, "no")

            time.sleep(1)  # 리소스 최소화를 위해 대기

        except NoSuchWindowException:
            print("마지막 창이 닫혔습니다. 새 창을 확인합니다.")
            driver2.refresh()
            last_opened_window_handle = None  # 창 닫힘 감지 시 핸들 초기화
        except KeyboardInterrupt:
            print("사용자에 의해 중단됨")
            break
        except Exception as e:
            print(f"오류 발생: {e}")
            break


def doAction(arg, driver, driver2):
    try:
        # 초기 페이지로 이동
        driver.get(arg)
        driver2.get("http://pattern2024.com/bbs/login.php?agency=pt6")
        try:
            # 요소가 나타날 때까지 최대 10초 동안 기다립니다.
            id_input = WebDriverWait(driver2, 20).until(
                EC.presence_of_element_located((By.ID, "login_id"))
            )

            password_input = driver2.find_element(By.ID, "login_pw")
            submit_button = driver2.find_element(By.CLASS_NAME, "btn_submit")
            login_id = "dpauto1"
            password = "1212"
            id_input.click()
            id_input.send_keys(login_id)
            password_input.click()
            password_input.send_keys(password)
            submit_button.click()
        except TimeoutException:
            print("Timed out waiting for the element to appear")

        startThread3(driver, driver2)
    except WebDriverException as e:
        print("WebDriver 연결 오류 발생:", e)
        # 오류 처리 로직, 예를 들어, 드라이버 재시작


stop_event = threading.Event()

serial_check = get_current_drive_serial()


def main(a, b):
    # 현재 실행 중인 스크립트 파일의 경로를 가져옵니다.

    sp = b.split(",")
    if sp[0] == "1":
        tkinter.messagebox.showwarning("동시 사용오류", "다른곳에서 동시접속 사용중입니다.\n사용중인 아이피 : %s" % sp[1])
    else:
        global width, height, driver, driver2

        if monitors[0].width < 1367:
            width = monitors[0].width * 1.2
            height = monitors[0].height * 1.8
        elif monitors[0].width > 1367 and monitors[0].width < 1610:
            width = monitors[0].width / 1.1
            height = monitors[0].height * 1.5
        elif monitors[0].width > 1610 and monitors[0].width < 1900:
            width = monitors[0].width / 1.35
            height = monitors[0].height * 1.2
        elif monitors[0].width > 1900 and monitors[0].width < 2500:
            width = monitors[0].width / 1.2
            height = monitors[0].height * 1.35
        elif monitors[0].width > 2500 and monitors[0].width < 3000:
            width = monitors[0].width / 1.68
            height = monitors[0].height / 1.1
        elif monitors[0].width > 3000:
            width = monitors[0].width / 2.5
            height = monitors[0].height / 1.5
        driver = webdriver.Chrome(service=ChromeService(driver_path), options=options)  # <- options로 변경
        driver2 = webdriver.Chrome(service=ChromeService(driver_path), options=options)
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )
        driver.set_window_size(width - 120, height)
        driver.set_window_position(0, 0)
        driver2.set_window_size(width - 120, height)
        driver2.set_window_position(width - 120, 0)

        startThread2(a, driver, driver2)


def startThread(a, b):
    thread = threading.Thread(target=main, args=(a, b))
    thread.start()


def startThread2(a, b, c):
    thread = threading.Thread(target=doAction, args=(a, b, c))
    thread.start()


def startThread3(a, b):
    thread = threading.Thread(target=findurl(a, b))
    thread.start()


def startThread4(a, b, c):
    thread = threading.Thread(target=inputdoublex(a, b, c))
    thread.start()


def startThread5(a, b, c):
    thread = threading.Thread(target=crawlresult(a, b, c))
    thread.start()


def startThread6(a, b):
    thread = threading.Thread(target=autoBet(a, b))
    thread.start()


def startThread7(a):
    thread = threading.Thread(target=close_popup(a))
    thread.start()


def set_dpi_awareness():
    try:
        print("dpi ok")
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        print("dpi no")
        pass


def on_canvas_click(event):
    # 모든 이미지에 대해 클릭 위치 확인
    for img_id, info in images_info.items():
        x, y, width, height = info
        if x - width // 2 <= event.x <= x + width // 2 and y - height // 2 <= event.y <= y + height // 2:
            if img_id == "image1":
                startThread(entry_24.get(), t)
            if img_id == "image2":
                start_autobet()
            if img_id == "image3":
                stop_autobet()
            if img_id == "image4":
                stop_bet()
            if img_id == "image112":
                parse_betdata()


def parse_betdata():
    global vbet_amount, vbet_data, step_order, order, vbet_keys, selected_index
    if (driver2):
        vbet_amount = driver2.find_element(By.CSS_SELECTOR, "select[name=amount-vbet]").get_attribute("value")
        # PHP 스크립트가 위치한 URL (예: localhost 또는 실제 서버 URL)
        url = 'http://pattern2024.com/vbet/vbet_json.php'

        if serial_number == 'MASTER':
            datas = {
                'id': 'admin',
            }
        else:
            datas = {
                'id': serial_number.lower(),
            }

        # 요청 보내기
        response = requests.post(url, data=datas)

        # HTTP 상태 코드가 200(성공)일 경우
        if response.status_code == 200:
            try:
                # JSON 데이터를 파싱하여 파이썬 변수에 저장
                data = response.json()
                vbet_data = data.get('data')

                step_order = [0] * len(vbet_data)

                # order 배열 생성 (0, 1, 2, ... n-1)
                order = list(range(len(vbet_data)))

                # vbet_data의 키 리스트 생성
                vbet_keys = list(vbet_data.keys())

                key_map = {
                    "base": "1마틴",
                    "2nd": "2마틴",
                    "3rd": "3마틴",
                    "4th": "4마틴",
                    "5th": "5마틴",
                    "6th": "6마틴",
                    "7th": "7마틴",
                    "8th": "8마틴",
                    "9th": "9마틴",
                    "10th": "10마틴"
                }
                # entry_25에 저장할 문자열 초기화
                entry_text = ""

                # vbet1, vbet2, ... 등의 데이터를 처리

                for vbet_key, vbet_value in vbet_data.items():
                    martin_level = vbet_value.get('martin_level')
                    martin_kind = vbet_value.get('martin_kind')
                    selected_index = int(martin_level)
                    betting = vbet_value.get('betting')

                    if betting:
                        entry_text += f"{serial_number}\n---------------------------\n{vbet_key}\n마틴단계 {martin_level}, 마틴방식 {martin_kind}\n"

                        # 값이 있는 항목들만 텍스트에 추가
                        valid_bets = [f"{key_map.get(key, key)}={value}" for key, value in betting.items() if value]
                        if valid_bets:
                            entry_text += ', '.join(valid_bets)
                            entry_text += "\n================================\n"

                # 마지막 "|" 제거
                entry_text = entry_text.rstrip(" | ")

                # entry_25에 텍스트 설정
                entry_25.insert(tk.END, entry_text)  # 새로운 텍스트 삽입
                entry_25.see(tk.END)




            except ValueError:
                print("응답이 JSON 형식이 아닙니다.")
        else:
            print(f"HTTP 요청 실패. 상태 코드: {response.status_code}")


def show_next_order():
    global order_index

    # 현재 order 값 가져오기
    current_order = order[order_index]

    # order_index 증가 (순환)
    order_index = (order_index + 1) % len(order)

    return current_order


url = "http://15.164.129.23/serial_check2.php"
datas = {
    'serial_number': serial_number,
    'mac': get_mac_address(),
    'ip': get_external_ip(),
    'hours': set_hours
}

response = requests.post(url, data=datas)
t = response.text


def on_closing():
    global current_price, cal
    try:
        if driver:
            current_price = driver.find_element(By.CSS_SELECTOR, '.amount--bb99f span').get_attribute(
                'innerText').strip()
            price_number = re.sub(r'[^0-9.]', '', current_price)
            cal = int(float(price_number)) - int(float(price_number2))
    except:
        print("오류")
    recode_log(serial_number, 'END', start_price, current_price, 0, d_title, r_title, "", "", round, cal)

    if messagebox.askokcancel("종료", "종료하시겠습니까?"):
        martin_set_zero()
        stop_event.set()
        try:
            driver.quit()  # This will close the browser and kill the chromedriver.exe process
            driver2.quit()
            os.system("taskkill /f /im chromedriver.exe /t")
            print(f"크롬드라이버 강제 종료 성공")
        except Exception as e:
            print(f"Error closing the WebDriver: {e}")
        win.quit()
        win.destroy()


def calculate_amount(base_amount, stage):
    amount = base_amount
    for i in range(2, stage + 2):
        amount = amount * 2 + base_amount
    return amount

def tie_reset():
    global tie_step
    tie_step = 0
    entry_25.insert(tk.END, ("타이마틴단계 1단계로 복귀\n\n=================================\n\n"))


def login():
    username = entry_username.get()
    password = entry_password.get()
    url = "http://15.164.129.23/auto_login.php"
    datas = {
        'mb_id': username,
        'mb_password': password
    }

    response = requests.post(url, data=datas)
    t = response.text
    if t == "1":
        login_window.destroy()
    if t == "no":
        messagebox.showerror("로그인 실패", "잘못된 사용자 이름 또는 비밀번호")
        sys.exit()


def create_login_window():
    global login_window, entry_username, entry_password
    login_window = tk.Tk()
    login_window.title("로그인")
    login_window.geometry("300x200")

    label_username = tk.Label(login_window, text="사용자 이름:")
    label_username.pack()
    entry_username = tk.Entry(login_window)
    entry_username.pack()

    label_password = tk.Label(login_window, text="비밀번호:")
    label_password.pack()
    entry_password = tk.Entry(login_window, show="*")
    entry_password.pack()

    button_login = tk.Button(login_window, text="로그인", command=login)
    button_login.pack()

    login_window.protocol("WM_DELETE_WINDOW", login)
    login_window.mainloop()

class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey'):
        super().__init__(master)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

        self._add_placeholder()

    def _clear_placeholder(self, e):
        if self['fg'] == self.placeholder_color:
            self.delete(0, tk.END)
            self['fg'] = self.default_fg_color

    def _add_placeholder(self, e=None):
        if not self.get():
            self['fg'] = self.placeholder_color
            self.insert(0, self.placeholder)

entry_mlevel = None
entry_base = None
def bet_type_select(event):
    global bet_type, entry_mlevel, entry_base

    type_of_bet = entry_77.get()

    if type_of_bet == "TYPE1":
        bet_type = 0
        entry_25.insert(tk.END,
                        (
                            "=================================\n\nO,X둘다 줄따라 차례대로 배팅\n\n=================================\n\n"))
        entry_25.see(tk.END)
        if entry_mlevel is not None:
            entry_mlevel.destroy()
            entry_base.destroy()
            entry_mlevel = None

    elif type_of_bet == "TYPE2":
        bet_type = 1
        entry_25.insert(tk.END,
                        (
                            "=================================\n\nO또는 X 한개줄만 차례대로 배팅\n\n=================================\n\n"))
        entry_25.see(tk.END)
        if entry_mlevel is not None:
            entry_mlevel.destroy()
            entry_base.destroy()
            entry_mlevel = None
    elif type_of_bet == "TYPE3":
        bet_type = 2
        entry_25.insert(tk.END,
                        (
                            "=================================\n\n한줄씩 나눠서 배팅\n\n=================================\n\n"))
        entry_25.see(tk.END)
        if entry_mlevel is not None:
            entry_mlevel.destroy()
            entry_base.destroy()
            entry_mlevel = None
    elif type_of_bet == "TYPE4":
        bet_type = 3
        entry_25.insert(tk.END,
                        (
                            "=================================\n\n단계 총합으로 단계 조정\n\n=================================\n\n"))
        entry_25.see(tk.END)

        #마틴단계
        mlevel = ["1마틴", "2마틴", "3마틴", "4마틴", "5마틴", "6마틴", "7마틴", "8마틴", "9마틴", "10마틴"]
        mlevel.insert(0, "마틴단계설정")
        entry_mlevel = ttk.Combobox(
            win,
            value=mlevel,
            font=text_font3
        )
        entry_mlevel.place(
            x=210.0,
            y=335.0,
            width=100.0,
            height=25.0,
        )
        entry_mlevel.current(0)
        entry_mlevel.bind('<<ComboboxSelected>>', mlevel_select)

        entry_base = PlaceholderEntry(win, placeholder="베이스금액")

        entry_base.place(
            x=130.0,
            y=335.0,
            width=70.0,
            height=25.0,
        )

def get_base_value():
    global entry_base
    if entry_base is not None:  # entry_base가 None이 아니면 값을 가져옴
        try:
            base_value = entry_base.get()
            # 값을 정수나 실수로 변환해야 할 경우
            base_value = int(base_value)  # 또는 float(base_value)
            return base_value
        except ValueError:
            print("유효한 숫자를 입력하세요.")
            return None
    else:
        print("entry_base가 존재하지 않습니다.")
        return None

def mlevel_select(event):
    global selected_value2
    global selected_index

    selected_value2 = entry_mlevel.get()
    selected_num = re.sub(r'[^0-9]', '', selected_value2)
    try:
        selected_index = int(selected_num)
        print(selected_index)
    except:
        print("int아님")
def set1_click(value):
    global profit_stop2
    profit_stop2 = int(value)
    print(profit_stop2)
    entry_25.insert(tk.END, "==================================\n수익시 1마틴 복귀 금액 : " + str(
        profit_stop2) + " 설정 완료\n==================================\n\n")
    entry_25.see(tk.END)


# Socket.IO 클라이언트 인스턴스 생성
sio = socketio.Client()


@sio.event
def connect():
    print('Connection established')


@sio.event
def disconnect():
    print('Disconnected from server')


@sio.on('status-updated')
def on_status_updated(data):
    global stop_step
    print(data)

    if data['serial'] == serial_number and data['status'] == 1:
        stop_autobet()
    elif data['serial'] == serial_number and data['status'] == 0:
        m0 = data['stop_step']
        m1 = data['level']
        m2 = data['kind']
        m3 = data['cost']
        print(m0, m1, m2, m3)

        if m1 != 0:
            entry_7.current(m1)
            entry_77.current(m2)
            on_martin_select("")
            martin_kind_select("")
            entry_10.delete(0, tkinter.END)
            entry_10.state(['!readonly'])
            entry_10.insert(tk.END, m3)
            set1_click(m3)

        if m0 == 0:
            stop_step = 1
        else:
            stop_step = m0
        start_autobet()


def socketio_thread():
    sio.connect('wss://log2.pattern2024.com/socket.io', transports='websocket')
    sio.wait()


def start_socketio_thread():
    thread = threading.Thread(target=socketio_thread)
    thread.daemon = True
    thread.start()


visible = True  # 텍스트가 처음에 보이는 상태로 설정


def blink_text(text):
    global visible
    if visible:
        current_vmachine.delete(0, tk.END)  # 텍스트 삭제
    else:
        current_vmachine.insert(0, text)  # 텍스트 추가
    visible = not visible
    current_vmachine.after(500, blink_text(text))  # 500ms마다 blink_text 함수 호출


if __name__ == "__main__":
    start_socketio_thread()
    if not serial_number == "MASTER":
        create_login_window()
    martin_set_zero()
    recode_log(serial_number, 'OPEN', 0, 0, 0, "", "", "", "", "", cal)
    win = tk.Tk()
    win.geometry("450x690")
    win.configure(bg="#FFFFFF")
    win.title("PATTERN AUTO")
    win.attributes("-topmost", True)
    win.tk.call('tk', 'scaling', 1.0)

    text_font = ('Courier New', '8')
    text_font2 = ('Inter Black', '12')
    text_font4 = ('Inter Black', '15')

    canvas = Canvas(
        win,
        bg="#FFFFFF",
        height=690,
        width=450,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )

    canvas.place(x=0, y=0)

    image_image_1 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "image_1.png"))
    )

    image_1 = canvas.create_image(
        387.0,
        492.0,
        image=image_image_1
    )

    image_image_2 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "image_2_6.png"))
    )
    image_2 = canvas.create_image(
        225,
        360,
        image=image_image_2
    )

    canvas.create_text(
        24.0,
        20.0,
        anchor="nw",
        text="접속 사이트 URL",
        fill="#FFFFFF",
        font=("Roboto Bold", 18 * -1)
    )

    entry_image_24 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "entry_28.png"))
    )
    entry_bg_24 = canvas.create_image(
        183.5,
        70.0,
        image=entry_image_24
    )
    entry_24 = Entry(
        bd=0,
        bg="#FFFFFF",
        fg="#000716",
        highlightthickness=0,
        font=("Roboto Bold", 12 * -1)
    )
    entry_24.place(
        x=40.0,
        y=55.0,
        width=297.0,
        height=30.0
    )

    images_info = {}

    image_image_11 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "image_11.png"))
    )
    x1, y1 = 390, 70
    images_info['image1'] = (x1, y1, image_image_11.width(), image_image_11.height())
    image_11 = canvas.create_image(
        x1,
        y1,
        image=image_image_11
    )

    image_image_112 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "btn_1.png"))
    )
    x0, y0 = 70, 125
    images_info['image112'] = (x0, y0, image_image_112.width(), image_image_112.height())
    image_112 = canvas.create_image(
        x0,
        y0,
        image=image_image_112
    )

    image_image_12 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "btn_2.png"))
    )
    x2, y2 = 173, 125
    images_info['image2'] = (x2, y2, image_image_12.width(), image_image_12.height())
    image_12 = canvas.create_image(
        x2,
        y2,
        image=image_image_12
    )

    image_image_13 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "btn_3.png"))
    )
    x3, y3 = 378, 125
    images_info['image3'] = (x3, y3, image_image_13.width(), image_image_13.height())
    image_13 = canvas.create_image(
        x3,
        y3,
        image=image_image_13
    )

    image_image_14 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "btn_4.png"))
    )
    x4, y4 = 277, 125
    images_info['image4'] = (x4, y4, image_image_14.width(), image_image_14.height())
    image_14 = canvas.create_image(
        x4,
        y4,
        image=image_image_14
    )

    canvas.bind("<Button-1>", on_canvas_click)

    entry_image_25 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "entry_29_2.png"))
    )
    entry_bg_25 = canvas.create_image(
        223.0,
        523.0,
        image=entry_image_25
    )
    my_font = Font(family="Roboto Bold", size=10)
    entry_25 = scrolledtext.ScrolledText(
        bd=0,
        bg="#FFFFFF",
        fg="#000716",
        highlightthickness=0
    )
    entry_25.place(
        x=35.0,
        y=398.0,
        width=380.0,
        height=255.0
    )
    entry_25.configure(font=my_font)

    canvas.create_text(
        30.0,
        340.0,
        anchor="nw",
        text="로그정보",
        fill="#FFFFFF",
        font=("Roboto Bold", 18 * -1)
    )
    canvas.create_text(
        380.0,
        10.0,
        anchor="nw",
        text=serial_number,
        fill="#FFFFFF",
        font=("Roboto Bold", 12 * -1)
    )

    text_font3 = ('Arial', '12')
    betting_type = ["TYPE1", "TYPE2", "TYPE3", "TYPE4"]
    betting_type.insert(0, "배팅방식설정")
    entry_77 = ttk.Combobox(
        win,
        value=betting_type,
        font=text_font3
    )
    entry_77.place(
        x=320.0,
        y=335.0,
        width=100.0,
        height=25.0,
    )
    entry_77.current(0)
    entry_77.bind('<<ComboboxSelected>>', bet_type_select)

    # 금액관련
    entry_image_26 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "entry_29_3.png"))
    )
    entry_bg_26 = canvas.create_image(
        223.0,
        238.0,
        image=entry_image_26
    )
    canvas.create_text(
        40.0,
        180.0,
        anchor="nw",
        text="시작금액 : ",
        fill="#000000",
        font=("Inter Black", 15 * -1)
    )
    entry_3 = Entry(
        bd=0,
        bg="#FFFFFF",
        fg="#000716",
        highlightthickness=0,
        font=text_font4
    )
    entry_3.place(
        x=105.0,
        y=179.0,
        width=90.0,
        height=19.0
    )
    entry_3.insert(tk.END, 0)

    canvas.create_text(
        40.0,
        210.0,
        anchor="nw",
        text="현재금액 : ",
        fill="#000000",
        font=("Inter Black", 15 * -1)
    )
    entry_2 = Entry(
        bd=0,
        bg="#FFFFFF",
        fg="#000716",
        highlightthickness=0,
        font=text_font4
    )
    entry_2.place(
        x=105.0,
        y=209.0,
        width=90.0,
        height=19.0
    )
    entry_2.insert(tk.END, 0)

    canvas.create_text(
        40.0,
        240.0,
        anchor="nw",
        text="총 수익 : ",
        fill="#000000",
        font=("Inter Black", 15 * -1)
    )
    entry_1 = Entry(
        bd=0,
        bg="#FFFFFF",
        fg="#000716",
        highlightthickness=0,
        font=text_font4
    )
    entry_1.place(
        x=105.0,
        y=239.0,
        width=90.0,
        height=19.0
    )
    entry_1.insert(tk.END, 0)

    canvas.create_text(
        40.0,
        270.0,
        anchor="nw",
        text="수익시1마틴 - ",
        fill="#000000",
        font=("Inter Black", 15 * -1)
    )
    entry_4 = Entry(
        bd=1,
        bg="#FFFFFF",
        fg="#000716",
        highlightthickness=0,
        font=text_font4
    )
    entry_4.place(
        x=135.0,
        y=269.0,
        width=90.0,
        height=19.0
    )
    button_1 = tk.Button(
        win,
        text="입력",
        command=lambda: set1_click(entry_4.get()),
        activebackground="black",
        activeforeground="white",
        anchor="center",
        bd=3,
        bg="white",
        cursor="hand2",
        disabledforeground="gray",
        fg="black",
        font=("Inter Medium", 12 * -1),
        height=2,
        highlightbackground="black",
        highlightcolor="green",
        highlightthickness=2,
        justify="center",
        overrelief="raised",
        width=15,
        wraplength=100
    )

    button_1.pack()
    button_1.place(
        x=230.0,
        y=269.0,
        width=35.0,
        height=20.0
    )

    # 현재 배팅위치 canvas
    canvas2 = Canvas(
        win,
        bg="#000000",
        width=180,
        height=30,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )

    canvas2.place(x=225.0, y=179.0)
    canvas2.create_text(
        10.0,
        7.5,
        anchor="nw",
        text="현재 배팅 - ",
        fill="#FFCC00",
        font=("Inter Black", 15 * -1)
    )
    current_vmachine = Entry(
        bd=0,
        bg="#000000",
        fg="#FFCC00",
        highlightthickness=0,
        font=text_font4
    )
    current_vmachine.place(
        x=320.0,
        y=181.5,
        width=80.0,
        height=25.0
    )

    ab = t.split(",")

    if ab[0] == "0":
        win.protocol("WM_DELETE_WINDOW", on_closing)
        win.mainloop()

    else:
        tkinter.messagebox.showwarning("경고", "사용이 승인되지 않았습니다.")
        on_closing()
