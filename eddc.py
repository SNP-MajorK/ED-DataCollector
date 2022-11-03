# Created by MajorK https://github.com/SNP-MajorK/ED-DataCollector

import glob
import inspect
import os
import sqlite3
import threading
import time
import webbrowser
from builtins import print
from datetime import date, timedelta, datetime
from pathlib import Path
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from winreg import *

import requests
from PIL import ImageTk, Image
from prettytable import PrettyTable

import RegionMapData
from RegionMap import *

# import json

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
version_number = '0.7.0.2'
current_version = ('Version ' + str(version_number))
bgs = PrettyTable(['System', 'Faction', 'Influence'])
voucher = PrettyTable(['Voucher', 'System', 'Faction', 'Credits'])
mats_table = PrettyTable(['Materials', 'Count'])

# Set Program Path Data to random used Windows temp folder.
with OpenKey(HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders") as key:
    value = QueryValueEx(key, '{4C5C32FF-BB9D-43B0-B5B4-2D72E54EAAA4}')

# path = value[0] + '\\Frontier Developments\\Franky'
path = value[0] + '\\Frontier Developments\\Elite Dangerous\\'
# path = value[0] + '\\Frontier Developments\\Test'

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


database = resource_path("eddc.db")


def logger(funktion, schwelle):
    if schwelle > 0:
        # print('function', end = ' ')
        print(funktion)


def get_latest_version(var):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    try:
        response = requests.\
            get("https://raw.githubusercontent.com/SNP-MajorK/ED-DataCollector/codex_testing/version.json"
                , timeout=1)
        my_json = json.loads(response.text)
        # my_json = json.loads('[{"version": "1.0.0.0", "hyperlink": "link"}]')
    except requests.exceptions.ConnectionError:
        my_json = json.loads('[{"version": "0.0.0.0", "hyperlink": "link"}]')
        messagebox.showwarning("Check failed", "No Internet Connection")
    db_version()

    for d in my_json:
        online_version = d['version']
        link = d['hyperlink']
        online_version = online_version.replace('.','')
        cur_version = version_number.replace('.','')
        if cur_version == online_version:
            logger('no update needed', 1)
            if var != 1:
                messagebox.showinfo("No Update available", ("Already newest Version " + online_version))
        elif int(online_version) > int(cur_version):
            box = messagebox.askyesno("Update available", "New Version available\nOpen Downloadpage")
            if box:
                webbrowser.open(link, new=0, autoraise=True)


def last_tick():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    try:
        response = requests.get("https://elitebgs.app/api/ebgs/v5/ticks", timeout=3)
        todos = json.loads(response.text)
    except requests.exceptions.ConnectionError:
        print('Tick Error')
        todos = json.loads('[{"_id":"627fe6d6de3f1142b60d6dcd",'
                           '"time":"2022-05-14T16:56:36.000Z",'
                           '"updated_at":"2022-05-14T17:28:54.588Z",'
                           '"__v":0}]')
        messagebox.showwarning("TICK failed", "No Internet Connection")

    #

    # todos = json.loads(response.text)
    global t_hour
    global t_minute
    global tick_time
    for d in todos:
        lt_date = d['time']
        t_year = (lt_date[:4])
        t_month = (lt_date[5:7])
        t_day = (lt_date[8:10])
        t_hour = str(lt_date[11:13])
        t_minute = str(lt_date[14:16])
        tick_time = [t_year, t_month, t_day, t_hour, t_minute]


def file_names(var):
    # Changes because of new naming of logfiles!
    funktion = inspect.stack()[0][3] + ' Var = '+ str(var)
    logger(funktion, log_var)

    update_eleven = datetime(2022, 3, 14)
    tag2 = Tag.get()
    if len(tag2) < 2:
        return
    if len(tag2) > 2:
        tag2 = tag2[0:2]
    tag2 = str(int(tag2) - var).zfill(2)
    monat2 = Monat.get()
    jahr2 = Jahr.get()
    if var == 0: # Logs von dem Tag
        search_date = datetime(int("20" + jahr2), int(monat2), int(tag2))
        if search_date > update_eleven:
            journal_date = ("20" + str(jahr2) + "-" + str(monat2) + "-" + str(tag2) + "T")
            files = glob.glob(path + "\\Journal." + journal_date + "*.log")
            return files
        else:
            journal_date = str(jahr2 + monat2 + tag2)
            filenames = glob.glob(path + "\\Journal." + journal_date + "*.log")
            logger(filenames, 4)
            return filenames

    elif var == 1: # Alle Logfiles
        filenames = glob.glob(path + "\\Journal.*.log")
        fils = (glob.glob(path + "\\Journal.202*.log"))
        for i in fils:
            filenames.remove(i)
        for i in fils:
            filenames.append(i)
        return filenames
        # print(update_eleven)
    elif var == 2: # Logs von Gestern, Heute & ggf. Morgen
        yesterday = str(datetime.now() - timedelta(days=1))[0:10]
        today = str(datetime.now())[0:10]
        tomorrow =  str(datetime.now() + timedelta(days=1))[0:10]
        filenames = glob.glob(path + "\\Journal." + yesterday + "*.log")
        files_tod = glob.glob(path + "\\Journal." + today + "*.log")
        files_tom = glob.glob(path + "\\Journal." + tomorrow + "*.log")
        for i in files_tod:
            filenames.append(i)
        for i in files_tom:
            filenames.append(i)
        # print(filenames)
    return filenames

global linenr
linenr = 0


def tail_file(file):
    funktion = inspect.stack()[0][3]
    logger(funktion, 3)

    # print(file)
    global linenr
    a = linenr
    with open(file, 'r', encoding='UTF8') as datei:
        for count, zeile in enumerate(datei):
            linenr = a
            if linenr < count:
                # print(linenr, count)
                data = read_json(zeile)
                if data.get('event') == 'Commander':
                    cmdr = data['Name']
                if data.get('event') == 'StartJump'and data.get('JumpType') == "Hyperspace":
                    get_star_info(data)
                if data.get('event') == 'Scan':
                    get_info_for_get_body_name(data)
                if data.get('event') == 'ScanOrganic':
                    get_info_for_bio_scan(data)
                if data.get('event') == 'FSSDiscoveryScan':
                    get_info_for_system_Scan(data)
                if data.get('event') == 'FSSBodySignals':
                    get_info_scan_planets(data)
                if data.get('event') == 'Scan' and data.get('ScanType') == 'Detailed' and data.get('Landable'):
                    get_planet_info(data)
            linenr = count
        print(linenr)
    if a != linenr:
        return 1
    else:
        return 0

global data_old
data_old = None

def start_read_logs():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    files = file_names(2)
    # print('files = file_names(0)')

    if len(files) > 0:
        last = files[len(files) - 1]
    else:
        return

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("CREATE table IF NOT EXISTS logfiles (Name TEXT)")
    item = cursor.execute("SELECT Name FROM logfiles WHERE Name = ?", (last,)).fetchall()
    if not item:
        cursor.execute("INSERT INTO logfiles VALUES (?)", (last,))
        connection.commit()

        global linenr
        linenr = 0

    connection.close()

    data = None
    global data_old
    logger(last, 15)
    if tail_file(last) != 0:
        data = get_data_from_DB(last)
    if data != None:
        # print(data)
        data_old = data
    if data == None and data_old != None:
        data = data_old
        print('Benutze alte Daten, da es keine neuen gibt ????')

    # print('data_old' , data_old)
    # print('data' , data)
    if data == None and data_old == None:
        print('no new log files')
        data = read_data_from_last_system(last)
        data_old = data
    current_system = system_scan(last)
    if current_system[0] not in data[0][0]:
        data = None

    return data


def date_for_ma(mission_id, gmd_faction, x):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    mission_found = False
    while x < 7:
        filenames = file_names(0)
        for filename in filenames:
            if get_mission_data(mission_id, filename, gmd_faction):
                mission_found = True
                return mission_found
        x += 1


def get_mission_data(mission_id, journal_file, gmd_faction):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    global inf_data, docked
    docked = ''
    inf_data = ''
    ma_zeile = 0
    d_zeile = 0
    d_system = []
    # print(journal_file)
    with open(journal_file, 'r', encoding='UTF8') as datei:
        with open(journal_file, 'r', encoding='UTF8') as d_datei:
            for gmd_zeile in datei:
                ma_zeile += 1
                gmd_mission_id = str(mission_id)
                gmd_search_string = 'MissionAccepted'
                if (gmd_zeile.find(gmd_search_string)) > -1:
                    # print('suche nach Mission ID ' + gmd_mission_id)
                    if (gmd_zeile.find(gmd_mission_id)) > -1:
                        mission_found = True
                        # print('gefunden ' + gmd_mission_id)
                        data = json.loads(gmd_zeile)
                        # print(data)
                        if str(data['Faction']) == str(gmd_faction):
                            inf_data = (data['Influence'])
                            if mission_found:
                                for D_zeile in d_datei:
                                    d_zeile += 1
                                    gmd_search_docked = 'Docked'
                                    if (D_zeile.find(gmd_search_docked)) > -1:
                                        d_data = json.loads(D_zeile)
                                        docked_data = (d_data['SystemAddress'])
                                        if d_zeile < ma_zeile:
                                            d_system.append(docked_data)
                                docked = d_system[-1]
                                # print(str(gmd_mission_id) + " " + str(docked))
                                return docked
                        else:
                            docked = ''
                            return docked
                    else:
                        mission_found = False


def get_faction_for(system_address):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    filenames = file_names(0)
    for filename in filenames:
        with open(filename, 'r', encoding='UTF8') as datei:
            line = 0
            for zeile in datei:
                line += 1
                search_string = "FSDJump"
                if (zeile.find(search_string)) > -1:
                    data = read_json(zeile)
                    faction = (data['SystemFaction']['Name'])
                    return faction


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


def extract_data(data):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    try:
        for p in data["FactionEffects"]:
            if p['Faction'] != '':
                ed_faction = (p['Faction'])
                mission_id = data['MissionID']
                if not p['Influence']:
                    # print("extract_data no Data in p['Influence']")
                    mission_found = False
                    date_for_ma(mission_id, ed_faction, 0)
                    if docked:
                        p['Influence'] = [{'SystemAddress': docked, 'Trend': 'UpGood', 'Influence': inf_data}]
                    else:
                        p['Influence'] = [{'SystemAddress': docked, 'Trend': 'UpGood', 'Influence': ''}]
                extract_influence(p)


    except KeyError:
        logger('extract_data  - exception',log_var)
        ed_faction = (data['Faction'])
        mission_id = data['MissionID']
        date_for_ma(mission_id, ed_faction, 0)
        data['Influence'] = [{'SystemAddress': docked, 'Trend': 'UpGood', 'Influence': inf_data}]

        extract_influence(data)
    # ================================ End of extract_data


def extract_influence(data):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    for xx in data['Influence']:
        if xx['Trend'] == 'UpGood':
            if not read_influence_db(xx['SystemAddress'], data['Faction']):
                influence_db(xx['SystemAddress'], data['Faction'], len(xx['Influence']))
            else:
                # print(xx['SystemAddress'], data['Faction'], len(xx['Influence']))
                update_influence_db(xx['SystemAddress'], data['Faction'], len(xx['Influence']))
        if xx['Trend'] == 'DownBad':
            if not read_influence_db(xx['SystemAddress'], data['Faction']):
                influence_db(xx['SystemAddress'], data['Faction'], (len(xx['Influence']) * (-1)))
            else:
                update_influence_db(xx['SystemAddress'], data['Faction'], (len(xx['Influence']) * (-1)))


def star_systems_db(filenames): # Ließt alle SystemIDs und Systemnamen im Journal aus um sie in die DB zu speichern
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    for filename in filenames:
        with open(filename, 'r', encoding='UTF8') as datei:
            for zeile2 in datei:
                search_string2 = "FSDJump"
                if (zeile2.find(search_string2)) > -1:
                    star_systems_data = read_json(zeile2)
                    starchart_db(star_systems_data['SystemAddress'], star_systems_data['StarSystem'])


def influence_db(sys_id, Faction, Influence):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    if sys_id == '':
        # print('NULL')
        sys_id = 'NONE'
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("CREATE table IF NOT EXISTS influence (SystemName TEXT, Faction TEXT, Influence INTEGER)")
    system_name = cursor.execute("SELECT SystemName FROM starchart WHERE SystemID= ?", (sys_id,)).fetchall()
    if not sys_id == 'NONE':
        system_name = system_name[0][0]
        cursor.execute("SELECT SystemName, Faction, Influence FROM influence WHERE SystemName= ? and Faction = ?",
                       (system_name, Faction,))
        result = cursor.fetchall()
        if not result:
            cursor.execute("INSERT INTO influence VALUES (?, ?, ?)", (system_name, Faction, Influence))
            connection.commit()
    connection.close()


def update_influence_db(upd_inf_id, faction, Influence):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    if upd_inf_id == '':
        # print('NULL')
        upd_inf_id = 'NONE'
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("CREATE table IF NOT EXISTS influence (SystemName TEXT, Faction TEXT, Influence INTEGER)")
    system_name = cursor.execute("SELECT SystemName FROM starchart WHERE SystemID= ?", (upd_inf_id,)).fetchall()
    if not upd_inf_id == 'NONE':
        system_name = system_name[0][0]
        cursor.execute("SELECT Influence FROM influence WHERE SystemName= ? and Faction = ?", (system_name, faction,))
        result = cursor.fetchall()
        new_influence = (int(result[0][0])) + int(Influence)
        cursor.execute("UPDATE influence SET Influence = ? WHERE  SystemName= ? and Faction = ?",
                       (new_influence, system_name, faction))
        connection.commit()

    connection.close()


def read_influence_db(ID, faction):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    if isinstance(ID, int):
        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        cursor.execute("CREATE table IF NOT EXISTS influence (SystemName TEXT, Faction TEXT, Influence INTEGER)")
        system_name = cursor.execute("SELECT SystemName FROM starchart WHERE SystemID= ?", (ID,)).fetchall()
        # print(SystemName)
        try:
            system_name = system_name[0][0]
        except IndexError:
            filenames = file_names(0)
            star_systems_db(filenames)
            system_name = cursor.execute("SELECT SystemName FROM starchart WHERE SystemID= ?", (ID,)).fetchall()
            system_name = system_name[0][0]
        result = cursor.execute("SELECT Faction FROM influence WHERE SystemName = ? and Faction = ?",
                                (system_name, faction)).fetchall()
        connection.close()
        try:
            # print(result[0][0])
            return result[0][0]
        except IndexError:
            logger('read_inf_db ' + str(ID) + '  ' + str(faction), 2)
            logger('not yet in DB', 2)


def print_influence_db(filter_b):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    filter_b = '%' + filter_b + '%'
    cursor.execute("CREATE table IF NOT EXISTS influence (SystemName TEXT, Faction TEXT, Influence INTEGER)")
    data = cursor.execute("SELECT * FROM influence WHERE SystemName LIKE ? OR Faction LIKE ? GROUP BY 1, 2, 3",
                          (filter_b, filter_b)).fetchall()
    connection.close()
    return data


def starchart_db(sd_id, system_name):   # Erstellt eine DB mit SystemID und Systemnamen
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("CREATE table IF NOT EXISTS starchart (SystemID INTEGER, SystemName TEXT, Count INTEGER)")
    cursor.execute("SELECT SystemID FROM starchart WHERE SystemID= ?", (sd_id,))
    result = cursor.fetchall()
    if not result:
        # Wenn ID Systemname nicht in Tabelle vorhanden ist, wird sie hinzugefügt
        cursor.execute("INSERT INTO starchart VALUES (?, ?, '')", (sd_id, system_name,))
        connection.commit()
    connection.close()


def read_starchart_table(system_id):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    if isinstance(system_id, int):
        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        cursor.execute("CREATE table IF NOT EXISTS starchart (SystemID INTEGER, SystemName TEXT)")
        system_name = cursor.execute("SELECT SystemName FROM starchart WHERE SystemID = ?", (system_id,)).fetchall()
        try:
            connection.close()
            return system_name[0][0]
        except IndexError:
            logger('SystemAddress =  ' + str(system_id), 2)
            connection.close()


def einfluss_auslesen(journal_file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    tick_hour = tick_hour_label.get()
    tick_minute = tick_minute_label.get()
    tick_time[3] = tick_hour[0:2]
    tick_time[4] = tick_minute[0:2]
    # print(journal_file)
    with open(journal_file, 'r', encoding='UTF8') as datei:
        for zeile in datei:
            search_string = "MissionCompleted"
            if (zeile.find(search_string)) > -1:
                data = json.loads(zeile)
                # Verarbeite die Daten dem TICK entsprechend
                if check_tick_time(zeile, tick):
                    # print(data)
                    extract_data(data)
    # =========================================== End of dateien_einlesen()


def check_tick_time(zeile, ea_tick):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    tag2 = Tag.get()
    monat2 = Monat.get()
    jahr2 = Jahr.get()
    jahr2 = '20' + jahr2
    data = json.loads(zeile)
    timestamp = str(data['timestamp'])
    ctt_log_time = log_date(timestamp)
    tick_okay = False
    log_time_new = datetime(int(ctt_log_time[0]), int(ctt_log_time[1]), int(ctt_log_time[2]),
                            int(ctt_log_time[3]), int(ctt_log_time[4]))
    tick_time_new = datetime(int(jahr2), int(monat2), int(tag2), int(tick_time[3]), int(tick_time[4]))
    if ea_tick is True:
        # Nach dem Tick
        if tick_time_new < log_time_new:
            tick_okay = True
    else:
        # Vor dem Tick
        if tick_time_new > log_time_new:
            tick_okay = True
    return tick_okay


def multi_sell_exploration_data(journal_file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    with open(journal_file, 'r', encoding='UTF8') as datei:
        line = 0
        for zeile in datei:
            line += 1
            search_string = "MultiSellExplorationData"
            if (zeile.find(search_string)) > -1:
                if check_tick_time(zeile, tick):
                    data_found = line
                    data = find_last_docked(journal_file, data_found)
                    faction = data[0]
                    system_name = data[1]
                    data = json.loads(zeile)
                    # print('Sell ExplorationData ' + faction + ' ' + str(data["TotalEarnings"]))
                    vouchers_db('ExplorationData', system_name, str(faction), int(data["TotalEarnings"]))


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
                    data = json.loads(zeile)
                    vk = int(data['SellPrice'])
                    dek = int(data['AvgPricePaid'])
                    menge = int(data['Count'])
                    profit = (vk - dek) * menge
                    try:
                        if data['BlackMarket']:
                            vouchers_db('BlackMarket', system_name, str(faction), int(data["TotalSale"]))
                        else:
                            # print('MarketSell')
                            vouchers_db('MarketSell', system_name, str(faction), int(data["TotalSale"]))
                    except KeyError:
                        logger('KeyError BlackMarket', 2)
                        vouchers_db('MarketSell', system_name, str(faction), profit)


def find_last_docked(journal_file, data_found):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with open(journal_file, 'r', encoding='UTF8') as datei:
        line = 0
        factions = ['test']
        star_systems = ['test']
        faction = ''
        star_system = ''
        for zeile in datei:
            line += 1
            search_string = 'Docked'
            if (zeile.find(search_string)) > -1:
                data = json.loads(zeile)
                try:
                    docked_data = ((data['StationFaction'])['Name'])
                    if line < data_found:
                        factions.append(docked_data)
                    faction = factions[-1]
                except KeyError:
                    logger('Faction in Docked not found', 2)
                star_system = (data['StarSystem'])
                if line < data_found:
                    star_systems.append(star_system)
                star_system = star_systems[-1]
    return faction, star_system


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
                    faction = last_docked[0]
                    data = json.loads(zeile)
                    try:
                        if data['BrokerPercentage']:
                            logger('Ignoring Interstellar Factor', log_var)
                    except KeyError:
                        try:
                            for p in data["Factions"]:
                                if not p['Faction'] == '':
                                    vouchers_db('Bounty ', system_name, faction, int(p['Amount']))
                        except KeyError:
                            try:
                                if data['Faction'] == 'PilotsFederation':
                                    logger('InterstellarFactor', log_var)
                                elif not data['Faction'] == '':
                                    vouchers_db('CombatBonds', system_name, faction, int(data['Amount']))
                            except KeyError:
                                logger('No Faction Event', log_var)


def vouchers_db(vouchers, systemname, faction, amount):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    var = vouchers, systemname, faction, amount
    logger(var, log_var)

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("CREATE table IF NOT EXISTS vouchers (Vouchers TEXT, SystemName Text, Faction TEXT, Amount INTEGER)")
    item = cursor.execute("SELECT Amount FROM vouchers WHERE SystemName = ? and Faction = ? and Vouchers = ?",
                          (systemname, faction, vouchers)).fetchall()
    if not item:
        cursor.execute("INSERT INTO vouchers VALUES (?, ?, ?, ?)", (vouchers, systemname, faction, amount))
        connection.commit()
    else:
        item = cursor.execute("SELECT Amount FROM vouchers WHERE SystemName = ? and Faction = ? and Vouchers = ?",
                              (systemname, faction, vouchers)).fetchone()
        # print(item[0])
        amount += int(item[0])
        # print(amount)
        cursor.execute("UPDATE vouchers SET Amount = ? where SystemName = ? and Faction = ? and Vouchers = ?",
                       (amount, systemname, faction, vouchers))
        connection.commit()
    connection.close()


def print_vouchers_db(filter_b):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    filter_b = '%' + filter_b + '%'
    cursor.execute("CREATE table IF NOT EXISTS vouchers (Vouchers TEXT, SystemName Text, Faction TEXT, Amount INTEGER)")
    data = cursor.execute("""SELECT * FROM vouchers 
                                WHERE SystemName = ? 
                                OR Faction LIKE ? 
                                OR Vouchers LIKE ? GROUP BY 1, 2, 3""",
                          (filter_b, filter_b, filter_b)).fetchall()
    connection.close()
    return data


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
            logger('while auto_refresh', 2)
            if check_auto_refresh.get() != 0:
                logger(check_auto_refresh.get(), log_var)
                for i in range(0, 15):
                    time.sleep(1.0)
                    system.insert(INSERT, '.')
                if check_auto_refresh.get() != 0:
                    refreshing()


def refreshing():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    system.delete(1.0, END)
    system.insert(INSERT, 'Auswertung läuft ')
    i = 0
    while i < 4:
        time.sleep(0.4)
        system.insert(INSERT, '.')
        i += 1
    try:
        bgs.clear_rows()
    except AttributeError:
        logger('NoData in bgs.row', log_var)
    try:
        voucher.clear_rows()
    except AttributeError:
        logger('NoData in voucher.row', log_var)
    try:
        mats_table.clear_rows()
    except AttributeError:
        logger('NoData in voucher.row', log_var)
    if eddc_modul != 4:
        auswertung(eddc_modul)


def threading_auto():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    if eddc_modul == 4:
        logger('AUTO CODEX = 1 ', log_var)
        # tree.destroy()
        for record in tree.get_children():
            tree.delete(record)
        auswertung(eddc_modul)
    elif check_auto_refresh.get() != 0:
        threading.Thread(target=auto_refresh).start()
    else:
        threading.Thread(target=refreshing).start()
        # print('no Refresh')


def logging():
    global log_var
    log_var += 1
    print(log_var)


def mats_auslesen(journal_file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    mats_table.clear_rows()
    with open(journal_file, 'r', encoding='UTF8') as datei:
        for zeile in datei:
            search_string = 'MaterialCollected'
            if (zeile.find(search_string)) > -1:
                data = json.loads(zeile)
                # print(data)
                state = 1
                extract_engi_stuff(data, state)


def ody_mats_auslesen(journal_file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    mats_table.clear_rows()
    with open(journal_file, 'r', encoding='UTF8') as datei:
        for zeile in datei:
            search_string = 'BackpackChange'
            if (zeile.find(search_string)) > -1:
                data = json.loads(zeile)
                # print(data)
                try:
                    for xx in data['Added']:
                        # print(xx)
                        state = 1
                        extract_engi_stuff(xx, state)
                except KeyError:
                    state = (-1)
                    for xx in data['Removed']:
                        extract_engi_stuff(xx, state)
                    logger('failed', 10)


def older_logs(ol_log_time, lauf):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    var = ol_log_time, lauf
    logger(var, log_var)

    files = []
    datum = date(year=int(ol_log_time[0]), month=int(ol_log_time[1]), day=int(ol_log_time[2]))
    update_eleven = datetime(2022, 3, 14)
    new_date = str(datum - timedelta(days=lauf))
    today_year = str(datum)[2:4]
    today_month = str(datum)[5:7]
    today_day = str(datum)[8:10]
    # print(new_date)
    ol_year = str(new_date[2:4])
    ol_month = str(new_date[5:7])
    ol_day = str(new_date[8:10])

    old_date = str(datum)
    old_date = str(old_date[2:4] + old_date[5:7] + old_date[8:10])
    new_date = str(new_date[2:4] + new_date[5:7] + new_date[8:10])
    # print(ol_year, ol_month, ol_day)
    search_date = datetime(int("20" + ol_year), int(ol_month), int(ol_day))
    if search_date > update_eleven:
        older_journal_date = ("20" + str(ol_year) + "-" + str(ol_month) + "-" + str(ol_day) + "T")
        current_journal_date = ("20" + str(today_year) + "-" + str(today_month) + "-" + str(today_day) + "T")
        # print(journal_date)
        filenames = glob.glob(path + "\\Journal." + older_journal_date + "*.log")
        current_filenames = glob.glob(path + "\\Journal." + current_journal_date + "*.log")
        for i in filenames:
            files.append(i)
        for i in current_filenames:
            files.append(i)
        return files
    else:
        current_filenames = glob.glob(path + "\\Journal." + old_date + "*.log")
        filenames = glob.glob(path + "\\Journal." + new_date + "*.log")
        for i in filenames:
            files.append(i)
        for i in current_filenames:
            files.append(i)
        return files


def create_codex_entry():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    # type 0 = geo; 1 = bio ; 2 = space
    global bio_worth

    bio_worth = [('Albidum Sinuous Tubers', '111,300'), ('Aleoida Arcus', '379,300'), ('Aleoida Coronamus', '339,100'),
                 ('Aleoida Gravis', '596,500'), ('Aleoida Laminiae', '208,900'), ('Aleoida Spica', '208,900'),
                 ('Amphora Plant', '117,900'), ('Aureum Brain Tree', '115,900'), ('Bacterium Acies', '50,000'),
                 ('Bacterium Alcyoneum', '119,500'), ('Bacterium Aurasus', '78,500'), ('Bacterium Bullaris', '89,900'),
                 ('Bacterium Cerbrus', '121,300'), ('Bacterium Informem', '426,200'), ('Bacterium Nebulus', '296,300'),
                 ('Bacterium Omentum', '267,400'), ('Bacterium Scopulum', '280,600'), ('Bacterium Tela', '135,600'),
                 ('Bacterium Verrata', '233,300'), ('Bacterium Vesicula', '56,100'), ('Bacterium Volu', '400,500'),
                 ('Bark Mounds', '108,900'), ('Blatteum Bioluminescent Anemone', '110,500'),
                 ('Blatteum Sinuous Tubers', '111,300'), ('Cactoida Cortexum', '222,500'),
                 ('Cactoida Lapis', '164,000'), ('Cactoida Peperatis', '164,000'),
                 ('Cactoida Pullulanta', '222,500'), ('Cactoida Vermis', '711,500'),
                 ('Caeruleum Sinuous Tubers', '111,300'), ('Clypeus Lacrimam', '426,200'),
                 ('Clypeus Margaritus', '557,800'), ('Clypeus Speculumi', '711,500'),
                 ('Concha Aureolas', '400,500'), ('Concha Biconcavis', '806,300'), ('Concha Labiata', '157,100'),
                 ('Concha Renibus', '264,300'), ('Croceum Anemone', '110,500'), ('Crystalline Shards', '117,900'),
                 ('Electricae Pluma', '339,100'), ('Electricae Radialem', '339,100'),
                 ('Fonticulua Campestris', '63,600'),
                 ('Fonticulua Digitos', '127,700'), ('Fonticulua Fluctus', '900,000'), ('Fonticulua Lapida', '195,600'),
                 ('Fonticulua Segmentatus', '806,300'), ('Fonticulua Upupam', '315,300'), ('Frutexa Acus', '400,500'),
                 ('Frutexa Collum', '118,500'), ('Frutexa Fera', '118,100'), ('Frutexa Flabellum', '127,900'),
                 ('Frutexa Flammasis', '500,100'), ('Frutexa Metallicum', '118,100'), ('Frutexa Sponsae', '326,500'),
                 ('Fumerola Aquatis', '339,100'), ('Fumerola Carbosis', '339,100'), ('Fumerola Extremus', '711,500'),
                 ('Fumerola Nitris', '389,400'), ('Fungoida Bullarum', '224,100'), ('Fungoida Gelata', '206,300'),
                 ('Fungoida Setisis', '120,200'), ('Fungoida Stabitis', '174,000'), ('Gypseeum Brain Tree', '115,900'),
                 ('Lindigoticum Brain Tree', '115,900'), ('Lindigoticum Sinuous Tubers', '111,300'),
                 ('Lividum Brain Tree', '115,900'), ('Luteolum Anemone', '110,500'),
                 ('Osseus Cornibus', '109,500'), ('Osseus Discus', '596,500'),
                 ('Osseus Fractus', '239,400'), ('Osseus Pellebantus', '477,700'), ('Osseus Pumice', '197,800'),
                 ('Osseus Spiralis', '159,900'), ('Ostrinum Brain Tree', '115,900'),
                 ('Prasinum Bioluminescent Anemone', '110,500'), ('Prasinum Sinuous Tubers', '111,300'),
                 ('Puniceum Anemone', '110,500'), ('Puniceum Brain Tree', '115,900'),
                 ('Recepta Conditivus', '645,700'), ('Recepta Deltahedronix', '711,500'),
                 ('Recepta Umbrux', '596,500'), ('Roseum Anemone', '110,500'),
                 ('Roseum Bioluminescent Anemone', '110,500'), ('Roseum Brain Tree', '115,900'),
                 ('Roseum Sinuous Tubers', '111,300'), ('Rubeum Bioluminescent Anemone', '110,500'),
                 ('Stratum Araneamus', '162,200'), ('Stratum Cucumisis', '711,500'),
                 ('Stratum Excutitus', '162,200'), ('Stratum Frigus', '171,900'),
                 ('Stratum Laminamus', '179,500'), ('Stratum Limaxus', '102,500'), ('Stratum Paleas', '102,500'),
                 ('Stratum Tectonicas', '806,300'), ('Tubus Cavas', '171,900'), ('Tubus Compagibus', '102,700'),
                 ('Tubus Conifer', '315,300'), ('Tubus Rosarium', '400,500'), ('Tubus Sororibus', '557,800'),
                 ('Tussock Albata', '202,500'), ('Tussock Capillum', '370,000'), ('Tussock Caputus', '213,100'),
                 ('Tussock Catena', '125,600'), ('Tussock Cultro', '125,600'), ('Tussock Divisa', '125,600'),
                 ('Tussock Ignis', '130,100'), ('Tussock Pennata', '320,700'), ('Tussock Pennatis', '59,600'),
                 ('Tussock Propagito', '71,300'), ('Tussock Serrati', '258,700'), ('Tussock Stigmasis', '806,300'),
                 ('Tussock Triticum', '400,500'), ('Tussock Ventusa', '201,300'), ('Tussock Virgam', '645,700'),
                 ('Violaceum Sinuous Tubers', '111,300'), ('Viride Brain Tree', '115,900'),
                 ('Viride Sinuous Tubers', '111,300')]

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()

        cursor.execute("""CREATE table IF NOT EXISTS codex_entry (
                        data TEXT,
                        worth INTEGER,
                        type INTEGER, 
                        region TEXT)
                        """)

        cce_regions = RegionMapData.regions

        select = cursor.execute("SELECT * from codex_entry").fetchall()
        # print(select)
        if not select:
            for a in cce_regions:
                if a is not None:
                    for i in bio_worth:
                        cursor.execute("INSERT INTO codex_entry VALUES (?, ?, ?, ?)", (i[0], i[1], 0, a))
            connection.commit()


create_codex_entry()


def insert_codex_db(logtime, codex_name, icd_cmdr, codex_entry, category, region, icd_system):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    icd_log_time = (log_date(logtime))
    date_log = (icd_log_time[0] + "-" + icd_log_time[1] + "-" + icd_log_time[2])
    time_log = (icd_log_time[3] + ":" + icd_log_time[4] + ":" + icd_log_time[5])

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
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
        data = json.loads(zeile)
        return data
    except ValueError:
        logger(('read_json' ,zeile), log_var)
        data = ['']
        return data


def read_codex_add_info(journal_file, rlc_log_time, type):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with open(journal_file, 'r', encoding='UTF8') as datei:
        for zeile in datei:
            search_string = '"ScanType":"'+ type +'"'
            # print(search_string)
            if zeile.find(search_string) > -1:
                data = read_json(zeile)
                rcai_logtime = data['timestamp']
                if rcai_logtime == rlc_log_time:
                    # print(rcai_logtime, rlc_log_time)
                    # print(data)
                    info_1 = data['BodyName']
                    if 'Cluster' not in info_1:
                        try:
                            info_2 = data['PlanetClass']
                        except KeyError:
                            info_2 = ['']
                            # print(data)
                        try:
                            info_3 = data['Atmosphere']
                        except KeyError:
                            info_3 = ['']
                        if info_2 != [''] and info_3 != ['']:
                            return info_1, info_2, info_3
                    # else:
                    #     return


def read_log_codex(journal_file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    rlc_cmdr = check_cmdr(journal_file)

    with open(journal_file, 'r', encoding='UTF8') as datei:
        for zeile in datei:
            search_string = '"event":"CodexEntry"'
            if zeile.find(search_string) > -1:
                # print(zeile)
                data = read_json(zeile)
                logtime = data['timestamp']
                codex_name = (data['Name'])
                codex_entry = (data['Name_Localised'])
                category = data['SubCategory']
                region = data['Region_Localised']
                rlc_system = data['System']

                if 'Thargoid' in codex_entry:
                    codex_name = 'Xenological'
                    category = '$Codex_SubCategory_Goid'

                if 'Terrestrials' in category:
                    # print('IF ' + codex_entry)
                    codex_name = 'Terrestrials'
                    add_info = read_codex_add_info(journal_file, logtime, 'Detailed')
                    # print(add_info)
                    if add_info:
                        if add_info[1] != ['']:
                            codex_entry = add_info[1]
                        else:
                            codex_entry = (data['Name_Localised'])
                    else:
                        add_info = read_codex_add_info(journal_file, logtime, 'AutoScan')
                        # print(journal_file, logtime, 'AutoScan')
                        # print(add_info)
                        if add_info:
                            if add_info[1] != ['']:
                                codex_entry = add_info[1]
                                # print('Entry ' + codex_entry)
                            else:
                                codex_entry = (data['Name_Localised'])

                if 'Gas_Giants' in category:
                    codex_entry = (data['Name'])
                    codex_entry = str(codex_entry)
                    codex_entry = codex_entry.replace('$Codex_Ent_Standard_', '')
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

                if 'Thargoid' in  category:
                    codex_entry = (data['Name_Localised'])
                    codex_name = data['Category_Localised']

                insert_codex_db(logtime, codex_name, rlc_cmdr, codex_entry, category, region, rlc_system)


def read_bio_data(journal_file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    log = 'aktuelles  LOG' + str(journal_file)
    logger(log, log_var)

    with open(journal_file, 'r', encoding='UTF8') as datei:
        for i, zeile in enumerate(datei):
            search_string = '"ScanType":"Analyse"'
            if zeile.find(search_string) > -1:
                data = json.loads(zeile)
                biodata = (data['Species_Localised'])
                system_address_bio = data['SystemAddress']

                # find Region with SystemAddress
                region = (findRegionForBoxel(system_address_bio)['region'][1])
                # print(findRegionForBoxel(system_address_bio))

                timestamp = str(data['timestamp'])
                rbd_log_time = (log_date(timestamp))
                date_log = (rbd_log_time[0] + "-" + rbd_log_time[1] + "-" + rbd_log_time[2])
                time_log = (rbd_log_time[3] + ":" + rbd_log_time[4] + ":" + rbd_log_time[5])
                line_number = (i + 1)
                bio_cmdr = check_cmdr(journal_file)
                system_infos = check_system(journal_file, line_number)
                rbd_system = system_infos[0]
                body = system_infos[1]
                bio_color = find_codex(journal_file, line_number, biodata)
                if bio_color == '':
                    # print('bio_color ', biodata, bio_color)
                    lauf = 1
                    while lauf < 15:
                        # print('111')
                        filenames = older_logs(rbd_log_time, lauf)
                        # print(filenames)
                        for filename in reversed(filenames):
                            # print(filename)
                            region_cmdr = check_cmdr(filename)
                            if str(bio_cmdr) == str(region_cmdr):
                                bio_color = find_codex(filename, 99999, biodata)
                            if bio_color != '':
                                break
                        if bio_color != '':
                            if log_var > 4:
                                logger('codex info gefunden; break', log)
                            break
                        if not filenames:
                            bio_color = ''
                            if log_var > 4:
                                logger(('break not filenames' + str(lauf)), log_var)
                            break
                        if lauf == 999:
                            bio_color = ''
                            if log_var > 4:
                                logger(('break lauf ' + str(lauf)), log_var)
                            break
                        lauf = lauf + 1
                # else:
                #     region_cmdr = bio_cmdr

                if rbd_system == "blank":
                    lauf = 1
                    while lauf < 1000:
                        filenames = older_logs(rbd_log_time, lauf)
                        for filename in reversed(filenames):
                            system_cmdr = check_cmdr(filename)
                            if str(bio_cmdr) == str(system_cmdr):
                                system_infos = check_system(filename, 99999)
                                rbd_system = system_infos[0]
                                body = system_infos[1]
                                if rbd_system != 'blank':
                                    logger('if system != blank:', log_var)
                                    break
                        if rbd_system != 'blank':
                            logger('if system != blank:', log_var)
                            break
                        if not filenames:
                            rbd_system = "no System found"
                            body = "no Body found"
                            logger('if system != blank:', log_var)
                            break
                        lauf = lauf + 1
                # print(date_log, time_log, bio_cmdr, biodata, bio_color, rbd_system, body,
                #       region)
                codex_into_db(date_log, time_log, bio_cmdr, biodata, bio_color, rbd_system, body,
                              region)


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


def codex_into_db(date_log, time_log, cid_cmdr, data, bio_color, systemname, body, region):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
        # print(bio_color)
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("""CREATE table IF NOT EXISTS codex (
                    date_log date,
                    time_log timestamp,
                    cmdr TEXT,
                    data TEXT,
                    bio_color TEXT,
                    systemname TEXT,
                    body TEXT,
                    region TEXT,
                    codex INTEGER,
                    player_death INTEGER)
                    """)
    select = cursor.execute("""SELECT cmdr, data, bio_color, region FROM codex WHERE 
                            cmdr = ? and
                            data = ? and
                            bio_color = ? and
                            region = ?             
                            """, (cid_cmdr, data, bio_color, region)).fetchall()

    if not select:
        codex_boolean = 1
    else:
        codex_boolean = 0
        bio_color = ''

    if bio_color == '':
        codex_boolean = 0
    else:
        codex_boolean = 1

    item = cursor.execute("""SELECT date_log, time_log, cmdr FROM codex WHERE
                            date_log = ? and
                            time_log = ? and
                            cmdr = ?
                            """, (date_log, time_log, cid_cmdr)).fetchall()

    if not item:
        cursor.execute("INSERT INTO codex VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (date_log, time_log, cid_cmdr, data, bio_color, systemname, body, region, codex_boolean, 0))
        # sql = "INSERT INTO codex VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"

    connection.commit()


def insert_into_death_db(date_log, time_log, iid_cmdr):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("""CREATE table IF NOT EXISTS player_death (
                    date_log date,
                    time_log timestamp,
                    cmdr TEXT)
                    """)
    select = cursor.execute("""SELECT * FROM player_death WHERE 
                            date_log = ? and time_log = ? and cmdr = ?""", (date_log, time_log, iid_cmdr)).fetchall()
    # print(select)
    if not select:
        cursor.execute("INSERT INTO player_death VALUES (?, ?, ?)", (date_log, time_log, iid_cmdr))
    connection.commit()


def insert_into_last_sell(date_log, time_log, iis_sell, iis_cmdr):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
        # print(bio_color)
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("""CREATE table IF NOT EXISTS selling (
                    date_log date,
                    time_log timestamp,
                    sell TEXT,
                    cmdr TEXT)
                    """)
    select = cursor.execute("""SELECT * FROM selling WHERE 
                            date_log = ? and time_log = ? and sell = ?""", (date_log, time_log, iis_sell)).fetchall()
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
    # print(search_data[3])
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select = cursor.execute("SELECT worth FROM codex_entry WHERE data = ? ", (search_data[3],)).fetchone()
    if select:
        # print(select)
        # print(type(select))
        new = str(select[0])
        x = new.replace(',', '')
    else:
        x = 0
    y = int(x)
    return y


def insert_into_planet_bio_db(body_name, body_id, count, region):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    cursor.execute("""CREATE table IF NOT EXISTS planet_bio_info (
                                        body TEXT,
                                        body_id TEXT,
                                        count TEXT,
                                        region TEXT)""")

    select = cursor.execute("""SELECT body from planet_bio_info where body = ?""",
                            (body_name, )).fetchall()

    if select == []:
        cursor.execute("INSERT INTO planet_bio_info VALUES (?,?,?,?)",
                       (body_name, body_id, count, region))
        connection.commit()


def insert_into_bio_db(body_name, bio_scan_count, genus, species, color, mark_missing):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    bio_scan_count = int(bio_scan_count)

    cursor.execute("""CREATE table IF NOT EXISTS bio_info_on_planet (
                                        body TEXT,
                                        genus TEXT,
                                        species TEXT,
                                        bio_scan_count INTEGER,
                                        mark_missing TEXT)""")

    select = cursor.execute("""SELECT bio_scan_count from bio_info_on_planet where body = ? and genus = ? 
                                and species = ?""",
                            (body_name, genus, species)).fetchall()

    # print(select)
    # print(bio_scan_count, body_name, genus, species)
    if select == []:
        # print(select)
        cursor.execute("INSERT INTO bio_info_on_planet VALUES (?,?,?,?,?)",
                       (body_name, genus, species, bio_scan_count, mark_missing))
        connection.commit()

    elif int(bio_scan_count) != int(select[0][0]):
    # else:
    #     print(bio_scan_count,body_name,genus, species, mark_missing, select[0][0])
        cursor.execute("""UPDATE bio_info_on_planet SET bio_scan_count = ?
                        WHERE body = ? AND genus = ? AND species = ? """,
                       (bio_scan_count, body_name, genus, species))
        connection.commit()


def update_bio_db(body_name, bio_scan_count, genus, species):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    cursor.execute("""CREATE table IF NOT EXISTS bio_info_on_planet (
                                        body TEXT,
                                        genus TEXT,
                                        species TEXT,
                                        bio_scan_count INTEGER,
                                        mark_missing TEXT)""")

    select = cursor.execute("""SELECT bio_scan_count from bio_info_on_planet where body = ? and genus = ? 
                                 and species = ?""",
                            (body_name, genus, species)).fetchall()

    # if select[0][0] == bio_scan_count:
    #     print(select)


def get_data_from_DB(file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    current_system = system_scan(file)
    # print('current_system', current_system)
    if current_system == None:
        return ' '
    cmdr = check_cmdr(file)
    select = cursor.execute("SELECT * FROM planet_infos where SystemName = ?", (current_system[0],)).fetchall()
    body_name = mark_planet(file)
    print('select',select)
    print('body_name', body_name)
    if body_name and ((current_system[0]) in body_name):
        body = body_name.replace(str(current_system[0]), '')
        for number, i in enumerate(select):
            if body == i[3]:

                select.insert(0, select.pop(number))
    # print(select)
    return get_biodata_from_planet(cmdr, select)


def get_biodata_from_planet(cmdr, select):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    data_2 = []
    for i in select:
        # print('i ', i)
        system_address = int(i[0])
        system_name = str(i[1])
        body_name = str(i[1]) + str(i[3])
        star_class = str(i[2])
        distance = str(i[4])
        planet_type = str(i[5])
        body_atmos = str(i[6])
        body_gravity = str(i[7])
        body_temp = float(i[8])
        body_pressure = float(i[9])
        volcanism = str(i[10])
        materials = str(i[11])
        material = materials.split(' ')
        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        cursor.execute("""CREATE table IF NOT EXISTS planet_bio_info (
                                            body TEXT,
                                            body_id TEXT,
                                            count TEXT,
                                            region TEXT)""")

        b_count = cursor.execute("SELECT count FROM planet_bio_info where body = ?", (body_name,)).fetchone()
        if b_count:
            bio_count = b_count[0]
        else:
            bio_count = 0
        bio_names = select_prediction_db(star_class, planet_type, body_atmos,
                                         body_gravity, body_temp, body_pressure, volcanism)
        # print(star_class, planet_type, body_atmos, body_gravity, body_temp, body_pressure, volcanism)
        bio = []
        bcd = []
        for bio in bio_names:
            # print(bio)
            get_cod = get_color_or_distance(bio[0], star_class, material)
            # print(get_cod)
            bio = (*bio, get_cod[0][0][0], get_cod[1])
            if get_cod[1]:
                bcd.append(bio)
        # print(bcd)

        region = (findRegionForBoxel(system_address)['region'][1])
        missing_in_region = (missing_codex(cmdr, region))
        global normal_view
        normal_view = 4
        missing_bio = []
        if int(bio_count) > 0:
            data_2.append((body_name, distance, bio_count, '', '', '', '', '', '', region))
        for i in missing_in_region:
            missing_bio.append(i[3])
        mark_missing = 0

        select_bios_on_body = cursor.execute("""SELECT * from bio_info_on_planet where body = ? 
        and bio_scan_count > 0 Order by genus""", (body_name,)).fetchall()
        select_complete_bios_on_body = cursor.execute("""SELECT COUNT(species) from bio_info_on_planet where body = ? 
                and bio_scan_count = 3""", (body_name,)).fetchall()
        count_select = cursor.execute("SELECT count from planet_bio_info where body = ?", (body_name, )).fetchall()

        # print('Bios on Planet ', body_name, ' = ', count_select[0][0])
        # print('gescannte Bios ' , (select_bios_on_body))
        # print('komplett gescannte Bios ' , select_complete_bios_on_body)
        species_all = []
        genus_all = []

        for i in select_bios_on_body:
            bio_2 = i[1] + ' ' + i[2]
            gcod = (get_color_or_distance(bio_2, star_class, material))
            # print(bio_2, star_class, gcod)
            if i[3] == 1:
                scan = 'Scan in Progress 1 / 3'
            if i[3] == 2:
                scan = 'Scan in Progress 2 / 3'
            if i[3] == 3:
                scan = 'Scan complete 3 / 3'
            gcod_color = gcod[0][0][0]
            gcod_bio_distance = gcod[1]
            data_2.append(('', i[0], scan, i[1],
                           i[2], gcod_color, gcod_bio_distance, '', '', 0))
            species_all.append(str(i[2]))
            genus_all.append(str(i[1]))

        if int(count_select[0][0]) != int(select_complete_bios_on_body[0][0]):

            if bio_names != []:
                for count, i in enumerate(bcd):
                    bio_name = i[0].split(' ')
                    genus = bio_name[0]
                    species = bio_name[1]
                    temp = genus.capitalize() + ' ' + species.capitalize()
                    color =  i[2]
                    bio_distance = i[1]
                    if temp in missing_bio:
                        mark_missing = 1
                    else:
                        mark_missing = 0
                    bio_scan_count = get_bio_scan_count(temp, body_name)
                    if (bio_scan_count) == None:
                        return
                    insert_into_bio_db(body_name, bio_scan_count[1], genus.capitalize(),
                                       species.capitalize(), color, mark_missing)
                    if genus.capitalize() in genus_all:
                        continue
                    if species.capitalize() in species_all:
                        continue
                    if count > 0:
                        bio_name = str(bcd[count - 1]).split(' ')
                        genus2 = bio_name[0]
                        if genus == genus2:
                            genus = ''
                    data_2.append(('', body_name, bio_scan_count[0], genus.capitalize(),
                                species.capitalize(), color, bio_distance,'', '', mark_missing))

    if data_2:
        logger(('data_2', data_2), log_var)
        return data_2


def read_data_from_last_system(file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    starsystem = ''
    cmdr = ''

    with open(file, 'r', encoding='UTF8') as datei:
        for zeile in datei.readlines():
            data = read_json(zeile)
            if data.get('event',0) == 'Commander':
                cmdr = data.get('Name','0')
                with open(file, 'r', encoding='UTF8') as datei_2:
                    for zeile in datei_2.readlines()[::-1]:  # Read File line by line reversed!
                        data = read_json(zeile)
                        if data['event'] == 'Location':
                            starsystem = data['StarSystem']
                        if data['event'] == 'Disembark':
                            starsystem = data['StarSystem']
                        if data['event']== 'FSDJump':
                            starsystem = data['StarSystem']
                        if starsystem != '':
                            # print(starsystem)
                            with sqlite3.connect(database) as connection:
                                cursor = connection.cursor()
                                select = cursor.execute("SELECT * FROM planet_infos WHERE SystemName = ?",
                                                        (starsystem,)).fetchall()
                                if select:
                                    # print(select)
                                    data = get_biodata_from_planet(cmdr, select)
                                    return data
                            break


def treeview_codex():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    global filter_region, filter_cmdr, filter_bdata, combo_cmdr, combo_region, \
        combo_bio_data, b_data, regions, cmdr, tree, normal_view, death_frame, \
        death_date_combo, sell_combo, begin_time, end_time, sorting, refresher
    refresher = 0
    sorting = IntVar()
    normal_view = 4
    filter_region = ''
    filter_cmdr = ''
    filter_bdata = ''
    tree = Toplevel(root)
    tree.title('Display Codex Data')
    tree.geometry("1200x570")
    tree.minsize(1200, 570)
    tree.maxsize(1200, 570)
    tree.after(1, lambda: tree.focus_force())
    try:
        img = resource_path("eddc.ico")
        tree.iconbitmap(img)
    except TclError:
        print('Icon not found)')
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
    background_label = Label(tree, image=background_image)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)


    def switch_view():
        global normal_view
        if normal_view == 0:
            normal_view = 1
        else:
            normal_view = 0
        refresh_view()

    def codex_stars():
        global normal_view
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)
        normal_view = 3
        refresh_view()

    def system_scanner():
        global normal_view
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)
        normal_view = 4
        refresh_view()

    menu_tree = Menu(tree)
    tree.config(menu=menu_tree)
    file_menu = Menu(menu_tree, tearoff=False)
    menu_tree.add_cascade(label="More", menu=file_menu)
    file_menu.add_command(label="Bio Codex Entry / Missing Bios", command=switch_view)
    # file_menu.add_command(label="Player Death", command=player_death)
    file_menu.add_command(label="Codex Stars", command=codex_stars)
    file_menu.add_command(label="System Scanner", command=system_scanner)

    def create_frame():
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)

        global tree_frame, tree_scroll, codex_tree
        tree_frame = Frame(tree, bg='black')
        tree_frame.pack(pady=5)

        tree_scroll = Scrollbar(tree_frame)
        tree_scroll.pack(side=RIGHT, fill=Y)
        codex_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, selectmode="extended", height=13)
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


    def read_codex_data(rcd_cmdr, rcd_region):
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            if log_var > 4:
                logger((rcd_cmdr, rcd_region), log_var)
            if rcd_cmdr and rcd_region:
                select = cursor.execute("SELECT * FROM codex_data WHERE cmdr = ? and region = ?"
                                        "and category not like '%Organic_Structures%'"
                                        " ORDER by date_log DESC, time_log DESC",
                                        (rcd_cmdr, rcd_region)).fetchall()
            elif rcd_cmdr and not rcd_region:
                select = cursor.execute("SELECT * FROM codex_data WHERE cmdr = ? and "
                                        "category not like '%Organic_Structures%'"
                                        " ORDER by date_log DESC, time_log DESC",
                                        (rcd_cmdr,)).fetchall()
            elif rcd_region and not rcd_cmdr:
                select = cursor.execute("SELECT * FROM codex_data WHERE region = ? and "
                                        "category not like '%Organic_Structures%'"
                                        " ORDER by date_log DESC, time_log DESC",
                                        (rcd_region,)).fetchall()
            elif not rcd_cmdr and not rcd_region:
                select = cursor.execute("SELECT * FROM codex_data WHERE "
                                        "category not like '%Organic_Structures%'"
                                        " ORDER by date_log DESC, time_log DESC", ).fetchall()
        # print(select)
        return select


    def check_planets():
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)
        logger(normal_view, log_var)

        data = []
        data = start_read_logs()
        if not data:
            logger('No Data - check_planet', 2)
            data = [('DATE', 'TIME', 'COMMANDER', 'SPECIES',
                'VARIANT', 'SYSTEM', 'BODY', "REGION", "No Data", "No Data")]
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
        codex_tree.tag_configure('subrow', background='#f07b05')
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

    def codex_treeview():
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)
        summe = 0
        data = ['']
        update = 0
        if normal_view == 0:
            if sorting.get() != 0:
                update = 3  # Nach Datum sortiert
            else:
                update = 0  # Nach Biologischen Daten sortiert
            # print(update)
            data = select_filter(filter_cmdr, filter_region, filter_bdata, update)

        elif normal_view == 1:
            data = missing_codex(filter_cmdr, filter_region)
            update = 0
            set_main_column_and_heading()


        # All Codex Data except BIO
        elif normal_view == 3: # Zeige Codex Daten ohne die Biologischen vom CMDR und oder der Region an
            data = read_codex_data(filter_cmdr, filter_region)
            update = 0

        elif normal_view == 4: # Anhand der gescannten Daten wird ermittelt welche BIO Signal auf dem Planeten sein können
            global data2
            data2 = check_planets()
            if data2 != 0:
                data = data2
            # print('data' ,data)
            update = 0

        if not data:
            data = [('DATE', 'TIME', 'COMMANDER', 'SPECIES',
                     'VARIANT', 'SYSTEM', 'BODY', "In REGION ", 1, 1)]
            summe = 0
        elif normal_view == 2 or normal_view == 0:
            summe = 0
            for i in data:
                summe += worth_it(i)

        # creating treeview
        set_main_column_and_heading()

        if normal_view == 4:
            set_system_scanner_treeview()
        else:
            set_main_column_and_heading()

        # insert Data in treeview
        count = 0
        worth = ''
        subrow = 0

        if (len(data)) > 20:
            # open = 'False'
            open = 'True'
        else:
            open = 'True'
        counter = 'a'

        def treeview_insert(record, parent, count, open, tag):
            # print('treeview')
            # print(record, parent, count, open, tag)
            codex_tree.insert(parent=parent, index='end', iid=str(count), open=open, text="",
                              values=(count, record[0], record[1], record[2], record[3], record[4],
                                      worth, record[5], record[6], record[7]), tags=(tag,))

        for record in data:
            if normal_view == 2 or normal_view == 0:
                worth = worth_it(record)
                worth = format(worth, ',d')

            if update == 3:
                # Wenn nach Datum sortiert wird darf kein Subrow erstellt werden!
                record = (
                    record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7], 1,
                    record[9])

            if normal_view == 3:
                codex_tree.heading("Codex eintrag", text="Codex Category", anchor=E)
                codex_tree.heading("Codex Farbe", text="Codex Eintrag", anchor=E)
                codex_tree.column("Codex eintrag", anchor=E, width=200)
                codex_tree.column("Codex Farbe", anchor=E, width=220)
                codex_tree.column("Scan Value", anchor=E, width=0)
                codex_tree.column("Body", anchor=E, width=0)
                codex_tree.heading("Scan Value", text="", anchor=W)
                codex_tree.heading("Body", text="", anchor=W)

                record = (record[0], record[1], record[2], record[3], record[4], record[6], '',
                          record[7], 1, 0)

            if normal_view == 4: # SystemScanner
                set_system_scanner_treeview()
                # print('record' ,record)
                new = record[3] + ' ' + record[4]
                search = 0,1,2,new
                worth = worth_it(search)
                worth = format(worth, ',d')
                if record[0] != '': # Im Record sind Planeten Infos
                    record = (
                        record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[9], 1,
                        record[7])
                    counter = 'a'
                    worth = ''
                    tag = 'oddrow'
                    treeview_insert(record, '', count, open, tag)
                    subrow = 0
                else:
                    # print(record) # ('', '', 4, 'Osseus', 'Spiralis', [('Turquoise',)], 800, '', 'osseus spiralis', 0)
                    subrow += 1
                    if subrow % 2 == 0:
                        tag = 'oddrow'
                    else:
                        tag = 'evenrow'
                    if record[9] == 1:
                        if subrow % 2 == 0:
                            tag = 'missing_even'
                        else:
                            tag = 'missing_odd'
                    if count > 0:
                        count -= 1
                        record = (
                            record[0], record[0], record[0], record[3], record[4], record[5], record[6], record[2], 1,
                            record[7])
                        treeview_insert(record, str(count), str(str(count) + counter), open, tag)
                        counter = chr(ord(counter) + 1)

            else:
                if count % 2 == 0:
                    # Alle geraden Zeilen werden hellblau eingefärbt
                    if record[4] != '':
                        counter = 'a'
                    if record[8] != 0:
                        tag = 'evenrow'
                        treeview_insert(record, '', count, open, tag)
                    else:
                        count -= 1
                        treeview_insert(record, str(count), str(str(count) + counter), open, 'subrow')
                        counter = chr(ord(counter) + 1)

                else:
                    # Alle ungeraden Zeilen werden weiß eingefärbt.
                    if record[8] != 0:
                        tag = 'oddrow'
                        treeview_insert(record, '', count, open, tag)
                    else:
                        if count > 1 or count == 1:
                            count -= 1
                            treeview_insert(record, str(count), str(str(count) + counter), open, 'subrow')
                            counter = chr(ord(counter) + 1)

                        # elif count == 1:
                        #     count -= 1
                        #     treeview_insert(record, str(count), str(str(count) + counter), open, 'subrow')
                        #     counter = chr(ord(counter) + 1)

            count += 1
            #End for i in Record


        codex_tree.pack()
        if summe > 0 and (normal_view == 2 or normal_view == 0):
            summen_text = ('Summe  - Anzahl Einträge : ' + str(count) + '     Wertigkeit :  ' + str(f"{summe:,}"))
            summe = Label(tree_frame, text=summen_text, bg='black', fg='white')
            summe.pack(fill=X, side=RIGHT)

        #End of codex_treeview()

    def read_files(): # Gibt es was neues?
        funktion = inspect.stack()[0][3]
        logger(funktion, 2)
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
                # print('nothing new')
                return 1
            else:
                return 0

    def refresh_treeview():
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)
        threading.Thread(target=treeview_loop).start()

    def treeview_loop():
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)
        switch = 0

        while tree is not None and tree.winfo_exists():
            if normal_view != 4:
                switch = read_files()
            else:
                data3 = check_planets()
                switch = 0
                if data2 != data3:
                    switch = 1 # es gibt neue Daten zum Anzeigen

            b_date_new  = begin_time.get()
            e_date_new =  end_time.get()
            # print(b_date, begin_time.get())
            # print(e_date, end_time.get())
            #
            if b_date != b_date_new or e_date != e_date_new:
                print('Datums Filter hat sich verändert')
                switch = 1

            if switch == 1:
                logger('log have changed', 1)
                refresh_view()
                refresh_combo()
            else:
                print('nothing new')
                time.sleep(5.0)

    def refresh_view():
        global tree_start
        tree_start += 1
        # print(tree_start)
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)

        for i in codex_tree.get_children():
            # print(i)
            codex_tree.delete(i)
        tree_frame.destroy()
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
        filter_bdata = combo_bio_data.get()
        filter_bdata = '%' + filter_bdata + '%'
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        if normal_view == 3:
            third_combo = 'codex_name'
            s_table = 'codex_data'
        else:
            third_combo = 'data'
            s_table = 'codex'

        # 1 FILTER CMDR
        b_data = [(''), ('Aleoida'), ('Bacterium'), ('Cactoida'), ('Clypeus'), ('Concha'),
                  ('Electricae'), ('Fonticulua'), ('Fungoida'), ('Frutexa'), ('Fumerola'), ('Osseus'),
                  ('Recepta'), ('Stratum'), ('Tubus'), ('Tussock'), ('---------'),
                  ('Amphora Plant'), ('Anemone'), ('Bark Mounds'), ('Brain'),
                  ('Crystalline Shards'), ('Fumerola'), ('Tubers')]
        combo_bio_data.configure(values=b_data)

        if filter_cmdr and not filter_region and not filter_bdata:
            query = 'SELECT DISTINCT region FROM ' + s_table + ' where cmdr = ? ORDER BY region'
            selection_region = cursor.execute(query, (filter_cmdr,)).fetchall()
            regions = ['']
            for i in selection_region:
                regions = regions + [i[0]]
            combo_regions.configure(values=regions)
            # combo_bio_data.configure(values=b_data)

        # 2 FILTER CMDR & REGION
        if filter_cmdr and filter_region and not filter_bdata:
            selection = cursor.execute("SELECT DISTINCT data FROM codex "
                                       "where cmdr = ? and region = ? ORDER BY data",
                                       (filter_cmdr, filter_region)).fetchall()
            # combo_bio_data.configure(values=b_data)

        # 3 FILTER CMDR & BIO_DATA
        if filter_cmdr and not filter_region and filter_bdata:
            if filter_bdata == '%---------%':
                filter_bdata = ''
            selection_region = cursor.execute("SELECT DISTINCT region FROM codex "
                                              "where cmdr = ? and data like ? ORDER BY region",
                                              (filter_cmdr, filter_bdata)).fetchall()
            regions = ['']
            for i in selection_region:
                regions = regions + [i[0]]
            combo_regions.configure(values=regions)

        # 4 Filter REGION
        if not filter_cmdr and filter_region and not filter_bdata:
            selection_bio = cursor.execute("SELECT DISTINCT data FROM codex "
                                           "where region = ? ORDER BY data",
                                           (filter_region,)).fetchall()
            # combo_bio_data.configure(values=b_data)

            selection_cmdr = cursor.execute("SELECT DISTINCT cmdr FROM codex "
                                            "where region = ?  ORDER BY cmdr",
                                            (filter_region,)).fetchall()

            cmdrs = ['']
            for i in selection_cmdr:
                cmdrs = cmdrs + [i[0]]
            combo_cmdr.configure(values=cmdrs)

        # 5 Filter REGION & BIO
        if not filter_cmdr and filter_region and filter_bdata:
            if filter_bdata == '%---------%':
                filter_bdata = ''
            selection_cmdr = cursor.execute("SELECT DISTINCT cmdr FROM codex "
                                            "where region = ?  ORDER BY cmdr",
                                            (filter_region,)).fetchall()

            cmdrs = ['']
            for i in selection_cmdr:
                cmdrs = cmdrs + [i[0]]
            combo_cmdr.configure(values=cmdrs)
            # combo_bio_data.configure(values=b_data)

        # 6 Filter BIODATA
        if not filter_cmdr and not filter_region and filter_bdata:
            if filter_bdata == '%---------%':
                filter_bdata = ''
            selection_cmdr = cursor.execute("SELECT DISTINCT cmdr FROM codex "
                                            "where data like ? ORDER BY cmdr",
                                            (filter_bdata,)).fetchall()
            cmdrs = ['']
            for i in selection_cmdr:
                cmdrs = cmdrs + [i[0]]
            combo_cmdr.configure(values=cmdrs)

            selection_region = cursor.execute("SELECT DISTINCT region FROM codex "
                                              "where data like ?  ORDER BY region",
                                              (filter_bdata,)).fetchall()
            # print(selection_region)
            regions = ['']
            for i in selection_region:
                regions = regions + [i[0]]
            combo_regions.configure(values=regions)

        # 7 NO FILTER
        if not filter_cmdr and not filter_region and not filter_bdata:

            selection_cmdr = cursor.execute("SELECT DISTINCT cmdr FROM codex ORDER BY cmdr").fetchall()
            cmdrs = ['']
            for i in selection_cmdr:
                cmdrs = cmdrs + [i[0]]
            combo_cmdr.configure(values=cmdrs)

            selection_region = cursor.execute("SELECT DISTINCT region FROM codex ORDER BY region").fetchall()
            regions = ['']
            for i in selection_region:
                regions = regions + [i[0]]
            combo_regions.configure(values=regions)

        connection.commit()

        return filter

    def create_button():
        global combo_cmdr, combo_regions, combo_bio_data, refresh_button, death_date_combo, sell_combo, sorting

        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        # Combo CMDRs
        selection = cursor.execute("SELECT DISTINCT cmdr FROM codex ORDER BY cmdr").fetchall()
        connection.commit()
        cmdrs = ['']
        for i in selection:
            cmdrs = cmdrs + [i[0]]
        label_tag = Label(buttons_frame, text="Filter:", bg='black', fg='white', font=("Helvetica", 11))
        label_tag.pack(side=LEFT, padx=29)
        combo_cmdr = ttk.Combobox(buttons_frame, state='readonly')
        combo_cmdr['values'] = cmdrs
        combo_cmdr.current(0)
        combo_cmdr.bind("<<ComboboxSelected>>", selected)
        combo_cmdr.pack(side=LEFT, padx=15)

        # Combobox Region
        selection = cursor.execute("SELECT DISTINCT region FROM codex ORDER BY region").fetchall()
        connection.commit()
        region = ['']
        for i in selection:
            region = region + [i[0]]
        combo_regions = ttk.Combobox(buttons_frame, state='readonly')
        combo_regions['values'] = region
        combo_regions.current(0)
        combo_regions.bind("<<ComboboxSelected>>", selected)
        combo_regions.pack(side=LEFT, padx=15)

        # Combobox Biodata
        selection = cursor.execute("SELECT DISTINCT data FROM codex ORDER BY data").fetchall()
        connection.commit()
        b_data = [(''), ('Aleoida'), ('Bacterium'), ('Cactoida'), ('Clypeus'), ('Concha'),
                  ('Electricae'), ('Fonticulua'), ('Fungoida'), ('Frutexa'), ('Fumerola'), ('Osseus'),
                  ('Recepta'), ('Stratum'), ('Tubus'), ('Tussock'), ('---------'),
                  ('Amphora Plant'), ('Anemone'), ('Bark Mounds'), ('Brain'),
                  ('Crystalline Shards'), ('Fumerola'), ('Tubers')]
        # for i in selection:
        #     b_data = b_data + [i[0]]
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
        begin_time.insert(0, '2021-05-19')
        begin_time.pack(side=LEFT, padx=10)
        # b_date = begin_time.get()

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

        codex_frame = Frame(tree, highlightbackground="blue", highlightthickness=1, bd=10)
        codex_frame.pack()
        connection.close()

    global tree_start
    tree_start = 0

    create_button()
    create_frame()
    codex_treeview()

    def selected_record(e): # Shows Picture of selected Item
        global my_img, my_label
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)
        selected_tree = codex_tree.focus()
        values = codex_tree.item(selected_tree, 'values')
        if values == ('0', 'DATE', 'TIME', 'COMMANDER', 'SPECIES', 'VARIANT', '', 'SYSTEM', 'BODY', 'REGION') \
                or \
                values == ('0', 'DATE', 'TIME', 'COMMANDER', 'SPECIES', 'VARIANT', '0', 'SYSTEM', 'BODY', 'In REGION '):
            return
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
                logger("File not found",log_var)
                logger(png, log_var)
                file = resource_path("images/Kein_Bild.png")
                image = Image.open(file)
                image = image.resize((320, 145))
                my_img = ImageTk.PhotoImage(image)
        else:
            return
        my_label = Label(tree, image=my_img)
        my_label.place(x=837, y=400)

    codex_tree.bind("<ButtonRelease-1>", selected_record)
    # connection.close()
    # refresh_view()
    refresh_treeview()


    if tree_start > 1:
        print('tree_start', tree_start)
        time.sleep(3.0)
        # refresh_view()
        refresh_treeview()
    else:
        tree_start += 1
        print('tree_start', tree_start)
    tree.mainloop()


