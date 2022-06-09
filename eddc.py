# Created by MajorK https://github.com/SNP-MajorK/ED-DataCollector

import glob
import threading
import time
import sqlite3
import inspect
import os
import webbrowser
from builtins import print
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from distutils.version import StrictVersion
from PIL import ImageTk, Image
from pathlib import Path
from winreg import *
from datetime import date, timedelta, datetime
import requests
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
b_date = '2021-05-19'
e_date = '2040-01-01'
success = FALSE
t_hour = 'Tick Time'
t_minute = 'Tick Minute'
inf_data = ''
docked = ''
bio_worth = []
version_number = '0.6.0.0'
current_version = ('Version ' + str(version_number))
bgs = PrettyTable(['System', 'Faction', 'Influence'])
voucher = PrettyTable(['Voucher', 'System', 'Faction', 'Credits'])
mats_table = PrettyTable(['Materials', 'Count'])

# Set Program Path Data to random used Windows temp folder.
with OpenKey(HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders") as key:
    value = QueryValueEx(key, '{4C5C32FF-BB9D-43B0-B5B4-2D72E54EAAA4}')
path = value[0] + '\\Frontier Developments\\Elite Dangerous\\'
# path = value[0] + '\\Frontier Developments\\Franky'
# path = value[0] + '\\Frontier Developments\\Test'

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


database = resource_path("eddc.db")


def get_latest_version(var):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

    try:
        response = requests.\
            get("https://raw.githubusercontent.com/SNP-MajorK/ED-DataCollector/codex_testing/version.json"
                , timeout=1)
        my_json = json.loads(response.text)
    except requests.exceptions.ConnectionError:
        my_json = json.loads('[{"version": "0.0.0.0", "hyperlink": "link"}]')
        messagebox.showwarning("Check failed", "No Internet Connection")
    db_version()

    for d in my_json:
        new_version = d['version']
        link = d['hyperlink']
        live_version = new_version[:-2]
        cur_version = version_number[:-2]
        if StrictVersion(cur_version) == StrictVersion(live_version):
            print('no update needed')
            if var != 1:
                messagebox.showinfo("No Update available", ("Already newest Version " + live_version))
        elif StrictVersion(live_version) > StrictVersion(cur_version):
            box = messagebox.askyesno("Update available", "New Version available\nOpen Downloadpage")
            if box:
                webbrowser.open(link, new=0, autoraise=True)


def last_tick():
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

    try:
        response = requests.get("https://elitebgs.app/api/ebgs/v5/ticks", timeout=1)
        todos = json.loads(response.text)
    except requests.exceptions.ConnectionError:
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
    if log_var > 2:
        print('function ' + inspect.stack()[0][3] + ' Var = '+ str(var))
    update_eleven = datetime(2022, 3, 14)
    tag2 = Tag.get()
    tag2 = str(int(tag2) - var).zfill(2)
    monat2 = Monat.get()
    jahr2 = Jahr.get()
    if var == 0:
        search_date = datetime(int("20" + jahr2), int(monat2), int(tag2))
        if search_date > update_eleven:
            journal_date = ("20" + str(jahr2) + "-" + str(monat2) + "-" + str(tag2) + "T")
            files = glob.glob(path + "\\Journal." + journal_date + "*.log")
            if log_var > 2:
                print(files)
            return files
        else:
            journal_date = str(jahr2 + monat2 + tag2)
            filenames = glob.glob(path + "\\Journal." + journal_date + "*.log")
            if log_var > 2:
                print(filenames)
            return filenames
    else:
        filenames = glob.glob(path + "\\Journal.*.log")
        fils = (glob.glob(path + "\\Journal.202*.log"))
        for i in fils:
            filenames.remove(i)
        for i in fils:
            filenames.append(i)
        # print(update_eleven)
        return filenames


def date_for_ma(mission_id, gmd_faction, x):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    mission_found = False
    while x < 7:
        filenames = file_names(0)
        for filename in filenames:
            if get_mission_data(mission_id, filename, gmd_faction):
                mission_found = True
                return mission_found
        x += 1


def get_mission_data(mission_id, journal_file, gmd_faction):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
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
                            if log_var > 2:
                                print(inf_data)
                                print(mission_id + mission_found)
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
                            # print(data)
                            if log_var > 1:
                                print('gmd - else : ' + str(data['Faction']) + ' ' + str(gmd_faction))
                            docked = ''
                            return docked
                    else:
                        mission_found = False
                        # print(gmd_zeile)
                        # print('gmd_ ' + str(mission_found) + " " + str(gmd_mission_id))


def get_faction_for(system_address):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
        print(system_address)
    filenames = file_names(0)
    for filename in filenames:
        with open(filename, 'r', encoding='UTF8') as datei:
            line = 0
            for zeile in datei:
                line += 1
                search_string = "FSDJump"
                if (zeile.find(search_string)) > -1:
                    data = json.loads(zeile)
                    faction = (data['SystemFaction']['Name'])
                    return faction


def log_date(timestamp):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
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
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    try:
        for p in data["FactionEffects"]:
            if log_var == 3:
                print(data['timestamp'])
            if p['Faction'] != '':
                if log_var == 3:
                    print('MissionID ' + str(data['MissionID']))
                ed_faction = (p['Faction'])
                mission_id = data['MissionID']
                if not p['Influence']:
                    print("extract_data no Data in p['Influence']")
                    # print(p)
                    if log_var > 3:
                        print(p['Influence'])
                    mission_found = False
                    date_for_ma(mission_id, ed_faction, 0)
                    if docked:
                        p['Influence'] = [{'SystemAddress': docked, 'Trend': 'UpGood', 'Influence': inf_data}]
                    else:
                        p['Influence'] = [{'SystemAddress': docked, 'Trend': 'UpGood', 'Influence': ''}]
                extract_influence(p)
            else:
                print('No Faction in LOG')
                print(p['Influence'])


    except KeyError:
        print('extract_data  - exception')
        ed_faction = (data['Faction'])
        mission_id = data['MissionID']
        date_for_ma(mission_id, ed_faction, 0)
        data['Influence'] = [{'SystemAddress': docked, 'Trend': 'UpGood', 'Influence': inf_data}]
        if log_var == 3:
            print(data['Influence'])
        extract_influence(data)
    # ================================ End of extract_data


def extract_influence(data):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
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


def star_systems_db(filenames):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    for filename in filenames:
        with open(filename, 'r', encoding='UTF8') as datei:
            for zeile2 in datei:
                search_string2 = "FSDJump"
                if (zeile2.find(search_string2)) > -1:
                    star_systems_data = json.loads(zeile2)
                    starchart_db(star_systems_data['SystemAddress'], star_systems_data['StarSystem'])


def influence_db(sys_id, Faction, Influence):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
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
            if log_var > 2:
                print('DB Else')
            cursor.execute("INSERT INTO influence VALUES (?, ?, ?)", (system_name, Faction, Influence))
            connection.commit()
    connection.close()


def update_influence_db(upd_inf_id, faction, Influence):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
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
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
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
            if log_var > 1:
                print('read_inf_db ' + str(ID) + '  ' + str(faction))
                print('not yet in DB')


def print_influence_db(filter_b):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    filter_b = '%' + filter_b + '%'
    cursor.execute("CREATE table IF NOT EXISTS influence (SystemName TEXT, Faction TEXT, Influence INTEGER)")
    data = cursor.execute("SELECT * FROM influence WHERE SystemName LIKE ? OR Faction LIKE ? GROUP BY 1, 2, 3",
                          (filter_b, filter_b)).fetchall()
    connection.close()
    return data


def starchart_db(sd_id, system_name):
    # if log_var > 2:
    #     print('function ' + inspect.stack()[0][3])
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("CREATE table IF NOT EXISTS starchart (SystemID INTEGER, SystemName TEXT)")
    cursor.execute("SELECT SystemID FROM starchart WHERE SystemID= ?", (sd_id,))
    result = cursor.fetchall()
    if not result:
        # Wenn ID Systemname nicht in Tabelle vorhanden ist, wird sie hinzugefügt
        cursor.execute("INSERT INTO starchart VALUES (?, ?)", (sd_id, system_name,))
        connection.commit()
    connection.close()


def read_starchart_table(system_id):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    if isinstance(system_id, int):
        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        cursor.execute("CREATE table IF NOT EXISTS starchart (SystemID INTEGER, SystemName TEXT)")
        system_name = cursor.execute("SELECT SystemName FROM starchart WHERE SystemID = ?", (system_id,)).fetchall()
        try:
            connection.close()
            return system_name[0][0]
        except IndexError:
            print('SystemAddress =  ' + str(system_id))
            connection.close()


def einfluss_auslesen(journal_file):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    tick_hour = tick_hour_label.get()
    tick_minute = tick_minute_label.get()
    tick_time[3] = tick_hour[0:2]
    tick_time[4] = tick_minute[0:2]
    if log_var == 5:
        print(tick_time)
    # print(journal_file)
    with open(journal_file, 'r', encoding='UTF8') as datei:
        for zeile in datei:
            search_string = "MissionCompleted"
            if (zeile.find(search_string)) > -1:
                data = json.loads(zeile)
                if log_var > 1:
                    print('function ' + inspect.stack()[0][3])
                    print(data)
                # Verarbeite die Daten dem TICK entsprechend
                if check_tick_time(zeile, tick):
                    # print(data)
                    extract_data(data)
    # Starchart aktualisieren!
    # starsystem(3)
    # =========================================== End of dateien_einlesen()


def check_tick_time(zeile, ea_tick):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    tag2 = Tag.get()
    monat2 = Monat.get()
    jahr2 = Jahr.get()
    jahr2 = '20' + jahr2
    data = json.loads(zeile)
    timestamp = str(data['timestamp'])
    ctt_log_time = log_date(timestamp)
    tick_okay = False
    # print('log_time' + str(log_time))
    # print('ea_tick' + str(tick_time))
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
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    with open(journal_file, 'r', encoding='UTF8') as datei:
        line = 0
        for zeile in datei:
            line += 1
            search_string = "MultiSellExplorationData"
            if (zeile.find(search_string)) > -1:
                if check_tick_time(zeile, tick):
                    data_found = line
                    data = find_last_docked(journal_file, data_found)
                    if log_var > 1:
                        print(data)
                    faction = data[0]
                    system_name = data[1]
                    data = json.loads(zeile)
                    # print('Sell ExplorationData ' + faction + ' ' + str(data["TotalEarnings"]))
                    vouchers_db('ExplorationData', system_name, str(faction), int(data["TotalEarnings"]))


def market_sell(journal_file):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

    with open(journal_file, 'r', encoding='UTF8') as datei:
        line = 0
        for zeile in datei:
            line += 1
            search_string = "MarketSell"
            if (zeile.find(search_string)) > -1:
                if check_tick_time(zeile, tick):
                    data_found = line
                    data = find_last_docked(journal_file, data_found)
                    if log_var > 1:
                        print(data)
                    faction = data[0]
                    system_name = data[1]
                    data = json.loads(zeile)
                    vk = int(data['SellPrice'])
                    dek = int(data['AvgPricePaid'])
                    menge = int(data['Count'])
                    profit = (vk - dek) * menge
                    print('Profit  ' + str(profit))
                    try:
                        if data['BlackMarket']:
                            vouchers_db('BlackMarket', system_name, str(faction), int(data["TotalSale"]))
                        else:
                            print('MarketSell')
                            vouchers_db('MarketSell', system_name, str(faction), int(data["TotalSale"]))
                    except KeyError:
                        print('KeyError BlackMarket')
                        vouchers_db('MarketSell', system_name, str(faction), profit)


def find_last_docked(journal_file, data_found):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

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
                    print('Faction in Docked not found')
                star_system = (data['StarSystem'])
                if line < data_found:
                    star_systems.append(star_system)
                star_system = star_systems[-1]
    return faction, star_system


def redeem_voucher(journal_file):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

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
                    if log_var > 1:
                        print(data)
                    try:
                        if data['BrokerPercentage']:
                            print('Ignoring Interstellar Factor')
                    except KeyError:
                        try:
                            for p in data["Factions"]:
                                if not p['Faction'] == '':
                                    vouchers_db('Bounty ', system_name, faction, int(p['Amount']))
                                    if log_var > 1:
                                        print(data)
                        except KeyError:
                            try:
                                if data['Faction'] == 'PilotsFederation':
                                    print('InterstellarFactor')
                                elif not data['Faction'] == '':
                                    vouchers_db('CombatBonds', system_name, faction, int(data['Amount']))
                                    if log_var > 1:
                                        print(data)
                            except KeyError:
                                print('No Faction Event')


def vouchers_db(vouchers, systemname, faction, amount):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
        print(vouchers, systemname, faction, amount)

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
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

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
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    if eddc_modul != 4:
        while check_auto_refresh.get() != 0:
            print('while auto_refresh')
            if check_auto_refresh.get() != 0:
                print(check_auto_refresh.get())
                for i in range(0, 15):
                    time.sleep(1.0)
                    system.insert(INSERT, '.')
                if check_auto_refresh.get() != 0:
                    refreshing()


def refreshing():
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    print('while refreshing')
    system.delete(1.0, END)
    system.insert(INSERT, 'Auswertung läuft ')
    i = 0
    while i < 4:
        time.sleep(0.4)
        system.insert(INSERT, '.')
        i += 1
    if log_var > 1:
        print('Checkbox an oder aus ' + str(check_auto_refresh.get()))
    try:
        bgs.clear_rows()
    except AttributeError:
        print('NoData in bgs.row')
    try:
        voucher.clear_rows()
    except AttributeError:
        print('NoData in voucher.row')
    try:
        mats_table.clear_rows()
    except AttributeError:
        print('NoData in voucher.row')
    if eddc_modul != 4:
        auswertung(eddc_modul)


def threading_auto():
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    if eddc_modul == 4:
        print('AUTO CODEX = 1 ')
        tree.destroy()
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
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

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
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
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
                    print('failed')

    # ===========================  GUI erstellung  ==============================


def older_logs(ol_log_time, lauf):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
        print(ol_log_time, lauf)

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
        if log_var > 3:
            print(files)
        return files
    else:
        current_filenames = glob.glob(path + "\\Journal." + old_date + "*.log")
        filenames = glob.glob(path + "\\Journal." + new_date + "*.log")
        for i in filenames:
            files.append(i)
        for i in current_filenames:
            files.append(i)
        if log_var > 3:
            print(files)
        return files


def create_codex_entry():
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
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
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

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
        print(zeile)
        data = {''}
        return data


def read_codex_add_info(journal_file, rlc_log_time, type):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

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
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
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
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
        print('aktuelles  LOG' + str(journal_file))
    # bio_color = ['blank']
    # region_cmdr = ""
    with open(journal_file, 'r', encoding='UTF8') as datei:
        for i, zeile in enumerate(datei):
            search_string = '"ScanType":"Analyse"'
            if zeile.find(search_string) > -1:
                data = json.loads(zeile)
                # print(data)
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
                            if log_var > 5:
                                print(filename, region_cmdr , bio_cmdr)
                            if str(bio_cmdr) == str(region_cmdr):
                                bio_color = find_codex(filename, 99999, biodata)
                            if bio_color != '':
                                if log_var > 5:
                                    print('codex info in ' + str(filename) + ' gefunden; break')
                                break
                        if bio_color != '':
                            if log_var > 4:
                                print('codex info gefunden; break')
                            break
                        if not filenames:
                            bio_color = ''
                            if log_var > 4:
                                print('break not filenames' + str(lauf))
                            break
                        if lauf == 999:
                            bio_color = ''
                            if log_var > 4:
                                print('break lauf ' + str(lauf))
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
                                    print('if system != blank:')
                                    break
                        if rbd_system != 'blank':
                            print('if system != blank:')
                            break
                        if not filenames:
                            rbd_system = "no System found"
                            body = "no Body found"
                            print('if system != blank:')
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
                data = json.loads(zeile)
                temp.append(data[item])
        if temp:
            success = TRUE
            # print(success, temp, filename)
        else:
            success = FALSE
            # print(success, temp, filename)
        return temp


def codex_into_db(date_log, time_log, cid_cmdr, data, bio_color, systemname, body, region):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
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
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
        # print(bio_color)
    # print(date_log, time_log, cmdr)
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
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
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
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
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
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
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


def treeview_codex():
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    global filter_region, filter_cmdr, filter_bdata, combo_cmdr, combo_region, \
        combo_bio_data, b_data, regions, cmdr, tree, normal_view, death_frame, \
        death_date_combo, sell_combo, begin_time, end_time, sorting, refresher
    refresher = 0
    sorting = IntVar()
    normal_view = 0
    filter_region = ''
    filter_cmdr = ''
    filter_bdata = ''
    tree = Toplevel()
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
                    rowheight=25,
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
        if log_var > 2:
            print('function ' + inspect.stack()[0][3])
        normal_view = 3
        refresh_view()

    def player_death():
        global success, death_date_combo, sell_combo, normal_view
        normal_view = 2

        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        filter_cmdr = combo_cmdr.get()
        # print(filter_cmdr)
        select_sell = cursor.execute("""SELECT * FROM selling WHERE cmdr = ? GROUP BY date_log 
                                        ORDER BY date_log DESC""",
                                     (filter_cmdr,)).fetchall()
        global sell, sell_combo, death_frame, filter_sday, filter_dday, begin_time, end_time
        check_window = death_frame.winfo_exists()
        if check_window:
            death_frame.destroy()
        else:
            print('ERROR death_frame.destroy')
        death_frame = Frame(tree, background='black')
        death_frame.pack(side=LEFT, padx=25)

        label_tag = Label(death_frame, text="Last Sell:", bg='black', fg='white', font=("Helvetica", 11))
        label_tag.grid(column=0, row=1, padx=5)
        sell = ['']
        for i in select_sell:
            sell = sell + [i[0]]
        sell_combo = ttk.Combobox(death_frame)
        sell_combo['values'] = sell
        sell_combo.current(0)
        sell_combo.bind("<<ComboboxSelected>>", death_selected)
        label_tag = Label(death_frame, text="VON:", bg='black', fg='white', font=("Helvetica", 11))
        label_tag.grid(column=1, row=0, padx=5)
        sell_combo.grid(column=1, row=1, padx=5)
        cursor.execute("""CREATE table IF NOT EXISTS player_death (
                        date_log date,
                        time_log timestamp,
                        cmdr TEXT)
                        """)
        select_death = cursor.execute("""SELECT * FROM player_death WHERE cmdr = ? 
                                        GROUP BY date_log ORDER BY date_log DESC""",
                                      (filter_cmdr,)).fetchall()
        # print(select_death)
        label_tag = Label(death_frame, text="Last Death:", bg='black', fg='white', font=("Helvetica", 11))
        label_tag.grid(column=3, row=1, padx=5)

        death_date = ['']
        for i in select_death:
            death_date = death_date + [i[0]]
        death_date_combo = ttk.Combobox(death_frame)
        death_date_combo['values'] = death_date
        death_date_combo.current(0)
        death_date_combo.bind("<<ComboboxSelected>>", death_selected)
        label_tag = Label(death_frame, text="BIS:", bg='black', fg='white', font=("Helvetica", 11))
        label_tag.grid(column=4, row=0, padx=5)
        death_date_combo.grid(column=4, row=1, padx=5)
        # print(normal_view)
        refresh_button = Button(death_frame, text='Refresh', command=refresh_treeview)
        refresh_button.grid(column=5, row=1, padx=5)
        death_button = Button(death_frame, text='Mark for Death', command=set_to_death)
        death_button.grid(column=6, row=1, padx=5)

    def set_to_death():

        print(b_date, e_date)
        std_cmdr = combo_cmdr.get()
        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        # data = []
        if std_cmdr:
            data = cursor.execute("SELECT * FROM codex where cmdr = ? "
                                  "AND date_log BETWEEN ? AND ? "
                                  "ORDER by cmdr, region, data, date_log, time_log",
                                  (std_cmdr, b_date, e_date)).fetchall()
            if data:
                cursor.execute("UPDATE codex SET player_death = 1 where cmdr = ? "
                               "AND date_log BETWEEN ? AND ? ",
                               (std_cmdr, b_date, e_date)).fetchall()
                print('DEATH between ' + str(b_date) + ' and ' + str(e_date))
                connection.commit()

    menu_tree = Menu(tree)
    tree.config(menu=menu_tree)
    file_menu = Menu(menu_tree, tearoff=False)
    menu_tree.add_cascade(label="More", menu=file_menu)
    file_menu.add_command(label="Bio Codex Entry / Missing Bios", command=switch_view)
    # file_menu.add_command(label="Player Death", command=player_death)
    file_menu.add_command(label="Codex Stars", command=codex_stars)

    def create_frame():
        global death_frame
        death_frame = Frame(tree, background='black')
        if log_var > 2:
            print('function ' + inspect.stack()[0][3])
        global tree_frame, tree_scroll, codex_tree
        tree_frame = Frame(tree, bg='black')
        tree_frame.pack(pady=10)
        tree_scroll = Scrollbar(tree_frame)
        tree_scroll.pack(side=RIGHT, fill=Y)
        codex_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, selectmode="extended")
        tree_scroll.config(command=codex_tree.yview)

    def selected(event):
        if log_var > 2:
            print('function ' + inspect.stack()[0][3])
        global filter_region, filter_cmdr, filter_bdata, filter_sday, filter_dday, \
            begin_time, end_time, sell_combo, death_date_combo
        filter_region = combo_regions.get()
        filter_cmdr = combo_cmdr.get()
        filter_bdata = combo_bio_data.get()
        refresh_combo()
        refresh_view()
        # print(filter_cmdr + " " + filter_region + " " + filter_bdata)

    # def death_selected(event):
    #     global begin_time, end_time
    #
    #     filter_sday = sell_combo.get()
    #     if filter_sday != '':
    #         b_date = filter_sday
    #         begin_time.delete(0, END)
    #         begin_time.insert(0, b_date)
    #
    #     filter_dday = death_date_combo.get()
    #     if filter_dday != '':
    #         e_date = filter_dday
    #         end_time.delete(0, END)
    #         end_time.insert(0, e_date)
    #     refresh_combo()

    def worth_it(search_data):
        if log_var > 5:
            print('function ' + inspect.stack()[0][3])
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

    def read_codex_data(rcd_cmdr, rcd_region):
        if log_var > 2:
            print('function ' + inspect.stack()[0][3])
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            if log_var > 2:
                print(rcd_cmdr, rcd_region)
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

    def codex_treeview():
        if log_var > 2:
            print('function ' + inspect.stack()[0][3])
        summe = 0
        data = ['']
        update = 0
        if normal_view == 0:
            if sorting.get() != 0:
                update = 3
            else:
                update = 0
            data = select_filter(filter_cmdr, filter_region, filter_bdata, update)

        # Missing BIO Codex Entrys
        elif normal_view == 1:
            data = missing_codex(filter_cmdr, filter_region)
            update = 0

        # Player Death
        elif normal_view == 2:
            update = 2
            data = select_filter(filter_cmdr, filter_region, filter_bdata, update)

        # All Codex Data except BIO
        elif normal_view == 3:
            data = read_codex_data(filter_cmdr, filter_region)
            update = 0


        if not data:
            data = [('DATE', 'TIME', 'COMMANDER', 'SPECIES',
                     'VARIANT', 'SYSTEM', 'BODY', "REGION", 1, 1)]
            summe = 0
        elif normal_view == 2 or normal_view == 0:
            summe = 0
            for i in data:
                summe += worth_it(i)

        # creating treeview
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
        codex_tree.tag_configure('subrow', background="yellow")

        # print(data)
        # insert Data in treeview
        count = 0
        counter = 'a'
        worth = ''
        for record in data:
            if normal_view == 2 or normal_view == 0:
                worth = worth_it(record)
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

                # print(record)
                record = (record[0], record[1], record[2], record[3], record[4], record[6], '',
                          record[7], 1, 1)

            if count % 2 == 0:
                # Alle geraden Zeilen werden hellblau eingefärbt
                if record[8] != 0:
                    codex_tree.insert(parent='', index='end', iid=str(count), text="",
                                      values=(count, record[0], record[1], record[2], record[3], record[4], worth,
                                              record[5], record[6], record[7]), tags=('evenrow',))
                else:
                    count -= 1
                    codex_tree.insert(parent=str(count), index='end', iid=str(str(count) + counter), text="",
                                      values=(count, record[0], record[1], record[2], record[3], record[4], worth,
                                              record[5], record[6], record[7]), tags=('subrow',))
                    counter = chr(ord(counter) + 1)

            else:
                # Alle ungeraden Zeilen werden weiß eingefärbt.
                if record[8] != 0:
                    codex_tree.insert(parent='', index='end', iid=str(count), text="",
                                      values=(count, record[0], record[1], record[2], record[3], record[4], worth,
                                              record[5], record[6], record[7]), tags=('oddrow',))
                else:
                    if count > 1:
                        count -= 1
                        codex_tree.insert(parent=str(count), index='end', iid=str(str(count) + counter), text="",
                                          values=(count, record[0], record[1], record[2], record[3], record[4], worth,
                                                  record[5], record[6], record[7]), tags=('subrow',))
                        counter = chr(ord(counter) + 1)
                    elif count == 1:
                        codex_tree.insert(parent='', index='end', iid=str(str(count) + counter), text="",
                                          values=(count, record[0], record[1], record[2], record[3], record[4], worth,
                                                  record[5], record[6], record[7]), tags=('subrow',))
                        counter = chr(ord(counter) + 1)
            count += 1
        codex_tree.pack()
        if summe > 0 and (normal_view == 2 or normal_view == 0):
            summen_text = ('Summe  - Anzahl Einträge : ' + str(count) + '     Wertigkeit :  ' + str(f"{summe:,}"))
            summe = Label(tree_frame, text=summen_text, bg='black', fg='white')
            summe.pack(fill=X, side=RIGHT)

    def read_files():
        if log_var > 2:
            print('function ' + inspect.stack()[0][3])
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
        if log_var > 2:
            print('function ' + inspect.stack()[0][3])

        threading.Thread(target=treeview_loop).start()

    def treeview_loop():
        if log_var > 2:
            print('function ' + inspect.stack()[0][3])
        switch = 0

        while tree is not None and tree.winfo_exists():
            switch = read_files()
            # print(switch)
            if switch == 1:
                print('log have changed')
                refresh_view()
                refresh_combo()
                time.sleep(5.0)
            else:
                # print('nothing new')
                time.sleep(5.0)

    def refresh_view():
        if log_var > 2:
            print('function ' + inspect.stack()[0][3])

        global b_date, e_date, death_frame
        for i in codex_tree.get_children():
            codex_tree.delete(i)
        check_window = death_frame.winfo_exists()
        if check_window:
            death_frame.destroy()
        else:
            print('ERROR death_frame.destroy')
        tree_frame.destroy()
        b_date = begin_time.get()
        e_date = end_time.get()
        create_frame()
        codex_treeview()
        codex_tree.bind("<ButtonRelease-1>", selected_record)

    global buttons_frame
    buttons_frame = Frame(tree, background='black')
    buttons_frame.pack(fill=X, pady=15)

    create_frame()
    codex_treeview()

    def refresh_combo():
        if log_var > 2:
            print('function ' + inspect.stack()[0][3])
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

        # print(abbruch)

        # 1 FILTER CMDR
        b_data = [(''), ('Aleoida'), ('Bacterium'), ('Bark Mounds'), ('Brain'),
                  ('Cactoida'), ('Clypeus'), ('Concha'), ('Crystalline Shards'),
                  ('Electricae'), ('Fonticulua'), ('Frutexa'),  ('Fumerola'), ('Osseus'),
                  ('Recepta'), ('Stratum'), ('Tubus'), ('Tussock'), ('---------'),
                  ('Amphora Plant'), ('Anemone'), ('Crystalline Shards'), ('Fumerola'), ('Tubers')]
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
            print(selection_region)
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
        b_data = [(''), ('Aleoida'), ('Bacterium'), ('Bark Mounds'), ('Brain'),
                  ('Cactoida'), ('Clypeus'), ('Concha'), ('Crystalline Shards'),
                  ('Electricae'), ('Fonticulua'), ('Frutexa'),  ('Fumerola'), ('Osseus'),
                  ('Recepta'), ('Stratum'), ('Tubus'), ('Tussock'), ('---------'),
                  ('Amphora Plant'), ('Anemone'), ('Crystalline Shards'), ('Fumerola'), ('Tubers')]
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
        # e_date = end_time.get()
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

    create_button()

    def selected_record(e):
        global my_img, my_label
        if log_var > 2:
            print('function ' + inspect.stack()[0][3])
        selected_tree = codex_tree.focus()
        values = codex_tree.item(selected_tree, 'values')
        my_img = ''
        if values:
            if log_var > 2:
                print(values)
            if normal_view == 3:
                var = str(values[5]).split()
                if 'D' in var[0]:
                    var = ['D', 'Type', 'Star']
            else:
                var = str(values[4]).split()
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
                print("File not found")
                print(png)
                file = resource_path("images/Kein_Bild.png")
                image = Image.open(file)
                image = image.resize((320, 145))
                my_img = ImageTk.PhotoImage(image)
        else:
            print("Es wurde nichts selektiert")
        my_label = Label(tree, image=my_img)
        my_label.place(x=837, y=385)

    codex_tree.bind("<ButtonRelease-1>", selected_record)

    # connection.close()

    def missing_codex(filter_cmdr, filter_region):
        if log_var > 2:
            print('function ' + inspect.stack()[0][3])
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
            data.append((' ', ' ', i[0], i[1], ' ', ' ', ' ', i[2], 1))
            lauf += 1
        return data

    refresh_view()
    refresh_treeview()
    tree.mainloop()


