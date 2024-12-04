# Created by MajorK https://github.com/SNP-MajorK/ED-DataCollector

import fnmatch
import glob
import io
import queue
import random
import re
import ssl
import threading
import time as t
import urllib.request
import webbrowser
import customtkinter
import plotly.express as px
import psycopg2
import requests
import snp_server
from builtins import print
from datetime import datetime, date, time, timedelta
from difflib import get_close_matches
from itertools import product
from pathlib import Path
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from urllib.parse import urlparse
from winreg import *
from queue import Queue
from PIL import Image, ImageDraw, ImageFont
from discord_webhook import DiscordWebhook
from prettytable import PrettyTable
from requests import post
from tkcalendar import DateEntry
from bio_data import *
from compass import compass_gui, get_status_data
from gui_positionen import load_position, save_position

# import compass, gui_positionen, snp_server
# from sqlite3 import Connection

filter_name = ''
eddc_modul = 1
root = ''
tree = ''
popup = ''
log_var = 0
tick = True
tick_time = []
log_time = []
faction_list = []
system_list = []
influence_list = []
Starsystem_list = []
SystemAddress_list = []
index_of_list = []
today = date.today()
today = str(today)
Year = (today[2:4])
Month = (today[5:7])
Day = (today[8:10])
b_date = ''
e_date = ''
success = FALSE
t_hour = 'Tick Time'
t_minute = 'Tick Minute'
inf_data = ''
docked = ''
bio_worth = []
version_number = '0.9.6.2'
current_version = ('Version ' + str(version_number))
global status  # popup_open, tree_open, old_view_name
root_open = False
popup_open = False
tree_open = False
view_name = 'system_scanner'
old_view_name = 'old'
expedition_upload = 0
update_server = 0
# data_old = StringVar()
fully = 0
bgs = PrettyTable(['System', 'Faction', 'Influence'])
voucher = PrettyTable(['Voucher', 'System', 'Faction', 'Credits'])
ground_cz_table = PrettyTable(['System', 'Faction', 'State', 'Count'])
mats_table = PrettyTable(['Materials', 'Type', 'Grade', 'Count'])
tw_pass_table = PrettyTable(['System', 'Passengers'])
tw_rescue_table = PrettyTable(['System', 'Rescued'])
tw_cargo_table = PrettyTable(['System', 'Cargo'])
thargoid_table = PrettyTable(['Interceptor', 'Kills', 'Credits'])
boxel_table = PrettyTable(['Systemname', 'MainStar'])
codex_bio_table = PrettyTable(['ID', 'Datum', 'Zeit', 'CMDR', 'Bio', 'Farbe', 'Credits', 'System', 'Body', 'Sektor'])
codex_stars_table = PrettyTable(['ID', 'Datum', 'Zeit', 'CMDR', 'Codex Eintrag', 'Typ', 'System', 'Sektor'])
system_scanner_table = PrettyTable(['Datum', 'Zeit', 'CMDR', 'Bio', 'Farbe',
                                    'Credits', 'System', 'Body', 'Sektor', 'Missing'])
statistics_table = PrettyTable(['ID', 'Datum', 'Zeit', 'Systemname', 'Body', 'Class', 'Mass', 'Age', 'Temp ', 'Region'])
eddc_user = 'anonym'
aus_var = 0


def get_time():
    return datetime.now()


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def logger(text, schwelle):
    if schwelle > 0:
        print(text)


database = str(resource_path("eddc.db"))
global log_path
# path = ''
db_file = Path(database)

if not db_file.is_file():
    logger('create db', 1)
    create_codex_entry()
    create_DB_Bio_prediction()
    create_DB_Bio_color()


# Funktion, um das Ergebnis zu prüfen und bei None auf 0 zu setzen
def get_value_or_default(query_result, default=0):
    return query_result[0] if query_result and query_result[0] is not None else default


def create_tables():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()

        cursor.execute("DROP TABLE IF EXISTS odyssey")
        cursor.execute("DROP TABLE IF EXISTS compare_for_ss")

        cursor.execute('''CREATE TABLE IF NOT EXISTS eddc_positions (
                            id INTEGER PRIMARY KEY,
                            x INTEGER,
                            y INTEGER
                        )''')

        cursor.execute("""CREATE TABLE IF NOT EXISTS active_expedition 
                                                (start_date date, 
                                                start_time timestamp,
                                                stop_date date, 
                                                stop_time timestamp)                                                
                                                """)

        cursor.execute(f'''CREATE TABLE IF NOT EXISTS bio_scan_data
                                        (date_log date, 
                                        time_log timestamp,
                                        cmdr TEXT,
                                        system TEXT,
                                        body_name TEXT,
                                        bio TEXT,
                                        color TEXT,
                                        scantype TEXT,
                                        latitude REAL,
                                        longitude REAL                                         
                                        )''')

        cursor.execute("""CREATE TABLE IF NOT EXISTS exploration_records 
                                        (date_log date, 
                                        time_log timestamp,
                                        cmdr TEXT,
                                        system TEXT,
                                        body TEXT,
                                        max_distance REAL,
                                        max_gravity REAL,
                                        max_body_count INTEGER,
                                        max_temp REAL,   
                                        max_radius REAL,
                                        min_radius REAL                                                                               
                                        )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS white_dwarfs 
                                        (date_log date, 
                                        time_log timestamp,
                                        cmdr TEXT,
                                        star_system TEXT,
                                        star_type TEXT                                                                                
                                        )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS compare_for_ss 
                                        (current_system TEXT, 
                                        planets_with_atmo INTEGER, 
                                        planets_bio_scaned INTEGER, 
                                        bios_scaned INTEGER
                                        )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS thargoid_war_data 
                                (date_log date, 
                                time_log timestamp, 
                                system_address TEXT, 
                                system_name TEXT, 
                                current_state TEXT, 
                                war_progress REAL, 
                                upload INTEGER)""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS DVRII 
                                        (jump_distance INTEGER, 
                                        hottest_body REAL,
                                        coldest_body REAL,
                                        most_bodys INTEGER,
                                        death_counter INTEGER,
                                        white_dwarf INTEGER,
                                        max_gravitation REAL,
                                        min_gravitation REAL,
                                        max_radius REAL,
                                        min_radius REAL                                        
                                        )""")

        item = cursor.execute("""SELECT * from DVRII""").fetchall()
        if not item:
            cursor.execute("""INSERT INTO DVRII(jump_distance, hottest_body, coldest_body, most_bodys, death_counter, 
            white_dwarf, max_gravitation, min_gravitation, max_radius, min_radius) VALUES (99999999, 99999999, 
            1, 99999999, 99999999, 99999999, 99999999, 1, 99999999, 1)""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS player_death 
                                (date_log date, 
                                time_log timestamp, 
                                cmdr TEXT,
                                KillerName TEXT, 
                                KillerRank TEXT)""")

        cursor.execute("CREATE TABLE IF NOT EXISTS logfiles (Name TEXT, explorer INTEGER, "
                       "bgs INTEGER, Mats INTEGER, CMDR TEXT, last_line INTEGER, Full_scan_var INTEGER, "
                       "expedition INTEGER, exp_lines INTEGER)")

        cursor.execute("""CREATE table IF NOT EXISTS flight_log 
                            (date_log date, time_log timestamp, SystemID INTEGER, 
                            SystemName TEXT, event TEXT, cmdr TEXT)""")

        cursor.execute('''CREATE TABLE IF NOT EXISTS compass (
                            body_name TEXT,
                            Waypoint INTEGER,
                            latitude REAL,
                            longitude REAL,
                            reached INTEGER
                        )''')

        cursor.execute("""CREATE table IF NOT EXISTS influence_db
                            (date_log date, time_log timestamp, voucher_type TEXT, SystemName TEXT, 
                            SystemAddress INTEGER, faction TEXT, amount INTEGER, upload INTEGER)""")

        cursor.execute("CREATE table IF NOT EXISTS odyssey (Name TEXT, Count INTEGER)")

        cursor.execute(f'''CREATE table IF NOT EXISTS engineering_mats (
                            date_log date, 
                            time_log timestamp,
                            Name TEXT, 
                            name_en TEXT, 
                            name_de TEXT, 
                            Category TEXT,
                            Grade INTEGER,
                            Count INTEGER)''')

        cursor.execute("""CREATE table IF NOT EXISTS lan_db (lang TEXT, switch INTEGER)""")

        cursor.execute("""CREATE table IF NOT EXISTS mission_failed 
                            (date_log date, time_log timestamp, mission_id INTEGER)""")

        cursor.execute("""CREATE table IF NOT EXISTS mission_accepted 
                            (date_log date, time_log timestamp, system TEXT, system_address INTEGER, faction TEXT, 
                            influence INTEGER, mission_id INTEGER)""")
        cursor.execute("""CREATE table IF NOT EXISTS server (
                            url TEXT, user TEXT, eddc_user TEXT, path TEXT, upload INTEGER, com_style TEXT, 
                            com_trans REAL, com_back TEXT, com_text TEXT, exp_upload INTEGER, exp_user TEXT)""")
        #
        item = cursor.execute("""SELECT * from server""").fetchall()
        if not item:
            # print(item)
            cursor.execute("""INSERT INTO SERVER (eddc_user, upload, com_style, com_trans, exp_upload, exp_user) 
                                VALUES ('anonym', 0, 'mica', 0.9, 0, 'anonym')""")

        cursor.execute("""CREATE table IF NOT EXISTS ground_cz (date_log date, time_log timestamp,
                            system TEXT, settlement TEXT, faction TEXT, state TEXT)""")

        # cursor.execute("CREATE table IF NOT EXISTS stars (SystemID INTEGER, star_class TEXT)")

        cursor.execute("""CREATE table IF NOT EXISTS star_data 
                            (date_log date, time_log timestamp, cmdr TEXT, body_id INTEGER, starsystem TEXT,
                            body_name TEXT, system_address INTEGER, Main TEXT, distance TEXT, 
                            startype TEXT, sub_class TEXT, mass REAL, radius REAL, age REAL, surface_temp REAL,
                            luminosity TEXT, rotation_period REAL,  axis_tilt REAL, discovered TEXT, mapped TEXT,
                            parents TEXT)""")

        cursor.execute("""CREATE table IF NOT EXISTS codex (date_log date, time_log timestamp, cmdr TEXT,
                        data TEXT,
                        bio_color TEXT,
                        systemname TEXT,
                        body TEXT,
                        region TEXT,
                        codex INTEGER,
                        player_death INTEGER)
                        """)

        cursor.execute("""CREATE table IF NOT EXISTS bary_centre (
                            date_log date,
                            time_log timestamp,
                            StarSystem TEXT, 
                            SystemAddress INTEGER, 
                            BodyID INTEGER, 
                            Children TEXT,
                            SemiMajorAxis REAL, 
                            Eccentricity REAL, 
                            OrbitalInclination REAL, 
                            Periapsis REAL, 
                            OrbitalPeriod REAL, 
                            AscendingNode REAL, 
                            MeanAnomaly REAL
                            )""")

        cursor.execute("""CREATE table IF NOT EXISTS codex_show (
                                cmdr TEXT,
                                data TEXT, 
                                region TEXT)
                                """)

        cursor.execute("""CREATE table IF NOT EXISTS codex_data (
                        date_log date,
                        time_log timestamp,
                        cmdr TEXT,                        
                        codex_name TEXT,
                        codex_entry TEXT,
                        category TEXT,
                        system TEXT,
                        region TEXT)
                        """)

        cursor.execute("""CREATE table IF NOT EXISTS planet_infos (
                        date_log date, 
                        time_log timestamp,
                        cmdr TEXT, 
                        SystemID INTEGER, 
                        SystemName TEXT, 
                        Main_Star TEXT, 
                        Local_Stars TEXT,
                        BodyName TEXT, 
                        BodyID INTEGER, 
                        DistanceToMainStar INTEGER, 
                        Tidal_lock Text, 
                        Terraform_state TEXT,
                        PlanetType TEXT, 
                        Atmosphere TEXT, 
                        Gravity REAL, 
                        Temperature REAL, 
                        Pressure REAL,
                        Landable TEXT, 
                        volcanism TEXT, 
                        sulphur_concentration REAL, 
                        Rings INTEGER, 
                        Mass REAL, 
                        Radius REAL, 
                        SemiMajorAxis REAL, 
                        Eccentricity REAL, 
                        OrbitalInclination REAL, 
                        Periapsis REAL, 
                        OrbitalPeriod REAL, 
                        AscendingNode REAL, 
                        MeanAnomaly REAL, 
                        RotationPeriod REAL, 
                        AxialTilt REAL, 
                        Discovered TEXT, 
                        Mapped TEXT, 
                        Materials TEXT
                        )""")

        cursor.execute("""CREATE table IF NOT EXISTS planet_bio_info (
                                            body TEXT,
                                            body_id TEXT,
                                            count TEXT,
                                            region TEXT,
                                            bio_genus)""")

        cursor.execute("""CREATE table IF NOT EXISTS bio_info_on_planet (
                                            body TEXT,
                                            genus TEXT,
                                            species TEXT,
                                            bio_scan_count INTEGER,
                                            mark_missing TEXT)""")

        # cursor.execute("""CREATE table IF NOT EXISTS star_map (
        #                                             starsystem TEXT,
        #                                             system_address TEXT,
        #                                             body_ID INTEGER,
        #                                             bodyname TEXT)""")

        cursor.execute("""CREATE table IF NOT EXISTS temp (
                                                timestamp TEXT,
                                                scantype TEXT,
                                                species TEXT,
                                                body TEXT)""")

        cursor.execute("""CREATE table IF NOT EXISTS selling ( date_log date, time_log timestamp, 
                        sell TEXT, cmdr TEXT) """)

        cursor.execute("""CREATE table IF NOT EXISTS db_version (version INTEGER)""")

        # cursor.execute("CREATE table IF NOT EXISTS influence (SystemName TEXT, Faction TEXT, Influence INTEGER)")
        connection.commit()

        create_codex_entry()
        create_DB_Bio_prediction()
        create_DB_Bio_color()


create_tables()

with sqlite3.connect(database) as connection:
    cursor = connection.cursor()
    cursor.execute("""CREATE table IF NOT EXISTS server (
                        url TEXT, user TEXT, eddc_user TEXT, path TEXT, upload INTEGER, com_style TEXT, 
                        com_trans REAL, com_back TEXT, com_text TEXT, exp_upload INTEGER, exp_user TEXT)""")

    cursor.execute("""SELECT * FROM server""")
    result = cursor.fetchall()
    if result:
        webhook_url = result[0][0]
        web_hock_user = result[0][1]
        eddc_user = result[0][2]
        log_path = result[0][3]

if log_path is None:
    # Set Program Path Data to random used Windows temp folder.
    with OpenKey(HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders") as key:
        value = QueryValueEx(key, '{4C5C32FF-BB9D-43B0-B5B4-2D72E54EAAA4}')
    # path = value[0] + '\\Frontier Developments\\Test'
    # path = value[0] + '\\Frontier Developments\\Franky'
    # path = value[0] + '\\Frontier Developments\\Bernd'
    log_path = value[0] + '\\Frontier Developments\\Elite Dangerous\\'

print(log_path)


def uri_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc])
    except:
        return False


def extract_uppercase_letters(text):
    uppercase_letters = re.findall(r'[A-Z]+', text)
    return uppercase_letters


def get_latest_version(var):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    try:
        response = requests. \
            get("https://raw.githubusercontent.com/SNP-MajorK/ED-DataCollector/master/version.json", timeout=1)
        my_json = json.loads(response.text)
        # my_json = json.loads('[{"version": "1.0.0.0", "hyperlink": "link"}]')
    except requests.exceptions.ConnectionError:
        my_json = json.loads('[{"version": "0.0.0.0", "hyperlink": "link"}]')
        messagebox.showwarning("Check failed", "No Internet Connection")
    db_version()

    for d in my_json:
        online_version = d['version']
        link = d['hyperlink']
        online_version = online_version.replace('.', '')
        cur_version = version_number.replace('.', '')
        if cur_version == online_version:
            # logger('no update needed', 1)
            if var != 1:
                messagebox.showinfo("No Update available", ("Already newest Version " + online_version))
        elif int(online_version) > int(cur_version):
            box = messagebox.askyesno("Update available", "New Version available\nOpen Downloadpage")
            if box:
                webbrowser.open(link, new=0, autoraise=True)


def new_server_settings():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    global log_path
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute("""SELECT * FROM server""")
        result = cursor.fetchall()
        # print(result)
        if result != []:
            if result[0][1] != ('' or None):
                web_hock_user = result[0][1]
            else:
                web_hock_user = ''
            if result[0][0] != ('' or None):
                webhook_url = result[0][0]
            else:
                webhook_url = ''
            if result[0][2] != ('' or None):
                eddc_user = result[0][2]
            else:
                eddc_user = 'anonym'
            if result[0][3] is not None:
                path_new = result[0][3]
                if path_new:
                    path = path_new
            else:
                path = log_path
                update = f'''UPDATE server set path = "{path}"'''
                cursor.execute(update)
                connection.commit()
            if int(result[0][4]) == 1 or int(result[0][4]) == 0:
                up_server = int(result[0][4])
            else:
                up_server = IntVar()
            if result[0][5] != ('' or None):
                com_style = result[0][5]
            else:
                com_style = 'mica'
            if result[0][6] != ('' or None):
                com_trans = result[0][6]
            else:
                com_trans = 0.9
            if result[0][7] != ('' or None):
                com_back = result[0][7]
            else:
                com_back = 'black'
            if result[0][8] != ('' or None):
                com_text = result[0][8]
            else:
                com_text = 'white'
            if int(result[0][9]) == 1 or int(result[0][9]) == 0:
                exp_upload = int(result[0][9])
            else:
                exp_upload = IntVar()
            if result[0][10] != ('' or None):
                exp_user = result[0][10]
            else:
                exp_user = 'anonym'
        else:
            web_hock_user = ''
            webhook_url = ''
            eddc_user = 'anonym'
            up_server = IntVar()
            com_style = 'mica'
            com_trans = 0.9
            com_back = 'black'
            com_text = 'white'
            exp_upload = 0
            exp_user = 'anonym'

    server_settings = customtkinter.CTkToplevel()
    server_settings.title('Server Einrichtung')
    server_settings.geometry("400x200")
    server_settings.minsize(400, 520)
    server_settings.maxsize(400, 800)
    server_settings.after(100, lambda: server_settings.focus_force())
    server_settings.config(background='black')
    top_blank = customtkinter.CTkFrame(master=server_settings, bg_color='black', fg_color='black')
    top_blank.pack(fill=X)

    scale_label = customtkinter.CTkLabel(master=top_blank,
                                         text='EDDC Skalieren',
                                         text_color='white',
                                         font=("Helvetica", 18))
    scale_label.pack()

    scale_frame = customtkinter.CTkFrame(master=top_blank, bg_color='black', fg_color='black')
    scale_frame.pack(fill=X, padx=10)

    def slider_event(value):

        value = float(value)
        customtkinter.set_widget_scaling(value)  # widget dimensions and text size
        customtkinter.set_window_scaling(value)  # window geometry dimensions

    def dpi_aware():
        customtkinter.deactivate_automatic_dpi_awareness()

    dpi_aware_check = customtkinter.CTkCheckBox(master=scale_frame, text="Disable automatic scaling ",
                                                command=dpi_aware, font=("Helvetica", 12))
    dpi_aware_check.grid(padx=5, column=0, row=0, pady=10)

    scale = customtkinter.CTkComboBox(scale_frame, state='readonly',
                                      width=70,
                                      values=['1.5', '1.4', '1.3', '1.2', '1.1', '1.0', '0.9', '0.8', '0.7', '0.6'],
                                      command=slider_event)
    scale.set('1.0')
    scale.grid(padx=50, column=1, row=0, pady=10)

    try:
        img = resource_path("eddc.ico")
        server_settings.iconbitmap(img)
    except TclError:
        logger('Icon not found', 1)

    if sys.platform.startswith("win"):
        server_settings.after(200, lambda: server_settings.iconbitmap(img))

    headline = customtkinter.CTkLabel(master=top_blank,
                                      text='Expeditions Einrichtung',
                                      text_color='white',
                                      font=("Helvetica", 18))
    headline.pack(pady=10)

    global update_server
    global expedition_upload
    expedition_upload = IntVar()
    update_server = IntVar()

    expedition_name_frame = customtkinter.CTkFrame(master=top_blank, bg_color='black', fg_color='black')
    expedition_name_frame.pack(fill=X, padx=10)

    expedition_name_label = customtkinter.CTkLabel(master=expedition_name_frame, text='Name : ',
                                                   text_color='white', font=("Helvetica", 14))
    expedition_name_label.grid(column=0, row=0, sticky=W, padx=5)

    # expedition_name_entry = customtkinter.CTkEntry(master=expedition_name_frame, width=200, font=("Helvetica", 14))
    # expedition_name_entry.insert(0, exp_user)
    # expedition_name_entry.grid(column=1, row=0, sticky=W, padx=5)

    cmdrs = get_cmdr_names()

    expedition_name_combobox = customtkinter.CTkComboBox(master=expedition_name_frame,
                                                         values=cmdrs,
                                                         font=("Helvetica", 14),
                                                         width=200)
    expedition_name_combobox.set(exp_user)
    expedition_name_combobox.grid(column=1, row=0, sticky="w", padx=5)

    expedition_upload_but = customtkinter.CTkCheckBox(master=expedition_name_frame, text="DVR Upload",
                                                      variable=expedition_upload, offvalue=0, onvalue=1,
                                                      text_color='white', command=upd_server2, font=("Helvetica", 12))
    expedition_upload_but.grid(column=2, row=0, sticky=W, padx=10, pady=3)

    if exp_upload == 0:
        expedition_upload_but.deselect()
    else:
        expedition_upload_but.select()

    headline = customtkinter.CTkLabel(master=top_blank,
                                      text='Discord Einrichtung',
                                      text_color='white',
                                      font=("Helvetica", 18))
    headline.pack(pady=5)

    name_frame = customtkinter.CTkFrame(master=top_blank, bg_color='black', fg_color='black')
    name_frame.pack(fill=X, padx=10)

    upload_but = customtkinter.CTkCheckBox(master=name_frame, text="BGS Upload  ",
                                           variable=update_server, offvalue=0, onvalue=1,
                                           text_color='white', command=upd_server, font=("Helvetica", 12))
    upload_but.grid(column=1, row=0, sticky=E, pady=1)

    if up_server == 0:
        upload_but.deselect()
    else:
        upload_but.select()

    name_label = customtkinter.CTkLabel(master=name_frame, text='CMDR : ', text_color='white', font=("Helvetica", 14))
    name_label.grid(column=0, row=1, sticky=W)

    name_entry = customtkinter.CTkEntry(master=name_frame, width=200, font=("Helvetica", 14))
    name_entry.insert(0, eddc_user)
    name_entry.grid(column=1, row=1, sticky=W)

    discord_user = customtkinter.CTkLabel(master=name_frame, text='Discord Bot Name : ',
                                          text_color='white', font=("Helvetica", 14))
    discord_user.grid(column=0, row=2, sticky=W)
    discord_user_entry = customtkinter.CTkEntry(master=name_frame, width=200, font=("Helvetica", 14))
    discord_user_entry.insert(0, web_hock_user)
    discord_user_entry.grid(column=1, row=2, sticky=W)

    discord_label = customtkinter.CTkLabel(master=name_frame, text='Discord Webhook URL : ',
                                           text_color='white', font=("Helvetica", 14))
    discord_label.grid(column=0, row=3, sticky=W)
    discord_entry = customtkinter.CTkEntry(master=name_frame, width=200, font=("Helvetica", 14))
    discord_entry.insert(0, webhook_url)
    discord_entry.grid(column=1, row=3, sticky=W)

    path_label = customtkinter.CTkLabel(master=name_frame, text='Journal Log Pfad : ',
                                        text_color='white', font=("Helvetica", 14))
    path_label.grid(column=0, row=4, sticky=W)
    path_entry = customtkinter.CTkEntry(master=name_frame, width=200, font=("Helvetica", 14))
    path_entry.insert(0, path)
    path_entry.grid(column=1, row=4, sticky=W)

    # Kompass Overlay Style
    com_frame = customtkinter.CTkFrame(master=top_blank, bg_color='black', fg_color='black')
    com_frame.pack(fill=X, padx=10)

    com_label = customtkinter.CTkLabel(master=com_frame, text='Kompass Style     ',
                                       text_color='white', font=("Helvetica", 14))
    com_label.grid(column=0, row=0, sticky=W, pady=10)

    com_style_label = customtkinter.CTkLabel(master=com_frame, text='Style     ',
                                             text_color='white', font=("Helvetica", 14))
    com_style_label.grid(column=0, row=1, sticky=W, padx=10)

    com_trans_label = customtkinter.CTkLabel(master=com_frame, text='Alpha      ',
                                             text_color='white', font=("Helvetica", 14))
    com_trans_label.grid(column=1, row=1, sticky=W, padx=10)

    com_back_label = customtkinter.CTkLabel(master=com_frame, text='Hintergrund  ',
                                            text_color='white', font=("Helvetica", 14))
    com_back_label.grid(column=2, row=1, sticky=W, padx=10)

    com_text_label = customtkinter.CTkLabel(master=com_frame, text='Textfarbe  ',
                                            text_color='white', font=("Helvetica", 14))
    com_text_label.grid(column=3, row=1, sticky=W, padx=10)

    com_style_combo = customtkinter.CTkComboBox(com_frame, state='readonly', width=80)
    com_style_combo.configure(values=('mica', 'acrylic', 'aero', 'native', 'popup', 'normal', 'inverse', 'win7'))
    com_style_combo.set(com_style)
    com_style_combo.grid(column=0, row=2, sticky=W)

    com_trans_combo = customtkinter.CTkComboBox(com_frame, state='readonly', width=70)
    com_trans_combo.configure(values=('1.0', '0.9', '0.8', '0.7', '0.6'))
    com_trans_combo.set(com_trans)
    com_trans_combo.grid(column=1, row=2, sticky=W)

    com_back_combo = customtkinter.CTkComboBox(com_frame, state='readonly', width=80)
    com_back_combo.configure(values=('black', 'white', 'yellow', 'blue', 'orange'))
    com_back_combo.set(com_back)
    com_back_combo.grid(column=2, row=2, sticky=W)

    com_text_combo = customtkinter.CTkComboBox(com_frame, state='readonly', width=80)
    com_text_combo.configure(values=('black', 'white', 'yellow', 'blue', 'orange'))
    com_text_combo.set(com_text)
    com_text_combo.grid(column=3, row=2, sticky=W, pady=15)

    def save(url, user, eddc_user, path, com_style, com_trans, com_back, com_text, exp_user):
        update_serv = update_server.get()
        update_exp_upload = expedition_upload.get()
        # print(com_style, com_trans)
        url_is_ok = 1
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            if not url or not user:
                pass
            if url:
                if uri_validator(url):
                    url_is_ok = 1
                else:
                    messagebox.showwarning("Check failed", "URL ist nicht korrekt")
                    server_settings.focus_force()
                    url_is_ok = 0
            cursor.execute("""SELECT * FROM server""")
            result = cursor.fetchall()
            if url_is_ok == 1:
                if eddc_user == '':
                    eddc_user = 'anonym'
                if result == []:
                    cursor.execute("INSERT INTO server VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                   (url, user, eddc_user, path, update_serv, com_style,
                                    com_trans, com_back, com_text, update_exp_upload, exp_user))
                else:
                    cursor.execute("drop table server")
                    cursor.execute("""CREATE table IF NOT EXISTS server (
                                        url TEXT, user TEXT, eddc_user TEXT, path TEXT, upload INTEGER, com_style TEXT, 
                                        com_trans REAL, com_back TEXT, com_text TEXT, 
                                        exp_upload INTEGER, exp_user TEXT)""")
                    cursor.execute("INSERT INTO server VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                   (url, user, eddc_user, path, update_serv, com_style, com_trans,
                                    com_back, com_text, update_exp_upload, exp_user))
                connection.commit()
                server_settings.after(200, server_settings.destroy)

    save_but = customtkinter.CTkButton(master=top_blank, text='Speichern',
                                       command=lambda: save(discord_entry.get(), discord_user_entry.get(),
                                                            name_entry.get(), path_entry.get(),
                                                            com_style_combo.get(), float(com_trans_combo.get()),
                                                            com_back_combo.get(), com_text_combo.get(),
                                                            expedition_name_combobox.get()
                                                            ),
                                       font=("Helvetica", 12))
    save_but.pack(pady=10)


def last_tick():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    try:
        response = requests.get("https://elitebgs.app/api/ebgs/v5/ticks", timeout=1)  #
        todos = json.loads(response.text)
    except:
        logger('Tick Error', 1)
        tick_data = ('[{"_id":"627fe6d6de3f1142b60d6dcd",'
                     '"time":"2022-05-14T16:56:36.000Z",'
                     '"updated_at":"2022-05-14T17:28:54.588Z",'
                     '"__v":0}]')
        todos = json.loads(tick_data)
        messagebox.showwarning("TICK failed",
                               f"Fehler beim Abrufen der Daten.")
    for d in todos:
        lt_date = d.get('time')
        t_year = (lt_date[:4])
        t_month = (lt_date[5:7])
        t_day = (lt_date[8:10])
        t_hour = str(lt_date[11:13])
        t_minute = str(lt_date[14:16])
        tick_time = [t_year, t_month, t_day, t_hour, t_minute]
        return tick_time


def file_names(var):
    # Changes because of new naming of logfiles!
    funktion = inspect.stack()[0][3] + ' Var = ' + str(var)
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute("""SELECT * FROM server""")
        result = cursor.fetchall()
        if result:
            eddc_user = result[0][2]
            if result[0][3] == 0:
                global log_path
                log_path = result[0][3]

    # update_eleven = datetime(2022, 3, 14)
    date_get = str(date_entry.get_date())

    my_date = date_get.split('-')
    tag2 = my_date[2]
    monat2 = my_date[1]
    jahr2 = my_date[0].replace('20', '', 1)

    #  Logs von dem Tag X
    if var == 0:
        search_date = datetime(int("20" + jahr2), int(monat2), int(tag2))
        journal_date_new = ("20" + str(jahr2) + "-" + str(monat2) + "-" + str(tag2) + "T")
        journal_date_old = str(jahr2 + monat2 + tag2)
        file_path_old = log_path + "\\Journal." + journal_date_old + "*.log"
        file_path_new = log_path + "\\Journal." + journal_date_new + "*.log"
        filenames = glob.glob(file_path_old)
        files = glob.glob(file_path_new)
        for i in files:
            filenames.append(i)
        return filenames

    # Alle Logfiles
    elif var == 1:
        filenames = glob.glob(log_path + "\\Journal.*.log")
        files_with_year = (glob.glob(log_path + "\\Journal.202*.log"))
        for i in files_with_year:
            filenames.remove(i)
        for i in files_with_year:
            filenames.append(i)
        return filenames

    #  Logs von gestern, heute & ggf. morgen
    elif var == 2:
        yesterday = str(datetime.now() - timedelta(days=1))[0:10]
        today = str(datetime.now())[0:10]
        tomorrow = str(datetime.now() + timedelta(days=1))[0:10]
        filenames = glob.glob(log_path + "\\Journal." + yesterday + "*.log")
        files_tod = glob.glob(log_path + "\\Journal." + today + "*.log")
        files_tom = glob.glob(log_path + "\\Journal." + tomorrow + "*.log")
        for i in files_tod:
            filenames.append(i)
        for i in files_tom:
            filenames.append(i)
        return filenames

    #  Lese die Logs von dem Tag X ein, und wenn vorhanden welche von den vortagen.
    elif var == 3:
        # tag2 = Tag.get()
        journal_date = ("20" + str(jahr2) + "-" + str(monat2) + "-" + str(tag2) + "T")
        files = glob.glob(log_path + "\\Journal." + journal_date + "*.log")
        filenames = glob.glob(log_path + "\\Journal.*.log")
        lauf = 1
        while not files:
            journal_date = ("20" + str(jahr2) + "-" + str(monat2) + "-" + str(tag2) + "T")
            files = glob.glob(log_path + "\\Journal." + journal_date + "*.log")
            lauf += 1
            if lauf == 5:
                break
        if not files:
            return []
        last = files[len(files) - 1]
        index = (filenames.index(last))
        i = 0
        data = []
        while index >= i and i != 5:
            # print(filenames[index-i])
            data.append(filenames[index - i])
            i += 1
        # print('Files - 5 ',data)
        return data

    #  Logs von heute
    elif var == 4:
        today = str(datetime.now())[0:10]
        files_tod = glob.glob(log_path + "\\Journal." + today + "*.log")
        return files_tod

    # Wähle die ersten 20 Dateien aus und konvertiere in String-Pfade
    elif var == 5:
        pfad = Path(log_path)
        # Verwende glob, um nur die passenden Dateien zu finden
        dateien = [f for f in pfad.glob('Journal.*.log') if f.is_file()]

        # Sortiere die Dateien nach Änderungsdatum (neueste zuerst)
        dateien.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        neuste_dateien = [str(f) for f in dateien[:20]]
        return neuste_dateien


def file_is_last(filename):
    # t1 = get_time()
    files = file_names(1)
    # t2 = get_time()
    # print(str(timedelta.total_seconds(t2 - t1)))
    if files[-1] != filename:
        return 1
    else:
        return 0


def tail_file(file):
    funktion = inspect.stack()[0][3]

    line_in_db = check_logfile_in_db(file, 'line', '')
    logger((funktion, file, str(line_in_db)), log_var)

    if not Path(file).exists():
        messagebox.showwarning("Check failed", f"File not found: {file}")
        return
    current_line_nr = 0
    with open(file, 'r', encoding='UTF8') as datei:
        for current_line_nr, line in enumerate(datei):
            if current_line_nr <= line_in_db:
                continue

            data = read_json(line)
            if data == ['']:
                logger((funktion + 'ignore Data'), 2)
                return

            cmdr = read_cmdr(file)
            check_cmdr(file, cmdr)
            if not cmdr or cmdr == 'UNKNOWN':
                logger(f'''No CMDR {file}''', 2)
                return

            event = data.get('event')
            if event:
                process_event(event, data, file, cmdr)

        check_logfile_in_db(file, 'line', current_line_nr)


def process_event(event, data, file, cmdr):
    match event:
        case 'Location':
            set_system(data, cmdr)
        case 'Scan':
            get_info_for_get_body_name(data, cmdr)
            if data.get('StarType'):
                get_all_stars(data, cmdr)
            elif data.get('ScanType'):
                get_planet_info(data, cmdr)
        case 'ScanBaryCentre':
            get_bary(data)
        case 'FSDJump':
            set_main_star(data, cmdr)
            set_system(data, cmdr)
        case 'StartJump':
            if data.get('JumpType') == "Hyperspace":
                get_star_info(data, cmdr)
        case 'ScanOrganic':
            get_info_for_bio_scan(data, file)
            read_bio_data(data, file)
        case 'FSSBodySignals' | 'SAASignalsFound':
            get_info_scan_planets(data)
        case 'SAASignalsFound':
            get_info_scan_planets(data)
        case 'CodexEntry':
            read_log_codex(data, file)
        case 'Shutdown':
            check_logfile_in_db(file, 'explorer', 'set')


# --- CMDR Funktionen überprüfen ----


# global data_old
data_old = None


def count_lines_efficiently(filename):
    line_count = 0
    with open(filename, 'r') as file:
        for _ in file:
            line_count += 1
    return line_count


