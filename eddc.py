# Created by MajorK https://github.com/SNP-MajorK/ED-DataCollector

import glob
import random
import re
import ssl
import threading
import time
import urllib.request
import webbrowser
from builtins import print
from datetime import date, timedelta, datetime
from pathlib import Path
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from urllib.parse import urlparse
from winreg import *

# import ttkbootstrap as tb
# from ttkbootstrap import Style

import plotly.express as px
import psycopg2
import requests
from PIL import ImageTk, Image, ImageDraw, ImageFont
from prettytable import PrettyTable
from requests import post

import snp_server
from bio_data import *

filter_name = ''
eddc_modul = 1
root = ''
tree = ''
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
version_number = '0.8.0.1'
current_version = ('Version ' + str(version_number))
global status
# data_old = StringVar()
fully = 0
bgs = PrettyTable(['System', 'Faction', 'Influence'])
voucher = PrettyTable(['Voucher', 'System', 'Faction', 'Credits'])
ground_cz_table = PrettyTable(['System', 'Faction', 'State', 'Count'])
mats_table = PrettyTable(['Materials', 'Count'])
tw_pass_table = PrettyTable(['System', 'Passengers'])
tw_rescue_table = PrettyTable(['System', 'Rescued'])
tw_cargo_table = PrettyTable(['System', 'Cargo'])
thargoid_table = PrettyTable(['Interceptor', 'Kills', 'Credits'])
boxel_table = PrettyTable(['Systemname', 'MainStar'])
codex_bio_table = PrettyTable(['ID', 'Datum', 'Zeit', 'CMDR', 'Bio', 'Farbe', 'Credits', 'System', 'Body', 'Sektor'])
codex_stars_table = PrettyTable(['ID', 'Datum', 'Zeit', 'CMDR', 'Codex Eintrag', 'Typ', '', 'System', ' ', 'Sektor'])
system_scanner_table = PrettyTable(['ID', 'Datum', 'Zeit', 'CMDR', 'Bio', 'Farbe',
                                    'Credits', 'System', 'Body', 'Sektor', 'Missing'])
statistics_table = PrettyTable(['ID', 'Datum', 'Zeit', 'Systemname', 'Body', 'Class', 'Mass', 'Age', 'Temp ', 'Region'])

eddc_user = 'anonym'

def get_time():
    return datetime.now()


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def logger(text, schwelle):
    if schwelle > 0:
       print(text)



database = resource_path("eddc.db")
global path
# path = ''
db_file = Path(database)

if not db_file.is_file():
    logger('create db', 1)
    create_codex_entry()
    create_DB_Bio_prediction()
    create_DB_Bio_color()


