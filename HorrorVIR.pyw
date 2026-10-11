import os
import json
import random
import socket
import time
import threading
import tkinter as tk
import ctypes
import getpass
import subprocess

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import win32gui
    import win32con
except ImportError:
    win32gui = None
    win32con = None


GAME_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(
    GAME_DIR,
    "config.yml"
)

SAVE_FILE = os.path.join(
    GAME_DIR,
    "spielstand.json"
)

WALLPAPER_DIR = os.path.join(
    GAME_DIR,
    "wallpapers"
)

CAMERA_FILE = os.path.join(
    WALLPAPER_DIR,
    "camera_capture.jpg"
)

HORROR_VIDEO = os.path.join(
    WALLPAPER_DIR,
    "horror.mp4"
)


DEFAULT_CONFIG = {
    "wallpaper": True,
    "jumpscares": True,
    "system_errors": True,
    "red_cmds": True,
    "screen_flicker": True,
    "camera": False,
    "ip_display": True,
    "autostart": False,
    "second_monitor": True,
    "horror_video": True
}


DEFAULT_SAVE = {
    "chapter": 1,
    "fear": 0,
    "events": 0,
    "errors": 0,
    "cmds": 0,
    "jumpscares": 0,
    "camera_used": False,
    "second_monitor_events": 0,
    "video_events": 0,
    "phase": 1
}