def missing_codex(filter_cmdr, filter_region):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    global normal_view
    normal_view = 1

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cmdrs = cursor.execute("SELECT DISTINCT cmdr FROM codex").fetchall()
        # print(cmdrs)
        cursor.execute("DROP TABLE IF EXISTS codex_show")
        connection.commit()
        cursor.execute("""CREATE table IF NOT EXISTS codex_show (
                                cmdr TEXT,
                                data TEXT, 
                                region TEXT)
                                """)
        region = RegionMapData.regions
        # del region[0]

        select_show = cursor.execute("SELECT * from codex_show").fetchall()
        if not select_show:
            for cmdr in cmdrs:
                for a in region:
                    if a is not None:
                        for i in bio_worth:
                            cursor.execute("INSERT INTO codex_show VALUES (?, ?, ?)", (cmdr[0], i[0], a))
            connection.commit()
        # select all Codex Entrys from Codex
        temp = cursor.execute("SELECT DISTINCT cmdr, data, region FROM codex WHERE codex.codex = 1").fetchall()
        if temp:
            # print(temp)
            for i in temp:
                cmdr_select = cursor.execute("""SELECT * from codex_entry where data = ?
                                                and region = ?""", (i[1], i[2])).fetchall()
                delete_cmdr = str(i[0])
                delete_bio = str(cmdr_select[0][0])
                delete_region = str(cmdr_select[0][3])
                # Deletes Entrys from codex_show
                cursor.execute("DELETE FROM codex_show WHERE cmdr = ? AND data = ? AND region = ?",
                               (delete_cmdr, delete_bio, delete_region))
            connection.commit()

        if filter_cmdr and filter_region:
            select = cursor.execute("SELECT * FROM codex_show WHERE cmdr = ? and region = ?"
                                    "ORDER BY data",
                                    (filter_cmdr, filter_region)).fetchall()

        if filter_cmdr and not filter_region:
            select = cursor.execute("SELECT * FROM codex_show WHERE cmdr = ?"
                                    "ORDER BY data",
                                    (filter_cmdr,)).fetchall()

        if not filter_cmdr and filter_region:
            select = cursor.execute("SELECT * FROM codex_show WHERE region = ?"
                                    "ORDER BY data",
                                    (filter_region,)).fetchall()

        if not filter_cmdr and not filter_region:
            select = cursor.execute("SELECT * FROM codex_show ORDER BY region, data").fetchall()
    lauf = 1
    data = []
    for i in select:
        data.append((' ', ' ', i[0], i[1], ' ', ' ', ' ', i[2], 1, 1))
        lauf += 1
    return data