def create_tables():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()

        cursor.execute("DROP TABLE IF EXISTS odyssey")

        cursor.execute('''CREATE TABLE IF NOT EXISTS eddc_positions (
                            id INTEGER PRIMARY KEY,
                            x INTEGER,
                            y INTEGER
                        )''')

        cursor.execute("""CREATE TABLE IF NOT EXISTS thargoid_war_data 
                                (date_log date, 
                                time_log timestamp, 
                                system_address TEXT, 
                                system_name TEXT, 
                                current_state TEXT, 
                                war_progress REAL, 
                                upload INTEGER)""")

        cursor.execute("CREATE TABLE IF NOT EXISTS logfiles (Name TEXT, explorer INTEGER, "
                       "bgs INTEGER, CMDR TEXT, last_line INTEGER)")

        cursor.execute("""CREATE table IF NOT EXISTS flight_log 
                            (date_log date, time_log timestamp, SystemID INTEGER, 
                            SystemName TEXT, event TEXT, cmdr TEXT)""")

        cursor.execute("""CREATE table IF NOT EXISTS influence_db
                            (date_log date, time_log timestamp, voucher_type TEXT, SystemName TEXT, 
                            SystemAddress INTEGER, faction TEXT, amount INTEGER, upload INTEGER)""")

        cursor.execute("CREATE table IF NOT EXISTS odyssey (Name TEXT, Count INTEGER)")

        cursor.execute("""CREATE table IF NOT EXISTS lan_db (lang TEXT, switch INTEGER)""")

        cursor.execute("""CREATE table IF NOT EXISTS mission_failed 
                            (date_log date, time_log timestamp, mission_id INTEGER)""")

        cursor.execute("""CREATE table IF NOT EXISTS mission_accepted 
                            (date_log date, time_log timestamp, system TEXT, system_address INTEGER, faction TEXT, 
                            influence INTEGER, mission_id INTEGER)""")

        cursor.execute("""CREATE table IF NOT EXISTS server (
                            url TEXT, user TEXT, eddc_user TEXT, path TEXT, upload INTEGER)""")
        #
        item = cursor.execute("""SELECT * from server""").fetchall()
        if not item:
            # print(item)
            cursor.execute("""INSERT INTO SERVER (eddc_user, upload) VALUES ('anonym',0)""").fetchall()

        cursor.execute("""CREATE table IF NOT EXISTS ground_cz (date_log date, time_log timestamp,
                            system TEXT, settlement TEXT, faction TEXT, state TEXT)""")

        # cursor.execute("CREATE table IF NOT EXISTS stars (SystemID INTEGER, star_class TEXT)")

        cursor.execute("""CREATE table IF NOT EXISTS star_data 
                            (date_log date, time_log timestamp, body_id INTEGER, starsystem TEXT,
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

        cursor.execute("""CREATE table IF NOT EXISTS player_death (
                        date_log date,
                        time_log timestamp,
                        cmdr TEXT)
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

        # cursor.execute("""CREATE table IF NOT EXISTS codex_entry (
        #                 data TEXT,
        #                 worth INTEGER,
        #                 type INTEGER,
        #                 region TEXT)
        #                 """)

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

        cursor.execute("""CREATE table IF NOT EXISTS planet_infos (date_log date, time_log timestamp,
                        SystemID INTEGER, SystemName TEXT, Main_Star TEXT, Local_Stars TEXT,
                        BodyName TEXT, BodyID INTEGER, DistanceToMainStar TEXT, Tidal_lock Text, Terraform_state TEXT,
                        PlanetType TEXT, Atmosphere TEXT, Gravity TEXT, Temperature TEXT, Pressure TEXT,
                        Landable TEXT, volcanism TEXT, sulphur_concentration TEXT, Rings INTEGER, Mass REAL, Radius REAL, 
                        SemiMajorAxis REAL, Eccentricity REAL, OrbitalInclination REAL, Periapsis REAL, 
                        OrbitalPeriod REAL, AscendingNode REAL, MeanAnomaly REAL, RotationPeriod REAL, 
                        AxialTilt REAL, Discovered TEXT, Mapped TEXT, Materials TEXT)""")

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
                        url TEXT, user TEXT, eddc_user TEXT, path TEXT, upload INTEGER)""")

    cursor.execute("""SELECT * FROM server""")
    result = cursor.fetchall()
    if result != []:
        webhook_url = result[0][0]
        web_hock_user = result[0][1]
        eddc_user = result[0][2]
        path = result[0][3]

if not path:
    # Set Program Path Data to random used Windows temp folder.
    with OpenKey(HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders") as key:
        value = QueryValueEx(key, '{4C5C32FF-BB9D-43B0-B5B4-2D72E54EAAA4}')
    # path = value[0] + '\\Frontier Developments\\Test'
    # path = value[0] + '\\Frontier Developments\\Franky'
    # path = value[0] + '\\Frontier Developments\\Bernd'
    path = value[0] + '\\Frontier Developments\\Elite Dangerous\\'


# print(path)

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


def server_settings():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    global path
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute("""SELECT * FROM server""")
        result = cursor.fetchall()
        # print(result)
        if result != []:
            # print(result[0][1])
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
            if result[0][3] != ('' or None):
                path_new = result[0][3]
                if path_new:
                    path = path_new
            # print(result[0][4])
            if int(result[0][4]) == 1 or int(result[0][4]) == 0:
                # print('reset_pos')
                up_server = int(result[0][4])
            else:
                up_server = IntVar()
        else:
            web_hock_user = ''
            webhook_url = ''
            eddc_user = 'anonym'
            up_server = IntVar()

    server_settings = Toplevel(root)
    server_settings.title('Server Einrichtung')
    server_settings.geometry("400x200")
    server_settings.minsize(400, 180)
    server_settings.maxsize(1200, 180)
    server_settings.after(1, lambda: server_settings.focus_force())
    try:
        img = resource_path("eddc.ico")
        server_settings.iconbitmap(img)
    except TclError:
        logger('Icon not found', 1)

    top = Label(server_settings, bg='grey')
    top.pack(fill=X)

    top_blank = Label(top, bg='black')
    top_blank.pack(fill=X)
    headline = Label(top_blank, text='Server Einrichtung', bg='black', fg='white', font=("Helvetica", 11))
    headline.pack()

    global update_server
    update_server = IntVar()

    upload_but = Checkbutton(top_blank, text="BGS Upload  ",
                             variable=update_server,
                             bg='black',
                             fg='white',
                             selectcolor='black',
                             activebackground='black',
                             activeforeground='white',
                             command=upd_server,
                             font=("Helvetica", 10))
    upload_but.pack()

    if up_server == 0:
        upload_but.deselect()
    else:
        upload_but.select()

    name_frame = Frame(top_blank, bg='black')
    name_frame.pack(fill=X)

    name_label = Label(name_frame, text='Name : ', bg='black', fg='white', font=("Helvetica", 11))
    name_label.grid(column=0, row=0, sticky=W)

    name_entry = Entry(name_frame, width=20, font=("Helvetica", 11))
    name_entry.insert(0, eddc_user)
    name_entry.grid(column=1, row=0, sticky=W)

    discord_user = Label(name_frame, text='Discord Bot Name : ', bg='black', fg='white', font=("Helvetica", 11))
    discord_user.grid(column=0, row=1, sticky=W)
    discord_user_entry = Entry(name_frame, width=26, font=("Helvetica", 11))
    discord_user_entry.insert(0, web_hock_user)
    discord_user_entry.grid(column=1, row=1, sticky=W)

    discord_label = Label(name_frame, text='Discord Webhook URL : ', bg='black', fg='white', font=("Helvetica", 11))
    discord_label.grid(column=0, row=2, sticky=W)
    discord_entry = Entry(name_frame, width=26, font=("Helvetica", 11))
    discord_entry.insert(0, webhook_url)
    discord_entry.grid(column=1, row=2, sticky=W)

    path_label = Label(name_frame, text='Journal Log Pfad : ', bg='black', fg='white', font=("Helvetica", 11))
    path_label.grid(column=0, row=3, sticky=W)
    path_entry = Entry(name_frame, width=26, font=("Helvetica", 11))
    path_entry.insert(0, path)
    path_entry.grid(column=1, row=3, sticky=W)

    def save(url, user, eddc_user, path):
        update_serv = update_server.get()
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
                    cursor.execute("INSERT INTO server VALUES (?, ?, ?, ?, ?)",
                                   (url, user, eddc_user, path, update_serv))
                else:
                    cursor.execute("drop table server")
                    cursor.execute("""CREATE table IF NOT EXISTS server (
                                                url TEXT, user TEXT, eddc_user TEXT, path TEXT, upload INTEGER)""")
                    cursor.execute("INSERT INTO server VALUES (?, ?, ?, ?, ?)",
                                   (url, user, eddc_user, path, update_serv))
                connection.commit()
                server_settings.destroy()

    save_but = Button(top_blank,
                      text='Speichern',
                      activebackground='#000050',
                      activeforeground='white',
                      bg='black',
                      fg='white',
                      command=lambda: save(discord_entry.get(), discord_user_entry.get(),
                                           name_entry.get(), path_entry.get()),
                      font=("Helvetica", 10))
    save_but.pack()


def last_tick():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    try:
        response = requests.get("https://elitebgs.app/api/ebgs/v5/ticks", timeout=1)
        todos = json.loads(response.text)
    except:
        logger(('Tick Error'),1)
        tick_data = ('[{"_id":"627fe6d6de3f1142b60d6dcd",'
                     '"time":"2022-05-14T16:56:36.000Z",'
                     '"updated_at":"2022-05-14T17:28:54.588Z",'
                     '"__v":0}]')
        todos = json.loads(tick_data)
        messagebox.showwarning("TICK failed", "No Internet Connection")
    for d in todos:
        lt_date = d['time']
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
        if result != []:
            eddc_user = result[0][2]
            if result[0][3] == 0:
                global path
                path = result[0][3]

    update_eleven = datetime(2022, 3, 14)
    tag2 = Tag.get()
    if len(tag2) < 2:
        return
    if len(tag2) > 2:
        tag2 = tag2[0:2]
    tag2 = str(int(tag2)).zfill(2)
    monat2 = Monat.get()
    jahr2 = Jahr.get()
    # print('Hallo ', tag2, monat2, jahr2)

    if var == 0:  # Logs von dem Tag X
        search_date = datetime(int("20" + jahr2), int(monat2), int(tag2))
        if search_date > update_eleven:
            journal_date = ("20" + str(jahr2) + "-" + str(monat2) + "-" + str(tag2) + "T")
            files = glob.glob(path + "\\Journal." + journal_date + "*.log")
            return files
        else:
            journal_date = str(jahr2 + monat2 + tag2)
            filenames = glob.glob(path + "\Journal." + journal_date + "*.log")
            return filenames

    elif var == 1:  # Alle Logfiles
        filenames = glob.glob(path + "\\Journal.*.log")
        fils = (glob.glob(path + "\\Journal.202*.log"))
        for i in fils:
            filenames.remove(i)
        for i in fils:
            filenames.append(i)
        return filenames

    elif var == 2:  # Logs von gestern, heute & ggf. morgen
        yesterday = str(datetime.now() - timedelta(days=1))[0:10]
        today = str(datetime.now())[0:10]
        tomorrow = str(datetime.now() + timedelta(days=1))[0:10]
        filenames = glob.glob(path + "\\Journal." + yesterday + "*.log")
        files_tod = glob.glob(path + "\\Journal." + today + "*.log")
        files_tom = glob.glob(path + "\\Journal." + tomorrow + "*.log")
        for i in files_tod:
            filenames.append(i)
        for i in files_tom:
            filenames.append(i)
        return filenames

    elif var == 3:  # Lese die Logs von dem Tag X ein, und wenn vorhanden welche von den vortagen.
        tag2 = Tag.get()
        journal_date = ("20" + str(jahr2) + "-" + str(monat2) + "-" + str(tag2) + "T")
        files = glob.glob(path + "\\Journal." + journal_date + "*.log")
        filenames = glob.glob(path + "\\Journal.*.log")
        lauf = 1
        while files == []:
            journal_date = ("20" + str(jahr2) + "-" + str(monat2) + "-" + str(tag2) + "T")
            files = glob.glob(path + "\\Journal." + journal_date + "*.log")
            lauf += 1
            if lauf == 5:
                break
        if files == []:
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
        return (data)

    elif var == 4:
        today = str(datetime.now())[0:10]
        files_tod = glob.glob(path + "\\Journal." + today + "*.log")
        return files_tod


def tail_file(file):
    funktion = inspect.stack()[0][3]
    global line_nr
    line_in_db = check_logfile_in_DB(file, 'line', '')
    logger((funktion, file, str(line_in_db)), log_var)
    is_file = os.path.isfile(file)
    if not is_file:
        messagebox.showwarning("Check failed", "File not found" + file)
        return
    with open(file, 'r', encoding='UTF8') as datei:
        total_lines = sum(1 for line in datei)
        if total_lines == (line_in_db+1):
            return
    with open(file, 'r', encoding='UTF8') as datei:
        cmdr = read_cmdr(file)
        check_cmdr(file, cmdr)
        if not cmdr or cmdr == 'UNKNOWN' :
            # check_logfile_in_DB(file, 'explorer', 'set')
            print('No CMDR ' + file)
            return
        for line_nr, zeile in enumerate(datei):
            if line_nr >= line_in_db: # work
                data = read_json(zeile)
                # print(data.get('timestamp'), data.get('event'))
                if data == ['']:
                    logger((funktion + 'ignore Data'),1)
                    return
                event = data.get('event')
                match event:
                    case 'Location':
                        set_system(data, cmdr)
                    case 'Scan':
                        if data.get('StarType'):
                            get_all_stars(data)
                        if data.get('ScanType') and not data.get('StarType'):
                            get_planet_info(data)
                    case 'ScanBaryCentre':
                        get_bary(data)
                    case 'FSDJump':
                        set_main_star(data)
                        set_system(data, cmdr)
                    case 'StartJump':
                        if data.get('JumpType') == "Hyperspace":
                            get_star_info(data)
                    case 'ScanOrganic':
                        get_info_for_bio_scan(data, file)
                        read_bio_data(data, file)
                    case 'FSSBodySignals':
                        get_info_scan_planets(data)
                    case 'SAASignalsFound':
                        get_info_scan_planets(data)
                    case 'CodexEntry':
                        read_log_codex(data, file)
                    case 'Shutdown':
                        check_logfile_in_DB(file, 'explorer', 'set')
        try:
            if line_nr > line_in_db:
                check_logfile_in_DB(file, 'line', line_nr)
        except:
            line_nr = 0
            check_logfile_in_DB(file, 'line', 0)


# global data_old
data_old = None


def count_lines_efficiently(filename):
    line_count = 0
    with open(filename, 'r') as file:
        for line in file:
            line_count += 1
    return line_count


def start_read_logs():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    global data_old
    files = file_names(1)

    if len(files) > 0:
        last = files[len(files) - 1]
    else:
        return

    data = None
    if check_logfile_in_DB(last, 'explorer', 'check') != 1:
        check_logfile_in_DB(last, '', 'insert')
        tail_file(last)
    else:
        if data_old and data_old != ' ' and check_last(last) == 1 :
            print('USE OLD DATA')
            # print(data_old)
            return data_old

    current_system = get_last_system_in_DB()
    logger((funktion, str(current_system[0])), log_var)
    if current_system == None:
        return

    data = get_data_from_DB(last, current_system)
    # print(data)

    logger(last, log_var)

    if data != None:
        data_old = data
    if data == None and data_old != None:
        data = data_old

    if not isinstance(data, str) and data != None and current_system[0] != None:
        if current_system[0] not in data[0][0]:
            data = None
    else:  # Wenn Data ein string ist, setze es auf None
        data = [(current_system[0], 'No', 'Data', '',
                 'System', 'without', 'life', "", "", "")]
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


def star_systems_db(filenames):  # Liest alle SystemIDs und Systemnamen im Journal aus um sie in die DB zu speichern
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    for filename in filenames:
        with open(filename, 'r', encoding='UTF8') as datei:
            for zeile in datei:
                data = read_json(zeile)
                if data.get('event') == 'Scan':
                    get_info_for_get_body_name(data)  # star_map
                if data.get('event') == 'StartJump' and data.get('JumpType') == "Hyperspace":
                    # print(data)
                    get_info_for_get_body_name(data)  # star_map


def print_influence_db(filter_b):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    data = []
    data_list = []
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        se = tick_select()
        filter_b = '%' + filter_b + '%'
        sql = 'SELECT DISTINCT(SystemName), faction FROM influence_db where ' \
              'voucher_type = "influence" and ' + se + ' order by 1'
        new_data = cursor.execute(sql).fetchall()
        for i in new_data:
            sql = 'SELECT SUM(amount) FROM influence_db where voucher_type = "influence" and SystemName = "' + str(i[0]) + \
                  '" and faction = "' + str(i[1]) + '" and ' + se
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
            filter = cursor.execute("""SELECT * FROM tmp_filter_inf WHERE SystemName LIKE ? OR 
                                        Faction LIKE ? GROUP BY 1, 2, 3""",
                                    (filter_b, filter_b)).fetchall()
            data = filter
        else:
            data = data_list
    return data


def einfluss_auslesen(journal_file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    # tick_hour = tick_hour_label.get()
    # tick_minute = tick_minute_label.get()
    # tick_time[3] = tick_hour[0:2]
    # tick_time[4] = tick_minute[0:2]
    t1 = get_time()
    line = 0
    with open(journal_file, 'r', encoding='UTF8') as datei:
        for zeile in datei:
            line += 1
            data = read_json(zeile)
            event = data.get('event')
            match event:
                case 'Docked':
                    get_info_for_get_body_name(data)  # star_map
                case 'Location':
                    get_info_for_get_body_name(
                        data)  # star_map
                case 'StartJump':
                    if data.get('JumpType') == "Hyperspace":
                        get_info_for_get_body_name(data)  # star_map
                case "MissionAccepted":
                    system_data = find_last_docked(journal_file, line)
                    system = system_data[1]
                    system_address = system_data[2]
                    mission_data(data, system, system_address)
                case "MissionFailed":
                    mission_failed(data)
                case 'MissionCompleted':
                    if check_logfile_in_DB(journal_file, 'bgs', 'check') == 0:
                        mission_completed(data)
                case 'Shutdown':
                    check_logfile_in_DB(journal_file, 'bgs', 'set')
    t2 = get_time()
    # print('read all ' + str(journal_file) + '    ' + str(timedelta.total_seconds(t2 - t1)))

    # =========================================== End of dateien_einlesen()


def get_data_mission_acceppted(mission_id):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    mission_id = int(mission_id)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select = cursor.execute("""SELECT * from mission_accepted where mission_id = ?""", (mission_id,)).fetchall()
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
                    new_data = get_data_mission_acceppted(mission_id)
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


#

def mission_failed(data):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    timestamp = data.get('timestamp')
    log_time = (log_date(timestamp))
    date_log = (log_time[0] + "-" + log_time[1] + "-" + log_time[2])
    time_log = (log_time[3] + ":" + log_time[4] + ":" + log_time[5])
    faction = data.get('Faction')
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
            sel = "SELECT system_address, faction, influence from mission_accepted where mission_id = ? "
            select = cursor.execute(sel, (i[0],)).fetchall()
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
    tag2 = Tag.get()
    monat2 = Monat.get()
    jahr2 = Jahr.get()
    jahr2 = '20' + jahr2
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
                war_progress  = i[5]

                with psycopg2.connect(dbname=snp_server.db_name, user=snp_server.db_user, password=snp_server.db_pass,
                                      host=snp_server.db_host, port=5432) as psql_conn:
                    psql = psql_conn.cursor()
                    p_select = "SELECT * FROM thargoid_war where " \
                               "datetime = \'" + str(timestamp) + "\' and SystemAddress = '" + str(system_address) \
                               +"' and " "SystemName = '" + system_name + "'"
                    psql.execute(p_select)
                    result = psql.fetchall()
                    if result == []:
                        insert = 'INSERT INTO thargoid_war (datetime, SystemAddress, SystemName, current_state, ' \
                                 'war_progress) VALUES (timestamp \'' + str(timestamp) + '\', ' + str(system_address) \
                                 + ' , \'' + system_name + '\' , \'' + current_state +'\' , '  + str(war_progress) + ')'
                        psql.execute(insert)
                        psql_conn.commit()

                update = "UPDATE thargoid_war_data SET upload = 1 where date_log = ? and time_log = ? " \
                         "and system_address = ? and system_name = ? and current_state = ? and war_progress = ?"
                cursor.execute(update, (date_log, time_log, system_address, system_name,current_state, war_progress))
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
        next_success_state = war_data.get('NextStateSuccess')
        next_fail_state = war_data.get('NextStateFailure')
        success_state = war_data.get('SuccessStateReached')
        war_progress = war_data.get('WarProgress')
        if war_progress == 0:
            return
        war_progress = war_progress * 100
        insert_war_data(date_log, time_log, system_address, system_name, current_state, war_progress)
        return (date_log, time_log, system_address, system_name, current_state, war_progress)


def update_thargoid_war():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    result = []
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
                 + str(time_log) + "' and system_address = "  + str(system_address) + " and system_name = '" \
                 + str(system_name) +"' and war_progress = " + str(war_progress)
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
        oneweek = str(datetime.now() - timedelta(days=7))[0:10]
        today = str(datetime.now())[0:10]
        sql = "SELECT system_name, date_log, time_log, war_progress  FROM thargoid_war_data where date_log BETWEEN '" \
              + oneweek + "' and '"+ today +"' ORDER by 2 DESC, 3 DESC"
        cursor.execute(sql)
        result = cursor.fetchall()
        systems = []
        dates = []
        progress = []
        system.insert(END, (('Folgende Systeme sind in der Datenbank vorhanden: \n\n')))
        for i in result:
            if i[0] not in systems:
                systems.append(i[0])
                wp_date = str(i[1]).split('-')
                new_date = wp_date[2] + '.' + wp_date[1] + '.' + wp_date[0]
                dates.append(new_date)
                prog = str(i[3]).split('.')
                progress.append(prog[0])
        for count, s in enumerate(systems):
            system.insert(END, ((str(systems[count]) + '\t\t\t\t '+ str(dates[count]) + '\t\t '
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
        fig = px.line(x = timestamp, y = war_progress, title = title, labels = {'x': 'Datum', 'y':'War Progress'},
                      markers = True)
        fig.show()
    else:
        system.insert(END, (('Das System ' + b_filter + ' wurde nicht in Datenbank gefunden: \n')))
        system.insert(END, (('\n')))


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
        faction = ''
        star_system = ''
        system_address = ''
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
                select = 'select * from influence_db where datetime = \'' + str(timestamp) + '\' ' \
                        'and name = \'' + eddc_user + '\' ' \
                        'and voucher_type = \'' + voucher_type + '\' ' \
                        'and systemname = \'' + system_name + '\' ' \
                        'and systemaddress = ' + str(system_address) + \
                        ' and faction = \'' + faction + '\' ' \
                        'and amount = ' + str(amount) + ';'
                psql.execute(select)
                result = psql.fetchall()
                if result == []:
                    insert = 'INSERT INTO influence_db (datetime, name, voucher_type, systemname, systemaddress, faction, amount) VALUES ' \
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

    tag = Tag.get()
    monat2 = Monat.get()
    jahr2 = '20' + Jahr.get()

    h_tick = tick_hour_label.get()
    m_tick = tick_minute_label.get()
    tick_time = h_tick + ':' + m_tick
    date = jahr2 + '-' + monat2 + '-' + tag
    search_date = datetime(int(jahr2), int(monat2), int(tag), int(h_tick), int(m_tick))

    if tick:  # nach dem Tick
        tommorow = str(search_date + timedelta(days=1))[0:10]
        select_tick = '((date_log = "' + date + '" and time_log > "' + tick_time + '") or ' \
                                                                                   '(date_log = "' + tommorow + '" and time_log < "' + tick_time + '"))'
    else:  # vor dem Tick
        yesterday = str(search_date - timedelta(days=1))[0:10]
        select_tick = '((date_log = "' + date + '" and time_log < "' + tick_time + '") or ' \
                                                                                   '( date_log = "' + yesterday + '" and time_log > "' + tick_time + '"))'
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


def combat_window(data):
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
        count_combo.current(count)
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
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
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


def auto_refresh():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    if eddc_modul != 4:
        while check_auto_refresh.get() != 0:
            logger('while auto_refresh', log_var)
            if check_auto_refresh.get() != 0:
                logger(check_auto_refresh.get(), log_var)
                #  'Autorefresh gestartet '
                for i in range(0, 30):
                    time.sleep(1)
                    system.insert(INSERT, '.')
                if check_auto_refresh.get() != 0:
                    refreshing()


def refreshing():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    t1 = get_time()

    system.delete(1.0, END)
    system.insert(INSERT, 'Auswertung läuft ')
    time.sleep(0.2)
    tables = [bgs, voucher, mats_table, tw_pass_table, tw_rescue_table, tw_cargo_table,
              thargoid_table, boxel_table, codex_bio_table, codex_stars_table, system_scanner_table]
    for table in tables:
        try:
            table.clear_rows()
        except AttributeError:
            logger(('NoData in ' + str(table)), 2)
    if eddc_modul != 4:
        # auswertung(eddc_modul)
        def start_auswertung():
            auswertung(eddc_modul)

        def waiting():
            while thread1.is_alive():
                if not thread1.is_alive():
                    break
                else:
                    time.sleep(0.5)
                    system.insert(INSERT, '.')

        thread1 = threading.Thread(target=start_auswertung)
        thread2 = threading.Thread(target=waiting)
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
        t2 = get_time()
        # print('refreshing   ' + str(timedelta.total_seconds(t2 - t1)))


def threading_auto():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    global start
    start_auto = threading.Thread(target=auto_refresh)
    start_refresh = threading.Thread(target=refreshing)
    var_code = [7, 8, 4]
    if eddc_modul == 4:
        logger('AUTO CODEX = 1 ', 5)
        treeview_codex()
        # for record in tree.get_children():
        #     tree.delete(record)
        # auswertung(eddc_modul)

    elif check_auto_refresh.get() != 0 and eddc_modul not in var_code:
        start_auto.start()
    else:
        if not start_auto.is_alive():
            start_refresh.start()
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
    with open(journal_file, 'r', encoding='UTF8') as datei:
        for zeile in datei:
            search_string = 'MaterialCollected'
            if (zeile.find(search_string)) > -1:
                data = read_json(zeile)
                state = 1
                extract_engi_stuff(data, state)


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
                           (date_log, time_log, icd_cmdr, codex_name, codex_entry, category, icd_system, region))


def read_json(zeile):
    try:
        if zeile == '\n':
            # logger(('exit - leerzeile'), 2)
            zeile = '{"timestamp": "2022-11-20T18:49:07Z", "event": "Friends", "Status": "Online"}'
        data = json.loads(zeile)
        return data
    except ValueError:
        logger(('read_json', zeile), log_var)
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
    rlc_system = data['System']
    rbd_log_time = (log_date(data.get('timestamp')))
    date_log = (rbd_log_time[0] + "-" + rbd_log_time[1] + "-" + rbd_log_time[2])
    time_log = (rbd_log_time[3] + ":" + rbd_log_time[4] + ":" + rbd_log_time[5])

    if 'Thargoid' in codex_entry:
        codex_name = 'Xenological'
        category = '$Codex_SubCategory_Goid'

    if 'Terrestrials' in category:
        # print('IF ' + codex_entry)
        terra_state = ['Non Terraformable', 'Terraformable']
        codex_name = 'Terrestrials'
        codex_entry = serach_body(data, journal_file)
        if not codex_entry:
            name = (data.get('Name'))
            match name:
                case '$Codex_Ent_Standard_Rocky_No_Atmos_Name;':
                    codex_entry = 'Rocky body - ' + terra_state[0]
                case '$Codex_Ent_Standard_Ter_Rocky_Name;':
                    codex_entry = 'Rocky body - ' + terra_state[0]

                case '$Codex_Ent_Standard_Ter_Rocky_Ice_Name;':
                    codex_entry = 'Rocky ice body - ' + terra_state[0]
                case '$Codex_Ent_Standard_Rocky_Ice_No_Atmos_Name;':
                    codex_entry = 'Rocky ice body - ' + terra_state[0]

                case '$Codex_Ent_Standard_Ice_No_Atmos_Name;':
                    codex_entry = 'Icy body - ' + terra_state[0]

                case '$Codex_Ent_Standard_Ter_Ice_Name;':
                    codex_entry = 'Icy body - ' + terra_state[0]

                case 'Name":"$Codex_Ent_Standard_Ter_High_Metal_Content_Name;':
                    codex_entry = 'High metal content body - ' + terra_state[0]
                case 'Name":"$Codex_Ent_Standard_High_Metal_Content_No_Atmos_Name;':
                    codex_entry = 'High metal content body - ' + terra_state[0]
                case '$Codex_Ent_TRF_Ter_High_Metal_Content_Name;':
                    codex_entry = 'High metal content body - ' + terra_state[1]
                case '$Codex_Ent_TRF_High_Metal_Content_No_Atmos_Name;':
                    codex_entry = 'High metal content body - ' + terra_state[1]

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
        codex_name = 'Stars'

    if 'Organic_Structures' in category:
        codex_entry = (data['Name_Localised'])
        codex_name = "Biological Discovery"
        not_bios = ['Albulum Gourd Mollusc', 'Crystalline Shards', 'Bark Mounds', 'Albidum Peduncle Tree',
                    'Purpureum Metallic Crystals', 'Prasinum Ice Crystals', 'Flavum Metallic Crystals',
                    'Lindigoticum Ice Crystals', 'Rubeum Ice Crystals', 'Rubeum Metallic Crystals',
                    'Prasinum Metallic Crystals', 'Prasinum Bioluminescent Anemone',
                    'Roseum Bioluminescent Anemone', 'Biolumineszente Prasinum-Anemone',
                    'Solid Mineral Spheres', 'Lindigoticum Silicate Crystals',
                    'Cobalteum Rhizome Pod', 'Albidum Silicate Crystals',
                    'Roseum Ice Crystals', 'Albidum Ice Crystals', 'Prasinum Sinuous Tubers', 'Roseum Brain Tree']
        if codex_entry in not_bios:
            logtime = data.get('timestamp')
            insert_codex_db(logtime, codex_name, rlc_cmdr, codex_entry, category, region, rlc_system)
        else:
            species = str(data['Name_Localised'])
            tmp = species.split()
            if len(tmp) > 3:
                codex_bio = str(tmp[0]) + ' ' + str(tmp[1])
                bio_color = str(tmp[3])
            else:
                codex_bio = data.get('Name_Localised')
                bio_color = ''
            system_address = data.get('SystemAddress')
            body_id = data.get('BodyID')
            bodys = get_body_from_sc(logtime, system_address, journal_file)
            body = bodys[0]
            if not body and not body_id:
                body_id = find_body_data(journal_file, date_log, time_log)
            if not body and body_id:
                body = get_body(system_address, body_id)
            t3 = get_time()
            if not body:
                logger('No Body founbd!', 1)
                logger((date_log, time_log, rlc_cmdr, codex_bio, bio_color, rlc_system, body, region),1)
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
    with open(journal_file, 'r', encoding='UTF8') as datei:
        for zeile in datei:
            data = read_json(zeile)
            event = data.get('event')
            match event:
                case 'Location':
                    get_info_for_get_body_name(data)
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
    if biodata == None or system_address_bio == 0:
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
        for zeile in datei:
            search_string = '"event":"Commander"'
            if zeile.find(search_string) > -1:
                data = read_json(zeile)
                # data = json.loads(zeile)
                cc_cmdr = data.get('Name', 'UNKNOWN')
                return cc_cmdr
        # print(zeile)
        zeilen = datei.readlines()
        if len(zeilen) == 0:
            print(file)
            return 'UNKNOWN'
        data = read_json(zeile)
        if data.get('event') == 'Shutdown':
            return 'UNKNOWN'
        # return 'UNKNOWN'


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
        select = cursor.execute("""SELECT Bodyname FROM planet_infos WHERE 
                                SystemID = ? and BodyID = ? """, (system_address, body_id)).fetchall()
        # print(str(system_adrress), str(body_id), select)
        if select:
            return select[0][0]
        else:
            star_select = cursor.execute("""SELECT starsystem, body_name FROM star_data WHERE 
                                                        System_address = ? and body_id = ? """,
                                        (system_address, body_id)).fetchall()
            if star_select:
                system_name = star_select[0][0]
                body_name = star_select[0][1]
                body_name = body_name.replace(system_name, '')
                return body_name


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
            bio = '%' + i[3] + '%'
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

        if select == []:
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
        select = cursor.execute("""SELECT * FROM planet_infos where SystemName = ? and landable = 1 and 
                                    Atmosphere like '%atmosphere%' """, (current_system[0],)).fetchall()
        cmdr = cursor.execute("Select CMDR from logfiles where Name = ?", (file,)).fetchone()
    if not cmdr:
        cmdr = check_cmdr(file, '')
    if select == []:
        return ' '
    new = []
    active_body = activ_planet_scan(file)
    first = []
    for i in select:  # Nun werden nur die Körper mit Odyssey Bio Signalen herrausgefiltert
        body = i[3] + i[6]
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            select2 = cursor.execute("""SELECT * FROM planet_bio_info where body = ? """, (body,)).fetchall()
            # select2 = cursor.execute("""SELECT * FROM planet_bio_info where body = ? """, ('Aucoks XK-M d8-11 5 b',)).fetchall()
        if select2 != []:
            if body == active_body:
                first.append(i)
            else:
                new.append(i)
    for a in new:  # Damit der zuletzt betretene oder gescannte Trabant im Fokus steht.
        first.append(a)
    data = get_biodata_from_planet(cmdr[0], first)
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


def get_biodata_from_planet(cmdr, select):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    data_2 = []
    if select == []:
        logger((funktion, 'select leer'), 2)
        return ''

    address = (select[0][2])
    region = (findRegionForBoxel(address)['region'][1])

    for i in select:
        system_address = int(i[2])
        system_name = str(i[3])
        body = str(i[6])
        body_name = str(i[3]) + str(i[6])
        main_star_class = []
        # print(i[4])
        if i[4] == None:
            logger('Hoppla',1)
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

        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            b_count = cursor.execute("SELECT count FROM planet_bio_info where body = ?", (body_name,)).fetchall()
        if b_count:
            bio_count = b_count[0][0]
        else:
            return

        bio_names = []
        bio = []
        bcd = []
        iob = ''

        if main_star_class == []:
            with sqlite3.connect(database) as connection:
                cursor = connection.cursor()
                main_sql = f'''SELECT startype FROM star_data where 
                                system_address = {system_address} and main = 1'''
                main_star = cursor.execute(main_sql).fetchone()

        potential_bios = []
        for star_class in main_star_class:
            if star_class != '':
                temp = select_prediction_db(star_class, planet_type, body_atmos,
                                            body_gravity, body_temp, body_pressure, volcanism, sulphur_concentration)
                for t in temp:
                    for bio_a in t:
                        potential_bios.append(bio_a)
        new_list = []
        potential_bios = list(dict.fromkeys(potential_bios))

        if main_star_class[1] != None:
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
            data_2.append((body_name, distance, bio_count, all_stars, atmo, '', '', '', region,''))
        # for i in missing_in_region:
        #     missing_bio.append(i[3])
        mark_missing = 0

        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            select_bios_on_body = cursor.execute("""SELECT * from bio_info_on_planet where body = ? 
            and bio_scan_count > 0 Order by genus""", (body_name,)).fetchall()
            select_complete_bios_on_body = cursor.execute("""SELECT COUNT(species) from bio_info_on_planet 
                    where body = ? and bio_scan_count = 3""", (body_name,)).fetchall()


        species_all = []
        genus_all = []
        for i in select_bios_on_body:
            scan = ' '
            bio_2 = i[1] + ' ' + i[2]
            gcc = get_codex_color(bio_2, system_name, body)
            if gcc[0] == 'Unknown':
                cod = get_color_or_distance(bio_2, main_star_class[0], material)
                if cod:
                    gcc = cod[1][0][0], gcc[1]
                else:
                    continue
            if i[3] == 1:
                scan = 'Scan in Progress 1 / 3'
            if i[3] == 2:
                scan = 'Scan in Progress 2 / 3'
            if i[3] > 2:
                scan = 'Scan completed   3 / 3'
            if gcc:
                gcod_color = gcc[0]
                gcod_bio_distance = gcc[1]
                worth = worth_it([(0, 0, 0, i[2])])
                worth = ((f'{worth:,}').replace(',', '.'))
                # worth = worth_it(i[2])
                data_2.append(('', '', '', i[1], i[2], worth, gcod_color, gcod_bio_distance, scan, 0))
                species_all.append(str(i[2]))
                genus_all.append(str(i[1]))

        if int(b_count[0][0]) != int(select_complete_bios_on_body[0][0]):
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
                if (bio_scan_count) == None:
                    logger(('bio_scan_count = 0'), 1)
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
                fdg = check_genus(body_name, genus) # Wenn der Planet mit dem DOS gescannt wurde
                if fdg != None:
                    identified_on_body = str(fdg[0])
                    iob = identified_on_body.split(', ')
                    del iob[0] # erste Element wird gelöscht. bio_genus [, Bacterium, Tubus]
                    if genus.capitalize() in iob: # Nur die Bios sollen übernommen werden die auch der DOS erkannt hat
                        marked = 1
                else: # Alle Bios werden übernommen wenn kein DOS ausgeführt wurde.
                    marked = 1
                if genus == genus2:
                    genus = ''
                else:
                    genus2 = genus
                if marked == 1:
                    worth = worth_it([(0,0,0,species.capitalize())])
                    worth = ((f'{worth:,}').replace(',', '.'))
                    data_2.append(('', '', '', genus.capitalize(), species.capitalize(),
                                   worth,color, bio_distance, '', mark_missing))
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
    return (date_log, time_log, system_id, system_name)


def get_last_system_in_DB():
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

    with open(file, 'r', encoding='UTF8') as datei:
        for zeile in datei.readlines():
            data = read_json(zeile)
            if data.get('event', 0) == 'Commander':
                cmdr = data.get('Name', '0')
                with open(file, 'r', encoding='UTF8') as datei_2:
                    for zeile in datei_2.readlines()[::-1]:  # Read File line by line reversed!
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

    system.insert(END, (('Daten werden eingelesen \n')))
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
    system.delete('1.0', END)

    war_data_to_online_db()
    update_thargoid_war()
    b_filter = Filter.get()
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
        # print(lines_in_file)
        # print(str(last_line_in_db[0][0]+1))

        if (last_line_in_db[0][0]+1) == lines_in_file:
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
        connection.commit()
        # exit(1)
        print('Test if windows exists')
        try:
            if tree_frame.winfo_exists():
                codex_tree.delete(*codex_tree.get_children())
                tree_frame.destroy()
        except NameError:
            print('windows does not exists')
        root.destroy()
        exit(1)
    return


def treeview_codex():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    global filter_region, filter_cmdr, filter_bdata, combo_cmdr, combo_region, \
        combo_bio_data, b_data, regions, cmdr, tree, normal_view, death_frame, \
        death_date_combo, sell_combo, begin_time, end_time, sorting, refresher, my_codex_preview
    refresher = 0
    sorting = IntVar()
    # normal_view = 1
    normal_view = 4
    filter_region = ''
    filter_cmdr = ''
    filter_bdata = ''
    tree = Toplevel(root)
    tree.title('Display Codex Data')
    tree.geometry("1200x570")
    tree.minsize(1200, 570)
    tree.maxsize(1200, 1080)
    tree.after(1, lambda: tree.focus_force())
    try:
        img = resource_path("eddc.ico")
        tree.iconbitmap(img)
    except TclError:
        logger('Icon not found', 1)

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

    def save_position():
        position = {
            "x": tree.winfo_x(),
            "y": tree.winfo_y()
        }
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE eddc_positions SET x = ? , y = ? where id = 2",
                           (position["x"], position["y"]))
            connection.commit()

    def load_position():
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT x, y FROM eddc_positions where id = 2")
            position = cursor.fetchone()
            if position:
                tree.geometry("+{}+{}".format(position[0], position[1]))

    load_position()
    tree.bind("<Configure>", lambda event: save_position())

    style = ttk.Style(tree)
    style.theme_use('default')
    style.configure('Treeview',
                    background="#D3D3D3",
                    foreground="black",
                    rowheight=21,
                    fieldbackground="#D3D3D3"
                    )
    style.map('Treeview',
              background=[('selected', "#CDB872")])
    bg_treeview = resource_path("bg_treeview.png")
    background_image = PhotoImage(file=bg_treeview)
    background_label = Label(tree, image=background_image, bg='black', anchor='s')
    background_label.place(relwidth=1, relheight=1)

    # background_label.pack()

    def switch_view():
        global normal_view
        if normal_view == 0:
            normal_view = 1
        else:
            normal_view = 0
        refresh_view()
        refresh_combo()

    def codex_stars():
        global normal_view
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)
        normal_view = 3
        b_data = ['', 'Star', 'Carbon-Stars', 'Giant Stars', 'Gas Giant', 'Proto Stars',
                  'Brown Dwarfs', 'Non-Sequenz Stars', 'Terrestrials', 'Geology and Anomalies', 'Xenological']
        combo_bio_data.configure(values=b_data)
        refresh_view()
        refresh_combo()

    def system_scanner():
        global normal_view
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)
        normal_view = 4
        refresh_view()
        refresh_combo()

    def ed_statistics():
        global normal_view
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)
        normal_view = 5
        refresh_view()
        refresh_combo()


    menu_tree = Menu(tree)
    tree.config(menu=menu_tree)
    file_menu = Menu(menu_tree, tearoff=False)
    # menu_tree.add_cascade(label="More", menu=file_menu)
    menu_tree.add_cascade(label="Bio Scans", command=switch_view)
    menu_tree.add_cascade(label="Codex Stars", command=codex_stars)
    menu_tree.add_cascade(label="System Scanner", command=system_scanner)
    # file_menu.add_command(label="Bio Scans / Missing Bios", command=switch_view)
    # file_menu.add_command(label="Codex Stars", command=codex_stars)
    # file_menu.add_command(label="System Scanner", command=system_scanner)

    # file_menu.add_command(label="Player Death", command=player_death)
    # file_menu.add_command(label="ED: Statistics", command=ed_statistics)


    def create_frame():
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)

        global tree_frame, tree_scroll, codex_tree
        print('Test if windows exists')
        try:
            if tree_frame.winfo_exists():
                codex_tree.delete(*codex_tree.get_children())
                tree_frame.destroy()
        except NameError:
            print('windows does not exists')
        tree_frame = Frame(tree, bg='black')
        tree_frame.pack(pady=5)
        load_position()

        tree_scroll = Scrollbar(tree_frame)
        tree_scroll.pack(side=RIGHT, fill=Y)
        codex_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, selectmode="extended", height=14)
        tree_scroll.config(command=codex_tree.yview)

    def selected(event):
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)

        global filter_region, filter_cmdr, filter_bdata, filter_sday, filter_dday, \
            begin_time, end_time, sell_combo, death_date_combo
        filter_region = combo_regions.get()
        filter_cmdr = combo_cmdr.get()
        filter_bdata = combo_bio_data.get()
        refresh_combo()
        refresh_view()

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
            sql_beginn = f'''SELECT date_log, time_log, cmdr, codex_name, codex_entry, '', system, '', region 
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
                select = cursor.execute(sql_beginn + part + sql_end).fetchall()
                return select
            select = cursor.execute(sql_beginn + part + sql_end).fetchall()
            return select

    def check_planets():
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)

        data = []
        data = start_read_logs()
        if not data:
            # file = [('C:\\Users\\jiyon\\Saved Games\\Frontier Developments\\Elite Dangerous\\Journal.2023-05-12T203603.01.log'),]
            # data = get_data_from_DB(file[0])
            logger('No Data - check_planet', 2)
            data = [('Body', 'Distance', 'Count', 'Genus',
                     'Family', 'Value', 'Color', "Distance", "Region", "No Data")]
        return data

    def set_main_column_and_heading():
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

    def set_system_scanner_treeview():
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)

        codex_tree.heading("Datum", text="Body", anchor=W)
        codex_tree.column("Datum", anchor=W, width=180)
        codex_tree.heading("Zeit", text="Distance to main Star", anchor=W)
        codex_tree.column("Zeit", anchor=CENTER, width=100)
        codex_tree.heading("CMDR", text="Count", anchor=CENTER)
        codex_tree.column("CMDR", anchor=CENTER, width=50)
        codex_tree.heading("Codex eintrag", text="Familie", anchor=CENTER)
        codex_tree.column("Codex eintrag", anchor=CENTER, width=80)
        codex_tree.heading("Codex Farbe", text="Spezies", anchor=CENTER)
        codex_tree.column("Codex Farbe", anchor=CENTER, width=150)
        codex_tree.heading("Scan Value", text="Scan Value", anchor=E)
        codex_tree.heading("System", text="Color", anchor=CENTER)
        codex_tree.column("System", anchor=CENTER, width=150)
        codex_tree.heading("Body", text="Colony Distance", anchor=CENTER)
        codex_tree.column("Body", anchor=CENTER, width=100)
        codex_tree.heading("Region", text="Region", anchor=E)

    def set_stars_treeview():
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)

        print('reset_pos')

        codex_tree.heading("Datum", text="Datum", anchor=W)
        codex_tree.heading("Zeit", text="Zeit", anchor=W)
        codex_tree.heading("CMDR", text="CMDR", anchor=CENTER)
        codex_tree.heading("Codex eintrag", text="Codex", anchor=CENTER)
        codex_tree.heading("Codex Farbe", text="-kategorie", anchor=CENTER)
        codex_tree.heading("Scan Value", text=" ", anchor=E)
        codex_tree.heading("System", text="System", anchor=CENTER)
        codex_tree.heading("Body", text="", anchor=CENTER)
        codex_tree.heading("Region", text="Region", anchor=E)

        codex_tree.column("Datum", anchor=CENTER, width=80)
        codex_tree.column("Zeit", anchor=CENTER, width=100)
        codex_tree.column("CMDR", anchor=CENTER, width=120)
        codex_tree.column("Codex eintrag", anchor=E, width=150)
        codex_tree.column("Codex Farbe", anchor=E, width=200)
        codex_tree.column("Scan Value", anchor=CENTER, width=5)
        codex_tree.column("System", anchor=E, width=200)
        codex_tree.column("Body", anchor=CENTER, width=5)
        codex_tree.column("Region", anchor=E, width=250)

    def set_statistics_treeview():
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

    def get_statistics_data():
        funktion = inspect.stack()[0][3]
        logger(funktion, 1)

        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            filter_region = combo_regions.get()
            filter_cmdr = combo_cmdr.get()
            filter_bdata = combo_bio_data.get()
            print(filter_cmdr)
            print(filter_region)
            print(filter_bdata)
            if filter_cmdr and not filter_region and filter_bdata:
                if filter_cmdr == 'Stars':
                    print('filter stars')
                    if filter_bdata == 'TEMP':
                        filter_bdata = 'surface_temp'

                    sql = f'''SELECT sd.date_log, sd.time_log, sd.starsystem, sd.body_name, sd.startype, sd.mass, sd.age, 
                    sd.surface_temp, sd.system_address from star_data sd                     
                    where "{filter_bdata}" > 0 ORDER by "{filter_bdata}" DESC LIMIT 10'''

                else:
                    if filter_bdata == 'TEMP':
                        filter_bdata = 'Temperature'
                    sql = f'''SELECT pi.date_log, pi.time_log, pi.systemname, pi.bodyname, pi.planettype, pi.mass, 
                    pi.gravity, pi.temperature, pi.systemid from planet_infos pi 
                    where {filter_bdata} > 0 ORDER by {filter_bdata} DESC LIMIT 10'''
            else:
                sql = f'''SELECT sd.date_log, sd.time_log, sd.starsystem, sd.body_name, sd.startype, sd.mass, sd.age, 
                sd.surface_temp, sd.system_address from star_data sd where mass > 0 ORDER by mass DESC LIMIT 10'''
            print(sql)
            select = cursor.execute(sql).fetchall()
            new_data = []
            for i in select:
                system_address = (i[8])
                region = (findRegionForBoxel(system_address)['region'][1])
                # print(region)
                age = str(i[6]) +' MY'
                temp = str(float(i[7]) - 273.15) + ' C°'
                new_data.append((i[0] ,i[1] ,i[2] ,i[3] ,i[4] ,i[5] ,age ,temp ,region))
            return new_data
        # pass

    def codex_treeview():
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)

        t1 = get_time()
        summe = 0
        data = ['']
        update = 0
        if normal_view == 0:
            t11 = get_time()
            if sorting.get() != 0:
                update = 3  # Nach Datum sortiert
            else:
                update = 0  # Nach biologischen Daten sortiert
            data = select_filter(filter_cmdr, filter_region, filter_bdata, update)
            t12 = get_time()
            logger(('Normal Codex   ' + str(timedelta.total_seconds(t12 - t1))), 1)

        elif normal_view == 1:
            t11 = get_time()
            data = missing_codex(filter_cmdr, filter_region)
            t12 = get_time()
            logger(('missing_codex   ' + str(timedelta.total_seconds(t12 - t11))), 1)
            update = 0

        # All Codex Data except BIO
        elif normal_view == 3:  # Zeige Codex Daten ohne die Biologischen vom CMDR und oder der Region an
            data_time_1 = get_time()
            data = read_codex_data(filter_cmdr, filter_region)
            update = 0
            data_time_2 = get_time()
            logger(('get read_codex_ Data   ' + str(timedelta.total_seconds(data_time_2 - data_time_1))), 1)

        elif normal_view == 4:  # Anhand der gescannten Daten wird ermittelt welche BIO Signal auf dem Planeten sein können
            global data2
            data2 = check_planets()
            if data2 != 0:
                data = data2
            update = 0

        elif normal_view == 5: # Statistik Menü
            data = get_statistics_data()
            worth = ''

        if not data:
            data = [('DATE', 'TIME', 'COMMANDER', 'SPECIES',
                     'VARIANT', 'SYSTEM', 'BODY', "In REGION ", 3)]
            summe = 0
        elif normal_view == 2 or normal_view == 0:  ###### ?????????????
            summe = 0
            summe = worth_it(data)

        # creating treeview
        set_main_column_and_heading()
        if normal_view == 4:
            set_system_scanner_treeview()
        elif normal_view == 0 or normal_view == 1:
            set_main_column_and_heading()
        elif normal_view == 3:
            set_stars_treeview()
        elif normal_view == 5:
            set_statistics_treeview()
        # insert Data in treeview
        global treeview_count
        treeview_count = 0
        worth = ''
        subrow = 0
        open = 'True'
        counter = 'a'

        t3 = get_time()

        def add_entries(entries):
            global treeview_count
            for idx, entry in enumerate(entries):
                treeview_count += 1
                new_entry = (treeview_count,) + entry
                tags = ()
                if entry[1] != '' and normal_view == 4:
                    tags = ('header',)
                else:
                    if idx % 2 == 1:
                        if normal_view == 4:
                            if entry[9] == 1:
                                tags = ('odd_new',)
                            else:
                                tags = ('odd',)
                        else:
                            tags = ('odd',)
                    else:
                        if normal_view == 4:
                            if entry[9] == 1:
                                tags = ('even_new',)
                            else:
                                tags = ('even',)
                        else:
                            tags = ('even',)
                codex_tree.insert('', 'end', values=new_entry, tags=tags)

        codex_tree.tag_configure('odd', background='lightblue')
        codex_tree.tag_configure('even', background='white')
        codex_tree.tag_configure('odd_new', background='lightgreen', font=('Arial', 9, 'bold'))
        codex_tree.tag_configure('even_new', background='#26D5B3', font=('Arial', 9, 'bold'))
        codex_tree.tag_configure('header', background='ivory3', font=('Arial', 9, 'bold'))

        add_entries(data)

        summen_text = ''
        codex_tree.pack()
        if summe > 0 and (normal_view == 2 or normal_view == 0):
            summen_text = ('Summe  - Anzahl Einträge : ' + str(treeview_count) + '     Wertigkeit :  ' + str(f"{summe:,}"))
            summen_label = Label(tree_frame, text=summen_text, bg='black', fg='white')
            summen_label.pack(fill=X, side=RIGHT)
        t2 = get_time()
        logger(('codex_treeview  ' + str(timedelta.total_seconds(t2 - t1))),1)
        logger(('for record ...  ' + str(timedelta.total_seconds(t2 - t3))),1)
        # End of codex_treeview()

    def read_files():  # Gibt es was neues?
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)
        create_tables()

        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            select_cd = cursor.execute("""
                                            SELECT date_log, time_log FROM codex_data ORDER BY date_log desc, 
                                            time_log DESC LIMIT 1;
                                            """, ).fetchall()
            select_c = cursor.execute("""
                                            SELECT date_log, time_log FROM codex ORDER BY date_log desc, 
                                            time_log DESC LIMIT 1;
                                            """, ).fetchall()
            read_codex_entrys()
            select_cd_new = cursor.execute("""
                                            SELECT date_log, time_log FROM codex_data ORDER BY date_log desc, 
                                            time_log DESC LIMIT 1;
                                            """, ).fetchall()
            select_c_new = cursor.execute("""
                                            SELECT date_log, time_log FROM codex ORDER BY date_log desc, 
                                            time_log DESC LIMIT 1;
                                            """, ).fetchall()
            # print(select_c, select_c_new)
            # print(select_cd, select_cd_new)

            if select_cd != select_cd_new or select_c != select_c_new:
                return 1
            else:
                return 0

    def refresh_treeview():
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)
        # t7 = get_time()
        threading.Thread(target=treeview_loop).start()
        # t8 = get_time()
        # print('treeview_loop  ' + str(timedelta.total_seconds(t8 - t7)))

    def treeview_loop():
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)
        switch = 0
        try:
            while tree is not None and tree.winfo_exists():
                if normal_view != 4:
                    switch = read_files()
                else:
                    data3 = check_planets()
                    switch = 0
                    if data2 != data3:
                        switch = 1  # es gibt neue Daten zum Anzeigen

                b_date_new = begin_time.get()
                e_date_new = end_time.get()

                if b_date != b_date_new or e_date != e_date_new:
                    logger('Datums Filter hat sich verändert', 1)
                    switch = 1

                if switch == 1:
                    # logger('log has changed', 1)
                    refresh_view()
                    refresh_combo()
                else:
                    # full_scan()
                    time.sleep(2.0)
        except:
            time.sleep(2.0)
            # pass

    def refresh_view():
        global tree_start
        tree_start += 1
        # print(tree_start)
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)

        # codex_tree.delete(*codex_tree.get_children())
        # tree_frame.destroy()
        global b_date, e_date
        b_date = begin_time.get()
        e_date = end_time.get()
        create_frame()
        codex_treeview()
        codex_tree.bind("<ButtonRelease-1>", selected_record)

    global buttons_frame
    buttons_frame = Frame(tree, background='black')
    buttons_frame.pack(fill=X, pady=15)

    def refresh_combo():
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)
        read_codex_entrys()
        # lang = read_language()
        filter_bio_data = combo_bio_data.get()
        if filter_bio_data:
            filter_bdata = '%' + filter_bio_data + '%'
        else:
            filter_bdata = ''

        s_table = 'codex'
        if normal_view == 3:
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

            third_combo = 'codex_name'
            s_table = 'codex_data'
            if selected_value == '<- back':
                b_data = ['', 'Star', 'Carbon-Stars', 'Giant Stars', 'Gas Giant', 'Proto Stars',
                          'Brown Dwarfs', 'Non-Sequenz Stars', 'Terrestrials', 'Geology and Anomalies', 'Xenological']
                combo_bio_data.configure(values=b_data)


        elif normal_view == 1 or normal_view == 0:
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
                print(query_cmdr)

            try:
                selection_region = cursor.execute(query_region).fetchall()
            except sqlite3.OperationalError:
                print(query_region)

            for cmdr in selection_cmdr:
                cmdrs = cmdrs + [cmdr[0]]

            for region in selection_region:
                regions = regions + [region[0]]

            if normal_view == 4:
                b_data = ['']
                cmdrs = ['']
                regions = ['']
            if normal_view == 0 or normal_view == 1:
                combo_bio_data.configure(values=b_data)
            elif normal_view == 5:  # statistics Combo Filter
                cmdrs = ('Stars', 'Bodys')
                query_region = f'''SELECT DISTINCT region FROM codex_entry ORDER BY region'''
                b_data = ('MASS', 'AGE', 'TEMP')

                selection_region = cursor.execute(query_region).fetchall()
                for region in selection_region:
                    regions = regions + [region[0]]
                combo_bio_data.configure(values=b_data)

            connection.commit()
            combo_cmdr.configure(values=cmdrs)
            combo_regions.configure(values=regions)


    def create_button():
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)

        global combo_cmdr, combo_regions, combo_bio_data, refresh_button, death_date_combo, sell_combo, sorting
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        select_cmdr = cursor.execute("SELECT DISTINCT cmdr FROM codex ORDER BY cmdr").fetchall()
        connection.commit()
        select_region = cursor.execute("SELECT DISTINCT region FROM codex ORDER BY region").fetchall()
        connection.commit()

        b_data = [('')]
        cmdrs = [('')]
        region = [('')]

        if normal_view != 4:
            for i in select_cmdr:
                cmdrs = cmdrs + [i[0]]

            # Combobox Region
            for i in select_region:
                region = region + [i[0]]

        if normal_view == 3:
            b_data = ['', 'Star', 'Carbon-Stars', 'Giant Stars', 'Gas Giant', 'Proto Stars',
                      'Brown Dwarfs', 'Non-Sequenz Stars', 'Terrestrials', 'Geology and Anomalies', 'Xenological']

        elif normal_view == 1 or normal_view == 0:
            b_data = [(''), ('Aleoida'), ('Bacterium'), ('Cactoida'), ('Clypeus'), ('Concha'),
                      ('Electricae'), ('Fonticulua'), ('Fungoida'), ('Frutexa'), ('Fumerola'), ('Osseus'),
                      ('Recepta'), ('Stratum'), ('Tubus'), ('Tussock'), ('---------'),
                      ('Amphora Plant'), ('Anemone'), ('Bark Mounds'), ('Brain'),
                      ('Crystalline Shards'), ('Fumerola'), ('Tubers')]


        label_tag = Label(buttons_frame, text="Filter:", bg='black', fg='white', font=("Helvetica", 11))
        label_tag.pack(side=LEFT, padx=29)
        combo_cmdr = ttk.Combobox(buttons_frame, state='readonly')
        combo_cmdr['values'] = cmdrs
        combo_cmdr.current(0)
        combo_cmdr.bind("<<ComboboxSelected>>", selected)
        combo_cmdr.pack(side=LEFT, padx=15)

        combo_regions = ttk.Combobox(buttons_frame, state='readonly')
        combo_regions['values'] = region
        combo_regions.current(0)
        combo_regions.bind("<<ComboboxSelected>>", selected)
        combo_regions.pack(side=LEFT, padx=15)

        combo_bio_data = ttk.Combobox(buttons_frame, state='readonly')
        combo_bio_data['values'] = b_data
        combo_bio_data.current(0)
        combo_bio_data.bind("<<ComboboxSelected>>", selected)
        combo_bio_data.pack(side=LEFT, padx=10)

        sell_combo = ttk.Combobox(buttons_frame, state='readonly')
        sell_combo['values'] = ''
        death_date_combo = ttk.Combobox(buttons_frame, state='readonly')
        death_date_combo['values'] = ''

        refresh_button = Button(buttons_frame, text='Refresh', command=refresh_treeview)
        refresh_button.pack(side=LEFT, padx=20)

        global begin_time, end_time
        label_tag = Label(buttons_frame, text="Datum - Anfang:", bg='black', fg='white', font=("Helvetica", 11))
        label_tag.pack(side=LEFT, padx=10)
        begin_time = Entry(buttons_frame, width=10, font=("Helvetica", 11))
        begin_time.insert(0, '2014-12-16')
        begin_time.pack(side=LEFT, padx=10)

        label_tag = Label(buttons_frame, text="Ende: ", bg='black', fg='white', font=("Helvetica", 11))
        label_tag.pack(side=LEFT, padx=10)
        end_time = Entry(buttons_frame, width=10, font=("Helvetica", 11))
        end_time.insert(0, str(date.today()))
        end_time.pack(side=LEFT, padx=10)
        global b_date, e_date
        b_date = begin_time.get()
        e_date = end_time.get()
        global sort_button
        sort_button = Checkbutton(buttons_frame,
                                  text="Sort by Date",
                                  bg='black',
                                  fg='white',
                                  selectcolor='black',
                                  activebackground='black',
                                  activeforeground='white',
                                  variable=sorting,
                                  command=refresh_view,
                                  onvalue=3)
        sort_button.pack(side=LEFT, padx=10)
        sort_button.select()

        # codex_frame = Frame(tree, highlightbackground="blue", highlightthickness=1, bd=10)
        # codex_frame.pack()
        connection.close()

    global tree_start
    tree_start = 0

    t1 = get_time()
    create_button()
    t2 = get_time()
    create_frame()
    t3 = get_time()
    codex_treeview()
    t4 = get_time()

    # print('create_button  ' + str(timedelta.total_seconds(t2 - t1)))
    # print('create_frame  ' + str(timedelta.total_seconds(t3 - t2)))
    # print('codex_treeview  ' + str(timedelta.total_seconds(t4 - t3)))

    def selected_record(e):  # Shows Picture of selected Item
        global my_img, my_codex_preview
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)
        selected_tree = codex_tree.focus()
        values = codex_tree.item(selected_tree, 'values')
        print(values)
        tables = [codex_bio_table, codex_stars_table, system_scanner_table]
        for table in tables:
            try:
                table.clear_rows()
            except AttributeError:
                logger(('NoData in ' + str(table)), 2)
        root.clipboard_clear()
        table = [codex_bio_table, codex_bio_table, '', codex_stars_table, system_scanner_table, statistics_table]

        if values == '':
            return
        if values == ('0', 'DATE', 'TIME', 'COMMANDER', 'SPECIES', 'VARIANT', '', 'SYSTEM', 'BODY', 'REGION') \
                or values == (
                '0', 'DATE', 'TIME', 'COMMANDER', 'SPECIES', 'VARIANT', '0', 'SYSTEM', 'BODY', 'In REGION ') \
                or values == ('0', 'Body', 'Distance', 'Count', 'Genus', 'Family', '', 'Value', 'Color', 'No Data') \
                or values == ('0', 'DATE', 'TIME', 'COMMANDER', 'SPECIES', 'VARIANT', '', 'SYSTEM', 'BODY', '') :
            return

        if values[4] =='':
            with sqlite3.connect(database) as connection:
                cursor = connection.cursor()
                query_s_bio = f'''SELECT DISTINCT(name) from bio_color where name like "%{values[5]}%"'''
                select_bio = cursor.execute(query_s_bio).fetchall()
                new_value = str(select_bio[0][0])
                new_value = new_value.split(' ')
                values = (values[0], values[1], values[2], values[3], new_value[0], new_value[1],
                          values[6],values[7], values[8], values[9], values[10])
        if values:
            (table[normal_view]).add_row(values) #                   table[ 1 = codex_bio_table ]
            root.clipboard_append((table[normal_view]).get_string())
            root.clipboard_append('\n')
        my_img = ''
        if values:
            if normal_view == 3:
                var = str(values[5]).split()
                if 'D' in var[0]:
                    var = ['D', 'Type', 'Star']
            else:
                var = str(values[4]).split()
            if normal_view == 4:
                # print(values[5])
                var = '%' + values[5] + '%'
                with sqlite3.connect(database) as connection:
                    cursor = connection.cursor()
                    select = cursor.execute("SELECT DISTINCT data FROM codex_entry WHERE data like ? ",
                                            (var,)).fetchall()
                    if select:
                        var = str(select[0][0]).split()
                # print(var)
            png = ''
            for x, i in enumerate(var):
                # print(x, len(var))
                if (x + 1) == len(var):
                    png += (var[x] + ".png")
                else:
                    png += (var[x] + '_')
            if Path('images/' + png).is_file():
                photo = "images/" + str(png)
                file = resource_path(photo)
                image = Image.open(file)
                image = image.resize((320, 145))
                my_img = ImageTk.PhotoImage(image)
                # print("File exist")
            else:
                logger("File not found", log_var)
                logger(png, log_var)
                file = resource_path("images/Kein_Bild.png")
                image = Image.open(file)
                image = image.resize((320, 145))
                my_img = ImageTk.PhotoImage(image)
        else:
            return
        my_codex_preview = Label(tree, image=my_img)
        my_codex_preview.place(x=837, y=400)
        # my_codex_preview.place()

    codex_tree.bind("<ButtonRelease-1>", selected_record)

    if tree_start == 0:
        #     logger(('tree_start > 1', tree_start), 1)
        #     refresh_treeview()
        # else:
        tree_start += 1
        logger(('tree_start', tree_start), 1)
        # threading.Thread(target=rescan_files).start()
        refresh_treeview()

    def on_closing():
        save_position()
        tree.destroy()

    tree.protocol("WM_DELETE_WINDOW", on_closing)

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


def missing_codex(filter_cmdr, filter_region):
    funktion = inspect.stack()[0][3]
    logger(funktion, 1)
    # global normal_view
    # normal_view = 1

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cmdrs = cursor.execute("SELECT DISTINCT cmdr FROM codex").fetchall()
        cursor.execute("DROP TABLE IF EXISTS codex_show")
        cursor.execute("""CREATE table IF NOT EXISTS codex_show (
                                cmdr TEXT,
                                data TEXT,
                                region TEXT)
                                """)
        connection.commit()

        bio_names = cursor.execute("SELECT DISTINCT data FROM codex_entry").fetchall()
        regions = RegionMapData.regions

        for cmdr in cmdrs:
            for region in regions:
                if region is not None:
                    for bio in bio_names:
                        cursor.execute("INSERT INTO codex_show VALUES (?, ?, ?)", (cmdr[0], bio[0], region))
        connection.commit()

        # select all Codex Entrys from Codex
        temp = cursor.execute("SELECT DISTINCT cmdr, data, region FROM codex WHERE codex.codex = 1").fetchall()
        if temp:
            del_sql = ''
            for i in temp:
                delete_cmdr = str(i[0])
                delete_bio = str(i[1])
                delete_region = str(i[2])
                del_sql = f'''DELETE FROM codex_show WHERE cmdr = "{delete_cmdr}" AND data = "{delete_bio}" AND region = "{delete_region}";\n'''
                cursor.execute(del_sql)
            connection.commit()

        filter_bio_data = combo_bio_data.get()
        if filter_bio_data:
            filter_bdata = '%' + filter_bio_data + '%'
        else:
            filter_bdata = ''

        if not filter_cmdr and not filter_region and not filter_bdata:
            query = f'''SELECT * FROM codex_show ORDER BY data'''
            select = cursor.execute(query).fetchall()

        elif filter_cmdr and filter_region and filter_bdata:
            query = f'''SELECT * FROM codex_show WHERE cmdr = "{filter_cmdr}" 
            and region = "{filter_region}" and data like "{filter_bdata}" ORDER BY data'''
            select = cursor.execute(query).fetchall()

        elif filter_cmdr and filter_region and not filter_bdata:
            query = f'''SELECT * FROM codex_show WHERE cmdr = "{filter_cmdr}" 
                        and region = "{filter_region}" ORDER BY data'''
            select = cursor.execute(query).fetchall()

        elif filter_cmdr and not filter_region and filter_bdata:
            query = f'''SELECT * FROM codex_show WHERE cmdr = "{filter_cmdr}"
             and data like "{filter_bdata}" ORDER BY data'''
            select = cursor.execute(query).fetchall()

        elif filter_cmdr and not filter_region and not filter_bdata:
            query = f'''SELECT * FROM codex_show WHERE cmdr = "{filter_cmdr}" ORDER BY data'''
            select = cursor.execute(query).fetchall()

        elif not filter_cmdr and filter_region and filter_bdata:
            query = f'''SELECT * FROM codex_show WHERE 
            region = "{filter_region}" and data like "{filter_bdata}" ORDER BY data'''
            select = cursor.execute(query).fetchall()

        elif not filter_cmdr and filter_region and not filter_bdata:
            query = f'''SELECT * FROM codex_show WHERE region = "{filter_region}" ORDER BY data'''
            select = cursor.execute(query).fetchall()

        elif not filter_cmdr and not filter_region and filter_bdata:
            query = f'''SELECT * FROM codex_show WHERE data like "{filter_bdata}" ORDER BY data'''
            select = cursor.execute(query).fetchall()

    print(query)
    lauf = 1
    data = []
    for i in select:
        data.append((' ', ' ', i[0], i[1], ' ', ' ', ' ', '', i[2]))
        lauf += 1
    return data


def get_info_for_bio_scan(data, file): # event: ScanOrganic
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    timestamp = data.get('timestamp')
    scantype = data.get('ScanType')
    species = data.get('Species_Localised')
    system = data.get('SystemAddress')
    body = data.get('Body')
    body_name = ''
    if system == 0 or body == 0:
        return
    # print(data)
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select = cursor.execute("""SELECT starsystem, body_name from star_data where 
                                                    system_address = ? and
                                                    body_ID = ?""",
                                (system, body)).fetchall()
        if select != []:
            body_name = str(select[0][0]) + str(select[0][1])
        else:
            select = cursor.execute("""SELECT systemname, bodyname from planet_infos where 
                                                                systemid = ? and
                                                                bodyID = ?""",
                                    (system, body)).fetchall()
            if select:
                body_name = str(select[0][0]) + str(select[0][1])
            else:
                if body_name == '':
                    # body_name = 'systemaddress, ' + str(system) + ', body ID, ' + str(body)
                    names = get_body_from_sc(timestamp, system, file)
                    body_name = str(names[1]) + str(names[0])
                    logger((funktion, body_name),2)
                    # return
                # return

        select = cursor.execute("""SELECT * from temp where
                                                    timestamp = ? and
                                                    scantype = ? and
                                                    species = ? and                                                    
                                                    body = ?""",
                                (timestamp, scantype, species, body_name)).fetchall()
        if not select:
            cursor.execute("INSERT INTO temp VALUES (?, ?, ?, ?)",
                           (timestamp, scantype, species, body_name))
            connection.commit()
        count = cursor.execute("Select DISTINCT species body from temp where body = ?",
                               (body_name,)).fetchall()
        count_bios = []
        for i in count:
            select_count = cursor.execute("""Select count(species) from temp where species = ? and body = ? """,
                                          (i[0], body_name)).fetchone()

            bio_name = i[0].split(' ')
            genus = bio_name[0]
            species_2 = bio_name[1]
            color = ''
            mark_missing = '0'
            count_1 = select_count[0]
            if select_count[0] == 0:
                count_1 = 0
            elif select_count[0] == 1:
                count_1 = 1
            elif select_count[0] == 2:
                count_1 = 2
            elif select_count[0] == 4:
                count_1 = 3

            insert_into_bio_db(body_name, count_1, genus, species_2, color, mark_missing)
    return (timestamp, scantype, species, system, body)


def get_info_for_get_body_name(data):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    timestamp = data.get('timestamp')
    log_time = (log_date(timestamp))
    date_log = (log_time[0] + "-" + log_time[1] + "-" + log_time[2])
    time_log = (log_time[3] + ":" + log_time[4] + ":" + log_time[5])
    starsystem = data.get('StarSystem')
    system_address = data.get('SystemAddress')
    body_ID = data.get('BodyID')
    body_name = data.get('BodyName')
    if not body_name:
        body_name = data.get('Body')

    if not starsystem or not system_address:
        return 0

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        if body_ID and body_name:
            select = cursor.execute("""SELECT starsystem from star_data where 
                                                starsystem = ? and 
                                                system_address = ? and
                                                body_id = ? and
                                                body_name = ?""",
                                    (starsystem, system_address, body_ID, body_name)).fetchall()
            if select != []:
                return (starsystem, system_address, body_ID, body_name)
        # else:
        #     select_two = cursor.execute("""SELECT starsystem from star_map where
        #                                                 starsystem = ? and
        #                                                 system_address = ?""",
        #                                 (starsystem, system_address)).fetchall()
        #     if select_two != []:
        #         return (starsystem, system_address, body_ID, bodyname)
        select = cursor.execute("""SELECT starsystem, system_address from star_data where system_address = ? """,
                                (system_address,)).fetchall()
        if not select:
            cursor.execute("""INSERT INTO star_data (date_log, time_log, starsystem, system_address, body_id, body_name) 
                           VALUES (?, ?, ?, ?, ?, ?)""",
                           (date_log, time_log, starsystem, system_address, body_ID, body_name))
            connection.commit()

    return (starsystem, system_address, body_ID, body_name)


