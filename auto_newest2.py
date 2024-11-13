import asyncio
import threading
import tkinter as tk
import tkinter.messagebox
import tkinter.scrolledtext as scrolledtext
from tkinter import *
from tkinter import ttk
from tkinter import messagebox, Toplevel
from tkinter import messagebox, Toplevel
from tkinter.font import Font
from undetected_playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

from playwright_stealth import stealth_sync
from screeninfo import get_monitors
import re
import json
import os
import platform
import shutil
import sys
import requests
import uuid
from pathlib import Path
from ctypes import windll
import traceback

processed_history = {}
# 리소스 경로 함수
def resource_path(relative_path):
    """ 리소스의 절대 경로를 얻기 위한 함수 """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def get_screen_resolution():
    # Get screen resolution taking DPI into account
    user32 = windll.user32
    #user32.SetProcessDPIAware()
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)

    # Get the system DPI scaling factor
    hdc = windll.user32.GetDC(0)
    dpi_scale = windll.gdi32.GetDeviceCaps(hdc, 88) / 96  # LOGPIXELSX is 88
    return int(screen_width), int(screen_height)

# 전역 변수 초기화
serial_number = 'MASTER'
vbet_amount = 0
vbet_data = {}
step_order = []
order = []
vbet_keys = []
selected_index = 0
profit_stop2 = 0
loss_stop2 = 0
cal = 0
price_number2 = 0
start_price = 0
current_price = 0
positive_cal = 0
lose = False
start = True
re_start = False
d_title = ""
r_title = ""
order_index = 0
next_value = 0
sum_price = 0
betting_price = 0
profit_stop_count = 1
tie_step = 0
stop_check = False
bet_type = 4  # 초기 베팅 타입 설정
base_price = 1000  # 초기 베이스 금액
round_num = ""
martin_kind = ""
go_bonus = False
side_bet = True
current_res = ""
betting_on = False
no_bet_count = 0
pause_status = False
pause_status2 = False
player_area = ""
banker_area = ""
autobet_called = False
c_res = ""
c_res2 = None
price_running = False
password = ""

# 로그 기록 함수
async def recode_log(serial, type, start_price, current_price, bet_price, title, room, status, step, round_num, cal):
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
        "round": round_num,
        "benefit": cal
    }
    try:
        requests.post(url, data=datas)
    except Exception as e:
        print(f"로그 전송 오류: {e}")


# 마틴 단계 초기화
async def martin_set_zero():
    url = "https://patternlog.platform-dev.xyz/martin_set_zero.php"
    datas = {
        'serial': serial_number,
    }
    try:
        requests.post(url, data=datas)
    except Exception as e:
        print(f"martin_set_zero 오류: {e}")


# 외부 IP 가져오기
def get_external_ip():
    try:
        response = requests.get('https://httpbin.org/ip')
        ip = response.json()['origin']
        return ip
    except Exception as e:
        print(f"IP 가져오기 오류: {e}")
        return "Unknown"


# MAC 주소 가져오기
def get_mac_address():
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2 * 6, 2)][::-1])
    return mac


# 허용된 사이트 가져오기
async def get_permitted_sites():
    try:
        url = 'http://pattern2024.com/get_sites.php'
        response = requests.get(url)
        data = response.text
        site_data = json.loads(data)
        site_names = [item['site'] for item in site_data]
        return site_names
    except Exception as e:
        print("데이터를 가져오는 중 오류 발생:", e)
        return []

def get_main_monitor_orientation():
    monitors = get_monitors()
    # 주 모니터(첫 번째 모니터) 선택
    main_monitor = monitors[1]
    width = main_monitor.width
    height = main_monitor.height
    orientation = "Landscape" if width > height else "Portrait"
    return orientation, width, height