def get_info_for_bio_scan(data):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    timestamp = data['timestamp']
    scantype = data['ScanType']
    species = data['Species_Localised']
    system = data['SystemAddress']
    body = data['Body']
    # print(data)
    cursor.execute("""CREATE table IF NOT EXISTS star_map (
                                                starsystem TEXT,
                                                system_address TEXT,
                                                body_ID INTEGER,
                                                bodyname TEXT)""")
    select = cursor.execute("""SELECT bodyname from star_map where 
                                                system_address = ? and
                                                body_ID = ?""",
                            (system, body)).fetchall()
    if select != []:
        body_name = select[0][0]
    else:
        return

    cursor.execute("""CREATE table IF NOT EXISTS temp (
                                            timestamp TEXT,
                                            scantype TEXT,
                                            species TEXT,
                                            body TEXT)""")

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

    # print(count)

    for i in count:
        select_count = cursor.execute("""Select count(species) from temp where species = ? and body = ? """,
                                      (i[0], body_name)).fetchone()

        bio_name = i[0].split(' ')
        genus = bio_name[0]
        species_2 = bio_name[1]
        color = ''
        mark_missing = '0'
        count_1 =  select_count[0]
        if select_count[0] == 0:
            count_1 = 0
        if select_count[0] == 1:
            count_1 = 1
        if select_count[0] == 2:
            count_1 = 2
        if select_count[0] == 4:
            count_1 = 3

        insert_into_bio_db(body_name, count_1, genus, species_2, color, mark_missing)
    connection.close()