def get_system(system_address):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select_system = cursor.execute("""SELECT starsystem from star_data where system_address = ?""",
                                       (system_address,)).fetchall()
        if select_system:
            return select_system[0][0]


def get_planet_info(data):
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
        body_gravity = float(body_gravity) / 10
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
                """INSERT INTO planet_infos VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) """,
                (date_log, time_log, system_id, system_name, main_star, local_star, body_name, body_id,
                 body_distance, tidal_lock, terraform_state, planet_type, body_atmos, body_gravity,
                 body_temp, body_pressure, landable, volcanism, sulphur_concentration, has_rings, mass, radius,
                 semiMajorAxis,
                 eccentricity, orbitalInclination, periapsis, orbital_period, ascending_node, mean_anomaly,
                 rotation_period, axial_tilt, discovered, mapped, materials))
            connection.commit()


def get_star_info(data):
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
            cursor.execute("""INSERT INTO star_data (date_log, time_log, starsystem, system_address, startype, Main) 
                                VALUES (?,?,?,?,?,?)""",
                           (date_log, time_log, starsystem, system_address, startype, 1)).fetchall()
            connection.commit()


def insert_star_data_in_db(star_data): # Tabelle star_data mit Daten füllen
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    date_log = star_data[0]
    time_log = star_data[1]
    body_id = star_data[2]
    starsystem = star_data[3]
    body_name = star_data[4]
    system_address = star_data[5]
    distance = star_data[6]
    startype = star_data[7]
    sub_class = star_data[8]
    mass = star_data[9]
    radius = star_data[10]
    age = star_data[11]
    surface_temp = star_data[12]
    luminosity = star_data[13]
    rotation_period = star_data[14]
    axis_tilt = star_data[15]
    discovered = star_data[16]
    mapped = star_data[17]
    parents = str(star_data[18])
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        if distance == 0.0: # Mainstar
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
                cursor.execute("INSERT INTO star_data VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                               (date_log, time_log, body_id, starsystem, body_name, system_address, 1, distance,
                                startype, sub_class, mass, radius, age, surface_temp, luminosity, rotation_period,
                                axis_tilt, discovered, mapped, parents))
                return

        select = cursor.execute("""SELECT starsystem, system_address from star_data where system_address = ? 
                                and body_id = ? """, (system_address, body_id,)).fetchall()

        if not select:
            cursor.execute("INSERT INTO star_data VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                           (date_log, time_log, body_id, starsystem, body_name, system_address, '', distance,
                            startype, sub_class, mass, radius, age, surface_temp, luminosity, rotation_period,
                            axis_tilt, discovered, mapped, parents))
            connection.commit()