def save_config(config):
    try:
        with open(
            CONFIG_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            for key, value in config.items():
                file.write(
                    key
                    + ": "
                    + str(value).lower()
                    + "\n"
                )
    except Exception:
        pass


def load_config():
    if not os.path.exists(CONFIG_FILE):
        config = DEFAULT_CONFIG.copy()
        save_config(config)
        return config

    config = DEFAULT_CONFIG.copy()

    try:
        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            for line in file:

                if ":" not in line:
                    continue

                key, value = line.strip().split(
                    ":",
                    1
                )

                key = key.strip()
                value = value.strip().lower()

                if key in config:
                    config[key] = value == "true"

    except Exception:
        save_config(config)

    return config


def save_game(save):
    try:
        with open(
            SAVE_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                save,
                file,
                indent=4
            )
    except Exception:
        pass


def load_game():
    if not os.path.exists(SAVE_FILE):
        save = DEFAULT_SAVE.copy()
        save_game(save)
        return save

    try:
        with open(
            SAVE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            save = json.load(file)

        for key, value in DEFAULT_SAVE.items():
            if key not in save:
                save[key] = value

        return save

    except Exception:
        save = DEFAULT_SAVE.copy()
        save_game(save)
        return save


def get_username():
    try:
        return getpass.getuser()
    except Exception:
        return "UNBEKANNT"


def get_local_ip():
    try:
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        sock.connect(
            ("8.8.8.8", 80)
        )

        ip = sock.getsockname()[0]

        sock.close()

        return ip

    except Exception:
        try:
            return socket.gethostbyname(
                socket.gethostname()
            )
        except Exception:
            return "UNBEKANNT"


def set_wallpaper(image_path):
    if not os.path.exists(image_path):
        return False

    try:
        ctypes.windll.user32.SystemParametersInfoW(
            20,
            0,
            image_path,
            3
        )
        return True
    except Exception:
        return False


def get_horror_images():
    os.makedirs(
        WALLPAPER_DIR,
        exist_ok=True
    )

    images = []

    for filename in os.listdir(
        WALLPAPER_DIR
    ):

        if filename.lower().endswith(
            (
                ".jpg",
                ".jpeg",
                ".png",
                ".bmp"
            )
        ):

            images.append(
                os.path.join(
                    WALLPAPER_DIR,
                    filename
                )
            )

    return images


def enable_autostart():
    try:
        startup = os.path.join(
            os.environ["APPDATA"],
            "Microsoft",
            "Windows",
            "Start Menu",
            "Programs",
            "Startup"
        )

        os.makedirs(
            startup,
            exist_ok=True
        )

        shortcut = os.path.join(
            startup,
            "Aaronia Horror.lnk"
        )

        python_path = os.path.abspath(
            os.sys.executable
        )

        script_path = os.path.abspath(
            __file__
        )

        command = (
            'powershell.exe '
            '-WindowStyle Hidden '
            '-Command '
            '"$ws=New-Object -ComObject WScript.Shell;'
            '$s=$ws.CreateShortcut('
            "'" + shortcut.replace(
                "'",
                "''"
            ) + "'"
            ');'
            '$s.TargetPath='
            "'" + python_path.replace(
                "'",
                "''"
            ) + "';"
            '$s.Arguments='
            "'" + '"' + script_path.replace(
                "'",
                "''"
            ) + '"' + "';"
            '$s.WorkingDirectory='
            "'" + GAME_DIR.replace(
                "'",
                "''"
            ) + "';"
            '$s.Save()"'
        )

        subprocess.run(
            command,
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

    except Exception:
        pass


def get_monitors():
    monitors = []

    if os.name != "nt":
        return monitors

    user32 = ctypes.windll.user32

    MONITORENUMPROC = ctypes.WINFUNCTYPE(
        ctypes.c_int,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.POINTER(
            ctypes.c_long * 4
        ),
        ctypes.c_void_p
    )

    def callback(
        hmonitor,
        hdc,
        rect,
        data
    ):

        left = rect.contents[0]
        top = rect.contents[1]
        right = rect.contents[2]
        bottom = rect.contents[3]

        monitors.append(
            (
                left,
                top,
                right,
                bottom
            )
        )

        return 1

    callback_function = MONITORENUMPROC(
        callback
    )

    user32.EnumDisplayMonitors(
        None,
        None,
        callback_function,
        0
    )

    return monitors


def first_start():

    if os.path.exists(CONFIG_FILE):
        return

    window = tk.Tk()

    window.title(
        "AARONIA HORROR - ERSTER START"
    )

    window.geometry(
        "800x820"
    )

    window.configure(
        bg="black"
    )

    window.resizable(
        False,
        False
    )

    tk.Label(
        window,
        text="AARONIA HORROR",
        bg="black",
        fg="red",
        font=(
            "Consolas",
            32,
            "bold"
        )
    ).pack(
        pady=25
    )

    tk.Label(
        window,
        text="SYSTEM-BERECHTIGUNGEN",
        bg="black",
        fg="white",
        font=(
            "Consolas",
            17,
            "bold"
        )
    ).pack()

    tk.Label(
        window,
        text="BENUTZER: " + get_username(),
        bg="black",
        fg="#888888",
        font=(
            "Consolas",
            11
        )
    ).pack(
        pady=8
    )

    variables = {}

    options = [
        (
            "wallpaper",
            "Horror-Bilder als Windows-Hintergrund"
        ),
        (
            "jumpscares",
            "Jumpscares"
        ),
        (
            "system_errors",
            "Fake-Systemfehler"
        ),
        (
            "red_cmds",
            "Rote Horror-CMD-Fenster"
        ),
        (
            "screen_flicker",
            "Bildschirm-Flackern"
        ),
        (
            "camera",
            "Kamera verwenden"
        ),
        (
            "ip_display",
            "Lokale IP-Adresse anzeigen"
        ),
        (
            "autostart",
            "Bei Windows-Anmeldung automatisch starten"
        ),
        (
            "second_monitor",
            "Zweiten Monitor für Horror-Effekte verwenden"
        ),
        (
            "horror_video",
            "horror.mp4 alle 10 Sekunden abspielen"
        )
    ]

    frame = tk.Frame(
        window,
        bg="black"
    )

    frame.pack(
        pady=15
    )

    for key, text in options:

        variable = tk.BooleanVar(
            value=DEFAULT_CONFIG[key]
        )

        variables[key] = variable

        tk.Checkbutton(
            frame,
            text=text,
            variable=variable,
            bg="black",
            fg="white",
            selectcolor="#330000",
            activebackground="black",
            activeforeground="red",
            font=(
                "Consolas",
                10
            ),
            width=58,
            anchor="w"
        ).pack(
            pady=4
        )

    tk.Label(
        window,
        text=(
            "KAMERA und AUTOSTART sind standardmäßig AUS."
        ),
        bg="black",
        fg="#aa0000",
        font=(
            "Consolas",
            9
        )
    ).pack(
        pady=10
    )

    def start_game():

        config = {}

        for key in DEFAULT_CONFIG:
            config[key] = variables[key].get()

        save_config(config)

        if config["autostart"]:
            enable_autostart()

        window.destroy()

    tk.Button(
        window,
        text="HORROR STARTEN",
        command=start_game,
        bg="#550000",
        fg="white",
        activebackground="#990000",
        activeforeground="white",
        font=(
            "Consolas",
            15,
            "bold"
        ),
        width=25,
        height=2,
        relief="flat"
    ).pack(
        pady=15
    )

    window.mainloop()


class HorrorGame:

    def __init__(self):

        self.config = load_config()
        self.save = load_game()

        self.running = True
        self.hidden = False
        self.camera_done = False
        self.start_time = time.time()
        self.open_windows = []

        self.root = tk.Tk()

        self.root.title(
            "AARONIA HORROR"
        )

        self.root.geometry(
            "1000x650"
        )

        self.root.configure(
            bg="black"
        )

        self.root.resizable(
            False,
            False
        )

        self.create_interface()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.fake_exit
        )

        self.root.after(
            800,
            self.random_event
        )

        if self.config["wallpaper"]:
            self.root.after(
                1000,
                self.wallpaper_loop
            )

        if self.config["camera"]:
            self.root.after(
                5000,
                self.camera_event
            )

        if self.config["horror_video"]:
            self.root.after(
                10000,
                self.video_event
            )

        if self.config["second_monitor"]:
            self.root.after(
                5000,
                self.second_monitor_event
            )

        self.root.after(
            5000,
            self.escalation_loop
        )

    def create_interface(self):

        top = tk.Frame(
            self.root,
            bg="#080808",
            height=45
        )

        top.pack(
            fill="x"
        )

        top.pack_propagate(
            False
        )

        tk.Label(
            top,
            text="AARONIA HORROR",
            bg="#080808",
            fg="#990000",
            font=(
                "Consolas",
                13,
                "bold"
            )
        ).pack(
            side="left",
            padx=15
        )

        self.exit_button = tk.Button(
            top,
            text="EXIT",
            command=self.fake_exit,
            bg="#300000",
            fg="white",
            activebackground="#700000",
            activeforeground="white",
            relief="flat",
            font=(
                "Consolas",
                10,
                "bold"
            ),
            width=10
        )

        self.exit_button.pack(
            side="right",
            padx=10,
            pady=8
        )

        self.title_label = tk.Label(
            self.root,
            text="AARONIA",
            bg="black",
            fg="#660000",
            font=(
                "Consolas",
                55,
                "bold"
            )
        )

        self.title_label.pack(
            pady=(80, 10)
        )

        self.user_label = tk.Label(
            self.root,
            text="BENUTZER: "
            + get_username(),
            bg="black",
            fg="#333333",
            font=(
                "Consolas",
                10
            )
        )

        self.user_label.pack(
            pady=5
        )

        self.status = tk.Label(
            self.root,
            text="HORROR-MODUS AKTIV",
            bg="black",
            fg="#777777",
            font=(
                "Consolas",
                16
            )
        )

        self.status.pack(
            pady=8
        )

        self.phase_label = tk.Label(
            self.root,
            text="PHASE 1",
            bg="black",
            fg="#440000",
            font=(
                "Consolas",
                12,
                "bold"
            )
        )

        self.phase_label.pack(
            pady=5
        )

        self.fear_label = tk.Label(
            self.root,
            text="FEAR: "
            + str(
                self.save["fear"]
            ),
            bg="black",
            fg="#880000",
            font=(
                "Consolas",
                11
            )
        )

        self.fear_label.pack()

        if self.config["ip_display"]:

            self.ip_label = tk.Label(
                self.root,
                text="LOCAL IP: "
                + get_local_ip(),
                bg="black",
                fg="#333333",
                font=(
                    "Consolas",
                    10
                )
            )

            self.ip_label.pack(
                pady=18
            )

    def update_fear(self):

        self.fear_label.config(
            text="FEAR: "
            + str(
                self.save["fear"]
            )
        )

    def fake_exit(self):

        self.save["fear"] += 10

        save_game(
            self.save
        )

        self.status.config(
            text="EXIT DENIED.",
            fg="red"
        )

        self.exit_button.config(
            text="NO ESCAPE"
        )

        self.update_fear()

        self.root.after(
            700,
            self.hide_game
        )

    def hide_game(self):

        self.hidden = True

        self.root.withdraw()

    def escalation_loop(self):

        if not self.running:
            return

        elapsed = time.time() - self.start_time

        if elapsed < 60:
            phase = 1
        elif elapsed < 120:
            phase = 2
        elif elapsed < 180:
            phase = 3
        elif elapsed < 240:
            phase = 4
        else:
            phase = 5

        self.save["phase"] = phase

        self.phase_label.config(
            text="PHASE "
            + str(phase)
        )

        if phase >= 2:
            self.save["fear"] += 2

        if phase >= 3:
            self.save["fear"] += 3

        if phase >= 4:
            self.save["fear"] += 4

        if phase >= 5:
            self.save["fear"] += 5

        save_game(
            self.save
        )

        self.update_fear()

        self.root.after(
            5000,
            self.escalation_loop
        )

    def random_event(self):

        if not self.running:
            return

        phase = self.save["phase"]

        events = [
            "message",
            "message",
            "error",
            "cmd",
            "flicker"
        ]

        if phase >= 2:

            events += [
                "message",
                "error",
                "cmd",
                "cmd",
                "jumpscare"
            ]

        if phase >= 3:

            events += [
                "jumpscare",
                "jumpscare",
                "cmd",
                "cmd",
                "error"
            ]

        if phase >= 4:

            events += [
                "jumpscare",
                "jumpscare",
                "jumpscare",
                "cmd",
                "cmd",
                "flicker"
            ]

        if phase >= 5:

            events += [
                "jumpscare",
                "jumpscare",
                "cmd",
                "cmd",
                "error",
                "error",
                "flicker",
                "flicker"
            ]

        event = random.choice(
            events
        )

        if event == "message":
            self.message_event()

        elif event == "error":
            self.error_event()

        elif event == "cmd":
            self.cmd_event()

        elif event == "jumpscare":
            self.jumpscare_event()

        elif event == "flicker":
            self.flicker_event()

        self.save["events"] += 1

        save_game(
            self.save
        )

        self.update_fear()

        if phase == 1:
            delay = random.randint(
                900,
                2200
            )

        elif phase == 2:
            delay = random.randint(
                600,
                1700
            )

        elif phase == 3:
            delay = random.randint(
                450,
                1300
            )

        elif phase == 4:
            delay = random.randint(
                300,
                900
            )

        else:
            delay = random.randint(
                180,
                700
            )

        self.root.after(
            delay,
            self.random_event
        )

    def message_event(self):

        messages = [
            "Du bist nicht allein.",
            "Hast du das gehört?",
            "Schau nicht hinter dich.",
            "Ich kann dich sehen.",
            "Warum bist du noch hier?",
            "Das Spiel beobachtet dich.",
            "Etwas ist hinter dir.",
            "Nicht umdrehen.",
            "Ich bin noch hier.",
            "Du solltest aufhören.",
            "Hast du gerade die Tür gehört?",
            "Warum bewegst du deine Maus?",
            "Ich weiß, dass du da bist.",
            "Das war nicht deine Maus.",
            "Du hast gerade etwas gesehen.",
            "Ich kenne diesen Computer.",
            "Warum hast du mich gestartet?",
            "DEIN SYSTEM IST NICHT ALLEIN",
            "HÖR AUF ZU SPIELEN",
            "ICH WARTE"
        ]

        self.status.config(
            text=random.choice(
                messages
            ),
            fg="#aa0000"
        )

        self.save["fear"] += random.randint(
            2,
            7
        )

        save_game(
            self.save
        )

        self.root.after(
            random.randint(
                500,
                1600
            ),
            lambda: self.status.config(
                text="HORROR-MODUS AKTIV",
                fg="#777777"
            )
        )

    def error_event(self):

        self.save["errors"] += 1
        self.save["fear"] += random.randint(
            3,
            9
        )

        save_game(
            self.save
        )

        window = tk.Toplevel(
            self.root
        )

        self.open_windows.append(
            window
        )

        window.title(
            "SYSTEM ERROR"
        )

        width = random.randint(
            430,
            600
        )

        height = random.randint(
            230,
            330
        )

        x = random.randint(
            100,
            900
        )

        y = random.randint(
            80,
            500
        )

        window.geometry(
            str(width)
            + "x"
            + str(height)
            + "+"
            + str(x)
            + "+"
            + str(y)
        )

        window.configure(
            bg="#050505"
        )

        window.attributes(
            "-topmost",
            True
        )

        messages = [
            "CRITICAL SYSTEM ERROR",
            "UNKNOWN PROCESS DETECTED",
            "SYSTEM INTEGRITY FAILED",
            "UNKNOWN ENTITY DETECTED",
            "MEMORY CORRUPTION",
            "ACCESS DENIED",
            "UNKNOWN PRESENCE",
            "SECURITY FAILURE",
            "SYSTEM IS NOT SAFE",
            "HORROR PROCESS ACTIVE",
            "USER DETECTED"
        ]

        tk.Label(
            window,
            text="SYSTEM ERROR",
            bg="#050505",
            fg="red",
            font=(
                "Consolas",
                22,
                "bold"
            )
        ).pack(
            pady=25
        )

        tk.Label(
            window,
            text=random.choice(
                messages
            ),
            bg="#050505",
            fg="#ff3333",
            font=(
                "Consolas",
                11
            )
        ).pack()

        tk.Label(
            window,
            text="ERROR 0x"
            + str(
                random.randint(
                    100000,
                    999999
                )
            ),
            bg="#050505",
            fg="#777777",
            font=(
                "Consolas",
                9
            )
        ).pack(
            pady=15
        )

        window.after(
            random.randint(
                900,
                2500
            ),
            lambda: self.destroy_window(
                window
            )
        )

    def destroy_window(
        self,
        window
    ):

        try:
            window.destroy()
        except Exception:
            pass

    def cmd_event(self):

        self.save["cmds"] += 1

        self.save["fear"] += random.randint(
            4,
            12
        )

        save_game(
            self.save
        )

        messages = [
            "I CAN SEE YOU",
            "DON'T CLOSE THE GAME",
            "RUN",
            "LOOK BEHIND YOU",
            "SYSTEM COMPROMISED",
            "THE GAME KNOWS",
            "ERROR ERROR ERROR",
            "YOU SHOULD NOT BE HERE",
            "WHY ARE YOU STILL PLAYING?",
            "UNKNOWN PRESENCE",
            "CONNECTION ESTABLISHED",
            "USER DETECTED",
            "HORROR PROTOCOL ACTIVE",
            "DO NOT TURN AROUND",
            "WE ARE WATCHING"
        ]

        text = random.choice(
            messages
        )

        title = (
            "AARONIA_HORROR_"
            + str(
                random.randint(
                    1000,
                    9999
                )
            )
        )

        command = (
            "color 4F & "
            "title "
            + title
            + " & "
            "echo. & "
            "echo ======================================== & "
            "echo       AARONIA HORROR SYSTEM & "
            "echo ======================================== & "
            "echo. & "
            "echo "
            + text
            + " & "
            "echo. & "
            "echo USER: "
            + get_username()
            + " & "
            "echo ERROR ID: "
            + str(
                random.randint(
                    1000,
                    9999
                )
            )
            + " & "
            "echo. & "
            "echo HORROR EVENT DETECTED & "
            "echo. & "
            "timeout /t 5 >nul"
        )

        try:

            subprocess.Popen(
                [
                    "cmd.exe",
                    "/c",
                    command
                ],
                creationflags=(
                    subprocess.CREATE_NEW_CONSOLE
                )
            )

            if win32gui is not None:

                threading.Thread(
                    target=self.shake_cmd,
                    args=(title,),
                    daemon=True
                ).start()

        except Exception:
            pass

    def find_window(
        self,
        title
    ):

        if win32gui is None:
            return None

        result = []

        def callback(
            hwnd,
            extra
        ):

            try:

                window_title = (
                    win32gui.GetWindowText(
                        hwnd
                    )
                )

                if title in window_title:
                    result.append(
                        hwnd
                    )

            except Exception:
                pass

        try:

            win32gui.EnumWindows(
                callback,
                None
            )

        except Exception:
            return None

        if result:
            return result[0]

        return None

    def shake_cmd(
        self,
        title
    ):

        hwnd = None

        for _ in range(50):

            hwnd = self.find_window(
                title
            )

            if hwnd:
                break

            time.sleep(
                0.08
            )

        if not hwnd:
            return

        try:

            rect = (
                win32gui.GetWindowRect(
                    hwnd
                )
            )

            original_x = rect[0]
            original_y = rect[1]

            phase = self.save["phase"]

            if phase == 1:
                shakes = 35
                strength = 10

            elif phase == 2:
                shakes = 50
                strength = 15

            elif phase == 3:
                shakes = 65
                strength = 20

            elif phase == 4:
                shakes = 80
                strength = 25

            else:
                shakes = 100
                strength = 32

            for _ in range(
                shakes
            ):

                offset_x = random.randint(
                    -strength,
                    strength
                )

                offset_y = random.randint(
                    -strength,
                    strength
                )

                win32gui.SetWindowPos(
                    hwnd,
                    win32con.HWND_TOP,
                    original_x + offset_x,
                    original_y + offset_y,
                    0,
                    0,
                    win32con.SWP_NOSIZE
                )

                time.sleep(
                    random.uniform(
                        0.015,
                        0.045
                    )
                )

            win32gui.SetWindowPos(
                hwnd,
                win32con.HWND_TOP,
                original_x,
                original_y,
                0,
                0,
                win32con.SWP_NOSIZE
            )

        except Exception:
            pass

    def jumpscare_event(self):

        self.save["jumpscares"] += 1

        self.save["fear"] += random.randint(
            10,
            25
        )

        save_game(
            self.save
        )

        monitors = get_monitors()

        window = tk.Toplevel(
            self.root
        )

        window.title(
            ""
        )

        window.attributes(
            "-topmost",
            True
        )

        window.configure(
            bg="black"
        )

        if monitors:

            monitor = random.choice(
                monitors
            )

            left = monitor[0]
            top = monitor[1]
            width = monitor[2] - monitor[0]
            height = monitor[3] - monitor[1]

            w = min(
                900,
                width
            )

            h = min(
                550,
                height
            )

            x = left + (
                width - w
            ) // 2

            y = top + (
                height - h
            ) // 2

            window.geometry(
                str(w)
                + "x"
                + str(h)
                + "+"
                + str(x)
                + "+"
                + str(y)
            )

        else:

            window.geometry(
                "800x500"
            )

        label = tk.Label(
            window,
            text=random.choice(
                [
                    "I SEE YOU",
                    "RUN",
                    "BEHIND YOU",
                    "DON'T LOOK AWAY",
                    "WAKE UP",
                    "YOU ARE NOT ALONE",
                    "LOOK BEHIND YOU",
                    "DON'T CLOSE YOUR EYES",
                    "I KNOW YOU ARE THERE",
                    "TURN AROUND"
                ]
            ),
            bg="black",
            fg="red",
            font=(
                "Arial",
                45,
                "bold"
            )
        )

        label.pack(
            expand=True
        )

        def flash(
            number
        ):

            if number >= 24:

                self.destroy_window(
                    window
                )

                return

            if number % 2 == 0:

                window.configure(
                    bg="#770000"
                )

                label.configure(
                    bg="#770000",
                    fg="white"
                )

            else:

                window.configure(
                    bg="black"
                )

                label.configure(
                    bg="black",
                    fg="red"
                )

            window.after(
                55,
                lambda: flash(
                    number + 1
                )
            )

        flash(0)

    def flicker_event(self):

        colors = [
            "black",
            "#220000",
            "black",
            "#440000",
            "black",
            "#770000",
            "black",
            "#330000",
            "black"
        ]

        def change(
            number
        ):

            if number >= len(
                colors
            ):
                return

            color = colors[number]

            widgets = [
                self.root,
                self.title_label,
                self.user_label,
                self.status,
                self.phase_label,
                self.fear_label
            ]

            if self.config["ip_display"]:
                widgets.append(
                    self.ip_label
                )

            for widget in widgets:

                try:
                    widget.configure(
                        bg=color
                    )
                except Exception:
                    pass

            self.root.after(
                45,
                lambda: change(
                    number + 1
                )
            )

        change(0)

    def wallpaper_loop(self):

        if not self.running:
            return

        images = get_horror_images()

        normal_images = [
            image
            for image in images
            if os.path.abspath(
                image
            ) != os.path.abspath(
                CAMERA_FILE
            )
        ]

        if normal_images:

            set_wallpaper(
                random.choice(
                    normal_images
                )
            )

        self.root.after(
            1000,
            self.wallpaper_loop
        )

    def second_monitor_event(self):

        if not self.running:
            return

        monitors = get_monitors()

        if len(monitors) < 2:

            self.root.after(
                random.randint(
                    4000,
                    9000
                ),
                self.second_monitor_event
            )

            return

        monitor = random.choice(
            monitors[1:]
        )

        left = monitor[0]
        top = monitor[1]
        width = monitor[2] - monitor[0]
        height = monitor[3] - monitor[1]

        window_width = min(
            700,
            width
        )

        window_height = min(
            430,
            height
        )

        x = left + (
            width - window_width
        ) // 2

        y = top + (
            height - window_height
        ) // 2

        window = tk.Toplevel(
            self.root
        )

        window.title(
            "UNKNOWN SYSTEM"
        )

        window.geometry(
            str(window_width)
            + "x"
            + str(window_height)
            + "+"
            + str(x)
            + "+"
            + str(y)
        )

        window.configure(
            bg="#030303"
        )

        window.attributes(
            "-topmost",
            True
        )

        horror_messages = [
            (
                "BITCOIN SYSTEM",
                "999 BTC WAITING",
                "CLAIM NOW"
            ),
            (
                "SYSTEM BREACH",
                "SECOND MONITOR INFECTED",
                "DO NOT CLOSE"
            ),
            (
                "UNKNOWN USER",
                "WE FOUND YOU",
                "RUN"
            ),
            (
                "HORROR PROTOCOL",
                "SIGNAL DETECTED",
                "LOOK BEHIND YOU"
            )
        ]

        title_text, main_text, button_text = (
            random.choice(
                horror_messages
            )
        )

        tk.Label(
            window,
            text=title_text,
            bg="#030303",
            fg="#ff2222",
            font=(
                "Consolas",
                27,
                "bold"
            )
        ).pack(
            pady=30
        )

        tk.Label(
            window,
            text=main_text,
            bg="#030303",
            fg="white",
            font=(
                "Consolas",
                19,
                "bold"
            )
        ).pack(
            pady=10
        )

        tk.Label(
            window,
            text=button_text,
            bg="#550000",
            fg="white",
            font=(
                "Consolas",
                18,
                "bold"
            ),
            width=20
        ).pack(
            pady=20
        )

        tk.Label(
            window,
            text="FICTIONAL HORROR EVENT",
            bg="#030303",
            fg="#444444",
            font=(
                "Consolas",
                9
            )
        ).pack()

        self.save[
            "second_monitor_events"
        ] += 1

        self.save["fear"] += 12

        save_game(
            self.save
        )

        window.after(
            random.randint(
                3500,
                7000
            ),
            lambda: self.destroy_window(
                window
            )
        )

        self.root.after(
            random.randint(
                5000,
                11000
            ),
            self.second_monitor_event
        )

    def video_event(self):

        if not self.running:
            return

        if not os.path.exists(
            HORROR_VIDEO
        ):

            self.root.after(
                10000,
                self.video_event
            )

            return

        self.save[
            "video_events"
        ] += 1

        self.save["fear"] += 15

        save_game(
            self.save
        )

        thread = threading.Thread(
            target=self.play_horror_video,
            daemon=True
        )

        thread.start()

        self.root.after(
            10000,
            self.video_event
        )

    def play_horror_video(self):

        if cv2 is None:
            return

        capture = None
        window_name = (
            "AARONIA HORROR VIDEO"
        )

        try:

            capture = cv2.VideoCapture(
                HORROR_VIDEO
            )

            if not capture.isOpened():
                return

            cv2.namedWindow(
                window_name,
                cv2.WINDOW_NORMAL
            )

            cv2.setWindowProperty(
                window_name,
                cv2.WND_PROP_TOPMOST,
                1
            )

            monitors = get_monitors()

            if monitors:

                monitor = random.choice(
                    monitors
                )

                left = monitor[0]
                top = monitor[1]

                width = monitor[2] - monitor[0]
                height = monitor[3] - monitor[1]

                video_width = min(
                    900,
                    width
                )

                video_height = min(
                    600,
                    height
                )

                cv2.resizeWindow(
                    window_name,
                    video_width,
                    video_height
                )

                cv2.moveWindow(
                    window_name,
                    left + (
                        width - video_width
                    ) // 2,
                    top + (
                        height - video_height
                    ) // 2
                )

            while self.running:

                success, frame = (
                    capture.read()
                )

                if not success:
                    break

                cv2.imshow(
                    window_name,
                    frame
                )

                key = cv2.waitKey(
                    20
                )

                if key == 27:
                    break

            cv2.destroyWindow(
                window_name
            )

        except Exception:
            pass

        finally:

            if capture is not None:
                capture.release()

            try:
                cv2.destroyAllWindows()
            except Exception:
                pass

    def camera_event(self):

        if self.camera_done:
            return

        self.camera_done = True

        if not self.config["camera"]:
            return

        if cv2 is None:

            self.status.config(
                text="OPENCV NICHT INSTALLIERT.",
                fg="red"
            )

            return

        thread = threading.Thread(
            target=self.capture_camera,
            daemon=True
        )

        thread.start()

    def capture_camera(self):

        camera = None

        try:

            camera = cv2.VideoCapture(
                0
            )

            if not camera.isOpened():

                self.root.after(
                    0,
                    lambda: self.status.config(
                        text="KAMERA NICHT VERFÜGBAR.",
                        fg="red"
                    )
                )

                return

            start_time = time.time()

            frame = None

            while (
                time.time()
                - start_time
                < 2
            ):

                success, current_frame = (
                    camera.read()
                )

                if success:
                    frame = current_frame

                time.sleep(
                    0.05
                )

            if frame is None:
                return

            os.makedirs(
                WALLPAPER_DIR,
                exist_ok=True
            )

            cv2.imwrite(
                CAMERA_FILE,
                frame
            )

            self.save[
                "camera_used"
            ] = True

            self.save[
                "fear"
            ] += 15

            save_game(
                self.save
            )

            self.root.after(
                0,
                self.camera_wallpaper
            )

        except Exception:

            self.root.after(
                0,
                lambda: self.status.config(
                    text="KAMERA-FEHLER.",
                    fg="red"
                )
            )

        finally:

            if camera is not None:
                camera.release()

    def camera_wallpaper(self):

        if not os.path.exists(
            CAMERA_FILE
        ):
            return

        self.status.config(
            text="DEIN BILD...",
            fg="red"
        )

        set_wallpaper(
            CAMERA_FILE
        )

        self.update_fear()

        self.root.after(
            2000,
            self.restore_horror_wallpaper
        )

    def restore_horror_wallpaper(self):

        images = get_horror_images()

        normal_images = [
            image
            for image in images
            if os.path.abspath(
                image
            ) != os.path.abspath(
                CAMERA_FILE
            )
        ]

        if normal_images:

            set_wallpaper(
                random.choice(
                    normal_images
                )
            )

        self.status.config(
            text="HORROR-MODUS AKTIV",
            fg="#777777"
        )

    def run(self):

        self.root.mainloop()


def main():

    if os.name != "nt":

        print(
            "Dieses Spiel benötigt Windows."
        )

        return

    os.makedirs(
        WALLPAPER_DIR,
        exist_ok=True
    )

    first_start()

    config = load_config()

    if config.get(
        "autostart",
        False
    ):

        enable_autostart()

    game = HorrorGame()

    game.run()


if __name__ == "__main__":
    main()