def get_info_for_get_body_name(data):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    starsystem = data.get('StarSystem')
    system_address = data.get('SystemAddress')
    body_ID = data.get('BodyID')
    bodyname = data.get('BodyName')
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("""CREATE table IF NOT EXISTS star_map (
                                            starsystem TEXT,
                                            system_address TEXT,
                                            body_ID INTEGER,
                                            bodyname TEXT)""")

    select = cursor.execute("""SELECT starsystem from star_map where 
                                            starsystem = ? and 
                                            system_address = ? and
                                            body_ID = ? and
                                            bodyname = ?""",
                            (starsystem, system_address, body_ID, bodyname)).fetchall()
    if select != []:
        return
    else:
        cursor.execute("INSERT INTO star_map VALUES (?, ?, ?, ?)",(starsystem, system_address, body_ID, bodyname))
        connection.commit()


def get_info_for_system_Scan(data):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    body_count = data['BodyCount'] # Anzahl der Himmelskörper
    system_name = data['SystemName']
    system_address = data['SystemAddress']
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("CREATE table IF NOT EXISTS starchart (SystemID INTEGER, SystemName TEXT, Count INTEGER)")
    select = cursor.execute("SELECT SystemName FROM starchart WHERE SystemID= ?", (system_address,)).fetchall()
    if select != []:
        count = cursor.execute("SELECT Count FROM starchart WHERE SystemID= ?", (system_address,)).fetchall()
        if count[0][0] == None:
            cursor.execute("Update starchart set count = ? WHERE SystemID= ?", (body_count, system_address,)).fetchall()
            connection.commit()
    else:
        cursor.execute("INSERT INTO starchart VALUES (?,?,?) ", (int(system_address), system_name, int(body_count)))
        connection.commit()
    connection.close()