def select_filter(sf_cmdr, region, bio_data, update):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

    create_tables()
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    data = []

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
    return data


def check_system(journal_file, zeilenr):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
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
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

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
    if log_var > 2:
        print('function ' + inspect.stack()[0][3] + " " + journal_file)
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


def system_scan(journal_file):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
        print('Start System Scan')
    search_string = 'FSSDiscoveryScan'
    with open(journal_file, 'r', encoding='UTF8') as datei:
        for zeile in datei.readlines()[::-1]:  # Read File line by line reversed!
            if zeile.find(search_string) > -1:
                data = json.loads(zeile)
                body_count = data['BodyCount']
                system_name = data['SystemName']
                system_address = data['SystemAddress']
                systems = (system_name, system_address, body_count)
                return systems


def scan_planets(journal_file, current_system):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
        print('Start Planetary Scan')
    search_string = '"event":"FSSBodySignals"'
    with open(journal_file, 'r', encoding='UTF8') as datei:
        for zeile in datei:
            if zeile.find(search_string) > -1:
                data = json.loads(zeile)
                # print(data)
                body_name = data['BodyName']
                system_address = data['SystemAddress']
                # print(system_address, current_system)
                if system_address == current_system[1]:
                    for signals in data['Signals']:
                        count = signals['Count']
                        signal_type = signals['Type_Localised']
                        print(body_name, signal_type, count)