def check_db_for_ss(current_system):  # Prüfe ob es neue Daten in der Datenbank vorhanden sind
    current_system = current_system[0]
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        sql = f'''SELECT * from compare_for_ss where current_system = "{current_system}"'''
        old_data = cursor.execute(sql).fetchall()

        sql1 = f'''SELECT COUNT(BodyName) FROM planet_infos where SystemName = "{current_system}"and landable = 1 
                    and Atmosphere like "%atmosphere%"'''
        sql2 = f'''select COUNT(bio_genus) from planet_bio_info where body like "%{current_system}%" 
                    and bio_genus != ""'''
        sql3 = f'''select COUNT(body_name) from bio_scan_data where body_name like "%{current_system}%"'''

        select1 = cursor.execute(sql1).fetchone()
        select2 = cursor.execute(sql2).fetchone()
        select3 = cursor.execute(sql3).fetchone()

        if not old_data:
            update_sql = f'''INSERT INTO compare_for_ss VALUES ("{current_system}", {select1[0]}, 
                                                                    {select2[0]}, {select3[0]} )'''
            cursor.execute(update_sql)
            connection.commit()
            return 0

        #  Wenn es in alles drei Tabellen keine neuen Daten gibt
        if old_data[0][1] == select1[0] and old_data[0][2] == select2[0] and old_data[0][3] == select3[0]:
            return 1  # Keine neuen Daten vorhanden
        else:
            update_sql = f'''UPDATE compare_for_ss SET planets_with_atmo = {select1[0]},
                                                        planets_bio_scaned =  {select2[0]},
                                                        bios_scaned = {select3[0]} 
                                                        where current_system = "{current_system}" '''
            cursor.execute(update_sql)
            connection.commit()
        return 0


def start_read_logs():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    global data_old
    files = file_names(1)

    if len(files) > 0:
        last = files[len(files) - 1]
    else:
        return

    if check_logfile_in_db(last, 'explorer', 'check') != 1:
        check_logfile_in_db(last, '', 'insert')
        tail_file(last)
    else:
        if data_old and data_old != ' ' and check_last(last) == 1:
            logger('USE OLD DATA', 2)
            return data_old

    current_system = get_last_system_in_db()
    logger((funktion, str(current_system[0])), log_var)
    if current_system is None:
        return

    if check_db_for_ss(current_system) == 1:
        # print('abkürzung', current_system)
        return data_old

    data = get_data_from_DB(last, current_system)

    logger(last, log_var)

    if data is not None:
        data_old = data
    if data is None and data_old is not None:
        data = data_old

    if not isinstance(data, str) and data is not None and current_system[0] is not None:
        if current_system[0] not in data[0][0]:
            data = None
    else:  # Wenn Data ein string ist, setze es auf None
        data = [(current_system[0], 'No', 'Data', '',
                 'System', 'without', 'life', "", "", "")]
        data_old = data
    return data


def log_date(timestamp):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    global log_time
    log_year = (timestamp[:4])
    log_month = (timestamp[5:7])
    log_day = (timestamp[8:10])
    log_hour = (timestamp[11:13])
    log_minute = (timestamp[14:16])
    log_seconds = (timestamp[17:19])
    # print(log_seconds)
    log_time = [log_year, log_month, log_day, log_hour, log_minute, log_seconds]
    # print(log_time)
    return log_time


def star_systems_db():  # Liest alle SystemIDs und Systemnamen im Journal aus um sie in die DB zu speichern
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    filenames = file_names(0)
    files = ()
    if isinstance(filenames, str):
        files += (filenames,)
    else:
        files = filenames
    for filename in files:
        cmdr = read_cmdr(filename)
        with open(filename, 'r', encoding='UTF8') as datei:
            for zeile in datei:
                data = read_json(zeile)
                if data.get('event') == 'Scan':
                    get_info_for_get_body_name(data, cmdr)  # star_map
                if data.get('event') == 'StartJump' and data.get('JumpType') == "Hyperspace":
                    # print(data)
                    get_info_for_get_body_name(data, cmdr)  # star_map


def print_influence_db(filter_b):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    data_list = []
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        se = tick_select()
        filter_b = '%' + filter_b + '%'
        sql = 'SELECT DISTINCT(SystemName), faction FROM influence_db where ' \
              'voucher_type = "influence" and ' + se + ' order by 1'
        new_data = cursor.execute(sql).fetchall()
        for i in new_data:
            sql = f'''SELECT SUM(amount) FROM influence_db where voucher_type = "influence" and 
            SystemName = "{str(i[0])}" and faction = "{str(i[1])}" and {se}'''
            # print(sql)
            cursor.execute(sql)
            result = cursor.fetchall()
            data_tup = (i[0], i[1], result[0][0])
            data_list.append(data_tup)
        if filter_b != '%%':
            cursor.execute("""CREATE TABLE IF NOT EXISTS tmp_filter_inf 
                                (SystemName TEXT, faction TEXT, influence INTEGER)""")
            cursor.execute("""DROP TABLE tmp_filter_inf""")
            cursor.execute("""CREATE TABLE IF NOT EXISTS tmp_filter_inf 
                                (SystemName TEXT, faction TEXT, influence INTEGER)""")

            for i in data_list:
                cursor.execute("""INSERT INTO tmp_filter_inf (SystemName, faction, influence) 
                                    VALUES (?, ?, ?)""", (i[0], i[1], i[2]))
                connection.commit()
            filter_tmp = cursor.execute("""SELECT * FROM tmp_filter_inf WHERE SystemName LIKE ? OR 
                                        Faction LIKE ? GROUP BY 1, 2, 3""", (filter_b, filter_b)).fetchall()
            data = filter_tmp
        else:
            data = data_list
    return data