def mark_planet(file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    with open(file, 'r', encoding='UTF8') as datei:
        for zeile in datei.readlines()[::-1]:  # Read File line by line reversed!
            data = read_json(zeile)
            if data.get('event') == 'Location' or data.get('event') == 'Disembark' or \
                    data.get('event') == 'SAAScanComplete':
                # print(data)
                # system_id = data.get('SystemAddress')
                body_name = data.get('Body')
                return body_name


def get_planet_info(data):
    # data['event'] == 'Scan' and data['ScanType'] == 'Detailed' and data['Landable']
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    # print(data)
    if data['Atmosphere']:
        system_id = data['SystemAddress']
        body_name = data['BodyName']
        if check_body(body_name) == 0:
            return
        planet_type = data['PlanetClass']
        body_atmos = data['Atmosphere']
        body_gravity = float(data['SurfaceGravity']) / 10
        body_temp = data['SurfaceTemperature']
        body_pressure = float(data['SurfacePressure']) / 100000
        body_distance = int(data['DistanceFromArrivalLS'])
        volcanism = data['Volcanism']
        if volcanism:
            # print(body_name, 'VOLCANISM Y ')
            volcanism = 'Y'
        else:
            # print(body_name, 'NO VOLCANISM')
            volcanism = 'N'
        material = []
        materials = ''

        for i in data['Materials']:
            material.append(i['Name'])
        for i in material:
            materials = materials + ' ' + str(i)
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        select = cursor.execute("SELECT star_class FROM stars WHERE SystemID= ?", (system_id,)).fetchall()
        if select != []:
            star_class = select[0][0]
        else:
            print('no star with ', system_id)
            return

        select = cursor.execute("SELECT SystemName FROM starchart WHERE SystemID= ?", (system_id,)).fetchall()
        if select != []:
            system_name = select[0][0]
        else:
            print('no SystemName with ', system_id)
            return

        body_name = body_name.replace(system_name, '')
        cursor.execute("""CREATE table IF NOT EXISTS planet_infos (
                                                                    SystemID INTEGER, 
                                                                    SystemName TEXT,
                                                                    StarClass TEXT,                                                                 
                                                                    BodyName TEXT,
                                                                    DistanceToMainStar TEXT,                                                                
                                                                    PlanetType TEXT,
                                                                    Atmosphere TEXT,
                                                                    Gravity TEXT,
                                                                    Temperature TEXT,
                                                                    Pressure TEXT,
                                                                    volcanism TEXT,
                                                                    Materials)""")

        select = cursor.execute("SELECT BodyName FROM planet_infos WHERE BodyName = ? and SystemName = ?"
                                , (body_name, system_name)).fetchall()
        # print('planet_infos' ,select)

        if select == []:
            cursor.execute("""INSERT INTO planet_infos VALUES (?,?,?,?,?,?,
                                                               ?,?,?,?,?,?) """,
                           (system_id, system_name, star_class, body_name, body_distance, planet_type,
                            body_atmos, body_gravity, body_temp, body_pressure, volcanism, materials))
            connection.commit()


def get_star_info(data):

    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    system_address = data['SystemAddress']
    star_class = data['StarClass']
    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    cursor.execute("CREATE table IF NOT EXISTS stars (SystemID INTEGER, star_class TEXT)")
    select = cursor.execute("SELECT SystemID FROM stars WHERE SystemID= ?", (system_address,)).fetchall()

    if select == []:
        cursor.execute("INSERT INTO stars VALUES (?,?) ", (system_address, star_class))
        connection.commit()
    connection.close()


def get_info_scan_planets(data):
    # data['event'] == 'FSSBodySignals':
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    body_name = data['BodyName']
    body_id = data['BodyID']
    system_address = data['SystemAddress']
    bio_count = 0
    region = (findRegionForBoxel(system_address)['region'][1])
    for signal in (data['Signals']):
        bio_count = (signal['Count'])
    for i in (data['Signals']):
        if 'Bio' in (i['Type_Localised']):
            insert_into_planet_bio_db(body_name, body_id, bio_count, region)
            if check_body(body_name) == 1:
                bios = get_species_for_planet(body_name)
                for i in bios:
                    bio = i.split(' ')
                    update_bio_db(body_name, bio_count, bio[0], bio[1])


def bio_scan(journal_file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    body_name = ''
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("""CREATE table IF NOT EXISTS temp (
                                            timestamp TEXT,
                                            scantype TEXT,
                                            species TEXT,
                                            body TEXT)""")
    search_string = '"event":"ScanOrganic"'
    bio_count = []
    with open(journal_file, 'r', encoding='UTF8') as datei:
        for zeile in datei:
            if zeile.find(search_string) > -1:
                data = json.loads(zeile)
                timestamp = data['timestamp']
                scantype = data['ScanType']
                species = data['Species_Localised']
                system = data['SystemAddress']
                body = data['Body']
                body_name = get_body_name(journal_file, system, body)
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

    count = cursor.execute("Select DISTINCT species, body from temp where body = ?",
                           (body_name,)).fetchall()
    count_bios = []
    for i in count:
        species_2 = i[0]
        select_count = cursor.execute("Select COUNT(species) from temp where species = ?",
                       (species_2,)).fetchone()
        count_bios.append(select_count)
    connection.close()


def get_body_name(journal_file, system, body):  # Anahnd des Systemnamens und der Body ID wird
                                                # der Name des Trabantens ermittelt
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    search_string = '"event":"Disembark"'
    bio_count = []
    with open(journal_file, 'r', encoding='UTF8') as datei:
        for zeile in datei:
            if zeile.find(search_string) > -1:
                data = json.loads(zeile)
                system_address = data['SystemAddress']
                body_ID = data['BodyID']
                if system == system_address and body == body_ID:
                    system_body = data['Body']
                    return system_body


def get_species_for_planet(body):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("""CREATE table IF NOT EXISTS temp (
                                            timestamp TEXT,
                                            scantype TEXT,
                                            species TEXT,
                                            body TEXT)""")
    select = cursor.execute("""SELECT species from temp where body = ?""", (body,)).fetchall()

    data = []
    for i in select:
        for a in i:
            data.append(a)
    return data


def get_bio_scan_count(bio, body_name): # Lese in der DB aus wie oft das BIO gescannt wurde
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    cursor.execute("""CREATE table IF NOT EXISTS temp (
                                            timestamp TEXT,
                                            scantype TEXT,
                                            species TEXT,
                                            body TEXT)""")

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
    print(b_date, e_date)

    if update != 3:
        order = 'cmdr, region, data, date_log, time_log'
    else:
        order = 'date_log desc, time_log DESC'

    bio_data = '%' + bio_data +'%'
    if bio_data == '%---------%':
        bio_data = ''


    if sf_cmdr and region and bio_data:
        data = cursor.execute("""SELECT * FROM codex where cmdr = ? and region = ? and data like ?
                              AND player_death = 0                              
                              AND date_log BETWEEN ? AND ? 
                              ORDER by """ + order,
                              (sf_cmdr, region, bio_data, b_date, e_date)).fetchall()
    # Fall 2 CMDR & Region
    elif sf_cmdr and region and not bio_data:
        data = cursor.execute("""SELECT * FROM codex where cmdr = ? and region = ?
                              AND player_death = 0                              
                              AND date_log BETWEEN ? AND ? 
                              ORDER by """ + order,
                              (sf_cmdr, region, b_date, e_date)).fetchall()
    # Fall 3 CMDR & Bio
    elif sf_cmdr and not region and bio_data:
        data = cursor.execute("""SELECT * FROM codex where cmdr = ? and data like ?
                              AND player_death = 0                              
                              AND date_log BETWEEN ? AND ?                               
                              ORDER by """ + order,
                              (sf_cmdr, bio_data, b_date, e_date)).fetchall()
    # Fall4 only CMDR
    elif sf_cmdr and not region and not bio_data:
        data = cursor.execute("""SELECT * FROM codex where cmdr = ?
                              AND player_death = 0                              
                              AND date_log BETWEEN ? AND ? 
                              ORDER by """ + order,
                              (sf_cmdr, b_date, e_date)).fetchall()
    # Fall 5 only Region
    elif not sf_cmdr and region and not bio_data:
        data = cursor.execute("""SELECT * FROM codex where region = ?
                              AND player_death = 0                              
                              AND date_log BETWEEN ? AND ?
                              ORDER by """ + order,
                              (region, b_date, e_date)).fetchall()
    # Fall 6 only Biodata
    elif not sf_cmdr and not region and bio_data:
        data = cursor.execute("""SELECT * FROM codex where data like ?
                              AND player_death = 0                              
                              AND date_log BETWEEN ? AND ? 
                              ORDER by """ + order,
                              (bio_data, b_date, e_date)).fetchall()
    # Fall 7 Region & Biodata
    elif not sf_cmdr and region and bio_data:
        data = cursor.execute("""SELECT * FROM codex where region = ? and data like ?
                              AND player_death = 0                              
                              AND date_log BETWEEN ? AND ? 
                              ORDER by """ + order,
                              (region, bio_data, b_date, e_date)).fetchall()
    # Fall 8 no Filter
    elif not sf_cmdr and not region and not bio_data:
        data = cursor.execute("""SELECT * FROM codex 
                              where player_death = 0 AND date_log BETWEEN ? AND ? 
                              ORDER by """ + order, (b_date, e_date)).fetchall()
        # ORDER by cmdr, region, data, date_log, time_log""", (b_date,e_date)).fetchall()
        # print(data)

    connection.commit()
    connection.close()
    # print(data)
    return data


def check_body(body_name):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    cursor.execute("""CREATE table IF NOT EXISTS planet_bio_info (
                                        body TEXT,
                                        body_id TEXT,
                                        count TEXT,
                                        region TEXT)""")

    select = cursor.execute("""SELECT body from planet_bio_info where body = ?""",
                            (body_name, )).fetchall()

    if select != []:
        # print('BODY in DB ' + body_name)
        return 1
    else:
        return 0


def check_system(journal_file, zeilenr):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    system_address = "blank"
    body = "blank"
    with open(journal_file, 'r', encoding='UTF8') as datei:
        for i, zeile in enumerate(datei):
            search_string = 'Disembark'
            if zeile.find(search_string) > -1:
                if zeilenr > i:
                    data = json.loads(zeile)
                    # print(data)
                    system_address = data['StarSystem']
                    body = data['Body']
        body = body.removeprefix(system_address)
    return system_address, body


def find_codex(journal_file, zeilenr, biodata):
    bio_color = ''
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    with open(journal_file, 'r', encoding='UTF8') as datei:
        for i, zeile in enumerate(datei):
            search_string = 'CodexEntry'
            if zeile.find(search_string) > -1:
                if zeilenr > i:
                    data = json.loads(zeile)
                    species = str(data['Name_Localised'])
                    tmp = species.split()
                    if len(tmp) > 3:
                        codex_bio = str(tmp[0]) + ' ' + str(tmp[1])
                        if biodata == codex_bio:
                            # print('gefunden')
                            bio_color = str(tmp[3])
                            break
                    else:
                        bio_color = ''
    # print(bio_color)
    return bio_color


def check_cmdr(journal_file):
    funktion = inspect.stack()[0][3] + " " + journal_file
    logger(funktion, log_var)

    cc_cmdr = ""
    with open(journal_file, 'r', encoding='UTF8') as datei:
        for zeile in datei:
            search_string = '"event":"Commander"'
            if zeile.find(search_string) > -1:
                data = json.loads(zeile)
                cc_cmdr = data['Name']
                break
    # print(cmdr)
    return cc_cmdr


def system_scan(journal_file): # Sucht im Logfile nach
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    # search_string = 'FSSDiscoveryScan'
    with open(journal_file, 'r', encoding='UTF8') as datei:
        for zeile in datei.readlines()[::-1]:  # Read File line by line reversed!
        # for zeile in datei:
            data = read_json(zeile)
            if data.get('event') == 'Location' or data.get('event') == "FSSDiscoveryScan":
                body_count = data.get('BodyCount')
                system_name = data.get('SystemName')
                if system_name == None:
                    system_name = data.get('StarSystem')
                system_address = data.get('SystemAddress')
                systems = (system_name, system_address, body_count)
                logger(systems, log_var)
                return systems


# def scan_planets(journal_file, current_system):
#     funktion = inspect.stack()[0][3]
#     logger(funktion, log_var)
#     global normal_view
#     search_string = '"event":"FSSBodySignals"'
#     data_2 = []
#     with open(journal_file, 'r', encoding='UTF8') as datei:
#         for zeile in datei:
#             if zeile.find(search_string) > -1:
#                 data = json.loads(zeile)
#                 body_name = data['BodyName']
#                 if check_body(body_name) == 1:
#                     bios = get_species_for_planet(body_name)
#                     for i in bios:
#                         bio_scan_count = get_bio_scan_count(i, body_name)
#                         bio = i.split(' ')
#                         update_bio_db(body_name, bio_scan_count[1], bio[0], bio[1])
#                     break
#                 body_id = data['BodyID']
#                 system_address = data['SystemAddress']
#                 if system_address == current_system[1]:
#                     # print(zeile)
#                     for signals in data['Signals']:
#                         count = signals['Count']
#                         signal_type = signals['Type_Localised']
#                         if 'Biolo' in signal_type:
#                             # print(data)
#                             biological = []
#                             gpi = get_plant_info(journal_file, body_name)
#                             logger('gpi', 1)
#                             logger(gpi, 1)
#                             cmdr_gp = check_cmdr(journal_file)
#                             region = (findRegionForBoxel(system_address)['region'][1])
#                             missing_in_region = (missing_codex(cmdr_gp, region))
#                             missing_bio = []
#                             for i in missing_in_region:
#                                 missing_bio.append(i[3])
#                             try :
#                                 body_distance = gpi[2]
#                             except TypeError:
#                                 gpi = ['','','']
#                             star_system = gpi[1]
#                             for i in gpi[0]:
#                                 biological.append(i[0])
#                             normal_view = 4
#                             data_2.append((body_name, body_distance, count, gpi[3], '', '', '', '', '', region))
#                             insert_into_planet_bio_db(body_name, gpi[3], body_distance, count, region)
#
#                             for count, bio in enumerate(biological):
#                                 bio_name = bio.split(' ')
#                                 genus = bio_name[0]
#                                 species = bio_name[1]
#                                 distance = (gpi[0][count][1])
#                                 color = (gpi[0][count][2])
#                                 temp = genus.capitalize() +' ' + species.capitalize()
#
#                                 bio_scan_count = get_bio_scan_count(bio, body_name)
#
#                                 mark_missing = 0
#                                 if temp in missing_bio:
#                                     mark_missing = 1
#                                 else:
#                                     mark_missing = 0
#                                 insert_into_bio_db(body_name, bio_scan_count[1], genus.capitalize(),
#                                                    species.capitalize(), color, mark_missing)
#
#                                 if count > 0:
#                                     bio_name = biological[count-1].split(' ')
#                                     genus2 = bio_name[0]
#                                     if genus == genus2:
#                                         genus = ''
#
#                                 data_2.append(('', body_name, bio_scan_count[0], genus.capitalize(),
#                                                species.capitalize(), color, distance,'', str(bio), mark_missing))
#
#     if data_2:
#         # print(data_2, ' data_2')
#         return data_2


# def get_plant_info(journal_file, body_name):
#     funktion = inspect.stack()[0][3]
#     logger(funktion, log_var)
#
#     search_string = '"ScanType":"Detailed"'
#     with open(journal_file, 'r', encoding='UTF8') as datei:
#         for zeile in datei:
#             if zeile.find(search_string) > -1:
#                 data = json.loads(zeile)
#                 body_name_new = data['BodyName']
#                 if body_name_new == body_name:
#                     planet_type = data['PlanetClass']
#                     body_atmos = data['Atmosphere']
#                     body_gravity = float(data['SurfaceGravity']) / 10
#                     body_temp = data['SurfaceTemperature']
#                     body_pressure = float(data['SurfacePressure']) / 100000
#                     body_distance = int(data['DistanceFromArrivalLS'])
#                     system = data['SystemAddress']
#                     system_name = data['StarSystem']
#                     material = []
#                     bio_names = []
#                     body_name_new = body_name_new.replace(system_name, '')
#                     for i in data['Materials']:
#                         material.append(i['Name'])
#                     bcd = []
#                     no_main_star = 0
#                     for i in data['Parents']:
#                         if 'Star' in str(i):
#                             no_main_star += 1
#                             star = i['Star']
#                             star_type = get_star(journal_file, system, star)
#                             bio_names = select_prediction_db(star_type, planet_type, body_atmos, body_gravity,
#                                                              body_temp)
#                             values = (star_type, planet_type, body_atmos, body_gravity, body_pressure,body_temp)
#                             # logger(values, log_var)
#                             # logger(bio_names, log_var)
#                             for i in bio_names:
#                                 get_cod = get_color_or_distance(i[0], star_type, material)
#                                 # print(get_cod, i[0], star_type, material)
#                                 i = (*i, get_cod[0][0][0], get_cod[1])
#                                 if get_cod[1]:
#                                     bcd.append(i)
#                     if no_main_star == 0:
#                         star = get_startype(journal_file, system)
#                         if star:
#                             star_type = get_startype(journal_file, system)
#                             bio_names = select_prediction_db(star_type, planet_type, body_atmos,
#                                                              body_gravity, body_temp)
#                             for i in bio_names:
#                                 get_cod = get_color_or_distance(i[0], star_type, material)
#                                 i = (*i, get_cod[0][0][0], get_cod[1])
#                                 if get_cod[1]:
#                                     bcd.append(i)
#                     return bcd, system_name, body_distance, body_name_new

#
# def get_startype(journal_file, system):
#     funktion = inspect.stack()[0][3]
#     logger(funktion, log_var)
#     search_string = '"event":"StartJump"'
#     with open(journal_file, 'r', encoding='UTF8') as datei:
#         for zeile in datei:
#             if zeile.find(search_string) > -1:
#                 data = json.loads(zeile)
#                 if data['JumpType'] == 'Hyperspace':
#                     if data['SystemAddress'] == system:
#                         return (data['StarClass'])

#
# def get_star(journal_file, system, star):
#     funktion = inspect.stack()[0][3]
#     logger(funktion, log_var)
#
#     search_string = '"event":"Scan"'
#     with open(journal_file, 'r', encoding='UTF8') as datei:
#         for zeile in datei:
#             if zeile.find(search_string) > -1:
#                 data = json.loads(zeile)
#                 if data['SystemAddress'] == system:
#                     if star == data['BodyID']:
#                         return(data['StarType'])


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


def create_DB_Bio_prediction():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    if check_table('Bio_prediction') == 1:
        return

    file = resource_path("bio_data2.txt")
    with open(file, 'r', encoding='UTF8') as datei:
        for zeile in datei.readlines():
            # print(zeile)
            zeile = zeile.rstrip('\n')
            zeile = zeile.split(';')
            try:
                zeile[1] = (zeile[1].split(','))                    # Stars
                zeile[2] = (zeile[2].split(','))  # Planets
                zeile[3] = (zeile[3].split(','))  # Pressure
                zeile[3] = float(zeile[3][0]), float(zeile[3][1])  # Pressure
                zeile[4] = (zeile[4].split(','))  # Gravity
                zeile[4] = float(zeile[4][0]), float(zeile[4][1])  # Gravity
                zeile[5] = (zeile[5].split(','))  # Athmosphere
                zeile[6] = (zeile[6].split(','))  # Temp
                zeile[6] = float(zeile[6][0]), float(zeile[6][1])  # Temp
                zeile[7] = str(zeile[7])  # Volcanism Y/N
            except IndexError:
                logger(zeile, 2)
            # print(zeile)
            insert_data_into_db(zeile)


def insert_data_into_db(bio_data):
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("""CREATE table IF NOT EXISTS Bio_prediction (
                    Name TEXT,
                    Startype TEXT,
                    Planettype TEXT,
                    Pressure_min FLOAT,
                    Pressure_max FLOAT,                    
                    Gravity_min FLOAT,
                    Gravity_max FLOAT,
                    Athmospere TEXT,
                    Temp_min FLOAT,
                    Temp_max FLOAT,
                    Volcanism TEXT)
                    """)
    # print(bio_data)
    for star in bio_data[1]:
        for planet in bio_data[2]:
            for athmospere in bio_data[5]:
                cursor.execute("INSERT INTO Bio_prediction VALUES (?,?,?,?,?,?,?,?,?,?,?)", (
                    bio_data[0],
                    star,
                    planet,
                    bio_data[3][0],
                    bio_data[3][1],
                    bio_data[4][0],
                    bio_data[4][1],
                    athmospere,
                    bio_data[6][0],
                    bio_data[6][1],
                    bio_data[7]))
    connection.commit()


create_DB_Bio_prediction()


def create_DB_Bio_color():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    if check_table('Bio_color') == 1:
        return

    file = resource_path("bio_color_distance.txt")
    with open(file, 'r', encoding='UTF8') as datei:
        for zeile in datei.readlines():
            # print(zeile)
            zeile = zeile.rstrip('\n')
            zeile = zeile.split(';')
            zeile[3] = (zeile[3].split(','))
            # print(zeile)
            for count, i in enumerate(zeile[3]):
                if count % 2 == 0:
                    # print(zeile[0], zeile[1], zeile[2],zeile[3][count], zeile[3][count + 1])
                    insert_into_db_bio_color(zeile[0], zeile[1], zeile[2], zeile[3][count], zeile[3][count + 1])
                    # exit(2)
            # insert_data_into_db(zeile)


def insert_into_db_bio_color(name, distance, criteria, criterium, color):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("""CREATE table IF NOT EXISTS Bio_color (
                    Name TEXT,
                    Distance INTEGER,
                    Criteria TEXT,
                    Criterium TEXT,
                    COLOR TEXT)""")
    cursor.execute("INSERT INTO Bio_color VALUES (?,?,?,?,?)",(name, distance, criteria, criterium, color))
    connection.commit()


create_DB_Bio_color()


def get_color_or_distance(bio_name, star, materials):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    bio_name = bio_name.split()
    bio_name2 = bio_name[0].capitalize() + ' ' + bio_name[1].capitalize()
    select = cursor.execute("""SELECT DISTINCT criteria, distance from bio_color where name = ?""",
                                (bio_name2,)).fetchall()
    mats = []
    distance = cursor.execute("""SELECT DISTINCT distance from bio_color where name = ?""",
                         (bio_name2,)).fetchall()
    if select[0][0] == 'Star':
        data = cursor.execute("""SELECT COLOR from bio_color where name = ? and Criterium = ?""",
                                (bio_name2, star)).fetchall()
        if data != []:
            data = data[0]
        # print('star', distance, data)
    else:
        data = []
        for mat in materials:
            mat = mat.capitalize()
            select = cursor.execute("""SELECT COLOR from bio_color where name = ? and Criterium = ?""",
                                (bio_name2, mat)).fetchall()
            if select:
                for i in select:
                    data.append(i[0])
    # print(distance, data)
    return distance, data


def select_prediction_db(star_type, planet_type ,body_atmos, body_gravity, body_temp, body_pressure, volcanism):
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
    # print('select Bio_prediction',  star_type, planet_type ,body_atmos,
    #       body_gravity, body_temp, body_pressure, volcanism)

    # volcanism wieder aus geschaltet, weil es nicht korrekt ermittelt wird.

    select_prediction = cursor.execute("""SELECT DISTINCT Name FROM Bio_prediction where
                                        Planettype = ? and
                                        Athmospere like ? and
                                        Gravity_min < ? and Gravity_max > ? and
                                        Temp_min <= ? and Temp_max >= ? and
                                        Pressure_min < ? and Pressure_max > ? 
                                        """,
                                       (planet_type, body_atmos, body_gravity, body_gravity,
                                        body_temp, body_temp, body_pressure, body_pressure) ).fetchall()
    # print(select_prediction)
    return select_prediction


def extract_engi_stuff(data, state):
    name = data.get('Name_Localised', 0)
    if name == 0:
        name = data.get('Name', 0)
    engi_stuff_ody_db(str(name), int(data['Count']), state)


def engi_stuff_ody_db(name, count, state):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("CREATE table IF NOT EXISTS odyssey (Name TEXT, Count INTEGER)")
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
    cursor.execute("CREATE table IF NOT EXISTS odyssey (Name TEXT, Count INTEGER)")
    # ody_select = cursor.execute("SELECT * FROM odyssey WHERE Name LIKE ? ORDER BY Name",
    #                             (filter_b,)).fetchall()
    ody_select = cursor.execute("SELECT * FROM odyssey ORDER BY Count DESC").fetchall()
    connection.close()
    # print(ody_select)
    return ody_select


def cp_to_clipboard():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    root.clipboard_clear()
    if eddc_modul == 1:
        root.clipboard_append(voucher.get_string(sortby="System"))
        root.clipboard_append('\n')
        root.clipboard_append('\n')
        root.clipboard_append(bgs.get_string(sortby="System"))
    elif eddc_modul == 3:
        root.clipboard_append(mats_table.get_string(sortby="Materials"))
    elif eddc_modul == 2:
        root.clipboard_append(mats_table.get_string(sortby="Materials"))
    root.update()


def menu(var):
    # Dem Modul entsprechenden werden GUI Elemente aus- bzw eingeschaltet oder de- bzw. aktiviert.

    global eddc_modul
    # print(var)
    menu_var = [0, 'BGS', 'ody_mats', 'MATS', 'CODEX', 'combat', 'thargoid']
    Filter.delete(0, END)
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


def insert_logfile_in_db(file):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("CREATE table IF NOT EXISTS logfiles (Name TEXT)")
    item = cursor.execute("SELECT Name FROM logfiles WHERE Name = ?", (file,)).fetchall()
    if not item:
        cursor.execute("INSERT INTO logfiles VALUES (?)", (file,))
        connection.commit()
    connection.close()


def select_last_log_file():
    # Vorletztes Logfile aus der Datenbank auslesen und übergeben.

    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("CREATE table IF NOT EXISTS logfiles (Name TEXT)")
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
    # print('filename', filenames_codex)
    last_log_file = select_last_log_file()[0]
    logger(last_log_file, log_var)
    # print('the log-file before the last from DB ', last_log_file)
    if last_log_file != '0':
        lauf = 0
        for i in filenames_codex:
            if i != last_log_file:
                lauf += 1
            else:
                # print(i, last_log_file)
                break
        # print(filenames_codex)
        if len(filenames_codex) > 1:
            i = 0
            # Alle Logfiles vor dem last_log_file werden aus der Liste entfernt
            while i < lauf:
                filenames_codex.pop(0)
                i += 1
    # nur die neuesten Logfiles und die letzen zwei schon eingelesenen werden übergeben.
    # print(filenames_codex)
    return filenames_codex


def read_codex_entrys():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    system.delete('1.0', END)
    system.insert(END, 'Codex Daten werden gelesen \n')
    # Lade alle logfiles in die Variable filenames_codex
    # filenames_codex = glob.glob(path + "\\Journal.*.log")
    filenames = file_names(1)
    # print(filenames)
    last_log = (len(filenames))
    # print(last_log)
    check_last_logs(filenames, last_log)
    # print(filenames)
    count = 1
    for count, filename in enumerate(filenames):
        if count % 10 == 0:
            # time.sleep(0.1)
            system.delete('1.0', END)
            postion = 'File \t' + str(count) + ' of ' + str(len(filenames))
            system.insert(END, str(postion))
        # time.sleep(0.5)
        read_bio_data(filename)
        read_log_codex(filename)
        read_player_death(filename)
        insert_logfile_in_db(filename)
    system.delete('1.0', END)
    postion = 'File \t' + str(count + 1) + ' of ' + str(len(filenames))
    system.insert(END, str(postion))
    system.insert(END, '\nDaten wurden eingelesen')
    time.sleep(1)
    # if count+1 == len(filenames) and len(filenames) > 1:
    #     vat = 0


def run_once_rce(filenames):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    if len(filenames) > 5:
        print('start run_once')
        thread_rce = threading.Thread(target=read_codex_entrys, args=())
        thread_rce.start()
        print('stop run_once')
    else:
        read_codex_entrys()


def wait_to_finish():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    success = 0
    files = file_names(1)
    count_files = len(files)
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    item = cursor.execute("SELECT count(*) FROM logfiles", ()).fetchall()
    xx = int(item[0][0])
    while xx < count_files:
        time.sleep(1)
        item = cursor.execute("SELECT count(*) FROM logfiles", ()).fetchall()
        xx = int(item[0][0])
        # print(count_files, item[0][0])
        success = 1
    return success


def combat_rank():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
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
                    data = json.loads(zeile)
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
    # print(ranking)
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
    s = 'Summe', 0,summe
    system.insert(END, ('───────────────────────────\n'))
    system.insert(END, ((str(s[0])) + '\t \t \t \t' + (str(s[2])) + ' \n'))
    system.insert(END, ('───────────────────────────\n'))


def get_filenames_of_last_7_days():
    filenames = []
    system.delete(1.0, END)
    today = str(datetime.now())[0:10].split('-')
    i = 0
    while i <= 7:
        file = older_logs(today, i)
        if file:
            for f in file:
                filenames.append(f)
        i += 1
    return filenames


def thargoids():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    system.delete(1.0, END)
    b_filter = Filter.get()
    filenames = file_names(0)
    # print(filenames)
    thargoid_rewards = [('Thargoid Scout', 80000, 0),
                        ('Thargoid Cyclops', 8000000, 0),
                        ('Thargoid Basilisk', 24000000, 0),
                        ('Thargoid Medusa', 40000000, 0),
                        ('Thargoid Hydra', 60000000, 0)]

    for filename in filenames:
        with open(filename, 'r', encoding='UTF8') as datei:
            for zeile in datei:
                search_string = 'VictimFaction_Localised":"Thargoids'
                search_string2 = '"event":"FactionKillBond"'
                if (zeile.find(search_string2)) > -1 and (zeile.find(search_string)) > -1:
                    data = read_json(zeile)
                    reward = data['Reward']
                    # print(reward)
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
    s = 'Summe', 0,summe
    system.insert(END, ('───────────────────────────\n'))
    system.insert(END, ((str(s[0])) + '\t \t \t' + (str(s[2])) + ' \n'))
    system.insert(END, ('───────────────────────────\n'))
    return


def auswertung(eddc_modul):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    logger('lösche tabellen', log_var)

    cursor.execute("DROP TABLE IF EXISTS influence")
    cursor.execute("DROP TABLE IF EXISTS odyssey")
    cursor.execute("DROP TABLE IF EXISTS vouchers")
    system.delete(.0, END)
    last_log_file = select_last_log_file()[0]
    # print('the log-file before the last from DB ', last_log_file)
    if last_log_file != '0' or eddc_modul != 4:
        filenames = file_names(0)  # Alle Logfiles der Eingabe entsprechend
    else:
        filenames = file_names(1)  # Alle Logfiles
    nodata = 0

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
        if eddc_modul == 4:
            logger('Test', 1)
            xx = select_last_log_file()[0]
            if xx == '0':
                filenames = file_names(1)
            logger('Keine Log-Files für Heute vorhanden', 1)
            read_codex_entrys()
            treeview_codex()
        else:
            system.insert(END, 'Keine Log-Files für den Tag vorhanden')
    else:
        if eddc_modul == 1: # BGS Main
            star_systems_db(filenames)
            filenames = file_names(0)
            for filename in filenames:
                einfluss_auslesen(filename)
                redeem_voucher(filename)
                multi_sell_exploration_data(filename)
                market_sell(filename)
            b_filter = Filter.get()
            data = print_vouchers_db(b_filter)
            if data:
                system.insert(END,
                              '    ----------    Bounty, Bonds, ExplorerData and Trade ...    ----------\n\n')
                for i in data:
                    tmp = f"{i[3]:,}"
                    tmp = tmp.replace(',', '.')
                    tmp = tmp + ' Cr'
                    system.insert(END, ((str(i[1])[0:15]) + '\t\t' + (str(i[2])[0:25]) + '\t\t\t' + (str(i[0])[0:15])
                                        + '\n\t\t\t\t\t' + tmp + '\n'))
                    voucher.add_row((i[0], i[1], i[2], tmp))
                system.insert(END,
                              (
                                  '\n    -----------------------------------  Influence  '
                                  '-----------------------------------\n'))
                system.insert(END, '\n')
            else:
                nodata = 1
                logger('NO VOUCHER DATA', 3)
            data = print_influence_db(b_filter)
            if data:
                for i in data:
                    system.insert(END, ((str(i[0])[0:15]) + '\t\t' + (str(i[1])[0:25]) + '\t\t\t\t' + str(i[2]) + '\n'))
                    bgs.add_row((i[0], i[1], i[2]))
            else:
                logger('NO INFLUENCE DATA', 2)
                if nodata == 1:
                    system.insert(END, '\n\tKeine Daten vorhanden')

        elif eddc_modul == 3: # Collected Enginieering Material
            star_systems_db(filenames)
            for filename in filenames:
                mats_auslesen(filename)
            b_filter = Filter.get()
            data = print_engi_stuff_db(b_filter)
            summe = 0
            for i in data:
                system.insert(END, ((str(i[0]).capitalize()) + '\t \t \t \t \t' + (str(i[1])) + '\n'))
                mats_table.add_row((i[0], i[1]))
                summe += i[1]
            a = 'Summe', summe
            system.insert(END, ('─────────────────────────────────\n'))
            system.insert(END, ((str(a[0])) + '\t \t \t \t \t' + (str(a[1])) + '\n'))
            system.insert(END, ('─────────────────────────────────\n'))

        elif eddc_modul == 2: # Collected Odyssey on Foot Material
            star_systems_db(filenames)
            logger('ody_mats == 1', 2)
            for filename in filenames:
                ody_mats_auslesen(filename)
            b_filter = Filter.get()
            data = print_engi_stuff_db(b_filter)
            summe = 0
            for i in data:
                system.insert(END, ((str(i[0])) + '\t \t \t \t' + (str(i[1])) + '\n'))
                mats_table.add_row((i[0], i[1]))
                summe += i[1]
            a = 'Summe', summe
            system.insert(END, ('───────────────────────────\n'))
            system.insert(END, ((str(a[0])) + '\t \t \t \t' + (str(a[1])) + '\n'))
            system.insert(END, ('───────────────────────────\n'))

        elif eddc_modul == 4: # Codex Treeview
            # system.insert(END, 'Codex Daten werden gelesen')
            run_once_rce(filenames)
            last_log_file = select_last_log_file()[0]
            if last_log_file != '0':
                treeview_codex()

        elif eddc_modul == 5: # Kampfrang
            combat_rank()

        elif eddc_modul == 6: # Thargoid
            thargoids()


def set_language_db(var):
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    # print('before ', var)
    cursor.execute("""CREATE table IF NOT EXISTS lan_db 
    (lang TEXT, switch INTEGER)""")

    if var == 'leer':

        item = cursor.execute("SELECT lang FROM lan_db").fetchall()
        # print(item)
        if not item:
            cursor.execute("INSERT INTO lan_db VALUES (?, ?)", ('german', '1'))
            connection.commit()
        else:
            connection.close()
            return item
        connection.close()
        # return select
    elif var == 'german':
        cursor.execute("UPDATE lan_db SET lang = ?", (var,))
        connection.commit()
        connection.close()

    elif var == 'english':
        cursor.execute("UPDATE lan_db SET lang = ?", (var,))
        connection.commit()
        connection.close()
    # print('after ', var)
    return var


def update_db():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("ALTER TABLE starchart RENAME TO TempOldTable")
    cursor.execute("CREATE table IF NOT EXISTS starchart (SystemID INTEGER, SystemName TEXT, Count INTEGER)")
    cursor.execute("INSERT INTO starchart (SystemID, SystemName) Select SystemID, SystemName FROM TempOldTable")


    connection.commit()
    connection.close()


def db_version(): # Programmstand und DB Stand werden mit einander verglichen
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("""CREATE table IF NOT EXISTS db_version (version INTEGER)""")
    item = cursor.execute("SELECT version FROM db_version").fetchall()
    # print(item[0][0], version_number)
    if not item:
        cursor.execute("INSERT INTO db_version VALUES (?)", (version_number,))
        connection.commit()
        connection.close()
    elif item[0][0] != version_number:
        cursor.execute("UPDATE db_version set version = ?", (version_number,))
        connection.commit()
        connection.close()
        logger('Update Version', 2)
        update_db()
        # connection.commit()
    elif item[0][0] == version_number:
        logger('Same Version', 2)
        connection.close()


def delete_all_tables():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)

    box = messagebox.askyesno("Delete all Data?", "Delete all Data?")
    if box:
        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        tables = cursor.execute("SELECT name FROM sqlite_schema WHERE type='table'").fetchall()
        for table in tables:
            x = (table[0])
            statement = 'DROP TABLE IF EXISTS ' + str(x)
            cursor.execute(statement)
        connection.commit()
        create_tables()


def create_tables():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    cursor.execute("""CREATE table IF NOT EXISTS codex (
                    date_log date,
                    time_log timestamp,
                    cmdr TEXT,
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

    cursor.execute("""CREATE table IF NOT EXISTS codex_show (
                            cmdr TEXT,
                            data TEXT, 
                            region TEXT)
                            """)

    cursor.execute("""CREATE table IF NOT EXISTS codex_entry (
                    data TEXT,
                    worth INTEGER,
                    type INTEGER, 
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
                                                                        SystemID INTEGER, 
                                                                        SystemName TEXT,
                                                                        StarClass TEXT,                                                                 
                                                                        BodyName TEXT,
                                                                        DistanceToMainStar TEXT,                                                                
                                                                        PlanetType TEXT,
                                                                        Atmosphere TEXT,
                                                                        Gravity TEXT,
                                                                        Temperature TEXT,
                                                                        Pressure TEXT,
                                                                        volcanism TEXT,
                                                                        Materials)""")

    cursor.execute("""CREATE table IF NOT EXISTS planet_bio_info (
                                        body TEXT,
                                        body_id TEXT,
                                        count TEXT,
                                        region TEXT)""")


    cursor.execute("""CREATE table IF NOT EXISTS bio_info_on_planet (
                                        body TEXT,
                                        genus TEXT,
                                        species TEXT,
                                        bio_scan_count INTEGER,
                                        mark_missing TEXT)""")

    cursor.execute("""CREATE table IF NOT EXISTS star_map (
                                                starsystem TEXT,
                                                system_address TEXT,
                                                body_ID INTEGER,
                                                bodyname TEXT)""")

    cursor.execute("CREATE table IF NOT EXISTS starchart (SystemID INTEGER, SystemName TEXT, Count INTEGER)")


    cursor.execute("""CREATE table IF NOT EXISTS temp (
                                            timestamp TEXT,
                                            scantype TEXT,
                                            species TEXT,
                                            body TEXT)""")

    create_codex_entry()

    create_DB_Bio_prediction()

    create_DB_Bio_color()


# noinspection PyGlobalUndefined
def main():
    funktion = inspect.stack()[0][3]
    logger(funktion, log_var)
    global system, root, Tag, Monat, Jahr, tick_hour_label, tick_minute_label, eddc_modul, ody_mats, \
        vor_tick, nach_tick, Filter, tree, check_but  # , label_tag, label_monat, label_jahr

    create_tables()
    select = set_language_db('leer')
    if not select or select[0][0] == 'german' or select == 'leer':
        text = ['Tag', 'Monat', 'Jahr', 'Der letzte Tick war um:', 'vor dem Tick', 'nach dem Tick']
    else:
        text = ['Day', 'Month', 'Year', 'Last BGS TICK was at  ', 'before Tick', 'after Tick']

    root = Tk()
    root.title('Elite Dangerous Data Collector')
    try:
        img = resource_path("eddc.ico")
        root.iconbitmap(img)
    except TclError:
        print('Icon not found)')

    root.configure(background='black')
    root.minsize(415, 500)
    root.maxsize(415, 500)
    snpx = resource_path("SNPX.png")
    horizon = resource_path("Horizon.png")
    bg = PhotoImage(file=snpx)
    bg2 = PhotoImage(file=horizon)

    my_menu = Menu(root)
    root.config(menu=my_menu)

    file_menu = Menu(my_menu, tearoff=False)
    my_menu.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="BGS", command=lambda: menu('BGS'))
    file_menu.add_command(label="Codex", command=lambda: menu('CODEX'), accelerator= "Ctrl+q")
    file_menu.add_command(label="MATS", command=lambda: menu('MATS'))
    file_menu.add_command(label="Odyssey", command=lambda: menu('ody_mats'))
    file_menu.add_command(label="Combat Rank", command=lambda: menu('combat'))
    file_menu.add_command(label="Thargoids", command=lambda: menu('thargoid'))
    # file_menu.add_command(label="Wing_Missions", command=wing_missions)
    # file_menu.add_command(label="Read Logs", command=start_read_logs)
    file_menu.bind_all("<Control-q>", lambda e: menu('CODEX'))
    file_menu.add_command(label="Exit", command=root.quit)
    settings_menu = Menu(my_menu, tearoff=False)
    my_menu.add_cascade(label="Setting", menu=settings_menu)
    about_menu = Menu(my_menu, tearoff=False)
    my_menu.add_cascade(label="About", menu=about_menu)
    about_menu.add_command(label="Version Check", command=lambda: get_latest_version(0))
    about_menu.add_command(label="Delete all Data in DB", command=lambda: delete_all_tables())

    my_top_logo = Label(root, image=bg, bg='black')
    my_top_logo.pack(fill=X)
    my_bottom_logo = Label(root, image=bg2, bg='black')
    my_bottom_logo.place(x=0, y=100)
    # --------------------------------- my_text_box -----------------------------------
    my_text_box = Label(root, bg='black', borderwidth=2)
    my_text_box.config(width=280)
    # my_text_box = Label(root)
    my_text_box.place(x=25, y=100)

    # --------------------------------- my_time_label -----------------------------------

    # my_time_label = Frame(my_text_box, bg='black')
    my_time_label = Frame(my_text_box, bg='black', borderwidth=2)
    my_text_box.config(width=250)
    my_time_label.pack(pady=5)
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

    # my_time_label

    global check_auto_refresh

    # bgs_tick_frame
    global last_tick_label

    bgs_tick_frame = Frame(my_text_box, bg='black', borderwidth=2)
    # bgs_tick_frame = Frame(my_text_box, bg='black')
    bgs_tick_frame.pack(side=LEFT, pady=5)
    last_tick_label = Label(bgs_tick_frame, text=text[3], bg='black', fg='white', font=("Helvetica", 12), justify=LEFT)
    last_tick_label.grid(column=0, row=0)

    # my_tick

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

    # my_tick
    my_check_box_place = Frame(root, bg='black', borderwidth=2)
    my_check_box_place.place(x=300, y=100)
    check_auto_refresh = IntVar()
    #
    check_but = Checkbutton(my_check_box_place, text="Autorefresh    ",
                            variable=check_auto_refresh,
                            bg='black',
                            fg='white',
                            selectcolor='black',
                            activebackground='black',
                            activeforeground='white',
                            command=threading_auto,
                            font=("Helvetica", 10))
    check_but.pack()

    # my_boxes

    my_boxes = Frame(root, bg='black', borderwidth=2)
    my_boxes.place(x=300, y=125)

    v = IntVar()
    vor_tick = Radiobutton(my_boxes,
                           text=text[4], bg='black', fg='white', selectcolor='black',
                           activebackground='black', activeforeground='white',
                           # padx=10,
                           variable=v,
                           value=1, command=tick_false)
    vor_tick.grid(column=0, row=0, sticky=W)

    nach_tick = Radiobutton(my_boxes,
                            text=text[5], bg='black', fg='white', selectcolor='black',
                            activebackground='black', activeforeground='white',
                            # padx=10,
                            variable=v,
                            value=2, command=tick_true)
    nach_tick.grid(column=0, row=1, sticky=W)
    nach_tick.select()

    # my_folder

    my_folder = Frame(root, bg='black')
    my_folder.place(x=15, y=180)
    myfolder_grid = Frame(my_folder, bg='black')
    myfolder_grid.grid()

    label_filter = Label(myfolder_grid,
                         text="Filter:",
                         bg='black',
                         fg='white',
                         font=("Helvetica", 12))
    label_filter.grid(column=0, row=0, sticky=W)
    Filter = Entry(myfolder_grid, width=37, font=("Helvetica", 10))

    Filter.insert(0, filter_name)
    Filter.grid(column=0, row=0)

    folder = Entry(myfolder_grid, width=62, bg='black', fg='white', font=("Helvetica", 8))
    folder.insert(END, path)
    folder.grid(column=0, row=1, pady=5)
    # my_folder

    system = Text(root, height=14, width=54, bg='black', fg='white', font=("Helvetica", 10))
    system.place(x=15, y=235)

    version_but = Button(root,
                         text=current_version,
                         activebackground='#000050',
                         activeforeground='white',
                         bg='black',
                         fg='white',
                         command=logging,
                         font=("Helvetica", 10))
    version_but.place(x=15, y=465)

    def cp_to_clipboard():
        funktion = inspect.stack()[0][3]
        logger(funktion, log_var)

        root.clipboard_clear()
        if eddc_modul == 1:
            root.clipboard_append(voucher.get_string(sortby="System"))
            root.clipboard_append('\n')
            root.clipboard_append('\n')
            root.clipboard_append(bgs.get_string(sortby="System"))
        elif eddc_modul == 3:
            root.clipboard_append(mats_table.get_string(sortby="Materials"))
        elif eddc_modul == 2:
            root.clipboard_append(mats_table.get_string(sortby="Materials"))
        root.update()


    clipboard = Button(root,
                       text='Copy to Clipboard',
                       activebackground='#000050',
                       activeforeground='white',
                       bg='black',
                       fg='white',
                       command=cp_to_clipboard,
                       font=("Helvetica", 10))
    clipboard.place(x=175, y=465)

    ok_but = Button(root,
                    # width=4,
                    activebackground='#000050',
                    activeforeground='white',
                    text='OK',
                    bg='black',
                    fg='white',
                    command=threading_auto,
                    font=("Helvetica", 10))
    ok_but.place(x=368, y=465)

    def callback(event):
        funktion = inspect.stack()[0][3]
        logger(funktion, 1)
        logger(event,1)
        threading_auto()

    root.bind('<Return>', callback)

    def refresh_label(data):
        label_tag.config(text=data[0])
        label_monat.config(text=data[1])
        label_jahr.config(text=data[2])
        last_tick_label.config(text=data[3])
        vor_tick.config(text=data[4])
        nach_tick.config(text=data[5])

    def set_language(language):
        if language == 1:
            data = ['Tag', 'Monat', 'Jahr', 'Der letzte TICK war um ', 'vor dem Tick', 'nach dem Tick']
            set_language_db('german')
        # elif language == 2:
        else:
            data = ['Day', 'Month', 'Year', 'Last BGS TICK was at ', 'before Tick', 'after Tick']
            set_language_db('english')
        refresh_label(data)
        # return data

    def language_de():
        language = 1
        set_language(language)

    def language_en():
        language = 2
        set_language(language)

    settings_menu.add_command(label="Sprache - Deutsch", command=language_de)
    settings_menu.add_command(label="Language - English", command=language_en)

    get_latest_version(1)
    root.mainloop()



last_tick()

main()