def extract_engi_stuff(data, state):
    try:
        engi_stuff_ody_db(str(data['Name_Localised']), int(data['Count']), state)
    except KeyError:
        engi_stuff_ody_db(str(data['Name']), int(data['Count']), state)


def engi_stuff_ody_db(name, count, state):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

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
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

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
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

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
    menu_var = [0, 'BGS', 'ody_mats', 'MATS', 'CODEX', 'combat', 'SystemScan']
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
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
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

    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
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
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    # print('filename', filenames_codex)
    last_log_file = select_last_log_file()[0]
    if log_var > 2:
        print(last_log_file)
    # print('the log-file before the last from DB ', last_log_file)
    if last_log_file != '0':
        lauf = 0
        for i in filenames_codex:
            if i != last_log_file:
                lauf += 1
            else:
                # print(i, last_log_file)
                break
        i = -1
        # Alle Logfiles vor dem last_log_file werden aus der Liste entfernt
        while i < lauf:
            filenames_codex.pop(0)
            i += 1
    # nur die neuesten Logfiles und die letzen zwei schon eingelesenen werden übergeben.
    # print(filenames_codex)
    return filenames_codex


def read_codex_entrys():
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
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
    # if count+1 == len(filenames) and len(filenames) > 1:
    #     vat = 0