# Tkinter Application 클래스 정의
class Application(tk.Tk):
    def __init__(self, loop):
        super().__init__()
        self.loop = loop
        self.s_bet = False

        # 가격 업데이트 관련 변수
        self.price_running = True
        self.price_task = None
        self.start_price = None
        self.last_baccarat_time = 0

        self.playwright1 = None
        self.browser1 = None
        self.context1 = None
        self.page1 = None
        self.current_new_page = None
        self.price_updated = False

        self.playwright2 = None
        self.browser2 = None
        self.context2 = None
        self.page2 = None
        self.title("PATTERN AUTO")
        self.geometry("450x690")
        self.resizable(False, False)  # 창 크기 고정
        self.configure(bg="#FFFFFF")
        self.attributes("-topmost", True)

        # 폰트 설정
        self.text_font = ('Courier New', '8')
        self.text_font2 = ('Inter Black', '12')
        self.text_font4 = ('Inter Black', 15 * -1)
        self.my_font = Font(family="Roboto Bold", size=15 * -1)

        # 캔버스 생성
        self.canvas = Canvas(
            self,
            bg="#FFFFFF",
            height=690,
            width=450,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)

        self.image_image_1 = PhotoImage(
            file=resource_path(os.path.join("assets/frame0", "image_1.png"))
        )

        self.image_1 = self.canvas.create_image(
            387.0,
            492.0,
            image=self.image_image_1
        )

        self.image_image_2 = PhotoImage(
            file=resource_path(os.path.join("assets/frame0", "image_2_6.png"))
        )
        self.image_2 = self.canvas.create_image(
            225,
            360,
            image=self.image_image_2
        )

        self.canvas.create_text(
            24.0,
            20.0,
            anchor="nw",
            text="접속 사이트 URL",
            fill="#FFFFFF",
            font=("Roboto Bold", 18 * -1)
        )

        self.entry_image_24 = PhotoImage(
            file=resource_path(os.path.join("assets/frame0", "entry_28.png"))
        )
        self.entry_bg_24 = self.canvas.create_image(
            183.5,
            70.0,
            image=self.entry_image_24
        )
        self.entry_24 = Entry(
            bd=0,
            bg="#FFFFFF",
            fg="#000716",
            highlightthickness=0,
            font=("Roboto Bold", 12 * -1)
        )
        self.entry_24.place(
            x=40.0,
            y=55.0,
            width=297.0,
            height=30.0
        )

        # 이미지 로드 및 배치
        self.images_info = {}
        self.load_images()

        # 로그 정보 스크롤텍스트
        self.entry_25 = scrolledtext.ScrolledText(
            self,
            bd=0,
            bg="#FFFFFF",
            fg="#000716",
            highlightthickness=0,
            font=self.my_font
        )
        self.entry_25.place(x=35.0, y=398.0, width=380.0, height=255.0)

        # 로그 정보 텍스트 라벨
        self.canvas.create_text(
            30.0,
            340.0,
            anchor="nw",
            text="로그정보",
            fill="#FFFFFF",
            font=("Roboto Bold", 18 * -1)
        )

        # 시리얼 번호 표시
        self.canvas.create_text(
            380.0,
            10.0,
            anchor="nw",
            text=serial_number,
            fill="#FFFFFF",
            font=("Roboto Bold", 12 * -1)
        )

        self.entry_image_26 = PhotoImage(
            file=resource_path(os.path.join("assets/frame0", "entry_29_3.png"))
        )
        self.entry_bg_26 = self.canvas.create_image(
            223.0,
            238.0,
            image=self.entry_image_26
        )
        self.entry_image_25 = PhotoImage(
            file=resource_path(os.path.join("assets/frame0", "entry_29_2.png"))
        )
        self.entry_bg_25 = self.canvas.create_image(
            223.0,
            523.0,
            image=self.entry_image_25
        )

        # 금액 관련 엔트리 및 버튼
        self.create_amount_entries()

        # 현재 배팅 위치 표시
        self.create_current_betting_display()

        # 리셋 버튼
        self.reset_button1 = tk.Button(self, text="단계\n리셋", command=self.reset1, font=self.text_font4)
        self.reset_button1.place(x=355.0, y=240.0, width=50.0, height=50.0)

        # 접속 사이트 URL 엔트리
        self.entry_24 = Entry(
            self,
            bd=0,
            bg="#FFFFFF",
            fg="#000716",
            highlightthickness=0,
            font=("Roboto Bold", 12 * -1)
        )
        self.entry_24.place(x=40.0, y=55.0, width=297.0, height=30.0)



        # 베팅 시작 시 필요한 초기화
        asyncio.run_coroutine_threadsafe(self.initialize(), self.loop)

        # 창 닫기 이벤트
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 캔버스 클릭 이벤트 바인딩
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def load_images(self):
        # 이미지 로드 및 캔버스에 배치
        image_files = {
            'image1': "image_11.png",
            'image112': "btn_1.png",
            'image2': "btn_2.png",
            'image3': "btn_3.png",
            'image4': "btn_4.png"
        }
        for img_id, filename in image_files.items():
            image_path = resource_path(os.path.join("assets/frame0", filename))
            try:
                img = PhotoImage(file=image_path)
                x, y = self.get_image_position(img_id)
                self.images_info[img_id] = (x, y, img.width(), img.height())
                self.canvas.create_image(x, y, image=img)
                setattr(self, f"image_{img_id}", img)  # Prevent garbage collection
            except Exception as e:
                print(f"{filename} 로드 오류: {e}")

    def get_image_position(self, img_id):
        positions = {
            'image1': (390, 70),
            'image112': (70, 125),
            'image2': (173, 125),
            'image3': (378, 125),
            'image4': (277, 125)
        }
        return positions.get(img_id, (0, 0))

    def create_amount_entries(self):
        # 시작 금액
        self.canvas.create_text(
            40.0,
            180.0,
            anchor="nw",
            text="시작금액 : ",
            fill="#000000",
            font=("Inter Black", 15 * -1)
        )
        self.entry_3 = Entry(
            self,
            bd=0,
            bg="#FFFFFF",
            fg="#000716",
            highlightthickness=0,
            font=self.text_font4
        )
        self.entry_3.place(x=105.0, y=179.0, width=90.0, height=19.0)
        self.entry_3.insert(tk.END, 0)

        # 현재 금액
        self.canvas.create_text(
            40.0,
            205.0,
            anchor="nw",
            text="현재금액 : ",
            fill="#000000",
            font=("Inter Black", 15 * -1)
        )
        self.entry_2 = Entry(
            self,
            bd=0,
            bg="#FFFFFF",
            fg="#000716",
            highlightthickness=0,
            font=self.text_font4
        )
        self.entry_2.place(x=105.0, y=204.0, width=90.0, height=19.0)
        self.entry_2.insert(tk.END, 0)

        # 총 수익
        self.canvas.create_text(
            40.0,
            230.0,
            anchor="nw",
            text="총 수익 : ",
            fill="#000000",
            font=("Inter Black", 15 * -1)
        )
        self.entry_1 = Entry(
            self,
            bd=0,
            bg="#FFFFFF",
            fg="#000716",
            highlightthickness=0,
            font=self.text_font4
        )
        self.entry_1.place(x=105.0, y=229.0, width=90.0, height=19.0)
        self.entry_1.insert(tk.END, 0)

        # 수익시 일시정지
        self.canvas.create_text(
            40.0,
            255.0,
            anchor="nw",
            text="수익시 일시정지 - ",
            fill="#000000",
            font=("Inter Black", 15 * -1)
        )
        self.entry_4 = Entry(
            self,
            bd=1,
            bg="#FFFFFF",
            fg="#000716",
            highlightthickness=0,
            font=self.text_font4
        )
        self.entry_4.place(x=155.0, y=254.0, width=90.0, height=19.0)
        self.button_1 = tk.Button(
            self,
            text="입력",
            command=lambda: asyncio.run_coroutine_threadsafe(self.set1_click(self.entry_4.get()), self.loop),
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
        self.button_1.place(x=250.0, y=254.0, width=35.0, height=20.0)

        # 손실시 일시정지
        self.canvas.create_text(
            40.0,
            280.0,
            anchor="nw",
            text="손실시 일시정지 - ",
            fill="#000000",
            font=("Inter Black", 15 * -1)
        )
        self.entry_42 = Entry(
            self,
            bd=1,
            bg="#FFFFFF",
            fg="#000716",
            highlightthickness=0,
            font=self.text_font4
        )
        self.entry_42.place(x=155.0, y=279.0, width=90.0, height=19.0)
        self.button_2 = tk.Button(
            self,
            text="입력",
            command=lambda: asyncio.run_coroutine_threadsafe(self.set2_click(self.entry_42.get()), self.loop),
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
        self.button_2.place(x=250.0, y=279.0, width=35.0, height=20.0)

    def create_current_betting_display(self):
        # 현재 배팅 위치 표시
        self.canvas2 = Canvas(
            self,
            bg="#000000",
            width=180,
            height=30,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas2.place(x=225.0, y=179.0)
        self.canvas2.create_text(
            10.0,
            7.5,
            anchor="nw",
            text="현재 배팅 - ",
            fill="#FFCC00",
            font=("Inter Black", 15 * -1)
        )
        self.current_vmachine = Entry(
            self,
            bd=0,
            bg="#000000",
            fg="#FFCC00",
            highlightthickness=0,
            font=self.text_font4
        )
        self.current_vmachine.place(x=320.0, y=181.5, width=80.0, height=25.0)

    async def initialize(self):
        # 초기화 작업
        await martin_set_zero()
        await recode_log(serial_number, 'OPEN', 0, 0, 0, "", "", "", "", "", cal)

    def insert_log(self, message):
        # Thread-safe GUI 업데이트
        self.after(0, self.entry_25.insert, tk.END, message)
        self.after(0, self.entry_25.see, tk.END)

    def create_login_window(self):
        # 로그인 창 생성
        self.login_window = tk.Toplevel(self)
        self.login_window.title("로그인")
        self.login_window.geometry("300x200")

        label_username = tk.Label(self.login_window, text="사용자 이름:")
        label_username.pack()
        self.entry_username = tk.Entry(self.login_window)
        self.entry_username.pack()

        label_password = tk.Label(self.login_window, text="비밀번호:")
        label_password.pack()
        self.entry_password = tk.Entry(self.login_window, show="*")
        self.entry_password.pack()

        button_login = tk.Button(self.login_window, text="로그인",
                                 command=lambda: asyncio.run_coroutine_threadsafe(self.login(), self.loop))
        button_login.pack()

        self.login_window.protocol("WM_DELETE_WINDOW",
                                   lambda: asyncio.run_coroutine_threadsafe(self.login(), self.loop))

    async def login(self):
        # 로그인 처리
        username = self.entry_username.get()
        password = self.entry_password.get()
        url = "http://pattern2024.com/auto_login.php"
        datas = {
            'mb_id': username,
            'mb_password': password
        }

        try:
            response = requests.post(url, data=datas)
            t = response.text
            if t == "1":
                self.login_window.destroy()
            elif t == "no":
                messagebox.showerror("로그인 실패", "잘못된 사용자 이름 또는 비밀번호")
                self.destroy()
                sys.exit()
        except Exception as e:
            print(f"login 오류: {e}")
            messagebox.showerror("로그인 실패", "네트워크 오류")
            self.destroy()
            sys.exit()

    def on_canvas_click(self, event):

        # 캔버스 클릭 이벤트 핸들러
        for img_id, info in self.images_info.items():
            x, y, width_img, height_img = info
            if (x - width_img // 2 <= event.x <= x + width_img // 2 and
                    y - height_img // 2 <= event.y <= y + height_img // 2):
                if img_id == "image1":
                    if not hasattr(self, 'startThread_has_run') or not self.startThread_has_run:
                        future = asyncio.run_coroutine_threadsafe(get_permitted_sites(), self.loop)
                        site_names = future.result()
                        value_24 = self.entry_24.get().strip()
                        has_value_24 = bool(value_24)
                        if not has_value_24:
                            messagebox.showwarning("경고", "입력한 값이 없습니다.")
                            return
                        is_valid = True
                        if has_value_24:
                            if not any(site_name in value_24 for site_name in site_names):
                                is_valid = False
                        if is_valid:
                            asyncio.run_coroutine_threadsafe(self.run_playwright(value_24), self.loop)
                            self.startThread_has_run = True
                        else:
                            messagebox.showwarning("도메인 오류", "허용되지 않은 도메인으로 접속을 시도하여 프로그램을 종료합니다.")
                            self.on_closing()
                    else:
                        messagebox.showinfo("알림", "이미 실행 중이거나 창을 닫았을 경우 프로그램을 종료 후 다시 실행해 주세요.")

                elif img_id == "image2":
                    asyncio.run_coroutine_threadsafe(self.start_autobet(), self.loop)
                elif img_id == "image3":
                    asyncio.run_coroutine_threadsafe(self.stop_autobet(), self.loop)
                elif img_id == "image4":
                    asyncio.run_coroutine_threadsafe(self.stop_bet(), self.loop)
                elif img_id == "image112":
                    asyncio.run_coroutine_threadsafe(self.parse_betdata(), self.loop)

    async def chip_selection(self, price, c_res, step, round_, bonus, vname, new_page):

        global player_area, banker_area, start

        try:
            # 전역 변수 대신 클래스 변수 사용
            bet_price = int(price)
            remaining_price = int(price)  # 원본 price를 보존하려면 다른 변수 사용

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

            try:
                games_container = await new_page.wait_for_selector('.games-container', timeout=15000)
                if games_container:
                    iframe_element = await games_container.wait_for_selector('iframe', timeout=10000)
                    if iframe_element:
                        iframe = await iframe_element.content_frame()
                    else:
                        print("iframe_element를 찾을 수 없습니다.")
                        return
                else:
                    print(".games-container 요소를 찾을 수 없습니다.")
                    return
            except PlaywrightTimeoutError:
                print("게임 컨테이너를 찾는 데 타임아웃이 발생했습니다.")
                return
            except Exception as e:
                print(f"게임 컨테이너를 찾는 중 오류 발생: {e}")
                traceback.print_exc()
                return

            # 칩 계산 및 클릭
            for value, name in chips:
                if remaining_price >= value:
                    count = remaining_price // value
                    remaining_price %= value
                    if count > 0:
                        result.append(f"{name}번칩 {int(count)}개")
                        css_selector = f".expandedChipStack--f87da > div:nth-child({name}) .chip--29b81"
                        try:
                            chip = iframe.locator(css_selector)
                            print(f"chip locator: {chip}")
                            # 요소 상태 확인
                            is_visible = await chip.is_visible()
                            is_enabled = await chip.is_enabled()
                            print(f"chip is_visible: {is_visible}, is_enabled: {is_enabled}")
                            if is_visible and is_enabled:
                                await chip.scroll_into_view_if_needed()
                                print("chip이 보입니다. 클릭 시도 중...")
                                try:
                                    await chip.click(force=True)
                                    player_area = iframe.locator('.player--76ad0')
                                    banker_area = iframe.locator('.banker--6ce2f')

                                    for _ in range(int(count)):
                                        if betstop:
                                            insert_log.insert("실제 칩 배팅 정지중..\n\n")
                                        else:
                                            if bonus == "bonus":
                                                await self.click_chip2(c_res)
                                            else:
                                                await self.click_chip(c_res, player_area, banker_area)

                                    start = False
                                    # return 제거
                                except PlaywrightTimeoutError:
                                    print(f"강제 클릭 타임아웃 발생")
                                except Exception as e:
                                    print(f"강제 클릭 중 오류 발생: {e}")
                            else:
                                print("chip이 보이거나 활성화되지 않았습니다.")
                        except Exception as e:
                            print(f"칩 {name}을 선택하는 중 예상치 못한 오류 발생: {e}")
                            continue

            if c_res == "T":
                entry_25.insert(
                    tk.END,
                    ("※※ " + ", ".join(result) + "🟢 TIE에 " + str(
                        bet_price) + "원 배팅 ※※\n\n=================================\n\n"),
                    "green"
                )
                entry_25.see(tk.END)
            else:
                if step == -1:
                    message = "세션만료 방지를 위한 P에 1000원 배팅\n\n=================================\n\n"
                    self.insert_log(message)
                else:
                    log_message = f"{', '.join(result)} {c_res} {vname} 에 {bet_price}원 배팅\n\n=================================\n\n"
                    print(result, c_res, vname, bet_price)
                    self.insert_log(log_message)
                    await recode_log(vname, 'RUNNING', self.start_price, current_price, bet_price, d_title, r_title, c_res,
                               step,
                               round, cal)


        except Exception as e:
            print(f"chip_selection 오류: {e}")
            traceback.print_exc()

    async def click_chip(self, c_res, player_area: 'Locator', banker_area: 'Locator'):
        """
        Playwright를 사용하여 칩을 클릭하는 함수.
        """
        global autobet_called
        try:
            if c_res == "P":
                # 플레이어 영역 클릭 로직
                locator = player_area
                area_name = "player_area"
            elif c_res == "B":
                # 뱅커 영역 클릭 로직
                locator = banker_area
                area_name = "banker_area"
            else:
                print(f"알 수 없는 c_res 값: {c_res}")
                return

            # 요소의 가시성 및 활성화 상태 확인
            is_visible = await locator.is_visible()
            is_enabled = await locator.is_enabled()
            print(f"{area_name} is_visible: {is_visible}, is_enabled: {is_enabled}")

            if not is_visible:
                print(f"{area_name}가 보이지 않습니다.")
                return
            if not is_enabled:
                print(f"{area_name}가 활성화되지 않았습니다.")
                return

            # 요소를 뷰로 스크롤
            await locator.scroll_into_view_if_needed()
            print(f"{area_name}을(를) 뷰로 스크롤했습니다.")

            # 강제 클릭 시도
            try:
                await locator.click(force=True)
                print(f"{area_name} 클릭 완료 (force=True 사용)")
                autobet_called = False
                return
            except PlaywrightTimeoutError:
                print(f"{area_name} 강제 클릭 타임아웃 발생")
            except Exception as e:
                print(f"{area_name} 강제 클릭 중 오류 발생: {e}")

        except Exception as e:
            print(f"click_chip 오류: {e}")
            traceback.print_exc()

    async def start_autobet(self):
        global lose, betstop, step_order, next_value, sum_price, betting_price, price_running, c_res, c_res2
        # 오토베팅 시작
        print("오토시작")
        self.s_bet = True
        lose = False
        betstop = False
        self.price_running = True
        c_res = None
        c_res2 = None

        # price_updated 플래그 초기화
        self.price_updated = False

        step_order = [0] * len(vbet_data)
        next_value = 0
        sum_price = 0
        betting_price = base_price

        await recode_log(serial_number, 'START', start_price, current_price, 0, d_title, r_title, "", "", "", cal)
        self.insert_log("==================================\n오토프로그램 시작\n==================================\n\n")


    async def stop_autobet(self):
        global step, current_price, re_start, step_order, next_value, sum_price, betting_price, check_type, cal, price_running, c_res, c_res2

        # 오토베팅 정지
        print("오토정지")
        self.price_running = False
        re_start = True
        self.s_bet = False
        next_value = 0
        check_type = ""
        step_order = [0] * len(vbet_data)
        sum_price = 0
        betting_price = base_price
        c_res = None
        c_res2 = None

        await recode_log(serial_number, 'STOP', start_price, current_price, 0, d_title, r_title, "", "", round_num, cal)
        self.insert_log("==================================\n패턴 오토프로그램 일시정지\n==================================\n\n\n")

        # get_price 태스크 취소
        if self.price_task:
            self.price_task.cancel()
            try:
                await self.price_task
            except asyncio.CancelledError:
                pass
            self.price_task = None

    async def stop_bet(self):
        global betstop
        betstop = True
        self.insert_log(
            "=======================================\n실제 칩 배팅 정지\n=======================================\n\n")

    async def get_base_value(self) -> int:
        global base_price
        try:
            # 요소 선택: 최대 5초 대기 (5000 밀리초)
            selector = '.vbet-setting-area:first-child input[name="base-bet"]'
            element = await self.page2.wait_for_selector(selector, timeout=5000)

            if element:
                # 'value' 속성 값 가져오기
                value_str = await element.get_attribute('value')

                # 'value'를 정수로 변환
                base_value = self.clean_value(value_str)
                if base_value is not None:
                    print(f"Base Value (int): {base_value}")
                    base_price = base_value
                    return base_value
                else:
                    print(f"Value '{value_str}' is not a valid integer.")
            else:
                print("Element not found or 'value' attribute is missing.")

        except TimeoutError:
            print("entry_base가 존재하지 않거나 유효한 숫자가 아닙니다.")
            base_price = 1000
            return 1000  # 기본값 반환
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            base_price = 1000
            return 1000  # 기본값 반환

    async def parse_betdata(self):
        global vbet_amount, vbet_data, step_order, order, vbet_keys, selected_index, r_title, base_price
        # select[name=amount-vbet]의 선택된 값 가져오기
        vbet_amount_str = await self.page2.locator("select[name=amount-vbet]").input_value()

        # int로 변환
        vbet_amount = int(vbet_amount_str)
        try:
            if vbet_amount > 0:

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
                        if serial_number == "MASTER":
                            sn = 'ADMIN'
                        else:
                            sn = serial_number
                        base_price = vbet_data[sn.lower() + '-1']['betting']['base']

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
                                valid_bets = [f"{key_map.get(key, key)}={value}" for key, value in betting.items() if
                                              value]
                                if valid_bets:
                                    entry_text += ', '.join(valid_bets)
                                    entry_text += "\n================================\n"

                        # 마지막 "|" 제거
                        entry_text = entry_text.rstrip(" | ")

                        # entry_25에 텍스트 설정
                        self.insert_log(entry_text)  # 새로운 텍스트 삽입

                    except ValueError:
                        print("응답이 JSON 형식이 아닙니다.")
                else:
                    print(f"HTTP 요청 실패. 상태 코드: {response.status_code}")
                # 베팅 데이터 파싱 로직
                self.insert_log("베팅 데이터 파싱 완료\n")
                # 예시: 실제 데이터 파싱 및 GUI 업데이트
        except Exception as e:
            print(f"parse_betdata 오류: {e}")

    async def run_playwright(self, url):
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.91 Safari/537.36"

        try:
            # DPI를 고려한 화면 해상도 가져오기
            screen_width, screen_height = get_screen_resolution()

            print(screen_width, screen_height)

            if screen_width < 1921:
                device_scale_factor = 0.65
                half_width = screen_width // 1.3
                full_height = screen_height * 1.2
            elif screen_width < 2561:
                device_scale_factor = 1.25
                half_width = round((screen_width // 1.75))
                full_height = round((screen_height // 1.1))
            elif screen_width > 2561:
                device_scale_factor = 1
                half_width = screen_width // 2
                full_height = screen_height // 1.2
            else:
                device_scale_factor = 1
                half_width = (screen_width // 2) * 1.5
                full_height = (screen_height // 1.2) * 1.5

            chrome_path = find_chrome_executable()
            print(chrome_path)
            profile_path = "C:/Users/khj/AppData/Local/Google/Chrome/User Data"
            p_p = "C:/temp/profile"

            # Playwright 인스턴스 시작 (하나의 인스턴스에서 두 브라우저 관리)
            async with async_playwright() as playwright:
                print("Launching the first browser instance...")

                chrome_args1 = [
                    '--lang=ko_KR',
                    f'--user-agent={user_agent}',
                    f'--window-size={half_width},{full_height}',
                    f'--window-position=0,0',
                    f'--force-device-scale-factor={device_scale_factor}',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-extensions',
                    '--high-dpi-support=1',
                    '--start-maximized'

                ]

                h_h = round(half_width)

                chrome_args2 = [
                    '--lang=ko_KR',
                    f'--user-agent={user_agent}',
                    f'--window-size={half_width},{full_height}',
                    f'--window-position={h_h},0',
                    f'--force-device-scale-factor={device_scale_factor}',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-extensions',
                    '--high-dpi-support=1',
                    '--start-maximized'
                ]

                browser1 = await playwright.chromium.launch(
                    headless=False,
                    executable_path=chrome_path,
                    args=chrome_args1
                )

                context1 = await browser1.new_context(
                    no_viewport=True,
                    #viewport={"width": half_width, "height": full_height},
                    #device_scale_factor=device_scale_factor,
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.91 Safari/537.36"
                )
                self.page1 = await context1.new_page()
                #await self.page1.goto(url)

                # 두 번째 브라우저 인스턴스 열기
                print("Launching the second browser instance...")
                browser2 = await playwright.chromium.launch(
                    headless=False,
                    executable_path=chrome_path,
                    args=chrome_args2
                )

                context2 = await browser2.new_context(
                    no_viewport=True,
                    #viewport={"width": half_width, "height": full_height},
                    #device_scale_factor=device_scale_factor,
                    user_agent=user_agent
                )
                self.page2 = await context2.new_page()
                await asyncio.gather(
                    self.page1.goto(url),  # 실제 웹소켓 페이지 URL로 변경
                    self.page2.goto('http://pattern2024.com/bbs/login.php?agency=pt9')
                )
                #await self.page2.goto("http://pattern2024.com/bbs/login.php?agency=pt9")

                # 로그인 작업 수행 (두 번째 브라우저)
                login_id = serial_number.lower()
                #await self.page2.fill("#login_id", login_id)
                #await self.page2.fill("#login_pw", password)
                await self.page2.fill("#login_id", "admin")
                await self.page2.fill("#login_pw", "1asdsasd")
                await self.page2.click(".btn_submit")


                # `page1`에서 새 창이 열릴 때 감지하기 위한 핸들러 등록
                # 동기화 이벤트 생성
                process_completed_event = asyncio.Event()

                # `page1`에서 새 창이 열릴 때 감지하기 위한 핸들러 등록
                self.page1.context.on("page", lambda new_page: asyncio.create_task(
                    handle_new_page(new_page, self.page1, self.page2, process_completed_event, self)
                ))

                await asyncio.sleep(360000)

                # 브라우저가 닫힐 때까지 대기
                await asyncio.gather(
                    self.browser1.wait_for_close(),
                    self.browser2.wait_for_close()
                )

                # 브라우저 종료 후 로그 기록
                print("Both browsers have closed successfully.")
                # Playwright 정리
                await self.browser1.close()
                await self.browser2.close()
                await self.playwright.stop()

                # 로그에 브라우저 종료 기록
                self.insert_log("브라우저가 정상적으로 종료되었습니다.\n")


        except Exception as e:
            print(f"run_playwright 오류:{e}")

    def on_closing(self):
        # 어플리케이션 종료 시 처리
        global price_running
        try:
            current_price = self.entry_2.get()
            price_number = re.sub(r'[^0-9.]', '', current_price)
            cal = int(float(price_number)) - int(float(price_number2))
        except:
            print("오류")

        asyncio.run_coroutine_threadsafe(
            recode_log(serial_number, 'END', start_price, current_price, 0, d_title, r_title, "", "", round_num, cal),
            self.loop
        )

        if messagebox.askokcancel("종료", "종료하시겠습니까?"):
            price_running = False
            asyncio.run_coroutine_threadsafe(martin_set_zero(), self.loop)

            # Playwright 브라우저가 열려있다면 닫기
            if self.browser1 and self.browser1.is_connected():
                asyncio.run_coroutine_threadsafe(self.browser1.close(), self.loop)
            if self.playwright1:
                asyncio.run_coroutine_threadsafe(self.playwright1.stop(), self.loop)

            if self.browser2 and self.browser2.is_connected():
                asyncio.run_coroutine_threadsafe(self.browser2.close(), self.loop)
            if self.playwright2:
                asyncio.run_coroutine_threadsafe(self.playwright2.stop(), self.loop)

            self.destroy()

    async def set1_click(self, value):
        global profit_stop2
        try:
            profit_stop2 = int(value)
            self.insert_log("==================================\n수익시 일시정지 금액 : " + str(
                profit_stop2) + " 설정 완료\n==================================\n\n")
        except ValueError:
            print("유효한 수익시 일시정지 금액을 입력하세요.")

    async def set2_click(self, value):
        global loss_stop2
        try:
            loss_stop2 = int(value)
            self.insert_log("==================================\n손실시 일시정지 금액 : " + str(
                loss_stop2) + " 설정 완료\n==================================\n\n")
        except ValueError:
            print("유효한 손실시 일시정지 금액을 입력하세요.")

    def reset1(self):
        global step_order, next_value, order_index, start, betting_price, sum_price
        step_order = [0] * len(vbet_data)
        next_value = 0
        order_index = 1
        sum_price = 0
        betting_price = base_price
        start = True
        self.insert_log("==================================\n마틴 단계 1 단계로\n==================================\n\n")
        # 베팅 초기화 로직 추가
        # 예시: Playwright를 사용하여 베팅 초기화
        # asyncio.run_coroutine_threadsafe(self.reset_betting(), self.loop)

    # 추가적인 비동기 함수 및 로직 구현 필요
    async def get_price(self, new_page):
        print(f'running get_price : {self.price_running}, {self.price_updated}')
        global cal, r_title
        previous_price_number = 0  # 이전 가격 저장 변수

        while True:
            try:
                # .games-container 요소 대기
                games_container = await new_page.wait_for_selector('.games-container', timeout=15000)
                if games_container:
                    iframe_element = await games_container.wait_for_selector('iframe', timeout=10000)
                    if iframe_element:
                        iframe = await iframe_element.content_frame()
                    else:
                        print("iframe_element를 찾을 수 없습니다.")
                        self.insert_log("iframe_element를 찾을 수 없습니다. get_price 일시정지.")
                        self.price_running = False
                        break
                else:
                    print(".games-container 요소를 찾을 수 없습니다.")
                    self.insert_log(".games-container 요소를 찾을 수 없습니다. get_price 일시정지.")
                    self.price_running = False
                    break
            except PlaywrightTimeoutError:
                print("게임 컨테이너를 찾는 데 타임아웃이 발생했습니다.")
                self.insert_log("게임 컨테이너를 찾는 데 타임아웃이 발생했습니다. get_price 일시정지.")
                self.price_running = False
                break
            except Exception as e:
                print(f"게임 컨테이너를 찾는 중 오류 발생: {e}")
                self.insert_log(f"게임 컨테이너를 찾는 중 오류 발생: {e}. get_price 일시정지.")
                traceback.print_exc()
                self.price_running = False
                break

            try:
                # .amount--f8dd5 span 요소 대기 및 텍스트 추출
                element = await iframe.wait_for_selector('.amount--f8dd5 span', timeout=5000)
                current_price = await element.inner_text()
                current_price = current_price.strip()
                price_number = re.sub(r'[^0-9.]', '', current_price)

                # 이전 가격 초기화
                if previous_price_number == 0:
                    previous_price_number = float(price_number)
                if self.start_price is not None:
                    cal = int(float(price_number)) - int(float(self.start_price))
                else:
                    cal = 0
                positive_cal = abs(cal)

                # 이전 가격 업데이트
                previous_price_number = float(price_number)

                # GUI 업데이트
                self.update_entries(price_number, cal)

                # entry_3을 한 번만 업데이트
                if not self.price_updated:
                    self.entry_3.config(state='normal')  # 편집 가능 상태로 변경
                    self.entry_3.delete(0, tk.END)  # 기존 내용 삭제
                    self.entry_3.insert(0, price_number)  # 새로운 가격 입력
                    self.entry_3.config(state='readonly')  # 읽기 전용으로 설정
                    self.start_price = price_number
                    self.price_updated = True  # 플래그 설정

            except PlaywrightTimeoutError:
                # 요소를 찾지 못했을 경우
                #self.insert_log("Element '.amount--f8dd5 span' not found. get_price 일시정지.")
                pass
            except Exception as e:
                self.insert_log(f"Error in get_price: {e}")
                self.price_running = False
                break

            await asyncio.sleep(1)  # 1초 대기

    def update_entries(self, price_number, cal):
        # tkinter는 메인 스레드에서만 안전하게 업데이트 가능
        def _update():
            self.entry_1.config(state='normal')
            self.entry_1.delete(0, tk.END)
            self.entry_1.insert(0, str(cal))
            self.entry_1.config(state='readonly')

            self.entry_2.config(state='normal')
            self.entry_2.delete(0, tk.END)
            self.entry_2.insert(0, str(price_number))
            self.entry_2.config(state='readonly')

        self.after(0, _update)

async def handle_resize(width, height):
    print(f"브라우저 창이 {width}x{height}로 변경되었습니다.")


async def handle_websocket(websocket, page2, process_completed_event, new_page, self):
    try:
        target_ws_url = '/public/baccarat/player/game/'
        if target_ws_url in websocket.url:
            print(f"타겟 웹소켓 연결 감지: {websocket.url}")
            # 'framereceived' 이벤트 핸들러 수정: frame.data를 전달
            #websocket.on("framereceived", lambda payload: asyncio.create_task(1(payload)))
            await page2.reload()
            websocket.on("framereceived", lambda frame: asyncio.create_task(
                process_received_payload(frame, page2, process_completed_event, new_page, self)
            ))
            print("framereceived 이벤트 핸들러 등록 완료")
            # get_price 백그라운드 태스크 시작
            asyncio.create_task(self.get_price(new_page))
            print("get_price 이벤트 핸들러 등록 완료")

    except Exception as e:
        print("handle_websocket 함수에서 오류 발생:")
        print(e)
        traceback.print_exc()

# asyncio 이벤트 루프를 별도의 스레드에서 실행

async def handle_new_page(new_page, page1, page2, process_completed_event, self):
    global d_title, r_title
    try:
        # 새 창의 로드 완료 대기
        await new_page.wait_for_load_state('networkidle')
        print("새 창 로드 완료")

        d_title = await page1.title()

        # 웹소켓 이벤트 핸들러 등록
        new_page.on("websocket", lambda ws: asyncio.create_task(
            handle_websocket(ws, page2, process_completed_event, new_page, self)
        ))
        print("new_page 웹소켓 핸들러 등록 완료")

        # URL에 'game=baccarat'가 포함될 때까지 대기
        print("URL 변경 대기 중... (game=baccarat 포함 확인)")
        await new_page.wait_for_function(
            "() => window.location.href.includes('game=baccarat')",
            polling=1000,
            timeout=3000000  # 30초 대기
        )
        print("URL에 'game=baccarat'가 포함됨 확인")

        # 자동화 방지 스크립트 삽입
        await new_page.add_init_script("""
            // 기존 속성 추가
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
            Object.defineProperty(navigator, 'languages', { get: () => ['ko-KR', 'ko'] });

            // Chrome 객체 추가
            window.chrome = { runtime: {} };

            // navigator.permissions 조작
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ? 
                    Promise.resolve({ state: 'denied' }) : 
                    originalQuery(parameters)
            );

            // userAgent 및 platform 설정
            Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
            Object.defineProperty(navigator, 'userAgent', {
                get: () => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.91 Safari/537.36'
            });
        """)
        print("자동화 방지 스크립트가 성공적으로 삽입되었습니다.")


        # 추가 작업 진행
        print(f"'game=baccarat'를 포함하는 새 창이 열렸습니다: {new_page.url}")

        await self.parse_betdata()

        # new_page를 클래스 변수에 저장
        self.current_new_page = new_page

        r_title = await get_r_title(new_page)

        process_completed_event.set()

    except asyncio.TimeoutError:
        print("URL에 'game=baccarat'가 포함되지 않아 타임아웃이 발생했습니다.")
    except Exception as e:
        print(f"handle_new_page 함수에서 오류 발생: {e}")


async def process_received_payload(payload, page2, process_completed_event, new_page, self):
    try:
        await process_completed_event.wait()
        data = json.loads(payload)
        message_type = data.get('type', '')
        args = data.get('args', {})

        if message_type == "baccarat.encodedShoeState":
            current_time = time.time()
            # 마지막 실행 시간과 현재 시간의 차이를 계산
            time_since_last = current_time - self.last_baccarat_time
            if time_since_last >= 5:
                # 쿨다운이 지났으므로 함수 실행
                self.last_baccarat_time = current_time  # 마지막 실행 시간 업데이트
                history_v2 = args.get('history_v2', [])
                await update_page2_with_history(page2, history_v2)
                await asyncio.sleep(1)  # 원래 5초 대기라고 주석이 있었으나, 1초로 설정됨
                await click_check_pattern(page2, new_page, self)
            else:
                # 쿨다운 기간 내이므로 함수 실행 건너뜀
                remaining_time = 5 - time_since_last
                print(f"쿨다운 중: {remaining_time:.2f}초 후에 다시 시도할 수 있습니다.")

    except Exception as e:
        print("process_received_payload 함수에서 오류 발생:")
        print(e)
        traceback.print_exc()

async def update_page2_with_history(page2, history_v2):
    try:
        #print(f"page2의 id='{table_id}' 요소를 업데이트 시작")

        # page2에서 해당 table_id를 가진 요소 찾기
        target_element = await page2.query_selector('.result2.active')
        if not target_element:
            #print(f"page2에서 id='{table_id}' 요소를 찾을 수 없습니다.")
            return

        # .pattern3 요소 찾기
        pattern3 = await target_element.query_selector('.pattern3')
        if not pattern3:
            print(f"page2의 id='{table_id}' 요소 내에 .pattern3 요소를 찾을 수 없습니다.")
            return

        # .pattern3 내의 모든 ul 요소 삭제 (특정 범위 내에서)
        await pattern3.evaluate("""
                    (element) => {
                        const uls = element.querySelectorAll('ul');
                        console.log(`Deleting ${uls.length} ul elements`);
                        uls.forEach(ul => ul.remove());                        
                    }
                """, pattern3)
        #print(f"table_id='{table_id}'의 .pattern3 내 모든 ul 요소를 삭제했습니다.")

        # JavaScript 코드 정의: 전체 history를 다시 추가
        js_code = """
                   (payload) => {
                       const { history } = payload;

                       const targetElement = document.querySelector('.result2.active');
                       if (!targetElement) return;

                       const pattern3 = targetElement.querySelector('.pattern3');
                       if (!pattern3) return;

                       // 마지막 ul과 마지막 winner 확인
                       let lastUl = pattern3.querySelector('ul:last-child');
                       let lastWinner = null;

                       if (lastUl) {
                           const lastLi = lastUl.querySelector('li:last-child');
                           if (lastLi) {
                               const lastP = lastLi.querySelector('p');
                               if (lastP) {
                                   if (lastP.classList.contains('ball_p2')) {
                                       lastWinner = 'Player';
                                   } else if (lastP.classList.contains('ball_b2')) {
                                       lastWinner = 'Banker';
                                   }
                               }
                           }
                       }

                       history.forEach(item => {
                           const winner = item.winner;
                           if (!winner || (winner !== 'Player' && winner !== 'Banker' && winner !== 'Tie')) return;

                           if (winner === 'Tie') {
                               // 'Tie'인 경우, 마지막 ul의 마지막 li에 p 요소 추가
                               if (lastUl && lastUl.querySelector('li:last-child')) {
                                   const lastLi = lastUl.querySelector('li:last-child');
                                   const pTie = document.createElement('p');
                                   pTie.className = 'line_t';
                                   pTie.textContent = 'T';
                                   lastLi.appendChild(pTie);
                               }
                           } else {
                               const li = document.createElement('li');
                               const p = document.createElement('p');

                               if (winner === 'Player') {
                                   p.className = 'ball_p2';
                                   p.textContent = 'P';
                               } else if (winner === 'Banker') {
                                   p.className = 'ball_b2';
                                   p.textContent = 'B';
                               }

                               li.appendChild(p);

                               if (winner === lastWinner && lastUl) {
                                   lastUl.appendChild(li);
                               } else {
                                   const newUl = document.createElement('ul');
                                   newUl.className = 'history-ul';
                                   newUl.appendChild(li);
                                   pattern3.appendChild(newUl);
                                   lastUl = newUl;
                                   lastWinner = winner;
                               }
                           }
                       });

                       // .pattern3 요소의 X축 스크롤을 오른쪽 끝으로 이동
                       pattern3.scrollLeft = pattern3.scrollWidth;
                   }
               """

        # 인자를 하나의 딕셔너리로 전달
        payload = {
            'history': history_v2
        }

        # evaluate 호출 시 단일 인자(payload) 전달
        await page2.evaluate(js_code, payload)

        #print(f"page2의 id='{table_id}' 요소를 성공적으로 업데이트했습니다.")
    except Exception as e:
        #print("update_page2_with_history 함수에서 오류 발생:")
        #print(e)
        traceback.print_exc()


async def get_c_res(self, page2):
    try:
        # '.c-txt33' 요소의 존재 여부 확인
        elements = page2.locator('.c-txt33')
        count = await elements.count()

        if count > 0:
            # 요소가 존재하면 inner_text 가져오기
            c_res = await elements.first.inner_text()
            c_res = c_res.strip()  # 공백 제거

            if not c_res:
                # inner_text가 비어있는 경우 처리
                c_res = None  # 또는 원하는 기본값 설정
            else:
                pass
        else:
            # 요소가 존재하지 않을 경우 처리
            self.insert_log("'.c-txt33' 요소가 존재하지 않습니다.")
            c_res = None  # 또는 원하는 기본값 설정

        return c_res

    except Exception as e:
        # 예상치 못한 오류 처리
        self.insert_log(f"'.c-txt33' 요소를 처리하는 중 오류 발생: {e}")
        traceback.print_exc()
        return None  # 또는 원하는 기본값 설정

async def click_check_pattern(page2, new_page, self):
    global autobet_called, step_order, stop_check, sum_price, base_price, c_res, c_res2
    try:
        #print(f"tableId='{table_id}'의 .check-pattern 요소 클릭 시도")
        # 해당 table_id의 .check-pattern 요소 찾기
        selector = '.result2.active .pattern_group2 .tit .t'
        check_pattern_element = await page2.query_selector(selector)
        if check_pattern_element:
            await check_pattern_element.click()
            await asyncio.sleep(2)  # 5초 대기

            tie_check = await page2.locator('.result2.active .pattern_group2 ul:last-child li:last-child p:last-child').inner_text()
            c_res = await get_c_res(self, page2)

            #c_res = await page2.locator('.c-txt33').inner_text()
            if c_res2:
                print(f'이전 배팅: {c_res2}')
            print(f'다음 예측: {c_res}')

            if c_res2 is not None and not start:
                if tie_check == c_res2:
                    self.insert_log("=================================\n승리\n=================================\n\n")
                    await recode_log(vbet_key, 'WIN', start_price, current_price, 0, d_title, r_title,"", "",round, cal)
                    if vbet_amount > 1:
                        sum_price += betting_price
                    else:
                        step_order[current_int - 1] = 0
                        bet_input = step_order[current_int - 1] + 1
                        try:
                            if lose:
                                # Lose 조건일 때 클릭할 요소의 셀렉터
                                bet_selector = f".{vbet_key} .lbet1"
                            else:
                                # Lose 조건이 아닐 때 클릭할 요소의 셀렉터
                                bet_selector = f".{vbet_key} .lbet{bet_input}"

                            # 요소를 찾고 클릭 시도
                            bet_locator = page2.locator(bet_selector)

                            # 요소가 나타날 때까지 대기 (최대 15초)
                            await bet_locator.wait_for(state="visible", timeout=15000)

                            # 클릭
                            await bet_locator.click()
                            print(f"Successfully clicked on selector: {bet_selector}")

                        except PlaywrightTimeoutError:
                            print(f"Timeout: Selector '{bet_selector}' not found within the given time.")
                        except Exception as e:
                            print(f"Error clicking on bet button: {e}")
                elif tie_check != c_res2:
                    if tie_check == "T":
                        self.insert_log("================================\n타이\n================================\n\n")
                        await recode_log(vbet_key, 'TIE', self.start_price, current_price, 0, d_title, r_title, "","",round, cal)
                    else:
                        self.insert_log("=================================\n패배\n=================================\n\n")
                        await recode_log(vbet_key, 'LOSE', start_price, current_price, 0, d_title, r_title, "", "",round, cal)
                        # if bet_type != 3:
                        #    step_order[current_int - 1] += 1
                        if vbet_amount > 1:
                            sum_price -= betting_price
                        else:
                            step_order[current_int - 1] += 1
                            bet_input = step_order[current_int - 1] + 1
                            try:
                                if lose:
                                    # Lose 조건일 때 클릭할 요소의 셀렉터
                                    bet_selector = f".{vbet_key} .lbet1"
                                else:
                                    # Lose 조건이 아닐 때 클릭할 요소의 셀렉터
                                    bet_selector = f".{vbet_key} .lbet{bet_input}"

                                # 요소를 찾고 클릭 시도
                                bet_locator = page2.locator(bet_selector)

                                # 요소가 나타날 때까지 대기 (최대 15초)
                                await bet_locator.wait_for(state="visible", timeout=15000)

                                # 클릭
                                await bet_locator.click()
                                print(f"Successfully clicked on selector: {bet_selector}")

                            except PlaywrightTimeoutError:
                                print(f"Timeout: Selector '{bet_selector}' not found within the given time.")
                            except Exception as e:
                                print(f"Error clicking on bet button: {e}")

                elif tie_check == "T":
                    self.insert_log("================================\n타이\n================================\n\n")
                    await recode_log(vbet_key, 'TIE', start_price, current_price, 0, d_title, r_title, "", "",round, cal)

            # 추가적인 요소의 셀렉터 정의 (Selenium의 CSS_SELECTOR와 유사)
            element_selector = '[class*="gameResult"] > div'

            # element_selector가 나타날 때까지 대기
            try:
                games_container = await new_page.wait_for_selector('.games-container', timeout=15000)  # 타임아웃을 15초로 연장
                if games_container:
                    # 첫 번째 iframe 요소 선택
                    iframe_element = await games_container.wait_for_selector('iframe', timeout=10000)  # 타임아웃을 10초로 연장
                    if iframe_element:
                        # iframe의 Frame 객체 가져오기
                        iframe = await iframe_element.content_frame()
                        if iframe:
                            element_handle = await iframe.wait_for_selector(element_selector, timeout=15000)
                            if element_handle:
                                print(f"element_selector '{element_selector}' 발견")
                                # 4초 대기 후 autoBet 실행
                                await asyncio.sleep(2)
                                print(self.s_bet, autobet_called)
                                if self.s_bet and not autobet_called:
                                    if not start:
                                        autobet_called = True
                                    await autoBet(page2, new_page, c_res, self)
                                else:
                                    print(f"s_bet이 False입니다. autoBet 함수를 호출하지 않습니다.")
                            else:
                                print(f"셀렉터 '{element_selector}'에 해당하는 요소를 찾을 수 없습니다.")
            except PlaywrightTimeoutError:
                print(f"element_selector '{element_selector}'를 찾는 데 타임아웃이 발생했습니다.")
                return
            except Exception as e:
                print(f"element_selector '{element_selector}'를 찾는 중 오류 발생: {e}")


        else:
            #print(f"tableId='{table_id}'에 해당하는 .check-pattern 요소를 찾을 수 없습니다.")
            return  # 클릭할 요소가 없으면 이후 단계를 수행할 필요 없음

    except Exception as e:
        #print("click_check_pattern 함수에서 오류 발생:")
        #print(e)
        traceback.print_exc()

async def autoBet(page2, new_page, c_res, self):
    martin_list = ['base', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th']
    page1 = new_page

    # 필요한 전역 변수 선언
    global step, x_stop, lose, start, current_price, t_check, last_tie_step, group_level, autobet_called, c_res2
    global player_bonus, banker_bonus, group2_get, group2_get_sum
    global tie_on, re_start, win_stack, ask_dialog, tie_step, tie_area, stop_check
    global stop_check2, stop_check4, lose_stack, stop_step2, check_type, check_kind
    global compare_mybet, highest_variable, element_length, previously_selected, current_group
    global long_go_o, long_go_x, round_no, cal, change_on, change_no, order_index
    global martin_kind, step_o, vbet_key, current_int, next_value, step_order
    global order_index, betting_price, sum_price, go_bet, current_res, base_price
    global no_bet_count, betting_on, positive_cal

    try:
        # .games-container 요소 선택
        games_container = await new_page.wait_for_selector('.games-container', timeout=15000)  # 타임아웃을 15초로 연장
        if games_container:
            # 첫 번째 iframe 요소 선택
            iframe_element = await games_container.wait_for_selector('iframe', timeout=10000)  # 타임아웃을 10초로 연장
            if iframe_element:
                # iframe의 Frame 객체 가져오기
                iframe = await iframe_element.content_frame()
                if iframe:
                    # 요소를 찾기
                    tie_area = await iframe.locator('.tie--4b300').element_handle()
                    current_price = await iframe.locator('.amount--f8dd5 span').inner_text()
                    round_no = await page2.locator('.result2 .current_no').inner_text()

                    # 가격 계산
                    price_number = re.sub(r'[^0-9.]', '', current_price)
                    cal = int(float(price_number)) - int(float(price_number))
                    positive_cal = abs(cal)
                    print(positive_cal)

                    if betting_price == 0:
                        betting_price = base_price



                    try:
                        # type과 kind 속성 확인
                        check_type = "O"
                        check_kind = "B"

                        print(f"CURRENT RES : {c_res}")

                        c_res2 = await get_c_res(self, page2)

                        # current_res 값 가져오기
                        if c_res is not None:

                            autobet_called = True

                            tie_check = await page2.locator('.result2.active .pattern_group2 ul:last-child li:last-child p:last-child').inner_text()
                            t_check = tie_check
                            go_bet = True
                            if tie_check == "T":
                                no_bet_count += 1
                            else:
                                no_bet_count = 0


                            # check_type이 O인 경우 로직
                            if check_type == "O":

                                if cal > 0 and (profit_stop2 != 0 and profit_stop2 * profit_stop_count <= cal):
                                    await stop_autobet()
                                    pass
                                elif cal < 0 and (loss_stop2 != 0 and loss_stop2 <= positive_cal):
                                    await stop_autobet()
                                    pass
                                else:
                                    if tie_check == "T":
                                        lose = False
                                    if lose:
                                        if len(vbet_data) == 1:
                                            next_value = 0
                                            step_order[next_value] = 0
                                        else:
                                            next_value = show_next_order()
                                            step_order[next_value] = 0
                                    else:
                                        if bet_type != 2:
                                            if tie_check == "T":
                                                next_value = next_value
                                            else:
                                                next_value = show_next_order()


                                        if re_start or start:
                                            next_value = 0
                                            order_index = 1
                                            step_order = [0] * len(vbet_data)
                                            sum_price = 0
                                            betting_price = base_price



                                    if not start and vbet_amount > 1:
                                        print("합계를 비교하여 단계를 높힐지 1로 돌릴지")
                                        print("합계 금액 : " + str(sum_price))
                                        self.insert_log(f"그룹 합계 금액 : {sum_price}\n\n")

                                        if next_value == 0 and t_check != "T":
                                            if sum_price > 0:
                                                # 수익 시 로직
                                                next_value = 0
                                                order_index = 1
                                                step_order = [0] * len(vbet_data)
                                                betting_price = base_price
                                                sum_price = 0

                                                # ".bet1" 요소들 찾기
                                                bet1_elements = page2.locator(".bet1")
                                                bet1_count = await bet1_elements.count()
                                                for i in range(bet1_count):
                                                    bet1_element = bet1_elements.nth(i)
                                                    await bet1_element.fill("")  # 기존 값을 지우기
                                                    await bet1_element.fill(str(base_price))  # base_price 입력

                                                # ".lbet1" 요소들 클릭하기
                                                lbet1_elements = page2.locator(".lbet1")
                                                lbet1_count = await lbet1_elements.count()
                                                for i in range(lbet1_count):
                                                    lbet1_element = lbet1_elements.nth(i)
                                                    await lbet1_element.click()

                                                # ".all-reset-input" 클릭하기
                                                await page2.locator(".all-reset-input").click()

                                                self.insert_log(
                                                    "=================================\n\n그룹 합계 수익, 전체 배팅 금액 "
                                                    f"{betting_price}원 배팅\n\n=================================\n\n")

                                            elif sum_price < 0:
                                                if lose:
                                                    # 패배 시 로직
                                                    next_value = 0
                                                    order_index = 1
                                                    step_order = [0] * len(vbet_data)
                                                    betting_price = base_price
                                                    sum_price = 0

                                                    # ".bet1" 요소들 찾기
                                                    bet1_elements = page2.locator(".bet1")
                                                    bet1_count = await bet1_elements.count()
                                                    for i in range(bet1_count):
                                                        bet1_element = bet1_elements.nth(i)
                                                        await bet1_element.fill("")  # 기존 값을 지우기
                                                        await bet1_element.fill(str(base_price))  # base_price 입력

                                                    # ".lbet1" 요소들 클릭하기
                                                    lbet1_elements = page2.locator(".lbet1")
                                                    lbet1_count = await lbet1_elements.count()
                                                    for i in range(lbet1_count):
                                                        lbet1_element = lbet1_elements.nth(i)
                                                        await lbet1_element.click()

                                                    # ".all-reset-input" 클릭하기
                                                    await page2.locator(".all-reset-input").click()

                                                    self.insert_log(
                                                        "=================================\n\n패배 전체 마틴단계 1로 복귀 "
                                                        f"{betting_price}원 배팅\n\n=================================\n\n")

                                                else:
                                                    # 손실 시 로직
                                                    step_order = [x + 1 for x in step_order]
                                                    print(abs(sum_price), base_price)
                                                    betting_price = abs(sum_price) + base_price

                                                    # 특정 ".bet{n}" 요소 찾기
                                                    bet_selector = f".vbet-container > div:nth-child(1) .bet{step_order[0] + 1}"
                                                    bet_element = page2.locator(bet_selector)
                                                    await bet_element.fill(str(betting_price))  # betting_price 입력

                                                    # ".lbet{n}" 요소들 클릭하기
                                                    lbet_selector = f".lbet{step_order[0] + 1}"
                                                    lbet_elements = page2.locator(lbet_selector)
                                                    lbet_count = await lbet_elements.count()
                                                    for i in range(lbet_count):
                                                        lbet_element = lbet_elements.nth(i)
                                                        await lbet_element.click()

                                                    # ".all-input" 클릭하기
                                                    await page2.locator(".all-input").click()

                                                    self.insert_log(
                                                        "=================================\n\n그룹 합계 손실, 손실 금액 : "
                                                        f"{sum_price} 전체 배팅 금액 {betting_price}원 배팅(손실금+베이스)\n\n"
                                                        "=================================\n\n")

                                        elif next_value != 0:
                                            if sum_price > 0:
                                                # 수익 시 로직
                                                next_value = 0
                                                order_index = 1
                                                step_order = [0] * len(vbet_data)
                                                betting_price = base_price
                                                sum_price = 0

                                                # ".bet1" 요소들 찾기
                                                bet1_elements = page2.locator(".bet1")
                                                bet1_count = await bet1_elements.count()
                                                for i in range(bet1_count):
                                                    bet1_element = bet1_elements.nth(i)
                                                    await bet1_element.fill("")  # 기존 값을 지우기
                                                    await bet1_element.fill(str(base_price))  # base_price 입력

                                                # ".lbet1" 요소들 클릭하기
                                                lbet1_elements = page2.locator(".lbet1")
                                                lbet1_count = await lbet1_elements.count()
                                                for i in range(lbet1_count):
                                                    lbet1_element = lbet1_elements.nth(i)
                                                    await lbet1_element.click()

                                                # ".all-reset-input" 클릭하기
                                                await page2.locator(".all-reset-input").click()

                                                # GUI 업데이트
                                                self.insert_log("=================================\n\n그룹 합계 수익, 전체 배팅 금액 "
                                                                f"{betting_price}원 배팅\n\n=================================\n\n")
                                    # 추가 로직 진행
                                    vbet_key = vbet_keys[next_value]
                                    martin_kind = vbet_data[vbet_key]['martin_kind']
                                    betting = vbet_data[vbet_key]['betting']
                                    current_position = vbet_key[-1]
                                    current_int = int(current_position)
                                    print(vbet_key)


                                    if vbet_amount == 1:
                                        selector = f".{vbet_key} .vbet-betting input.active"
                                        input_element = page2.locator(selector)

                                        # 요소가 로드될 때까지 대기
                                        await input_element.wait_for(state='visible', timeout=5000)

                                        # 'data-ml' 속성 값 가져오기
                                        data_ml = await input_element.get_attribute("data-ml")
                                        if data_ml is not None:
                                            step_order[next_value] = int(data_ml)
                                        else:
                                            print(f"'data-ml' 속성을 찾을 수 없습니다: {selector}")

                                    step_o = step_order[next_value]

                                    # Tkinter Entry 위젯 업데이트
                                    self.current_vmachine.delete(0, tk.END)
                                    self.current_vmachine.insert(tk.END, vbet_key)

                                    # vmachine-name 요소 클릭
                                    vmachine_selector = f".{vbet_key} .vmachine-name"
                                    vmachine_element = page2.locator(vmachine_selector)
                                    print("여기2")
                                    await vmachine_element.click()
                                    # 위 로직을 Playwright에 맞게 작성했으며, 더 많은 로직을 Playwright와 비동기 방식으로 구현할 수 있습니다.

                                    print("여기3")
                                    print(t_check)

                                    # TIE 조건 처리
                                    if t_check == "T":
                                        if lose:
                                            step_o = last_tie_step
                                            last_tie_step = 0
                                            lose = False
                                        else:
                                            tie_on = True
                                            print("step유지")
                                    else:
                                        if lose:
                                            step_o = 0

                                        print(f"스타트 :{start}")

                                        if start:
                                            step_o = 0
                                            print("여기4")

                                        # 재시작 조건 처리
                                    if re_start:
                                        re_start = False
                                    print("여기4")

                                        # Tkinter Entry 위젯 업데이트
                                    self.insert_log(f"{step_o + 1}마틴 진행\n")
                                    # entry_25.see(tk.END)  # Tkinter Text 위젯 사용 시 추가

                                    # 베팅 조건 처리
                                    if vbet_amount > 1:
                                        for i in range(20):
                                            if step_o == i:
                                                if selected_index == i + 1 and vbet_amount - 1 == next_value:
                                                    lose = True
                                                    last_tie_step = step
                                                    tie_on = True
                                                print("OO")
                                                await self.chip_selection(betting_price, c_res, step_o, round, "",
                                                                          vbet_key, new_page)
                                                break  # 일치하는 조건을 찾으면 반복문을 종료
                                    else:
                                        for i in range(20):
                                            if step_o == i:
                                                if selected_index == i + 1:
                                                    lose = True
                                                    last_tie_step = step
                                                    tie_on = True
                                                print("OO")
                                                await self.chip_selection(betting[martin_list[i]], c_res, step_o,
                                                                          round, "", vbet_key, new_page)
                                                break  # 일치하는 조건을 찾으면 반복문을 종료


                        else:
                            print("맞는패턴없음 PASS")
                            go_bet = False
                            no_bet_count += 1
                            if no_bet_count == 4:
                                await self.chip_selection(1000, 'P', -1, 0, "",
                                                          "", new_page)
                                no_bet_count = 0
                            autobet_called = False



                    except TimeoutError:
                        print("요소를 찾지 못해 타임아웃이 발생했습니다.")
                    except Exception as e:
                        print(f"오류 발생 autobet: {e}")
    except Exception as e:
        print(f"게임 프레임 찾기 오류: {e}")
        return None

def show_next_order():
    global order_index

    # 현재 order 값 가져오기
    current_order = order[order_index]

    # order 길이가 1보다 클 때만 order_index 증가
    if len(order) > 1:
        # order_index 증가 (순환)
        order_index = (order_index + 1) % len(order)

    return current_order


# Playwright 및 가격 가져오기 함수
async def get_price(new_page, update_callback):
    global price_running
    previous_price_number = 0  # 이전 가격을 저장하는 변수 (price_number2에 해당)

    while price_running:
        try:
            games_container = await new_page.wait_for_selector('.games-container', timeout=15000)
            if games_container:
                iframe_element = await games_container.wait_for_selector('iframe', timeout=10000)
                if iframe_element:
                    iframe = await iframe_element.content_frame()
                else:
                    print("iframe_element를 찾을 수 없습니다.")
                    return
            else:
                print(".games-container 요소를 찾을 수 없습니다.")
                return
        except PlaywrightTimeoutError:
            print("게임 컨테이너를 찾는 데 타임아웃이 발생했습니다.")
            return
        except Exception as e:
            print(f"게임 컨테이너를 찾는 중 오류 발생: {e}")
            traceback.print_exc()
            return

        try:
            # 최대 5초 동안 .amount--f8dd5 span 요소가 나타날 때까지 대기
            element = await iframe.wait_for_selector('.amount--f8dd5 span', timeout=5000)
            current_price = await element.inner_text()
            current_price = current_price.strip()
            price_number = re.sub(r'[^0-9.]', '', current_price)

            # 이전 가격이 설정되지 않은 경우 초기화
            if previous_price_number == 0:
                previous_price_number = float(price_number)

            cal = int(float(price_number)) - int(float(previous_price_number))
            positive_cal = abs(cal)

            # 이전 가격 업데이트
            previous_price_number = float(price_number)

            # GUI 업데이트를 위한 콜백 호출
            update_callback(price_number, cal)

        except PlaywrightTimeoutError:
            # 요소를 찾지 못한 경우 그냥 넘어감
            insert_log("Element '.amount--f8dd5 span' not found. Passing...")
        except Exception as e:
            insert_log(f"Error in get_price: {e}")

        await asyncio.sleep(1)


# GUI 업데이트 함수
def update_entries(price_number, cal):
    # tkinter는 메인 스레드에서만 업데이트 가능하므로 after를 사용
    def _update():
        entry_2.config(state='normal')
        entry_2.delete(0, tk.END)
        entry_2.insert(0, str(cal))
        entry_2.config(state='readonly')

        entry_1.config(state='normal')
        entry_1.delete(0, tk.END)
        entry_1.insert(0, str(price_number))
        entry_1.config(state='readonly')

    root.after(0, _update)


async def get_r_title(page):
    try:
        # '.tableName--ed38c' 클래스 이름을 가진 요소 선택
        element = page.locator('.tableName--ed38c')

        # 요소가 존재하는지 확인
        if await element.count() > 0:
            # 요소의 inner_text 가져오기 (자동으로 공백을 정리함)
            r_title = await element.inner_text()

            # 추가로 strip()을 적용할 필요가 없을 수 있지만, 확실히 하기 위해 사용
            r_title = r_title.strip()

            return r_title
        else:
            print("'.tableName--ed38c' 요소를 찾을 수 없습니다.")
            return None
    except Exception as e:
        print(f"오류 발생: {e}")
        return None

def start_asyncio_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def login():
    global password
    username = entry_username.get()
    password = entry_password.get()
    url = "http://pattern2024.com/auto_login.php"
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

def find_chrome_executable():
    system = platform.system()
    chrome_executable = None

    if system != "Windows":
        print("이 함수는 Windows 시스템에서만 작동합니다.")
        return None

    # Windows에서 Chrome의 일반적인 설치 경로
    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            chrome_executable = path
            print(f"Chrome이 발견되었습니다: {chrome_executable}")
            return chrome_executable

    # 레지스트리를 통해 Chrome 경로 찾기
    try:
        import winreg
    except ImportError:
        print("winreg 모듈을 불러올 수 없습니다.")
        return None

    try:
        # 64비트 레지스트리 키 경로
        reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
            chrome_executable, _ = winreg.QueryValueEx(key, "")
            if os.path.exists(chrome_executable):
                print(f"레지스트리를 통해 Chrome이 발견되었습니다: {chrome_executable}")
                return chrome_executable
    except FileNotFoundError:
        print("레지스트리에서 Chrome 경로를 찾을 수 없습니다.")
    except Exception as e:
        print(f"레지스트리 조회 중 오류 발생: {e}")

    # 시스템 PATH에서 Chrome 찾기
    chrome_in_path = shutil.which("chrome")
    if chrome_in_path and os.path.exists(chrome_in_path):
        chrome_executable = chrome_in_path
        print(f"시스템 PATH에서 Chrome이 발견되었습니다: {chrome_executable}")
        return chrome_executable

    print("Chrome 실행 파일을 찾을 수 없습니다.")
    return None

# 메인 함수
def main():
    if not serial_number == "MASTER":
        create_login_window()
    loop = asyncio.new_event_loop()
    t = threading.Thread(target=start_asyncio_loop, args=(loop,), daemon=True)
    t.start()

    app = Application(loop)
    app.mainloop()


if __name__ == "__main__":
    main()
