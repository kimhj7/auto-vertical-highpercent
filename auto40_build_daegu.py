import time
import subprocess
import tkinter.messagebox
import tkinter.scrolledtext as scrolledtext
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

options = ChromeOptions()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.183 Safari/537.36"
options.add_argument('user-agent=' + user_agent)
options.add_argument("lang=ko_KR")
options.add_argument('--window-size=1920,1020')

monitors = get_monitors()

options.add_argument("force-device-scale-factor=0.6")
options.add_argument("high-dpi-support=0.6")

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

def recode_log(type, start_price, current_price, bet_price, title, room, status, step, round, cal):
    url = "https://log2.pattern2024.com/log"
    datas = {
        'serial': serial_number,
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
                        inputdoublex(elem, driver, driver2)
                        crawlresult(driver, driver2)

                        update_completed = True

            # 리소스 사용 최소화를 위해 잠시 대기
            time.sleep(1)
        except KeyboardInterrupt:
            # 사용자가 Ctrl+C를 누르면 루프 종료
            break


basecost = 0
martin2 = 0
martin3 = 0
martin4 = 0
martin5 = 0
martin6 = 0
martin7 = 0
martin8 = 0
martin9 = 0
martin10 = 0
martin11 = 0
martin12 = 0
martin13 = 0
martin14 = 0
martin15 = 0
martin16 = 0
martin17 = 0
martin18 = 0
martin19 = 0
martin20 = 0
martin21 = 0
martin22 = 0
martin23 = 0
martin24 = 0
martin25 = 0
martin26 = 0
martin27 = 0
martin28 = 0
martin29 = 0
martin30 = 0
martin31 = 0
martin32 = 0
martin33 = 0
martin34 = 0
martin35 = 0
martin36 = 0
martin37 = 0
martin38 = 0
martin39 = 0
martin40 = 0

step = 0
price_number2 = 0
start_price = 0
current_price = 0
cal = 0
s_bet = False
selected_value = "마틴단계설정"
selected_value2 = "마틴단계설정"
selected_index = 0
selected_type = 1

martin_kind = "마틴종류설정"

# KRW 칩 가격
k_chip1 = 1000
k_chip2 = 2000
k_chip3 = 5000
k_chip4 = 25000
k_chip5 = 100000
k_chip6 = 500000

# CNY 칩 가격
c_chip1 = 1
c_chip2 = 10
c_chip3 = 50
c_chip4 = 2500
c_chip5 = 1000
c_chip6 = 5000

# USD 칩 가격
d_chip1 = 1
d_chip2 = 5
d_chip3 = 10
d_chip4 = 30
d_chip5 = 100
d_chip6 = 200

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


def start_autobet():
    print(stop_step)
    global basecost, martin2, martin3, martin4, martin5, martin6, martin7, martin8, martin9, martin10, martin11, martin12, martin13, martin14, martin15, martin16, martin17, martin18, martin19, martin20, martin21, martin22, martin23, martin24, martin25, martin26, martin27, martin28, martin29, martin30, martin31, martin32, martin33, martin34, martin35, martin36, martin37, martin38, martin39, martin40, profit_stop2, loss_stop2, lose, betstop, pause_status, pause_status2

    pause_status = False
    pause_status2 = False

    entry_99.state(['disabled'])

    betstop = False

    pause_control(0)

    martin_set_zero()

    if selected_value2 != "마틴단계설정":
        try:
            basecost = int(entry_10.get()) if entry_10.get() else 0
            martin2 = int(entry_11.get()) if entry_11.get() else 0
            martin3 = int(entry_12.get()) if entry_12.get() else 0
            martin4 = int(entry_13.get()) if entry_13.get() else 0
            martin5 = int(entry_14.get()) if entry_14.get() else 0
            martin6 = int(entry_15.get()) if entry_15.get() else 0
            martin7 = int(entry_16.get()) if entry_16.get() else 0
            martin8 = int(entry_17.get()) if entry_17.get() else 0
            martin9 = int(entry_18.get()) if entry_18.get() else 0
            martin10 = int(entry_19.get()) if entry_19.get() else 0
            martin11 = int(entry_20.get()) if entry_20.get() else 0
            martin12 = int(entry_21.get()) if entry_21.get() else 0
            martin13 = int(entry_22.get()) if entry_22.get() else 0
            martin14 = int(entry_23.get()) if entry_23.get() else 0
            martin15 = int(entry_224.get()) if entry_224.get() else 0
            martin16 = int(entry_225.get()) if entry_225.get() else 0
            martin17 = int(entry_226.get()) if entry_226.get() else 0
            martin18 = int(entry_227.get()) if entry_227.get() else 0
            martin19 = int(entry_228.get()) if entry_228.get() else 0
            martin20 = int(entry_229.get()) if entry_229.get() else 0
            martin21 = int(entry_231.get()) if entry_231.get() else 0
            martin22 = int(entry_232.get()) if entry_232.get() else 0
            martin23 = int(entry_233.get()) if entry_233.get() else 0
            martin24 = int(entry_234.get()) if entry_234.get() else 0
            martin25 = int(entry_235.get()) if entry_235.get() else 0
            martin26 = int(entry_236.get()) if entry_236.get() else 0
            martin27 = int(entry_237.get()) if entry_237.get() else 0
            martin28 = int(entry_238.get()) if entry_238.get() else 0
            martin29 = int(entry_239.get()) if entry_239.get() else 0
            martin30 = int(entry_240.get()) if entry_240.get() else 0
            martin31 = int(entry_241.get()) if entry_241.get() else 0
            martin32 = int(entry_242.get()) if entry_242.get() else 0
            martin33 = int(entry_243.get()) if entry_243.get() else 0
            martin34 = int(entry_244.get()) if entry_244.get() else 0
            martin35 = int(entry_245.get()) if entry_245.get() else 0
            martin36 = int(entry_246.get()) if entry_246.get() else 0
            martin37 = int(entry_247.get()) if entry_247.get() else 0
            martin38 = int(entry_248.get()) if entry_248.get() else 0
            martin39 = int(entry_249.get()) if entry_249.get() else 0
            martin40 = int(entry_250.get()) if entry_250.get() else 0

            profit_stop2 = int(entry_5.get()) if entry_5.get() else 0
            loss_stop2 = int(entry_4.get()) if entry_4.get() else 0
        except ValueError:
            basecost = 0  # 입력 값이 숫자가 아닌 경우 0을 할당
            martin2 = 0
            martin3 = 0
            martin4 = 0
            martin5 = 0
            martin6 = 0
            martin7 = 0
            martin8 = 0
            martin9 = 0
            martin10 = 0
            martin11 = 0
            martin12 = 0
            martin13 = 0
            martin14 = 0
            martin15 = 0
            martin16 = 0
            martin17 = 0
            martin18 = 0
            martin19 = 0
            martin20 = 0
            martin21 = 0
            martin22 = 0
            martin23 = 0
            martin24 = 0
            martin25 = 0
            martin26 = 0
            martin27 = 0
            martin28 = 0
            martin29 = 0
            martin30 = 0
            martin31 = 0
            martin32 = 0
            martin33 = 0
            martin34 = 0
            martin35 = 0
            martin36 = 0
            martin37 = 0
            martin38 = 0
            martin39 = 0
            martin40 = 0
            profit_stop2 = 0
            loss_stop2 = 0

        if (basecost == "" or basecost == 0) and selected_index > 0:
            tkinter.messagebox.showwarning("오류", "베이스금액이 입력되지 않았습니다.")
        else:
            print("오토시작")
            global s_bet, group1_sum
            s_bet = True
            lose = False
            group1_sum = basecost + martin2 + martin3 + martin4 + martin5 + martin6

            s = martin_kind + " 오토프로그램 시작"
            entry_25.insert(tk.END,
                            "==================================\n%s\n==================================\n\n" % s.center(
                                30))
            recode_log('START', start_price, current_price, 0, d_title, r_title, "", "", "", cal)

    else:
        tkinter.messagebox.showwarning("통화 및 마틴단계 선택", "게임에서 사용될 통화 및 마틴단계를 선택 후 다시 시도해 주세요.")
    if re_start:
        entry_25.insert(tk.END, str(stop_step) + "마틴부터 다시 시작\n\n")
        entry_25.see(tk.END)


def stop_autobet():
    global check_type, cal

    print("오토정지")
    global s_bet, step, current_price, re_start
    entry_99.state(['!disabled'])
    re_start = True
    s_bet = False
    check_type = ""
    step = 0
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
    recode_log('STOP', start_price, current_price, 0, d_title, r_title, "", "", round, cal)
    time.sleep(2)
    try:
        current_price = driver.find_element(By.CSS_SELECTOR, '.amount--bb99f span').get_attribute('innerText').strip()
        price_number = re.sub(r'[^0-9.]', '', current_price)
        cal = int(float(price_number)) - int(float(price_number2))
    except:
        print("오류")
    recode_log('STOP_PRICE_CHECK', start_price, current_price, 0, d_title, r_title, "", "", round, cal)
    time.sleep(2)
    try:
        current_price = driver.find_element(By.CSS_SELECTOR, '.amount--bb99f span').get_attribute('innerText').strip()
        price_number = re.sub(r'[^0-9.]', '', current_price)
        cal = int(float(price_number)) - int(float(price_number2))
    except:
        print("오류")
    recode_log('STOP_PRICE_CHECK', start_price, current_price, 0, d_title, r_title, "", "", round, cal)


def profit_stop_func():
    print("수익으로 인한 오토정지")
    global s_bet, step, start
    s_bet = False
    step = 0
    start = True
    s = "수익으로 인한 오토프로그램 정지"
    entry_25.insert(tk.END,
                    "==================================\n%s\n==================================\n\n\n" % s.center(30))
    entry_25.see(tk.END)
    recode_log('PROFIT_STOP', start_price, current_price, 0, d_title, r_title, "", "", round, cal)


def loss_stop_func():
    print("손실로 인한 오토정지")
    global s_bet, step, start
    s_bet = False
    step = 0
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


def chip_selection(price, c_res, step, round, bonus):
    global current_price

    bet_price = int(price)
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
            entry_25.insert(tk.END, (", ".join(result) + " " + tx + "에 " + str(
                bet_price) + "원 배팅\n\n=================================\n\n"))
            entry_25.see(tk.END)
            recode_log('RUNNING', start_price, current_price, bet_price, d_title, r_title, tx, step, round, cal)
        else:
            entry_25.insert(tk.END, (", ".join(result) + " " + c_res + "에 " + str(
                bet_price) + "원 배팅\n\n=================================\n\n"))
            entry_25.see(tk.END)
            recode_log('RUNNING', start_price, current_price, bet_price, d_title, r_title, c_res, step, round, cal)




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
    step = 0
    start = True
    messagebox.showinfo("결과", "마틴단계 1단계로 복귀")


def stop_action():
    stop_autobet()
    messagebox.showinfo("결과", "프로그램 일시정지")


def create_alert():
    try:
        sound_path = resource_path(os.path.join("assets", "beep.mp3"))
        playsound.playsound(sound_path, block=False)
    except:
        print("사운드오류")
    top = Toplevel()
    top.title("진행여부")
    top.geometry("500x200")
    top.configure(bg="#FFFFFF")
    top.attributes("-topmost", True)

    canvas = Canvas(
        top,
        bg="#FFFFFF",
        height=200,
        width=500,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )

    canvas.place(x=0, y=0)
    canvas.create_text(
        90.99999999999989,
        42.00000000000001,
        anchor="nw",
        text="이 창은 입력이 없을시 5초후에\n자동으로 종료되고 다음단계를 진행합니다.",
        fill="#000000",
        font=("Inter SemiBold", 18 * -1)
    )

    confirm_btn = Button(
        top,
        text="계속진행",
        bg="#3A7FF6",
        fg="#FFFFFF",
        borderwidth=0,
        highlightthickness=0,
        command=lambda: [confirm_action(), top.destroy()],
        relief="flat"
    )
    confirm_btn.place(
        x=26.999999999999883,
        y=116.0,
        width=138.41378784179688,
        height=42.2931022644043
    )

    go1_btn = Button(
        top,
        text="1단계로",
        bg="#077D21",
        fg="#FFFFFF",
        borderwidth=0,
        highlightthickness=0,
        command=lambda: [cancel_action(), top.destroy()],
        relief="flat"
    )
    go1_btn.place(
        x=180.79310607910145,
        y=116.0,
        width=138.41378784179688,
        height=42.2931022644043
    )

    stop_btn = Button(
        top,
        text="일시정지",
        bg="#F63A67",
        fg="#FFFFFF",
        borderwidth=0,
        highlightthickness=0,
        command=lambda: [stop_action(), top.destroy()],
        relief="flat"
    )
    stop_btn.place(
        x=334.586212158203,
        y=116.0,
        width=138.41378784179688,
        height=42.2931022644043
    )

    # 5초 후에 자동으로 창을 닫습니다.
    top.after(6000, top.destroy)


martin_values = [basecost, martin2, martin3, martin4, martin5, martin6, martin7, martin8, martin9, martin10, martin11,
                 martin12, martin13, martin14, martin15, martin16, martin17, martin18, martin19, martin20, martin21,
                 martin22, martin23, martin24, martin25, martin26, martin27, martin28, martin29, martin30, martin31,
                 martin32, martin33, martin34, martin35, martin36, martin37, martin38, martin39, martin40]

win_stack = 0
tie_stack = 0
lose_stack = 0
stop_check = False
stop_check2 = False
stop_check3 = False
stop_check4 = False
stop_step2 = 0
compare_mybet = ""
# 우선순위 리스트 생성
priority_list = ['a', 'b', 'c', 'd', 'e', 'f']

# 이전에 선택된 변수를 저장할 변수
previously_selected = None
current_group = 'group1'
highest_variable = ''
highest_variable2 = ''
highest_variable3 = ''

element_length = 0

long_go_o = False
long_go_x = False

round = ""

def fetch_data(driver2):
    def get_element_value(selector):
        try:
            element = driver2.find_element(By.CSS_SELECTOR, selector)
            return int(element.get_attribute('data-value').strip())
        except (NoSuchElementException, ValueError, AttributeError):
            return 0  # 요소가 없거나 값이 잘못된 경우 기본값 0을 반환

    recent_percent1 = get_element_value('.result1 .recent_percent1')
    recent_percent1_2 = get_element_value('.result1 .recent_percent2')
    recent_percent2 = get_element_value('.result2 .recent_percent1')
    recent_percent2_2 = get_element_value('.result2 .recent_percent2')
    recent_percent3 = get_element_value('.result3 .recent_percent1')
    recent_percent3_2 = get_element_value('.result3 .recent_percent2')

    return {
        'group1': [('a', recent_percent2), ('b', recent_percent2_2)],
        'group2': [('c', recent_percent1), ('d', recent_percent1_2)],
        'group3': [('e', recent_percent3), ('f', recent_percent3_2)]
    }

def fetch_data2(driver2):
    def get_element_value(selector):
        try:
            element = driver2.find_element(By.CSS_SELECTOR, selector)
            return int(element.get_attribute('data-value').strip())
        except (NoSuchElementException, ValueError, AttributeError):
            return 0  # 요소가 없거나 값이 잘못된 경우 기본값 0을 반환

    recent_percent1 = get_element_value('.result1 .recent_percent1')
    max_percent1 = get_element_value('.result1 .max_lost.max_lost1')
    recent_percent1_2 = get_element_value('.result1 .recent_percent2')
    max_percent1_2 = get_element_value('.result1 .max_lost.max_lost2')
    recent_percent2 = get_element_value('.result2 .recent_percent1')
    max_percent2 = get_element_value('.result2 .max_lost.max_lost1')
    recent_percent2_2 = get_element_value('.result2 .recent_percent2')
    max_percent2_2 = get_element_value('.result2 .max_lost.max_lost2')
    recent_percent3 = get_element_value('.result3 .recent_percent1')
    max_percent3 = get_element_value('.result3 .max_lost.max_lost1')
    recent_percent3_2 = get_element_value('.result3 .recent_percent2')
    max_percent3_2 = get_element_value('.result3 .max_lost.max_lost2')

    return {
        'group1': [('a', (recent_percent2*1.5)+max_percent2), ('b', (recent_percent2_2*1.5)+max_percent2_2)],
        'group2': [('c', (recent_percent1*1.5)+max_percent1), ('d', (recent_percent1_2*1.5)+max_percent1_2)],
        'group3': [('e', (recent_percent3*1.5)+max_percent3), ('f', (recent_percent3_2*1.5)+max_percent3_2)]
    }

def select_highest_variable(groups, previously_selected):
    # 전체 변수들을 하나의 리스트로 합침
    all_variables = [var for group_vars in groups.values() for var in group_vars]

    # 값을 기준으로 내림차순 정렬, 값이 같으면 우선순위에 따라 정렬
    all_variables.sort(key=lambda x: (-x[1], priority_list.index(x[0])))

    # 결과를 저장할 변수
    highest_variable = None

    # 가장 높은 값을 가지는 변수를 선택
    for var_name, var_value in all_variables:
        highest_variable = var_name
        break

    return highest_variable


def select_highest_variable2(groups):
    # 그룹 1, 2, 3의 첫 번째 변수만 비교하고, 같은 그룹에서 선택되지 않도록 함
    selected_vars = [('a', groups['group1'][0][1], 'group1'), ('c', groups['group2'][0][1], 'group2'), ('e', groups['group3'][0][1], 'group3')]

    # 값을 기준으로 내림차순 정렬, 값이 같으면 우선순위에 따라 정렬
    selected_vars.sort(key=lambda x: (-x[1], priority_list.index(x[0])))

    # 결과를 저장할 변수
    highest_variable2 = None

    for var in selected_vars:
        if var[2] != current_group:
            highest_variable2 = var[0]
            break

    return highest_variable2

def select_highest_variable3(groups):
    # 그룹 1, 2, 3의 두 번째 변수만 비교하고, 같은 그룹에서 선택되지 않도록 함
    selected_vars = [('b', groups['group1'][1][1], 'group1'), ('d', groups['group2'][1][1], 'group2'), ('f', groups['group3'][1][1], 'group3')]

    # 값을 기준으로 내림차순 정렬, 값이 같으면 우선순위에 따라 정렬
    selected_vars.sort(key=lambda x: (-x[1], priority_list.index(x[0])))

    # 결과를 저장할 변수
    highest_variable3 = None

    for var in selected_vars:
        if var[2] != current_group:
            highest_variable3 = var[0]
            break

    return highest_variable3

def determine_group(variable):
    if variable in ['a', 'b']:
        return 'group1'
    elif variable in ['c', 'd']:
        return 'group2'
    elif variable in ['e', 'f']:
        return 'group3'
    return None

def main_loop(driver2):
    global previously_selected, current_group, highest_variable, highest_variable2, highest_variable3

    while True:
        # 데이터를 가져옴
        groups = fetch_data(driver2)
        groups2 = fetch_data2(driver2)

        # 가장 높은 값을 가지는 변수를 선택
        highest_variable = select_highest_variable(groups, previously_selected)
        print(f"가장 높은 값을 가지는 변수: {highest_variable}")

        # 현재 그룹을 결정
        current_group = determine_group(highest_variable)
        print(f"현재 그룹: {current_group}")

        # 가장 높은 값을 가지는 변수 2 선택
        highest_variable2 = select_highest_variable2(groups2)
        print(f"a, c, e 중 가장 높은 값을 가지는 변수: {highest_variable2}")

        # 가장 높은 값을 가지는 변수 3 선택
        highest_variable3 = select_highest_variable3(groups2)
        print(f"b, d, f 중 가장 높은 값을 가지는 변수: {highest_variable3}")

        # 이전에 선택된 변수 업데이트
        previously_selected = highest_variable

        # 예제에서는 루프를 한번만 돌도록 설정 (실제 사용에서는 루프 지속 필요)
        break

def stop_bet():
    global betstop
    betstop = True
    entry_25.insert(tk.END, (
        "=======================================\n실제 칩 배팅 정지\n=======================================\n\n"))
    entry_25.see(tk.END)


def autoBet(driver, driver2):
    martin_list = [basecost, martin2, martin3, martin4, martin5, martin6, martin7, martin8, martin9, martin10, martin11,
                   martin12, martin13, martin14, martin15, martin16, martin17, martin18, martin19, martin20, martin21,
                   martin22, martin23, martin24, martin25, martin26, martin27, martin28, martin29, martin30, martin31,
                   martin32, martin33, martin34, martin35, martin36, martin37, martin38, martin39, martin40]

    if s_bet:
        global step, x_stop, lose, start, current_price, t_check, last_tie_step, group_level, player_area, banker_area, player_bonus, banker_bonus, group2_get, group2_get_sum, tie_on, re_start, win_stack, ask_dialog, tie_step, tie_area, tie_stack, stop_check, stop_check2, stop_check3, stop_check4, lose_stack, stop_step2, check_type, check_kind, compare_mybet, highest_variable, element_length, previously_selected, current_group, long_go_o, long_go_x, round, cal

        player_area = driver.find_element(By.CSS_SELECTOR, '.player--d9544')
        banker_area = driver.find_element(By.CSS_SELECTOR, '.banker--7e77b')
        player_bonus = driver.find_element(By.CSS_SELECTOR, '.left--caa19 .item--11cf3')
        banker_bonus = driver.find_element(By.CSS_SELECTOR, '.right--87590 .item--11cf3')
        tie_area = driver.find_element(By.CSS_SELECTOR, '.tie--a582d')
        current_price = driver.find_element(By.CSS_SELECTOR, '.amount--bb99f span').get_attribute('innerText').strip()
        round = driver2.find_element(By.CSS_SELECTOR, '.result1 .current_no').get_attribute('innerText').strip()

        price_number = re.sub(r'[^0-9.]', '', current_price)
        cal = int(float(price_number)) - int(float(price_number2))
        positive_cal = cal * -1

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
                stop_check1 = driver2.find_element(By.CSS_SELECTOR,
                                                   '.result.active .pattern2 > ul:last-child > li:last-child p').get_attribute(
                    'innerHTML').strip()
                double_up_check = len(
                    driver2.find_elements(By.CSS_SELECTOR, '.result.active .pattern2 > ul:last-child > li'))

                recent_percent1 = int(driver2.find_element(By.CSS_SELECTOR, '.result1 .recent_percent1').get_attribute(
                    'data-value').strip())
                max_percent1 = int(driver2.find_element(By.CSS_SELECTOR, '.result1 .max_lost.max_lost1').get_attribute(
                    'data-value').strip())
                recent_percent1_2 = int(
                    driver2.find_element(By.CSS_SELECTOR, '.result1 .recent_percent2').get_attribute(
                        'data-value').strip())
                max_percent1_2 = int(
                    driver2.find_element(By.CSS_SELECTOR, '.result1 .max_lost.max_lost2').get_attribute(
                        'data-value').strip())
                recent_percent2 = int(driver2.find_element(By.CSS_SELECTOR, '.result2 .recent_percent1').get_attribute(
                    'data-value').strip())
                max_percent2 = int(driver2.find_element(By.CSS_SELECTOR, '.result2 .max_lost.max_lost1').get_attribute(
                    'data-value').strip())
                recent_percent2_2 = int(
                    driver2.find_element(By.CSS_SELECTOR, '.result2 .recent_percent2').get_attribute(
                        'data-value').strip())
                max_percent2_2 = int(
                    driver2.find_element(By.CSS_SELECTOR, '.result2 .max_lost.max_lost2').get_attribute(
                        'data-value').strip())
                recent_percent3 = int(driver2.find_element(By.CSS_SELECTOR, '.result3 .recent_percent1').get_attribute(
                    'data-value').strip())
                max_percent3 = int(driver2.find_element(By.CSS_SELECTOR, '.result2 .max_lost.max_lost1').get_attribute(
                    'data-value').strip())
                recent_percent3_2 = int(
                    driver2.find_element(By.CSS_SELECTOR, '.result3 .recent_percent2').get_attribute(
                        'data-value').strip())
                max_percent3_2 = int(
                    driver2.find_element(By.CSS_SELECTOR, '.result3 .max_lost.max_lost2').get_attribute(
                        'data-value').strip())

                element_length = len(driver2.find_elements(By.CSS_SELECTOR, '.result1 .pattern2 > ul > li'))

            except NoSuchElementException:
                stop_check1 = False
                double_up_check = 0

                recent_percent1 = 0
                max_percent1 = 0
                recent_percent1_2 = 0
                max_percent1_2 = 0
                recent_percent2 = 0
                max_percent2 = 0
                recent_percent2_2 = 0
                max_percent2_2 = 0
                recent_percent3 = 0
                max_percent3 = 0
                recent_percent3_2 = 0
                max_percent3_2 = 0

                element_length = 0

            if check_type == "O":
                if ox == "X":
                    if t_check == "TIE":
                        pass
                    else:
                        if not start:
                            if lose_stack <= long_stop_value:
                                lose_stack += 1

                if (cal > 0) and (profit_stop2 != 0 and profit_stop2 < cal):
                    profit_stop_func()
                    pass
                elif (cal < 0) and (loss_stop2 != 0 and loss_stop2 < positive_cal):
                    loss_stop_func()
                    pass
                elif (stop_check1 and stop_check1 == "X") and lose:
                    if t_check == "TIE":
                        step = last_tie_step
                        last_tie_step = 0
                        lose = True
                        group_level = 1
                        entry_25.insert(tk.END, (str(step + 1) + "마틴 진행\n"))
                        entry_25.see(tk.END)
                        chip_selection(martin_list[step], c_res, step, round, "")
                        compare_mybet = c_res
                        tie_on = False
                        tie_stack += 1
                    else:
                        entry_25.insert(tk.END, ("처음으로 단계로 돌아감\n"))
                        entry_25.see(tk.END)
                        group_level = 1
                        step = 0
                        lose_stack = 0
                        start = True
                        tie_on = False
                        lose = False
                        pass
                elif (stop_check1 and stop_check1 == "X") and (
                        double_up_check >= long_stop_value2) and long_stop_w2:
                    if double_up_check > long_stop_value2:
                        if t_check == "TIE":
                            lose_stack = lose_stack
                        else:
                            lose_stack -= 1
                    entry_25.insert(tk.END,
                                    ("연속 패 : " + str(lose_stack) + "패 - " + str(
                                        long_stop_value) + "연패시 정지후 패턴 변경\n\n"))
                    entry_25.see(tk.END)
                    entry_25.insert(tk.END, ("X장줄 예상 정지중..\n"))
                    entry_25.see(tk.END)
                    recode_log('LONG_STOP', start_price, current_price, 0, d_title, r_title, "", "", round, cal)
                    stop_check = True
                    stop_check2 = True

                    if (stop_check1 and stop_check1 == "X") and (lose_stack >= long_stop_value) and long_stop_w:
                        stop_check = True
                        stop_check2 = True
                        stop_check3 = True
                        stop_check4 = True
                        stop_step2 = step

                        if not long_go_o:
                            entry_25.insert(tk.END, ("연패방지 정지 후 패턴이동..\n"))
                            entry_25.see(tk.END)
                            recode_log('CHANGE_STOP', start_price, current_price, 0, d_title, r_title, "", "", round, cal)
                            if check_kind == "A":
                                if recent_percent2 > recent_percent2_2 and recent_percent2 > recent_percent3 and recent_percent2 > recent_percent3_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                    check_type = "O"
                                elif recent_percent2_2 > recent_percent2 and recent_percent2_2 > recent_percent3 and recent_percent2_2 > recent_percent3_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                    time.sleep(0.2)
                                    driver2.find_element(By.CSS_SELECTOR, '.result2 .tc2').click()
                                    check_type = "X"
                                elif recent_percent3 > recent_percent2 and recent_percent3 > recent_percent2_2 and recent_percent3 > recent_percent3_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result3').click()
                                    check_type = "O"
                                elif recent_percent3_2 > recent_percent2 and recent_percent3_2 > recent_percent3 and recent_percent3_2 > recent_percent2_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result3').click()
                                    time.sleep(0.2)
                                    driver2.find_element(By.CSS_SELECTOR, '.result3 .tc2').click()
                                    check_type = "X"
                                elif (
                                        recent_percent2 == recent_percent3 or recent_percent2 == recent_percent3_2) and recent_percent2 > recent_percent2_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                    check_type = "O"
                                elif (
                                        recent_percent2_2 == recent_percent3_2 or recent_percent2_2 == recent_percent3) and recent_percent2_2 > recent_percent2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                    time.sleep(0.2)
                                    driver2.find_element(By.CSS_SELECTOR, '.result2 .tc2').click()
                                    check_type = "X"
                            elif check_kind == "B":
                                if recent_percent1 > recent_percent1_2 and recent_percent1 > recent_percent3 and recent_percent1 > recent_percent3_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                                    check_type = "O"
                                elif recent_percent1_2 > recent_percent1 and recent_percent1_2 > recent_percent3 and recent_percent1_2 > recent_percent3_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                                    time.sleep(0.2)
                                    driver2.find_element(By.CSS_SELECTOR, '.result1 .tc2').click()
                                    check_type = "X"
                                elif recent_percent3 > recent_percent1 and recent_percent3 > recent_percent1_2 and recent_percent3 > recent_percent3_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result3').click()
                                    check_type = "O"
                                elif recent_percent3_2 > recent_percent1 and recent_percent3_2 > recent_percent3 and recent_percent3_2 > recent_percent1_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result3').click()
                                    time.sleep(0.2)
                                    driver2.find_element(By.CSS_SELECTOR, '.result3 .tc2').click()
                                    check_type = "X"
                                elif (
                                        recent_percent1 == recent_percent3 or recent_percent1 == recent_percent3_2) and recent_percent1 > recent_percent1_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                                    check_type = "O"
                                elif (
                                        recent_percent1_2 == recent_percent3_2 or recent_percent1_2 == recent_percent3) and recent_percent1_2 > recent_percent1:
                                    driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                                    time.sleep(0.2)
                                    driver2.find_element(By.CSS_SELECTOR, '.result1 .tc2').click()
                                    check_type = "X"
                            elif check_kind == "C":
                                if recent_percent1 > recent_percent1_2 and recent_percent1 > recent_percent2 and recent_percent1 > recent_percent2_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                                    check_type = "O"
                                elif recent_percent1_2 > recent_percent1 and recent_percent1_2 > recent_percent2 and recent_percent1_2 > recent_percent2_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                                    time.sleep(0.2)
                                    driver2.find_element(By.CSS_SELECTOR, '.result1 .tc2').click()
                                    check_type = "X"
                                elif recent_percent2 > recent_percent1 and recent_percent2 > recent_percent1_2 and recent_percent2 > recent_percent2_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                    check_type = "O"
                                elif recent_percent2_2 > recent_percent1 and recent_percent2_2 > recent_percent2 and recent_percent2_2 > recent_percent1_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                    time.sleep(0.2)
                                    driver2.find_element(By.CSS_SELECTOR, '.result2 .tc2').click()
                                    check_type = "X"
                                elif (
                                        recent_percent1 == recent_percent2 or recent_percent1 == recent_percent2_2) and recent_percent2 > recent_percent2_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                    check_type = "O"
                                elif (
                                        recent_percent1_2 == recent_percent2_2 or recent_percent1_2 == recent_percent2) and recent_percent2_2 > recent_percent2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                    time.sleep(0.2)
                                    driver2.find_element(By.CSS_SELECTOR, '.result2 .tc2').click()
                                    check_type = "X"
                            lose_stack = 0
                    pass
                elif (stop_check1 and stop_check1 == "X") and (lose_stack >= long_stop_value) and long_stop_w:
                    entry_25.insert(tk.END, ("연패방지 정지 후 패턴이동..\n"))
                    entry_25.see(tk.END)
                    recode_log('CHANGE_STOP', start_price, current_price, 0, d_title, r_title, "", "", round, cal)
                    stop_check = True
                    stop_check2 = True
                    stop_check3 = True
                    stop_check4 = True
                    stop_step2 = step
                    if not long_go_o:
                        if check_kind == "A":
                            if recent_percent2 > recent_percent2_2 and recent_percent2 > recent_percent3 and recent_percent2 > recent_percent3_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                check_type = "O"
                            elif recent_percent2_2 > recent_percent2 and recent_percent2_2 > recent_percent3 and recent_percent2_2 > recent_percent3_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                time.sleep(0.2)
                                driver2.find_element(By.CSS_SELECTOR, '.result2 .tc2').click()
                                check_type = "X"
                            elif recent_percent3 > recent_percent2 and recent_percent3 > recent_percent2_2 and recent_percent3 > recent_percent3_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result3').click()
                                check_type = "O"
                            elif recent_percent3_2 > recent_percent2 and recent_percent3_2 > recent_percent3 and recent_percent3_2 > recent_percent2_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result3').click()
                                time.sleep(0.2)
                                driver2.find_element(By.CSS_SELECTOR, '.result3 .tc2').click()
                                check_type = "X"
                            elif (
                                    recent_percent2 == recent_percent3 or recent_percent2 == recent_percent3_2) and recent_percent2 > recent_percent2_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                check_type = "O"
                            elif (
                                    recent_percent2_2 == recent_percent3_2 or recent_percent2_2 == recent_percent3) and recent_percent2_2 > recent_percent2:
                                driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                time.sleep(0.2)
                                driver2.find_element(By.CSS_SELECTOR, '.result2 .tc2').click()
                                check_type = "X"
                        elif check_kind == "B":
                            if recent_percent1 > recent_percent1_2 and recent_percent1 > recent_percent3 and recent_percent1 > recent_percent3_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                                check_type = "O"
                            elif recent_percent1_2 > recent_percent1 and recent_percent1_2 > recent_percent3 and recent_percent1_2 > recent_percent3_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                                time.sleep(0.2)
                                driver2.find_element(By.CSS_SELECTOR, '.result1 .tc2').click()
                                check_type = "X"
                            elif recent_percent3 > recent_percent1 and recent_percent3 > recent_percent1_2 and recent_percent3 > recent_percent3_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result3').click()
                                check_type = "O"
                            elif recent_percent3_2 > recent_percent1 and recent_percent3_2 > recent_percent3 and recent_percent3_2 > recent_percent1_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result3').click()
                                time.sleep(0.2)
                                driver2.find_element(By.CSS_SELECTOR, '.result3 .tc2').click()
                                check_type = "X"
                            elif (
                                    recent_percent1 == recent_percent3 or recent_percent1 == recent_percent3_2) and recent_percent1 > recent_percent1_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                                check_type = "O"
                            elif (
                                    recent_percent1_2 == recent_percent3_2 or recent_percent1_2 == recent_percent3) and recent_percent1_2 > recent_percent1:
                                driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                                time.sleep(0.2)
                                driver2.find_element(By.CSS_SELECTOR, '.result1 .tc2').click()
                                check_type = "X"
                        elif check_kind == "C":
                            if recent_percent1 > recent_percent1_2 and recent_percent1 > recent_percent2 and recent_percent1 > recent_percent2_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                                check_type = "O"
                            elif recent_percent1_2 > recent_percent1 and recent_percent1_2 > recent_percent2 and recent_percent1_2 > recent_percent2_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                                time.sleep(0.2)
                                driver2.find_element(By.CSS_SELECTOR, '.result1 .tc2').click()
                                check_type = "X"
                            elif recent_percent2 > recent_percent1 and recent_percent2 > recent_percent1_2 and recent_percent2 > recent_percent2_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                check_type = "O"
                            elif recent_percent2_2 > recent_percent1 and recent_percent2_2 > recent_percent2 and recent_percent2_2 > recent_percent1_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                time.sleep(0.2)
                                driver2.find_element(By.CSS_SELECTOR, '.result2 .tc2').click()
                                check_type = "X"
                            elif (
                                    recent_percent1 == recent_percent2 or recent_percent1 == recent_percent2_2) and recent_percent2 > recent_percent2_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                check_type = "O"
                            elif (
                                    recent_percent1_2 == recent_percent2_2 or recent_percent1_2 == recent_percent2) and recent_percent2_2 > recent_percent2:
                                driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                time.sleep(0.2)
                                driver2.find_element(By.CSS_SELECTOR, '.result2 .tc2').click()
                                check_type = "X"
                        lose_stack = 0
                    pass
                else:
                    long_go_o = False
                    if ox == "X":
                        if martin_kind == "다니엘시스템" or (step > 2 and step < 6):
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

                        win_stack = 0
                        if t_check == "TIE":
                            print(lose_stack)
                            if lose:
                                step = step
                                last_tie_step = 0
                                lose = False
                                group_level = 1
                            else:
                                if stop_check4:
                                    step += 1
                                    stop_check = False
                                    stop_check2 = False
                                    stop_check3 = False
                                    stop_check4 = False
                                else:
                                    step = step
                                    tie_on = True
                                    print("step유지")
                            if long_stop_w:
                                entry_25.insert(tk.END, ("연속 패 : " + str(lose_stack) + "패 - " + str(
                                    long_stop_value) + "연패시 정지후 패턴 변경\n\n"))
                                entry_25.see(tk.END)
                        else:
                            if lose:
                                step = 0
                            else:
                                if win_stack > 1:
                                    step = 0
                                else:
                                    step += 1
                                    long_go_o = False
                                    stop_check = False
                                    stop_check2 = False
                                    stop_check3 = False
                                    stop_check4 = False
                            if start:
                                step = 0
                                lose_stack = 0
                            if long_stop_w:
                                entry_25.insert(tk.END, ("연속 패 : " + str(lose_stack) + "패 - " + str(
                                    long_stop_value) + "연패시 정지후 패턴 변경\n\n"))
                                entry_25.see(tk.END)
                        if re_start:
                            if pause_step != 0:
                                step = pause_step - 1
                            else:
                                step = stop_step - 1
                                group_level = 1
                            re_start = False

                        entry_25.insert(tk.END, (str(step + 1) + "마틴 진행\n"))
                        entry_25.see(tk.END)

                        for i in range(40):
                            if step == i:
                                if selected_index == i + 1:
                                    lose = True
                                    last_tie_step = step
                                    tie_on = True
                                chip_selection(martin_list[i], c_res, step, round, "")
                                if step > 5:
                                    chip_selection(martin_list[i]/5, c_res, step, round, "bonus")
                                compare_mybet = c_res
                                break  # 일치하는 조건을 찾으면 반복문을 종료

                        start = False

                    if ox == "O":

                        if group_level == 2:
                            if group2_get == 0:
                                group2_get = martin9
                            if start:
                                entry_25.insert(tk.END, ("2단계 진행 시작\n"))
                                entry_25.see(tk.END)
                                driver2.find_element(By.CSS_SELECTOR, '.go-level2').click()

                        if t_check == "TIE":
                            tie_stack += 1
                            if lose:
                                step = last_tie_step
                                last_tie_step = 0
                                lose = False
                                group_level = 1

                            else:
                                if stop_check4:
                                    step += 1
                                    stop_check = False
                                    stop_check2 = False
                                    stop_check3 = False
                                    stop_check4 = False
                                else:
                                    step = step
                                    print("step유지")

                                if martin_kind == "크루즈1" or martin_kind == "크루즈2" or martin_kind == "크루즈3" or martin_kind == "크루즈4" or martin_kind == "크루즈5" or martin_kind == "크루즈3_2" or martin_kind == "크루즈3_3" or martin_kind == "크루즈3_4":
                                    entry_25.insert(tk.END,
                                                    ("연속 승 : " + str(win_stack) + "승 - 2연승시 마틴 1단계로 복귀\n\n"))
                                    entry_25.see(tk.END)
                                if (martin_kind == "일반+크루즈" and step > 3) or (martin_kind == "슈퍼+크루즈" and step > 3):
                                    entry_25.insert(tk.END,
                                                    ("연속 승 : " + str(win_stack) + "승 - 2연승시 마틴 1단계로 복귀\n\n"))
                                    entry_25.see(tk.END)
                                if (martin_kind == "일반+크루즈_2" and step > 4) or (martin_kind == "슈퍼+크루즈_2" and step > 4):
                                    entry_25.insert(tk.END,
                                                    ("연속 승 : " + str(win_stack) + "승 - 2연승시 마틴 1단계로 복귀\n\n"))
                                    entry_25.see(tk.END)

                        else:
                            if start or re_start:
                                win_stack = 0
                            else:
                                if stop_check2:
                                    if stop_check3:

                                        lose_stack = 0
                                    else:
                                        win_stack = 0
                                    stop_check2 = False
                                    stop_check3 = False

                                elif stop_check3:

                                    stop_check3 = False
                                    lose_stack = 0

                                else:
                                    lose_stack = 0
                                    win_stack += 1

                                if martin_kind == "크루즈1" or martin_kind == "크루즈2":
                                    if step < 7:
                                        entry_25.insert(tk.END,
                                                        ("연속 승 : " + str(win_stack) + "승 - 2연승시 마틴 1단계로 복귀\n\n"))
                                        entry_25.see(tk.END)
                                if martin_kind == "크루즈3" or martin_kind == "크루즈4" or martin_kind == "크루즈5":
                                    if win_stack > 0 and step > selected_index - 4:
                                        step = 0
                                    else:
                                        entry_25.insert(tk.END,
                                                        ("연속 승 : " + str(win_stack) + "승 - 2연승시 마틴 1단계로 복귀\n\n"))
                                        entry_25.see(tk.END)
                                if martin_kind == "크루즈3_2" or martin_kind == "크루즈3_3" or martin_kind == "크루즈3_4":
                                    entry_25.insert(tk.END,
                                                    ("연속 승 : " + str(win_stack) + "승 - 2연승시 마틴 1단계로 복귀\n\n"))
                                    entry_25.see(tk.END)
                                if martin_kind == "일반+크루즈" or martin_kind == "슈퍼+크루즈":
                                    if step > 3:
                                        entry_25.insert(tk.END,
                                                        ("연속 승 : " + str(win_stack) + "승 - 2연승시 마틴 1단계로 복귀\n\n"))
                                        entry_25.see(tk.END)
                                if martin_kind == "일반+크루즈_2" or martin_kind == "슈퍼+크루즈_2":
                                    if step > 4:
                                        entry_25.insert(tk.END,
                                                        ("연속 승 : " + str(win_stack) + "승 - 2연승시 마틴 1단계로 복귀\n\n"))
                                        entry_25.see(tk.END)
                            if lose:
                                if t_check == "TIE":
                                    step = last_tie_step
                                else:
                                    step = 0
                                lose = False
                            else:
                                if martin_kind == "크루즈1" or martin_kind == "크루즈2":
                                    if martin_kind == "크루즈1":
                                        step += 1
                                    if martin_kind == "크루즈2" and win_stack == 0:
                                        step += 1
                                    if win_stack > 1 and step < 7:
                                        step = 0
                                    if win_stack == 2:
                                        try:
                                            sound_path = resource_path(os.path.join("assets", "start.mp3"))
                                            playsound.playsound(sound_path, block=False)
                                        except:
                                            print("사운드오류")
                                elif martin_kind == "크루즈3" or martin_kind == "크루즈4" or martin_kind == "크루즈5":
                                    if stop_check:
                                        if stop_check3:
                                            step -= 1
                                        else:
                                            step += 1
                                        stop_check = False
                                        stop_check2 = False
                                        stop_check3 = False
                                        stop_check4 = False
                                    elif stop_check2:
                                        if stop_check3:
                                            step -= 1
                                            stop_check3 = False
                                        else:
                                            step += 1

                                        stop_check = False
                                        stop_check2 = False
                                        stop_check3 = False
                                        stop_check4 = False
                                    else:
                                        if step == 0:
                                            step = 0
                                        else:
                                            step -= 1

                                    if win_stack > 1:
                                        step = 0
                                    if win_stack == 2:
                                        try:
                                            sound_path = resource_path(os.path.join("assets", "start.mp3"))
                                            playsound.playsound(sound_path, block=False)
                                        except:
                                            print("사운드오류")
                                    if win_stack > 0 and step > selected_index - 4:
                                        step = 0
                                elif martin_kind == "크루즈3_2":
                                    if stop_check:
                                        if stop_check3:
                                            if step == 1:
                                                step = 0
                                            elif step == 0:
                                                step = 0
                                            else:
                                                step -= 2
                                        else:
                                            step += 1
                                        stop_check = False
                                        stop_check2 = False
                                        stop_check3 = False
                                        stop_check4 = False
                                    elif stop_check2:
                                        if stop_check3:
                                            if step == 1:
                                                step = 0
                                            elif step == 0:
                                                step = 0
                                            else:
                                                step -= 2
                                            stop_check3 = False
                                        else:
                                            step += 1

                                        stop_check = False
                                        stop_check2 = False
                                        stop_check3 = False
                                        stop_check4 = False
                                    else:
                                        if step == 0:
                                            step = 0
                                        else:
                                            if step == 1:
                                                step = 0
                                            elif step == 0:
                                                step = 0
                                            else:
                                                step -= 2

                                    if win_stack > 1:
                                        step = 0
                                    if win_stack == 2:
                                        try:
                                            sound_path = resource_path(os.path.join("assets", "start.mp3"))
                                            playsound.playsound(sound_path, block=False)
                                        except:
                                            print("사운드오류")
                                elif martin_kind == "크루즈3_3":
                                    if stop_check:
                                        if stop_check3:
                                            if step == 1:
                                                step = 0
                                            elif step == 0:
                                                step = 0
                                            else:
                                                step -= 3
                                            if step < 0:
                                                step = 0
                                        else:
                                            step += 1
                                        stop_check = False
                                        stop_check2 = False
                                        stop_check3 = False
                                        stop_check4 = False
                                    elif stop_check2:
                                        if stop_check3:
                                            if step == 1:
                                                step = 0
                                            elif step == 0:
                                                step = 0
                                            else:
                                                step -= 3
                                            if step < 0:
                                                step = 0
                                            stop_check3 = False
                                        else:
                                            step += 1

                                        stop_check = False
                                        stop_check2 = False
                                        stop_check3 = False
                                        stop_check4 = False
                                    else:
                                        if step == 0:
                                            step = 0
                                        else:
                                            if step == 1:
                                                step = 0
                                            elif step == 0:
                                                step = 0
                                            else:
                                                step -= 3
                                            if step < 0:
                                                step = 0
                                        if step < 0:
                                            step = 0

                                    if win_stack > 1:
                                        step = 0
                                    if win_stack == 2:
                                        try:
                                            sound_path = resource_path(os.path.join("assets", "start.mp3"))
                                            playsound.playsound(sound_path, block=False)
                                        except:
                                            print("사운드오류")
                                elif martin_kind == "크루즈3_4":
                                    if stop_check:
                                        if stop_check3:
                                            if step == 1:
                                                step = 0
                                            elif step < 1:
                                                step = 0
                                            else:
                                                step -= 4
                                            if step < 0:
                                                step = 0
                                        else:
                                            step += 1
                                        stop_check = False
                                        stop_check2 = False
                                        stop_check3 = False
                                        stop_check4 = False
                                    elif stop_check2:
                                        if stop_check3:
                                            if step == 1:
                                                step = 0
                                            elif step == 0:
                                                step = 0
                                            else:
                                                step -= 4
                                            if step < 0:
                                                step = 0
                                            stop_check3 = False
                                        else:
                                            step += 1

                                        stop_check = False
                                        stop_check2 = False
                                        stop_check3 = False
                                        stop_check4 = False
                                    else:
                                        if step == 0:
                                            step = 0
                                        else:
                                            if step == 1:
                                                step = 0
                                            elif step == 0:
                                                step = 0
                                            else:
                                                step -= 4
                                            if step < 0:
                                                step = 0
                                        if step < 0:
                                            step = 0

                                    if win_stack > 1:
                                        step = 0
                                    if win_stack == 2:
                                        try:
                                            sound_path = resource_path(os.path.join("assets", "start.mp3"))
                                            playsound.playsound(sound_path, block=False)
                                        except:
                                            print("사운드오류")
                                elif martin_kind == "일반+크루즈" or martin_kind == "슈퍼+크루즈":
                                    if stop_check:
                                        if stop_check3 and step > 3:
                                            if step == 1:
                                                step = 0
                                            elif step < 1:
                                                step = 0
                                            else:
                                                if step > 3:
                                                    step = 3
                                                elif step < 4:
                                                    step = 0
                                            if step < 0:
                                                step = 0
                                        else:
                                            step += 1
                                        stop_check = False
                                        stop_check2 = False
                                        stop_check3 = False
                                        stop_check4 = False
                                    elif stop_check2:
                                        if stop_check3 and step > 3:
                                            if step == 1:
                                                step = 0
                                            elif step == 0:
                                                step = 0
                                            else:
                                                if step > 3:
                                                    step = 3
                                                elif step < 4:
                                                    step = 0
                                            if step < 0:
                                                step = 0
                                            stop_check3 = False
                                        else:
                                            step += 1

                                        stop_check = False
                                        stop_check2 = False
                                        stop_check3 = False
                                        stop_check4 = False
                                    else:
                                        if step == 0:
                                            step = 0
                                        else:
                                            if step == 1:
                                                step = 0
                                            elif step == 0:
                                                step = 0
                                            else:
                                                if step > 3:
                                                    step = 3
                                                elif step < 4:
                                                    step = 0
                                            if step < 0:
                                                step = 0
                                        if step < 0:
                                            step = 0

                                    if step > 3:
                                        if win_stack > 1:
                                            step = 0
                                        if win_stack == 2:
                                            try:
                                                sound_path = resource_path(os.path.join("assets", "start.mp3"))
                                                playsound.playsound(sound_path, block=False)
                                            except:
                                                print("사운드오류")
                                elif martin_kind == "일반+크루즈_2" or martin_kind == "슈퍼+크루즈_2":
                                    if stop_check:
                                        if stop_check3 and step > 4:
                                            if step == 1:
                                                step = 0
                                            elif step < 1:
                                                step = 0
                                            else:
                                                if step > 4:
                                                    step = 4
                                                elif step < 5:
                                                    step = 0
                                            if step < 0:
                                                step = 0
                                        else:
                                            step += 1
                                        stop_check = False
                                        stop_check2 = False
                                        stop_check3 = False
                                        stop_check4 = False
                                    elif stop_check2:
                                        if stop_check3 and step > 4:
                                            if step == 1:
                                                step = 0
                                            elif step == 0:
                                                step = 0
                                            else:
                                                if step > 4:
                                                    step = 4
                                                elif step < 5:
                                                    step = 0
                                            if step < 0:
                                                step = 0
                                            stop_check3 = False
                                        else:
                                            step += 1

                                        stop_check = False
                                        stop_check2 = False
                                        stop_check3 = False
                                        stop_check4 = False
                                    else:
                                        if step == 0:
                                            step = 0
                                        else:
                                            if step == 1:
                                                step = 0
                                            elif step == 0:
                                                step = 0
                                            else:
                                                if step > 4:
                                                    step = 4
                                                elif step < 5:
                                                    step = 0
                                            if step < 0:
                                                step = 0
                                        if step < 0:
                                            step = 0

                                    if step > 4:
                                        if win_stack > 1:
                                            step = 0
                                        if win_stack == 2:
                                            try:
                                                sound_path = resource_path(os.path.join("assets", "start.mp3"))
                                                playsound.playsound(sound_path, block=False)
                                            except:
                                                print("사운드오류")

                                else:
                                    if martin_kind == "크루즈1" or martin_kind == "크루즈2":
                                        if win_stack > 1:
                                            step = 0
                                        else:
                                            step += 1
                                    elif martin_kind == "다니엘시스템":
                                        if stop_check:
                                            step += 1
                                            stop_check = False
                                            stop_check2 = False
                                            stop_check3 = False
                                            stop_check4 = False
                                        else:
                                            if step == 0:
                                                step = 0
                                            else:
                                                if step > 12:
                                                    step -= 2
                                                else:
                                                    step -= 1
                                            if step < 0:
                                                step = 0
                                    else:
                                        if stop_check:
                                            step += 1
                                            stop_check = False
                                        else:
                                            step = 0
                            if start:
                                step = 0
                                lose_stack = 0
                            if stop_check3:
                                step = step
                                stop_check3 = False
                                lose_stack = 0
                        if re_start:
                            if pause_step != 0:
                                step = pause_step - 1
                            else:
                                step = stop_step - 1
                                group_level = 1
                            re_start = False

                        if stop_check3 and t_check == "TIE":
                            stop_check3 = False
                            pass
                        else:
                            entry_25.insert(tk.END, (str(step + 1) + "마틴 진행\n"))
                            entry_25.see(tk.END)

                            for i in range(40):
                                if step == i:
                                    if selected_index == i + 1:
                                        lose = True
                                        last_tie_step = step
                                        tie_on = True
                                    chip_selection(martin_list[i], c_res, step, round, "")
                                    if step > 5:
                                        chip_selection(martin_list[i] / 5, c_res, step, round, "bonus")
                                    compare_mybet = c_res
                                    break  # 일치하는 조건을 찾으면 반복문을 종료

                        start = False

                        group2_get = 0
            elif check_type == "X":
                if ox == "O":
                    if t_check == "TIE":
                        pass
                    else:
                        if not start:
                            if lose_stack <= long_stop_value:
                                lose_stack += 1
                if (cal > 0) and (profit_stop2 != 0 and profit_stop2 < cal):
                    profit_stop_func()
                    pass
                elif (cal < 0) and (loss_stop2 != 0 and loss_stop2 < positive_cal):
                    loss_stop_func()
                    pass
                elif (stop_check1 and stop_check1 == "O") and lose:
                    if t_check == "TIE":
                        step = last_tie_step
                        last_tie_step = 0
                        lose = True
                        group_level = 1
                        entry_25.insert(tk.END, (str(step + 1) + "마틴 진행\n"))
                        entry_25.see(tk.END)
                        chip_selection(martin_list[step], c_res, step, round, "")
                        compare_mybet = c_res
                        tie_on = False
                        tie_stack += 1
                    else:
                        entry_25.insert(tk.END, ("처음으로 단계로 돌아감\n"))
                        entry_25.see(tk.END)
                        group_level = 1
                        step = 0
                        lose_stack = 0
                        start = True
                        tie_on = False
                        lose = False
                        pass
                elif (stop_check1 and stop_check1 == "O") and (
                        double_up_check >= long_stop_value2) and long_stop_w2 and not start:
                    if double_up_check > long_stop_value2:
                        if t_check == "TIE":
                            lose_stack = lose_stack
                        else:
                            lose_stack -= 1
                    entry_25.insert(tk.END,
                                    ("연속 패 : " + str(lose_stack) + "패 - " + str(
                                        long_stop_value) + "연패시 정지후 패턴 변경\n\n"))
                    entry_25.see(tk.END)
                    entry_25.insert(tk.END, ("O장줄 예상 정지중..\n"))
                    entry_25.see(tk.END)
                    stop_check = True
                    stop_check2 = True
                    recode_log('LONG_STOP', start_price, current_price, 0, d_title, r_title, "", "", round, cal)

                    if (stop_check1 and stop_check1 == "O") and (lose_stack >= long_stop_value) and long_stop_w:
                        stop_check = True
                        stop_check2 = True
                        stop_check3 = True
                        stop_check4 = True
                        stop_step2 = step

                        if not long_go_x:
                            entry_25.insert(tk.END, ("연패방지 정지 후 패턴이동..\n"))
                            entry_25.see(tk.END)
                            recode_log('CHANGE_STOP', start_price, current_price, 0, d_title, r_title, "", "", round, cal)
                            if check_kind == "A":
                                if recent_percent2 > recent_percent2_2 and recent_percent2 > recent_percent3 and recent_percent2 > recent_percent3_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                    check_type = "O"
                                elif recent_percent2_2 > recent_percent2 and recent_percent2_2 > recent_percent3 and recent_percent2_2 > recent_percent3_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                    time.sleep(0.2)
                                    driver2.find_element(By.CSS_SELECTOR, '.result2 .tc2').click()
                                    check_type = "X"
                                elif recent_percent3 > recent_percent2 and recent_percent3 > recent_percent2_2 and recent_percent3 > recent_percent3_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result3').click()
                                    check_type = "O"
                                elif recent_percent3_2 > recent_percent2 and recent_percent3_2 > recent_percent3 and recent_percent3_2 > recent_percent2_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result3').click()
                                    time.sleep(0.2)
                                    driver2.find_element(By.CSS_SELECTOR, '.result3 .tc2').click()
                                    check_type = "X"
                                elif (
                                        recent_percent2 == recent_percent3 or recent_percent2 == recent_percent3_2) and recent_percent2 > recent_percent2_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                    check_type = "O"
                                elif (
                                        recent_percent2_2 == recent_percent3_2 or recent_percent2_2 == recent_percent3) and recent_percent2_2 > recent_percent2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                    time.sleep(0.2)
                                    driver2.find_element(By.CSS_SELECTOR, '.result2 .tc2').click()
                                    check_type = "X"
                            elif check_kind == "B":
                                if recent_percent1 > recent_percent1_2 and recent_percent1 > recent_percent3 and recent_percent1 > recent_percent3_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                                    check_type = "O"
                                elif recent_percent1_2 > recent_percent1 and recent_percent1_2 > recent_percent3 and recent_percent1_2 > recent_percent3_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                                    time.sleep(0.2)
                                    driver2.find_element(By.CSS_SELECTOR, '.result1 .tc2').click()
                                    check_type = "X"
                                elif recent_percent3 > recent_percent1 and recent_percent3 > recent_percent1_2 and recent_percent3 > recent_percent3_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result3').click()
                                    check_type = "O"
                                elif recent_percent3_2 > recent_percent1 and recent_percent3_2 > recent_percent3 and recent_percent3_2 > recent_percent1_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result3').click()
                                    time.sleep(0.2)
                                    driver2.find_element(By.CSS_SELECTOR, '.result3 .tc2').click()
                                    check_type = "X"
                                elif (
                                        recent_percent1 == recent_percent3 or recent_percent1 == recent_percent3_2) and recent_percent1 > recent_percent1_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                                    check_type = "O"
                                elif (
                                        recent_percent1_2 == recent_percent3_2 or recent_percent1_2 == recent_percent3) and recent_percent1_2 > recent_percent1:
                                    driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                                    time.sleep(0.2)
                                    driver2.find_element(By.CSS_SELECTOR, '.result1 .tc2').click()
                                    check_type = "X"
                            elif check_kind == "C":
                                if recent_percent1 > recent_percent1_2 and recent_percent1 > recent_percent2 and recent_percent1 > recent_percent2_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                                    check_type = "O"
                                elif recent_percent1_2 > recent_percent1 and recent_percent1_2 > recent_percent2 and recent_percent1_2 > recent_percent2_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                                    time.sleep(0.2)
                                    driver2.find_element(By.CSS_SELECTOR, '.result1 .tc2').click()
                                    check_type = "X"
                                elif recent_percent2 > recent_percent1 and recent_percent2 > recent_percent1_2 and recent_percent2 > recent_percent2_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                    check_type = "O"
                                elif recent_percent2_2 > recent_percent1 and recent_percent2_2 > recent_percent2 and recent_percent2_2 > recent_percent1_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                    time.sleep(0.2)
                                    driver2.find_element(By.CSS_SELECTOR, '.result2 .tc2').click()
                                    check_type = "X"
                                elif (
                                        recent_percent1 == recent_percent2 or recent_percent1 == recent_percent2_2) and recent_percent2 > recent_percent2_2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                    check_type = "O"
                                elif (
                                        recent_percent1_2 == recent_percent2_2 or recent_percent1_2 == recent_percent2) and recent_percent2_2 > recent_percent2:
                                    driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                    time.sleep(0.2)
                                    driver2.find_element(By.CSS_SELECTOR, '.result2 .tc2').click()
                                    check_type = "X"
                            lose_stack = 0

                        pass
                elif (stop_check1 and stop_check1 == "O") and (lose_stack >= long_stop_value) and long_stop_w:
                    entry_25.insert(tk.END, ("연패방지 정지 후 패턴이동..\n"))
                    entry_25.see(tk.END)
                    stop_check = True
                    stop_check2 = True
                    stop_check3 = True
                    stop_check4 = True
                    stop_step2 = step
                    recode_log('CHANGE_STOP', start_price, current_price, 0, d_title, r_title, "", "", round, cal)
                    print((recent_percent1_2 * 1.5) + max_percent1_2, (recent_percent2_2 * 1.5) + max_percent2_2,
                          (recent_percent3_2 * 1.5) + max_percent3_2)
                    if not long_go_o:
                        if check_kind == "A":
                            if recent_percent2 > recent_percent2_2 and recent_percent2 > recent_percent3 and recent_percent2 > recent_percent3_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                check_type = "O"
                            elif recent_percent2_2 > recent_percent2 and recent_percent2_2 > recent_percent3 and recent_percent2_2 > recent_percent3_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                time.sleep(0.2)
                                driver2.find_element(By.CSS_SELECTOR, '.result2 .tc2').click()
                                check_type = "X"
                            elif recent_percent3 > recent_percent2 and recent_percent3 > recent_percent2_2 and recent_percent3 > recent_percent3_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result3').click()
                                check_type = "O"
                            elif recent_percent3_2 > recent_percent2 and recent_percent3_2 > recent_percent3 and recent_percent3_2 > recent_percent2_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result3').click()
                                time.sleep(0.2)
                                driver2.find_element(By.CSS_SELECTOR, '.result3 .tc2').click()
                                check_type = "X"
                            elif (
                                    recent_percent2 == recent_percent3 or recent_percent2 == recent_percent3_2) and recent_percent2 > recent_percent2_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                check_type = "O"
                            elif (
                                    recent_percent2_2 == recent_percent3_2 or recent_percent2_2 == recent_percent3) and recent_percent2_2 > recent_percent2:
                                driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                time.sleep(0.2)
                                driver2.find_element(By.CSS_SELECTOR, '.result2 .tc2').click()
                                check_type = "X"
                        elif check_kind == "B":
                            if recent_percent1 > recent_percent1_2 and recent_percent1 > recent_percent3 and recent_percent1 > recent_percent3_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                                check_type = "O"
                            elif recent_percent1_2 > recent_percent1 and recent_percent1_2 > recent_percent3 and recent_percent1_2 > recent_percent3_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                                time.sleep(0.2)
                                driver2.find_element(By.CSS_SELECTOR, '.result1 .tc2').click()
                                check_type = "X"
                            elif recent_percent3 > recent_percent1 and recent_percent3 > recent_percent1_2 and recent_percent3 > recent_percent3_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result3').click()
                                check_type = "O"
                            elif recent_percent3_2 > recent_percent1 and recent_percent3_2 > recent_percent3 and recent_percent3_2 > recent_percent1_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result3').click()
                                time.sleep(0.2)
                                driver2.find_element(By.CSS_SELECTOR, '.result3 .tc2').click()
                                check_type = "X"
                            elif (
                                    recent_percent1 == recent_percent3 or recent_percent1 == recent_percent3_2) and recent_percent1 > recent_percent1_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                                check_type = "O"
                            elif (
                                    recent_percent1_2 == recent_percent3_2 or recent_percent1_2 == recent_percent3) and recent_percent1_2 > recent_percent1:
                                driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                                time.sleep(0.2)
                                driver2.find_element(By.CSS_SELECTOR, '.result1 .tc2').click()
                                check_type = "X"
                        elif check_kind == "C":
                            if recent_percent1 > recent_percent1_2 and recent_percent1 > recent_percent2 and recent_percent1 > recent_percent2_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                                check_type = "O"
                            elif recent_percent1_2 > recent_percent1 and recent_percent1_2 > recent_percent2 and recent_percent1_2 > recent_percent2_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                                time.sleep(0.2)
                                driver2.find_element(By.CSS_SELECTOR, '.result1 .tc2').click()
                                check_type = "X"
                            elif recent_percent2 > recent_percent1 and recent_percent2 > recent_percent1_2 and recent_percent2 > recent_percent2_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                check_type = "O"
                            elif recent_percent2_2 > recent_percent1 and recent_percent2_2 > recent_percent2 and recent_percent2_2 > recent_percent1_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                time.sleep(0.2)
                                driver2.find_element(By.CSS_SELECTOR, '.result2 .tc2').click()
                                check_type = "X"
                            elif (
                                    recent_percent1 == recent_percent2 or recent_percent1 == recent_percent2_2) and recent_percent2 > recent_percent2_2:
                                driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                check_type = "O"
                            elif (
                                    recent_percent1_2 == recent_percent2_2 or recent_percent1_2 == recent_percent2) and recent_percent2_2 > recent_percent2:
                                driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                                time.sleep(0.2)
                                driver2.find_element(By.CSS_SELECTOR, '.result2 .tc2').click()
                                check_type = "X"
                        lose_stack = 0
                    pass
                else:

                    if ox == "O":
                        if martin_kind == "다니엘시스템" or (step > 2 and step < 6):
                            if check_kind == "A":
                                driver2.find_element(By.CSS_SELECTOR, '.result1').click()
                            elif check_kind == "B":
                                driver2.find_element(By.CSS_SELECTOR, '.result2').click()
                            elif check_kind == "C":
                                driver2.find_element(By.CSS_SELECTOR, '.result3').click()
                            current_res = driver2.find_element(By.CSS_SELECTOR,
                                                               '.result.active .o-pattern .to-result')
                            c_res = current_res.get_attribute('innerHTML').strip()
                            check_type = "O"
                        win_stack = 0
                        if t_check == "TIE":
                            print(lose_stack)
                            if lose:
                                step = step
                                last_tie_step = 0
                                lose = False
                                group_level = 1
                            else:
                                if stop_check4:
                                    step += 1
                                    stop_check = False
                                    stop_check2 = False
                                    stop_check3 = False
                                    stop_check4 = False
                                else:
                                    step = step
                                    tie_on = True
                                    print("step유지")
                            if long_stop_w:
                                entry_25.insert(tk.END, ("연속 패 : " + str(lose_stack) + "패 - " + str(
                                    long_stop_value) + "연패시 정지후 패턴 변경\n\n"))
                                entry_25.see(tk.END)
                        else:
                            if lose:
                                step = 0
                            else:
                                if win_stack > 1:
                                    step = 0
                                else:
                                    step += 1
                                    long_go_x = False
                                    stop_check = False
                                    stop_check2 = False
                                    stop_check3 = False
                                    stop_check4 = False
                            if start:
                                step = 0
                                lose_stack = 0
                            if long_stop_w:
                                entry_25.insert(tk.END, ("연속 패 : " + str(lose_stack) + "패 - " + str(
                                    long_stop_value) + "연패시 정지후 패턴 변경\n\n"))
                                entry_25.see(tk.END)
                        if re_start:
                            if pause_step != 0:
                                step = pause_step - 1
                            else:
                                step = stop_step - 1
                                group_level = 1
                            re_start = False

                        if martin_kind == "크루즈3":
                            if step > 4 and win_stack > 0:
                                if t_check == "TIE":
                                    step = step
                                else:
                                    step = 0

                        entry_25.insert(tk.END, (str(step + 1) + "마틴 진행\n"))
                        entry_25.see(tk.END)

                        for i in range(40):
                            if step == i:
                                if selected_index == i + 1:
                                    lose = True
                                    last_tie_step = step
                                    tie_on = True
                                chip_selection(martin_list[i], c_res, step, round, "")
                                if step > 5:
                                    chip_selection(martin_list[i]/5, c_res, step, round, "bonus")
                                compare_mybet = c_res
                                break  # 일치하는 조건을 찾으면 반복문을 종료

                        start = False

                    if ox == "X":

                        if group_level == 2:
                            if group2_get == 0:
                                group2_get = martin9
                            if start:
                                entry_25.insert(tk.END, ("2단계 진행 시작\n"))
                                entry_25.see(tk.END)
                                driver2.find_element(By.CSS_SELECTOR, '.go-level2').click()

                        if t_check == "TIE":
                            tie_stack += 1
                            if lose:
                                step = last_tie_step
                                last_tie_step = 0
                                lose = False
                                group_level = 1

                            else:
                                if stop_check4:
                                    step += 1
                                    stop_check = False
                                    stop_check2 = False
                                    stop_check3 = False
                                    stop_check4 = False
                                else:
                                    step = step
                                    print("step유지")
                                if martin_kind == "크루즈1" or martin_kind == "크루즈2" or martin_kind == "크루즈3" or martin_kind == "크루즈4" or martin_kind == "크루즈5" or martin_kind == "크루즈3_2" or martin_kind == "크루즈3_3" or martin_kind == "크루즈3_4":
                                    entry_25.insert(tk.END,
                                                    ("연속 승 : " + str(win_stack) + "승 - 2연승시 마틴 1단계로 복귀\n\n"))
                                    entry_25.see(tk.END)
                                if (martin_kind == "일반+크루즈" and step > 3) or (martin_kind == "슈퍼+크루즈" and step > 3):
                                    entry_25.insert(tk.END,
                                                    ("연속 승 : " + str(win_stack) + "승 - 2연승시 마틴 1단계로 복귀\n\n"))
                                    entry_25.see(tk.END)
                                if (martin_kind == "일반+크루즈_2" and step > 4) or (martin_kind == "슈퍼+크루즈_2" and step > 4):
                                    entry_25.insert(tk.END,
                                                    ("연속 승 : " + str(win_stack) + "승 - 2연승시 마틴 1단계로 복귀\n\n"))
                                    entry_25.see(tk.END)

                        else:
                            if start or re_start:
                                win_stack = 0
                            else:
                                if stop_check2:
                                    if stop_check3:

                                        lose_stack = 0
                                    else:
                                        win_stack = 0
                                    stop_check2 = False
                                    stop_check3 = False

                                elif stop_check3:

                                    stop_check3 = False
                                    lose_stack = 0

                                else:
                                    lose_stack = 0
                                    win_stack += 1

                                if martin_kind == "크루즈1" or martin_kind == "크루즈2":
                                    if step < 7:
                                        entry_25.insert(tk.END,
                                                        ("연속 승 : " + str(win_stack) + "승 - 2연승시 마틴 1단계로 복귀\n\n"))
                                        entry_25.see(tk.END)
                                if martin_kind == "크루즈3" or martin_kind == "크루즈4" or martin_kind == "크루즈5":
                                    if win_stack > 0 and step > selected_index - 4:
                                        step = 0
                                    else:
                                        entry_25.insert(tk.END,
                                                        ("연속 승 : " + str(win_stack) + "승 - 2연승시 마틴 1단계로 복귀\n\n"))
                                        entry_25.see(tk.END)
                                if martin_kind == "크루즈3_2" or martin_kind == "크루즈3_3" or martin_kind == "크루즈3_4":
                                    entry_25.insert(tk.END,
                                                    ("연속 승 : " + str(win_stack) + "승 - 2연승시 마틴 1단계로 복귀\n\n"))
                                    entry_25.see(tk.END)
                                if martin_kind == "일반+크루즈" or martin_kind == "슈퍼+크루즈":
                                    if step > 3:
                                        entry_25.insert(tk.END,
                                                        ("연속 승 : " + str(win_stack) + "승 - 2연승시 마틴 1단계로 복귀\n\n"))
                                        entry_25.see(tk.END)
                                if martin_kind == "일반+크루즈_2" or martin_kind == "슈퍼+크루즈_2":
                                    if step > 4:
                                        entry_25.insert(tk.END,
                                                        ("연속 승 : " + str(win_stack) + "승 - 2연승시 마틴 1단계로 복귀\n\n"))
                                        entry_25.see(tk.END)
                            if lose:
                                if t_check == "TIE":
                                    step = last_tie_step
                                else:
                                    step = 0
                                lose = False
                            else:
                                if martin_kind == "크루즈1" or martin_kind == "크루즈2":
                                    if martin_kind == "크루즈1":
                                        step += 1
                                    if martin_kind == "크루즈2" and win_stack == 0:
                                        step += 1
                                    if win_stack > 1 and step < 7:
                                        step = 0
                                    if win_stack == 2:
                                        try:
                                            sound_path = resource_path(os.path.join("assets", "start.mp3"))
                                            playsound.playsound(sound_path, block=False)
                                        except:
                                            print("사운드오류")
                                elif martin_kind == "크루즈3" or martin_kind == "크루즈4" or martin_kind == "크루즈5":
                                    if stop_check:
                                        if stop_check3:
                                            step -= 1
                                        else:
                                            step += 1
                                        stop_check = False
                                        stop_check2 = False
                                        stop_check3 = False
                                        stop_check4 = False
                                    elif stop_check2:
                                        if stop_check3:
                                            step -= 1
                                            stop_check3 = False
                                        else:
                                            step += 1

                                        stop_check = False
                                        stop_check2 = False
                                        stop_check3 = False
                                        stop_check4 = False
                                    else:
                                        if step == 0:
                                            step = 0
                                        else:
                                            step -= 1

                                    if win_stack > 1:
                                        step = 0
                                    if win_stack == 2:
                                        try:
                                            sound_path = resource_path(os.path.join("assets", "start.mp3"))
                                            playsound.playsound(sound_path, block=False)
                                        except:
                                            print("사운드오류")
                                    if win_stack > 0 and step > selected_index - 4:
                                        step = 0
                                elif martin_kind == "크루즈3_2":
                                    if stop_check:
                                        if stop_check3:
                                            if step == 1:
                                                step = 0
                                            elif step == 0:
                                                step = 0
                                            else:
                                                step -= 2
                                        else:
                                            step += 1
                                        stop_check = False
                                        stop_check2 = False
                                        stop_check3 = False
                                        stop_check4 = False
                                    elif stop_check2:
                                        if stop_check3:
                                            if step == 1:
                                                step = 0
                                            elif step == 0:
                                                step = 0
                                            else:
                                                step -= 2
                                            stop_check3 = False
                                        else:
                                            step += 1

                                        stop_check = False
                                        stop_check2 = False
                                        stop_check3 = False
                                        stop_check4 = False
                                    else:
                                        if step == 0:
                                            step = 0
                                        else:
                                            if step == 1:
                                                step = 0
                                            elif step == 0:
                                                step = 0
                                            else:
                                                step -= 2

                                    if win_stack > 1:
                                        step = 0
                                    if win_stack == 2:
                                        try:
                                            sound_path = resource_path(os.path.join("assets", "start.mp3"))
                                            playsound.playsound(sound_path, block=False)
                                        except:
                                            print("사운드오류")
                                elif martin_kind == "크루즈3_3":
                                    if stop_check:
                                        if stop_check3:
                                            if step == 1:
                                                step = 0
                                            elif step == 0:
                                                step = 0
                                            else:
                                                step -= 3
                                            if step < 0:
                                                step = 0
                                        else:
                                            step += 1
                                        stop_check = False
                                        stop_check2 = False
                                        stop_check3 = False
                                        stop_check4 = False
                                    elif stop_check2:
                                        if stop_check3:
                                            if step == 1:
                                                step = 0
                                            elif step == 0:
                                                step = 0
                                            else:
                                                step -= 3
                                            if step < 0:
                                                step = 0
                                            stop_check3 = False
                                        else:
                                            step += 1

                                        stop_check = False
                                        stop_check2 = False
                                        stop_check3 = False
                                        stop_check4 = False
                                    else:
                                        if step == 0:
                                            step = 0
                                        else:
                                            if step == 1:
                                                step = 0
                                            elif step == 0:
                                                step = 0
                                            else:
                                                step -= 3
                                            if step < 0:
                                                step = 0
                                        if step < 0:
                                            step = 0

                                    if win_stack > 1:
                                        step = 0
                                    if win_stack == 2:
                                        try:
                                            sound_path = resource_path(os.path.join("assets", "start.mp3"))
                                            playsound.playsound(sound_path, block=False)
                                        except:
                                            print("사운드오류")
                                elif martin_kind == "크루즈3_4":
                                    if stop_check:
                                        if stop_check3:
                                            if step == 1:
                                                step = 0
                                            elif step < 1:
                                                step = 0
                                            else:
                                                step -= 4
                                            if step < 0:
                                                step = 0
                                        else:
                                            step += 1
                                        stop_check = False
                                        stop_check2 = False
                                        stop_check3 = False
                                        stop_check4 = False
                                    elif stop_check2:
                                        if stop_check3:
                                            if step == 1:
                                                step = 0
                                            elif step == 0:
                                                step = 0
                                            else:
                                                step -= 4
                                            if step < 0:
                                                step = 0
                                            stop_check3 = False
                                        else:
                                            step += 1

                                        stop_check = False
                                        stop_check2 = False
                                        stop_check3 = False
                                        stop_check4 = False
                                    else:
                                        if step == 0:
                                            step = 0
                                        else:
                                            if step == 1:
                                                step = 0
                                            elif step == 0:
                                                step = 0
                                            else:
                                                step -= 4
                                            if step < 0:
                                                step = 0
                                        if step < 0:
                                            step = 0

                                    if win_stack > 1:
                                        step = 0
                                    if win_stack == 2:
                                        try:
                                            sound_path = resource_path(os.path.join("assets", "start.mp3"))
                                            playsound.playsound(sound_path, block=False)
                                        except:
                                            print("사운드오류")
                                elif martin_kind == "일반+크루즈" or martin_kind == "슈퍼+크루즈":
                                    if stop_check:
                                        if stop_check3 and step > 3:
                                            if step == 1:
                                                step = 0
                                            elif step < 1:
                                                step = 0
                                            else:
                                                if step > 3:
                                                    step = 3
                                                elif step < 4:
                                                    step = 0
                                            if step < 0:
                                                step = 0
                                        else:
                                            step += 1
                                        stop_check = False
                                        stop_check2 = False
                                        stop_check3 = False
                                        stop_check4 = False
                                    elif stop_check2:
                                        if stop_check3 and step > 3:
                                            if step == 1:
                                                step = 0
                                            elif step == 0:
                                                step = 0
                                            else:
                                                if step > 3:
                                                    step = 3
                                                elif step < 4:
                                                    step = 0
                                            if step < 0:
                                                step = 0
                                            stop_check3 = False
                                        else:
                                            step += 1

                                        stop_check = False
                                        stop_check2 = False
                                        stop_check3 = False
                                        stop_check4 = False
                                    else:
                                        if step == 0:
                                            step = 0
                                        else:
                                            if step == 1:
                                                step = 0
                                            elif step == 0:
                                                step = 0
                                            else:
                                                if step > 3:
                                                    step = 3
                                                elif step < 4:
                                                    step = 0
                                            if step < 0:
                                                step = 0
                                        if step < 0:
                                            step = 0

                                    if step > 3:
                                        if win_stack > 1:
                                            step = 0
                                        if win_stack == 2:
                                            try:
                                                sound_path = resource_path(os.path.join("assets", "start.mp3"))
                                                playsound.playsound(sound_path, block=False)
                                            except:
                                                print("사운드오류")
                                elif martin_kind == "일반+크루즈_2" or martin_kind == "슈퍼+크루즈_2":
                                    if stop_check:
                                        if stop_check3 and step > 4:
                                            if step == 1:
                                                step = 0
                                            elif step < 1:
                                                step = 0
                                            else:
                                                if step > 4:
                                                    step = 4
                                                elif step < 5:
                                                    step = 0
                                            if step < 0:
                                                step = 0
                                        else:
                                            step += 1
                                        stop_check = False
                                        stop_check2 = False
                                        stop_check3 = False
                                        stop_check4 = False
                                    elif stop_check2:
                                        if stop_check3 and step > 4:
                                            if step == 1:
                                                step = 0
                                            elif step == 0:
                                                step = 0
                                            else:
                                                if step > 4:
                                                    step = 4
                                                elif step < 5:
                                                    step = 0
                                            if step < 0:
                                                step = 0
                                            stop_check3 = False
                                        else:
                                            step += 1

                                        stop_check = False
                                        stop_check2 = False
                                        stop_check3 = False
                                        stop_check4 = False
                                    else:
                                        if step == 0:
                                            step = 0
                                        else:
                                            if step == 1:
                                                step = 0
                                            elif step == 0:
                                                step = 0
                                            else:
                                                if step > 4:
                                                    step = 4
                                                elif step < 5:
                                                    step = 0
                                            if step < 0:
                                                step = 0
                                        if step < 0:
                                            step = 0

                                    if step > 4:
                                        if win_stack > 1:
                                            step = 0
                                        if win_stack == 2:
                                            try:
                                                sound_path = resource_path(os.path.join("assets", "start.mp3"))
                                                playsound.playsound(sound_path, block=False)
                                            except:
                                                print("사운드오류")
                                else:
                                    if martin_kind == "크루즈1" or martin_kind == "크루즈2":
                                        if win_stack > 1:
                                            step = 0
                                        else:
                                            step += 1
                                    elif martin_kind == "다니엘시스템":
                                        if stop_check:
                                            step += 1
                                            stop_check = False
                                            stop_check2 = False
                                            stop_check3 = False
                                            stop_check4 = False
                                        else:
                                            if step == 0:
                                                step = 0
                                            else:
                                                if step > 12:
                                                    step -= 2
                                                else:
                                                    step -= 1
                                            if step < 0:
                                                step = 0
                                    else:
                                        if stop_check:
                                            step += 1
                                            stop_check = False
                                        else:
                                            step = 0
                            if start:
                                step = 0
                                lose_stack = 0
                            if stop_check3:
                                step = step
                                stop_check3 = False
                                lose_stack = 0
                        if re_start:
                            if pause_step != 0:
                                step = pause_step - 1
                            else:
                                step = stop_step - 1
                                group_level = 1
                            re_start = False

                        if stop_check3 and t_check == "TIE":
                            stop_check3 = False
                            pass
                        else:
                            entry_25.insert(tk.END, (str(step + 1) + "마틴 진행\n"))
                            entry_25.see(tk.END)

                            for i in range(40):
                                if step == i:
                                    if selected_index == i + 1:
                                        lose = True
                                        last_tie_step = step
                                        tie_on = True
                                    chip_selection(martin_list[i], c_res, step, round, "")
                                    if step > 5:
                                        chip_selection(martin_list[i] / 5, c_res, step, round, "bonus")
                                    compare_mybet = c_res
                                    break  # 일치하는 조건을 찾으면 반복문을 종료

                        start = False

                        group2_get = 0

            if tie_stack > 0:
                tie_step = 0
                tie_stack = 0
            if tie_auto_value:
                entry_25.insert(tk.END, ("타이 승 : " + str(tie_stack) + "\n타이 " + str(tie_step + 1) + "마틴 진행\n"))
                entry_25.see(tk.END)
                chip_selection(tie_values[tie_step], "T", step, round, "")
                compare_mybet = c_res
                tie_step += 1

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
    global current_price, previous_win, previous_lose

    while True:
        try:
            current_price = driver.find_element(By.CSS_SELECTOR, '.amount--bb99f span').get_attribute(
                'innerText').strip()

            price_number = re.sub(r'[^0-9.]', '', current_price)
            cal = int(float(price_number)) - int(float(price_number2))
            positive_cal = cal * -1

            entry_1.config(state='normal')
            entry_2.config(state='normal')
            entry_2.delete(0, tkinter.END)
            entry_2.insert(0, price_number)
            entry_1.delete(0, tkinter.END)
            entry_1.insert(0, cal)
            entry_1.config(state='readonly')
            entry_2.config(state='readonly')
        except NoSuchElementException:
            # 요소가 발견되지 않으면 계속 반복
            pass

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
                        if not stop_check and not stop_check3 and s_bet:
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
                                            recode_log('TIE', start_price, current_price, 0, d_title, r_title, "", "",
                                                       round, cal)
                                        else:
                                            entry_25.insert(tk.END, (
                                                "=================================\n승리\n=================================\n\n"))
                                            entry_25.see(tk.END)
                                            recode_log('WIN', start_price, current_price, 0, d_title, r_title, "", "",
                                                       round, cal)
                                            previous_win = True
                                            previous_lose = False

                                    elif check_ox == "X":
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
                                            recode_log('LOSE', start_price, current_price, 0, d_title, r_title, "", "",
                                                       round, cal)
                                            previous_win = False
                                            previous_lose = True
                                elif check_type == "X":
                                    if check_ox == "O":
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
                                            recode_log('LOSE', start_price, current_price, 0, d_title, r_title, "", "",
                                                       round, cal)
                                            previous_win = False
                                            previous_lose = True
                                    elif check_ox == "X":
                                        if tie_check == "TIE":
                                            entry_25.insert(tk.END, (
                                                "================================\n타이\n================================\n\n"))
                                            entry_25.see(tk.END)
                                            recode_log('TIE', start_price, current_price, 0, d_title, r_title, "", "",
                                                       round, cal)
                                        else:
                                            entry_25.insert(tk.END, (
                                                "=================================\n승리\n=================================\n\n"))
                                            entry_25.see(tk.END)
                                            recode_log('WIN', start_price, current_price, 0, d_title, r_title, "", "",
                                                       round, cal)
                                            previous_win = True
                                            previous_lose = False

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
    recode_log('OPEN_ROOM', start_price, start_price, 0, d_title, r_title, "", "", "", cal)

    element = arg2
    elem2 = element.find_element(By.TAG_NAME, 'svg')
    elem3 = elem2.find_element(By.TAG_NAME, 'svg')
    elem4 = elem3.find_element(By.TAG_NAME, 'svg')
    elem5 = elem4.find_element(By.TAG_NAME, 'svg')
    elem6 = elem5.find_element(By.TAG_NAME, 'svg')
    elem7 = elem6.find_elements(By.TAG_NAME, 'svg')
    finish_check = driver.find_element(By.CLASS_NAME, 'svg--47a93')

    update_completed = False

    while True:

        # 업데이트가 완료된 경우 루프 중지
        if update_completed:
            break

        try:
            # 현재 페이지의 제목 가져오기
            current_title = driver2.title

            # 이전 페이지 제목과 현재 페이지 제목이 다를 경우 출력
            if current_title == "더블X패턴":

                for e in elem7:
                    try:
                        e.is_displayed()
                        text_to_input = e.get_attribute('name')

                        if text_to_input is None:
                            pass
                        else:
                            previous_title = ""
                            p_button = driver2.find_element(By.CSS_SELECTOR, ".pattern_group2 .ct-p")
                            b_button = driver2.find_element(By.CSS_SELECTOR, ".pattern_group2 .ct-b")
                            t_button = driver2.find_element(By.CSS_SELECTOR, ".pattern_group2 .ct-t")
                            if "Tie" in text_to_input:
                                text_to_input = text_to_input
                            else:
                                text_to_input = text_to_input[:6]
                            if text_to_input == "Player":
                                p_button.click()
                            elif text_to_input == "Banker":
                                b_button.click()
                            elif "Banker Tie" in text_to_input:
                                b_button.click()
                                t_button.click()
                            elif "Player Tie" in text_to_input:
                                p_button.click()
                                t_button.click()
                            elif text_to_input == "Banker TiePlayer":
                                b_button.click()
                                t_button.click()

                    except StaleElementReferenceException:
                        print("요소가 사라졌습니다. 다른 작업을 수행합니다.1")
                        break

                    except IndexError:
                        pass
                    except Exception as ex:
                        print(f"오류 발생: {ex}")
                        break
                update_completed = True
            else:
                time.sleep(1)

        except StaleElementReferenceException:
            print("요소가 사라졌습니다. 다른 작업을 수행합니다.")
            break

        except KeyboardInterrupt:
            # 사용자가 Ctrl+C를 누르면 루프 종료
            break
        except Exception as e:
            print(f"오류 발생: {e}")
            break


def findurl(driver, driver2):
    last_opened_window_handle = None
    last_checked_url = ""
    room_search = True

    global docrawl, d_title, r_title, start

    d_title = driver.title
    entry_25.insert(tk.END, "\n%s사이트 접속\n\n" % d_title)
    entry_25.see(tk.END)

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
        driver2.get("http://pattern2024.com/bbs/login.php?agency=pt5")
        try:
            # 요소가 나타날 때까지 최대 10초 동안 기다립니다.
            id_input = WebDriverWait(driver2, 20).until(
                EC.presence_of_element_located((By.ID, "login_id"))
            )

            password_input = driver2.find_element(By.ID, "login_pw")
            submit_button = driver2.find_element(By.CLASS_NAME, "btn_submit")
            login_id = serial_number.lower()
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
        global width, height, driver
        print(monitors)

        width = 1820
        height = 1100
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
        driver.set_window_size(width, height)
        driver.set_window_position(0, 0)
        driver2.set_window_size(width, height)
        driver2.set_window_position(0, height)

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


def on_martin_select(event):
    global selected_value2
    global selected_index

    selected_value2 = entry_7.get()
    selected_num = re.sub(r'[^0-9]', '', selected_value2)
    try:
        selected_index = int(selected_num)
    except:
        print("int아님")
    # 모든 Entry의 상태를 먼저 readonly로 설정
    for entry in martin_entries:
        entry.state(['readonly'])

    # 선택된 값에 따라 해당하는 Entry들을 editable로 설정
    for i in range(selected_index):
        entry_10.state(['!readonly'])


def martin_kind_select(event):
    global martin_kind, long_stop_w2

    martin_kind = entry_77.get()

    if martin_kind == "다니엘시스템":
        long_stop_w2 = False
        c3.deselect()


def on_select2(event):
    global stop_step
    selected_step = entry_99.get()
    print(selected_step)
    selected_step_to_int = int(selected_step)
    stop_step = selected_step_to_int


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
        current_price = driver.find_element(By.CSS_SELECTOR, '.amount--bb99f span').get_attribute('innerText').strip()
        price_number = re.sub(r'[^0-9.]', '', current_price)
        cal = int(float(price_number)) - int(float(price_number2))
    except:
        print("오류")
    recode_log('END', start_price, current_price, 0, d_title, r_title, "", "", round, cal)

    if messagebox.askokcancel("종료", "종료하시겠습니까?"):
        martin_set_zero()
        stop_event.set()
        win.quit()
        win.destroy()


def calculate_amount(base_amount, stage):
    amount = base_amount
    for i in range(2, stage + 2):
        amount = amount * 2 + base_amount
    return amount


def set1_click(value):
    value = int(value)
    if martin_kind == "크루즈1":
        base_bet = [1, 1, 2, 3, 4, 6, 8, 11, 15, 20, 30, 40, 60, 80, 120, 160, 240, 320, 480, 640, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    elif martin_kind == "일반마틴":
        base_bet = [2 ** i for i in range(40)]
    elif martin_kind == "슈퍼마틴":
        base_bet = [1]
        for i in range(1, 40):
            next_value = base_bet[-1] * 2 + 1
            base_bet.append(next_value)
    elif martin_kind == "다니엘시스템":
        base_bet = list(range(1, 41))

    elif martin_kind == "크루즈2":
        base_bet = [1, 1, 2, 3, 4, 6, 9, 14, 21, 31, 47, 70, 105, 158, 237, 355, 533, 799, 1199, 1798, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    elif martin_kind == "크루즈3":
        base_bet = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765, 1, 1, 1, 1,
                    1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    elif martin_kind == "크루즈3_2":
        base_bet = [1, 1, 2, 4, 7, 12, 21, 37, 65, 114, 200, 351, 616, 1081, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    elif martin_kind == "크루즈3_3":
        base_bet = [1, 1, 2, 4, 8, 15, 28, 52, 97, 181, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    elif martin_kind == "크루즈3_4":
        base_bet = [1, 1, 2, 4, 8, 16, 31, 60, 116, 224, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    elif martin_kind == "크루즈4":
        base_bet = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765, 1, 1, 1, 1, 1,
                    1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    elif martin_kind == "크루즈5":
        base_bet = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765, 1, 1, 1, 1, 1,
                    1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    elif martin_kind == "일반+크루즈":
        base_bet = [1, 2, 4, 8, 8, 16, 24, 40, 64, 104, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765, 1, 1, 1, 1, 1,
                    1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    elif martin_kind == "일반+크루즈_2":
        base_bet = [1, 2, 4, 8, 16, 16, 32, 48, 80, 128, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765, 1, 1, 1, 1, 1,
                    1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    elif martin_kind == "슈퍼+크루즈":
        base_bet = [1, 3, 7, 15, 12, 24, 39, 63, 102, 165, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765, 1, 1, 1, 1, 1,
                    1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    elif martin_kind == "슈퍼+크루즈_2":
        base_bet = [1, 3, 7, 15, 31, 27, 54, 85, 139, 224, 363, 587, 950, 1537, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

    print(martin_kind)

    multiply = value / base_bet[0]
    sum_price = 0
    for j in range(39):
        martin_entries[j].state(['!readonly'])
        martin_entries[j].delete(0, tkinter.END)
    for i in range(selected_index - 1):
        martin_entries[i].state(['!readonly'])
        martin_entries[i].delete(0, tkinter.END)
        martin_entries[i].insert(tk.END, int(base_bet[i + 1]) * int(multiply))
        sum_price += int(base_bet[i + 1]) * int(multiply)
    sum_price += value
    entry_25.insert(tk.END, "합계금액 총 : " + str(format(sum_price, ',')) + "\n\n")
    entry_25.see(tk.END)
    # entry_4.delete(0, tkinter.END)
    # entry_5.delete(0, tkinter.END)
    # entry_5.insert(tk.END, value * 25)
    # entry_4.insert(tk.END, value * 25)


def set3_click(value):
    global tie_values
    base_bet = [1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 22, 25, 29, 33, 38,
                43, 49, 56, 65, 74, 84, 97, 110, 126]
    value = int(value)
    multiply = value / base_bet[0]

    tie_values = [base_bet[i] * multiply for i in range(40)]

    total_sum_tie = int(sum(tie_values))

    entry_25.insert(tk.END, "타이 합계금액 총 : " + str(format(total_sum_tie, ',')) + "\n\n")
    entry_25.see(tk.END)


def set4_click(value):
    global long_stop_value
    value = int(value)
    long_stop_value = value


def set5_click(value):
    global long_stop_value2
    value = int(value)
    long_stop_value2 = value


def tie_auto():
    global tie_auto_value
    print(CheckVar1.get())

    if CheckVar1.get() == 0:
        tie_auto_value = False
        entry_230.state(['readonly'])
    elif CheckVar1.get() == 1:
        tie_auto_value = True
        entry_230.state(['!readonly'])


def long_stop():
    global long_stop_w
    if CheckVar2.get() == 0:
        long_stop_w = False
        entry_999.state(['readonly'])
        entry_25.insert(tk.END,
                        ("=================================\n\n연패방지기능 OFF\n\n=================================\n\n"))
        entry_25.see(tk.END)
    elif CheckVar2.get() == 1:
        if CheckVar3.get() == 0:
            entry_25.insert(tk.END,
                            ("=================================\n\n연패방지 단독사용불가\n장줄정지과 같이 사용하세요.\n\n=================================\n\n"))
            entry_25.see(tk.END)
            c2.deselect()
            long_stop_w = False
        else:
            long_stop_w = True
            entry_999.state(['!readonly'])
            entry_25.insert(tk.END,
                            ("=================================\n\n연패방지기능 ON\n\n=================================\n\n"))
            entry_25.see(tk.END)



def long_stop2():
    global long_stop_w2, long_stop_w
    if CheckVar3.get() == 0:
        long_stop_w2 = False
        entry_9999.state(['readonly'])
        entry_25.insert(tk.END,
                        ("=================================\n\n장줄정지기능 OFF\n\n=================================\n\n"))
        entry_25.see(tk.END)
        c2.deselect()
        long_stop_w = False
    elif CheckVar3.get() == 1:
        long_stop_w2 = True
        entry_9999.state(['!readonly'])
        entry_25.insert(tk.END,
                        ("=================================\n\n장줄정지기능 ON\n\n=================================\n\n"))
        entry_25.see(tk.END)


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

    if data['serial'] == serial_number and data['status']  == 1:
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

if __name__ == "__main__":
    start_socketio_thread()
    if not serial_number == "MASTER":
        create_login_window()
    martin_set_zero()
    recode_log('OPEN', 0, 0, 0, "", "", "", "", "", cal)
    win = tk.Tk()
    win.geometry("1060x500")
    win.configure(bg="#FFFFFF")
    win.title("PATTERN AUTO")
    win.attributes("-topmost", True)
    win.tk.call('tk', 'scaling', 1.0)

    text_font = ('Courier New', '8')
    text_font2 = ('Inter Black', '12')


    canvas = Canvas(
        win,
        bg="#FFFFFF",
        height=500,
        width=1060,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )

    canvas.place(x=0, y=0)

    image_image_1 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "image_1.png"))
    )

    image_1 = canvas.create_image(
        507.0,
        492.0,
        image=image_image_1
    )

    image_image_2 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "image_2.png"))
    )
    image_2 = canvas.create_image(
        530,
        250,
        image=image_image_2
    )

    entry_image_1 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "entry_1.png"))
    )
    entry_bg_1 = canvas.create_image(
        490.0,
        61.0,
        image=entry_image_1
    )
    entry_1 = Entry(
        bd=0,
        bg="#FFFFFF",
        fg="#000716",
        highlightthickness=0,
        font=text_font
    )
    entry_1.place(
        x=445.0,
        y=51.0,
        width=90.0,
        height=18.0
    )

    canvas.create_text(
        465.0,
        30.0,
        anchor="nw",
        text="총 수익",
        fill="#FFFFFF",
        font=("Inter Black", 15 * -1)
    )

    image_image_3 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "image_3.png"))
    )
    image_3 = canvas.create_image(
        490.0,
        52.0,
        image=image_image_3
    )

    entry_image_2 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "entry_2.png"))
    )
    entry_bg_2 = canvas.create_image(
        295.0,
        62.5,
        image=entry_image_2
    )
    entry_2 = Entry(
        bd=0,
        bg="#FFFFFF",
        fg="#000716",
        highlightthickness=0,
        font=text_font
    )
    entry_2.place(
        x=250.0,
        y=52.0,
        width=90.0,
        height=19.0
    )

    canvas.create_text(
        265.0,
        31.0,
        anchor="nw",
        text="현재금액",
        fill="#FFFFFF",
        font=("Inter Black", 15 * -1)
    )

    image_image_4 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "image_4.png"))
    )
    image_4 = canvas.create_image(
        294.0,
        53.0,
        image=image_image_4
    )

    entry_image_3 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "entry_3.png"))
    )
    entry_bg_3 = canvas.create_image(
        97.5,
        63.5,
        image=entry_image_3
    )
    entry_3 = Entry(
        bd=0,
        bg="#FFFFFF",
        fg="#000716",
        highlightthickness=0,
        font=text_font
    )
    entry_3.place(
        x=53.0,
        y=53.0,
        width=89.0,
        height=19.0
    )
    entry_1.config(state='readonly')
    entry_2.config(state='readonly')
    entry_3.config(state='readonly')

    canvas.create_text(
        68.0,
        32.0,
        anchor="nw",
        text="시작금액",
        fill="#FFFFFF",
        font=("Inter Black", 15 * -1)
    )

    image_image_5 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "image_5.png"))
    )
    image_5 = canvas.create_image(
        99.0,
        53.0,
        image=image_image_5
    )

    entry_image_4 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "entry_4.png"))
    )
    entry_bg_4 = canvas.create_image(
        490.0,
        139.5,
        image=entry_image_4
    )
    entry_4 = Entry(
        bd=0,
        bg="#FFFFFF",
        fg="#000716",
        highlightthickness=0,
        font=text_font2
    )
    entry_4.place(
        x=445.0,
        y=129.0,
        width=90.0,
        height=19.0
    )

    canvas.create_text(
        441.0,
        110.0,
        anchor="nw",
        text="손실시종료금액",
        fill="#FFFFFF",
        font=("Inter Black", 15 * -1)
    )

    image_image_6 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "image_6.png"))
    )
    image_6 = canvas.create_image(
        490.0,
        130.0,
        image=image_image_6
    )

    entry_image_5 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "entry_5.png"))
    )
    entry_bg_5 = canvas.create_image(
        295.0,
        140.5,
        image=entry_image_5
    )
    entry_5 = Entry(
        bd=0,
        bg="#FFFFFF",
        fg="#000716",
        highlightthickness=0,
        font=text_font2
    )
    entry_5.place(
        x=250.0,
        y=130.0,
        width=90.0,
        height=19.0
    )

    canvas.create_text(
        245.0,
        110.0,
        anchor="nw",
        text="수익시종료금액",
        fill="#FFFFFF",
        font=("Inter Black", 15 * -1)
    )

    image_image_7 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "image_7.png"))
    )
    image_7 = canvas.create_image(
        294.0,
        131.0,
        image=image_image_7
    )

    canvas.create_text(
        60.0,
        135.0,
        anchor="nw",
        text="단계",
        fill="#FFFFFF",
        font=("Inter Black", 15 * -1)
    )

    set_martin = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18",
                  "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35",
                  "36", "37", "38", "39", "40"]

    entry_99 = ttk.Combobox(
        win,
        values=set_martin,
        font=text_font,
        state='disabled'
    )
    entry_99.place(
        x=95.0,
        y=130.0,
        width=45.0,
        height=25.0
    )
    entry_99.current(0)
    entry_99.bind('<<ComboboxSelected>>', on_select2)

    canvas.create_text(
        55.0,
        110.0,
        anchor="nw",
        text="정지후단계설정",
        fill="#FFFFFF",
        font=("Inter Black", 15 * -1)
    )

    image_image_8 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "image_8.png"))
    )
    image_8 = canvas.create_image(
        99.0,
        131.0,
        image=image_image_8
    )

    image_image_9 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "image_9.png"))
    )
    image_9 = canvas.create_image(
        340.0,
        338.0,
        image=image_image_9
    )

    image_image_10 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "image_10.png"))
    )
    image_10 = canvas.create_image(
        340.0,
        338.0,
        image=image_image_10
    )

    canvas.create_text(
        78.0,
        205.0,
        anchor="nw",
        text="마  틴",
        fill="#000000",
        font=("Inter Black", 23 * -1)
    )

    martin_level = [str(i) + "마틴" for i in range(1, 41)]
    martin_level.insert(0, "마틴단계설정")
    text_font3 = ('Arial', '12')

    win.option_add('*TCombobox*Listbox.font', text_font3)
    entry_7 = ttk.Combobox(
        win,
        value=martin_level,
        font=text_font3
    )
    entry_7.place(
        x=87.0,
        y=242.0,
        width=92.0,
        height=18.0,
    )
    entry_7.current(0)
    entry_7.bind('<<ComboboxSelected>>', on_martin_select)

    canvas.create_text(
        35.0,
        243.0,
        anchor="nw",
        text="마틴단계",
        fill="#000000",
        font=("Inter Black", 12 * -1)
    )

    martin_kind = ["크루즈1", "크루즈2", "크루즈3","크루즈3_2","크루즈3_3","크루즈3_4","크루즈4", "크루즈5", "일반마틴", "슈퍼마틴", "다니엘시스템", "일반+크루즈", "일반+크루즈_2", "슈퍼+크루즈", "슈퍼+크루즈_2"]
    martin_kind.insert(0, "마틴방식설정")
    entry_77 = ttk.Combobox(
        win,
        value=martin_kind,
        font=text_font3
    )
    entry_77.place(
        x=87.0,
        y=267.0,
        width=92.0,
        height=18.0,
    )
    entry_77.current(0)
    entry_77.bind('<<ComboboxSelected>>', martin_kind_select)

    canvas.create_text(
        35.0,
        268.0,
        anchor="nw",
        text="마틴방식",
        fill="#000000",
        font=("Inter Black", 12 * -1)
    )

    canvas.create_text(
        205.0,
        215.0,
        anchor="nw",
        text="베이스",
        fill="#F8DF00",
        font=("Inter Medium", 12 * -1)
    )

    entry_10 = ttk.Entry(
        win,
        state="readonly",
        font=text_font2
    )
    entry_10.place(
        x=240.5,
        y=215.0,
        width=43.0,
        height=17.0
    )
    button_1 = tk.Button(
        win,
        text="입력",
        command=lambda: set1_click(entry_10.get()),
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
        x=290.0,
        y=215.0,
        width=35.0,
        height=20.0
    )

    canvas.create_text(
        210.0,
        240.0,
        anchor="nw",
        text="2nd",
        fill="#F8DF00",
        font=("Inter Medium", 12 * -1)
    )

    entry_11 = ttk.Entry(
        win,
        state="readonly",
        font=text_font2
    )
    entry_11.place(
        x=240.5,
        y=240.0,
        width=63.0,
        height=17.0
    )

    canvas.create_text(
        210.0,
        265.0,
        anchor="nw",
        text="3th",
        fill="#F8DF00",
        font=("Inter Medium", 12 * -1)
    )

    entry_12 = ttk.Entry(
        win,
        state="readonly",
        font=text_font2
    )
    entry_12.place(
        x=240.5,
        y=265.0,
        width=63.0,
        height=17.0
    )

    canvas.create_text(
        210.0,
        290.0,
        anchor="nw",
        text="4th",
        fill="#F8DF00",
        font=("Inter Medium", 12 * -1)
    )
    entry_13 = ttk.Entry(
        win,
        state="readonly",
        font=text_font2
    )
    entry_13.place(
        x=240.5,
        y=290.0,
        width=63.0,
        height=17.0
    )

    canvas.create_text(
        210.0,
        315.0,
        anchor="nw",
        text="5th",
        fill="#F8DF00",
        font=("Inter Medium", 12 * -1)
    )
    entry_14 = ttk.Entry(
        win,
        state="readonly",
        font=text_font2
    )
    entry_14.place(
        x=240.5,
        y=315.0,
        width=63.0,
        height=17.0
    )

    canvas.create_text(
        210.0,
        340.0,
        anchor="nw",
        text="6th",
        fill="#F8DF00",
        font=("Inter Medium", 12 * -1)
    )
    entry_15 = ttk.Entry(
        win,
        state="readonly",
        font=text_font2
    )
    entry_15.place(
        x=240.5,
        y=340.0,
        width=63.0,
        height=17.0
    )
    entry_16 = ttk.Entry(
        win,
        state="readonly",
        font=text_font2
    )
    entry_16.place(
        x=240.5,
        y=365.0,
        width=63.0,
        height=17.0
    )

    canvas.create_text(
        210.0,
        365.0,
        anchor="nw",
        text="7th",
        fill="#F8DF00",
        font=("Inter Medium", 12 * -1)
    )

    canvas.create_text(
        210.0,
        390.0,
        anchor="nw",
        text="8th",
        fill="#F8DF00",
        font=("Inter Medium", 12 * -1)
    )
    entry_17 = ttk.Entry(
        win,
        state="readonly",
        font=text_font2
    )
    entry_17.place(
        x=240.5,
        y=390.0,
        width=63.0,
        height=17.0
    )

    canvas.create_text(
        210.0,
        415.0,
        anchor="nw",
        text="9th",
        fill="#F8DF00",
        font=("Inter Medium", 12 * -1)
    )
    entry_18 = ttk.Entry(
        win,
        state="readonly",
        font=text_font2
    )
    entry_18.place(
        x=240.5,
        y=415.0,
        width=63.0,
        height=17.0
    )

    canvas.create_text(
        210.0,
        440.0,
        anchor="nw",
        text="10th",
        fill="#F8DF00",
        font=("Inter Medium", 12 * -1)
    )
    entry_19 = ttk.Entry(
        win,
        state="readonly",
        font=text_font2
    )
    entry_19.place(
        x=240.5,
        y=440.0,
        width=63.0,
        height=17.0
    )

    canvas.create_text(
        330.0,
        215.0,
        anchor="nw",
        text="11th",
        fill="#F8DF00",
        font=("Inter Medium", 12 * -1)
    )
    entry_20 = ttk.Entry(
        win,
        state="readonly",
        font=text_font2
    )
    entry_20.place(
        x=360.5,
        y=215.0,
        width=63.0,
        height=17.0
    )

    canvas.create_text(
        330.0,
        240.0,
        anchor="nw",
        text="12th",
        fill="#F8DF00",
        font=("Inter Medium", 12 * -1)
    )
    entry_21 = ttk.Entry(
        win,
        state="readonly",
        font=text_font2
    )
    entry_21.place(
        x=360.5,
        y=240.0,
        width=63.0,
        height=17.0
    )

    canvas.create_text(
        330.0,
        265.0,
        anchor="nw",
        text="13th",
        fill="#F8DF00",
        font=("Inter Medium", 12 * -1)
    )
    entry_22 = ttk.Entry(
        win,
        state="readonly",
        font=text_font2
    )
    entry_22.place(
        x=360.5,
        y=265.0,
        width=62.0,
        height=18.0
    )
    canvas.create_text(
        330.0,
        290.0,
        anchor="nw",
        text="14th",
        fill="#F8DF00",
        font=("Inter Medium", 12 * -1)
    )
    canvas.create_text(
        330.0,
        315.0,
        anchor="nw",
        text="15th",
        fill="#F8DF00",
        font=("Inter Medium", 12 * -1)
    )
    entry_23 = ttk.Entry(
        win,
        state="readonly",
        font=text_font2
    )
    entry_23.place(
        x=360.5,
        y=290.0,
        width=63.0,
        height=17.0
    )
    entry_224 = ttk.Entry(
        win,
        state="readonly",
        font=text_font2
    )
    entry_224.place(
        x=360.5,
        y=315.0,
        width=63.0,
        height=17.0
    )
    canvas.create_text(
        330.0,
        340.0,
        anchor="nw",
        text="16th",
        fill="#F8DF00",
        font=("Inter Medium", 12 * -1)
    )
    entry_225 = ttk.Entry(
        win,
        state="readonly",
        font=text_font2
    )
    entry_225.place(
        x=360.5,
        y=340.0,
        width=63.0,
        height=17.0
    )
    canvas.create_text(
        330.0,
        365.0,
        anchor="nw",
        text="17th",
        fill="#F8DF00",
        font=("Inter Medium", 12 * -1)
    )
    entry_226 = ttk.Entry(
        win,
        state="readonly",
        font=text_font2
    )
    entry_226.place(
        x=360.5,
        y=365.0,
        width=63.0,
        height=17.0
    )
    canvas.create_text(
        330.0,
        390.0,
        anchor="nw",
        text="18th",
        fill="#F8DF00",
        font=("Inter Medium", 12 * -1)
    )
    entry_227 = ttk.Entry(
        win,
        state="readonly",
        font=text_font2
    )
    entry_227.place(
        x=360.5,
        y=390.0,
        width=63.0,
        height=17.0
    )
    canvas.create_text(
        330.0,
        415.0,
        anchor="nw",
        text="19th",
        fill="#F8DF00",
        font=("Inter Medium", 12 * -1)
    )
    entry_228 = ttk.Entry(
        win,
        state="readonly",
        font=text_font2
    )
    entry_228.place(
        x=360.5,
        y=415.0,
        width=63.0,
        height=17.0
    )
    canvas.create_text(
        330.0,
        440.0,
        anchor="nw",
        text="20th",
        fill="#F8DF00",
        font=("Inter Medium", 12 * -1)
    )
    entry_229 = ttk.Entry(
        win,
        state="readonly",
        font=text_font2
    )
    entry_229.place(
        x=360.5,
        y=440.0,
        width=63.0,
        height=17.0
    )

    canvas.create_text(
        45.0,
        395.0,
        anchor="nw",
        text="타이오토",
        fill="#000000",
        font=("Inter Medium", 15 * -1)
    )

    CheckVar1 = IntVar()

    c1 = tk.Checkbutton(win, text="사용", variable=CheckVar1, command=tie_auto)
    c1.config(bg="#FFFFFF", fg="#000000", font=text_font2,
              selectcolor="WHITE")
    c1.place(
        x=115.5,
        y=390.0
    )

    canvas.create_text(
        45.0,
        420.0,
        anchor="nw",
        text="베이스",
        fill="#000000",
        font=("Inter Medium", 12 * -1)
    )
    entry_230 = ttk.Entry(
        win,
        state="readonly",
        font=text_font2
    )
    entry_230.place(
        x=85.0,
        y=418.0,
        width=53.0,
        height=18.0
    )
    button_3 = tk.Button(
        win,
        text="입력",
        command=lambda: set3_click(entry_230.get()),
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

    button_3.pack()
    button_3.place(
        x=145.0,
        y=418.0,
        width=35.0,
        height=20.0
    )

    canvas.create_text(
        45.0,
        440.0,
        anchor="nw",
        text="타이단계리셋",
        fill="#000000",
        font=("Inter Medium", 12 * -1)
    )

    button_4 = tk.Button(
        win,
        text="리셋",
        command=tie_reset,
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

    button_4.pack()
    button_4.place(
        x=145.0,
        y=440.0,
        width=35.0,
        height=20.0
    )
    for i in range(21, 31):
        y_position = 215 + (i - 21) * 25  # y 위치 계산
        ordinal_suffix = "th"
        if i == 21:
            ordinal_suffix = "st"
        elif i == 22:
            ordinal_suffix = "nd"
        elif i == 23:
            ordinal_suffix = "rd"
        canvas.create_text(
            435.0,
            y_position,
            anchor="nw",
            text=f"{i}{ordinal_suffix}",
            fill="#F8DF00",
            font=("Inter Medium", 12 * -1)
        )
        entry_name = f"entry_{231 + (i - 21)}"
        entry = ttk.Entry(
            win,
            state="readonly",
            font=text_font2
        )
        entry.place(
            x=465.0,
            y=y_position,
            width=63.0,
            height=17.0
        )
        locals()[entry_name] = entry
    for j in range(31, 41):
        y_position = 215 + (j - 31) * 25  # y 위치 계산
        ordinal_suffix = "th"
        canvas.create_text(
            535.0,
            y_position,
            anchor="nw",
            text=f"{j}{ordinal_suffix}",
            fill="#F8DF00",
            font=("Inter Medium", 12 * -1)
        )
        entry_name = f"entry_{231 + (j - 21)}"
        entry = ttk.Entry(
            win,
            state="readonly",
            font=text_font2
        )
        entry.place(
            x=565.0,
            y=y_position,
            width=63.0,
            height=17.0
        )
        locals()[entry_name] = entry

    martin_entries = [entry_11, entry_12, entry_13, entry_14, entry_15, entry_16, entry_17, entry_18, entry_19,
                      entry_20, entry_21, entry_22, entry_23, entry_224, entry_225, entry_226, entry_227, entry_228,
                      entry_229, entry_231, entry_232, entry_233, entry_234, entry_235, entry_236, entry_237,
                      entry_238, entry_239, entry_240, entry_241, entry_242, entry_243, entry_244, entry_245, entry_246,
                      entry_247, entry_248, entry_249, entry_250]

    canvas.create_text(
        684.0,
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
        843.5,
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
        x=700.0,
        y=55.0,
        width=297.0,
        height=30.0
    )

    images_info = {}

    image_image_11 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "image_11.png"))
    )
    x1, y1 = 720, 125
    images_info['image1'] = (x1, y1, image_image_11.width(), image_image_11.height())
    image_11 = canvas.create_image(
        x1,
        y1,
        image=image_image_11
    )

    image_image_12 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "image_12.png"))
    )
    x2, y2 = 801, 125
    images_info['image2'] = (x2, y2, image_image_12.width(), image_image_12.height())
    image_12 = canvas.create_image(
        x2,
        y2,
        image=image_image_12
    )

    image_image_13 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "image_13.png"))
    )
    x3, y3 = 963, 125
    images_info['image3'] = (x3, y3, image_image_13.width(), image_image_13.height())
    image_13 = canvas.create_image(
        x3,
        y3,
        image=image_image_13
    )

    image_image_14 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "image_14.png"))
    )
    x4, y4 = 882, 125
    images_info['image4'] = (x4, y4, image_image_14.width(), image_image_14.height())
    image_14 = canvas.create_image(
        x4,
        y4,
        image=image_image_14
    )

    canvas.bind("<Button-1>", on_canvas_click)

    entry_image_25 = PhotoImage(
        file=resource_path(os.path.join("assets/frame0", "entry_29.png"))
    )
    entry_bg_25 = canvas.create_image(
        853.0,
        353.0,
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
        x=695.0,
        y=228.0,
        width=320.0,
        height=250.0
    )
    entry_25.configure(font=my_font)

    canvas.create_text(
        690.0,
        170.0,
        anchor="nw",
        text="로그정보",
        fill="#FFFFFF",
        font=("Roboto Bold", 18 * -1)
    )
    canvas.create_text(
        1000.0,
        10.0,
        anchor="nw",
        text=serial_number,
        fill="#FFFFFF",
        font=("Roboto Bold", 12 * -1)
    )
    canvas.create_text(
        820.0,
        180.0,
        anchor="nw",
        text="연패방지",
        fill="#FFFFFF",
        font=("Inter Medium", 15 * -1)
    )

    CheckVar2 = IntVar()

    c2 = tk.Checkbutton(win, text="설정값", variable=CheckVar2, command=long_stop)
    c2.config(bg="#026832", fg="#F8DF00", font=text_font3,
              selectcolor="black")
    c2.select()
    c2.place(
        x=890.5,
        y=176.0
    )

    entry_999 = ttk.Entry(
        win,
        font=text_font3
    )
    entry_999.place(
        x=950.5,
        y=178.0,
        width=30.0,
        height=20.0
    )
    entry_999.insert(tk.END, "3")
    button_4 = tk.Button(
        win,
        text="입력",
        command=lambda: set4_click(entry_999.get()),
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

    button_4.pack()
    button_4.place(
        x=987.5,
        y=178.0,
        width=35.0,
        height=20.0
    )

    canvas.create_text(
        820.0,
        157.0,
        anchor="nw",
        text="장줄정지",
        fill="#FFFFFF",
        font=("Inter Medium", 15 * -1)
    )

    CheckVar3 = IntVar()

    c3 = tk.Checkbutton(win, text="설정값", variable=CheckVar3, command=long_stop2)
    c3.config(bg="#026832", fg="#F8DF00", font=text_font3,
              selectcolor="black")
    c3.select()
    c3.place(
        x=890.5,
        y=153.0
    )

    entry_9999 = ttk.Entry(
        win,
        font=text_font3
    )
    entry_9999.place(
        x=950.5,
        y=155.0,
        width=30.0,
        height=20.0
    )
    entry_9999.insert(tk.END, "3")
    button_5 = tk.Button(
        win,
        text="입력",
        command=lambda: set5_click(entry_9999.get()),
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

    button_5.pack()
    button_5.place(
        x=987.5,
        y=155.0,
        width=35.0,
        height=20.0
    )

    info_text = "1,2마틴현재패턴\n3마틴부터 줄따라\n일반+크루즈_2\n6마틴부터 5마틴으로"

    canvas.create_text(
        35.0,
        295.0,
        anchor="nw",
        text="=====================\n%s\n=====================" % info_text.center(10),
        fill="#000000",
        font=("Inter Medium", 12 * -1)
    )

    ab = t.split(",")

    if ab[0] == "0":
        win.protocol("WM_DELETE_WINDOW", on_closing)
        win.mainloop()

    else:
        tkinter.messagebox.showwarning("경고", "사용이 승인되지 않았습니다.")
        on_closing()