def get_all_stars(data):
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
    star_data = [date_log, time_log, body_id, starsystem, body_name, system_address, distance, startype,
                 sub_class, mass, radius, age, surface_temp, luminosity, rotation_period, axis_tilt, discovered,
                 mapped, parents]
    # print(star_data)
    insert_star_data_in_db(star_data)


def set_main_star(data):
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
    # if body_id != 0:
    #     body_name = body_name.replace((starsystem + ' '), '')
    # else:
    #     body_name = body_name.replace((starsystem), '')

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()

        select = cursor.execute("""SELECT starsystem, system_address from star_data where system_address = ? """,
                                (system_address,)).fetchall()
        if not select:
            cursor.execute("""INSERT INTO star_data (date_log, time_log, body_id, starsystem, body_name, 
            system_address, Main) VALUES (?,?,?,?,?,?,?)""",
                (date_log, time_log, body_id, starsystem, body_name, system_address, 1)).fetchall()

            connection.commit()

    return (body_id, starsystem, body_name, system_address)


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


def get_info_scan_planets(data):    # data['event'] == 'FSSBodySignals':
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



def get_species_for_planet(body):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    select = cursor.execute("""SELECT species from temp where body = ?""", (body,)).fetchall()

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
    select = cursor.execute("""SELECT count(species) from temp where
                                                species like ? and                                                    
                                                body = ?""",
                            (bio, body_name)).fetchall()

    # print(bio, body_name, select)

    if select[0][0] == 0:
        return ' ', 0
    if select[0][0] == 1:
        return 'Scan in Progress 1 / 3', 1
    if select[0][0] == 2:
        return 'Scan in Progress 2 / 3', 2
    if select[0][0] == 4:
        return 'Scan complete 3 / 3', 3