def run_once_rce(filenames):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

    if len(filenames) > 5:
        print('start run_once')
        thread_rce = threading.Thread(target=read_codex_entrys, args=())
        thread_rce.start()
        print('stop run_once')
    else:
        read_codex_entrys()


def wait_to_finish():
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
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
        print(count_files, item[0][0])
        success = 1
    return success


def combat_rank():
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
                    data = json.loads(zeile)
                    if data['TargetLocked']:
                        if data['ScanStage'] == 3 and data['LegalStatus'] == 'Wanted':
                            try:
                                sh_target = data['Ship_Localised']
                            except KeyError:
                                sh_target = data['Ship']
                            sh_total_reward = data['Bounty']
                            pilot_rank = data['PilotRank']
                        elif data['ScanStage'] > 0:
                            if data['ScanStage'] != 3:
                                try:
                                    sh_target = data['Ship_Localised']
                                except KeyError:
                                    sh_target = data['Ship']
                                sh_total_reward = 0
                                pilot_rank = data['PilotRank']

                search_string = '"event":"Bounty"'
                if (zeile.find(search_string)) > -1:
                    data = json.loads(zeile)
                    try:
                        b_target = data['Target_Localised']
                    except KeyError:
                        b_target = data['Target']
                    b_total_reward = data['TotalReward']
                    if log_var > 2:
                        print(b_target, b_total_reward, sh_target, sh_total_reward, pilot_rank)
                    tmp = int(sh_total_reward)
                    tmp += 300
                    if b_total_reward == tmp:
                        sh_total_reward = tmp
                    if b_target == sh_target and b_total_reward == sh_total_reward:
                        print('')
                        print(b_target, b_total_reward)
                        print(sh_target, sh_total_reward, pilot_rank)
                        print('')
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
    select = set_language_db('leer')
    searcher = 1
    for a in ranking:
        if not select or select[0][0] == 'german' or select == 'leer':
            if b_filter == a[1]:
                searcher = a[3]
        else:
            if b_filter == a[0]:
                searcher = a[3]

    for i in ranking:
        if i[2] > 0 and i[3] > (searcher - 1):
            if not select or select[0][0] == 'german' or select == 'leer':
                system.insert(END, ((str(i[1])) + '\t \t \t \t' + (str(i[2])) + '\n'))
            else:
                system.insert(END, ((str(i[0])) + '\t \t \t \t' + (str(i[2])) + '\n'))