def einfluss_auslesen(journal_file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    cmdr = read_cmdr(journal_file)

    # t1 = get_time()
    line = 0
    with open(journal_file, 'r', encoding='UTF8') as datei:
        for zeile in datei:
            line += 1
            data = read_json(zeile)
            event = data.get('event')
            match event:
                case 'Docked':
                    get_info_for_get_body_name(data, cmdr)  # star_map
                case 'Location':
                    get_info_for_get_body_name(data, cmdr)  # star_map
                case 'StartJump':
                    if data.get('JumpType') == "Hyperspace":
                        get_info_for_get_body_name(data, cmdr)  # star_map
                case "MissionAccepted":
                    system_data = find_last_docked(journal_file, line)
                    system = system_data[1]
                    system_address = system_data[2]
                    mission_data(data, system, system_address)
                case "MissionFailed":
                    mission_failed(data)
                case 'MissionCompleted':
                    if check_logfile_in_db(journal_file, 'bgs', 'check') == 0:
                        mission_completed(data)
                case 'Shutdown':
                    check_logfile_in_db(journal_file, 'bgs', 'set')
    # t2 = get_time()
    # print('read all ' + str(journal_file) + '    ' + str(timedelta.total_seconds(t2 - t1)))

    # =========================================== End of dateien_einlesen()


def get_data_mission_accepted(mission_id):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    mission_id = int(mission_id)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select = cursor.execute("""SELECT * from mission_accepted where mission_id = ?""",
                                (mission_id,)).fetchall()
        if select != []:
            return select[0]
        else:
            return


def mission_completed(data):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    timestamp = data.get('timestamp')
    # log_time = (log_date(timestamp))
    # date_log = (log_time[0] + "-" + log_time[1] + "-" + log_time[2])
    # time_log = (log_time[3] + ":" + log_time[4] + ":" + log_time[5])
    mission_id = data.get('MissionID')

    for faction_effects in data.get("FactionEffects", 'LEER'):
        if faction_effects:
            if faction_effects.get('Faction'):
                faction = faction_effects.get('Faction')
                effects = faction_effects.get('Influence')
                if effects == []:  # Kein Einfluss im Log, der Einfluss wird der Auftragsannahme gezogen
                    new_data = get_data_mission_accepted(mission_id)
                    if new_data:
                        if new_data[4] == faction:
                            voucher_db(timestamp, 'influence', new_data[2], new_data[3], new_data[4], new_data[5])

                for inf in faction_effects.get('Influence'):
                    system_address = inf.get('SystemAddress')
                    trend = inf.get('Trend')
                    if trend == 'UpGood':
                        influence = int(len(inf.get('Influence')))
                    else:
                        influence = int(len(inf.get('Influence'))) * -1
                    system_name = get_system(system_address)
                    voucher_db(timestamp, 'influence', system_name, system_address, faction, influence)


def mission_failed(data):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    timestamp = data.get('timestamp')
    log_time = (log_date(timestamp))
    date_log = (log_time[0] + "-" + log_time[1] + "-" + log_time[2])
    time_log = (log_time[3] + ":" + log_time[4] + ":" + log_time[5])
    # faction = data.get('Faction')
    mission_id = data.get('MissionID')
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select = cursor.execute("SELECT * from mission_failed where "
                                "date_log = ? and time_log = ? and mission_id = ?",
                                (date_log, time_log, mission_id)).fetchall()
        # print(select)
        if not select:
            cursor.execute("INSERT INTO mission_failed VALUES (?, ?, ?)",
                           (date_log, time_log, mission_id))
            connection.commit()


def mission_data(data, system, system_address):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    timestamp = data.get('timestamp')
    log_time = (log_date(timestamp))
    date_log = (log_time[0] + "-" + log_time[1] + "-" + log_time[2])
    time_log = (log_time[3] + ":" + log_time[4] + ":" + log_time[5])
    faction = data.get('Faction')
    influence = len(data.get('Influence'))
    mission_id = data.get('MissionID')

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select = cursor.execute("""SELECT * from mission_accepted where date_log = ? and time_log = ? 
                                and system_address = ? and faction = ? and influence = ? and mission_id = ?""",
                                (date_log, time_log, system_address, faction, influence, mission_id)).fetchall()
        # print(select)
        if not select:
            cursor.execute("INSERT INTO mission_accepted VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (date_log, time_log, system, system_address, faction, influence, mission_id))
            connection.commit()


def failed_mission():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        se = tick_select()
        sel = "SELECT mission_id from mission_failed where " + se
        select = cursor.execute(sel).fetchall()
        for i in select:
            # sel = "SELECT system_address, faction, influence from mission_accepted where mission_id = ? "
            # select = cursor.execute(sel, (i[0],)).fetchall()
            # influence_db(select[0][0], select[0][1], (int(select[0][2])* -1))
            sel2 = "SELECT date_log, time_log, system, system_address, faction, influence " \
                   "from mission_accepted where mission_id = ? "
            select = cursor.execute(sel2, (i[0],)).fetchall()
            if not select:
                # print(sel2)
                return
            timestamp = select[0][0] + ' ' + select[0][1]
            voucher_type = 'influence'
            voucher_db(timestamp, voucher_type, select[0][2], select[0][3], select[0][4], (int(select[0][5]) * -1))
            # inf_db(timestamp, voucher_type, )
            # inf_db(date_log, time_log, system_name, system_address, faction, influence)


def check_tick_time(zeile, ea_tick):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    date_get = str(date_entry.get_date())
    my_date = date_get.split('-')
    tag2 = my_date[2]
    monat2 = my_date[1]
    jahr2 = my_date[0]
    # data = json.loads(zeile)
    data = read_json(zeile)
    timestamp = str(data['timestamp'])
    ctt_log_time = log_date(timestamp)
    tick_okay = False
    tick_time = last_tick()
    log_time_new = datetime(int(ctt_log_time[0]), int(ctt_log_time[1]), int(ctt_log_time[2]),
                            int(ctt_log_time[3]), int(ctt_log_time[4]))
    tick_time_new = datetime(int(jahr2), int(monat2), int(tag2), int(tick_time[3]), int(tick_time[4]))
    if ea_tick is True:  # Nach dem Tick
        if tick_time_new < log_time_new:  # Wenn Daten im Log nach dem TICK waren
            tick_okay = True
    else:  # Vor dem Tick
        if tick_time_new > log_time_new:  # Wenn Daten im Log vor dem TICK waren
            tick_okay = True
    return tick_okay


def insert_war_data(date_log, time_log, system_address, system_name, current_state, war_progress):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS thargoid_war_data 
        (date_log date, 
        time_log timestamp, 
        system_address TEXT, 
        system_name TEXT, 
        current_state TEXT, 
        war_progress REAL, 
        upload INTEGER)""")

        cursor.execute("""SELECT * FROM thargoid_war_data where date_log= ? and time_log = ? and 
                            system_address = ? and system_name = ?""",
                       (date_log, time_log, system_address, system_name))
        result = cursor.fetchall()

        if not result:
            cursor.execute("INSERT INTO thargoid_war_data VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (date_log, time_log, system_address, system_name, current_state, war_progress, 0))
            connection.commit()


def war_data_to_online_db():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    sql = "SELECT * FROM thargoid_war_data where upload = 0"
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select = cursor.execute(sql).fetchall()

        cursor.execute("""CREATE TABLE IF NOT EXISTS thargoid_war_data 
                                (date_log date, 
                                time_log timestamp, 
                                system_address TEXT, 
                                system_name TEXT, 
                                current_state TEXT, 
                                war_progress REAL, 
                                upload INTEGER)""")
        if select != []:
            for i in select:
                date_log = i[0]
                time_log = i[1]
                timestamp = str(date_log) + ' ' + str(time_log)
                system_address = i[2]
                system_name = i[3]
                current_state = i[4]
                war_progress = i[5]

                with psycopg2.connect(dbname=snp_server.db_name, user=snp_server.db_user, password=snp_server.db_pass,
                                      host=snp_server.db_host, port=5432) as psql_conn:
                    psql = psql_conn.cursor()
                    p_select = "SELECT * FROM thargoid_war where " \
                               "datetime = \'" + str(timestamp) + "\' and SystemAddress = '" + str(system_address) \
                               + "' and " "SystemName = '" + system_name + "'"
                    psql.execute(p_select)
                    result = psql.fetchall()
                    if result == []:
                        insert = 'INSERT INTO thargoid_war (datetime, SystemAddress, SystemName, current_state, ' \
                                 'war_progress) VALUES (timestamp \'' + str(timestamp) + '\', ' + str(system_address) \
                                 + ' , \'' + system_name + '\' , \'' + current_state + '\' , ' + str(war_progress) + ')'
                        psql.execute(insert)
                        psql_conn.commit()

                update = "UPDATE thargoid_war_data SET upload = 1 where date_log = ? and time_log = ? " \
                         "and system_address = ? and system_name = ? and current_state = ? and war_progress = ?"
                cursor.execute(update, (date_log, time_log, system_address, system_name, current_state, war_progress))
                connection.commit()


def thargoid_war_data(data):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    war_data = data.get('ThargoidWar')

    if not war_data:
        return
    else:
        timestamp = data.get('timestamp')
        log_time = (log_date(timestamp))
        date_log = (log_time[0] + "-" + log_time[1] + "-" + log_time[2])
        time_log = (log_time[3] + ":" + log_time[4] + ":" + log_time[5])

        system_address = data.get('SystemAddress')
        system_name = data.get('StarSystem')

        current_state = war_data.get('CurrentState')
        # next_success_state = war_data.get('NextStateSuccess')
        # next_fail_state = war_data.get('NextStateFailure')
        # success_state = war_data.get('SuccessStateReached')
        war_progress = war_data.get('WarProgress')
        if war_progress == 0:
            return
        war_progress = war_progress * 100
        insert_war_data(date_log, time_log, system_address, system_name, current_state, war_progress)
        return date_log, time_log, system_address, system_name, current_state, war_progress


def update_thargoid_war():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with psycopg2.connect(dbname=snp_server.db_name, user=snp_server.db_user, password=snp_server.db_pass,
                          host=snp_server.db_host, port=5432) as psql_conn:
        psql = psql_conn.cursor()
        select = "SELECT * FROM thargoid_war"
        psql.execute(select)
        result = psql.fetchall()
    for i in result:
        timestamp = i[0]
        timestamp = str(timestamp).split(' ')

        date_log = timestamp[0]
        time_log = timestamp[1]
        system_address = i[1]
        system_name = i[2]
        current_state = i[3]
        war_progress = i[4]

        sql = "select * from thargoid_war_data where date_log = '" + str(date_log) + "' and time_log = '" \
              + str(time_log) + "' and system_address = " + str(system_address) + " and system_name = '" \
              + str(system_name) + "' and war_progress = " + str(war_progress)
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            select = cursor.execute(sql).fetchall()
            if select == []:
                insert = "INSERT INTO thargoid_war_data VALUES ('" + str(date_log) + "', '" + str(time_log) + "', " \
                         + str(system_address) + ", '" + str(system_name) + "', '" + str(current_state) \
                         + "', " + str(war_progress) + ", 1)"
                cursor.execute(insert)
                connection.commit()


def show_war_data():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        one_week = str(datetime.now() - timedelta(days=7))[0:10]
        today = str(datetime.now())[0:10]
        sql = "SELECT system_name, date_log, time_log, war_progress  FROM thargoid_war_data where date_log BETWEEN '" \
              + one_week + "' and '" + today + "' ORDER by 2 DESC, 3 DESC"
        cursor.execute(sql)
        result = cursor.fetchall()
        systems = []
        dates = []
        progress = []
        eddc_text_box.insert(END, 'Folgende Systeme sind in der Datenbank vorhanden: \n\n')
        for i in result:
            if i[0] not in systems:
                systems.append(i[0])
                wp_date = str(i[1]).split('-')
                new_date = wp_date[2] + '.' + wp_date[1] + '.' + wp_date[0]
                dates.append(new_date)
                prog = str(i[3]).split('.')
                progress.append(prog[0])
        for count, s in enumerate(systems):
            eddc_text_box.insert(END, ((str(systems[count]) + '\t\t\t\t ' + str(dates[count]) + '\t\t '
                                        + str(progress[count]) + '\n')))


def auswertung_thargoid_war(b_filter):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    timestamp = []
    war_progress = []
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()

        sql = "SELECT date_log, time_log, war_progress FROM thargoid_war_data where " \
              "system_name = \'" + b_filter + "\' ORDER BY 1, 2"
        result = cursor.execute(sql).fetchall()
        if result != []:
            for i in result:
                zeit = (i[0] + ' ' + i[1])
                timestamp.append(zeit)
                war_progress.append(i[2])
    if timestamp != [] or war_progress != []:
        title = "War Progress of System " + b_filter
        fig = px.line(x=timestamp, y=war_progress, title=title, labels={'x': 'Datum', 'y': 'War Progress'},
                      markers=True)
        fig.show()
    else:
        eddc_text_box.insert(END, ('Das System ' + b_filter + ' wurde nicht in Datenbank gefunden: \n'))
        eddc_text_box.insert(END, '\n')


def multi_sell_exploration_data(journal_file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    with open(journal_file, 'r', encoding='UTF8') as datei:
        line = 0
        for zeile in datei:
            line += 1
            search_string = "MultiSellExplorationData"
            search_string2 = "SellExplorationData"

            if (zeile.find(search_string)) > -1 or (zeile.find(search_string2)) > -1:
                if check_tick_time(zeile, tick):
                    data_found = line
                    data = find_last_docked(journal_file, data_found)
                    faction = data[0]
                    system_name = data[1]
                    system_address = data[2]
                    # data = json.loads(zeile)
                    data = read_json(zeile)
                    timestamp = (data['timestamp'])
                    # print('Sell ExplorationData ' + faction + ' ' + str(data["TotalEarnings"]))
                    # vouchers_db('ExplorationData', system_name, str(faction), int(data["TotalEarnings"]))
                    voucher_db(timestamp, 'ExplorationData', system_name, system_address,
                               str(faction), int(data["TotalEarnings"]))


def market_sell(journal_file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with open(journal_file, 'r', encoding='UTF8') as datei:
        line = 0
        for zeile in datei:
            line += 1
            search_string = "MarketSell"
            if (zeile.find(search_string)) > -1:
                if check_tick_time(zeile, tick):
                    data_found = line
                    data = find_last_docked(journal_file, data_found)
                    faction = data[0]
                    system_name = data[1]
                    system_address = data[2]
                    # data = json.loads(zeile)
                    data = read_json(zeile)
                    timestamp = (data['timestamp'])
                    vk = int(data['SellPrice'])
                    dek = int(data['AvgPricePaid'])
                    menge = int(data['Count'])
                    profit = (vk - dek) * menge
                    try:
                        if data['BlackMarket']:
                            # vouchers_db('BlackMarket', system_name, str(faction), profit)
                            voucher_db(timestamp, 'BlackMarket', system_name, system_address,
                                       str(faction), int(profit))
                        else:
                            # print('MarketSell')
                            # vouchers_db('MarketSell', system_name, str(faction), profit)
                            voucher_db(timestamp, 'MarketSell', system_name, system_address,
                                       str(faction), int(profit))
                    except KeyError:
                        logger('KeyError BlackMarket', log_var)
                        # print(data)
                        # vouchers_db('MarketSell', system_name, str(faction), profit)
                        voucher_db(timestamp, 'MarketSell', system_name, system_address,
                                   str(faction), int(profit))


def find_last_docked(journal_file, data_found):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with open(journal_file, 'r', encoding='UTF8') as datei:
        line = 0
        factions = ['---']
        star_systems = ['---']
        system_addresses = ['---']

        for zeile in datei:
            line += 1
            # data = json.loads(zeile)
            data = read_json(zeile)
            if data.get('event') == 'Docked' or data.get('event') == 'Location':
                if data.get('event') == 'Docked':
                    docked_data = ((data['StationFaction'])['Name'])
                    if line < data_found:
                        factions.append(docked_data)
                star_system = (data['StarSystem'])
                if line < data_found:
                    star_systems.append(star_system)
                system_address = data.get('SystemAddress')
                if line < data_found:
                    system_addresses.append(system_address)
    faction = factions[-1]
    # print(factions)
    system_address = system_addresses[-1]
    star_system = star_systems[-1]
    return faction, star_system, system_address


def redeem_voucher(journal_file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with open(journal_file, 'r', encoding='UTF8') as datei:
        line = 0
        for zeile in datei:
            line += 1
            search_string = "RedeemVoucher"
            if (zeile.find(search_string)) > -1:
                if check_tick_time(zeile, tick):
                    data_found = line
                    last_docked = find_last_docked(journal_file, data_found)
                    system_name = last_docked[1]
                    system_address = last_docked[2]
                    # data = json.loads(zeile)
                    data = read_json(zeile)
                    timestamp = data.get('timestamp')
                    try:
                        if data['BrokerPercentage']:
                            logger('Ignoring Interstellar Factor', log_var)
                    except KeyError:
                        try:
                            for p in data["Factions"]:
                                # print(data)
                                if not p['Faction'] == '':
                                    # print(p['Faction'])
                                    # vouchers_db('Bounty ', system_name, str(p['Faction']), int(p['Amount']))
                                    voucher_db(timestamp, 'Bounty', system_name, system_address, str(p['Faction']),
                                               int(p['Amount']))
                        except KeyError:
                            try:
                                if data['Faction'] == 'PilotsFederation':
                                    logger('InterstellarFactor', log_var)
                                elif not data['Faction'] == '':
                                    # print(data)
                                    # vouchers_db('CombatBonds', system_name, str(data['Faction']), int(data['Amount']))
                                    voucher_db(timestamp, 'CombatBonds', system_name, system_address,
                                               str(data['Faction']), int(data['Amount']))

                            except KeyError:
                                logger('No Faction Event', log_var)


def update_eddc_db():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute("""SELECT * FROM server""")
        result = cursor.fetchall()
        if result != []:
            eddc_user = result[0][2]
            if result[0][4] == 0:
                return
        else:
            eddc_user = 'anonym'
        sql = 'SELECT * FROM influence_db WHERE upload = 0'
        item = cursor.execute(sql).fetchall()

        for i in item:
            date_log = str(i[0])
            time_log = str(i[1])
            voucher_type = str(i[2])
            system_name = str(i[3])
            system_address = str(i[4])
            faction = str(i[5])
            amount = str(i[6])
            timestamp = date_log + ' ' + time_log
            system_name = system_name.replace("'", "''")
            faction = faction.replace("'", "''")
            with psycopg2.connect(dbname=snp_server.db_name, user=snp_server.db_user,
                                  password=snp_server.db_pass, host=snp_server.db_host, port=5432) as psql_conn:
                psql = psql_conn.cursor()
                select = 'select * from influence_db where datetime = ' + str(timestamp) + \
                         ' and name = ' + eddc_user + ' and voucher_type = ' + voucher_type + \
                         ' and systemname = ' + system_name + ' and systemaddress = ' + str(system_address) + \
                         ' and faction = ' + faction + 'and amount = ' + str(amount) + ';'

                psql.execute(select)
                result = psql.fetchall()
                if result == []:
                    insert = 'INSERT INTO influence_db ' \
                             '(datetime, name, voucher_type, systemname, systemaddress, faction, amount) VALUES ' \
                             '(timestamp \'' + str(timestamp) + '\', \'' + eddc_user + '\', \'' + \
                             voucher_type + '\', \'' + system_name + '\', ' + str(
                        system_address) + ', \'' + faction + '\', ' \
                             + str(amount) + ');'
                    psql.execute(insert)
                    psql_conn.commit()

            system_name = str(i[3])
            faction = str(i[5])
            sql = 'UPDATE influence_db set upload = 1 where date_log = "' + date_log \
                  + '" and time_log = "' + time_log \
                  + '" and voucher_type = "' + voucher_type \
                  + '" and systemname = "' + system_name \
                  + '" and systemaddress = ' + system_address \
                  + ' and faction = "' + faction \
                  + '" and amount = ' + amount
            cursor.execute(sql)


def voucher_db(timestamp, voucher_type, system_name, system_address, faction, amount):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        # timestamp = data.get('timestamp')
        log_time = (log_date(timestamp))
        date_log = (log_time[0] + "-" + log_time[1] + "-" + log_time[2])
        time_log = (log_time[3] + ":" + log_time[4] + ":" + log_time[5])
        cursor.execute("""select * from influence_db where date_log = ? and time_log = ?
                            and voucher_type = ? and systemaddress = ? and faction = ?""",
                       (date_log, time_log, voucher_type, system_address, faction))
        item = cursor.fetchall()
        if item == []:
            cursor.execute("""INSERT INTO influence_db VALUES (?,?,?,?,?,?,?,?)""",
                           (date_log, time_log, voucher_type, system_name, system_address, faction, amount, 0))
            connection.commit()


def insert_into_combat_zone(date_log, time_log, system_name, settlement, faction, state):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        item = cursor.execute("""SELECT * from ground_cz where date_log = ? and time_log = ? 
                                and system = ? and settlement = ? and faction = ? and state = ?""",
                              (date_log, time_log, system_name, settlement, faction, state)).fetchall()
        if item == []:
            cursor.execute("INSERT INTO ground_cz VALUES (?, ?, ?, ?, ?,? )",
                           (date_log, time_log, system_name, settlement, faction, state))
            connection.commit()


def tick_select():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    date_get = str(date_entry.get_date())
    my_date = date_get.split('-')
    tag2 = my_date[2]
    monat2 = my_date[1]
    jahr2 = my_date[0]

    h_tick = tick_hour_label.get()
    m_tick = tick_minute_label.get()
    tick_time = h_tick + ':' + m_tick
    date = jahr2 + '-' + monat2 + '-' + tag2
    search_date = datetime(int(jahr2), int(monat2), int(tag2), int(h_tick), int(m_tick))

    if tick:  # nach dem Tick
        tomorrow = str(search_date + timedelta(days=1))[0:10]
        select_tick = f'''((date_log = "' + {date} + '" and time_log > "' + {tick_time} + '") or 
                            (date_log = "' + {tomorrow} + '" and time_log < "' + {tick_time} + '"))'''
    else:  # vor dem Tick
        yesterday = str(search_date - timedelta(days=1))[0:10]
        select_tick = f'''((date_log = "' + {date} + '" and time_log < "' + {tick_time} + '") or 
                            ( date_log = "' + {yesterday} + '" and time_log > "' + {tick_time} + '"))'''
    return select_tick


def print_combat_zone():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    data = []
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select_tick = tick_select()

        select = 'SELECT distinct(system) FROM ground_cz WHERE ' + select_tick
        systems = cursor.execute(select).fetchall()
        select = 'SELECT * FROM ground_cz WHERE ' + select_tick
        all = cursor.execute(select).fetchall()
        for i in systems:
            select = 'SELECT distinct(faction) FROM ground_cz WHERE ' + select_tick
            factions = cursor.execute(select).fetchall()
            for f in factions:
                select = 'SELECT distinct(state) FROM ground_cz WHERE system = ? and faction = ? and ' + select_tick
                state = cursor.execute(select, (i[0], f[0])).fetchall()
                for s in state:
                    select = 'SELECT count(state) FROM ground_cz WHERE system = ? and faction = ? and ' \
                             'state = ? and ' + select_tick
                    count = cursor.execute(select, (i[0], f[0], s[0])).fetchall()
                    for c in count:
                        data.append((i[0], f[0], s[0], c[0]))
    #
    # print(data)
    # new = combat_window(data)
    # print(new)
    return data


new_data = []


def combat_window(root, data):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    global new_data
    new_data = []
    combat_windows = Toplevel()
    combat_windows.title('Server Einrichtung')
    combat_windows.geometry("400x200")
    combat_windows.minsize(750, 200)
    combat_windows.maxsize(1200, 500)
    combat_windows.configure(background='black')
    combat_windows.after(1, lambda: combat_windows.focus_force())
    try:
        img = resource_path("eddc.ico")
        combat_windows.iconbitmap(img)
    except TclError:
        logger('Icon not found', 1)

    if sys.platform.startswith("win"):
        combat_windows.after(200, lambda: combat_windows.iconbitmap(img))

    headline = Label(combat_windows, text='Bodenkampf erkannt', bg='black', fg='white', font=("Helvetica", 11))
    headline.pack()
    top_blank = Frame(combat_windows, bg='black')
    top_blank.pack(pady=5)
    # print(len(data))
    lauf = 1
    # # new_frame = Frame(top_blank, bg='white')
    # # new_frame.pack(pady=0, fill=X)
    #
    for i in data:
        system = (i[0],)
        faction = (i[1],)
        difficulty = (i[2],)
        count = ((i[3] - 1),)
        global system_combo
        system_combo = ttk.Combobox(top_blank, state='readonly')
        system_combo['values'] = system
        system_combo.current(0)
        # system_combo.bind("<<ComboboxSelected>>", selected)
        system_combo.grid(column=0, row=lauf, sticky=W, padx=10, pady=5)

        faction_combo = ttk.Combobox(top_blank, state='readonly')
        faction_combo['values'] = faction
        faction_combo.current(0)
        # faction_combo.bind("<<ComboboxSelected>>", selected)
        faction_combo.grid(column=1, row=lauf, sticky=W, padx=10, pady=5)

        difficulty_combo = ttk.Combobox(top_blank, state='readonly')
        difficulty_combo['values'] = difficulty
        difficulty_combo.current(0)
        # difficulty_combo.bind("<<ComboboxSelected>>", selected)
        difficulty_combo.grid(column=2, row=lauf, sticky=W, padx=10, pady=5)

        count_combo = ttk.Combobox(top_blank)
        count_combo['values'] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        count_combo.current(0)
        # count_combo.bind("<<ComboboxSelected>>", selected)
        count_combo.grid(column=3, row=lauf, sticky=W, padx=10, pady=5)
        lauf += 1

    def save(data, i, var):
        # print(data, i, var)
        new_var = (i[0], i[1], i[2], var)
        # print(new_var)
        data.remove(i)
        data.append(new_var)

        combat_windows.destroy()
        # print(data)

    save_but = Button(combat_windows,
                      text='Speichern',
                      activebackground='#000050',
                      activeforeground='white',
                      bg='black',
                      fg='white',
                      command=lambda: save(data, i, count_combo.get()),
                      font=("Helvetica", 10))
    save_but.pack(pady=5)

    root.wait_window(combat_windows)


def print_vouchers_db(filter_b):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        filter_b = '%' + filter_b + '%'
        data_list = []
        se = tick_select()
        sql = 'SELECT DISTINCT(SystemName), faction, voucher_type FROM influence_db where ' \
              'voucher_type != "influence" and ' + se + ' order by 1'
        # print(sql)
        new_data = cursor.execute(sql).fetchall()

        for i in new_data:
            sql = 'SELECT SUM(amount) FROM influence_db where voucher_type != "influence" and ' \
                  'SystemName = "' + i[0] + \
                  '" and faction = "' + i[1] + '" and voucher_type = "' + i[2] + '" and ' + se
            # print(sql)
            cursor.execute(sql)
            result = cursor.fetchall()
            data_tup = (i[2], i[0], i[1], result[0][0])
            data_list.append(data_tup)
        if filter_b != '%%':
            cursor.execute("""DROP TABLE IF EXISTS tmp_filter_voucher""")
            cursor.execute("""CREATE TABLE IF NOT EXISTS tmp_filter_voucher 
                                            (Type TEXT, SystemName TEXT, faction TEXT, amount INTEGER)""")
            for i in data_list:
                cursor.execute("""INSERT INTO tmp_filter_voucher VALUES (?, ?, ?, ?)""", (i[0], i[1], i[2], i[3]))
                connection.commit()
            filter = cursor.execute("""SELECT * FROM tmp_filter_voucher WHERE SystemName LIKE ? OR 
                                                    Faction LIKE ? GROUP BY 1, 2, 3, 4""",
                                    (filter_b, filter_b)).fetchall()
            data = filter
        else:
            data = data_list
    return data


def get_correct_region(region):
    # Überprüft, ob die Schreibweise der Region in der JSON und ggf. verbessert diese.

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        # Alle Regionen aus der Datenbank abrufen
        cursor.execute("SELECT DISTINCT region FROM codex_entry")
        all_regions = cursor.fetchall()
        all_regions = [r[0] for r in all_regions]

        # Mögliche Übereinstimmungen für die gegebene region finden
        # n=Anzahl der ähnlichen ausgaben
        # cutoff bestimmt die Ähnlichkeitsgrenze
        matches = get_close_matches(region, all_regions, n=1, cutoff=0.8)

        # Wenn eine Übereinstimmung gefunden wurde, gib sie zurück, ansonsten gib None zurück
        if matches:
            return matches[0]
        else:
            return 'None'


def ground_combat(journal_file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    ground_cz_table.clear_rows()
    with open(journal_file, 'r', encoding='UTF8') as datei:
        lauf = 0
        reward = 0
        for zeile in datei:
            data = read_json(zeile)
            if data['event'] == 'ApproachSettlement':
                timestamp = data.get('timestamp')
                log_time = (log_date(timestamp))
                date_log = (log_time[0] + "-" + log_time[1] + "-" + log_time[2])
                time_log = (log_time[3] + ":" + log_time[4] + ":" + log_time[5])

                if reward != 0:
                    reward = reward / 10
                    match reward:
                        case _ if reward > 50000:
                            insert_into_combat_zone(date_log, time_log, system_name, settlement, faction, 'high')
                        case _ if reward > 10000 and reward < 40000:
                            insert_into_combat_zone(date_log, time_log, system_name, settlement, faction, 'medium')
                        case _ if reward < 10000:
                            insert_into_combat_zone(date_log, time_log, system_name, settlement, faction, 'low')

                settlement = data['Name']
                system_address = data['SystemAddress']
                system_name = get_system(system_address)

                body_name = data['BodyName']
                lauf = 1
                reward = 0
            if data['event'] == 'FactionKillBond' and lauf < 11:
                faction = data['AwardingFaction']
                reward = reward + int(data['Reward'])
                lauf += 1
        if reward != 0:
            timestamp = data.get('timestamp')
            log_time = (log_date(timestamp))
            date_log = (log_time[0] + "-" + log_time[1] + "-" + log_time[2])
            time_log = (log_time[3] + ":" + log_time[4] + ":" + log_time[5])

            reward = reward / 10
            match reward:
                case _ if reward > 50000:
                    insert_into_combat_zone(date_log, time_log, system_name, settlement, faction, 'high')
                case _ if reward > 10000 and reward < 40000:
                    insert_into_combat_zone(date_log, time_log, system_name, settlement, faction, 'medium')
                case _ if reward < 10000:
                    insert_into_combat_zone(date_log, time_log, system_name, settlement, faction, 'low')


def tick_true():
    global tick
    tick = True


def tick_false():
    global tick
    tick = False


auto_refresh_lauf = 0


def auto_refresh():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    global auto_refresh_lauf

    if auto_refresh_lauf == 1:
        return

    if eddc_modul in {13, 4}:  # Prüfen und verlassen, wenn Modul nicht verarbeitet werden soll
        return

    auto_refresh_lauf = 1

    def update_progress():
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)
        # """Aktualisiert den Fortschritt, während 'Auswertung läuft'."""
        eddc_text_box.delete(1.0, "end")
        eddc_text_box.insert("end", "Auswertung läuft\n\n")
        lauf = 0
        # Punkt-Fortschritt in der Textbox anzeigen
        while check_auto_refresh.get() != 0:
            if lauf == 20:
                break
            t.sleep(0.5)
            if lauf == 0:
                eddc_text_box.insert("end", "\n")
            eddc_text_box.insert("end", ".")
            eddc_text_box.see("end")
            lauf += 1

    def start_refresh():
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)
        # """Starte die Auswertung und bereite die Tabellen vor."""
        # refreshing()  # Vorbereitung und Tabelle löschen

        # Auswertung als Thread starten
        auswertung_thread = threading.Thread(target=auswertung, args=(eddc_modul,))
        auswertung_thread.start()
        auswertung_thread.join()

    # Threads für Fortschritt und Auswertung starten
    progress_thread = threading.Thread(target=update_progress)
    refresh_thread = threading.Thread(target=start_refresh)

    progress_thread.start()
    refresh_thread.start()

    refresh_thread.join()  # Warten bis die Auswertung beendet ist
    progress_thread.join()  # Warten bis der Fortschritt beendet ist
    # Falls Checkbox noch aktiv ist, erneut aufrufen
    if check_auto_refresh.get() != 0:
        auto_refresh_lauf = 0
        auto_refresh()  # Rekursiv aufrufen für kontinuierliches Refreshing
    auto_refresh_lauf = 0


def refreshing():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    # Falls Modul Kompass oder Codex, Funktion verlassen
    if eddc_modul in {13, 4}:
        return

    eddc_text_box.delete(1.0, "end")
    eddc_text_box.insert("end", "Auswertung läuft\n\n")
    t.sleep(0.2)

    tables = [bgs, voucher, mats_table, tw_pass_table, tw_rescue_table, tw_cargo_table,
              thargoid_table, boxel_table, codex_bio_table, codex_stars_table, system_scanner_table]

    for table in tables:
        try:
            table.clear_rows()
        except AttributeError:
            logger(f"NoData in {table}", 2)


def threading_auto():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    global eddc_modul
    start_auto = threading.Thread(target=auto_refresh)

    var_code = [7, 8, 4, 13]
    if eddc_modul in var_code:
        logger('Ignore Auto Refresh', 2)
        return

    if eddc_modul == 4:
        logger('AUTO CODEX = 1 ', 5)
        custom_table_view()

    elif check_auto_refresh.get() != 0 and auto_refresh_lauf == 0:
        start_auto.start()
    else:
        if not start_auto.is_alive() and auto_refresh_lauf == 0:
            auswertung(eddc_modul)
    update_eddc_db()


def logging():
    global log_var
    log_var += 1
    print(log_var)


def mats_auslesen(journal_file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    mats = []
    mats_table.clear_rows()
    t1 = get_time()
    with open(journal_file, 'r', encoding='UTF8') as datei:
        for zeile in datei:
            search_string = 'MaterialCollected'
            if (zeile.find(search_string)) > -1:
                data = read_json(zeile)
                engineering_mats(data)
    t2 = get_time()
    logger('Mats all ' + str(timedelta.total_seconds(t2 - t1)), 2)


def ody_mats_auslesen(journal_file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    mats_table.clear_rows()
    test_data = []
    with open(journal_file, 'r', encoding='UTF8') as datei:
        for zeile in datei:
            search_string = 'BackpackChange'
            if (zeile.find(search_string)) > -1:
                data = read_json(zeile)
                try:
                    for xx in data['Added']:
                        state = 1
                        extract_engi_stuff(xx, state)
                        test_data.append(xx.get('Name_Localised'))
                except KeyError:
                    state = (-1)
                    for xx in data['Removed']:
                        extract_engi_stuff(xx, state)
                        test_data.append(xx.get('Name_Localised'))
    return test_data


def insert_codex_db(logtime, codex_name, icd_cmdr, codex_entry, category, region, icd_system):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    icd_log_time = (log_date(logtime))
    date_log = (icd_log_time[0] + "-" + icd_log_time[1] + "-" + icd_log_time[2])
    time_log = (icd_log_time[3] + ":" + icd_log_time[4] + ":" + icd_log_time[5])

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select = cursor.execute("""SELECT date_log, time_log, cmdr, codex_name, region FROM codex_data WHERE 
                                date_log = ? and
                                time_log = ? and
                                cmdr = ? and
                                codex_name = ? and
                                region = ?             
                                """, (date_log, time_log, icd_cmdr, codex_name, region)).fetchall()
        if not select:
            cursor.execute("INSERT INTO codex_data VALUES (?,?,?,?,?,?,?,?)",
                           (date_log, time_log, icd_cmdr, codex_name, codex_entry,
                            category, icd_system, region))
            connection.commit()


def read_json(zeile):
    try:
        if zeile == '\n':
            zeile = '{"timestamp": "2022-11-20T18:49:07Z", "event": "Friends", "Status": "Online"}'
        return json.loads(zeile)
    except ValueError:
        logger(('read_json', zeile), 2)
        zeile = '{"timestamp": "2022-11-20T18:49:07Z", "event": "Friends", "Status": "Online"}'
        data = json.loads(zeile)
        return data


def read_log_codex(data, journal_file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    rlc_cmdr = check_cmdr(journal_file, '')
    logtime = data['timestamp']
    codex_name = (data['Name'])
    codex_entry = (data['Name_Localised'])
    category = data['SubCategory']
    region = data['Region_Localised']
    region = get_correct_region(region)
    rlc_system = data['System']
    rbd_log_time = (log_date(data.get('timestamp')))
    date_log = (rbd_log_time[0] + "-" + rbd_log_time[1] + "-" + rbd_log_time[2])
    time_log = (rbd_log_time[3] + ":" + rbd_log_time[4] + ":" + rbd_log_time[5])

    if 'Thargoid' in codex_entry:
        codex_name = 'Xenological'
        category = '$Codex_SubCategory_Goid'

    if 'Terrestrials' in category:
        # print('IF ' + codex_entry)
        terra_state = ['(NT)', '(T)']
        codex_name = 'Terrestrials'
        codex_entry = serach_body(data, journal_file)
        # if not codex_entry:
        name = (data.get('Name'))
        match name:
            case '$Codex_Ent_Standard_Rocky_No_Atmos_Name;':
                codex_entry = 'Rocky body - ' + terra_state[0]
            case '$Codex_Ent_Standard_Ter_Rocky_Name;':
                codex_entry = 'Rocky body - ' + terra_state[0]
            case '$Codex_Ent_TRF_Ter_Rocky_Name;':
                codex_entry = 'Rocky body - ' + terra_state[1]
            case '$Codex_Ent_TRF_Rocky_No_Atmos_Name;':
                codex_entry = 'Rocky body - ' + terra_state[1]

            case '$Codex_Ent_Standard_Ter_Metal_Rich_Name;':
                codex_entry = 'Metal Rich - ' + terra_state[0]
            case '$Codex_Ent_Standard_Metal_Rich_No_Atmos_Name;':
                codex_entry = 'Metal Rich - ' + terra_state[0]
            case '$Codex_Ent_TRF_Ter_Metal_Rich_Name;':
                codex_entry = 'Rocky body - ' + terra_state[1]

            case '$Codex_Ent_Standard_Ter_Rocky_Ice_Name;':
                codex_entry = 'Rocky ice body - ' + terra_state[0]
            case '$Codex_Ent_Standard_Rocky_Ice_No_Atmos_Name;':
                codex_entry = 'Rocky ice body - ' + terra_state[0]
            case '$Codex_Ent_TRF_Ter_Rocky_Ice_Name;':
                codex_entry = 'Rocky ice body - ' + terra_state[1]

            case '$Codex_Ent_Standard_Ice_No_Atmos_Name;':
                codex_entry = 'Icy body - ' + terra_state[0]
            case '$Codex_Ent_Standard_Ter_Ice_Name;':
                codex_entry = 'Icy body - ' + terra_state[0]

            case '$Codex_Ent_Standard_Ter_High_Metal_Content_Name;':
                codex_entry = 'High metal content body - ' + terra_state[0]
            case '$Codex_Ent_TRF_Ter_High_Metal_Content_Name;':
                codex_entry = 'High metal content body - ' + terra_state[1]
            case '$Codex_Ent_Standard_High_Metal_Content_No_Atmos_Name;':
                codex_entry = 'High metal content body - ' + terra_state[0]
            case '$Codex_Ent_TRF_High_Metal_Content_No_Atmos_Name;':
                codex_entry = 'High metal content body - ' + terra_state[1]

            case '$Codex_Ent_Standard_Water_Worlds_Name;':
                codex_entry = 'Water World - ' + terra_state[0]
            case '$Codex_Ent_TRF_Water_Worlds_Name;':
                codex_entry = 'Water world - ' + terra_state[1]

            case '$Codex_Ent_Earth_Likes_Name;':
                codex_entry = 'Earth like world'

            case '$Codex_Ent_Standard_Ammonia_Worlds_Name;':
                codex_entry = 'Ammonia world'

    if 'Gas_Giants' in category:
        codex_entry = (data['Name'])
        codex_entry = str(codex_entry)
        codex_entry = codex_entry.replace('$Codex_Ent_Standard_', '')
        codex_entry = codex_entry.replace('$Codex_Ent_', '')
        codex_entry = codex_entry.replace('_', ' ')
        codex_entry = codex_entry.replace('Name;', '')
        codex_entry = codex_entry.replace('gas ;', '')
        codex_entry = codex_entry.replace('giant ;', '')

        codex_name = 'Gas Giant'

    if 'Stars' in category:
        new_name = codex_name.replace('Codex_Ent_', '')
        if ('_TypeGiant' or '_TypeSuperGiant') in new_name:
            new_name = new_name.replace('_TypeGiant', ' Type Giant')
            new_name = new_name.replace('_TypeSuperGiant', ' Type Supergiant')
        else:
            new_name = new_name.replace('_Type', ' Type Star')

        new_name = new_name.replace(';', '')
        new_name = new_name.replace('$', '')
        new_name = new_name.replace('_Name', '')
        new_name = new_name.replace('Stars', '')
        codex_entry = new_name.replace('_', ' ')

        codex_name = 'Stars'

    if 'Organic_Structures' in category:
        lauf = 0
        system_address = data.get('SystemAddress')
        body_id = data.get('BodyID')
        bodys = get_body_from_sc(logtime, system_address, journal_file)
        body = bodys[0]
        if not body and not body_id:
            body_id = find_body_data(journal_file, date_log, time_log)
        if not body and body_id:
            body = get_body(system_address, body_id)
        codex_entry = (data['Name_Localised'])
        codex_name = "Biological Discovery"
        ndl = data.get('NearestDestination_Localised', 'leer')
        if 'stellar' in ndl or 'Bemerkenswerte' in ndl:
            body = ''

        not_bios = ['Albulum Gourd Mollusc', 'Crystalline Shards', 'Bark Mounds', 'Albidum Peduncle Tree',
                    'Purpureum Metallic Crystals', 'Prasinum Ice Crystals', 'Flavum Metallic Crystals',
                    'Lindigoticum Ice Crystals', 'Rubeum Ice Crystals', 'Rubeum Metallic Crystals',
                    'Prasinum Metallic Crystals', 'Prasinum Bioluminescent Anemone',
                    'Roseum Bioluminescent Anemone', 'Biolumineszente Prasinum-Anemone',
                    'Solid Mineral Spheres', 'Lindigoticum Silicate Crystals',
                    'Cobalteum Rhizome Pod', 'Albidum Silicate Crystals', 'Crystals', 'tree'
                                                                                      'Roseum Ice Crystals', 'Crystals',
                    'Tubers', 'Brain Tree',
                    'Hirnbaum', 'kugeln', 'Metallkristalle', 'Kristallscherben', 'Silikatkristalle'
                                                                                 'Kugelmolluske', 'Eiskristalle',
                    'Stielbaum', 'Anemone', 'Stielhülse', 'scherben'
                                                          'Borkenhügel', 'Silikatkristalle', 'Leerenherz', 'hülse',
                    'Silikatkristalle', 'Windenknollen',
                    'molluske', 'Amphorenpflanze', 'kugeln', 'Kalkplatten', 'bäume', 'Aster']
        for i in not_bios:
            if i in codex_entry and lauf == 0:
                logtime = data.get('timestamp')
                insert_codex_db(logtime, codex_name, rlc_cmdr, codex_entry, category, region, rlc_system)
                codex_into_db(date_log, time_log, rlc_cmdr, codex_entry, '', rlc_system, body, region, 1)
                lauf = 1

        if ' - ' not in codex_entry and lauf == 0:
            logger(codex_entry, 2)
        if lauf == 0 and '- ' in codex_entry:
            tmp = codex_entry.split('-')
            codex_bio = str(tmp[0])
            bio_color = str(tmp[1])
            codex_bio = codex_bio.lstrip()
            bio_color = bio_color.lstrip()
            codex_bio = codex_bio.rstrip()
            bio_color = bio_color.rstrip()

            # t3 = get_time()
            if not body:
                logger('No Body found!' + codex_entry, 1)
                logger((date_log, time_log, rlc_cmdr, codex_bio, bio_color, rlc_system, body, region), 1)
            else:
                codex_into_db(date_log, time_log, rlc_cmdr, codex_bio, bio_color, rlc_system, body, region, 1)
            return

    if 'Geology_and_Anomalies' in category:
        codex_entry = (data['Name_Localised'])
        codex_name = "Geology and Anomalies"

    if 'Guardian' in category:
        codex_entry = (data['Name'])
        codex_entry = str(codex_entry)
        codex_entry = codex_entry.replace('$Codex_Ent_', '')
        codex_entry = codex_entry.replace('_', ' ')
        codex_entry = codex_entry.replace('Name;', '')
        codex_name = data['Category_Localised']

    if 'Thargoid' in category:
        codex_entry = (data['Name_Localised'])
        codex_name = data['Category_Localised']

    insert_codex_db(logtime, codex_name, rlc_cmdr, codex_entry, category, region, rlc_system)


def find_body_data(journal_file, date_log, time_log):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    cmdr = read_cmdr(journal_file)
    with open(journal_file, 'r', encoding='UTF8') as datei:
        for zeile in datei:
            data = read_json(zeile)
            event = data.get('event')
            match event:
                case 'Location':
                    get_info_for_get_body_name(data, cmdr)
                case 'ScanOrganic':
                    timestamp = data.get('timestamp')
                    # print(timestamp)
                    log_time = (log_date(timestamp))
                    new_date_log = (log_time[0] + "-" + log_time[1] + "-" + log_time[2])
                    new_time_log = (log_time[3] + ":" + log_time[4] + ":" + log_time[5])
                    if new_time_log == time_log and new_date_log == date_log:
                        body_id = data.get('Body')
                        return body_id


def new_bio_color(biodata, systemname, body):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        sql = "SELECT bio_color FROM codex where data = '" + biodata + "' and " \
                                                                       "systemname = '" + str(
            systemname) + "' and body = '" + str(body) + "'"
        cursor.execute(sql)
        result = cursor.fetchall()
        # print(result)
        if result:
            return result[0][0]


def get_body_from_sc(rlc_log_time, system_address, journal_file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    rlc_log_time = rlc_log_time.split('T')

    rlc_log_date = rlc_log_time[0]
    rlc_log_date = rlc_log_date.split('-')

    rlc_log_time = rlc_log_time[1]
    rlc_log_time = rlc_log_time.replace('Z', '')
    rlc_log_time = rlc_log_time.split(':')
    new = []
    disembark = []
    location = []

    date_codex = datetime(int(rlc_log_date[0]), int(rlc_log_date[1]), int(rlc_log_date[2]),
                          int(rlc_log_time[0]), int(rlc_log_time[1]), int(rlc_log_time[2]))
    with open(journal_file, 'r', encoding='UTF8') as datei:
        for zeile in datei:
            data = read_json(zeile)
            event = data.get('event')
            if event == 'SupercruiseExit':
                log_time = data.get('timestamp')
                log_time = log_time.split('T')
                log_date = log_time[0]
                log_date = log_date.split('-')
                log_time = log_time[1]
                log_time = log_time.replace('Z', '')
                log_time = log_time.split(':')
                date_disembark = datetime(int(log_date[0]), int(log_date[1]), int(log_date[2]),
                                          int(log_time[0]), int(log_time[1]), int(log_time[2]))
                if date_disembark < date_codex:
                    system_name = data.get('StarSystem')
                    body_name = data.get('Body')
                    body_name = body_name.replace(system_name, '')
                    new.append(body_name)
            if event == 'Disembark':
                log_time = data.get('timestamp')
                log_time = log_time.split('T')
                log_date = log_time[0]
                log_date = log_date.split('-')
                log_time = log_time[1]
                log_time = log_time.replace('Z', '')
                log_time = log_time.split(':')
                date_disembark = datetime(int(log_date[0]), int(log_date[1]), int(log_date[2]),
                                          int(log_time[0]), int(log_time[1]), int(log_time[2]))
                if date_disembark < date_codex:
                    system_name = data.get('StarSystem')
                    body_name = data.get('Body')
                    body_name = body_name.replace(system_name, '')
                    disembark.append(body_name)
            if event == 'Location':
                log_time = data.get('timestamp')
                log_time = log_time.split('T')
                log_date = log_time[0]
                log_date = log_date.split('-')
                log_time = log_time[1]
                log_time = log_time.replace('Z', '')
                log_time = log_time.split(':')
                date_disembark = datetime(int(log_date[0]), int(log_date[1]), int(log_date[2]),
                                          int(log_time[0]), int(log_time[1]), int(log_time[2]))
                if date_disembark < date_codex:
                    system_name = data.get('StarSystem')
                    body_name = data.get('Body')
                    body_name = body_name.replace(system_name, '')
                    location.append(body_name)
    if new != []:
        return (new[-1], system_name)
    else:
        if disembark != []:
            return (disembark[-1], system_name)
        else:
            if location != []:
                return (location[-1], system_name)


def get_system_data(system_address, body_id):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        sql = "SELECT SystemName, BodyName FROM planet_infos where SystemID = " \
              + str(system_address) + " and BodyID = " + str(body_id)
        cursor.execute(sql)
        result = cursor.fetchall()
        if result:
            return result[0]
        else:
            logger((funktion, 'no Body found'), log_var)
            star_select = cursor.execute("""SELECT starsystem, body_name FROM star_data WHERE 
                                                        System_address = ? and body_id = ? """,
                                         (system_address, body_id)).fetchall()
            if star_select:
                system_name = star_select[0][0]
                body_name = star_select[0][1]
                body_name = body_name.replace(system_name, '')
                return body_name


def read_body_info(file, system_address, body_id):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    system_address = str(system_address)
    body_id = 'BodyID":' + str(body_id)

    with open(file, 'r', encoding='UTF8') as datei:
        for zeile in datei:
            if (zeile.find(system_address)) > -1 and (zeile.find(body_id)) > -1:
                data = read_json(zeile)
                star_system = data.get('StarSystem')
                if not star_system:
                    continue
                # print(data)
                body = data.get('BodyName')
                if not body:
                    body = data.get('Body')
                # body = data.get('Body')
                star_system = data.get('StarSystem')
                body = body.replace(star_system + ' ', '')
                return star_system, body


def read_bio_data(data, journal_file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    biodata = (data.get('Species_Localised'))
    system_address_bio = data.get('SystemAddress')
    body_id = data.get('Body')
    if biodata is None or system_address_bio == 0:
        logger(('exit read_bio_data Data corrupt', data), 2)
        return

    # find Region with SystemAddress
    region = (findRegionForBoxel(system_address_bio)['region'][1])
    # print(findRegionForBoxel(system_address_bio))

    timestamp = str(data['timestamp'])
    rbd_log_time = (log_date(timestamp))
    date_log = (rbd_log_time[0] + "-" + rbd_log_time[1] + "-" + rbd_log_time[2])
    time_log = (rbd_log_time[3] + ":" + rbd_log_time[4] + ":" + rbd_log_time[5])
    system_infos = get_system_data(system_address_bio, body_id)
    if not system_infos:
        system_infos = read_body_info(journal_file, system_address_bio, body_id)
    try:
        rbd_system = system_infos[0]
        body = system_infos[1]
    except TypeError:
        system_infos = get_system_data(system_address_bio, body_id)
        rbd_system = system_infos[0]
        body = system_infos[1]
    color = data.get('Variant_Localised')
    if color:
        bio_color = color.replace(biodata, '')
        bio_color = bio_color.replace(' - ', '')
    else:
        bio_color = new_bio_color(biodata, rbd_system, body)
    # bio_color = ''

    # print(date_log, time_log, biodata, bio_color, rbd_system, body, region)
    bio_cmdr = check_cmdr(journal_file, '')
    codex_into_db(date_log, time_log, bio_cmdr, biodata, bio_color, rbd_system, body,
                  region, 0)


def read_log(filename, search_string, item):
    global success
    # print(search_string, item)
    temp = []
    with open(filename, 'r', encoding='UTF8') as datei:
        for zeile in datei:
            if zeile.find(search_string) > -1:
                data = read_json(zeile)
                temp.append(data[item])
        if temp:
            success = TRUE
            # print(success, temp, filename)
        else:
            success = FALSE
            # print(success, temp, filename)
        return temp


def read_cmdr(file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    cc_cmdr = ""
    with open(file, 'r', encoding='UTF8') as datei:
        logger(file, log_var)
        for zeile in datei:
            search_string = '"event":"Commander"'
            if zeile.find(search_string) > -1:
                data = read_json(zeile)
                cc_cmdr = data.get('Name', 'UNKNOWN')
                return cc_cmdr
        # print(zeile)
        zeilen = datei.readlines()
        if len(zeilen) == 0:
            return 'UNKNOWN'
        data = read_json(zeile)
        if data.get('event') == 'Shutdown':
            return 'UNKNOWN'


def codex_into_db(date_log, time_log, cid_cmdr, data, bio_color, systemname, body, region, codex):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    # print(bio_color)

    body = body.lstrip()
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()

        item = cursor.execute("""SELECT * FROM codex WHERE
                                cmdr = ? and 
                                data = ? and
                                systemname = ? and
                                body = ? and
                                region = ? 
                                """, (cid_cmdr, data, systemname, body, region)).fetchall()

        if not item:
            cursor.execute("INSERT INTO codex VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (date_log, time_log, cid_cmdr, data, bio_color, systemname, body, region, codex, 0))
            connection.commit()
            # sql = "INSERT INTO codex VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"


def insert_into_death_db(date_log, time_log, iid_cmdr):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select = cursor.execute("""SELECT * FROM player_death WHERE 
                                date_log = ? and time_log = ? and cmdr = ?""",
                                (date_log, time_log, iid_cmdr)).fetchall()
        # print(select)
        if not select:
            cursor.execute("INSERT INTO player_death VALUES (?, ?, ?)", (date_log, time_log, iid_cmdr))
        connection.commit()


def get_body(system_address, body_id):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        star_select = cursor.execute("""SELECT SystemName, Bodyname FROM planet_infos WHERE 
                                SystemID = ? and BodyID = ? """, (system_address, body_id)).fetchall()
        if not star_select:
            star_select = cursor.execute("""SELECT starsystem, body_name FROM star_data WHERE 
                                                        System_address = ? and body_id = ? """,
                                         (system_address, body_id)).fetchall()
        if star_select:
            return str(star_select[0][0] + star_select[0][1])


def insert_into_last_sell(date_log, time_log, iis_sell, iis_cmdr):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    # print(bio_color)
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select = cursor.execute("""SELECT * FROM selling WHERE 
                                date_log = ? and time_log = ? and sell = ?""",
                                (date_log, time_log, iis_sell)).fetchall()
        # print(select)
        if not select:
            cursor.execute("INSERT INTO selling VALUES (?, ?, ?, ?)", (date_log, time_log, iis_sell, iis_cmdr))
        connection.commit()


def read_player_death(filename):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    tod_log = read_log(filename, '"event":"Died"', 'timestamp')  # Time of Death from Logfiles
    # print(tod_log, success)
    if tod_log:
        # print('Test')
        cmdr_names = read_log(filename, '"event":"Commander"', 'Name')
        cmdr_names = cmdr_names[0]
        # print(tod_log)
        for tod in tod_log:
            timestamp = tod
            tod = (log_date(timestamp))
            date_log = (tod[0] + "-" + tod[1] + "-" + tod[2])
            time_log = (tod[3] + ":" + tod[4] + ":" + tod[5])
            # print(date_log, time_log, cmdrs)
            insert_into_death_db(date_log, time_log, cmdr_names)
    multi_sell(filename)


def multi_sell(filename):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    cmdr_names = ''

    multi_sell_expo_data = read_log(filename, '"event":"MultiSellExplorationData"', 'timestamp')
    if multi_sell_expo_data:
        for i in multi_sell_expo_data:
            sell_time = (log_date(i))
            date_log = (sell_time[0] + "-" + sell_time[1] + "-" + sell_time[2])
            time_log = (sell_time[3] + ":" + sell_time[4] + ":" + sell_time[5])
            sell_type = 'Multisell ExplorationData'
            # print(date_log, time_log, sell_date)
            if success:
                cmdr_names = read_log(filename, '"event":"Commander"', 'Name')
                cmdr_names = cmdr_names[0]
            insert_into_last_sell(date_log, time_log, sell_type, cmdr_names)


def worth_it(search_data):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    y = 0
    with sqlite3.connect(database) as connection:
        for i in search_data:
            if view_name == 'system_scanner':
                bio = i[3]
            else:
                bio = i[4]
            bio = '%' + bio + '%'
            cursor = connection.cursor()
            select = cursor.execute("SELECT worth FROM codex_entry WHERE data like ? and region = 'Galactic Centre'",
                                    (bio,)).fetchone()
            if select:
                new = str(select[0])
                x = new.replace(',', '')
            else:
                x = 0
            y += int(x)
    return y


def insert_into_planet_bio_db(body_name, body_id, count, region, bio_genus):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select = cursor.execute("""SELECT body from planet_bio_info where body = ?""",
                                (body_name,)).fetchall()

        select_genus = cursor.execute("""SELECT bio_genus from planet_bio_info where body = ?""",
                                      (body_name,)).fetchall()

        if select == []:
            cursor.execute("INSERT INTO planet_bio_info VALUES (?,?,?,?,?)",
                           (body_name, body_id, count, region, bio_genus))
            connection.commit()

        if bio_genus and select != [] and select_genus == [('',)]:
            cursor.execute("""UPDATE planet_bio_info SET bio_genus = ? 
                                where body = ? and body_id = ? and region = ?""",
                           (bio_genus, body_name, body_id, region))
            connection.commit()


def insert_into_bio_db(body_name, bio_scan_count, genus, species, color, mark_missing):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        bio_scan_count = int(bio_scan_count)
        select = cursor.execute("""SELECT bio_scan_count from bio_info_on_planet where body = ? and genus = ? 
                                    and species = ?""",
                                (body_name, genus, species)).fetchall()

        if not select:
            cursor.execute("INSERT INTO bio_info_on_planet VALUES (?,?,?,?,?)",
                           (body_name, genus, species, bio_scan_count, mark_missing))
            connection.commit()
        elif int(bio_scan_count) > int(select[0][0]):
            cursor.execute("""UPDATE bio_info_on_planet SET bio_scan_count = ?
                            WHERE body = ? AND genus = ? AND species = ? """,
                           (bio_scan_count, body_name, genus, species))
            connection.commit()


def update_bio_db(body_name, bio_scan_count, genus, species):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select = cursor.execute("""SELECT bio_scan_count from bio_info_on_planet where body = ? and genus = ? 
                                     and species = ?""",
                                (body_name, genus, species)).fetchall()


def get_data_from_DB(file, current_system):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select = cursor.execute("""SELECT date_log, time_log, SystemID, SystemName, Main_Star, Local_Stars, 
        BodyName, BodyID, DistanceToMainStar, Tidal_lock, Terraform_state, PlanetType, Atmosphere, Gravity, 
        Temperature, Pressure, Landable, volcanism, sulphur_concentration, Rings, Mass, Radius, SemiMajorAxis, 
        Eccentricity, OrbitalInclination, Periapsis, OrbitalPeriod, AscendingNode, MeanAnomaly, RotationPeriod, 
        AxialTilt, Discovered, Mapped, Materials, cmdr FROM planet_infos where SystemName = ? and landable = 1 and 
        Atmosphere like '%atmosphere%' """, (current_system[0],)).fetchall()
        cmdr = cursor.execute("Select CMDR from logfiles where Name = ?", (file,)).fetchone()
    if not cmdr:
        cmdr = check_cmdr(file, '')
    if select == []:
        return ' '
    new = []
    active_body = activ_planet_scan(file)
    first = []
    for i in select:  # Nun werden nur die Körper mit Odyssey Bio Signalen herausgefiltert
        body = i[3] + i[6]
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            select2 = cursor.execute("""SELECT * FROM planet_bio_info where body = ? """, (body,)).fetchall()
        if select2 != []:
            if body == active_body:
                first.append(i)
            else:
                new.append(i)
    for a in new:  # Damit der zuletzt betretene oder gescannte Trabant im Fokus steht.
        first.append(a)
    t1 = get_time()
    data = get_biodata_from_planet(cmdr[0], first)
    t2 = get_time()
    # print('get_biodata_from_planet ' + str(timedelta.total_seconds(t2 - t1)))
    return data


def missing_bio_test(bio, region):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        query = f'''SELECT * FROM codex where data like "{bio}" and region = "{region}"'''
        run_query = cursor.execute(query).fetchall()
        # print(run_query)
        if run_query:
            return 0
        else:
            return 1


def get_codex_color(bio, system_name, body):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    # logger((bio, system_name, body), 2)
    body = body.lstrip(' ')

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()

        color = cursor.execute("""SELECT bio_color FROM CODEX where SystemName = ? and BODY = ? and 
                                        data = ? """, (system_name, body, bio)).fetchone()

        distance = cursor.execute("""SELECT DISTINCT(distance) FROM bio_color where Name = ? """, (bio,)).fetchone()
        if not color:
            color = ['Unknown', 0]
        return color[0], distance[0]


def correct_star_data(system_address):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select = cursor.execute("Select startype from star_data where system_address = ? WHERE Main = 1",
                                (system_address,)).fetchall()
        star = str(select[0][0])
        cursor.execute("Update planet_infos Set Main_Star = ? where SystemID = ?", (star, system_address))
        connection.commit()
        return star


def filter_letters_only(input_list):
    filtered_list = [element for element in input_list if element.isalpha()]
    return filtered_list


def extract_planet_data(i):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    system_address = int(i[2])
    system_name = str(i[3])
    body = str(i[6])
    body_name = str(i[3]) + str(i[6])
    main_star_class = []
    if i[4] == None:
        logger('Hoppla', 1)
        main_star_class.append(str(correct_star_data(system_address)))
    else:
        main_star_class.append(str(i[4]))
    local_star = str(i[5])
    local_star = local_star.split(', ')
    for ls in local_star:
        main_star_class.append(ls)
    distance = str(i[8])
    planet_type = str(i[11])
    body_atmos = str(i[12])
    body_gravity = str(i[13])
    body_temp = float(i[14])
    body_pressure = float(i[15])
    volcanism = str(i[17])
    sulphur_concentration = float(i[18])
    materials = str(i[33])
    material = materials.split(' ')

    if not main_star_class:
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            main_sql = f'''SELECT startype FROM star_data where 
                            system_address = {system_address} and main = 1'''
            main_star_class = cursor.execute(main_sql).fetchone()

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        b_count = cursor.execute("SELECT count FROM planet_bio_info where body = ?",
                                 (body_name,)).fetchall()
    if b_count:
        bio_count = b_count[0][0]
    else:
        bio_count = 0

    return (system_address, system_name, body, body_name, main_star_class, local_star, distance,
            planet_type, body_atmos, body_gravity, body_temp, body_pressure, volcanism,
            sulphur_concentration, material, bio_count)


# Welche Bios gibt es auf dem Himmelskörper
def get_biodata_from_planet(cmdr, select):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    data_2 = []
    if not select:
        logger((funktion, 'select leer'), 2)
        return ''

    address = (select[0][2])
    region = (findRegionForBoxel(address)['region'][1])

    for i in select:
        (system_address, system_name, body, body_name, main_star_class, local_star, distance,
         planet_type, body_atmos, body_gravity, body_temp, body_pressure, volcanism,
         sulphur_concentration, material, bio_count) = extract_planet_data(i)

        bio_names = []
        bio = []
        bcd = []
        iob = ''

        potential_bios = []
        main_star_class = list(dict.fromkeys(main_star_class))  # löscht doppelte Eintrage in der Liste
        for star_class in main_star_class:
            if star_class != '':
                temp = select_prediction_db(star_class, planet_type, body_atmos,
                                            body_gravity, body_temp, body_pressure, volcanism, sulphur_concentration)
                for t in temp:
                    for bio_a in t:
                        potential_bios.append(bio_a)
        new_list = []
        potential_bios = list(dict.fromkeys(potential_bios))  # löscht doppelte Eintrage in der Liste

        if main_star_class[1] is not None:
            local = ((str(main_star_class[1])).lstrip())
            if local == main_star_class[0]:
                main_star_class = main_star_class[0]

        all_stars = ''
        for star_class in main_star_class:
            if star_class != '':
                if all_stars != '':
                    all_stars = all_stars + ', ' + str(star_class)
                all_stars = all_stars + str(star_class)
                for bio in potential_bios:
                    pass_var = 0
                    get_cod = get_color_or_distance(bio, star_class, material)
                    # print(bio, get_cod)
                    if get_cod:
                        for count, i in enumerate(bcd):
                            if bio in i:
                                new = (get_cod[1][0]) + (bcd[count][1])
                                bcd[count] = bcd[count][0], new, bcd[count][2]
                                pass_var = 1
                        if pass_var != 1:
                            bio2 = (bio, get_cod[1][0], (get_cod[0]))
                            if get_cod[1]:
                                bcd.append(bio2)
                                pass_var = 0

        # region = (findRegionForBoxel(system_address)['region'][1])
        # missing_in_region = (missing_codex(cmdr, region))
        missing_bio = []
        atmo = body_atmos.replace('atmosphere', '')
        atmo = atmo.replace('thin', '')
        atmo = atmo.replace('thick', '')
        atmo = atmo.lstrip()
        atmo = atmo.capitalize()
        if int(bio_count) > 0:
            data_2.append((body_name, distance, bio_count, all_stars, atmo, '', '', '', region, ''))
        # for i in missing_in_region:
        #     missing_bio.append(i[3])
        mark_missing = 0

        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            select_bios_on_body = cursor.execute("""SELECT * from bio_info_on_planet where body = ?
            and bio_scan_count >= 0 Order by genus""", (body_name,)).fetchall()
            select_complete_bios_on_body = cursor.execute("""SELECT COUNT(species) from bio_info_on_planet 
                    where body = ? and bio_scan_count = 3""", (body_name,)).fetchall()

        species_all = []
        genus_all = []
        for bios in select_bios_on_body:
            bio_2 = bios[1] + ' ' + bios[2]
            species, genus = bio_2.split(' ')
            select_scan_type = f'''SELECT scantype FROM bio_scan_data where             
            body_name = "{body_name}" and bio = "{bio_2}" ORDER by time_log desc LIMIT 1'''
            select_scan_type_exe = cursor.execute(select_scan_type).fetchone()
            scan = ' '
            gcc = get_codex_color(bio_2, system_name, body)
            if gcc[0] == 'Unknown':
                cod = get_color_or_distance(bio_2, main_star_class[0], material)
                if cod:
                    gcc = cod[1][0][0], gcc[1]
                else:
                    continue
            if select_scan_type_exe[0] == 'Log':
                scan = 'Scan in Progress 1 / 3'
            elif select_scan_type_exe[0] == 'Sample':
                scan = 'Scan in Progress 2 / 3'
            elif select_scan_type_exe[0] == 'Analyse':
                scan = 'Scan completed   3 / 3'

            if gcc:
                gcod_color = gcc[0]
                gcod_bio_distance = gcc[1]
                worth = worth_it([(0, 0, 0, genus)])
                worth = (f'{worth:,}'.replace(',', '.'))
                # worth = worth_it(i[2])
                data_2.append(('', '', '', species, genus, worth, gcod_color, gcod_bio_distance, scan, 0))
                species_all.append(str(genus))
                genus_all.append(str(species))

        if bio_count != int(select_complete_bios_on_body[0][0]):
            for count, i in enumerate(bcd):
                bio_name = i[0].split(' ')
                # logger((body_name, bio_name), log_var)
                genus = bio_name[0]
                genus2 = ''
                species = bio_name[1]
                temp = genus.capitalize() + ' ' + species.capitalize()
                color = i[1]
                bio_distance = i[2]
                mark_missing = missing_bio_test(temp, region)
                # if temp in missing_bio:
                #     mark_missing = 1
                # else:
                #     mark_missing = 0
                bio_scan_count = get_bio_scan_count(temp, body_name)
                if (bio_scan_count) is None:
                    logger('bio_scan_count = 0', 1)
                    continue
                insert_into_bio_db('body_name', bio_scan_count[1], genus.capitalize(),
                                   species.capitalize(), color, mark_missing)
                if genus.capitalize() in genus_all:
                    continue
                if species.capitalize() in species_all:
                    continue
                if count > 0:
                    # print(bcd[count - 1][0], 'Name')
                    bio_name = str(bcd[count - 1][0]).split(' ')
                    genus2 = bio_name[0]
                marked = 0
                fdg = check_genus(body_name, genus)  # Wenn der Planet mit dem DOS gescannt wurde
                if fdg is not None:
                    identified_on_body = str(fdg[0])
                    iob = identified_on_body.split(', ')
                    del iob[0]  # erste Element wird gelöscht. bio_genus [, Bacterium, Tubus]
                    if genus.capitalize() in iob:  # Nur die Bios sollen übernommen werden die auch der DOS erkannt hat
                        marked = 1
                else:  # Alle Bios werden übernommen, wenn kein DOS ausgeführt wurde.
                    marked = 1
                if genus == genus2:
                    genus = ''
                else:
                    genus2 = genus
                if marked == 1:
                    worth = worth_it([(0, 0, 0, species.capitalize())])
                    worth = (f'{worth:,}'.replace(',', '.'))
                    data_2.append(('', '', '', genus.capitalize(), species.capitalize(),
                                   worth, color, bio_distance, '', mark_missing))
    if data_2:
        # logger(('data_2', data_2), 2)
        return data_2


def serach_body(data, file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    timestamp = data.get('timestamp')

    with open(file, 'r', encoding='UTF8') as datei:
        for zeile in datei:
            new_data = read_json(zeile)
            if timestamp == new_data.get('timestamp'):
                # print('yeahhhh')
                # print(new_data)
                type_list = ['Ammonia world', 'Water world', 'Earthlike body']
                if new_data.get('event') == 'Scan':
                    type = new_data.get('PlanetClass')
                    terraform_state = new_data.get('TerraformState')
                    if terraform_state == '' and type not in type_list:
                        terraform_state = 'Non Terraformable'
                    if type:
                        if type not in type_list:
                            codex_entry = type + ' - ' + terraform_state
                            return codex_entry
                        else:
                            return type


def set_system(data, cmdr):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    event = data.get('event')
    timestamp = data.get('timestamp')
    log_time = (log_date(timestamp))
    date_log = (log_time[0] + "-" + log_time[1] + "-" + log_time[2])
    time_log = (log_time[3] + ":" + log_time[4] + ":" + log_time[5])
    system_id = data.get('SystemAddress')
    system_name = data.get('StarSystem')

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select = cursor.execute("""SELECT * from flight_log 
                                    where date_log = ? and time_log = ? and SystemID = ?""",
                                (date_log, time_log, system_id)).fetchall()
        if not select:
            cursor.execute("""INSERT INTO flight_log VALUES (?,?,?,?,?,?)""",
                           (date_log, time_log, system_id, system_name, event, cmdr))
            connection.commit()
    return date_log, time_log, system_id, system_name


def get_last_system_in_db():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select = cursor.execute("""SELECT SystemName FROM flight_log where
                                    date_log = (SELECT date_log FROM flight_log ORDER BY date_log DESC LIMIT 1)
                                    ORDER BY time_log DESC LIMIT 1""").fetchall()
        #
        # select = cursor.execute("""SELECT SystemName FROM flight_log where systemname = 'Aucoks XK-M d8-11'"""
        #                         ).fetchall()
        if select:
            return select[0]
        else:
            return [' ']


def read_data_from_last_system(file, mission_id):  # NEEDS REVIEW
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    starsystem = ''
    go = 0

    # with open(file, 'r', encoding='UTF8') as datei:
    #     for zeile in datei.readlines():
    #         data = read_json(zeile)
    #         if data.get('event', 0) == 'Commander':
    #             cmdr = data.get('Name', '0')
    with open(file, 'r', encoding='UTF8') as datei_2:
        for zeile in reversed(file):  # Read File line by line reversed!
            data = read_json(zeile)
            if data['event'] == 'MissionAccepted':
                mission = data.get('MissionID')
                if mission == mission_id:
                    go = 1
            if go == 1:
                if data['event'] == 'Docked':
                    starsystem = data['StarSystem']
                    return starsystem
                if data['event'] == 'Location':
                    starsystem = data['StarSystem']
                    return starsystem
                if data['event'] == 'Disembark':
                    starsystem = data['StarSystem']
                    return starsystem
                if data['event'] == 'FSDJump':
                    starsystem = data['StarSystem']
                    return starsystem


def send_to_discord(content):
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute("""SELECT * FROM server""")
        result = cursor.fetchall()
        if result != []:
            web_hock_user = result[0][1]
            webhook_url = result[0][0]
            eddc_user = result[0][2]
            if webhook_url and web_hock_user and eddc_user:
                data = {
                    "content": content,  # Den Content geben wir der Funktion mit...
                    "username": web_hock_user  # ... und den Username haben wir eh schon hinterlegt... ;-)
                }
                post(webhook_url, data=data)


def war_progress():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    eddc_text_box.insert(END, 'Daten werden eingelesen \n')
    filenames = file_names(2)
    for file in filenames:
        logger(file, log_var)
        with open(file, 'r', encoding='UTF8') as datei:
            for line_nr, zeile in enumerate(datei):
                data = read_json(zeile)
                event = data.get('event')
                match event:
                    case 'Location':
                        thargoid_war_data(data)
                    case 'FSDJump':
                        thargoid_war_data(data)
    eddc_text_box.delete('1.0', END)

    war_data_to_online_db()
    update_thargoid_war()
    b_filter = filter_entry.get()
    if b_filter:
        auswertung_thargoid_war(b_filter)
    show_war_data()


def check_last(file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        last_line_in_db = cursor.execute("""SELECT last_line FROM logfiles where
                                    name = ? """, (file,)).fetchall()
    if last_line_in_db:
        lines_in_file = count_lines_efficiently(file)

        if (last_line_in_db[0][0] + 1) == lines_in_file:
            return 1
        else:
            return 0


def reset_pos():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE from eddc_positions")
        cursor.execute("INSERT INTO eddc_positions (x, y) VALUES (130, 130)")
        cursor.execute("INSERT INTO eddc_positions (x, y) VALUES (130, 130)")
        cursor.execute("INSERT INTO eddc_positions (x, y) VALUES (130, 130)")
        cursor.execute("INSERT INTO eddc_positions (x, y) VALUES (130, 130)")
        connection.commit()
        cursor.execute("SELECT x, y FROM eddc_positions where id = 1")
        position = cursor.fetchone()
        if position:
            root.geometry("+{}+{}".format(position[0], position[1]))


def read_codex_data(rcd_cmdr, rcd_region):  # Data for Codex_stars
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    if log_var > 4:
        logger((rcd_cmdr, rcd_region), log_var)
    selected_value = combo_bio_data.get()
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        b_date = begin_time.get()
        e_date = end_time.get()
        sql_beginn = f'''SELECT ROW_NUMBER() OVER(ORDER BY date_log DESC, time_log DESC) AS Row, 
                        date_log, time_log, cmdr, codex_name, codex_entry, system, region 
                        FROM codex_data WHERE date_log >= '{b_date}' and date_log <= '{e_date}' and '''

        sql_end = f'''category not like '%Organic_Structures%' ORDER by date_log DESC, time_log DESC'''
        part = ''
        if rcd_region:
            part = part + 'region = "' + rcd_region + '" and '
        if rcd_cmdr:
            part = part + 'cmdr = "' + rcd_cmdr + '" and '

        if selected_value in ['Star', 'Carbon-Stars', 'Giant Stars', 'Gas Giant', 'Proto Stars',
                              'Brown Dwarfs', 'Non-Sequenz Stars', 'Terrestrials', 'Geology and Anomalies',
                              'Xenological']:
            if selected_value == 'Giant Stars':
                selected_value = '%giant%'
                part = part + 'codex_entry like "' + selected_value + '" and '
            elif selected_value == 'Proto Stars':
                part = part + '(codex_entry like "AeBe Type Star" or codex_entry like "T Tauri Star") and '
            elif selected_value == 'Brown Dwarfs':
                part = part + '(codex_entry like "%L% Type Star" or codex_entry like "%T %Type Star" or ' \
                              'codex_entry like "%Y% Type Star") and '
            elif selected_value == 'Carbon-Stars':
                part = part + '(codex_entry like "C Type Giant" or codex_entry like "CJ Type Giant" or ' \
                              'codex_entry like "CN Type Giant" or codex_entry like "MS Type Giant" or ' \
                              'codex_entry like "S Type Giant") and '
            elif selected_value == 'Non-Sequenz Stars':
                part = part + '(codex_entry like "Black Hole" or codex_entry like "%D% Type Star" ' \
                              'or codex_entry like "%W% Type Star") and '
            else:
                selected_value = '%' + selected_value + '%'
                part = part + 'codex_name like "' + selected_value + '" and '
            # print(selected_value + sql_beginn + part + sql_end)
            select = cursor.execute(sql_beginn + part + sql_end).fetchall()
            return select

        if selected_value not in ['', '<- back', None]:
            if selected_value in ['A', 'O', 'B', 'F', 'G', 'K', 'M', 'MS', 'S', 'L', 'T', 'Y']:
                selected_value = 'like "' + selected_value + ' Type%'
            elif selected_value in ['White Dwarf', 'Wolf-Rayet', 'Carbon-Star']:
                my_list = ['White Dwarf', 'Wolf-Rayet', 'Carbon-Star']
                translate = ['D', 'W', 'C']
                selected_value = translate[my_list.index(selected_value)]

                selected_value = 'like "' + selected_value + '%% Type %'
            elif selected_value in ['<- back', 'Gas Giant With Ammonia Life', 'Gas Giant With Water Life',
                                    'Sudarsky Class I',
                                    'Sudarsky Class II', 'Sudarsky Class III', 'Sudarsky Class IV',
                                    'Sudarsky Class V']:
                selected_value = '= "' + selected_value + ' '
            elif selected_value == 'Herbig AeBe':
                selected_value = 'like "%AeBe Type Star%'
            else:
                selected_value = 'like %' + selected_value + '%'
            part = part + 'codex_entry ' + selected_value + '" and '
            logger(sql_beginn + part + sql_end, log_var)
            select = cursor.execute(sql_beginn + part + sql_end).fetchall()
            return select
        select = cursor.execute(sql_beginn + part + sql_end).fetchall()
        return select


is_custom_table_view_open = False


def custom_table_view():
    global tree, view_name, backup_row
    global is_custom_table_view_open

    if is_custom_table_view_open:
        return
    is_custom_table_view_open = True
    backup_row = ['']
    # normal_view = 0
    active_view = ['bio_codex', 'stellar_codex', 'system_scanner']
    view_name = 'bio_codex'
    tree = customtkinter.CTkToplevel()
    tree.title('Display Codex Data')

    def on_close():
        global is_custom_table_view_open, aus_var
        is_custom_table_view_open = False
        aus_var = 0
        tree.destroy()

    tree.protocol("WM_DELETE_WINDOW", on_close)

    # load_position()
    load_position(tree, 2, 1200, 570)

    tree.minsize(1200, 570)
    tree.maxsize(1200, 600)
    tree.after(100, lambda: tree.focus_force())
    try:
        img = resource_path("eddc.ico")
        # tree.iconphoto(False, PhotoImage(file=img))
        tree.iconbitmap(img)
    except TclError:
        logger('Icon not found', 1)

    if sys.platform.startswith("win"):
        tree.after(200, lambda: tree.iconbitmap(img))
    tree.bind("<Configure>", lambda event: save_position(tree, 2))

    menu_tree = Menu(tree)
    tree.config(menu=menu_tree)
    file_menu = Menu(menu_tree, tearoff=False)
    # menu_tree.add_cascade(label="More", menu=file_menu)
    menu_tree.add_cascade(label="Bio Scans", command=lambda: switch_view('bio_codex'))
    menu_tree.add_cascade(label="Missing Bio Codex", command=lambda: switch_view('missing_codex'))
    menu_tree.add_cascade(label="Codex Stars", command=lambda: switch_view('stellar_codex'))
    menu_tree.add_cascade(label="System Scanner", command=lambda: switch_view('system_scanner'))

    bg_treeview = customtkinter.CTkImage(dark_image=Image.open(resource_path("bg_treeview.png")),
                                         size=(1200, 570))
    background_label = customtkinter.CTkLabel(tree, bg_color='black', image=bg_treeview, text='')
    background_label.place(relwidth=1, relheight=1)
    global buttons_frame
    buttons_frame = customtkinter.CTkFrame(tree, bg_color='black', fg_color='black')
    buttons_frame.pack(fill=X, pady=15)

    def selected(var):
        global filter_region, filter_cmdr, filter_bdata
        filter_region = combo_regions.get()
        filter_cmdr = combo_cmdr.get()
        filter_bdata = combo_bio_data.get()
        refresh_codex_data(view_name)

    def create_button():
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)

        global combo_cmdr, combo_regions, combo_bio_data, refresh_button, sorting
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            select_cmdr = cursor.execute("SELECT DISTINCT cmdr FROM codex ORDER BY cmdr").fetchall()
            select_region = cursor.execute("SELECT DISTINCT region FROM codex ORDER BY region").fetchall()

        b_data = [('')]
        cmdrs = [('')]
        region = [('')]

        # if normal_view != 4:
        for i in select_cmdr:
            cmdrs = cmdrs + [i[0]]
        # Combobox Region
        for i in select_region:
            region = region + [i[0]]

        b_data = [(''), ('Aleoida'), ('Bacterium'), ('Cactoida'), ('Clypeus'), ('Concha'),
                  ('Electricae'), ('Fonticulua'), ('Fungoida'), ('Frutexa'), ('Fumerola'), ('Osseus'),
                  ('Recepta'), ('Stratum'), ('Tubus'), ('Tussock'), ('---------'),
                  ('Amphora Plant'), ('Anemone'), ('Bark Mounds'), ('Brain'),
                  ('Crystalline Shards'), ('Fumerola'), ('Tubers')]

        label_tag = customtkinter.CTkLabel(master=buttons_frame, text="Filter:", text_color='white',
                                           font=("Helvetica", 14))
        label_tag.pack(side=LEFT, padx=29)

        combo_cmdr = customtkinter.CTkComboBox(buttons_frame, state='readonly', command=selected)
        combo_cmdr.configure(values=cmdrs)
        combo_cmdr.pack(side=LEFT, padx=15)

        combo_regions = customtkinter.CTkComboBox(buttons_frame, state='readonly', command=selected)
        combo_regions.configure(values=region)
        combo_regions.pack(side=LEFT, padx=15)

        combo_bio_data = customtkinter.CTkComboBox(buttons_frame, state='readonly', command=selected)
        combo_bio_data.configure(values=b_data)
        combo_bio_data.pack(side=LEFT, padx=10)

        refresh_button = customtkinter.CTkButton(master=buttons_frame, text='Refresh',
                                                 command=lambda: refresh_codex_data(view_name),
                                                 width=80, font=("Helvetica", 14))
        refresh_button.pack(side=LEFT, padx=20)

        global begin_time, end_time
        label_tag = customtkinter.CTkLabel(master=buttons_frame, text="Datum - Anfang:",
                                           text_color='white', font=("Helvetica", 14))
        label_tag.pack(side=LEFT, padx=10)

        begin_time = customtkinter.CTkEntry(master=buttons_frame, width=90, font=("Helvetica", 14))
        begin_time.insert(0, '2014-12-16')
        begin_time.pack(side=LEFT, padx=10)

        label_ende = customtkinter.CTkLabel(master=buttons_frame, text="Ende: ",
                                            text_color='white', font=("Helvetica", 14))
        label_ende.pack(side=LEFT, padx=10)

        end_time = customtkinter.CTkEntry(master=buttons_frame, width=90, font=("Helvetica", 14))
        end_time.insert(0, str(date.today()))
        end_time.pack(side=LEFT, padx=10)

        global b_date, e_date
        b_date = begin_time.get()
        e_date = end_time.get()

    create_button()

    style = ttk.Style(tree)
    style.theme_use('default')
    style.configure('Treeview',
                    background="black",
                    foreground="white",
                    rowheight=15,
                    fieldbackground="#3d3b3a"
                    )
    style.map('Treeview', background=[('selected', "#f07b05")])

    tree_frame = Frame(tree, bg='black')
    tree_frame.pack(pady=5)

    tree_scroll = Scrollbar(tree_frame)
    tree_scroll.pack(side=RIGHT, fill=Y)
    codex_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, selectmode="extended", height=17)
    tree_scroll.config(command=codex_tree.yview)

    # Tabellen Schema
    def main_schema():
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)

        codex_tree['columns'] = ('Index', 'Datum', 'Zeit', 'CMDR', 'Codex eintrag', 'Codex Farbe', 'Scan Value',
                                 'System', 'Body', 'Region', '')
        codex_tree.column("#0", width=15, stretch=NO)
        codex_tree.column("Index", anchor=W, width=30)
        codex_tree.column("Datum", anchor=W, width=70)
        codex_tree.column("Zeit", anchor=W, width=55)
        codex_tree.column("CMDR", anchor=CENTER, width=120)
        codex_tree.column("Codex eintrag", anchor=E, width=180)
        codex_tree.column("Codex Farbe", anchor=E, width=100)
        codex_tree.column("Scan Value", anchor=E, width=80)
        codex_tree.column("System", anchor=E, width=180)
        codex_tree.column("Body", anchor=E, width=80)
        codex_tree.column("Region", anchor=E, width=200)
        codex_tree.column("", anchor=E, width=1)

        codex_tree.heading("#0", text="", anchor=W)
        codex_tree.heading("Index", text="Index", anchor=W)
        codex_tree.heading("Datum", text="Datum", anchor=W)
        codex_tree.heading("Zeit", text="Zeit", anchor=W)
        codex_tree.heading("CMDR", text="CMDR", anchor=CENTER)
        codex_tree.heading("Codex eintrag", text="Codex Eintrag", anchor=E)
        codex_tree.heading("Codex Farbe", text="Codex Farbe", anchor=E)
        codex_tree.heading("Scan Value", text="Scan Value", anchor=E)
        codex_tree.heading("System", text="System", anchor=E)
        codex_tree.heading("Body", text="Body", anchor=E)
        codex_tree.heading("Region", text="Region", anchor=E)

        # configure treeview
        codex_tree.tag_configure('oddrow', background="white")
        codex_tree.tag_configure('evenrow', background="lightblue")
        codex_tree.tag_configure('missing_odd', background="lightgreen", font=('Arial', 9, 'bold'))
        codex_tree.tag_configure('missing_even', background="#26D5B3", font=('Arial', 9, 'bold'))

    # Tabellen Schema
    def system_scanner_schema():
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)

        codex_tree['columns'] = ('Datum', 'Zeit', 'CMDR', 'Codex eintrag', 'Codex Farbe', 'Scan Value',
                                 'System', 'Body', 'Region', 'Missing')

        codex_tree.heading("Datum", text="Body", anchor=W)
        codex_tree.column("Datum", anchor=W, width=180)

        codex_tree.heading("Zeit", text="Distance to main Star", anchor=W)
        codex_tree.column("Zeit", anchor=CENTER, width=150)

        codex_tree.heading("CMDR", text="Count", anchor=CENTER)
        codex_tree.column("CMDR", anchor=CENTER, width=50)

        codex_tree.heading("Codex eintrag", text="Familie", anchor=CENTER)
        codex_tree.column("Codex eintrag", anchor=CENTER, width=100)

        codex_tree.heading("Codex Farbe", text="Spezies", anchor=CENTER)
        codex_tree.column("Codex Farbe", anchor=CENTER, width=150)

        codex_tree.heading("Scan Value", text="Scan Value", anchor=E)
        codex_tree.column("Scan Value", anchor=CENTER, width=100)

        codex_tree.heading("System", text="Color", anchor=CENTER)
        codex_tree.column("System", anchor=CENTER, width=150)

        codex_tree.heading("Body", text="Colony Distance", anchor=CENTER)
        codex_tree.column("Body", anchor=CENTER, width=100)

        codex_tree.heading("Region", text="Region", anchor=E)
        codex_tree.column("Region", anchor=CENTER, width=170)

        codex_tree.heading("Missing", text="Missing", anchor=E)
        codex_tree.column("Missing", anchor=CENTER, width=10)

    # Tabellen Schema
    def codex_stars_schema():
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)

        codex_tree['columns'] = ('Index', 'Datum', 'Zeit', 'CMDR', 'Kategorie', 'Eintrag', 'System', 'Region')
        # print('reset_pos')
        codex_tree.column("#0", width=15, stretch=NO)
        codex_tree.heading("#0", text="", anchor=W)

        codex_tree.heading("Index", text="", anchor=W)
        codex_tree.heading("Datum", text="Datum", anchor=W)
        codex_tree.heading("Zeit", text="Zeit", anchor=W)
        codex_tree.heading("CMDR", text="CMDR", anchor=CENTER)
        codex_tree.heading("Kategorie", text="Codex", anchor=CENTER)
        codex_tree.heading("Eintrag", text="-kategorie", anchor=CENTER)
        codex_tree.heading("System", text="System", anchor=CENTER)
        codex_tree.heading("Region", text="Region", anchor=E)

        codex_tree.column("Index", width=15, stretch=YES)
        codex_tree.column("Datum", anchor=W, width=70)
        codex_tree.column("Zeit", anchor=W, width=55)
        codex_tree.column("CMDR", anchor=CENTER, width=120)
        codex_tree.column("Kategorie", anchor=E, width=150)
        codex_tree.column("Eintrag", anchor=E, width=200)
        codex_tree.column("System", anchor=E, width=200)
        codex_tree.column("Region", anchor=E, width=250)

    # Tabellen Schema
    def statistics_schema():
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)

        codex_tree.heading("Datum", text="Date", anchor=W)
        codex_tree.heading("Zeit", text="Time", anchor=W)
        codex_tree.heading("CMDR", text="System Name", anchor=CENTER)
        codex_tree.heading("Codex eintrag", text="Body", anchor=CENTER)
        codex_tree.heading("Codex Farbe", text="Class", anchor=CENTER)
        codex_tree.heading("Scan Value", text="Mass", anchor=CENTER)
        codex_tree.heading("System", text="AGE", anchor=CENTER)
        codex_tree.heading("Body", text="TEMP", anchor=CENTER)
        codex_tree.heading("Region", text="Region", anchor=E)

        codex_tree.column("Datum", anchor=CENTER, width=80)
        codex_tree.column("Zeit", anchor=CENTER, width=80)
        codex_tree.column("CMDR", anchor=CENTER, width=150)
        codex_tree.column("Codex eintrag", anchor=CENTER, width=80)
        codex_tree.column("Codex Farbe", anchor=E, width=200)
        codex_tree.column("Scan Value", anchor=E, width=80)
        codex_tree.column("System", anchor=E, width=100)
        codex_tree.column("Body", anchor=E, width=120)
        codex_tree.column("Region", anchor=E, width=220)

    def codex_data():
        global backup_row, filter_cmdr, filter_region, filter_bdata, \
            combo_regions, combo_cmdr, combo_bio_data
        filter_region = combo_regions.get()
        filter_cmdr = combo_cmdr.get()
        filter_bdata = combo_bio_data.get()

        rowdata = get_codex_data(filter_cmdr, filter_region, filter_bdata)
        if old_view_name != 'missing_codex':
            main_schema()

        if backup_row != rowdata:
            backup_row = rowdata
            return rowdata
        else:
            return 0

    def stellar_data():
        global view_name, backup_row
        view_name = 'stellar_codex'
        rcd_cmdr = combo_cmdr.get()
        rcd_region = combo_regions.get()

        rowdata = read_codex_data(rcd_cmdr, rcd_region)
        # print(rowdata[0])
        codex_stars_schema()

        if backup_row != rowdata:
            backup_row = rowdata
            return rowdata
        else:
            return 0

    def system_scanner():
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)
        global view_name, backup_row
        view_name = 'system_scanner'
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)

        rowdata = []
        t1 = get_time()
        rowdata = start_read_logs()
        t2 = get_time()
        # print('start_read_logs  ' + str(timedelta.total_seconds(t2 - t1)))

        system_scanner_schema()
        if not rowdata:
            rowdata = [('Body', 'Distance', 'Count', 'Genus',
                        'Family', 'Value', 'Color', "Distance", "Region", "Missing")]
        if backup_row != rowdata:
            backup_row = rowdata
            return rowdata
        else:
            return 0

    def refresh_combo():
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)
        # print(view_name)
        # read_codex_entrys()
        # lang = read_language()
        filter_bio_data = combo_bio_data.get()
        if filter_bio_data:
            filter_bdata = '%' + filter_bio_data + '%'
        else:
            filter_bdata = ''

        s_table = 'codex'
        if view_name == 'stellar_codex':
            selected_value = combo_bio_data.get()
            if selected_value == 'Star':
                combo_bio_data.configure(values=['<- back', 'O', 'B', 'A', 'F', 'G', 'K', 'M'])
            elif selected_value == 'Carbon-Stars':
                combo_bio_data.configure(values=['<- back', 'Carbon-Star', 'MS', 'S'])
            elif selected_value == 'Giant Stars':
                combo_bio_data.configure(values=['<- back', 'B', 'A', 'F', 'G', 'K', 'M', 'MS', 'C', 'CJ', 'CN', 'S'])
            elif selected_value == 'Gas Giant':
                combo_bio_data.configure(
                    values=['<- back', 'Gas Giant With Ammonia Life', 'Gas Giant With Water Life', 'Sudarsky Class I',
                            'Sudarsky Class II', 'Sudarsky Class III', 'Sudarsky Class IV', 'Sudarsky Class V'])
            elif selected_value == 'Proto Stars':
                combo_bio_data.configure(values=['<- back', 'Herbig AeBe', 'T Tauri'])
            elif selected_value == 'Brown Dwarfs':
                combo_bio_data.configure(values=['<- back', 'L', 'T', 'Y'])
            elif selected_value == 'Non-Sequenz Stars':
                combo_bio_data.configure(values=['<- back', 'Black Hole', 'White Dwarf', 'Wolf-Rayet'])
            elif selected_value == '<- back':
                combo_bio_data.configure(values=['Star', 'Carbon-Stars', 'Giant Stars', 'Gas Giant', 'Proto Stars',
                                                 'Brown Dwarfs', 'Non-Sequenz Stars', 'Terrestrials',
                                                 'Geology and Anomalies',
                                                 'Xenological'])
                combo_bio_data.set(value='')
            elif selected_value == '':
                combo_bio_data.configure(values=['Star', 'Carbon-Stars', 'Giant Stars', 'Gas Giant', 'Proto Stars',
                                                 'Brown Dwarfs', 'Non-Sequenz Stars', 'Terrestrials',
                                                 'Geology and Anomalies',
                                                 'Xenological'])

            third_combo = 'codex_name'
            s_table = 'codex_data'
            if selected_value == '<- back':
                b_data = ['', 'Star', 'Carbon-Stars', 'Giant Stars', 'Gas Giant', 'Proto Stars',
                          'Brown Dwarfs', 'Non-Sequenz Stars', 'Terrestrials', 'Geology and Anomalies', 'Xenological']
                combo_bio_data.configure(values=b_data)

        # elif view_name == 'bio_codex' or view_name == 'system_scanner' or view_name == 'missing_codex':
        else:
            s_table = 'codex'
            b_data = [(''), ('Aleoida'), ('Bacterium'), ('Cactoida'), ('Clypeus'), ('Concha'),
                      ('Electricae'), ('Fonticulua'), ('Fungoida'), ('Frutexa'), ('Fumerola'), ('Osseus'),
                      ('Recepta'), ('Stratum'), ('Tubus'), ('Tussock'), ('---------'),
                      ('Amphora Plant'), ('Anemone'), ('Bark Mounds'), ('Brain'),
                      ('Crystalline Shards'), ('Fumerola'), ('Tubers')]

        if filter_bdata == '%---------%' or filter_bdata == '%%':
            filter_bdata = ''
        cmdrs = ['']
        regions = ['']
        if s_table == 'codex_data':
            data = 'codex_entry'
        else:
            data = 'data'

        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()

            query_cmdr = f'''SELECT DISTINCT cmdr FROM {s_table} ORDER BY cmdr '''
            query_region = f'''SELECT DISTINCT region FROM {s_table} ORDER BY region '''

            try:
                selection_cmdr = cursor.execute(query_cmdr).fetchall()
            except sqlite3.OperationalError:
                logger(query_cmdr, 2)

            try:
                selection_region = cursor.execute(query_region).fetchall()
            except sqlite3.OperationalError:
                logger(query_region, 2)

            for cmdr in selection_cmdr:
                cmdrs = cmdrs + [cmdr[0]]

            for region in selection_region:
                regions = regions + [region[0]]

            if view_name == 'system_scanner':
                b_data = ['']
                cmdrs = ['']
                regions = ['']
            if view_name != 'stellar_codex':
                combo_bio_data.configure(values=b_data)
            # elif normal_view == 5:  # statistics Combo Filter
            #     cmdrs = ('Stars', 'Bodys')
            #     query_region = f'''SELECT DISTINCT region FROM codex_entry ORDER BY region'''
            #     b_data = ('MASS', 'AGE', 'TEMP')
            #
            #     selection_region = cursor.execute(query_region).fetchall()
            #     for region in selection_region:
            #         regions = regions + [region[0]]
            #     combo_bio_data.configure(values=b_data)

            # connection.commit()
            combo_cmdr.configure(values=cmdrs)
            combo_regions.configure(values=regions)

    #  Daten für die Tabelle
    data = get_codex_data('', '', '')
    main_schema()

    global treeview_count
    treeview_count = 0

    def add_entries(entries):
        global treeview_count
        treeview_count = 0

        for idx, entry in enumerate(entries):
            treeview_count += 1
            new_entry = entry
            tags = ()
            if len(entry) < 2:
                return
            if entry[1] != '' and view_name == active_view[2]:
                # active_view = ['bio_codex' ,'stellar_codex', 'system_scanner']
                tags = ('header',)
                parent_item = idx
                codex_tree.insert('', iid=parent_item, index='end', values=new_entry, tags=tags)
                if idx == 0:
                    codex_tree.item(parent_item, open=True)
                # print('', idx, new_entry, tags)
            else:
                if idx % 2 == 1:
                    if view_name == active_view[2]:  # active_view = ['bio_codex' ,'stellar_codex', 'system_scanner']
                        if entry[9] == 1:
                            tags = ('odd_new',)
                        else:
                            tags = ('odd',)
                    else:
                        tags = ('odd',)
                else:
                    if view_name == active_view[2]:  # active_view = ['bio_codex' ,'stellar_codex', 'system_scanner']
                        if entry[9] == 1:
                            tags = ('even_new',)
                        else:
                            tags = ('even',)
                    else:
                        tags = ('even',)
            if entry[1] == '' and view_name == active_view[2]:
                # print(codex_tree.get_children())
                codex_tree.insert(parent=str(parent_item), index="end", values=new_entry, tags=tags)

            else:
                if tags != ('header',):
                    codex_tree.insert('', 'end', values=new_entry, tags=tags)

    codex_tree.tag_configure('odd', background='#569fe3', foreground='white')
    codex_tree.tag_configure('even', background='white', foreground='black')
    codex_tree.tag_configure('odd_new', background='#7B0037', foreground='white', font=('Arial', 9, 'bold'))
    codex_tree.tag_configure('even_new', background='#ffbfeb', foreground='black', font=('Arial', 9, 'bold'))
    codex_tree.tag_configure('header', background='#381f0b', foreground='white', font=('Arial', 10))
    # codex_tree.tag_configure('header', background='grey', foreground='#f07b05', font=('Arial', 10))

    add_entries(data)
    refresh_combo()

    codex_tree.pack()
    if view_name == 'bio_codex':
        global summen_label
        summe = worth_it(data)
        summen_text = ('Anzahl Einträge : ' + str(treeview_count) + '     Wertigkeit :  ' + str(
            f"{summe:,}"))
        summen_label = customtkinter.CTkLabel(tree_frame, text=summen_text, bg_color='black')
        summen_label.pack(fill=X, anchor=E)

    def selected_record(e):  # Shows Picture of selected Item
        global my_img, my_codex_preview
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)
        active_view = ['bio_codex', 'stellar_codex', 'system_scanner']
        selected_tree = codex_tree.focus()
        values = codex_tree.item(selected_tree, 'values')
        # print(values)
        tables = [codex_bio_table, codex_stars_table, system_scanner_table]
        for table in tables:
            try:
                table.clear_rows()
            except AttributeError:
                logger(('NoData in ' + str(table)), 2)
        root.clipboard_clear()
        table = [codex_bio_table, codex_stars_table, system_scanner_table, statistics_table]
        normal_view = 0
        if values == '':
            return
        if values == ('0', 'DATE', 'TIME', 'COMMANDER', 'SPECIES', 'VARIANT', '', 'SYSTEM', 'BODY', 'REGION') \
                or values == (
                '0', 'DATE', 'TIME', 'COMMANDER', 'SPECIES', 'VARIANT', '0', 'SYSTEM', 'BODY', 'In REGION ') \
                or values == ('0', 'Body', 'Distance', 'Count', 'Genus', 'Family', '', 'Value', 'Color', 'No Data') \
                or values == ('0', 'DATE', 'TIME', 'COMMANDER', 'SPECIES', 'VARIANT', '', 'SYSTEM', 'BODY', ''):
            return

        if values[4] == '':
            with sqlite3.connect(database) as connection:
                cursor = connection.cursor()
                query_s_bio = f'''SELECT DISTINCT(name) from bio_color where name like "%{values[5]}%"'''
                select_bio = cursor.execute(query_s_bio).fetchall()
                new_value = str(select_bio[0][0])
                new_value = new_value.split(' ')
                values = (values[0], values[1], values[2], values[3], new_value[0], new_value[1],
                          values[6], values[7], values[8], values[9], values[10])
        if values:
            for c, i in enumerate(active_view):
                if i == view_name:
                    normal_view = c
                    # print(normal_view, view_name, c)
            (table[normal_view]).add_row(values)  #                   table[ 1 = codex_bio_table ]
            root.clipboard_append((table[normal_view]).get_string())
            root.clipboard_append('\n')
        my_img = ''
        if values:
            if view_name == active_view[1]:  # active_view = ['bio_codex' ,'stellar_codex', 'system_scanner']
                var = str(values[5]).split()
                if 'D' in var[0]:
                    var = ['D', 'Type', 'Star']
            else:
                var = str(values[4]).split()
            if view_name == active_view[2]:
                # print(values)
                if values[0] != '':
                    directory_to_search = 'images/'
                    body = str(values[4]).split(' ')
                    partial_filename_to_find = str(body[0]).rstrip()

                    # print(partial_filename_to_find)

                    def find_file_in_directory(directory, partial_filename):
                        for root, dirs, files in os.walk(directory):
                            for file in fnmatch.filter(files, f'*{partial_filename}*'):
                                return os.path.join(root, file)
                        return None

                    result = find_file_in_directory(directory_to_search, partial_filename_to_find)
                    if not result:
                        return
                    # print(result + ' ds')
                    my_img = customtkinter.CTkImage(dark_image=Image.open(resource_path(result)), size=(320, 145))
                    my_codex_preview = customtkinter.CTkLabel(master=tree, image=my_img, text='')
                    my_codex_preview.place(x=837, y=400)
                    return
                else:
                    var = '%' + values[4] + '%'
                    with sqlite3.connect(database) as connection:
                        cursor = connection.cursor()
                        select = cursor.execute("SELECT DISTINCT data FROM codex_entry WHERE data like ? ",
                                                (var,)).fetchall()
                        if select:
                            var = str(select[0][0]).split()
            png = ''
            for x, i in enumerate(var):
                # print(x, len(var))
                if (x + 1) == len(var):
                    png += (var[x] + ".png")
                else:
                    png += (var[x] + '_')
            if Path('images/' + png).is_file():
                photo = "images/" + str(png)
            else:
                logger("File not found", log_var)
                logger(png, 2)
                photo = resource_path("images/Kein_Bild.png")
            my_img = customtkinter.CTkImage(dark_image=Image.open(resource_path(photo)), size=(320, 145))
        else:
            return
        my_codex_preview = customtkinter.CTkLabel(master=tree, image=my_img, text='')
        my_codex_preview.place(x=837, y=400)
        # my_codex_preview.place()

    codex_tree.bind("<ButtonRelease-1>", selected_record)

    def switch_view(module):  # beim switch der Module werden die Einträge in der Combobox gelöscht
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)

        combo_cmdr.set('')
        combo_regions.set('')
        combo_bio_data.set('')
        refresh_codex_data(module)
        refresh_combo()

    def refresh_codex_data(func):
        funktion = inspect.stack()[0][3], func
        logger(funktion, log_var)
        global view_name, old_view_name
        rowdata = ''
        view_name = func
        match func:
            case 'stellar_codex':
                rowdata = stellar_data()
                summen_label.configure(text='')
            case 'bio_codex':
                rowdata = codex_data()
            case 'system_scanner':
                rowdata = system_scanner()
                summen_label.configure(text='')
            case 'missing_codex':
                rowdata = missing_codex()
                if old_view_name != 'bio_codex':
                    main_schema()
                summen_label.configure(text='')

        # codex_tree.config(height=15)
        if rowdata != 0 or (view_name != old_view_name):
            codex_tree.delete(*codex_tree.get_children())
            old_view_name = view_name
            add_entries(rowdata)
            match func:
                case 'stellar_codex':
                    summen_label.configure(text='')
                case 'bio_codex':
                    summe = worth_it(rowdata)
                    summen_text = ('Anzahl Einträge : ' + str(treeview_count) + '     Wertigkeit :  ' + str(
                        f"{summe:,}"))
                    summen_label.configure(text=summen_text)
                case 'system_scanner':
                    summen_label.configure(text='')
            # print('refresh')

    def tree_loop(x):
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)
        refresh_codex_data(view_name)
        tree.after(x, lambda: tree_loop(3000))

    tree_loop(3000)
    tree.mainloop()


def rescan():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS codex")
        cursor.execute("DROP TABLE IF EXISTS codex_entry")
        cursor.execute("DROP TABLE IF EXISTS codex_data")
        cursor.execute("DROP TABLE IF EXISTS codex")
    create_tables()
    global rescan_lauf
    rescan_lauf = 0
    threading.Thread(target=rescan_files).start()


def create_codex_show_table():
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS codex_show")
        cursor.execute("""CREATE table IF NOT EXISTS codex_show (
                                cmdr TEXT,
                                data TEXT,
                                region TEXT)
                                """)
        cursor.execute("SELECT DISTINCT data FROM codex_entry")  # Alle Bios
        all_species = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT cmdr FROM codex")  # Alle CMDRs mit Codex Einträge
        all_names = [row[0] for row in cursor.fetchall()]

        regions = RegionMapData.regions
        filtered_regions = [region for region in regions if region is not None]

        # Erstelle alle möglichen Kombinationen von Namen, Regionen und Spezies
        all_combinations = list(product(all_names, all_species, filtered_regions))
        cursor.execute("SELECT DISTINCT cmdr, data, region FROM codex WHERE codex.codex = 1")
        existing_data = set(cursor.fetchall())

        # Finde fehlende Kombinationen
        missing_combinations = [combo for combo in all_combinations if combo not in existing_data]
        cursor.executemany("INSERT INTO codex_show VALUES (?, ?, ?)", missing_combinations)
        connection.commit()


def missing_codex():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    create_codex_show_table()
    global view_name
    view_name = 'missing_codex'
    filter_cmdr = combo_cmdr.get()
    filter_region = combo_regions.get()
    filter_bio_data = combo_bio_data.get()
    if filter_bio_data:
        filter_bdata = '%' + filter_bio_data + '%'
    else:
        filter_bdata = ''
    key = (bool(filter_cmdr), bool(filter_region), bool(filter_bdata))

    conditions = {
        (False, False, False): f'''SELECT * FROM codex_show ORDER BY data''',
        (True, True, True): f'''SELECT * FROM codex_show WHERE cmdr = "{filter_cmdr}" 
                                    and region = "{filter_region}" and data like "{filter_bdata}" ORDER BY data''',
        (True, False, False): f'''SELECT * FROM codex_show WHERE cmdr = "{filter_cmdr}" ORDER BY data''',
        (False, True, False): f'SELECT * FROM codex_show WHERE region = "{filter_region}" ORDER BY data',
        (False, False, True): f'SELECT * FROM codex_show WHERE data like "{filter_bdata}" ORDER BY data',
        (True, True, False): f'''SELECT * FROM codex_show WHERE cmdr = "{filter_cmdr}" 
                                    and region = "{filter_region}" ORDER BY data''',
        (True, False, True): f'''SELECT * FROM codex_show WHERE cmdr = "{filter_cmdr}" 
                                    and data like "{filter_bdata}" ORDER BY data''',
        (False, True, True): f'''SELECT * FROM codex_show WHERE region = "{filter_region}" 
                                    and data like "{filter_bdata}" ORDER BY data'''
    }

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        query = conditions.get(key)
        select = cursor.execute(query).fetchall()

    lauf = 1
    data = []
    for i in select:
        data.append((' ', ' ', ' ', i[0], i[1], ' ', ' ', ' ', '', i[2]))
        lauf += 1
    global backup_row
    if backup_row != data:
        backup_row = data
        return data
    else:
        return 0


def get_info_for_bio_scan(data, file):  # event: ScanOrganic
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    # latitude, longitude, altitude, radius, body_name_2, reached = compass.get_status_data()
    timestamp = data.get('timestamp')
    icd_log_time = (log_date(timestamp))
    date_log = (icd_log_time[0] + "-" + icd_log_time[1] + "-" + icd_log_time[2])
    time_log = (icd_log_time[3] + ":" + icd_log_time[4] + ":" + icd_log_time[5])

    scantype = data.get('ScanType')  # "ScanType": "Log"; 2x "ScanType":"Sample", "ScanType":"Analyse"
    species = data.get('Species_Localised')  # "Species_Localised": "Fonticulua Campestris",
    variant = data.get('Variant_Localised', ' - ')  # "Variant_Localised": "Fonticulua Campestris - Mauve",

    variant = variant.split('-')
    try:
        bio_color = variant[1].replace(' ', '')
    except IndexError:
        bio_color = ''
    system_address = data.get('SystemAddress')  # "SystemAddress":71235145978
    body = data.get('Body')  # "Body":10
    cmdr = read_cmdr(file)
    system_name = get_system(system_address)
    body_name = get_body(system_address, body)
    latitude, longitude, altitude, radius, body_name_2, reached, s_time = get_status_data()
    timestamp_1 = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    timestamp_2 = datetime.strptime(s_time, "%Y-%m-%dT%H:%M:%SZ")

    # Zeitdifferenz berechnen
    difference = abs(timestamp_1 - timestamp_2)

    # Grenze festlegen (z. B. 10 Sekunden)
    threshold = timedelta(seconds=10)

    if difference > threshold:
        latitude, longitude = '', ''
    if system_address == 0 or body == 0:
        return

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()

        new_select = cursor.execute(f'''SELECT * from bio_scan_data where
                                                    date_log = "{date_log}" and time_log = "{time_log}" and
                                                    cmdr = "{cmdr}" and system = "{system_name}" and 
                                                    body_name = "{body_name}" and scantype = "{scantype}" and 
                                                    bio = "{species}" and color = "{bio_color}" and 
                                                    latitude = "{latitude}" and longitude = "{longitude}"
                                                    ''').fetchall()

        if not new_select:
            sql_insert = f'''INSERT INTO bio_scan_data 
                                (date_log, time_log, cmdr, system, body_name, scantype, bio, color, latitude, longitude) 
                                VALUES ("{date_log}", "{time_log}", "{cmdr}", "{system_name}", "{body_name}", 
                                "{scantype}", "{species}", "{bio_color}", "{latitude}", "{longitude}")'''
            cursor.execute(sql_insert)
            connection.commit()
        count_bios = 0
        count_bios_new = cursor.execute(f'''Select COUNT(bio) from bio_scan_data where
                        body_name = "{body_name}" and bio = "{species}" and scantype != "Analyse"''').fetchone()
        if count_bios_new:
            count_bios = count_bios_new[0]
        mark_missing = '0'
        if species.find(" ") != -1:
            bio_name = species.split(' ')
            genus = bio_name[0]
            species_2 = bio_name[1]
        else:
            genus = species
            species_2 = ''

        insert_into_bio_db(body_name, count_bios, genus, species_2, bio_color, mark_missing)
    return timestamp, scantype, species, system_address, body


def get_info_for_get_body_name(data, cmdr):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    timestamp = data.get('timestamp')
    log_time = (log_date(timestamp))
    date_log = (log_time[0] + "-" + log_time[1] + "-" + log_time[2])
    time_log = (log_time[3] + ":" + log_time[4] + ":" + log_time[5])
    starsystem = data.get('StarSystem')
    system_address = data.get('SystemAddress')
    body_id = data.get('BodyID')
    body_name = data.get('BodyName')
    if not body_name:
        body_name = data.get('Body')

    if not starsystem or not system_address:
        return 0

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        if body_id and body_name:
            select = cursor.execute("""SELECT starsystem from star_data where 
                                                starsystem = ? and 
                                                system_address = ? and
                                                body_id = ? and
                                                body_name = ?""",
                                    (starsystem, system_address, body_id, body_name)).fetchall()
            if select != []:
                return starsystem, system_address, body_id, body_name
        select = cursor.execute("""SELECT starsystem, system_address from star_data where system_address = ? """,
                                (system_address,)).fetchall()
        if not select:
            cursor.execute("""INSERT INTO star_data 
            (date_log, time_log, cmdr, starsystem, system_address, body_id, body_name) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                           (date_log, time_log, cmdr, starsystem, system_address, body_id, body_name))
            connection.commit()
    return starsystem, system_address, body_id, body_name


def get_system(system_address):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select_system = cursor.execute("""SELECT starsystem from star_data where system_address = ?""",
                                       (system_address,)).fetchall()
        if select_system:
            return select_system[0][0]


def get_planet_info(data, cmdr):
    # data['event'] == 'Scan' and data['ScanType'] == 'Detailed' and data['Landable']
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    timestamp = data.get('timestamp')
    log_time = (log_date(timestamp))
    date_log = (log_time[0] + "-" + log_time[1] + "-" + log_time[2])
    time_log = (log_time[3] + ":" + log_time[4] + ":" + log_time[5])
    system_id = data.get('SystemAddress')
    system_name = data.get('StarSystem')
    body_name = data.get('BodyName')
    body_id = data.get('BodyID')

    body_parents = data.get('Parents')
    main_star = get_main_and_local(system_id, body_parents, body_name, system_name)
    local_star = ''
    if main_star != 'NULL':
        main = main_star[0]
        if len(main_star) > 1:
            for i, stars in enumerate(main_star):
                if i > 0:
                    local_star = local_star + ', ' + str(stars)
        local_star = local_star.lstrip(', ')

        main_star = main
    body_distance = int(data.get('DistanceFromArrivalLS'))
    tidal_lock = data.get("TidalLock")
    terraform_state = data.get("TerraformState")
    planet_type = data.get('PlanetClass')
    body_atmos = data.get('Atmosphere')
    body_gravity = data.get('SurfaceGravity')
    if body_gravity:
        body_gravity = round(float(body_gravity) / 9.80665, 3)
    body_temp = data.get('SurfaceTemperature')
    body_pressure = data.get('SurfacePressure')
    if body_pressure:
        body_pressure = float(body_pressure) / 100000
    landable = data.get("Landable")
    volcanism = data.get('Volcanism')
    atmosphere_composition = data.get('AtmosphereComposition')
    mass = data.get('MassEM')
    radius = data.get('Radius')
    semiMajorAxis = data.get("SemiMajorAxis")
    eccentricity = data.get("Eccentricity")
    orbitalInclination = data.get("OrbitalInclination")
    periapsis = data.get("Periapsis")
    orbital_period = data.get("OrbitalPeriod")
    ascending_node = data.get("AscendingNode")
    mean_anomaly = data.get("MeanAnomaly")
    rotation_period = data.get("RotationPeriod")
    axial_tilt = data.get("AxialTilt")
    if data.get('Rings'):
        has_rings = 1
    else:
        has_rings = 0
    # print('hat Ringe' +str(has_rings))
    discovered = data.get("WasDiscovered")
    mapped = data.get("WasMapped")

    composition = []
    sulphur_concentration = 0
    if atmosphere_composition:
        for i in atmosphere_composition:
            # print(body_name, i.get('Name'), i.get('Percent'))
            if i.get('Name') == 'SulphurDioxide' and i.get('Percent') >= 1:
                sulphur_concentration = i.get('Percent')
                logger((body_name, i.get('Name'), (str(sulphur_concentration) + '%')), log_var)
    if volcanism:
        volcanism = 'Y'
    else:
        volcanism = 'N'
    material = []
    materials = ''

    if data.get('Materials'):
        for i in data.get('Materials'):
            material.append(i['Name'])
        for i in material:
            materials = materials + ' ' + str(i)

    body_name = body_name.replace(system_name, '')
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select = cursor.execute("SELECT BodyName FROM planet_infos WHERE BodyName = ? and SystemName = ?"
                                , (body_name, system_name)).fetchall()

        if select == []:
            cursor.execute(
                """INSERT INTO planet_infos (date_log, time_log, cmdr, SystemID, SystemName, Main_Star, 
                Local_Stars, BodyName, BodyID, DistanceToMainStar, Tidal_lock, Terraform_state, PlanetType, Atmosphere, 
                Gravity, Temperature, Pressure, Landable, volcanism, sulphur_concentration, Rings, Mass, Radius, 
                SemiMajorAxis, Eccentricity, OrbitalInclination, Periapsis, OrbitalPeriod, AscendingNode, MeanAnomaly, 
                RotationPeriod, AxialTilt, Discovered, Mapped, Materials ) VALUES 
                (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) """,
                (date_log, time_log, cmdr, system_id, system_name, main_star, local_star, body_name, body_id,
                 body_distance, tidal_lock, terraform_state, planet_type, body_atmos, body_gravity,
                 body_temp, body_pressure, landable, volcanism, sulphur_concentration, has_rings, mass, radius,
                 semiMajorAxis, eccentricity, orbitalInclination, periapsis, orbital_period, ascending_node,
                 mean_anomaly, rotation_period, axial_tilt, discovered, mapped, materials))
            connection.commit()


def get_star_info(data, cmdr):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    timestamp = data.get('timestamp')
    log_time = (log_date(timestamp))
    date_log = (log_time[0] + "-" + log_time[1] + "-" + log_time[2])
    time_log = (log_time[3] + ":" + log_time[4] + ":" + log_time[5])
    starsystem = data.get('StarSystem')
    system_address = data.get('SystemAddress')
    startype = data['StarClass']
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select = cursor.execute("""SELECT starsystem, system_address from star_data where system_address = ? """,
                                (system_address,)).fetchall()
        if not select:
            cursor.execute("""INSERT INTO star_data 
            (date_log, time_log, cmdr, starsystem, system_address, startype, Main) VALUES (?,?,?,?,?,?,?)""",
                           (date_log, time_log, cmdr, starsystem, system_address, startype, 1)).fetchall()
            connection.commit()


def insert_star_data_in_db(star_data):  # Tabelle star_data mit Daten füllen
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    date_log = star_data[0]
    time_log = star_data[1]
    cmdr = star_data[2]
    body_id = star_data[3]
    starsystem = star_data[4]
    body_name = star_data[5]
    system_address = star_data[6]
    distance = star_data[7]
    startype = star_data[8]
    sub_class = star_data[9]
    mass = star_data[10]
    radius = star_data[11]
    age = star_data[12]
    surface_temp = star_data[13]
    luminosity = star_data[14]
    rotation_period = star_data[15]
    axis_tilt = star_data[16]
    discovered = star_data[17]
    mapped = star_data[18]
    parents = str(star_data[19])
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        if distance == 0.0:  # Mainstar
            select_main = cursor.execute("""SELECT starsystem, system_address from star_data where system_address = ? 
                                    and Main = 1""", (system_address,)).fetchall()

            if select_main:
                cursor.execute("""Update star_data set 
                                body_id = ?, body_name =?, distance = ?, 
                                startype = ?, sub_class = ?, mass = ?, 
                                radius = ?, age = ?, surface_temp = ?,
                                luminosity = ?, rotation_period = ?, axis_tilt = ?, 
                                discovered = ?, mapped = ?, parents = ?                                 
                                where starsystem = ? and system_address = ? and Main  = 1""",
                               (body_id, body_name, distance,
                                startype, sub_class, mass,
                                radius, age, surface_temp,
                                luminosity, rotation_period, axis_tilt,
                                discovered, mapped, parents,
                                starsystem, system_address))
                connection.commit()
                return
            select = cursor.execute("""SELECT starsystem, system_address from star_data where system_address = ? """,
                                    (system_address,)).fetchall()
            if not select:
                cursor.execute('''INSERT INTO star_data (date_log, time_log, cmdr, body_id, starsystem, body_name, 
                system_address, Main, distance, startype, sub_class, mass, radius, age, surface_temp, luminosity, 
                rotation_period, axis_tilt, discovered, mapped, parents) 
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                               (date_log, time_log, cmdr, body_id, starsystem, body_name, system_address, 1,
                                distance, startype, sub_class, mass, radius, age, surface_temp, luminosity,
                                rotation_period, axis_tilt, discovered, mapped, parents))
                connection.commit()
                return

        select = cursor.execute("""SELECT starsystem, system_address from star_data where system_address = ? 
                                and body_id = ? """, (system_address, body_id,)).fetchall()

        if not select:
            cursor.execute('''INSERT INTO star_data (date_log, time_log, cmdr, body_id, starsystem, body_name, 
                system_address, Main, distance, startype, sub_class, mass, radius, age, surface_temp, luminosity, 
                rotation_period, axis_tilt, discovered, mapped, parents) 
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                           (date_log, time_log, cmdr, body_id, starsystem, body_name, system_address, '', distance,
                            startype, sub_class, mass, radius, age, surface_temp, luminosity, rotation_period,
                            axis_tilt, discovered, mapped, parents))
            connection.commit()


def get_all_stars(data, cmdr):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    timestamp = data.get('timestamp')
    log_time = (log_date(timestamp))
    date_log = (log_time[0] + "-" + log_time[1] + "-" + log_time[2])
    time_log = (log_time[3] + ":" + log_time[4] + ":" + log_time[5])
    body_id = data.get('BodyID')
    starsystem = data.get('StarSystem')
    body_name = data.get('BodyName')
    if body_id != 0:
        body_name = body_name.replace((starsystem + ' '), '')
    else:
        body_name = body_name.replace((starsystem), '')
    system_address = data.get('SystemAddress')
    distance = data.get('DistanceFromArrivalLS')
    startype = data.get('StarType')
    sub_class = data.get('Subclass')
    mass = data.get('StellarMass')
    radius = data.get('Radius')
    age = data.get('Age_MY')
    surface_temp = data.get('SurfaceTemperature')
    luminosity = data.get('Luminosity')
    rotation_period = data.get('RotationPeriod')
    axis_tilt = data.get('AxialTilt')
    discovered = data.get('WasDiscovered')
    mapped = data.get('WasMapped')
    parents = data.get('Parents')
    star_data = [date_log, time_log, cmdr, body_id, starsystem, body_name, system_address, distance, startype,
                 sub_class, mass, radius, age, surface_temp, luminosity, rotation_period, axis_tilt, discovered,
                 mapped, parents]
    # print(star_data)
    insert_star_data_in_db(star_data)


def set_main_star(data, cmdr):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    if data.get('BodyType') != 'Star':
        logger(('no main star'), 2)
        return
    timestamp = data.get('timestamp')
    log_time = (log_date(timestamp))
    date_log = (log_time[0] + "-" + log_time[1] + "-" + log_time[2])
    time_log = (log_time[3] + ":" + log_time[4] + ":" + log_time[5])
    body_id = data.get('BodyID')
    starsystem = data.get('StarSystem')
    system_address = data.get('SystemAddress')
    body = data.get('SystemAddress')
    body_name = data.get('Body')

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select = cursor.execute("""SELECT starsystem, system_address from star_data where system_address = ? """,
                                (system_address,)).fetchall()
        if not select:
            cursor.execute("""INSERT INTO star_data 
            (date_log, time_log, cmdr, body_id, starsystem, body_name, system_address, Main) VALUES (?,?,?,?,?,?,?)""",
                           (date_log, time_log, cmdr, body_id, starsystem, body_name, system_address, 1)).fetchall()
            connection.commit()
    return body_id, starsystem, body_name, system_address


def get_bary(data):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    system_address = data.get('SystemAddress')
    starsystem = data.get('StarSystem')
    body_id = data.get('BodyID')
    # print('Barry Centre', system_address, starsystem, body_id)


def check_genus(body_name, genus2):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()

        select = cursor.execute("""SELECT bio_genus from planet_bio_info where body = ?""",
                                (body_name,)).fetchone()
    if select != ('',):
        return select
    else:
        return None


def get_info_scan_planets(data):  # data['event'] == 'FSSBodySignals':
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    genus = ''
    if data.get('event') == 'SAASignalsFound':
        for i in data.get('Genuses', {'None'}):
            if i == 'None':
                return
            geni = i.get('Genus_Localised')
            genus = genus + ', ' + geni
    body_name = data.get('BodyName')
    body_id = data.get('BodyID')
    system_address = data['SystemAddress']

    if body_name == 'body_name':
        logger(data, 2)

    bio_count = 0
    region = (findRegionForBoxel(system_address)['region'][1])

    for signal in (data.get('Signals')):

        if 'Bio' in (signal.get('Type')):
            bio_count = (signal['Count'])
            insert_into_planet_bio_db(body_name, body_id, bio_count, region, genus)
            if check_body(body_name) == 1:
                bios = get_species_for_planet(body_name)
                for i in bios:
                    bio = i.split(' ')
                    update_bio_db(body_name, bio_count, bio[0], bio[1])


def get_species_for_planet(body_name):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select = cursor.execute("""SELECT bio from bio_scan_data where body_name = ?""",
                                (body_name,)).fetchall()
    data = []
    for i in select:
        for a in i:
            data.append(a)
    return data


def get_bio_scan_count(bio, body_name):  # Lese in der DB aus wie oft das BIO gescannt wurde
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    select = cursor.execute("""SELECT count(bio) from bio_scan_data where
                                    bio like ? and body_name = ? and scantype != 'Analyse' """,
                            (bio, body_name)).fetchall()

    if select[0][0] == 0:
        return ' ', 0
    else:
        return f'''Scan in Progress {select[0][0]} / 3''', select[0][0]


def get_codex_query(sf_cmdr, region, new_bio_data, b_date, e_date):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    key = (bool(sf_cmdr), bool(region), bool(new_bio_data))

    select = f'''SELECT ROW_NUMBER() OVER(ORDER BY date_log DESC, time_log DESC) AS Row,
                    c1.date_log, c1.time_log, c1.cmdr, c1.data, c1.bio_color, 
                    (SELECT worth FROM codex_entry ce WHERE ce.data = c1.data) AS product_price, 
                    c1.systemname, c1.body, c1.region FROM codex c1'''

    conditions = {
        (True, True, True): f'''{select} 
                                where cmdr = "{sf_cmdr}" and data like "{new_bio_data}" and region = "{region}" 
                                AND date_log BETWEEN "{b_date}" AND "{e_date}" 
                                ORDER BY date_log DESC, time_log DESC;''',
        (True, True, False): f'''{select}  
                                where cmdr = "{sf_cmdr}" and region = "{region}" 
                                AND date_log BETWEEN "{b_date}" AND "{e_date}" 
                                ORDER BY date_log DESC, time_log DESC;''',
        (True, False, True): f'''{select} 
                                where cmdr = "{sf_cmdr}" and data like "{new_bio_data}" 
                                AND date_log BETWEEN "{b_date}" AND "{e_date}" 
                                ORDER BY date_log DESC, time_log DESC;''',
        (True, False, False): f'''{select}
                                where cmdr = "{sf_cmdr}" AND date_log BETWEEN "{b_date}" AND "{e_date}"
                                ORDER BY date_log DESC, time_log DESC;''',
        (False, True, False): f'''{select} where region = "{region}" 
                                AND date_log BETWEEN "{b_date}" AND "{e_date}" 
                                ORDER BY date_log DESC, time_log DESC;''',
        (False, False, True): f'''{select} where data like "{new_bio_data}" 
                                AND date_log BETWEEN "{b_date}" AND "{e_date}" 
                                ORDER BY date_log DESC, time_log DESC;''',
        (False, True, True): f'''{select} where data like "{new_bio_data}" and region = "{region}"
                                AND date_log BETWEEN "{b_date}" AND "{e_date}" 
                                ORDER BY date_log DESC, time_log DESC;''',
        (False, False, False): f'''{select} where date_log BETWEEN "{b_date}" AND "{e_date}" 
                                ORDER BY date_log DESC, time_log DESC;'''}
    query = conditions.get(key)
    return query


def get_codex_data(sf_cmdr, region, bio_data):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    b_date = begin_time.get()
    e_date = end_time.get()

    if bio_data == '%---------%':
        new_bio_data = ''
    elif bio_data != '':
        new_bio_data = '%' + bio_data + '%'
    else:
        new_bio_data = ''

    query = get_codex_query(sf_cmdr, region, new_bio_data, b_date, e_date)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        data = cursor.execute(query).fetchall()
    return data


def check_body(body_name):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    select = cursor.execute("""SELECT body from planet_bio_info where body = ?""",
                            (body_name,)).fetchall()

    if select != []:
        # print('BODY in DB ' + body_name)
        return 1
    else:
        return 0


def check_cmdr(journal_file, cmdr):
    logger(journal_file, log_var)
    funktion = inspect.stack()[0][3] + " " + journal_file + " " + cmdr
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        log_cmdr = cursor.execute("Select CMDR from logfiles where Name = ?",
                                  (journal_file,)).fetchall()
        if log_cmdr and log_cmdr[0][0] != 'UNKNOWN':
            if log_cmdr[0][0] is not None:
                return log_cmdr[0][0]
        select = cursor.execute("Select * from logfiles where Name = ? and (CMDR is NULL or CMDR = 'UNKNOWN')",
                                (journal_file,)).fetchall()

    if cmdr != '' and select:  # Trage CMDR Name in Tabelle ein
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            cursor.execute("Update logfiles set CMDR = ? where Name = ? and (CMDR is NULL or CMDR = 'UNKNOWN')",
                           (cmdr, journal_file))
            connection.commit()
        return
    elif cmdr == '':
        cc_cmdr = read_cmdr(journal_file)
        if cc_cmdr and select:
            with sqlite3.connect(database) as connection:
                cursor = connection.cursor()
                cursor.execute("Update logfiles set CMDR = ? where Name = ? and CMDR is NULL",
                               (cc_cmdr, journal_file))
                connection.commit()
        return cc_cmdr


def system_scan(journal_file):  # Sucht im Logfile nach dem letzten System
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with open(journal_file, 'r', encoding='UTF8') as datei:
        for zeile in datei.readlines()[::-1]:  # Read File line by line reversed!
            data = read_json(zeile)
            if data.get('event') == "FSSDiscoveryScan" or data.get('event') == 'Location':
                body_count = data.get('BodyCount')
                system_name = data.get('SystemName')
                if system_name == None:
                    system_name = data.get('StarSystem')
                system_address = data.get('SystemAddress')
                systems = (system_name, system_address, body_count)
                logger(systems, log_var)
                return systems


def activ_planet_scan(file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with open(file, 'r', encoding='UTF8') as datei:
        for zeile in reversed(list(datei)):  # Read File line by line reversed using iterator!
            # for zeile in datei.readlines()[::-1]:  # Read File line by line reversed!
            data = read_json(zeile)
            if data.get('event') == 'SAASignalsFound' \
                    or data.get('event') == "Touchdown" or data.get('event') == 'Disembark':
                # print(data.get('Body'))
                return data.get('Body')


def check_table(var):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    tables = cursor.execute("SELECT name FROM sqlite_schema WHERE type='table'").fetchall()
    for i in tables:
        if var in i:
            return 1
    return 0


def get_color_or_distance(bio_name, star, materials):
    funktion = inspect.stack()[0][3]
    logger((funktion, bio_name), log_var)
    # gcod_time_1 = get_time()
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    bio_name = bio_name.split()
    bio_name2 = bio_name[0].capitalize() + ' ' + bio_name[1].capitalize()
    select = cursor.execute("""SELECT DISTINCT criteria, distance from bio_color where name = ?""",
                            (bio_name2,)).fetchone()
    star = star.lstrip()
    distance = select[1]
    data = []
    if select == None:
        return
    if select[0] == 'Star':
        color = cursor.execute("""SELECT COLOR from bio_color where name = ? and Criterium = ?""",
                               (bio_name2, star)).fetchall()
        if color != []:
            data.append(color[0])
    else:
        for mat in materials:
            mat = mat.capitalize()
            select = cursor.execute("""SELECT COLOR from bio_color where name = ? and Criterium = ?""",
                                    (bio_name2, mat)).fetchall()
            if select:
                data.append(select[0])
    if data == []:
        return

    return distance, data


def clean_string(string):
    string = string.replace(' atmosphere', '')
    string = string.lower()
    if 'rich' in string:
        string = string.replace(' rich', '-rich')
    return string


def select_prediction_db(star_type, planet_type, body_atmos, body_gravity, body_temp, body_pressure,
                         volcanism, sulphur_concentration):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    body_atmos = clean_string(body_atmos)
    planet_type = clean_string(planet_type)
    star_type = clean_string(star_type)
    body_temp = int(body_temp)

    if volcanism == 'Y':
        select_prediction = []
        select_bacterium = cursor.execute("""SELECT DISTINCT Name FROM Bio_prediction where
                                            Name like '%bacterium tela%' or  
                                            Name like '%bacterium cerberus%' and  
                                            (Planettype = ? and
                                            Athmospere like ? and
                                            Gravity_min < ? and Gravity_max > ? and
                                            Temp_min <= ? and Temp_max >= ? and
                                            Pressure_min < ? and Pressure_max > ?) """,
                                          (planet_type, body_atmos, body_gravity, body_gravity,
                                           body_temp, body_temp, body_pressure, body_pressure)).fetchall()
        if sulphur_concentration < 1:
            select_bio = cursor.execute("""SELECT DISTINCT Name FROM Bio_prediction where
                                            Name not like '%bacterium%' and
                                            Name not like '%recepta%' and
                                            Planettype = ? and
                                            Athmospere like ? and
                                            Gravity_min < ? and Gravity_max > ? and
                                            Temp_min <= ? and Temp_max >= ? and
                                            Pressure_min < ? and Pressure_max > ? """,
                                        (planet_type, body_atmos, body_gravity, body_gravity,
                                         body_temp, body_temp, body_pressure, body_pressure)).fetchall()
        else:
            select_bio = cursor.execute("""SELECT DISTINCT Name FROM Bio_prediction where
                                            Name not like '%bacterium%' and
                                            Planettype = ? and
                                            Athmospere like ? and
                                            Gravity_min < ? and Gravity_max > ? and
                                            Temp_min <= ? and Temp_max >= ? and
                                            Pressure_min < ? and Pressure_max > ? """,
                                        (planet_type, body_atmos, body_gravity, body_gravity,
                                         body_temp, body_temp, body_pressure, body_pressure)).fetchall()
        # print('select_bio', select_bio)

        for i in select_bacterium:
            select_prediction.append(i)
        for a in select_bio:
            select_prediction.append(a)
    else:
        if sulphur_concentration < 1:
            select_prediction = cursor.execute("""SELECT DISTINCT Name FROM Bio_prediction where
                                                Name not like '%recepta%' and
                                                Planettype = ? and
                                                Athmospere like ? and
                                                Gravity_min < ? and Gravity_max > ? and
                                                Temp_min <= ? and Temp_max >= ? and
                                                Volcanism = ?""",
                                               (planet_type, body_atmos, body_gravity, body_gravity,
                                                body_temp, body_temp,
                                                volcanism)).fetchall()

        else:
            select_prediction = cursor.execute("""SELECT DISTINCT Name FROM Bio_prediction where
                                                Planettype = ? and
                                                Athmospere like ? and
                                                Gravity_min < ? and Gravity_max > ? and
                                                Temp_min <= ? and Temp_max >= ? and
                                                Pressure_min < ? and Pressure_max > ? and 
                                                Volcanism = ?""",
                                               (planet_type, body_atmos, body_gravity, body_gravity,
                                                body_temp, body_temp, body_pressure, body_pressure,
                                                volcanism)).fetchall()
    # print(select_prediction)
    return select_prediction


def between_sql():

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        timestamp = "2024-07-23T19:06:17Z"
        start_exp, stop_exp = timestamp_in_event(timestamp, 2)  # Start und Stop der Expedition
        start_date = str(start_exp).split(' ')[0]
        start_time = str(start_exp).split(' ')[1]
        stop_date = str(stop_exp).split(' ')[0]
        stop_time = str(stop_exp).split(' ')[1]

        between_sql = f''' (date_log = "{start_date}" and time_log > "{start_time}" or date_log > "{start_date}") 
                and (date_log = "{stop_date}" and time_log < "{stop_time}" or date_log < "{stop_date}")'''
    return between_sql


def get_challenge_data(db_cmdr, value, criteria):
    timestamp = "2024-07-23T19:06:17Z"
    start_exp, stop_exp = timestamp_in_event(timestamp, 2)
    #  start_time  2024-11-03 20:30:00
    #  stop_time   2025-03-15 20:00:00

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        start_date = str(start_exp).split(' ')[0]
        start_time = str(start_exp).split(' ')[1]
        stop_date = str(stop_exp).split(' ')[0]
        stop_time = str(stop_exp).split(' ')[1]

        sql = f'''SELECT {value}({criteria}), date_log, time_log, cmdr from planet_infos where
        landable = 1 and discovered = 0 and cmdr = "{db_cmdr}" and
        (date_log = "{start_date}" and time_log > "{start_time}" or date_log > "{start_date}") and 
        (date_log = "{stop_date}" and time_log < "{stop_time}" or date_log < "{stop_date}")'''
        result = cursor.execute(sql).fetchone()

        if result:
            return result


def check_cloud_vs_local():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    upload = ''
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()

        upload, user = cursor.execute("SELECT exp_upload, exp_user FROM server").fetchone()
        cmdr = str(user)

        between = between_sql()

        jump_cloud = cursor.execute(f'''SELECT jump_distance from dvrii''').fetchone()
        jump_local = cursor.execute(f'''SELECT MAX(max_distance) from exploration_records 
                                                    where {between}''').fetchone()
        jump_cloud = get_value_or_default(jump_cloud, 1)
        jump_local = get_value_or_default(jump_local)

        #  compare Cloud and Local Jump Distance
        if jump_cloud < jump_local:
            select_jump = f'''SELECT date_log, time_log, cmdr, max_distance
                                from exploration_records where max_distance = {jump_local}'''
            data = cursor.execute(select_jump).fetchall()
            if data:
                current_data = {
                    "timestamp": str(data[0][0]) + 'T' + str(data[0][1]) + 'Z',
                    "cmdr": str(data[0][2]),
                    "JumpDist": str(data[0][3])
                }
                if upload_cloud_records(current_data) == 1:
                    create_logo(current_data)

        bodys_cloud = cursor.execute(f'''SELECT most_bodys from dvrii;''').fetchone()
        select_bodys = f'''SELECT MAX(max_body_count), date_log, time_log, cmdr
                                from exploration_records where {between}'''
        data = cursor.execute(select_bodys).fetchone()

        # Werte prüfen und Standardwert setzen, falls None
        bodys_cloud = get_value_or_default(bodys_cloud, 1)
        bodys_local = get_value_or_default(data)

        if bodys_cloud < bodys_local:
            current_data = {
                "timestamp": str(data[1]) + 'T' + str(data[2]) + 'Z',
                "cmdr": str(data[3]),
                "max_body_count": bodys_local
            }
            if upload_cloud_records(current_data) == 1:
                create_logo(current_data)

        processing_challenge_data('hottest_body', 'MAX',
                                  'Temperature', cmdr, 'SurfaceTemperature')

        processing_challenge_data('coldest_body', 'MIN',
                                  'Temperature', cmdr, 'SurfaceTemperature')

        processing_challenge_data('max_gravitation', 'MAX',
                                  'Gravity', cmdr, 'SurfaceGravity')

        processing_challenge_data('min_gravitation', 'MIN',
                                  'Gravity', cmdr, 'SurfaceGravity')

        processing_challenge_data('max_radius', 'MAX',
                                  'radius', cmdr, 'Radius')

        processing_challenge_data('min_radius', 'MIN',
                                  'radius', cmdr, 'Radius')

        check_player_death_total()
        check_wds()


def check_max(max_var):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    # get_cloud_records()

    with sqlite3.connect(database) as cm_connection:
        cm_cursor = cm_connection.cursor()

        timestamp = max_var.get("timestamp")
        start_time, stop_time = timestamp_in_event(timestamp, 2)

        cmdr = max_var.get("cmdr")
        icd_log_time = (log_date(timestamp))
        date_log = (icd_log_time[0] + "-" + icd_log_time[1] + "-" + icd_log_time[2])
        time_log = (icd_log_time[3] + ":" + icd_log_time[4] + ":" + icd_log_time[5])
        check_log_time = datetime(int(icd_log_time[0]), int(icd_log_time[1]), int(icd_log_time[2]),
                                  int(icd_log_time[3]), int(icd_log_time[4]))

        start_time = str(start_time).split()[0]
        stop_time = str(stop_time).split()[0]

        between_sql = f''' and date_log BETWEEN "{start_time}" and "{stop_time}"'''

        if max_var.get('max_body_count'):

            star_system = max_var.get('System')
            body_count = max_var.get("max_body_count")

            check_sql = f'''SELECT * FROM exploration_records where
            date_log = "{date_log}" and time_log = "{time_log}" and cmdr = "{cmdr}" and
            system = "{star_system}" and max_body_count = {body_count}'''
            result = cm_cursor.execute(check_sql).fetchall()
            if not result:
                cm_cursor.execute('''INSERT INTO exploration_records
                                    (date_log, time_log, cmdr, system, max_body_count) VALUES (?,?,?,?,?)''',
                                  (date_log, time_log, cmdr, star_system, body_count))
                cm_connection.commit()

            max_body_count_sql = f'''SELECT MAX(max_body_count) FROM exploration_records
            where max_body_count is not NULL {between_sql}'''
            max_body_count_db = cm_cursor.execute(max_body_count_sql).fetchone()
            if max_body_count_db:
                if max_body_count_db[0]:
                    set_dvr = f'''Update dvrii set most_bodys = {max_body_count_db[0]}'''
                    check_cloud = f'''select most_bodys from dvrii'''
                    cloud_data = cm_cursor.execute(check_cloud).fetchone()
                    if cloud_data:
                        if cloud_data[0] < body_count:
                            cm_cursor.execute(set_dvr)
                    else:
                        cm_cursor.execute(set_dvr)

        if max_var.get('JumpDist'):

            cmdr = max_var.get("cmdr")
            star_system = max_var.get("System")
            jump_dist = max_var.get("JumpDist")

            distance_sql = f'''SELECT MAX(max_distance) FROM exploration_records where
                                max_distance is not NULL {between_sql}'''
            max_distance_db = cm_cursor.execute(distance_sql).fetchone()

            check_sql = f'''SELECT * FROM exploration_records where
                        date_log = "{date_log}" and time_log = "{time_log}" and cmdr = "{cmdr}" and
                        max_distance = "{jump_dist}"'''
            result = cm_cursor.execute(check_sql).fetchall()
            if not result:
                cm_cursor.execute('''INSERT INTO exploration_records
                                            (date_log, time_log, cmdr, system, max_distance)
                                            VALUES (?,?,?,?,?)''',
                                  (date_log, time_log, cmdr, star_system, jump_dist))
                cm_connection.commit()

            set_dvr = f'''Update dvrii set jump_distance = {jump_dist}'''
            check_cloud = f'''select jump_distance from dvrii'''
            cloud_data = cm_cursor.execute(check_cloud).fetchone()
            if cloud_data:
                if cloud_data[0] < jump_dist:
                    cm_cursor.execute(set_dvr)
            else:
                cm_cursor.execute(set_dvr)


def check_wds():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    with sqlite3.connect(database) as cm_connection:
        cm_cursor = cm_connection.cursor()

        cursor = cm_connection.cursor()
        upload = cursor.execute("""SELECT exp_user FROM server""").fetchall()
        if upload[0][0] == 'anonym':
            return
        else:
            db_cmdr = upload[0][0]

        check_lokal_wd = f'''select COUNT(DISTINCT(star_type)) from white_dwarfs where cmdr = "{db_cmdr}"'''
        local_wd = cm_cursor.execute(check_lokal_wd).fetchone()
        if local_wd:
            check_cloud_wd = f'''select white_dwarf from dvrii'''
            cloud_wd = cm_cursor.execute(check_cloud_wd).fetchone()
            if cloud_wd:
                if cloud_wd[0] < local_wd[0]:
                    current_data = {
                        "cmdr": db_cmdr,
                        "timestamp": str(datetime.now())[0:19],
                        "white_dwarf": local_wd[0]
                    }
                    if upload_cloud_records(current_data) == 1:
                        create_logo(current_data)


def get_cloud_data():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with psycopg2.connect(dbname=snp_server.db_name, user=snp_server.db_user, password=snp_server.db_pass,
                          host=snp_server.db_host, port=5432) as psql_conn:
        psql = psql_conn.cursor()
        p_select = f'''SELECT * FROM expeditions where end_expediton = false;'''
        psql.execute(p_select)
        result = psql.fetchall()
        if result:
            start_expedition = (result[0][2])
            stop_expedition = (result[0][3])

            start = str(start_expedition)
            start_log_time = (log_date(start))
            start_date_log = (start_log_time[0] + "-" + start_log_time[1] + "-" + start_log_time[2])
            start_time_log = (start_log_time[3] + ":" + start_log_time[4] + ":" + start_log_time[5])

            stop = str(stop_expedition)
            stop_log_time = (log_date(stop))
            stop_date_log = (stop_log_time[0] + "-" + stop_log_time[1] + "-" + stop_log_time[2])
            stop_time_log = (stop_log_time[3] + ":" + stop_log_time[4] + ":" + stop_log_time[5])

            with sqlite3.connect(database) as connection:
                cursor = connection.cursor()
                select = f'''SELECT start_date, stop_date FROM active_expedition'''
                result_date = cursor.execute(select).fetchall()
                if result_date:
                    delete_sql = f'''DELETE FROM active_expedition;'''
                    cursor.execute(delete_sql)
                    connection.commit()

                insert_sql = f'''INSERT INTO active_expedition (start_date, start_time, stop_date, stop_time) 
                                    VALUES ("{start_date_log}" , "{start_time_log}", 
                                    "{stop_date_log}", "{stop_time_log}") '''
                cursor.execute(insert_sql)
                connection.commit()

            logger(f'''Start der Expedition {start_expedition}''', 2)
            logger(f'''Datum von Heute {datetime.now()}''', 2)
            logger(f'''Ende der Expedition {stop_expedition}''', 2)
            if start_expedition < datetime.now() < stop_expedition:
                logger('Auf Tour', 2)
                return 1
            else:
                return 0
        else:
            return 0


#  Liegt der timestamp in der Zeitspanne eines aktiven Events
def timestamp_in_event(timestamp, var):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    check_time = log_date(timestamp)
    check_time_new = datetime(int(check_time[0]), int(check_time[1]), int(check_time[2]),
                              int(check_time[3]), int(check_time[4]))

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select = f'''SELECT * FROM active_expedition'''
        result_date = cursor.execute(select).fetchall()
        if result_date:
            start_date = str(result_date[0][0])
            start_time = str(result_date[0][1])
            start = log_date(str(start_date) + 'T' + str(start_time) + 'Z')
            start_new = datetime(int(start[0]), int(start[1]), int(start[2]), int(start[3]), int(start[4]))

            stop_date = str(result_date[0][2])
            stop_time = str(result_date[0][3])
            stop = log_date(str(stop_date) + 'T' + str(stop_time) + 'Z')
            stop_new = datetime(int(stop[0]), int(stop[1]), int(stop[2]), int(stop[3]), int(stop[4]))
            #  Wenn check_time_new im Zeitraum der Expedition liegt return 1 ansonsten return 0
            if var == 1:
                if start_new < check_time_new < stop_new:
                    return 1
                else:
                    return 0
            elif var == 2:
                return start_new, stop_new


def get_cloud_records():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with psycopg2.connect(dbname=snp_server.db_name, user=snp_server.db_user, password=snp_server.db_pass,
                          host=snp_server.db_host, port=5432) as psql_conn:
        psql = psql_conn.cursor()
        select = f'''SELECT timestamp, cmdr, jump_distance, hottest_body, coldest_body, most_bodys, 
        death_counter,  max_gravitation, min_gravitation, white_dwarf, max_radius, min_radius FROM DVRII;'''
        psql.execute(select)
        result = psql.fetchall()

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute(f'''CREATE table IF NOT EXISTS temp_expedition
                            (date_log date, time_log timestamp, cmdr TEXT,
                                jump_distance INTEGER,
                                hottest_body REAL,
                                coldest_body REAL,
                                most_bodys INTEGER,
                                death_counter INTEGER,
                                max_gravitation REAL,
                                min_gravitation REAL,
                                white_dwarf INTEGER,
                                max_radius REAL,
                                min_radius REAL)''')
        cursor.execute(f'''DELETE FROM temp_expedition''')
        # cursor.execute(f'''DELETE FROM dvrii''')

        for i in result:
            # Extrahiere das Datum und die Zeit aus dem ersten Element, falls es ein datetime-Objekt ist
            if isinstance(i[0], datetime):
                date_value = i[0].date()
                time_value = i[0].time()
            else:
                date_value = i[0]
                time_value = None  # Falls es kein datetime-Objekt ist

            # Ersetze None-Werte durch NULL und formatierte Strings für SQL
            formatted_values = [
                f'"{value}"' if isinstance(value, str) else
                (f'"{value}"' if isinstance(value, (date, time)) else
                 ('NULL' if value is None else value))
                for value in (date_value, time_value, *i[1:])
            ]

            # SQL-String erstellen
            insert_sql = f'''INSERT INTO temp_expedition VALUES ({", ".join(map(str, formatted_values))})'''

            # Ausführen der SQL-Anweisung
            cursor.execute(insert_sql)
        connection.commit()

        between = between_sql()

        max_list = ['jump_distance', 'hottest_body', 'most_bodys', 'death_counter', 'max_gravitation',
                    'white_dwarf', 'max_radius']
        min_list = ['coldest_body', 'min_gravitation', 'min_radius']

        for i in max_list:
            sql = f'''SELECT date_log, time_log, cmdr, MAX({i}) from temp_expedition where {between}'''
            result = cursor.execute(sql).fetchone()
            if result[3]:
                insert = f'''UPDATE dvrii SET ({i}) = "{result[3]}" '''
                cursor.execute(insert)
                connection.commit()

        for i in min_list:
            sql = f'''SELECT date_log, time_log, cmdr, MIN({i}) from temp_expedition where {between}'''
            result = cursor.execute(sql).fetchone()
            if result[3]:
                insert = f'''UPDATE dvrii SET ({i}) = "{result[3]}" '''
                cursor.execute(insert)
                connection.commit()

        cursor.execute(f'''DROP TABLE temp_expedition''')


def set_cloud_records():
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute(f'''DELETE FROM DVRII''')
        cursor.execute(f'''INSERT INTO DVRII(jump_distance, hottest_body, coldest_body, 
        most_bodys, death_counter, white_dwarf, max_gravitation, min_gravitation, max_radius, min_radius) 
        VALUES (99999999, 99999999, 1, 99999999, 99999999, 99999999, 99999999, 0.0001, 99999999, 1)''')
        connection.commit()


def upload_cloud_records(max_var):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    logger('Folgende Daten werden hochgeladen', 2)
    logger(max_var, 2)
    logger(' ', 2)

    #  Prüfen ob, Upload aktiv ist.
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        upload = cursor.execute("""SELECT exp_upload FROM server""").fetchall()
        if upload[0][0] == 0:
            return 0
    cmdr = max_var.get("cmdr")
    timestamp = max_var.get("timestamp")
    if timestamp_in_event(timestamp, 1) == 0:
        return 0
    jump_distance = max_var.get("JumpDist")
    hottest_body = max_var.get('MAX_Temperature')
    coldest_body = max_var.get('MIN_Temperature')
    most_bodys = max_var.get("max_body_count")
    death_counter = max_var.get('death_counter')
    white_dwarf = max_var.get('white_dwarf')
    max_gravitation = max_var.get('MAX_Gravity')
    min_gravitation = max_var.get('MIN_Gravity')
    max_radius = max_var.get('MAX_radius')
    min_radius = max_var.get('MIN_radius')

    insert_query = f"""
    INSERT INTO DVRII (timestamp, cmdr, jump_distance, hottest_body, coldest_body, most_bodys, 
    death_counter, white_dwarf, max_gravitation, min_gravitation, max_radius, min_radius)
    VALUES ('{timestamp}', '{cmdr}', 
            {jump_distance if jump_distance is not None else 'NULL'}, 
            {hottest_body if hottest_body is not None else 'NULL'}, 
            {coldest_body if coldest_body is not None else 'NULL'}, 
            {most_bodys if most_bodys is not None else 'NULL'}, 
            {death_counter if death_counter is not None else 'NULL'}, 
            {white_dwarf if white_dwarf is not None else 'NULL'}, 
            {max_gravitation if max_gravitation is not None else 'NULL'},
            {min_gravitation if min_gravitation is not None else 'NULL'},
            {max_radius if max_radius is not None else 'NULL'},
            {min_radius if min_radius is not None else 'NULL'}
            )
    ON CONFLICT (cmdr, timestamp)
    DO UPDATE
    SET jump_distance = GREATEST(DVRII.jump_distance, EXCLUDED.jump_distance),
        hottest_body = GREATEST(DVRII.hottest_body, EXCLUDED.hottest_body),
        coldest_body = GREATEST(DVRII.coldest_body, EXCLUDED.coldest_body),
        most_bodys = GREATEST(DVRII.most_bodys, EXCLUDED.most_bodys),
        death_counter = GREATEST(DVRII.death_counter, EXCLUDED.death_counter),
        white_dwarf = GREATEST(DVRII.white_dwarf, EXCLUDED.white_dwarf),
        max_gravitation = GREATEST(DVRII.max_gravitation, EXCLUDED.max_gravitation),
        min_gravitation = GREATEST(DVRII.min_gravitation, EXCLUDED.min_gravitation),
        max_radius = GREATEST(DVRII.max_radius, EXCLUDED.max_radius),
        min_radius = GREATEST(DVRII.min_radius, EXCLUDED.min_radius)
        ;
    """
    with psycopg2.connect(dbname=snp_server.db_name, user=snp_server.db_user, password=snp_server.db_pass,
                          host=snp_server.db_host, port=5432) as psql_conn:
        psql = psql_conn.cursor()
        try:
            psql.execute(insert_query)
        except psycopg2.errors.SyntaxError:
            messagebox.showwarning("Upload nicht möglich", "Der Upload ist gestört")
    return 1


def check_player_death_total():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    #  Start und Enddatum der Expedition ermitteln
    with psycopg2.connect(dbname=snp_server.db_name, user=snp_server.db_user, password=snp_server.db_pass,
                          host=snp_server.db_host, port=5432) as psql_conn:
        psql = psql_conn.cursor()
        p_select = f'''SELECT * FROM expeditions where name = \'DVRII_NRNF\''''
        psql.execute(p_select)
        result = psql.fetchall()
        start_expedition = (result[0][2])
        stop_expedition = (result[0][3])

        start_expedition = (log_date(str(start_expedition)))
        start_expedition = (start_expedition[0] + "-" + start_expedition[1] + "-" + start_expedition[2])

        stop_expedition = (log_date(str(stop_expedition)))
        stop_expedition = (stop_expedition[0] + "-" + stop_expedition[1] + "-" + stop_expedition[2])

    with sqlite3.connect(database) as connection_sql:
        cursor = connection_sql.cursor()
        upload = cursor.execute("""SELECT exp_user FROM server""").fetchall()
        if upload[0][0] == 'anonym':
            return
        else:
            db_cmdr = upload[0][0]

    #  Wie oft ist der Spieler auf der Expedition gestorben
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select_sql = f'''SELECT Count(*) from player_death where cmdr = "{db_cmdr}" and date_log
        BETWEEN "{start_expedition}" and "{stop_expedition}"'''
        result = cursor.execute(select_sql).fetchall()

        dvrii_select = f'''SELECT death_counter from dvrii'''
        death_counter = cursor.execute(dvrii_select).fetchall()

        #  Wenn der lokale Wert größer ist, soll er hochgeladen werden.
        if result[0][0] > death_counter[0][0]:
            current_data = {
                "cmdr": db_cmdr,
                "timestamp": str(datetime.now())[0:19],
                "death_counter": result[0][0]
            }
            if upload_cloud_records(current_data) == 1:
                create_logo(current_data)


#  Check ob, wir im Tour Datum liegen
get_cloud_data()


def get_scan_time():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        between = between_sql()
        select_sql = f'''SELECT * FROM bio_scan_data where scantype = "Analyse" and {between}'''
        events = cursor.execute(select_sql).fetchall()

    # Kombiniere Datum und Zeit zu einem vollständigen Zeitstempel
    def parse_event_time(event):
        return datetime.strptime(event[0] + " " + event[1], "%Y-%m-%d %H:%M:%S")

    # Events sortieren nach Zeit
    events = sorted(events, key=parse_event_time)

    # Prüfe, ob 3 Events innerhalb von 5 Minuten liegen
    threshold = timedelta(minutes=70)
    for i in range(len(events) - 2):  # Mindestens 3 Events erforderlich
        print(i)
        t1 = parse_event_time(events[i])
        t3 = parse_event_time(events[i + 2])  # Drittes Event
        if t3 - t1 <= threshold:
            print("Drei Events innerhalb von 5 Minuten gefunden!")
            print(len(events))
            print(events)
            print(events[i])
            print(events[i + 1])
            print(events[i + 2])
            print(events[i + 3])
            print(t3 - t1)
            break
    else:
        print("Keine drei Events innerhalb von 5 Minuten gefunden.")


def processing_challenge_data(search_word, grenzwert, kriterium, cmdr, category):
    funktion = inspect.stack()[0][3]
    logger((search_word, grenzwert, kriterium, cmdr, category), log_var)
    kriterium_cloud = ''
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        kriterium_cloud = cursor.execute(f'''SELECT {search_word} from dvrii;''').fetchone()
    data = get_challenge_data(cmdr, grenzwert, kriterium)
    default = 1

    if grenzwert == 'MIN':
        default = 0

    # Werte prüfen und Standardwert setzen, falls None
    kriterium_cloud = get_value_or_default(kriterium_cloud, default)
    kriterium_local = get_value_or_default(data)

    current_data = processing_cloud_vs_local(kriterium_local, kriterium_cloud, data,
                                             kriterium, grenzwert)
    if current_data != 1:
        if upload_cloud_records(current_data) == 1:
            create_logo(current_data)


def exploration_challenge():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    global eddc_modul, status
    eddc_modul = 14
    status.configure(text='Challenge')

    #  Suche die Logs von gestern heute und morgen
    log_files = file_names(2)

    if not log_files:
        return

    #  Check ob, Upload aktiv ist
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        # Beide Werte in einer einzigen Abfrage abrufen
        upload, user = cursor.execute("SELECT exp_upload, exp_user FROM server").fetchone()

        # Bedingungen prüfen
        if upload == 0:
            return
        elif user == 'anonym':
            return
        else:
            db_cmdr = user
    t1 = get_time()
    for journal_file in log_files:
        check_logfile_in_db(journal_file, '', 'insert')
        tail_file(journal_file)
        logger(journal_file, log_var)

        cmdr = read_cmdr(journal_file)
        if cmdr != db_cmdr:
            continue
        with (open(journal_file, 'r', encoding='UTF8') as datei):
            line_in_db = check_logfile_in_db(journal_file, 'exp_line', '')
            for current_line_nr, line in enumerate(datei):
                if current_line_nr <= line_in_db:
                    continue

                data = read_json(line)
                timestamp = data.get("timestamp")
                event = data.get('event')
                match event:
                    case 'FSDJump':
                        current_jump = {
                            "cmdr": cmdr,
                            "timestamp": data.get("timestamp"),
                            "System": data.get("StarSystem"),
                            "SystemAddress": data.get("SystemAddress"),
                            "JumpDist": data.get("JumpDist")}
                        current_data2 = current_jump
                        check_max(current_data2)

                    case 'FSSAllBodiesFound':
                        current_bodys = {
                            "cmdr": cmdr,
                            "timestamp": data.get("timestamp"),
                            "System": data.get("SystemName"),
                            "SystemAddress": data.get("SystemAddress"),
                            "max_body_count": data.get("Count")}
                        check_max(current_bodys)

                    case 'Died':
                        timestamp = data.get('timestamp')
                        log_time = (log_date(timestamp))
                        date_log = (log_time[0] + "-" + log_time[1] + "-" + log_time[2])
                        time_log = (log_time[3] + ":" + log_time[4] + ":" + log_time[5])

                        with sqlite3.connect(database) as connection:
                            cursor = connection.cursor()
                            killer_rank = data.get('KillerRank')
                            killer = data.get('KillerName')
                            select_sql = f'''SELECT * from player_death where
                            date_log = "{date_log}" and time_log = "{time_log}"'''
                            result_of_select = cursor.execute(select_sql).fetchall()
                            if not result_of_select:
                                insert_sql = f'''Insert INTO player_death
                                (date_log, time_log, cmdr, KillerName, KillerRank) VALUES
                                ("{date_log}", "{time_log}","{cmdr}" ,"{killer}", "{killer_rank}")'''
                                cursor.execute(insert_sql)
                                connection.commit()

                            if killer == 'Sciencekeeper':
                                current_data2 = {
                                    "cmdr": cmdr,
                                    "timestamp": data.get("timestamp"),
                                    "killer": killer
                                }
                                select = f'''SELECT * from player_death where
                                date_log = "{date_log}" and
                                time_log = "{time_log}" and
                                killer = 'Sciencekeeper'
                                '''
                                if not cursor.execute(select):
                                    create_logo(current_data2)

                    case 'Scan':
                        if data.get('StarType'):
                            if 'D' in data.get('StarType') and not data.get('WasDiscovered'):
                                timestamp = data.get("timestamp")
                                icd_log_time = (log_date(timestamp))
                                date_log = (icd_log_time[0] + "-" + icd_log_time[1] + "-" + icd_log_time[2])
                                time_log = (icd_log_time[3] + ":" + icd_log_time[4] + ":" + icd_log_time[5])
                                star_system = data.get('StarSystem')
                                star_type = data.get('StarType')
                                with sqlite3.connect(database) as connection_sql:
                                    cursor = connection_sql.cursor()
                                    sql_select = cursor.execute(f'''SELECT * FROM white_dwarfs where
                                    date_log = "{date_log}" and time_log = "{time_log}"
                                    and cmdr = "{cmdr}" and star_type = "{star_type}"''').fetchall()
                                    if sql_select:
                                        logger(sql_select, log_var)
                                        continue
                                    cursor.execute('''INSERT INTO white_dwarfs
                                    (date_log, time_log, cmdr, star_system, star_type) VALUES(?,?,?,?,?)''',
                                                   (date_log, time_log, cmdr, star_system, star_type))
                                    connection.commit()

            check_logfile_in_db(journal_file, 'exp_line', current_line_nr)
    t2 = get_time()
    logger(('read Files Exploration Challenge ' + str(timedelta.total_seconds(t2 - t1)) + ' sek.'), 1)
    logger('Einlesen Fertig', 2)

    get_cloud_records()
    # t3 = get_time()
    # logger(('get_cloud_records ' + str(timedelta.total_seconds(t3 - t2)) + ' sek.'), 1)

    #  Prüfe ob, lokale Daten größer als Cloud Werte sind und löse create Logo aus
    check_cloud_vs_local()

    #  Setze die Tabelle DVRII auf standard Werte damit, wenn der Download nicht funktioniert,
    #  keine falschen Daten einen create Logo auslösen
    # set_cloud_records()


def get_mats_info(name):
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        sql = f'''select * from horizon_materials where name = "{name}"'''
        select = cursor.execute(sql).fetchall()
        if select:
            return select[0][1], select[0][2], select[0][3], select[0][4]
        else:
            return '', '', '', ''


def mats_in_db(date_log, time_log, name, count):
    name_en, name_de, category, grade = get_mats_info(name)
    if not name_en or not name_de or not category or not grade:
        logger(str(name) + ' not in DB', 2)
        return
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        ody_item_select = cursor.execute(f'''SELECT Name FROM engineering_mats WHERE 
                                                Name = "{name}" and date_log = "{date_log}" and 
                                                time_log = "{time_log}"''').fetchall()
        if not ody_item_select:
            cursor.execute("INSERT INTO engineering_mats VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                           (date_log, time_log, name, name_en, name_de, category, grade, count))
            connection.commit()


def engineering_mats(data):
    timestamp = data.get('timestamp', 0)
    icd_log_time = (log_date(timestamp))
    date_log = (icd_log_time[0] + "-" + icd_log_time[1] + "-" + icd_log_time[2])
    time_log = (icd_log_time[3] + ":" + icd_log_time[4] + ":" + icd_log_time[5])
    # name = data.get('Name_Localised', 0)
    # if name == 0:
    name = data.get('Name', 0)
    count = data.get('Count', 0)
    # category = data.get('Category',0)
    mats_in_db(date_log, time_log, name, count)


def print_engineering_mats():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    new_filter = f'''name like "%%"'''
    b_filter = filter_entry.get()
    if b_filter == 'Encoded':
        new_filter = f'''category = "Encoded"'''
    elif b_filter == 'Raw':
        new_filter = f'''category = "Raw"'''
    elif b_filter == 'Manufactured':
        new_filter = f'''category = "Manufactured"'''
    elif b_filter == 'Grade 1':
        new_filter = f'''grade = 1'''
    elif b_filter == 'Grade 2':
        new_filter = f'''grade = 2'''
    elif b_filter == 'Grade 3':
        new_filter = f'''grade = 3'''
    elif b_filter == 'Grade 4':
        new_filter = f'''grade = 4'''
    elif b_filter == 'Grade 5':
        new_filter = f'''grade = 5'''
    else:
        new_filter = f'''name like "%{b_filter}%"'''
    time = str(tick_hour_label.get()) + ':' + str(tick_minute_label.get())
    if tick:
        time_log = f'''time_log >= "{time}"'''
    else:
        time_log = f'''time_log <= "{time}"'''
    date_get = str(date_entry.get_date())
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        sql = f'''SELECT DISTINCT(name), name_en, name_de, category, grade, SUM(count) as Gesamt FROM engineering_mats 
                    where {new_filter} and date_log = "{date_get}" and {time_log} GROUP BY Name order by gesamt desc'''
        select = cursor.execute(sql).fetchall()
        return select


def extract_engi_stuff(data, state):
    name = data.get('Name_Localised', 0)
    if name == 0:
        name = data.get('Name', 0)
    count = data.get('Count', 0)
    engi_stuff_ody_db(str(name), int(count), state)
    return str(name), int(data['Count']), state


def engi_stuff_ody_db(name, count, state):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    if state < 0:
        count = count * (-1)
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        ody_item_select = cursor.execute("SELECT Name FROM odyssey WHERE Name = ?", (name,)).fetchall()

        if not ody_item_select:
            cursor.execute("INSERT INTO odyssey VALUES (?, ?)", (name, count))
            connection.commit()
        else:
            ody_item_select = cursor.execute("SELECT Count FROM odyssey WHERE Name = ?", (name,)).fetchone()
            count += int(ody_item_select[0])
            cursor.execute("UPDATE odyssey SET Count = ? where Name = ?", (count, name))
            connection.commit()


def print_engi_stuff_db(filter_b):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    filter_b = '%' + filter_b + '%'
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        ody_select = cursor.execute("SELECT * FROM odyssey ORDER BY Count DESC").fetchall()
    # print(ody_select)
    return ody_select


def war_cargo(data, file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    if data.get('event') == 'MissionAccepted':
        mission_id = data.get('MissionID')
        cargo_count = data.get('Count')
        destination = data.get('DestinationSystem')
        system_name = read_data_from_last_system(file, mission_id)
        update_cargo_db("", "", mission_id, cargo_count, system_name, 0)
        return ("", "", mission_id, cargo_count, system_name, 0)
    if data.get('event') == 'MissionCompleted':
        logtime = data.get('timestamp')
        icd_log_time = (log_date(logtime))
        date_log = (icd_log_time[0] + "-" + icd_log_time[1] + "-" + icd_log_time[2])
        time_log = (icd_log_time[3] + ":" + icd_log_time[4] + ":" + icd_log_time[5])
        mission_id = data.get('MissionID')
        update_cargo_db(date_log, time_log, mission_id, "", "", 1)
        return (date_log, time_log, mission_id, "", "", 1)


def update_cargo_db(date_log, time_log, mission_id, cargo_count, destination, completed):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("""CREATE table IF NOT EXISTS cargomissions 
                        (date_log date, 
                        time_log timestamp, 
                        missionID INTEGER, 
                        cargocount INTEGER,
                        completed INTEGER,
                        system TEXT 
                        )""")

    select = cursor.execute("SELECT * from cargomissions where missionID = ?", (mission_id,)).fetchall()
    if select == []:
        cursor.execute("INSERT INTO cargomissions VALUES (?,?,?,?,?,?)",
                       ("", "", mission_id, cargo_count, completed, destination))
        connection.commit()

    if completed == 1:
        cursor.execute("""UPDATE cargomissions set date_log = ?, time_log = ?, 
                       completed = ? where missionID = ? """,
                       (date_log, time_log, completed, mission_id))
        connection.commit()


def read_passengers(data, file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    if data.get('event') == 'MissionAccepted':
        mission_id = data.get('MissionID')
        passengercount = data.get('PassengerCount')
        faction = data.get('Faction')
        system_name = read_data_from_last_system(file, mission_id)
        if system_name == '':
            logger((funktion, data), 1)
        update_pass_db("", "", mission_id, passengercount, system_name, 0)
        return ("", "", mission_id, passengercount, system_name, 0)
    if data.get('event') == 'MissionCompleted':
        logtime = data.get('timestamp')
        icd_log_time = (log_date(logtime))
        date_log = (icd_log_time[0] + "-" + icd_log_time[1] + "-" + icd_log_time[2])
        time_log = (icd_log_time[3] + ":" + icd_log_time[4] + ":" + icd_log_time[5])
        mission_id = data.get('MissionID')
        update_pass_db(date_log, time_log, mission_id, 0, "", 1)
        return (date_log, time_log, mission_id, 0, "", 1)


def update_pass_db(date_log, time_log, mission_id, passengercount, system_name, completed):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("""CREATE table IF NOT EXISTS passengermissions 
                        (date_log date, 
                        time_log timestamp, 
                        missionID INTEGER, 
                        passengercount INTEGER, 
                        completed INTEGER, 
                        system TEXT)""")

    select = cursor.execute("SELECT * from passengermissions where missionID = ?", (mission_id,)).fetchall()
    if select == []:
        cursor.execute("INSERT INTO passengermissions VALUES (?,?,?,?,?,?)",
                       ("", "", mission_id, passengercount, completed, system_name))
        connection.commit()

    if completed == 1:
        cursor.execute("""UPDATE passengermissions set date_log = ?, time_log = ?,
                       completed = ? where missionID =?""",
                       (date_log, time_log, completed, mission_id))
        connection.commit()


def war_rescue(data, file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    if data.get('event') == 'MissionAccepted':
        mission_id = data.get('MissionID')
        cargo_count = data.get('Count')
        system_name = read_data_from_last_system(file, mission_id)
        update_rescue_db("", "", mission_id, cargo_count, 0, system_name)
        return ("", "", mission_id, cargo_count, 0, system_name)
    if data.get('event') == 'MissionCompleted':
        logtime = data.get('timestamp')
        icd_log_time = (log_date(logtime))
        date_log = (icd_log_time[0] + "-" + icd_log_time[1] + "-" + icd_log_time[2])
        time_log = (icd_log_time[3] + ":" + icd_log_time[4] + ":" + icd_log_time[5])
        mission_id = data.get('MissionID')
        update_rescue_db(date_log, time_log, mission_id, "", 1, "")
        return (date_log, time_log, mission_id, "", 1, "")


def update_rescue_db(date_log, time_log, mission_id, cargo_count, completed, system_name):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    # print(date_log, time_log, mission_id, cargo_count, completed, system_name)
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("""CREATE table IF NOT EXISTS rescuemissions 
                        (date_log date, 
                        time_log timestamp, 
                        missionID INTEGER, 
                        cargocount INTEGER,
                        completed INTEGER,
                        system TEXT 
                        )""")

    select = cursor.execute("SELECT * from rescuemissions where missionID = ?", (mission_id,)).fetchall()
    if select == []:
        cursor.execute("INSERT INTO rescuemissions VALUES (?,?,?,?,?,?)",
                       ("", "", mission_id, cargo_count, completed, system_name))
        connection.commit()

    if completed == 1:
        cursor.execute("""UPDATE rescuemissions set date_log = ?, time_log = ?, 
                       completed = ? where missionID = ? """,
                       (date_log, time_log, completed, mission_id))
        connection.commit()


def ausgabe_pass():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    global eddc_text_box

    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    cursor.execute("""CREATE table IF NOT EXISTS rescuemissions 
                        (date_log date, 
                        time_log timestamp, 
                        missionID INTEGER, 
                        cargocount INTEGER,
                        completed INTEGER,
                        system TEXT 
                        )""")

    cursor.execute("""CREATE table IF NOT EXISTS cargomissions 
                         (date_log date, 
                         time_log timestamp, 
                         missionID INTEGER, 
                         cargocount INTEGER,
                         completed INTEGER, 
                         system TEXT 
                         )""")

    cursor.execute("""CREATE table IF NOT EXISTS passengermissions 
                        (date_log date, 
                        time_log timestamp, 
                        missionID INTEGER, 
                        passengercount INTEGER, 
                        completed INTEGER, 
                        system TEXT)""")

    date_get = str(date_entry.get_date())

    my_date = date_get.split('-')
    tag = my_date[2]
    monat = my_date[1]
    jahr = my_date[0]

    # tag = Tag.get()
    # monat = Monat.get()
    # jahr = '20' + Jahr.get()
    date_ed = jahr + '-' + monat + '-' + tag

    select_pass = cursor.execute("SELECT DISTINCT system from passengermissions where date_log = ? and completed = 1",
                                 (date_ed,)).fetchall()
    select_cargo = cursor.execute("SELECT DISTINCT system from cargomissions where date_log = ? and completed = 1",
                                  (date_ed,)).fetchall()
    select_rescue = cursor.execute("SELECT DISTINCT system from rescuemissions where date_log = ? and completed = 1",
                                   (date_ed,)).fetchall()

    summe_cargo = []
    eddc_text_box.delete('1.0', END)
    for i in select_cargo:
        system_se = i[0]
        anzahl = cursor.execute("SELECT SUM(cargocount) from cargomissions where system = ? and date_log = ?",
                                (system_se, date_ed)).fetchone()
        summe_cargo.append((system_se, anzahl[0]))

    eddc_text_box.insert(END, (('Cargo transfered \t \t \t \n')))
    eddc_text_box.insert(END, ('\n'))
    gesamt_cargo = 0
    if summe_cargo != []:
        for i in summe_cargo:
            eddc_text_box.insert(END, (((str(i[0])) + '\t \t \t \t' + (str(i[1])) + 't \n')))
            tw_cargo_table.add_row((i[0], i[1]))
            gesamt_cargo += int(i[1])
    eddc_text_box.insert(END, ('─────────────────────────────\n'))
    eddc_text_box.insert(END, ('Insgesamt \t \t \t \t' + (str(gesamt_cargo)) + 't \n'))
    eddc_text_box.insert(END, ('\n'))

    summe_rescue = []
    for i in select_rescue:
        system_se = i[0]
        anzahl = cursor.execute("SELECT SUM(cargocount) from rescuemissions where system = ? and date_log = ?",
                                (system_se, date_ed)).fetchone()
        summe_rescue.append((system_se, anzahl[0]))

    eddc_text_box.insert(END, (('Escape Pods rescued \t \t \t \n')))
    eddc_text_box.insert(END, ('\n'))
    gesamt_rescue = 0
    if summe_rescue:
        for i in summe_rescue:
            eddc_text_box.insert(END, (((str(i[0])) + '\t \t \t \t' + (str(i[1])) + 't \n')))
            tw_rescue_table.add_row((i[0], i[1]))
            gesamt_rescue += int(i[1])
    eddc_text_box.insert(END, ('─────────────────────────────\n'))
    eddc_text_box.insert(END, ('Insgesamt \t \t \t \t' + (str(gesamt_rescue)) + 't \n'))
    eddc_text_box.insert(END, ('\n'))

    summe_pass = []
    for i in select_pass:
        system_se = i[0]
        anzahl = cursor.execute("SELECT SUM(passengercount) from passengermissions where system = ? and date_log = ?",
                                (system_se, date_ed)).fetchone()
        summe_pass.append((system_se, anzahl[0]))

    eddc_text_box.insert(END, (('Passengers rescued \t \t \t \n')))
    eddc_text_box.insert(END, ('\n'))
    gesamt = 0
    if summe_pass != []:
        for i in summe_pass:
            eddc_text_box.insert(END, (((str(i[0])) + '\t \t \t \t' + (str(i[1])) + ' \n')))
            tw_pass_table.add_row((i[0], i[1]))
            gesamt += int(i[1])
    eddc_text_box.insert(END, ('─────────────────────────────\n'))
    eddc_text_box.insert(END, ('Insgesamt \t \t \t \t' + (str(gesamt)) + ' \n'))


def war():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    try:
        tw_pass_table.clear_rows()
        tw_cargo_table.clear_rows()
        tw_rescue_table.clear_rows()
    except AttributeError:
        logger('NoData in tw rows', 2)

    files = file_names(3)
    # print(files)
    if files is not None:
        for journal_file in files:
            with open(journal_file, 'r', encoding='UTF8') as datei:
                for zeile in datei:
                    data = read_json(zeile)
                    if 'Mission_TW_Rescue' in data.get('Name', 'Kein'):
                        war_rescue(data, journal_file)
                    elif 'Mission_TW_Passenger' in data.get('Name', 'Kein'):
                        read_passengers(data, journal_file)
                    elif 'Mission_TW_Collect' in data.get('Name', 'Kein'):
                        war_cargo(data, journal_file)
    ausgabe_pass()


def menu(var):
    # Dem Modul entsprechenden werden GUI Elemente aus- bzw eingeschaltet oder de- bzw. aktiviert.

    global eddc_modul
    # print(var)
    menu_var = [0, 'BGS', 'ody_mats', 'MATS', 'CODEX', 'combat', 'thargoid', 'boxel', 'cube', 'war', 'reset_pos',
                'summary', 'war_progress', 'compass', 'exploration_challenge']
    # eddc_modul     1        2          3       4        5          6          7        8      9        10
    # eddc_modul    11          12           13           14

    # Filter.delete(0, END)
    if var == menu_var[1]:
        eddc_modul = 1
    else:
        lauf = -1
        for i in menu_var:
            lauf += 1
            if var == i:
                eddc_modul = lauf
    # print(eddc_modul)
    auswertung(eddc_modul)


def select_last_log_file():
    # Vorletztes Logfile aus der Datenbank auslesen und übergeben.
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS logfiles (Name TEXT, explorer INTEGER, "
                   "bgs INTEGER, Mats INTEGER, CMDR TEXT, last_line INTEGER, Full_scan_var INTEGER, "
                   "expedition INTEGER, exp_lines INTEGER)")
    item = cursor.execute("SELECT Name FROM logfiles", ()).fetchall()
    if item:
        # Das vorletzte Logfiles
        file = item[len(item) - 2]
    else:
        # Da noch keine Logfiles eingelesen wurden, werden alle eingelesen
        file = ['0']
    # print(file)
    return file


def check_last_logs(filenames_codex, length):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    last_log_file = select_last_log_file()[0]
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    items = cursor.execute("SELECT Name FROM logfiles").fetchall()
    if not items:
        return filenames_codex
    logfiles = []
    for item in items:
        logfiles.append(item[0])

    if last_log_file != '0':
        new = [item for item in filenames_codex if item not in logfiles]
        return new


def check_codex_table():
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    items = cursor.execute("SELECT * FROM codex").fetchall()

    if not items:
        logger('keine Daten in Codex', 12)
        return 0
    else:
        return 1


def get_processed_files():
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        sql = "select count(Name) from logfiles"
        cursor.execute(sql)
        result = cursor.fetchall()
        return result[0][0]


def run_once_rce(filenames):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    if check_codex_table() == 0:
        filenames = file_names(1)

    if len(filenames) > 5:
        logger('start run_once', 2)
        file_queue = queue.Queue()
        progress_queue = queue.Queue()

        for filename in filenames:
            file_queue.put(filename)

        for _ in range(min(5, len(filenames))):
            file_queue.put(None)  # Signal für den Thread zum Beenden

        thread_workers = []
        for _ in range(min(5, len(filenames))):
            thread = threading.Thread(target=read_codex_entrys_worker, args=(file_queue, progress_queue))
            thread.start()
            thread_workers.append(thread)

        update_progress_thread = threading.Thread(target=update_progress,
                                                  args=(progress_queue, thread_workers, len(filenames)))
        update_progress_thread.start()
    else:
        read_codex_entrys(filenames)
        custom_table_view()


def read_codex_entrys(filenames):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    t1 = get_time()
    last_log = len(filenames)
    files = check_last_logs(filenames, last_log)
    count = 1
    for count, filename in enumerate(files):
        check_logfile_in_db(filename, '', 'insert')
        if count % 10 == 0:
            eddc_text_box.delete('1.0', END)
            position = f'File \t{count + 1} of {len(files)}'  # count + 1, because count is zero-based
            eddc_text_box.insert(END, str(position))
        with open(filename, 'r', encoding='UTF8') as datei:
            for zeile in datei:
                data = read_json(zeile)
                event = data.get('event')
                match event:
                    case 'CodexEntry':
                        read_log_codex(data, filename)
                    case 'ScanOrganic':
                        try:
                            read_bio_data(data, filename)
                        except TypeError:
                            logger(data, 2)

    eddc_text_box.delete('1.0', END)
    position = f'File \t{len(files)} of {len(files)}'
    eddc_text_box.insert(END, str(position))
    t2 = get_time()
    # print('read_codex_entrys   ' + str(timedelta.total_seconds(t2 - t1)))
    # customtable_view()


def read_codex_entrys_worker(file_queue, progress_queue):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    t1 = get_time()
    count = 0

    while True:
        filename = file_queue.get()
        if filename is None:
            break

        check_logfile_in_db(filename, '', 'insert')

        with open(filename, 'r', encoding='UTF8') as datei:
            for zeile in datei:
                data = read_json(zeile)
                event = data.get('event')
                match event:
                    case 'CodexEntry':
                        read_log_codex(data, filename)
                    case 'ScanOrganic':
                        try:
                            read_bio_data(data, filename)
                        except TypeError:
                            logger(data, 2)

        count += 1
        progress_queue.put(count)

    progress_queue.put(None)


def update_progress(progress_queue, thread_workers, total_files):
    def process_progress_queue():
        while True:
            count = progress_queue.get()
            if count is None:
                if all(not thread.is_alive() for thread in thread_workers):
                    custom_table_view()
                    return  # Exit the function once all threads are done
                continue
            processed_files = int(get_processed_files())
            eddc_text_box.delete('1.0', END)
            position = f'File \t{processed_files} of {total_files}'
            eddc_text_box.insert(END, str(position))
            root.after(100, process_progress_queue)
            break

    root.after(100, process_progress_queue)


def combat_rank():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    eddc_text_box.delete(1.0, END)
    b_target = ''
    b_total_reward = ''
    sh_target = ''
    sh_total_reward = '0'
    pilot_rank = ''
    ranking = [('Harmless', 'Harmlos', 0, 1), ('Mostly Harmless', 'Zumeist Harmlos', 0, 2), ('Novice', 'Neuling', 0, 3),
               ('Competent', 'Kompetent', 0, 4), ('Expert', 'Experte', 0, 5), ('Master', 'Meister', 0, 6),
               ('Dangerous', 'Gefährlich', 0, 7), ('Deadly', 'Tödlich', 0, 8), ('Elite', 'Elite', 0, 9)]
    b_filter = filter_entry.get()

    filenames = file_names(0)
    for filename in filenames:
        with open(filename, 'r', encoding='UTF8') as datei:
            for zeile in datei:
                search_string2 = '"event":"ShipTargeted"'
                if (zeile.find(search_string2)) > -1:
                    data = read_json(zeile)
                    if data['TargetLocked']:
                        if data['ScanStage'] == 3 and data['LegalStatus'] == 'Wanted':
                            sh_target = data.get('Ship_Localised')
                            if sh_target is None:
                                sh_target = data.get('Ship')
                            sh_total_reward = data['Bounty']
                            pilot_rank = data['PilotRank']
                        elif data['ScanStage'] > 0:
                            if data['ScanStage'] != 3:
                                sh_target = data.get('Ship_Localised')
                                if sh_target is None:
                                    sh_target = data.get('Ship')
                                sh_total_reward = 0
                                pilot_rank = data['PilotRank']

                search_string = '"event":"Bounty"'
                if (zeile.find(search_string)) > -1:
                    # data = json.loads(zeile)
                    data = read_json(zeile)
                    b_target = data.get('Target_Localised')
                    if b_target is None:
                        b_target = data.get('Target')
                    b_total_reward = data['TotalReward']
                    tmp = int(sh_total_reward)
                    tmp += 300
                    if b_total_reward == tmp:
                        sh_total_reward = tmp
                    if b_target == sh_target and b_total_reward == sh_total_reward:
                        # print('')
                        # print(b_target, b_total_reward)
                        # print(sh_target, sh_total_reward, pilot_rank)
                        # print('')
                        cr_success = 0
                        i = 0
                        while i < len(ranking):
                            temp = ranking[i]
                            if pilot_rank == temp[0]:
                                tmp = int(temp[2]) + 1
                                ranking[i] = (temp[0], temp[1], tmp, temp[3])
                                cr_success = 1
                                break
                            i += 1
                        if cr_success == 0:
                            ranking.append((pilot_rank, pilot_rank, 1))
                            # print(ranking)
    logger((ranking), 2)
    select = set_language_db('leer')
    searcher = 1
    for a in ranking:
        if not select or select[0][0] == 'german' or select == 'leer':
            if b_filter == a[1]:
                searcher = a[3]
        else:
            if b_filter == a[0]:
                searcher = a[3]
    summe = 0
    for i in ranking:
        if i[2] > 0 and i[3] > (searcher - 1):
            if not select or select[0][0] == 'german' or select == 'leer':
                eddc_text_box.insert(END, ((str(i[1])) + '\t \t \t \t' + (str(i[2])) + '\n'))
                summe += i[2]
            else:
                eddc_text_box.insert(END, ((str(i[0])) + '\t \t \t \t' + (str(i[2])) + '\n'))
                summe += i[2]
    s = 'Summe', 0, summe
    eddc_text_box.insert(END, '───────────────────────────\n')
    eddc_text_box.insert(END, ((str(s[0])) + '\t \t \t \t' + (str(s[2])) + ' \n'))
    eddc_text_box.insert(END, '───────────────────────────\n')


def boxel_search(keyword):
    if keyword == ' ' or keyword == '':
        logger('boxel search input-', log_var)
    else:
        ssl._create_default_https_context = ssl._create_unverified_context
        url_ssl = 'https://www.edsm.net/api-v1/systems?systemName=' + keyword + '&showPrimaryStar=1'
        url_ssl = url_ssl.replace(' ', '%20')
        show_data_for_system(url_ssl)


def cube_search(data):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    eddc_text_box.delete(1.0, END)
    if data == ' ' or data == '':
        return
    elif ';' not in data:
        messagebox.showwarning("Eingabe inkorrekt", "Systemname;Kubus-Größe")
        return
    else:
        input = data.split(';')
        url = 'https://www.edsm.net/api-v1/cube-systems?systemName=' + urllib.parse.quote(input[0]) + \
              '&showPrimaryStar=1&size=' + urllib.parse.quote(input[1])
        show_data_for_system(url)


def show_data_for_system(url):
    data = filter_entry.get()
    data_split = data.split(';')
    edsm_systems = []
    ssl._create_default_https_context = ssl._create_unverified_context
    eddc_text_box.delete(1.0, END)
    with urllib.request.urlopen(url) as f:
        systems = json.load(f)
        if systems == {} or systems == []:
            eddc_text_box.delete(1.0, END)
            eddc_text_box.insert(END, 'EDSM hat keine Einträge in der Nähe gefunden')
            return
        for i in systems:
            name = (i.get('name'))
            _type = (i.get('primaryStar').get('type'))
            if not _type:
                _type = 'Unknown'
            edsm_systems.append((name, _type))
    if eddc_modul == 7:
        eddc_text_box.insert(END, ('Es gibt ' + str(len(edsm_systems) + 1) +
                                   ' Einträge zu diesem Boxel in der EDSM DB'))
    else:
        eddc_text_box.insert(END, ('Es gibt ' + str(len(edsm_systems)) +
                                   ' Einträge in einem Kubus von ' + str(data_split[1]) + ' ly auf EDSM'))
    eddc_text_box.insert(END, '\n')

    count = [('Wolf-Rayet', 0), ('Black Hole', 0), ('super giant', 0)]
    boxel_nr = []
    # print(edsm_systems)
    for edsm_system in edsm_systems:
        new = edsm_system[0].replace(data, '')
        if '-' not in new:
            if eddc_modul == 7 and new.isnumeric():
                lower_edsm = str(edsm_system[0]).lower()
                lower_data = str(data).lower()
                boxel_nr.append(int(lower_edsm.replace(lower_data, '')))
        for index, c in enumerate(count):
            if c[0] in edsm_system[1]:
                count[index] = c[0], (c[1] + 1)
    eddc_text_box.insert(END, ('\n'))

    for element in count:
        eddc_text_box.insert(END, ((str(element[0])) + ' ' + (str(element[1])) + '\n'))
    eddc_text_box.insert(END, ('\n'))

    refresh_button = check_auto_refresh.get()

    if refresh_button == 0:
        for i in edsm_systems:
            eddc_text_box.insert(END, ((str(i[0])) + '\t \t \t' + (str(i[1])) + '\n'))
            boxel_table.add_row(((str(i[0])), (str(i[1]))))
    else:
        if boxel_nr == []:
            eddc_text_box.delete(1.0, END)
            eddc_text_box.insert(END, 'EDSM hat keine Einträge in der Nähe gefunden')
            return
        boxel_nr.sort()
        last = (boxel_nr[(len(boxel_nr) - 1)])
        x = 0
        new_edsm = []
        while x <= last:
            if x not in boxel_nr:
                new_edsm.append(x)
            x += 1
        eddc_text_box.insert(END, 'Folgende Systeme sind bei EDSM nicht bekannt !!! \n')
        for new in new_edsm:
            eddc_text_box.insert(END, (data + (str(new)) + '\n'))
            boxel_table.add_row((data + (str(new)), ''))
    return 1


def thargoids():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    eddc_text_box.delete(1.0, END)
    b_filter = filter_entry.get()
    filenames = file_names(0)
    thargoid_rewards = [('Thargoid Scout 1', 65000, 0),
                        ('Thargoid Scout 2', 75000, 0),
                        ('Thargoid Cyclops', 6500000, 0),
                        ('Thargoid Basilisk', 20000000, 0),
                        ('Thargoid Medusa', 34000000, 0),
                        ('Thargoid Orthrus', 40000000, 0),
                        ('Thargoid Hydra', 50000000, 0)]

    for filename in filenames:
        with open(filename, 'r', encoding='UTF8') as datei:
            for zeile in datei:
                search_string = 'VictimFaction":"$faction_Thargoid'
                if (zeile.find(search_string)) > -1:
                    data = read_json(zeile)
                    reward = data['Reward']
                    for count, i in enumerate(thargoid_rewards):
                        if (i[1]) == reward:
                            wert = int(thargoid_rewards[count][2])
                            wert += 1
                            thargoid_rewards[count] = thargoid_rewards[count][0], thargoid_rewards[count][1], wert
    summe = 0
    for i in thargoid_rewards:
        if (i[2]) != 0:
            eddc_text_box.insert(END, ((str(i[0])) + '\t \t \t \t' + (str(i[2])) + '\n'))
            summe += int(i[1]) * int(i[2])
    summe = format(summe, ',d')
    s = 'Summe', summe
    eddc_text_box.insert(END, '───────────────────────────\n')
    eddc_text_box.insert(END, ((str(s[0])) + '\t \t \t' + (str(s[1])) + ' \n'))
    eddc_text_box.insert(END, '───────────────────────────\n')
    return


def get_bio_summary_from_db(search_date):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    select_count = cursor.execute("""select count(date_log) from codex where date_log = ?""",
                                  (search_date,)).fetchall()

    select_bios = cursor.execute("""select data from codex where date_log = ?""",
                                 (search_date,)).fetchall()

    if select_count != [(0), ]:
        count = (select_count[0][0])
    else:
        count = 0
    worth = 0

    for i in select_bios:
        # print(i)
        select_worth = cursor.execute("""select distinct(worth) from codex_entry where data =  ?""",
                                      (i[0],)).fetchall()
        if select_worth:
            temp = str(select_worth[0][0]).replace(',', '')

            worth += int(temp)
    worth = (f'{worth:,}'.replace(',', '.'))
    text = ('Es wurden ' + str(count) + ' bio. Proben gesammelt')
    text2 = ('Diese sind ' + str(worth) + ' Credits wert')
    if count > 0:
        return text, text2


def get_star_data(search_date):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    cursor.execute("""CREATE table IF NOT EXISTS star_data 
                        (date_log date, time_log timestamp, cmdr TEXT, body_id INTEGER, starsystem TEXT,
                        body_name TEXT, system_address INTEGER, Main TEXT, distance TEXT, 
                        startype TEXT, sub_class TEXT, mass REAL, radius REAL, age REAL, surface_temp REAL,
                        luminosity TEXT, rotation_period REAL,  axis_tilt REAL, discovered TEXT, mapped TEXT,
                        parents TEXT)""")

    select = cursor.execute("""select count(distinct(system_address)) from star_data where date_log = ?""",
                            (search_date,)).fetchall()

    text = []
    if select:
        datum = search_date.split('-')
        # print(str(datum[2]))
        new_date = str(datum[2]) + '.' + str(datum[1]) + '.' + str(datum[0])
        text.append('Am ' + new_date + ' hast du ')
        select_discovered = cursor.execute("""select count(DISTINCT(system_address)) from star_data where discovered = 0 
                                                and date_log = ?""", (search_date,)).fetchall()

        text.append(str(select[0][0]) + '  Systeme besucht ')
        text.append('davon waren ' + str(select_discovered[0][0]) + ' Systeme unentdeckt.')

        select_terra = cursor.execute("""select count(DISTINCT(systemid)) from planet_infos where 
                                                Terraform_state = 'Terraformable' and discovered = 0
                                                and date_log = ?""", (search_date,)).fetchall()

        planettype = ['Water world', 'Ammonia world', 'Earthlike body', 'Sudarsky class V gas giant']

        select_mapped = cursor.execute("""select count(*) from planet_infos where mapped = 1 
                                                and date_log = ?""", (search_date,)).fetchall()

        if select_terra[0][0] >= 1:
            text.append('- ' + str(select_terra[0][0]) + ' terraformirbare Trabanten')

        for i in planettype:
            sql = "select count(systemid) from planet_infos where PlanetType = '" \
                  + i + "' and discovered = 0 and date_log = ?"
            select_water = cursor.execute(sql, (search_date,)).fetchall()
            if select_water[0][0] > 0:
                if i == 'Sudarsky class V gas giant':
                    if select_water[0][0] > 1:
                        i = 'Gas Riesen der Klasse V'
                    else:
                        i = 'Gas Riese der Klasse V'
                if i == 'Water world':
                    if select_water[0][0] > 1:
                        i = 'Wasser Welten'
                    else:
                        i = 'Wasser Welt'
                if i == 'Ammonia world':
                    if select_water[0][0] > 1:
                        i = 'Ammoniak Welten'
                    else:
                        i = 'Ammoniak Welt'
                if i == 'Earthlike body':
                    if select_water[0][0] > 1:
                        i = 'Erdaehnliche Welten'
                    else:
                        i = 'Erdaehnliche Welt'
                text.append('- ' + str(select_water[0][0]) + ' ' + i)
        # print(text)
        return text


def check_logfile_in_db(file, state, read_state):
    funktion = inspect.stack()[0][3]
    logger((funktion, file, state, read_state), log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS logfiles (Name TEXT, explorer INTEGER, "
                       "bgs INTEGER, Mats INTEGER, CMDR TEXT, last_line INTEGER, Full_scan_var INTEGER,"
                       "expedition INTEGER, exp_lines INTEGER)")
        sql = f'''Select * from logfiles where Name = "{file}" and CMDR is NULL'''
        select = cursor.execute(sql).fetchall()
        if select:
            cmdr = check_cmdr(file, '')

        if state == 'line':
            if read_state == '':
                sql_2 = f'''Select last_line from logfiles where Name = "{file}"'''
                select = cursor.execute(sql_2).fetchall()
                if select:
                    if select[0][0] is not None:
                        return int(select[0][0])
                    else:
                        return 0
                else:
                    return 0
            else:
                sql = f'''UPDATE logfiles SET last_line = "{read_state}" where name = "{file}";'''
                cursor.execute(sql)
                connection.commit()
                return read_state

        if state == 'exp_line':
            if read_state == '':
                sql_2 = f'''Select exp_lines from logfiles where Name = "{file}"'''
                select = cursor.execute(sql_2).fetchall()
                if select:
                    if select[0][0] is not None:
                        return int(select[0][0])
                    else:
                        return 0
                else:
                    return 0
            else:
                sql = f'''UPDATE logfiles SET exp_lines = "{read_state}" where name = "{file}";'''
                cursor.execute(sql)
                connection.commit()
                return read_state

        if read_state == 'set' or read_state == 'check':
            sql = f'''SELECT * from logfiles where Name = "{file}" and "{state}" = 1'''
            select = cursor.execute(sql).fetchall()
            #  Wenn {state} nicht 1 ist, kann die Datei noch gelesen werden
            if not select:
                if read_state == 'check':
                    return 0
                if read_state == 'set':
                    temp = file_is_last(file)
                    if temp == 0:
                        return 0
                    sql = f'''UPDATE logfiles SET "{state}" = 1 where name = "{file}";'''
                    cursor.execute(sql)
                    connection.commit()
                    return 1
            else:
                #  Wenn {state} 1 ist, wurde die Datei vollständig für den Fall eingelesen
                return 1
        #  Logfile wird in die Tabelle hinzugefügt
        elif read_state == 'insert':
            insert = 0
            sql = "SELECT * from logfiles where Name = '" + file + "';"
            select = cursor.execute(sql).fetchall()

            if select == []:
                cmdr = read_cmdr(file)
                cursor.execute("INSERT INTO logfiles (Name, CMDR) VALUES (?, ?)", (file, cmdr))
                connection.commit()
                insert = 1
            return insert


def get_main_and_local(system_id, body_parents, body_name, system_name):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()

        cursor.execute("""CREATE table IF NOT EXISTS star_data 
                            (date_log date, time_log timestamp, cmdr TEXT, body_id INTEGER, starsystem TEXT,
                            body_name TEXT, system_address INTEGER, Main TEXT, distance TEXT, 
                            startype TEXT, sub_class TEXT, mass REAL, radius REAL, age REAL, surface_temp REAL,
                            luminosity TEXT, rotation_period REAL,  axis_tilt REAL, discovered TEXT, mapped TEXT,
                            parents TEXT)""")
        local_star = []
        if body_parents:
            for i in body_parents:
                star = i.get('Star')
                if star:
                    select_lokal = cursor.execute(
                        "SELECT startype FROM star_data where system_address = ? and body_id = ?",
                        (system_id, star)).fetchone()
                    if select_lokal:
                        local_star.append(select_lokal[0])
                if 'Belt' in body_name:
                    continue
                body_name_wo_system = body_name.replace((system_name), '')
                uppercase_letters_list = extract_uppercase_letters(body_name_wo_system)
                if len(uppercase_letters_list) >= 1:
                    for i in uppercase_letters_list:
                        for element in i:
                            select_lokal = cursor.execute(
                                "SELECT startype FROM star_data where starsystem = ? and body_name = ?",
                                (system_name, element)).fetchone()
                            if select_lokal:
                                local_star.append(select_lokal[0])

                # bary_centre = i.get('Null')
                # if bary_centre:
                # print('Barry found '+ str(body_parents) +' ' + body_name)
                # select_lokal = cursor.execute("SELECT startype FROM star_data where system_address = ? and body_id = ?",
                #                         (system_id, bary_centre)).fetchone()
                # print(select_lokal)
        select_main = cursor.execute("SELECT startype FROM star_data where system_address = ? and Main = 1",
                                     (system_id,)).fetchone()

    stars = []
    if select_main:
        stars.append(select_main[0])

    if local_star:
        for local_s in local_star:
            if local_s not in stars:
                stars.append(local_s)

    if select_main:
        return stars
    else:
        return 'NULL'


def create_cmdr_stat(text, search_date):
    # print(text)
    list1 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q']
    b = random.randint(0, 10)
    pic = 'images/Card_' + list1[b] + '.png'
    bg_treeview = resource_path(pic)
    img = Image.open(pic)
    d = ImageDraw.Draw(img)
    y = 0
    x = 0
    for i in text:
        # print(i)
        caption = i
        if 'Hallo' in i:
            font = ImageFont.truetype('arial.ttf', size=32)
            y += 50
            x = 35
        else:
            font = ImageFont.truetype('arial.ttf', size=25)
            if 'Welt' in i or 'Gas' in i or 'terra' in i:
                x = 70
            else:
                x = 50
            if y == 50:
                y += 80
            else:
                y += 45
        d.text((x, y), caption, fill='#f07b05', font=font,
               stroke_width=2, stroke_fill='black')
    font = ImageFont.truetype('arial.ttf', size=10)
    d.text((25, 555), 'created with EDDC', fill='#f07b05', font=font,
           stroke_width=2, stroke_fill='black')
    d.text((435, 555), '©MajorK', fill='#f07b05', font=font,
           stroke_width=2, stroke_fill='black')

    img.show()
    # img.save(str(search_date) + '-Explorer.png')


def get_cmdr_names():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select = f'''SELECT DISTINCT(cmdr) from logfiles'''
        result = cursor.execute(select).fetchall()
        cmdr = ['anonym']
        if result:
            eddc_text_box.insert(END, '\n CMDR Daten werden eingelesen \n')
            for i in result:
                for a in i:
                    if a != 'UNKNOWN':
                        cmdr.append(a)
            return cmdr
        else:
            global cmdr_lauf
            cmdr_lauf = 1
            log_files = file_names(5)
            for journal_file in log_files:
                check_logfile_in_db(journal_file, '', 'insert')
            get_cmdr_names()


def test():
    # get_scan_time()
    get_cloud_records()


def processing_cloud_vs_local(local, cloud, data, category, minmax):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    current_data = 1
    if local > 0:
        if minmax == 'MAX':
            if cloud < local:
                current_data = {
                    "timestamp": str(data[1]) + 'T' + str(data[2]) + 'Z',
                    "cmdr": str(data[3]),
                    f'''{minmax}_{category}''': round(local, 3),
                    "MinorMax": minmax
                }
        elif minmax == 'MIN':
            if cloud > local:
                current_data = {
                    "timestamp": str(data[1]) + 'T' + str(data[2]) + 'Z',
                    "cmdr": str(data[3]),
                    f'''{minmax}_{category}''': round(local, 3),
                    "MinorMax": minmax
                }
    return current_data


def display_cloud_records():
    funktion = inspect.stack()[0][3]

    logger('Daten in der Cloud', 2)

    insert_query = f'''SELECT * from dvrii;'''

    with psycopg2.connect(dbname=snp_server.db_name, user=snp_server.db_user, password=snp_server.db_pass,
                          host=snp_server.db_host, port=5432) as psql_conn:
        cursor = psql_conn.cursor()
        cursor.execute(insert_query)
        result = cursor.fetchall()

        table = PrettyTable(['Index', 'timestamp', 'cmdr', 'jump_distance', 'hottest_body',
                             'most_bodys', 'death_counter', 'max_gravitation', 'white_dwarf'])
        for i in result:
            table.add_row((i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8]))
        logger(table, 2)
        table.clear_rows()


def send_to_discord2(achievement_png):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with io.BytesIO() as image_binary:
        achievement_png.save(image_binary, format='PNG')
        image_binary.seek(0)

        webhook = DiscordWebhook(
            url="https://discord.com/api/webhooks/1267488940487610451\
            /OtpB_6s9hgczC8lQbrRuDsDTlwzRUII4OKD-uYd4vyJc5KxN-me72jdS6ISPpHFYK_lR",
            username="ExplorerChallenge")

        webhook.add_file(file=image_binary.read(), filename="example.png")
        response = webhook.execute()

        if response.status_code == 200:

            logger('Erfolgreich gesendet', 2)
        else:
            logger(f"Fehler beim Senden des Bildes: {response.status_code}", 2)


def create_logo(max_list):  # Badges für die exploration challenge!!
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    max_font_size_title = 24  # Maximale Schriftgröße für Titel
    cmdr = max_list.get("cmdr")
    pic = 'images/NRNF/pokal_jubel_feuerwerk_2.png'

    # Zeilenabstand
    line_spacing = 7
    max_font_cmdr = 20
    zusatz = ''
    data = ''
    text = ' '

    if max_list.get('max_body_count'):
        pic = 'images/NRNF/pokal_sternenkarte.png'
        data = max_list.get("max_body_count")
        text = 'Meisten Körper'
        zusatz = ''
        max_font_size_title = 26  # Maximale Schriftgröße für Titel

    elif max_list.get('JumpDist'):
        pic = 'images/NRNF/pokal_hyperraumsprung.png'
        data = max_list.get("JumpDist")
        text = 'Weitester Sprung'
        zusatz = 'LJ'
        max_font_size_title = 26  # Maximale Schriftgröße für Titel

    elif max_list.get('MAX_Temperature'):
        pic = 'images/NRNF/pokal_hotsurface.png'
        text = 'Heißeste Oberfläche'
        data = round(float(max_list.get("MAX_Temperature")), 3)
        zusatz = '°K'
        max_font_size_title = 22  # Maximale Schriftgröße für Titel

    elif max_list.get('MIN_Temperature'):
        pic = 'images/NRNF/pokal_eiskalt.png'
        text = 'Kälteste Oberfläche'
        data = round(float(max_list.get("MIN_Temperature")), 3)
        zusatz = '°K'
        max_font_size_title = 21  # Maximale Schriftgröße für Titel

    elif max_list.get('MAX_Gravity'):
        pic = 'images/NRNF/pokal_jubel_feuerwerk_1.png'
        text = 'Höchste Gravitation'
        data = round(float(max_list.get("MAX_Gravity")), 3)
        zusatz = 'G'
        max_font_size_title = 23  # Maximale Schriftgröße für Titel

    elif max_list.get('MIN_Gravity'):
        pic = 'images/NRNF/pokal_low_gravitation.png'
        text = 'Niedrigste Gravitation'
        data = round(float(max_list.get("MIN_Gravity")), 3)
        zusatz = 'G'
        max_font_size_title = 22  # Maximale Schriftgröße für Titel

    elif max_list.get('MAX_radius'):
        pic = 'images/NRNF/pokal_planet_gross.png'
        text = 'Größter Radius'
        data = round(float(max_list.get("MAX_radius") / 1000), 2)
        zusatz = ' KM'
        max_font_size_title = 23  # Maximale Schriftgröße für Titel

    elif max_list.get('MIN_radius'):
        pic = 'images/NRNF/pokal_planet_klein.png'
        text = 'kleinster Radius'
        data = round(float(max_list.get("MIN_radius") / 1000), 2)
        zusatz = ' KM'
        max_font_size_title = 23  # Maximale Schriftgröße für Titel

    elif max_list.get('death_counter'):
        pic = 'images/NRNF/pokal_deathcounter.png'
        data = max_list.get("death_counter")
        text = 'Die meisten Rebuys?'
        max_font_size_title = 22  # Maximale Schriftgröße für Titel

    elif max_list.get('killer'):
        pic = 'images/NRNF/pokal_killedbysciencekeeper.png'
        text = 'R. I. P.'
        data = str(max_list.get("timestamp"))[:10]
        zusatz = ''
        line_spacing = 8
        max_font_size_title = 26  # Maximale Schriftgröße für Titel

    elif max_list.get('white_dwarf'):
        pic = 'images/NRNF/pokal_jubel_feuerwerk_2.png'
        wd = max_list.get("white_dwarf")
        text = cmdr
        cmdr = f'''hat {wd} unterschiedliche'''
        data = 'Weiße Zwerge gefunden'
        zusatz = ''
        max_font_size_title = 22  # Maximale Schriftgröße für Titel
        max_font_cmdr = 18

    font = ImageFont.truetype('arial.ttf', size=25)

    achievement_png = Image.open(pic)

    # Definiere die Text Variable
    text_variable = f"{text}\n{cmdr}\n{data} {zusatz}"

    # Zeichnen vorbereiten
    d = ImageDraw.Draw(achievement_png)

    # Definiere das Textfeld (oben links und unten rechts)
    text_box_top_left = (240, 850)
    text_box_bottom_right = (425, 910)

    # Berechne die Breite und Höhe des Textfeldes
    box_width = text_box_bottom_right[0] - text_box_top_left[0]
    box_height = text_box_bottom_right[1] - text_box_top_left[1]

    # Funktion zur Berechnung der Textblockhöhe
    def calculate_total_height(d, font_title, font_cmdr, line_spacing):
        title_bbox = d.textbbox((0, 0), text, font=font_title)
        title_height = title_bbox[3] - title_bbox[1]

        cmdr_bbox = d.textbbox((0, 0), cmdr, font=font_cmdr)
        cmdr_height = cmdr_bbox[3] - cmdr_bbox[1]

        jump_text = f"{data} {zusatz}"
        jump_bbox = d.textbbox((0, 0), jump_text, font=font_cmdr)
        jump_height = jump_bbox[3] - jump_bbox[1]

        total_height = title_height + line_spacing + cmdr_height + line_spacing + jump_height
        return total_height

    # Schriftgrößen für Titel und Cmdr
    font_title = ImageFont.truetype('arial.ttf', size=max_font_size_title)
    font_cmdr = ImageFont.truetype('arial.ttf', size=max_font_cmdr)

    # Versuche, die Titelgröße maximal zu halten, während die Cmdr-Größe dynamisch verkleinert wird
    while True:
        total_height = calculate_total_height(d, font_title, font_cmdr, line_spacing)

        if total_height <= box_height:
            # Wenn der Textblock passt, breche die Schleife ab
            break
        break

    # Berechne die Y-Startposition (zentriert im Textfeld)
    start_y = text_box_top_left[1] + (box_height - total_height) // 2
    title = text

    # Zeichne die erste Zeile (Titel) zentriert
    title_width = d.textbbox((0, 0), title, font=font_title)[2] - d.textbbox((0, 0), title, font=font_title)[0]
    start_x_title = text_box_top_left[0] + (box_width - title_width) // 2
    d.text((start_x_title, start_y), title, fill='#f07b05', font=font_title, stroke_width=3, stroke_fill='black')

    # Aktualisiere die Y-Position für die nächste Zeile
    start_y += (d.textbbox((0, 0), title, font=font_title)[3] - d.textbbox((0, 0), title, font=font_title)[
        1]) + line_spacing

    # Zeichne die zweite Zeile (Cmdr) zentriert
    cmdr_width = d.textbbox((0, 0), cmdr, font=font_cmdr)[2] - d.textbbox((0, 0), cmdr, font=font_cmdr)[0]
    start_x_cmdr = text_box_top_left[0] + (box_width - cmdr_width) // 2
    d.text((start_x_cmdr, start_y), cmdr, fill='#f07b05', font=font_cmdr, stroke_width=3, stroke_fill='black')

    # Aktualisiere die Y-Position für die nächste Zeile
    start_y += (d.textbbox((0, 0), cmdr, font=font_cmdr)[3] - d.textbbox((0, 0), cmdr, font=font_cmdr)[
        1]) + line_spacing

    # Zeichne die dritte Zeile (Sprungweite) zentriert
    jump_text = f"{data} {zusatz}"
    jump_width = d.textbbox((0, 0), jump_text, font=font_cmdr)[2] - d.textbbox((0, 0), jump_text, font=font_cmdr)[0]
    start_x_jump = text_box_top_left[0] + (box_width - jump_width) // 2
    d.text((start_x_jump, start_y), jump_text, fill='#f07b05', font=font_cmdr, stroke_width=3, stroke_fill='black')

    # thread_rce.start()
    # thread_rce = threading.Thread(target=achievement_png.show, args=())
    send_to_discord2(achievement_png)


def rescan_files():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    if rescan_lauf == 0:
        thread_rce = threading.Thread(target=scan_files, args=())
        thread_rce.start()


def scan_files():
    files = file_names(1)  # Alle Logfile werden geladen
    t1 = get_time()
    count = 1
    global rescan_lauf
    rescan_lauf = 1

    for count, filename in enumerate(files):
        check_logfile_in_db(filename, '', 'insert')
        if count % 10 == 0:
            eddc_text_box.delete('1.0', END)
            postion = 'File \t' + str(count) + ' of ' + str(len(files))
            eddc_text_box.insert(END, str(postion))
        with open(filename, 'r', encoding='UTF8') as datei:
            for zeile in datei:
                data = read_json(zeile)
                event = data.get('event')
                match event:
                    case 'CodexEntry':
                        read_log_codex(data, filename)
                    case 'Analyse':
                        read_bio_data(data, filename)
    if (len(files)) == (count + 1):
        eddc_text_box.delete('1.0', END)
        postion = 'File \t' + str(count + 1) + ' of ' + str(len(files))
        eddc_text_box.insert(END, str(postion))
    rescan_lauf = 0
    t2 = get_time()
    logger(('rescan codex ' + str(timedelta.total_seconds(t2 - t1)) + ' sek.'), 1)


def set_fully_read(file, state):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    is_file = os.path.isfile(file)
    if not is_file:
        return

    if os.path.getsize(file) == 0:
        check_logfile_in_db(file, state, 'set')

    temp = file_is_last(file)
    if temp == 0:
        return 0

        # print(os.path.getsize(file))
    if check_logfile_in_db(file, state, 'check') != 1:
        with open(file, 'r', encoding='UTF8') as datei_2:

            for zeile in datei_2.readlines()[::-1]:  # Read File line by line reversed!
                data = read_json(zeile)
                if data.get('event') == 'Shutdown':
                    logger('------------------ERROR------------------', 1)
                    logger(data, 2)
                    logger('------------------ERROR------------------', 1)
                    check_logfile_in_db(file, state, 'set')
                    return
                timestamp = data.get('timestamp')
                tod = (log_date(timestamp))
                date_log = date((int(tod[0])), int(tod[1]), int(tod[2]))
                yesterday = date.today() - timedelta(days=1)

                if date_log <= yesterday:
                    # print('SET ---')
                    check_logfile_in_db(file, state, 'set')
                break
    else:
        logger('already Fully_read', 1)


def full_scan():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    filenames = file_names(1)
    for i in filenames:
        check_logfile_in_db(i, '', 'insert')

    with (sqlite3.connect(database) as connection):
        cursor = connection.cursor()
        select = cursor.execute("select Name from logfiles where explorer is NULL").fetchall()
        full_scan_var = cursor.execute("select Full_scan_var from server").fetchall()

    eddc_text_box.delete(1.0, END)
    eddc_text_box.insert(INSERT, 'Auswertung läuft von ' + str(full_scan_var[0][0]) + ' Dateien')

    global fully
    if select and fully == 0:
        counter = 1
        fully = 1
        length = (len(select) - 1)
        logger((select[length][0], 2), 2)
        while length != 0 and counter != full_scan_var[0][0]:
            length = (len(select) - counter)
            counter += 1
            with open(select[length][0], 'r', encoding='UTF8') as datei:
                total_lines = sum(1 for line in datei)
                if total_lines < 5:
                    set_fully_read(select[length][0], 'explorer')
            tail_file(select[length][0])
            if check_logfile_in_db(select[length][0], 'explorer', 'check') != 1:
                set_fully_read(select[length][0], 'explorer')
                t.sleep(0.1)
                fully = 0
            else:
                fully = 0
        logger(funktion + ' done', 2)


def summary():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    text = []
    files = file_names(0)  # Logs von dem Tag X
    if len(files) > 0:
        last = files[len(files) - 1]
    else:
        last = files
    if not last:
        return

    cmdr = read_cmdr(last)
    text.append('Hallo CMDR ' + cmdr)
    for filename in files:
        tail_file(filename)

    date_get = str(date_entry.get_date())
    my_date = date_get.split('-')
    day = my_date[2]
    month = my_date[1]
    year = my_date[0].replace('20', '', 1)
    search_date = '20' + year + '-' + month + '-' + day
    text3 = (get_star_data(search_date))

    # text3.replace('Sudarsky class V gas giant', 'Gas Riese der Klasse V')
    if text3 != None:
        for i in text3:
            text.append(i)

    text2 = get_bio_summary_from_db(search_date)
    if text2 != None:
        text.append(text2[0])
        text.append(text2[1])
    create_cmdr_stat(text, search_date)


def auswertung(eddc_modul):
    global aus_var
    funktion = inspect.stack()[0][3] + ' eddc_modul ' + str(eddc_modul) + ' ' + str(aus_var)
    logger(funktion, log_var)

    # if aus_var == 1 and eddc_modul != 13:
    #     return
    # else:
    #     aus_var = 1

    if eddc_modul == 13:
        aus_var = 0
    create_tables()
    # system.delete(.0, END)
    check_but.configure(text='Auto refresh   ')
    eddc_text_box.delete(1.0, "end")
    eddc_text_box.insert("end", "Auswertung läuft\n\n")

    if eddc_modul == 10:  # Reset Position
        b_filter = filter_entry.get()
        reset_pos()
        # status.config(text='Test')
        aus_var = 0
        return

    if eddc_modul == 11:  # Tages Auswertung
        b_filter = filter_entry.get()
        summary()
        status.configure(text='Summary')
        aus_var = 0
        return

    if eddc_modul == 12:  # war_progress
        b_filter = filter_entry.get()
        war_progress()
        status.configure(text='War Progress')
        aus_var = 0
        return

    if eddc_modul == 13:  # compass_gui
        b_filter = filter_entry.get()
        status.configure(text='Compass')
        compass_gui()
        aus_var = 1
        return

    if eddc_modul == 14:  # exploration_challenge
        b_filter = filter_entry.get()
        status.configure(text='Challenge')
        print('exploration_challenge')
        exploration_challenge()
        aus_var = 0
        return

    if eddc_modul == 15:  # get_cmdr_names
        get_cmdr_names()
        aus_var = 0
        return

    if eddc_modul == 16:  # test
        status.configure(text='test')
        full_scan()
        aus_var = 0
        return

    if eddc_modul == 7:  # Boxel Analyser
        b_filter = filter_entry.get()
        check_but.configure(text='reverse         ')
        boxel_search(b_filter)
        status.configure(text='Boxel Analyse')
        aus_var = 0
        return

    elif eddc_modul == 9:  # Thargoid WAR
        status.configure(text='Thargoid-War')
        war()
        aus_var = 0
        return

    if eddc_modul == 8:  # Sphere Analyser
        b_filter = filter_entry.get()
        check_but.configure(text='reverse         ')
        cube_search(b_filter)
        status.configure(text='Kubus Analyse')
        aus_var = 0
        return

    last_log_file = select_last_log_file()[0]
    # print('the log-file before the last from DB ', last_log_file)
    if last_log_file != '0' or eddc_modul != 4:
        filenames = file_names(0)  # Alle Logfiles der Eingabe entsprechend

    else:
        filenames = file_names(1)  # Alle Logfiles

    nodata = 0
    nodata_voucher = 0

    logger(filenames, log_var)

    auto_refresh = False
    lauf_r = 0
    if auto_refresh is True:
        auto = len(filenames) - 1
        while lauf_r < auto:
            del filenames[lauf_r]
            lauf_r += 1
    if not filenames:
        # Wenn es keine logfiles an diesem Tag gibt, dann
        logger('Keine Log-Files für Heute vorhanden', 1)
        if eddc_modul == 4:
            status.configure(text='Codex')
            filenames = file_names(1)  # Alle Logfile werden geladen
            last_log = (len(filenames))
            files = check_last_logs(filenames, last_log)
            run_once_rce(files)
            aus_var = 0
        else:
            eddc_text_box.delete(.0, END)
            eddc_text_box.insert(END, 'Keine Log-Files für den Tag vorhanden')
            aus_var = 0
    else:
        if eddc_modul == 1:  # BGS Main
            aus_var = 0
            status.configure(text='BGS Mode')
            filenames = file_names(0)
            for filename in filenames:
                check_logfile_in_db(filename, '', 'insert')
                if check_logfile_in_db(filename, 'bgs', 'read') != 1:
                    einfluss_auslesen(filename)
                    # ground_combat(filename)
                    redeem_voucher(filename)
                    multi_sell_exploration_data(filename)
                    market_sell(filename)
            b_filter = filter_entry.get()
            eddc_text_box.delete(.0, END)
            data = print_vouchers_db(b_filter)
            if data:
                eddc_text_box.insert(END,
                                     '    ----------    Bounty, Bonds, ExplorerData and Trade    ----------\n\n')
                for i in data:
                    tmp = f"{i[3]:,}"
                    tmp = tmp.replace(',', '.')
                    tmp = tmp + ' Cr'
                    eddc_text_box.insert(END,
                                         ((str(i[1])[0:15]) + '\t\t' + (str(i[2])[0:25]) + '\t\t\t' + (str(i[0])[0:15])
                                          + '\n\t\t\t\t\t' + tmp + '\n'))
                    voucher.add_row((i[0], i[1], i[2], tmp))
                    nodata = 0
            else:
                nodata_voucher = 1
                logger('NO VOUCHER DATA', log_var)

            failed_mission()  # update auf die influence tabelle
            data = print_influence_db(b_filter)
            # print(data)
            if data:
                eddc_text_box.insert(END,
                                     (
                                         '\n    -----------------------------------  Einfluss  '
                                         '-----------------------------------\n'))
                eddc_text_box.insert(END, '\n')
                for i in data:
                    eddc_text_box.insert(END, (
                            (str(i[0])[0:15]) + '\t\t' + (str(i[1])[0:25]) + '\t\t\t\t' + str(i[2]) + '\n'))
                    bgs.add_row((i[0], i[1], i[2]))
                nodata = 0
            else:
                nodata = 1
            if nodata == 1 and nodata_voucher == 1:
                eddc_text_box.delete(.0, END)
                eddc_text_box.insert(END, 'Keine Daten vorhanden Überprüfe den Tick')

            thread_star_systems = threading.Thread(target=star_systems_db, args=())
            thread_star_systems.start()
            update_eddc_db()

        elif eddc_modul == 3:  # Collected Enginieering Material
            aus_var = 0
            status.configure(text='MATS Mode')
            for filename in filenames:
                if check_logfile_in_db(filename, 'Mats', 'check') == 0:
                    mats_auslesen(filename)
                    check_logfile_in_db(filename, 'Mats', 'set')
                else:
                    logger('no file read', 2)
            b_filter = filter_entry.get()
            data = print_engineering_mats()
            summe = 0
            eddc_text_box.delete(.0, END)

            lang = read_language()
            eddc_text_box.insert(END, (('Name			Type		Grade	Count\n')))
            eddc_text_box.insert(END, ('────────────────────────────────────────\n'))
            for i in data:
                if lang == 'english':
                    name = str(i[1])
                else:
                    name = str(i[2])
                rest = '\t\t\t' + (str(i[3])) + '\t\t' + (str(i[4])) + '\t' + (str(i[5])) + '\n'
                eddc_text_box.insert(END, ((name[0:25]) + rest))
                mats_table.add_row((name, i[2], i[4], i[5]))

                summe += i[5]
            a = 'Summe', summe
            eddc_text_box.insert(END, ('\n'))
            eddc_text_box.insert(END, ('────────────────────────────────────────\n'))
            eddc_text_box.insert(END, ((str(a[0])) + '\t\t\t\t\t     ' + (str(a[1])) + '\n'))
            eddc_text_box.insert(END, ('────────────────────────────────────────\n'))
            thread_star_systems = threading.Thread(target=star_systems_db, args=())
            thread_star_systems.start()

        elif eddc_modul == 2:  # Collected Odyssey on Foot Material
            aus_var = 0
            status.configure(text='Odyssey MATS')
            for filename in filenames:
                ody_mats_auslesen(filename)
            b_filter = filter_entry.get()
            data = print_engi_stuff_db(b_filter)
            summe = 0
            eddc_text_box.delete(.0, END)
            for i in data:
                eddc_text_box.insert(END, ((str(i[0])) + '\t \t \t \t' + (str(i[1])) + '\n'))
                mats_table.add_row((i[0], i[1]))
                summe += i[1]
            a = 'Summe', summe
            eddc_text_box.insert(END, ('───────────────────────────\n'))
            eddc_text_box.insert(END, ((str(a[0])) + '\t \t \t \t' + (str(a[1])) + '\n'))
            eddc_text_box.insert(END, ('───────────────────────────\n'))
            thread_star_systems = threading.Thread(target=star_systems_db, args=())
            thread_star_systems.start()
        elif eddc_modul == 4:  # Codex Treeview
            status.configure(text='Codex')
            logger('filenames', 2)
            run_once_rce(filenames)
            aus_var = 0

        elif eddc_modul == 5:  # Kampfrang
            status.configure(text='Combat Rank')
            combat_rank()
            aus_var = 0

        elif eddc_modul == 6:  # Thargoid
            status.configure(text='Thargoids')
            thargoids()
            aus_var = 0
    aus_var = 0


def read_language():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        item = cursor.execute("SELECT lang FROM lan_db").fetchone()
        return item[0]


def set_language_db(var):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        # print('before ', var)
        if var == 'leer':
            item = cursor.execute("SELECT lang FROM lan_db").fetchall()
            # print(item)
            if not item:
                cursor.execute("INSERT INTO lan_db VALUES (?, ?)", ('german', '1'))
                connection.commit()
            else:
                return item
        elif var == 'german':
            cursor.execute("UPDATE lan_db SET lang = ?", (var,))
            connection.commit()
        elif var == 'english':
            cursor.execute("UPDATE lan_db SET lang = ?", (var,))
            connection.commit()
    return var


# Funktion, um die Existenz einer Spalte zu prüfen
def column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [info[1] for info in cursor.fetchall()]  # Spaltennamen aus der zweiten Spalte (Index 1)
    return column_name in columns


def update_db(old_version):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    insert_sql = """Insert into Bio_prediction VALUES 
            ('bacterium bullaris', 'm', 'icy body', 0.001, 0.099,0.03,0.6,'thin methane',65.0,110.0,'N')"""

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()

        select = cursor.execute("""SELECT * from Bio_prediction where name = 'bacterium bullaris' and startype = 'm' 
                                    and Planettype = 'icy body' and Athmospere 
                                    like '%thin methane%' and Temp_max = 110""").fetchall()
        if not select:
            logger('UPDATE SQL', 2)
            cursor.execute(insert_sql)
            connection.commit()

        if not column_exists(cursor, 'server', 'Full_scan_var'):
            cursor.execute("ALTER TABLE server ADD Full_scan_var INTEGER")

        if not column_exists(cursor, 'dvrii', 'min_gravitation'):
            cursor.execute("ALTER TABLE dvrii ADD min_gravitation REAL")

        if not column_exists(cursor, 'dvrii', 'coldest_body'):
            cursor.execute("ALTER TABLE dvrii ADD coldest_body REAL")

        if not column_exists(cursor, 'dvrii', 'max_radius'):
            cursor.execute("ALTER TABLE dvrii ADD max_radius REAL")

        if not column_exists(cursor, 'dvrii', 'min_radius'):
            cursor.execute("ALTER TABLE dvrii ADD min_radius REAL")

        if not column_exists(cursor, 'star_data', 'cmdr'):
            cursor.execute("ALTER TABLE star_data ADD cmdr TEXT")

        if not column_exists(cursor, 'planet_infos', 'cmdr'):
            cursor.execute("ALTER TABLE planet_infos ADD cmdr TEXT")
        connection.commit()
    logger('update DB', 1)
    create_tables()


def db_version():  # Programmstand und DB Stand werden miteinander verglichen
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        item = cursor.execute("SELECT version FROM db_version").fetchall()
        if not item:
            cursor.execute("INSERT INTO db_version VALUES (?)", (version_number,))
            connection.commit()
        elif item[0][0] != version_number:
            cursor.execute("UPDATE db_version set version = ?", (version_number,))
            connection.commit()
            logger('Update Version', 2)
            update_db(item[0][0])
        elif item[0][0] == version_number:
            logger('Same Version', log_var)


def delete_all_tables():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    box = messagebox.askyesno("Delete all Data?", "Delete all Data?")
    if box:
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            tables = cursor.execute("SELECT name FROM sqlite_schema WHERE type='table'").fetchall()
            static_tables = ['Bio_color', 'codex_entry', 'server', 'Bio_prediction', 'lan_db']
            for table in tables:
                x = (table[0])
                if x in static_tables:
                    continue
                statement = 'DROP TABLE IF EXISTS ' + str(x)
                cursor.execute(statement)
            connection.commit()
            create_tables()
            get_cloud_data()


def upd_server():
    # print('change state')
    # print(update_server.get())
    upd_srv = update_server.get()
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute("""UPDATE server set upload = ?""", (upd_srv,))
        connection.commit()


def upd_server2():
    # print('change state')
    # print(update_server.get())
    upd_srv = expedition_upload.get()
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute("""UPDATE server set exp_upload = ?""", (upd_srv,))
        connection.commit()


def get_theme():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS theme (theme STRING)''')
        connection.commit()
        item = cursor.execute("SELECT theme FROM theme").fetchall()
        if item:
            return item[0][0]
        else:
            return 'solar'


def set_theme(theme):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS theme (theme STRING)''')
        item = cursor.execute("SELECT theme FROM theme").fetchall()
        if item:
            cursor.execute("Update theme set theme = ?", (theme,))
        else:
            cursor.execute("INSERT into theme VALUES (?)", (theme,))
        connection.commit()


get_latest_version(1)


def main():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    global eddc_text_box, root, Tag, Monat, Jahr, tick_hour_label, tick_minute_label, eddc_modul, ody_mats, \
        vor_tick, nach_tick, filter_entry, tree, check_but, status, date_entry, root_open
    # label_tag, label_monat, label_jahr

    select = set_language_db('leer')
    if not select or select[0][0] == 'german' or select == 'leer':
        text = ['Tag', 'Monat', 'Jahr', 'Der letzte Tick war um:', 'vor dem Tick', 'nach dem Tick', 'Datum: ']
    else:
        text = ['Day', 'Month', 'Year', 'Last BGS TICK was at  ', 'before Tick', 'after Tick', 'Date: ']

    root = customtkinter.CTk()

    root.title('Elite Dangerous Data Collector')
    root_open = True
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS eddc_positions (
                            id INTEGER PRIMARY KEY,
                            x INTEGER,
                            y INTEGER
                        )''')
        cursor.execute("SELECT x, y FROM eddc_positions ORDER BY id DESC LIMIT 1")
        position = cursor.fetchone()
        if not position:
            cursor.execute("INSERT INTO eddc_positions (x, y) VALUES (130, 130)")
            cursor.execute("INSERT INTO eddc_positions (x, y) VALUES (130, 130)")
            cursor.execute("INSERT INTO eddc_positions (x, y) VALUES (130, 130)")
            cursor.execute("INSERT INTO eddc_positions (x, y) VALUES (130, 130)")
            connection.commit()

    load_position(root, 1, 415, 500)
    root.bind("<Configure>", lambda event: save_position(root, 1))

    def on_closing(treeview_loop=None):
        global root_open
        save_position(root, 1)
        # for thread in threading.enumerate():
        #     print(thread.name, ' MAIN')
        try:
            treeview_loop.wait()
        except:
            pass
        root.destroy()

        root_open = False
        logger('root destroy', 2)

    root.protocol("WM_DELETE_WINDOW", on_closing)

    img = resource_path("eddc.ico")
    root.iconbitmap(img)
    root.minsize(415, 500)
    root.maxsize(415, 1440)
    root.config(background='black')

    my_menu = Menu(root)
    root.config(menu=my_menu)
    # Menü Leiste
    file_menu = Menu(my_menu, tearoff=False)
    my_menu.add_cascade(label="Statistik", menu=file_menu)
    file_menu.add_command(label="BGS", command=lambda: menu('BGS'))
    file_menu.add_command(label="MATS", command=lambda: menu('MATS'))
    file_menu.add_command(label="Odyssey", command=lambda: menu('ody_mats'))
    file_menu.add_command(label="Combat Rank", command=lambda: menu('combat'))
    file_menu.add_command(label="Thargoids", command=lambda: menu('thargoid'))
    file_menu.add_command(label="Beitrag zum Krieg", command=lambda: menu('war'))
    file_menu.add_command(label="War Progress", command=lambda: menu('war_progress'))
    file_menu.bind_all("<Control-q>", lambda e: menu('CODEX'))
    file_menu.add_command(label="Exit", command=root.quit)

    exploration_menu = Menu(my_menu, tearoff=False)
    my_menu.add_cascade(label="Exploration", menu=exploration_menu)
    exploration_menu.add_command(label="Codex", command=lambda: menu('CODEX'), accelerator="Ctrl+q")
    exploration_menu.add_command(label="Tages Zusammenfassung", command=lambda: menu('summary'))
    exploration_menu.add_command(label="Boxel Analyse", command=lambda: menu('boxel'))
    exploration_menu.add_command(label="Kubus Analyse", command=lambda: menu('cube'))
    exploration_menu.add_command(label="Kompass", command=lambda: menu('compass'))
    exploration_menu.add_command(label="Exploration Challenge", command=exploration_challenge)
    # exploration_menu.add_command(label="test", command=test)
    # exploration_menu.add_command(label="Full Scan", command=full_scan)
    exploration_menu.add_command(label="Rescan Codex", command=rescan)

    settings_menu = Menu(my_menu, tearoff=False)
    settings_menu.add_cascade(label="Server Einrichtung", command=lambda: new_server_settings())
    # settings_menu.add_cascade(label="Dark Theme", command=lambda: set_theme('solar'))
    # settings_menu.add_cascade(label="Light Theme", command=lambda: set_theme('cosmo'))
    my_menu.add_cascade(label="Setting", menu=settings_menu)
    about_menu = Menu(my_menu, tearoff=False)
    my_menu.add_cascade(label="About", menu=about_menu)
    about_menu.add_command(label="Version Check", command=lambda: get_latest_version(0))
    about_menu.add_command(label="Delete all Data in DB", command=lambda: delete_all_tables())
    about_menu.add_command(label="Reset Window", command=lambda: menu('reset_pos'), accelerator="Ctrl+w")
    about_menu.bind_all("<Control-w>", lambda e: menu('reset_pos'))

    pic = resource_path("SNPX.png")
    try:
        font = ImageFont.truetype('arial.ttf', size=13)
    except IOError:
        font = ImageFont.load_default()

    eddc_img = Image.open(pic)
    d = ImageDraw.Draw(eddc_img)
    x = 270
    y = 72
    d.text((x, y), '© ', fill='#f07b05', font=font, stroke_width=1, stroke_fill='black')
    font = ImageFont.truetype('arial.ttf', size=11)
    x = 285
    y = 73
    current_year = datetime.now().year
    created_by = f'''{current_year} by MajorK'''
    d.text((x, y), created_by, fill='#f07b05', font=font)
    bg = customtkinter.CTkImage(dark_image=eddc_img, size=(380, 100))

    my_top_logo = customtkinter.CTkLabel(master=root, bg_color='black', image=bg, text='')
    my_top_logo.pack()

    top_frame = customtkinter.CTkFrame(master=root, fg_color='black', bg_color='black')
    top_frame.pack(padx=10)

    button_frame = customtkinter.CTkFrame(master=root, width=410, height=350, fg_color='black', bg_color='black')
    button_frame.pack()

    top_left_frame = customtkinter.CTkFrame(master=top_frame, width=250, height=100,
                                            fg_color='black', bg_color='black')
    top_left_frame.grid(column=0, row=0, pady=5, padx=10)

    top_left_frame_line_1 = customtkinter.CTkFrame(master=top_left_frame, width=250, height=50,
                                                   bg_color='black', fg_color='black')
    top_left_frame_line_1.grid(column=0, row=0, pady=5, sticky=W)

    top_left_frame_line_2 = customtkinter.CTkFrame(master=top_left_frame, width=250, height=50,
                                                   bg_color='black', fg_color='black')
    top_left_frame_line_2.grid(column=0, row=1, pady=5)

    date_label = customtkinter.CTkLabel(master=top_left_frame_line_1, text=text[6], text_color='white',
                                        font=("Helvetica", 16), justify=LEFT, bg_color='black')
    date_label.grid(column=0, row=0, padx=5)
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('my.DateEntry',
                    fieldbackground='black',
                    background='black',
                    foreground='white',
                    arrowcolor='white')
    date_entry = DateEntry(top_left_frame_line_1, selectmode='day', width=7,
                           style='my.DateEntry', font=("Helvetica", 12), date_pattern="dd.mm.yy")
    date_entry.grid(column=1, row=0, padx=5)

    last_tick_label = customtkinter.CTkLabel(master=top_left_frame_line_2, text=text[3], text_color='white',
                                             font=("Helvetica", 16), justify=LEFT)
    last_tick_label.grid(column=0, row=0, padx=5)

    last_t = last_tick()  # [t_year, t_month, t_day, t_hour, t_minute]

    t_hour, t_minute = last_t[3], last_t[4]

    tick_hour_label = customtkinter.CTkEntry(master=top_left_frame_line_2, width=30, font=("Helvetica", 14))
    tick_hour_label.insert(0, str(t_hour))
    tick_hour_label.grid(column=1, row=0, padx=2)
    label_colon = customtkinter.CTkLabel(master=top_left_frame_line_2, text_color='white',
                                         text=""":""", font=("Helvetica", 12), justify=LEFT)
    label_colon.grid(column=2, row=0, padx=2)
    tick_minute_label = customtkinter.CTkEntry(master=top_left_frame_line_2, width=30,
                                               font=("Helvetica", 14))
    tick_minute_label.insert(0, str(t_minute))
    tick_minute_label.grid(column=3, row=0, padx=2)

    top_right_frame = customtkinter.CTkFrame(master=top_frame, width=150, height=100,
                                             fg_color='black', bg_color='black')
    top_right_frame.grid(column=1, row=0)
    tick_var = IntVar()

    def get_content_4_cp():
        content = ''
        voucher_data = voucher.get_string(sortby="System")
        v = voucher_data.split('\n')
        if v[3] != '+---------+--------+---------+---------+':
            content = voucher_data + '\n' + '\n'
        ground_cz_data = ground_cz_table.get_string(sortby="System")
        g = ground_cz_data.split('\n')
        if g[3] != '+--------+---------+-------+-------+':
            content = content + ground_cz_data + '\n' + '\n'
        bgs_data = bgs.get_string(sortby="System")
        b = bgs_data.split('\n')
        if b[3] != '+--------+---------+-----------+':
            content = content + bgs_data
        result = cursor.execute("""SELECT * FROM server""").fetchall()
        if result:
            eddc_user = result[0][2]
        else:
            eddc_user = 'anonym'
        if eddc_user != 'anonym':
            content = ('```fix\n Daten von CMDR ' + eddc_user + '``` ```\n' + content + '\n```')
        else:
            content = ('```\n' + content + '\n```')
        return content

    def cp_to_discord():
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)

        if eddc_modul == 1:
            content = get_content_4_cp()
            if content.strip() != '':
                send_to_discord(content)
            else:
                pass

    def cp_to_clipboard():
        funktion = inspect.stack()[0][3]
        logger(funktion, 5)

        content = ''
        root.clipboard_clear()
        if eddc_modul == 1:
            content = get_content_4_cp()
            if content.strip() != '':
                root.clipboard_append(content)

        elif eddc_modul == 3:
            root.clipboard_append(mats_table.get_string(sortby="Materials"))
        elif eddc_modul == 2:
            root.clipboard_append(mats_table.get_string(sortby="Materials"))
        elif eddc_modul == 9:
            root.clipboard_append(tw_cargo_table.get_string())
            root.clipboard_append('\n')
            root.clipboard_append(tw_pass_table.get_string())
            root.clipboard_append('\n')
            root.clipboard_append(tw_rescue_table.get_string())
        root.update()

    def toggle_text():

        current_text = tick_but.cget("text")
        if current_text == "before Tick":
            tick_but.configure(text="after Tick")
            tick_var = 1
            tick_true()
        else:
            tick_but.configure(text="before Tick")
            tick_var = 0
            tick_false()
        logger(str(tick_var) + ' ' + str(check_auto_refresh), 2)

    global check_auto_refresh

    check_auto_refresh = IntVar()
    check_but = customtkinter.CTkCheckBox(master=top_right_frame, text="Auto refresh   ",
                                          variable=check_auto_refresh,
                                          offvalue=0,
                                          onvalue=1,
                                          command=threading_auto,
                                          text_color='white',
                                          font=('Helvetica', 14))

    check_but.grid(column=0, row=0, sticky=W, pady=5)

    tick_but = customtkinter.CTkButton(master=top_right_frame, text="after Tick", width=100,
                                       command=toggle_text, font=("Helvetica", 14))
    tick_but.grid(column=0, row=1, sticky=W, pady=5)

    my_folder = customtkinter.CTkFrame(master=button_frame, fg_color='black')
    my_folder.pack(fill=X, padx=20)
    myfolder_grid = customtkinter.CTkFrame(master=my_folder, fg_color='black')
    myfolder_grid.grid(sticky=W)

    label_filter = customtkinter.CTkLabel(master=myfolder_grid, text_color='white',
                                          text="Filter: ", font=("Helvetica", 14))
    label_filter.grid(column=0, row=0, padx=5)

    filter_entry = customtkinter.CTkEntry(master=myfolder_grid, font=('Helvetica', 14), width=300)
    filter_entry.insert(0, '')
    filter_entry.grid(column=1, row=0)

    folder = customtkinter.CTkEntry(master=my_folder, width=380, font=("Helvetica", 10))
    folder.insert(END, log_path)
    folder.grid(pady=5)

    # system = Text(root, height=10, width=10, bg='black', fg='white', font=("Helvetica", 10))
    eddc_text_box = customtkinter.CTkTextbox(root, height=10, width=10, font=("Helvetica", 12), wrap=WORD,
                                             text_color='white', fg_color='black', bg_color='black',
                                             border_color='#f07b05', border_width=1)
    # system.configure(state="disabled")
    eddc_text_box.pack(padx=10, expand=True, fill="both")

    bottom_grid = customtkinter.CTkFrame(master=root, bg_color='black', fg_color='black')
    bottom_grid.pack(pady=10)
    # my_style.configure('info.TButton', font=('Helvetica', 8), background='black')
    version_but = customtkinter.CTkButton(master=bottom_grid, text=version_number, command=logging, width=80,
                                          font=("Helvetica", 14), text_color='white', height=35)
    version_but.grid(column=0, row=0, sticky=W, padx=10)

    c2c_logo = customtkinter.CTkImage(dark_image=Image.open(resource_path("copy.png")), size=(25, 25))
    clipboard = customtkinter.CTkButton(master=bottom_grid, image=c2c_logo, text='', command=cp_to_clipboard,
                                        width=50, height=35)
    clipboard.grid(column=1, row=0, sticky=W, padx=10)

    discord_logo = customtkinter.CTkImage(dark_image=Image.open(resource_path("Discord_logo.png")), size=(28, 20))
    discord = customtkinter.CTkButton(master=bottom_grid, image=discord_logo, text='', command=cp_to_discord,
                                      width=50, height=35)
    discord.grid(column=2, row=0, sticky=W, padx=10)

    status = customtkinter.CTkLabel(master=bottom_grid, text='BGS Mode', width=60,
                                    text_color='white', font=("Helvetica", 14), )
    status.grid(column=3, row=0, sticky=W, padx=10)

    ok_but = customtkinter.CTkButton(master=bottom_grid, text='OK', command=threading_auto, width=50,
                                     text_color='white', height=35, font=("Helvetica", 14), )
    ok_but.grid(column=4, row=0, sticky=W, padx=10)

    def callback(event):
        funktion = inspect.stack()[0][3]
        logger(funktion, 1)
        logger(event, 1)
        threading_auto()

    root.bind('<Return>', callback)

    def set_language(language):
        if language == 1:
            data = ['Tag', 'Monat', 'Jahr', 'Der letzte TICK war um', 'vor dem Tick', 'nach dem Tick']
            set_language_db('german')
        # elif language == 2:
        else:
            data = ['Day', 'Month', 'Year', 'Last BGS TICK was at ', 'before Tick', 'after Tick']
            set_language_db('english')
        os.execl(sys.executable, sys.executable, *sys.argv)

    settings_menu.add_command(label="Sprache - Deutsch", command=lambda: set_language(1))
    settings_menu.add_command(label="Language - English", command=lambda: set_language(2))
    get_cmdr_names()
    root.mainloop()


db_version()
main()