def select_filter(sf_cmdr, region, bio_data, update):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    create_tables()
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    data = []
    global b_date, e_date
    b_date = begin_time.get()
    e_date = end_time.get()
    # print(b_date, e_date)

    if update != 3:
        order = 'cmdr, region, data, date_log, time_log'
    else:
        order = 'date_log desc, time_log DESC'

    if bio_data != '':
        bio_data = '%' + bio_data + '%'
    if bio_data == '%---------%':
        bio_data = ''

    # # Fall 1 CMDR & REGION & BIO
    if sf_cmdr and region and bio_data:
        print('filter - 1')
        query = f'''SELECT c1.date_log, c1.time_log, c1.cmdr, c1.data, c1.bio_color, 
                    (SELECT worth FROM codex_entry ce WHERE ce.data = c1.data) AS product_price, 
                    c1.systemname, c1.body, c1.region FROM codex c1 
                    where cmdr = "{sf_cmdr}" and data like "{bio_data}" and region = "{region}"
                    AND date_log BETWEEN "{b_date}" AND "{e_date}" 
                    ORDER BY date_log DESC, time_log DESC;'''

    # # Fall 2 CMDR & Region
    elif sf_cmdr and region and not bio_data:
        print('filter - 3')
        query = f'''SELECT c1.date_log, c1.time_log, c1.cmdr, c1.data, c1.bio_color, 
                        (SELECT worth FROM codex_entry ce WHERE ce.data = c1.data) AS product_price, 
                        c1.systemname, c1.body, c1.region FROM codex c1 
                        where cmdr = "{sf_cmdr}" and region = "{region}"
                        AND date_log BETWEEN "{b_date}" AND "{e_date}" 
                        ORDER BY date_log DESC, time_log DESC;'''

    # # Fall 3 CMDR & Bio
    elif sf_cmdr and not region and bio_data:
        print('filter - 3')
        query = f'''SELECT c1.date_log, c1.time_log, c1.cmdr, c1.data, c1.bio_color, 
                (SELECT worth FROM codex_entry ce WHERE ce.data = c1.data) AS product_price, 
                c1.systemname, c1.body, c1.region FROM codex c1 
                where cmdr = "{sf_cmdr}" and data like "{bio_data}" 
                AND date_log BETWEEN "{b_date}" AND "{e_date}" 
                ORDER BY date_log DESC, time_log DESC;'''

    # # Fall4 only CMDR
    elif sf_cmdr and not region and not bio_data:
        print('filter - 4')
        query = f'''SELECT c1.date_log, c1.time_log, c1.cmdr, c1.data, c1.bio_color, 
                (SELECT worth FROM codex_entry ce WHERE ce.data = c1.data) AS product_price, 
                c1.systemname, c1.body, c1.region FROM codex c1 
                where cmdr = "{sf_cmdr}" AND date_log BETWEEN "{b_date}" AND "{e_date}" 
                ORDER BY date_log DESC, time_log DESC;'''
    # # Fall 5 only Region
    elif not sf_cmdr and region and not bio_data:
        print('filter - 5')
        query = f'''SELECT c1.date_log, c1.time_log, c1.cmdr, c1.data, c1.bio_color, 
                (SELECT worth FROM codex_entry ce WHERE ce.data = c1.data) AS product_price, 
                c1.systemname, c1.body, c1.region FROM codex c1 
                where region = "{region}"
                AND date_log BETWEEN "{b_date}" AND "{e_date}" 
                ORDER BY date_log DESC, time_log DESC;'''
    # # Fall 6 only Biodata
    elif not sf_cmdr and not region and bio_data:
        print('filter - 6')
        query = f'''SELECT c1.date_log, c1.time_log, c1.cmdr, c1.data, c1.bio_color, 
                    (SELECT worth FROM codex_entry ce WHERE ce.data = c1.data) AS product_price, 
                    c1.systemname, c1.body, c1.region FROM codex c1 
                    where data like "{bio_data}" 
                    AND date_log BETWEEN "{b_date}" AND "{e_date}" 
                    ORDER BY date_log DESC, time_log DESC;'''
    # # Fall 7 Region & Biodata
    elif not sf_cmdr and region and bio_data:
        print('filter - 1')
        query = f'''SELECT c1.date_log, c1.time_log, c1.cmdr, c1.data, c1.bio_color, 
                    (SELECT worth FROM codex_entry ce WHERE ce.data = c1.data) AS product_price, 
                    c1.systemname, c1.body, c1.region FROM codex c1 
                    where data like "{bio_data}" and region = "{region}"
                    AND date_log BETWEEN "{b_date}" AND "{e_date}" 
                    ORDER BY date_log DESC, time_log DESC;'''
    # # Fall 8 no Filter
    elif not sf_cmdr and not region and not bio_data:
        print('filter - 8')
        query = '''SELECT c1.date_log, c1.time_log, c1.cmdr, c1.data, c1.bio_color,
                      (SELECT worth FROM codex_entry ce WHERE ce.data = c1.data) AS product_price,
                      c1.systemname, c1.body, c1.region
                FROM codex c1 ORDER BY date_log DESC, time_log DESC;'''

    data = cursor.execute(query).fetchall()

    connection.commit()
    connection.close()
    # print(data)
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
    funktion = inspect.stack()[0][3] + " " + journal_file + " " + cmdr
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        log_cmdr = cursor.execute("Select CMDR from logfiles where Name = ?", (journal_file,)).fetchall()
        if log_cmdr:
            if log_cmdr[0][0] != None:
                return log_cmdr[0][0]
        select = cursor.execute("Select * from logfiles where Name = ? and CMDR is NULL", (journal_file,)).fetchall()

    if cmdr != '' and select:
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            cursor.execute("Update logfiles set CMDR = ? where Name = ? and CMDR is NULL", (cmdr, journal_file))
            connection.commit()
        return
    elif cmdr == '':
        cc_cmdr = read_cmdr(journal_file)
        if cc_cmdr and select:
            with sqlite3.connect(database) as connection:
                cursor = connection.cursor()
                cursor.execute("Update logfiles set CMDR = ? where Name = ? and CMDR is NULL", (cc_cmdr, journal_file))
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
        for zeile in datei.readlines()[::-1]:  # Read File line by line reversed!
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
    logger((funktion, bio_name ), log_var)
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
    # gcod_time_2 = get_time()
    # print('get_color_or_distance  ' + str(timedelta.total_seconds(gcod_time_2 - gcod_time_1)))
    return distance, data