def auswertung(eddc_modul):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    if log_var > 2:
        print("lösche tabellen")

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
    if log_var == 3:
        print(filenames)
    auto_refresh = False
    lauf_r = 0
    if auto_refresh is True:
        auto = len(filenames) - 1
        while lauf_r < auto:
            del filenames[lauf_r]
            lauf_r += 1
    # print(filenames)
    if not filenames:
        # Wenn es keine logfiles an diesem Tag gibt, dann
        if eddc_modul == 4:
            print('Test')
            xx = select_last_log_file()[0]
            # print(xx)
            if xx == '0':
                filenames = file_names(1)
            # system.insert(END, 'Codex Daten werden gelesen')
            print('Keine Log-Files für Heute vorhanden')
            read_codex_entrys()
            treeview_codex()
        else:
            system.insert(END, 'Keine Log-Files für den Tag vorhanden')
    else:
        if eddc_modul == 1:
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
                print('NO VOUCHER DATA')
            data = print_influence_db(b_filter)
            if data:
                for i in data:
                    system.insert(END, ((str(i[0])[0:15]) + '\t\t' + (str(i[1])[0:25]) + '\t\t\t\t' + str(i[2]) + '\n'))
                    bgs.add_row((i[0], i[1], i[2]))
            else:
                print('NO INFLUENCE DATA')
                if nodata == 1:
                    system.insert(END, '\n\tKeine Daten vorhanden')

        elif eddc_modul == 3:
            star_systems_db(filenames)
            for filename in filenames:
                mats_auslesen(filename)
            b_filter = Filter.get()
            data = print_engi_stuff_db(b_filter)
            for i in data:
                system.insert(END, ((str(i[0])) + '\t \t \t \t' + (str(i[1])) + '\n'))
                mats_table.add_row((i[0], i[1]))

        elif eddc_modul == 2:
            star_systems_db(filenames)
            print('ody_mats == 1')
            for filename in filenames:
                ody_mats_auslesen(filename)
            b_filter = Filter.get()
            data = print_engi_stuff_db(b_filter)
            for i in data:
                system.insert(END, ((str(i[0])) + '\t \t \t \t' + (str(i[1])) + '\n'))
                mats_table.add_row((i[0], i[1]))

        elif eddc_modul == 4:
            # system.insert(END, 'Codex Daten werden gelesen')
            run_once_rce(filenames)
            last_log_file = select_last_log_file()[0]
            if last_log_file != '0':
                treeview_codex()

        elif eddc_modul == 5:
            combat_rank()

        elif eddc_modul == 6:
            star_systems_db(filenames)
            for filename in filenames:
                current_system = system_scan(filename)
                scan_planets(filename, current_system)


def set_language_db(var):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
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


def db_version():
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("""CREATE table IF NOT EXISTS db_version (version INTEGER)""")
    item = cursor.execute("SELECT version FROM db_version").fetchall()
    # print(item[0][0], version_number)
    if not item:
        cursor.execute("INSERT INTO db_version VALUES (?)", (version_number,))
        connection.commit()
    elif item[0][0] != version_number:
        cursor.execute("UPDATE db_version set version = ?", (version_number,))
        print('Update Version')
        connection.commit()
    elif item[0][0] == version_number:
        print('Same Version')


def delete_all_tables():
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

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
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
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


# noinspection PyGlobalUndefined
def main():
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
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
    file_menu.add_command(label="SystemScan", command=lambda: menu('SystemScan'))
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
        if log_var > 2:
            print('function ' + inspect.stack()[0][3])

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
        if log_var > 2:
            print('function ' + inspect.stack()[0][3])
            print(event)
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