def select_prediction_db(star_type, planet_type, body_atmos, body_gravity, body_temp, body_pressure,
                         volcanism, sulphur_concentration):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    body_atmos = body_atmos.replace(' atmosphere', '')
    body_atmos = body_atmos.lower()
    if 'rich' in body_atmos:
        body_atmos = body_atmos.replace(' rich', '-rich')
    planet_type = planet_type.lower()
    star_type = star_type.lower()
    body_temp = int(body_temp)
    # print('select Bio_prediction',  planet_type ,body_atmos,
    #       body_gravity, body_temp, body_pressure, volcanism)

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


def extract_engi_stuff(data, state):
    name = data.get('Name_Localised', 0)
    if name == 0:
        name = data.get('Name', 0)
    count = data.get('Count',0)
    engi_stuff_ody_db(str(name), int(count), state)
    return (str(name), int(data['Count']), state)


def engi_stuff_ody_db(name, count, state):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    if state < 0:
        count = count * (-1)
    ody_item_select = cursor.execute("SELECT Name FROM odyssey WHERE Name = ?", (name,)).fetchall()

    if not ody_item_select:
        cursor.execute("INSERT INTO odyssey VALUES (?, ?)", (name, count))
        connection.commit()
    else:
        ody_item_select = cursor.execute("SELECT Count FROM odyssey WHERE Name = ?", (name,)).fetchone()
        count += int(ody_item_select[0])
        cursor.execute("UPDATE odyssey SET Count = ? where Name = ?", (count, name))
        connection.commit()
    connection.close()


def print_engi_stuff_db(filter_b):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    filter_b = '%' + filter_b + '%'
    # ody_select = cursor.execute("SELECT * FROM odyssey WHERE Name LIKE ? ORDER BY Name",
    #                             (filter_b,)).fetchall()
    ody_select = cursor.execute("SELECT * FROM odyssey ORDER BY Count DESC").fetchall()
    connection.close()
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
            logger((funktion, data),1)
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

    tag = Tag.get()
    monat = Monat.get()
    jahr = '20' + Jahr.get()
    date_ed = jahr + '-' + monat + '-' + tag

    select_pass = cursor.execute("SELECT DISTINCT system from passengermissions where date_log = ? and completed = 1",
                                 (date_ed,)).fetchall()
    select_cargo = cursor.execute("SELECT DISTINCT system from cargomissions where date_log = ? and completed = 1",
                                  (date_ed,)).fetchall()
    select_rescue = cursor.execute("SELECT DISTINCT system from rescuemissions where date_log = ? and completed = 1",
                                   (date_ed,)).fetchall()

    summe_cargo = []
    system.delete('1.0', END)
    for i in select_cargo:
        system_se = i[0]
        anzahl = cursor.execute("SELECT SUM(cargocount) from cargomissions where system = ? and date_log = ?",
                                (system_se, date_ed)).fetchone()
        summe_cargo.append((system_se, anzahl[0]))

    system.insert(END, (('Cargo transfered \t \t \t \n')))
    system.insert(END, ('\n'))
    gesamt_cargo = 0
    if summe_cargo != []:
        for i in summe_cargo:
            system.insert(END, (((str(i[0])) + '\t \t \t \t' + (str(i[1])) + 't \n')))
            tw_cargo_table.add_row((i[0], i[1]))
            gesamt_cargo += int(i[1])
    system.insert(END, ('─────────────────────────────\n'))
    system.insert(END, ('Insgesamt \t \t \t \t' + (str(gesamt_cargo)) + 't \n'))
    system.insert(END, ('\n'))

    summe_rescue = []
    for i in select_rescue:
        system_se = i[0]
        anzahl = cursor.execute("SELECT SUM(cargocount) from rescuemissions where system = ? and date_log = ?",
                                (system_se, date_ed)).fetchone()
        summe_rescue.append((system_se, anzahl[0]))

    system.insert(END, (('Escape Pods rescued \t \t \t \n')))
    system.insert(END, ('\n'))
    gesamt_rescue = 0
    if summe_rescue:
        for i in summe_rescue:
            system.insert(END, (((str(i[0])) + '\t \t \t \t' + (str(i[1])) + 't \n')))
            tw_rescue_table.add_row((i[0], i[1]))
            gesamt_rescue += int(i[1])
    system.insert(END, ('─────────────────────────────\n'))
    system.insert(END, ('Insgesamt \t \t \t \t' + (str(gesamt_rescue)) + 't \n'))
    system.insert(END, ('\n'))

    summe_pass = []
    for i in select_pass:
        system_se = i[0]
        anzahl = cursor.execute("SELECT SUM(passengercount) from passengermissions where system = ? and date_log = ?",
                                (system_se, date_ed)).fetchone()
        summe_pass.append((system_se, anzahl[0]))

    system.insert(END, (('Passengers rescued \t \t \t \n')))
    system.insert(END, ('\n'))
    gesamt = 0
    if summe_pass != []:
        for i in summe_pass:
            system.insert(END, (((str(i[0])) + '\t \t \t \t' + (str(i[1])) + ' \n')))
            tw_pass_table.add_row((i[0], i[1]))
            gesamt += int(i[1])
    system.insert(END, ('─────────────────────────────\n'))
    system.insert(END, ('Insgesamt \t \t \t \t' + (str(gesamt)) + ' \n'))


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
    menu_var = [0, 'BGS', 'ody_mats', 'MATS', 'CODEX', 'combat', 'thargoid', 'boxel', 'cube', 'war', 'reset_pos', 'summary',
                'war_progress']
    # eddc_modul     1        2          3       4        5          6          7        8      9       10      11
    # eddc_modul     12

    # Filter.delete(0, END)
    if var == menu_var[1]:
        check_but.config(state=NORMAL)
        vor_tick.config(state=NORMAL)
        nach_tick.config(state=NORMAL)
        last_tick_label.config(foreground='white')
        tick_hour_label.config(background='white')
        tick_minute_label.config(background='white')
        eddc_modul = 1
        auswertung(eddc_modul)
    else:
        if var == menu_var[4]:
            check_but.deselect()
            check_but.config(state=DISABLED)
        else:
            check_but.config(state=NORMAL)
        vor_tick.config(state=DISABLED)
        nach_tick.config(state=DISABLED)
        last_tick_label.config(foreground='black')
        tick_hour_label.config(background='black')
        tick_minute_label.config(background='black')
        lauf = -1
        for i in menu_var:
            lauf += 1
            if var == i:
                eddc_modul = lauf
                auswertung(eddc_modul)


def select_last_log_file():
    # Vorletztes Logfile aus der Datenbank auslesen und übergeben.
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS logfiles (Name TEXT, explorer INTEGER, "
                   "bgs INTEGER, CMDR TEXT, last_line INTEGER)")
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


def read_codex_entrys():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    t1 = get_time()
    # system.delete('1.0', END)
    # system.insert(END, 'Codex Daten werden gelesen \n')
    filenames = file_names(1)  # Alle Logfile werden geladen
    last_log = (len(filenames))
    files = check_last_logs(filenames, last_log)
    count = 1
    for count, filename in enumerate(files):
        check_logfile_in_DB(filename, '', 'insert')
        if count % 10 == 0:
            system.delete('1.0', END)
            position = 'File \t' + str(count) + ' of ' + str(len(files))
            system.insert(END, str(position))
        with open(filename, 'r', encoding='UTF8') as datei:
            for zeile in datei:
                data = read_json(zeile)
                event = data.get('event')
                match event:
                    case 'CodexEntry':
                        read_log_codex(data, filename)
                    case 'ScanOrganic':
                        read_bio_data(data, filename)
    system.delete('1.0', END)
    position = 'File \t' + str(len(files)) + ' of ' + str(len(files))
    system.insert(END, str(position))
    t2 = get_time()
    # print('read_codex_entrys   ' + str(timedelta.total_seconds(t2 - t1)))


def run_once_rce(filenames):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    thread_rce = threading.Thread(target=read_codex_entrys, args=())

    if len(filenames) > 5:
        logger('start run_once', 2)
        thread_rce.start()
        logger('stop run_once', 2)
        # treeview_codex()
    else:
        read_codex_entrys()
    # while True:
    if not thread_rce.is_alive():
        treeview_codex()
        # break


def combat_rank():
    funktion = inspect.stack()[0][3]
    logger(funktion, 2)
    system.delete(1.0, END)
    b_target = ''
    b_total_reward = ''
    sh_target = ''
    sh_total_reward = '0'
    pilot_rank = ''
    ranking = [('Harmless', 'Harmlos', 0, 1), ('Mostly Harmless', 'Zumeist Harmlos', 0, 2), ('Novice', 'Neuling', 0, 3),
               ('Competent', 'Kompetent', 0, 4), ('Expert', 'Experte', 0, 5), ('Master', 'Meister', 0, 6),
               ('Dangerous', 'Gefährlich', 0, 7), ('Deadly', 'Tödlich', 0, 8), ('Elite', 'Elite', 0, 9)]
    b_filter = Filter.get()

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
                            if sh_target == None:
                                sh_target = data.get('Ship')
                            sh_total_reward = data['Bounty']
                            pilot_rank = data['PilotRank']
                        elif data['ScanStage'] > 0:
                            if data['ScanStage'] != 3:
                                sh_target = data.get('Ship_Localised')
                                if sh_target == None:
                                    sh_target = data.get('Ship')
                                sh_total_reward = 0
                                pilot_rank = data['PilotRank']

                search_string = '"event":"Bounty"'
                if (zeile.find(search_string)) > -1:
                    # data = json.loads(zeile)
                    data = read_json(zeile)
                    b_target = data.get('Target_Localised')
                    if b_target == None:
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
    logger((ranking),2)
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
                system.insert(END, ((str(i[1])) + '\t \t \t \t' + (str(i[2])) + '\n'))
                summe += i[2]
            else:
                system.insert(END, ((str(i[0])) + '\t \t \t \t' + (str(i[2])) + '\n'))
                summe += i[2]
    s = 'Summe', 0, summe
    system.insert(END, ('───────────────────────────\n'))
    system.insert(END, ((str(s[0])) + '\t \t \t \t' + (str(s[2])) + ' \n'))
    system.insert(END, ('───────────────────────────\n'))


def boxel_search(input):
    if input == ' ' or input == '':
        logger('boxel search input-', 2)
    else:
        # url2 = 'https://www.edsm.net/api-v1/systems?systemName=' + urllib.parse.quote(input) + '&showPrimaryStar=1'
        ssl._create_default_https_context = ssl._create_unverified_context
        url_ssl = 'https://www.edsm.net/api-v1/systems?systemName=' + input + '&showPrimaryStar=1'
        url_ssl = url_ssl.replace(' ', '%20')
        show_data_for_system(url_ssl)


def cube_search(data):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    system.delete(1.0, END)
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
    data = Filter.get()
    input = data.split(';')
    edsm_systems = []
    ssl._create_default_https_context = ssl._create_unverified_context
    system.delete(1.0, END)
    with urllib.request.urlopen(url) as f:
        systems = json.load(f)
        if systems == {} or systems == []:
            system.delete(1.0, END)
            system.insert(END, ('EDSM hat keine Einträge in der Nähe gefunden'))
            return
        for i in systems:
            name = (i.get('name'))
            _type = (i.get('primaryStar').get('type'))
            if not _type:
                _type = 'Unknown'
            edsm_systems.append((name, _type))
    if eddc_modul == 7:
        system.insert(END, ('Es gibt ' + str(len(edsm_systems) + 1) +
                            ' Einträge zu diesem Boxel in der EDSM DB'))
    else:
        system.insert(END, ('Es gibt ' + str(len(edsm_systems)) +
                            ' Einträge in einem Kubus von ' + str(input[1]) + ' ly auf EDSM'))
    system.insert(END, ('\n'))

    count = [('Wolf-Rayet', 0), ('Black Hole', 0), ('super giant', 0)]
    boxel_nr = []
    print(edsm_systems)
    for edsm_system in edsm_systems:
        new = edsm_system[0].replace(data,'')
        print(new)
        if '-' not in new:
            if eddc_modul == 7 and new.isnumeric():
                lower_edsm = str(edsm_system[0]).lower()
                lower_data = str(data).lower()
                boxel_nr.append(int(lower_edsm.replace(lower_data, '')))
        for index, c in enumerate(count):
            if c[0] in edsm_system[1]:
                count[index] = c[0], (c[1] + 1)
    system.insert(END, ('\n'))

    for element in count:
        system.insert(END, ((str(element[0])) + ' ' + (str(element[1])) + '\n'))
    system.insert(END, ('\n'))

    check_but = check_auto_refresh.get()

    if check_but == 0:
        for i in edsm_systems:
            system.insert(END, ((str(i[0])) + '\t \t \t' + (str(i[1])) + '\n'))
            boxel_table.add_row(((str(i[0])), (str(i[1]))))
    else:
        if boxel_nr == []:
            system.delete(1.0, END)
            system.insert(END, ('EDSM hat keine Einträge in der Nähe gefunden'))
            return
        boxel_nr.sort()
        last = (boxel_nr[(len(boxel_nr) - 1)])
        x = 0
        new_edsm = []
        while x <= last:
            if x not in boxel_nr:
                new_edsm.append(x)
            x += 1
        system.insert(END, ('Folgende Systeme sind bei EDSM nicht bekannt !!! \n'))
        for new in new_edsm:
            system.insert(END, (data + (str(new)) + '\n'))
            boxel_table.add_row((data + (str(new)), ''))
    return 1


def thargoids():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    system.delete(1.0, END)
    b_filter = Filter.get()
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
            system.insert(END, ((str(i[0])) + '\t \t \t \t' + (str(i[2])) + '\n'))
            summe += int(i[1]) * int(i[2])
    summe = format(summe, ',d')
    s = 'Summe', summe
    system.insert(END, ('───────────────────────────\n'))
    system.insert(END, ((str(s[0])) + '\t \t \t' + (str(s[1])) + ' \n'))
    system.insert(END, ('───────────────────────────\n'))
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
        select_worth = cursor.execute("""select distinct(worth) from codex_entry where data =  ?""",
                                      (i[0],)).fetchall()
        temp = str(select_worth[0][0]).replace(',', '')

        worth += int(temp)
    worth = ((f'{worth:,}').replace(',', '.'))
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
                        (date_log date, time_log timestamp, body_id INTEGER, starsystem TEXT,
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


def check_logfile_in_DB(file, state, read_state):
    funktion = inspect.stack()[0][3]
    logger((funktion, file, state, read_state), log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS logfiles (Name TEXT, explorer INTEGER, "
                       "bgs INTEGER, CMDR TEXT, last_line INTEGER)")
        select = cursor.execute("Select * from logfiles where Name = ? and CMDR is NULL", (file,)).fetchall()
        if select:
            cmdr = check_cmdr(file, '')
        if state == 'line':
            if read_state == '':
                select = cursor.execute("Select last_line from logfiles where Name = ?", (file,)).fetchall()
                if select:
                    if select[0][0] != None:
                        return select[0][0]
                    return 0
                else:
                    return 0
            else:
                sql = "UPDATE logfiles SET last_line = "+ str(read_state) + " where name = '" + file + "';"
                cursor.execute(sql)
                connection.commit()
                return read_state

        if read_state == 'set' or read_state == 'check' :
            sql = "SELECT * from logfiles where Name = '" + file + "' and " + state + " = 1"
            select = cursor.execute(sql).fetchall()

            if select == []:
                if read_state == 'check':
                    return 0
                if read_state == 'set':
                    sql = "UPDATE logfiles SET " + state + " = 1 where name = '" + file + "';"
                    cursor.execute(sql)
                    connection.commit()
                    return 1
            else:
                return 1
        elif read_state == 'insert' :
            sql = "SELECT * from logfiles where Name = '" + file + "';"
            select = cursor.execute(sql).fetchall()
            if select == []:
                cmdr = check_cmdr(file, '')
                cursor.execute("INSERT INTO logfiles (Name, CMDR) VALUES (?, ?)", (file, cmdr))
                connection.commit()


def get_main_and_local(system_id, body_parents, body_name, system_name):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()

        cursor.execute("""CREATE table IF NOT EXISTS star_data 
                            (date_log date, time_log timestamp, body_id INTEGER, starsystem TEXT,
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
        check_logfile_in_DB(filename, '', 'insert')
        if count % 10 == 0:
            system.delete('1.0', END)
            postion = 'File \t' + str(count) + ' of ' + str(len(files))
            system.insert(END, str(postion))
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

        system.delete('1.0', END)
        postion = 'File \t' + str(count + 1) + ' of ' + str(len(files))
        system.insert(END, str(postion))
    rescan_lauf = 0
    t2 = get_time()
    logger(('rescan codex ' + str(timedelta.total_seconds(t2 - t1)) + ' sek.'),1)


def set_fully_read(file, state):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    is_file = os.path.isfile(file)
    if not is_file:
        return

    if os.path.getsize(file) == 0:
        check_logfile_in_DB(file, state, 'set')

        # print(os.path.getsize(file))
    if check_logfile_in_DB(file, state, 'check') != 1:
        with open(file, 'r', encoding='UTF8') as datei_2:
            for zeile in datei_2.readlines()[::-1]:  # Read File line by line reversed!
                data = read_json(zeile)
                # print(data)
                if data.get('event') == 'Shutdown':
                    logger(('------------------ERROR------------------'),1)
                    logger(data, 2)
                    logger(('------------------ERROR------------------'),1)
                    return
                timestamp = data.get('timestamp')
                tod = (log_date(timestamp))
                date_log = date((int(tod[0])), int(tod[1]), int(tod[2]))
                yesterday = date.today() - timedelta(days=1)

                if date_log <= yesterday:
                    # print('SET ---')
                    check_logfile_in_DB(file, state, 'set')
                break
    else:
        logger(('already Fully_read'), 1)


def full_scan():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS logfiles (Name TEXT, explorer INTEGER, "
                       "bgs INTEGER, CMDR TEXT, last_line INTEGER)")
        select = cursor.execute("select Name from logfiles where explorer is NULL").fetchall()
    global fully
    if select and fully == 0:
        fully = 1
        length = (len(select) - 2)
        logger((select[length][0], funktion), 2)
        global linenr
        linenr = 0
        tail_file(select[length][0])
        if check_logfile_in_DB(select[length][0], 'explorer', 'check') != 1:
            set_fully_read(select[length][0], 'explorer')
            time.sleep(0.1)
            fully = 0
        else:
            # print('done')
            time.sleep(0.1)
            fully = 0


def summary():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    text = []
    files = file_names(0)  # Logs einlesen nach Datum der Eingabe
    if len(files) > 0:
        last = files[len(files) - 1]
    else:
        last = files
    if last == []:
        return
    cmdr = read_cmdr(last)
    text.append('Hallo CMDR ' + cmdr)
    for filename in files:
        check_cmdr(filename, '')
        varia = check_logfile_in_DB(filename, 'explorer', 'check')
        if varia != 1:
            with open(filename, 'r', encoding='UTF8') as datei:
                for count, zeile in enumerate(datei):
                    data = read_json(zeile)
                    event = data.get('event')
                    match event:
                        case 'Location':
                            set_system(data, cmdr)
                        case 'Commander':
                            cmdr = data['Name']
                            check_cmdr(filename, cmdr)
                        case 'Scan':
                            get_info_for_get_body_name(data)  # star_map
                            if data.get('StarType'):
                                get_all_stars(data)
                            if data.get('ScanType') and not data.get('StarType'):
                                get_planet_info(data)
                        case 'ScanOrganic':
                            read_bio_data(data, filename)
                        case 'ScanBaryCentre':
                            get_bary(data)
                        case 'FSDJump':
                            set_main_star(data)
                            set_system(data, cmdr)
                        case 'StartJump':
                            if data.get('JumpType') == "Hyperspace":
                                get_star_info(data)
                        case 'ScanOrganic':
                            get_info_for_bio_scan(data, filename)
                            read_bio_data(data, filename)
                        case 'CodexEntry':
                            read_log_codex(data, filename)
                        case 'FSSBodySignals':
                            get_info_scan_planets(data)
                        case 'SAASignalsFound':
                            get_info_scan_planets(data)
                        case 'Shutdown':
                            check_logfile_in_DB(filename, 'explorer', 'set')

    day = Tag.get()
    month = Monat.get()
    year = Jahr.get()
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
    funktion = inspect.stack()[0][3] + ' eddc_modul ' + str(eddc_modul)
    logger(funktion, log_var)

    create_tables()
    # system.delete(.0, END)
    check_but.config(text='Autorefresh    ')

    if eddc_modul == 10:  # Reset Position
        b_filter = Filter.get()
        reset_pos()
        # status.config(text='Test')
        return

    if eddc_modul == 11:  # Boxel Analyser
        b_filter = Filter.get()
        summary()
        status.config(text='Summary')
        return

    if eddc_modul == 12:  # Test
        b_filter = Filter.get()
        t1 = get_time()
        war_progress()
        t2 = get_time()
        logger(('war_progress   ' + str(timedelta.total_seconds(t2 - t1))), 1)
        status.config(text='War Progress')
        return

    if eddc_modul == 7:  # Boxel Analyser
        b_filter = Filter.get()
        check_but.config(text='reverse         ')
        boxel_search(b_filter)
        status.config(text='Boxel Analyse')
        return

    elif eddc_modul == 9:  # Thargoid WAR
        status.config(text='Thargoid-War')
        war()
        return

    if eddc_modul == 8:  # Sphere Analyser
        b_filter = Filter.get()
        check_but.config(text='reverse         ')
        cube_search(b_filter)
        status.config(text='Kubus Analyse')
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
            status.config(text='Codex')
            filenames = file_names(1)  # Alle Logfile werden geladen
            last_log = (len(filenames))
            files = check_last_logs(filenames, last_log)
            run_once_rce(files)
            # treeview_codex()
        else:
            system.delete(.0, END)
            system.insert(END, 'Keine Log-Files für den Tag vorhanden')
    else:
        if eddc_modul == 1:  # BGS Main
            status.config(text='BGS Mode')
            star_systems_db(filenames)
            filenames = file_names(0)
            for filename in filenames:
                check_logfile_in_DB(filename, '', 'insert')
                if check_logfile_in_DB(filename, 'bgs', 'read') != 1:
                    einfluss_auslesen(filename)
                    # ground_combat(filename)
                    redeem_voucher(filename)
                    multi_sell_exploration_data(filename)
                    market_sell(filename)
            b_filter = Filter.get()
            system.delete(.0, END)
            data = print_vouchers_db(b_filter)
            if data:
                system.insert(END,
                              '    ----------    Bounty, Bonds, ExplorerData and Trade    ----------\n\n')
                for i in data:
                    tmp = f"{i[3]:,}"
                    tmp = tmp.replace(',', '.')
                    tmp = tmp + ' Cr'
                    system.insert(END, ((str(i[1])[0:15]) + '\t\t' + (str(i[2])[0:25]) + '\t\t\t' + (str(i[0])[0:15])
                                        + '\n\t\t\t\t\t' + tmp + '\n'))
                    voucher.add_row((i[0], i[1], i[2], tmp))
                    nodata = 0
            else:
                nodata_voucher = 1
                logger('NO VOUCHER DATA', log_var)

            # data = print_combat_zone()
            # if data:
            #     system.insert(END,
            #                   (
            #                       '\n    ---------------------------  Bodenkampfzonen  '
            #                       '-----------------------------\n'))
            #     system.insert(END, '\n')
            #     for i in data:
            #         system.insert(END, ((str(i[0])) + '\t\t' + (str(i[1])) + '\t\t\t' +
            #                             str(i[3]) + ' x ' + str(i[2])+ '\n'))
            #         ground_cz_table.add_row((i[0], i[1], i[2], i[3]))
            # # else:
            # #     logger('NO INFLUENCE DATA', 2)
            # #     if nodata == 1:
            # #         system.insert(END, '\n\tKeine Daten vorhanden')

            failed_mission()  # update auf die influence tabelle
            data = print_influence_db(b_filter)
            # print(data)
            if data:
                system.insert(END,
                              (
                                  '\n    -----------------------------------  Einfluss  '
                                  '-----------------------------------\n'))
                system.insert(END, '\n')
                for i in data:
                    system.insert(END, ((str(i[0])[0:15]) + '\t\t' + (str(i[1])[0:25]) + '\t\t\t\t' + str(i[2]) + '\n'))
                    bgs.add_row((i[0], i[1], i[2]))
                nodata = 0
            else:
                nodata = 1
            if nodata == 1 and nodata_voucher == 1:
                system.delete(.0, END)
                system.insert(END, 'Keine Daten vorhanden Überprüfe den Tick')

        elif eddc_modul == 3:  # Collected Enginieering Material
            status.config(text='MATS Mode')
            star_systems_db(filenames)
            for filename in filenames:
                mats_auslesen(filename)
            b_filter = Filter.get()
            data = print_engi_stuff_db(b_filter)
            summe = 0
            system.delete(.0, END)
            for i in data:
                system.insert(END, ((str(i[0]).capitalize()) + '\t \t \t \t \t' + (str(i[1])) + '\n'))
                mats_table.add_row((i[0], i[1]))
                summe += i[1]
            a = 'Summe', summe
            system.insert(END, ('─────────────────────────────────\n'))
            system.insert(END, ((str(a[0])) + '\t \t \t \t \t' + (str(a[1])) + '\n'))
            system.insert(END, ('─────────────────────────────────\n'))

        elif eddc_modul == 2:  # Collected Odyssey on Foot Material
            status.config(text='Odyssey MATS')
            star_systems_db(filenames)
            for filename in filenames:
                ody_mats_auslesen(filename)
            b_filter = Filter.get()
            data = print_engi_stuff_db(b_filter)
            summe = 0
            system.delete(.0, END)
            for i in data:
                system.insert(END, ((str(i[0])) + '\t \t \t \t' + (str(i[1])) + '\n'))
                mats_table.add_row((i[0], i[1]))
                summe += i[1]
            a = 'Summe', summe
            system.insert(END, ('───────────────────────────\n'))
            system.insert(END, ((str(a[0])) + '\t \t \t \t' + (str(a[1])) + '\n'))
            system.insert(END, ('───────────────────────────\n'))

        elif eddc_modul == 4:  # Codex Treeview
            status.config(text='Codex')
            run_once_rce(filenames)

        elif eddc_modul == 5:  # Kampfrang
            status.config(text='Combat Rank')
            combat_rank()

        elif eddc_modul == 6:  # Thargoid
            status.config(text='Thargoids')
            thargoids()


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


def update_db(old_version):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    sql = """Insert into Bio_prediction VALUES 
            ('bacterium bullaris', 'm', 'icy body', 0.001, 0.099,0.03,0.6,'thin methane',65.0,110.0,'N')"""

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()

        select = cursor.execute("""SELECT * from Bio_prediction where name = 'bacterium bullaris' and startype = 'm' 
                                    and Planettype = 'rocky ice body' and Athmospere 
                                    like '%thin methane%' and Temp_max = 110""").fetchall()
        if not select:
            print('UPDATE SQL')
            item = cursor.execute(sql)
            connection.commit()

    if old_version == '0.7.2.0' or old_version == '0.7.2.1' or old_version == '0.7.2.2':
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            cursor.execute("ALTER TABLE logfiles ADD last_line INTEGER")
        connection.commit()

    if old_version == '0.7.1.3' or old_version == '0.7.1.2' :
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            cursor.execute("ALTER TABLE logfiles ADD last_line INTEGER")
            cursor.execute("ALTER TABLE logfiles ADD explorer INTEGER")
            cursor.execute("ALTER TABLE logfiles ADD bgs INTEGER")
            cursor.execute("ALTER TABLE logfiles ADD CMDR TEXT")
            cursor.execute("DROP TABLE planet_infos")
        connection.commit()
    logger('update DB', 1)
    create_tables()


def db_version():  # Programmstand und DB Stand werden mit einander verglichen
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        item = cursor.execute("SELECT version FROM db_version").fetchall()
        # print(item[0][0], version_number)
        if not item:
            cursor.execute("INSERT INTO db_version VALUES (?)", (version_number,))
            connection.commit()
        elif item[0][0] != version_number:
            cursor.execute("UPDATE db_version set version = ?", (version_number,))
            connection.commit()
            logger('Update Version', 2)
            update_db(item[0][0])
            # connection.commit()
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


def upd_server():
    # print('change state')
    # print(update_server.get())
    upd_srv = update_server.get()
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute("""UPDATE server set upload = ?""", (upd_srv,))
        connection.commit()


def new_main():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    select = set_language_db('leer')
    if not select or select[0][0] == 'german' or select == 'leer':
        text = ['Tag', 'Monat', 'Jahr', 'Der letzte Tick war um:', 'vor dem Tick', 'nach dem Tick']
    else:
        text = ['Day', 'Month', 'Year', 'Last BGS TICK was at  ', 'before Tick', 'after Tick']

    root = tb.Window(themename="darkly")

    root.title('Elite Dangerous Data Collector')
    img = resource_path("eddc.ico")
    root.iconbitmap(img)
    root.minsize(415, 500)
    root.maxsize(415, 1440)
    root.config(background='black')
    snpx = resource_path("SNPX.png")
    horizon = resource_path("Horizon.png")
    bg = PhotoImage(file=snpx)
    bg2 = PhotoImage(file=horizon)
    my_style = tb.Style()
    my_menu = Menu(root)
    root.config(menu=my_menu)
    file_menu = Menu(my_menu, tearoff=False)
    my_menu.add_cascade(label="Statistik", menu=file_menu)
    file_menu.add_command(label="BGS", command=lambda: menu('BGS'))

    my_top_logo = tb.Label(root, image=bg, border=0)
    my_top_logo.pack()
    my_style.configure('TFrame', background='black')
    my_style.configure('TLabel', background='black')

    top_frame = tb.Frame(master=root, bootstyle='black', style='TFrame')
    top_frame.pack(padx=10)

    buttom_frame = tb.Frame(master=root, bootstyle='black', width=410, height=350, style='TFrame')
    buttom_frame.pack()

    top_left_frame = tb.Frame(master=top_frame, bootstyle='black', width=250, height=100, style='TFrame')
    top_left_frame.grid(column = 0, row = 0, pady=5, padx=10)

    top_left_frame_line_1 = tb.Frame(master=top_left_frame, bootstyle='black', width=250, height=50, style='TFrame')
    top_left_frame_line_1.grid(column=0, row=0, pady=5)

    top_left_frame_line_2 = tb.Frame(master=top_left_frame, bootstyle='black', width=250, height=50, style='TFrame')
    top_left_frame_line_2.grid(column=0, row=1, pady=5)

    Day, Month, Year = '07', '04', '2023'
    label_tag = tb.Label(master=top_left_frame_line_1, text=text[0], font=("Helvetica", 12), style='TLabel')
    label_tag.grid(column=0, row=0)
    Tag = tb.Entry(master=top_left_frame_line_1, width=2, font=("Helvetica", 12))
    Tag.insert(0, Day)
    Tag.grid(column=1, row=0, padx=5)
    label_monat = tb.Label(master=top_left_frame_line_1, text=text[1], font=("Helvetica", 12))
    label_monat.grid(column=2, row=0, padx=5)
    Monat = tb.Entry(master=top_left_frame_line_1, width=2, font=("Helvetica", 12))
    Monat.insert(0, Month)
    Monat.grid(column=3, row=0, padx=1)
    label_jahr = tb.Label(master=top_left_frame_line_1, text="Jahr:",  font=("Helvetica", 12))
    label_jahr.grid(column=4, row=0, padx=5)
    Jahr = tb.Entry(master=top_left_frame_line_1, width=4, font=("Helvetica", 12))
    Jahr.insert(0, Year)
    Jahr.grid(column=5, row=0)

    last_tick_label = tb.Label(master=top_left_frame_line_2, text=text[3], font=("Helvetica", 12), justify=LEFT)
    last_tick_label.grid(column=0, row=0, padx=5)

    last_t = last_tick()  # [t_year, t_month, t_day, t_hour, t_minute]

    t_hour, t_minute = last_t[3], last_t[4]

    tick_hour_label = tb.Entry(master=top_left_frame_line_2, width=2, font=("Helvetica", 12))
    tick_hour_label.insert(0, str(t_hour))
    tick_hour_label.grid(column=1, row=0, padx=2)

    label_colon = tb.Label(master=top_left_frame_line_2,
                        text=""":""", font=("Helvetica", 12),
                        justify=LEFT)
    label_colon.grid(column=2, row=0, padx=2)

    tick_minute_label = tb.Entry(master=top_left_frame_line_2, width=2, font=("Helvetica", 12))
    tick_minute_label.insert(0, str(t_minute))
    tick_minute_label.grid(column=3, row=0, padx=2)

    top_right_frame = tb.Frame(master=top_frame, bootstyle='black', width=150, height=100)
    top_right_frame.grid(column=1, row=0)

    # my_style.configure('success.TCheckbutton', font=('Helvetica', 6))
    my_style.configure('success.TCheckbutton', font=('Helvetica', 12), background='black')
    my_style.configure('link.TButton', font=('Helvetica', 12), background='black')
    my_style.configure('danger.Link.TButton', font=('Helvetica', 12), background='black')

    tick_var = IntVar()

    def toggle_text():
        print('pressed')
        current_text = tick_but.cget("text")
        if current_text == "before Tick":
            tick_but.config(text="after Tick", style='danger.Link.TButton')
        else:
            tick_but.config(text="before Tick", style='link.TButton')

    check_auto_refresh = IntVar()

    check_but = tb.Checkbutton(master=top_right_frame,
                               bootstyle="square-toggle",
                               text="Autorefresh    ",
                               variable=check_auto_refresh,
                               onvalue=1,
                               offvalue=0,
                               style='success.TCheckbutton')

    check_but.grid(column=0, row=0, sticky=W, pady=10)


    tick_but = tb.Button(master=top_right_frame,
                              bootstyle="success-square-toggle",
                              text="before Tick",
                              style='TButton',
                              command=toggle_text)

    tick_but.grid(column=0, row=1, sticky=W, pady=10)

    # v = IntVar()
    # vor_tick = tb.Radiobutton(master=top_right_frame,
    #                           bootstyle="success",
    #                           text=text[4],
    #                           variable=v,
    #                           value=1,
    #                           command=tick_false)
    #
    # vor_tick.grid(column=0, row=1, sticky=W, pady=5)
    #
    # nach_tick = tb.Radiobutton(master=top_right_frame,
    #                         bootstyle="success",
    #                         text=text[5],
    #                         variable=v,
    #                         value=2,
    #                         command=tick_true)
    # nach_tick.grid(column=0, row=2, sticky=W, pady=5)
    # # nach_tick.select()

    root.mainloop()


def main():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    global system, root, Tag, Monat, Jahr, tick_hour_label, tick_minute_label, eddc_modul, ody_mats, \
        vor_tick, nach_tick, Filter, tree, check_but  # , label_tag, label_monat, label_jahr

    select = set_language_db('leer')
    if not select or select[0][0] == 'german' or select == 'leer':
        text = ['Tag', 'Monat', 'Jahr', 'Der letzte Tick war um:', 'vor dem Tick', 'nach dem Tick']
    else:
        text = ['Day', 'Month', 'Year', 'Last BGS TICK was at  ', 'before Tick', 'after Tick']

    # ------- root -----
    root = Tk()
    root.title('Elite Dangerous Data Collector')

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

    def save_position():
        position = {
            "x": root.winfo_x(),
            "y": root.winfo_y()
        }
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE eddc_positions SET x = ? , y = ? where id = 1", (position["x"], position["y"]))
            connection.commit()

    def load_position():
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT x, y FROM eddc_positions where id = 1")
            position = cursor.fetchone()
            if position:
                root.geometry("+{}+{}".format(position[0], position[1]))

    load_position()
    root.bind("<Configure>", lambda event: save_position())

    def on_closing():
        save_position()
        # for thread in threading.enumerate():
        #     print(thread.name, ' MAIN')
        try:
            print('waiting')
            treeview_loop.wait()
        except:
            pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    try: # read icon file
        img = resource_path("eddc.ico")
        root.iconbitmap(img)
    except TclError:
        logger(('Icon not found)'), 1)
    root.configure(background='black')
    root.minsize(415, 500)
    root.maxsize(415, 1440)
    snpx = resource_path("SNPX.png")
    horizon = resource_path("Horizon.png")
    bg = PhotoImage(file=snpx)
    bg2 = PhotoImage(file=horizon)

    # ------------- menu Leiste -----------------
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
    exploration_menu.add_command(label="Kubus Anylyse", command=lambda: menu('cube'))
    exploration_menu.add_command(label="Rescan Codex", command=rescan)

    settings_menu = Menu(my_menu, tearoff=False)
    settings_menu.add_cascade(label="Server Einrichtung", command=lambda: server_settings())
    my_menu.add_cascade(label="Setting", menu=settings_menu)
    about_menu = Menu(my_menu, tearoff=False)
    my_menu.add_cascade(label="About", menu=about_menu)
    about_menu.add_command(label="Version Check", command=lambda: get_latest_version(0))
    about_menu.add_command(label="Delete all Data in DB", command=lambda: delete_all_tables())
    about_menu.add_command(label="Reset Window", command=lambda: menu('reset_pos') , accelerator="Ctrl+w")
    about_menu.bind_all("<Control-w>", lambda e: menu('reset_pos'))

    top_blank = Label(root, bg='black', height=5)
    top_blank.pack(padx=20, pady=10, fill=X)

    top_text = Label(root, bg='black', height=5)
    top_text.pack(padx=15, pady=5, fill=X)
    #
    my_text_box = Frame(top_text, bg='black')
    my_text_box.grid(column=0, row=0)

    my_check_box = Frame(top_text, bg='black')
    my_check_box.grid(column=1, row=0)

    my_top_logo = Label(root, image=bg, bg='black')
    my_top_logo.place(x=15, y=0)

    # --------------------------------- my_time_label -----------------------------------

    my_time_label = Frame(my_text_box, bg='black')
    my_time_label.pack(pady=5, fill=X)
    my_time_label.config(highlightbackground='black')

    label_tag = Label(my_time_label, text=text[0], bg='black', fg='white', font=("Helvetica", 12))
    label_tag.grid(column=0, row=0)
    Tag = Entry(my_time_label, width=2, font=("Helvetica", 12))
    Tag.insert(0, Day)
    Tag.grid(column=1, row=0, padx=5)
    label_monat = Label(my_time_label, text=text[1], bg='black', fg='white', font=("Helvetica", 12))
    label_monat.grid(column=2, row=0, padx=5)
    Monat = Entry(my_time_label, width=2, font=("Helvetica", 12))
    Monat.insert(0, Month)
    Monat.grid(column=3, row=0, padx=5)

    label_jahr = Label(my_time_label, text="Jahr:", bg='black', fg='white', font=("Helvetica", 12))
    label_jahr.grid(column=4, row=0, padx=5)
    Jahr = Entry(my_time_label, width=2, font=("Helvetica", 12))
    Jahr.insert(0, Year)
    Jahr.grid(column=5, row=0, padx=5)

    global check_auto_refresh, last_tick_label

    bgs_tick_frame = Frame(my_text_box, bg='black', borderwidth=2)
    # bgs_tick_frame = Frame(my_text_box, bg='black')
    bgs_tick_frame.pack(side=LEFT, pady=5)
    last_tick_label = Label(bgs_tick_frame, text=text[3], bg='black', fg='white', font=("Helvetica", 12), justify=LEFT)
    last_tick_label.grid(column=0, row=0)

    # my_tick
    last_t = last_tick() #[t_year, t_month, t_day, t_hour, t_minute]

    t_hour, t_minute = last_t[3], last_t[4]
    my_tick = Frame(bgs_tick_frame, bg='black')
    my_tick.grid(column=1, row=0)

    tick_hour_label = Entry(my_tick, width=2, font=("Helvetica", 12))
    tick_hour_label.insert(0, str(t_hour))
    tick_hour_label.grid(column=0, row=0)
    label_colon = Label(my_tick,
                        text=""":""", bg='black', fg='white', font=("Helvetica", 12),
                        justify=LEFT)
    label_colon.grid(column=2, row=0)

    tick_minute_label = Entry(my_tick, width=2, font=("Helvetica", 12))
    tick_minute_label.insert(0, str(t_minute))
    tick_minute_label.grid(column=3, row=0)

    my_boxes = Frame(my_check_box, bg='black', borderwidth=2)
    my_boxes.pack(padx=20)
    check_auto_refresh = IntVar()

    check_but = Checkbutton(my_boxes, text="Autorefresh    ",
                            variable=check_auto_refresh,
                            bg='black',
                            fg='white',
                            selectcolor='black',
                            activebackground='black',
                            activeforeground='white',
                            command=threading_auto,
                            font=("Helvetica", 10))
    check_but.grid(column=0, row=0, sticky=W)

    v = IntVar()
    vor_tick = Radiobutton(my_boxes,
                           text=text[4], bg='black', fg='white', selectcolor='black',
                           activebackground='black', activeforeground='white',
                           # padx=10,
                           variable=v,
                           value=1, command=tick_false)
    vor_tick.grid(column=0, row=1, sticky=W)

    nach_tick = Radiobutton(my_boxes,
                            text=text[5], bg='black', fg='white', selectcolor='black',
                            activebackground='black', activeforeground='white',
                            # padx=10,
                            variable=v,
                            value=2, command=tick_true)
    nach_tick.grid(column=0, row=2, sticky=W)
    nach_tick.select()

    my_folder = Frame(root, bg='black', border=2)
    my_folder.pack(fill=X, padx=20)
    myfolder_grid = Frame(my_folder, bg='black')
    myfolder_grid.grid(sticky=W)

    label_filter = Label(myfolder_grid,
                         text="Filter:",
                         bg='black',
                         fg='white',
                         font=("Helvetica", 12))
    label_filter.grid(column=0, row=0, sticky=W)
    Filter = Entry(myfolder_grid, width=37, font=("Helvetica", 10))

    Filter.insert(0, filter_name)
    Filter.grid(column=0, row=0)

    folder = Entry(myfolder_grid, width=60, bg='black', fg='white', font=("Helvetica", 8))
    folder.insert(END, path)
    folder.grid(column=0, row=1, pady=5)

    system = Text(root, height=10, width=10, bg='black', fg='white', font=("Helvetica", 10))
    system.pack(padx=10, expand=True, fill="both")

    bottom_grid = Frame(root, bg='black')
    bottom_grid.pack(pady=10)

    version_but = Button(bottom_grid,
                         text=current_version,
                         activebackground='#000050',
                         activeforeground='white',
                         bg='black',
                         fg='white',
                         command=logging,
                         font=("Helvetica", 10))
    version_but.grid(column=0, row=0, sticky=W, padx=5)

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
        # cursor.execute("""SELECT * FROM server""")
        # result = cursor.fetchall()
        if result != []:
            eddc_user = result[0][2]
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

    clipboard = Button(bottom_grid,
                       text='Cp2Clip',
                       activebackground='#000050',
                       activeforeground='white',
                       bg='black',
                       fg='white',
                       command=cp_to_clipboard,
                       font=("Helvetica", 10))
    clipboard.grid(column=1, row=0, sticky=W, padx=5)

    discord = Button(bottom_grid,
                     text='Discord',
                     activebackground='#000050',
                     activeforeground='white',
                     bg='black',
                     fg='white',
                     command=cp_to_discord,
                     font=("Helvetica", 10))
    discord.grid(column=2, row=0, sticky=W, padx=10)

    global status
    status = Label(bottom_grid, text='BGS Mode',
                   activebackground='#000050',
                   activeforeground='white',
                   width=12,
                   border=10,
                   bg='black',
                   fg='yellow',
                   font=("Helvetica", 10, 'bold'),
                   bd=2)
    # relief=SUNKEN)
    status.grid(column=3, row=0, sticky=W, padx=5)

    ok_but = Button(bottom_grid,
                    # width=4,
                    activebackground='#000050',
                    activeforeground='white',
                    text='OK',
                    bg='black',
                    fg='white',
                    command=threading_auto,
                    font=("Helvetica", 10))
    ok_but.grid(column=4, row=0, sticky=W, padx=5)

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
        root.destroy()
        main()

    settings_menu.add_command(label="Sprache - Deutsch", command=lambda: set_language(1))
    settings_menu.add_command(label="Language - English", command=lambda: set_language(2))
    get_latest_version(1)
    # for thread in threading.enumerate():
    #     print(thread.name, ' MAIN')

    root.mainloop()

# last_tick()

main()
# new_main()