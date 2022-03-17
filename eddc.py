# Created by MajorK https://github.com/SNP-MajorK/ED-DataCollector

import glob
import threading
import time
import sqlite3
import inspect, os
from builtins import print
from tkinter import *
from tkinter import ttk
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
BGS = 1
MATS = 0
ODYS = 0
CODEX = 0
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

# Set Program Path Data to random used Windows temp folder.
with OpenKey(HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders") as key:
    value = QueryValueEx(key, '{4C5C32FF-BB9D-43B0-B5B4-2D72E54EAAA4}')
path = value[0] + '\\Frontier Developments\\Elite Dangerous\\'
# path = value[0] + '\\Frontier Developments\\'

bgs = PrettyTable(['System', 'Faction', 'Influence'])
voucher = PrettyTable(['Voucher', 'System', 'Faction', 'Credits'])
mats_table = PrettyTable(['Materials', 'Count'])


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

database = resource_path("eddc.db")


def last_tick():
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    response = requests.get("https://elitebgs.app/api/ebgs/v5/ticks")
    todos = json.loads(response.text)

    global tick_time
    global t_hour
    global t_minute
    for d in todos:
        date = d['time']
        t_year = (date[:4])
        t_month = (date[5:7])
        t_day = (date[8:10])
        t_hour = str(date[11:13])
        t_minute = str(date[14:16])
        tick_time = [t_year, t_month, t_day, t_hour, t_minute]

def file_names(var):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    update_eleven = datetime(2022,3,14)
    if var == 0:
        Tag2 = Tag.get()
        Tag2 = str(int(Tag2) - var).zfill(2)
        Monat2 = Monat.get()
        Jahr2 = Jahr.get()
        search_date = datetime(int("20" + Jahr2), int(Monat2), int(Tag2))
        if search_date > update_eleven:
            Date = ("20" + str(Jahr2) + "-" + str(Monat2) + "-" + str(Tag2) + "T")
            print(Date)
            filenames = glob.glob(path + "\\Journal." + Date + "*.log")
            return filenames
        else:
            Date = str(Jahr2 + Monat2 + Tag2)
            filenames = glob.glob(path + "\\Journal." + Date + "*.log")
            print(filenames)
            return filenames
    else:
        print('TEst')
        search_date = datetime(int(Year), int(Month), int(Day))
        print(search_date)
        # update_eleven = update_eleven.strftime('%Y-%m-%d')
        if search_date > update_eleven:
            print("search_date")
            filenames = glob.glob(path + "\\Journal.202*.log")
            return (filenames)
        else:
            filenames = glob.glob(path + "\\Journal.*.log")
            return (filenames)

# def file_names_old(var):
#     if log_var > 2:
#         print('function ' + inspect.stack()[0][3])
#     Tag2 = Tag.get()
#     Tag2 = str(int(Tag2) - var).zfill(2)
#     Monat2 = Monat.get()
#     Jahr2 = Jahr.get()
#     Date = str(Jahr2 + Monat2 + Tag2)
#     Date = str(Jahr2 + Monat2 + Tag2)
#     filenames = glob.glob(path + "\\Journal." + Date + "*.log")
#     print(filenames)
#     return filenames


# def file_names_new(var):
 #     if log_var > 2:
#         print('function ' + inspect.stack()[0][3])
#     Tag2 = Tag.get()
#     Tag2 = str(int(Tag2) - var).zfill(2)
#     Monat2 = Monat.get()
#     Jahr2 = Jahr.get()
#     Date = str(Jahr2 + Monat2 + Tag2)
#     Date = ("20" + str(Jahr2) + "-" + str(Monat2)  + "-" + str(Tag2) +"T")
#     print(Date)
#     filenames = glob.glob(path + "\\Journal." + Date + "*.log")
#     return filenames




def date_for_ma(missionid, gmd_faction, x):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    mission_found = False
    while x < 7:
        Tag2 = str(int(Tag.get()) - x)
        Monat2 = Monat.get()
        Jahr2 = Jahr.get()
        Date = str(Jahr2 + Monat2 + str(Tag2).zfill(2))
        filenames = file_names(0)
        # filenames = glob.glob(path + "\\Journal." + Date + "*.log")
        for filename in filenames:
            # print(filename)
            if get_mission_data(missionid, filename, gmd_faction):
                mission_found = True
                return mission_found
        x += 1


def get_mission_data(missionid, journal_file, gmd_faction):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    global inf_data, docked
    docked = ''
    inf_data = ''
    MA_ZEILE = 0
    D_ZEILE = 0
    D_system = []
    # print(journal_file)
    datei = open(journal_file, 'r', encoding='UTF8')
    D_datei = open(journal_file, 'r', encoding='UTF8')
    for MA_zeile in datei:
        MA_ZEILE += 1
        gmd_mission_id = str(missionid)
        gmd_search_string = 'MissionAccepted'
        if (MA_zeile.find(gmd_search_string)) > -1:
            # print('suche nach Mission ID ' + gmd_mission_id)
            if (MA_zeile.find(gmd_mission_id)) > -1:
                mission_found = True
                # print('gefunden ' + gmd_mission_id)
                data = json.loads(MA_zeile)
                # print(data)
                if str(data['Faction']) == str(gmd_faction):
                    inf_data = (data['Influence'])
                    if log_var > 2:
                        print(inf_data)
                        print(missionid + mission_found)
                    if mission_found:
                        for D_zeile in D_datei:
                            D_ZEILE += 1
                            gmd_search_docked = 'Docked'
                            if (D_zeile.find(gmd_search_docked)) > -1:
                                D_data = json.loads(D_zeile)
                                docked_data = (D_data['SystemAddress'])
                                if D_ZEILE < MA_ZEILE:
                                    D_system.append(docked_data)
                        docked = D_system[-1]
                        datei.close()
                        return docked
                else:
                    # print(data)
                    if log_var > 1:
                        print('gmd - else : ' + str(data['Faction']) + ' ' + str(gmd_faction))
                    docked = ''
                    datei.close()
                    return docked
            else:
                mission_found = False
    datei.close()


def get_faction_for(system_address):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    filenames = file_names(0)
    for filename in filenames:
        datei = open(filename, 'r', encoding='UTF8')
        line = 0
        for zeile in datei:
            line += 1
            search_string = "FSDJump"
            if (zeile.find(search_string)) > -1:
                data = json.loads(zeile)
                faction = (data['SystemFaction']['Name'])
                datei.close()
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
                missionid = data['MissionID']
                if not p['Influence']:
                    print("extract_data no Data in p['Influence']")
                    # print(p)
                    if log_var > 3:
                        print(p['Influence'])
                    mission_found = False
                    date_for_ma(missionid, ed_faction, 0)
                    if docked:
                        p['Influence'] = [{'SystemAddress': docked, 'Trend': 'UpGood', 'Influence': inf_data}]
                    else:
                        p['Influence'] = [{'SystemAddress': docked, 'Trend': 'UpGood', 'Influence': ''}]
                extract_influence(p)
            else:
                print('else')
                print(p['Influence'])
                # for xx in p['Influence']:
                #     print(xx['SystemAddress'])
                #     # get_faction_for(xx['SystemAddress'])
                #     p['Faction'] = get_faction_for(xx['SystemAddress'])
                #     extract_influence(p)

    except KeyError:
        print('extract_data  - exception')
        ed_faction = (data['Faction'])
        missionid = data['MissionID']
        date_for_ma(missionid, ed_faction, 0)
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
                update_influence_db(xx['SystemAddress'], data['Faction'], len(xx['Influence']))
        if xx['Trend'] == 'DownBad':
            if not read_influence_db(xx['SystemAddress'], data['Faction']):
                influence_db(xx['SystemAddress'], data['Faction'], (len(xx['Influence']) * (-1)))
            else:
                update_influence_db(xx['SystemAddress'], data['Faction'], (len(xx['Influence']) * (-1)))


def starsystem(time):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    global starsytems_data, SystemAddress_list
    files = glob.glob(path + "\\Journal.*.log")
    filenames = []
    if (len(files)) < time:
        start = 0
    else:
        start = ((len(files)) - int(time))
    while start < (len(files)):
        filenames.append(files[start])
        start += 1
    star_systems_db(filenames)


def star_systems_db(filenames):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    for filename in filenames:
        datei = open(filename, 'r', encoding='UTF8')
        for zeile2 in datei:
            search_string2 = "FSDJump"
            if (zeile2.find(search_string2)) > -1:
                star_systems_data = json.loads(zeile2)
                starchart_db(star_systems_data['SystemAddress'], star_systems_data['StarSystem'])
        datei.close()


def influence_db(ID, Faction, Influence):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    if ID == '':
        # print('NULL')
        ID = 'NONE'
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("CREATE table IF NOT EXISTS influence (SystemName TEXT, Faction TEXT, Influence INTEGER)")
    SystemName = cursor.execute("SELECT SystemName FROM starchart WHERE SystemID= ?", (ID,)).fetchall()
    if not ID == 'NONE':
        SystemName = SystemName[0][0]
        cursor.execute("SELECT SystemName, Faction, Influence FROM influence WHERE SystemName= ? and Faction = ?",
                       (SystemName, Faction,))
        result = cursor.fetchall()
        if not result:
            if log_var > 2:
                print('DB Else')
            cursor.execute("INSERT INTO influence VALUES (?, ?, ?)", (SystemName, Faction, Influence))
            connection.commit()
    connection.close()


def update_influence_db(ID, Faction, Influence):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    if ID == '':
        # print('NULL')
        ID = 'NONE'
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("CREATE table IF NOT EXISTS influence (SystemName TEXT, Faction TEXT, Influence INTEGER)")
    SystemName = cursor.execute("SELECT SystemName FROM starchart WHERE SystemID= ?", (ID,)).fetchall()
    if not ID == 'NONE':
        SystemName = SystemName[0][0]
        cursor.execute("SELECT Influence FROM influence WHERE SystemName= ? and Faction = ?", (SystemName, Faction,))
        result = cursor.fetchall()
        new_influence = (int(result[0][0])) + int(Influence)
        cursor.execute("UPDATE influence SET Influence = ? WHERE  SystemName= ? and Faction = ?",
                       (new_influence, SystemName, Faction))
        connection.commit()

    connection.close()


def read_influence_db(ID, faction):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    if isinstance(ID, int):
        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        cursor.execute("CREATE table IF NOT EXISTS influence (SystemName TEXT, Faction TEXT, Influence INTEGER)")
        SystemName = cursor.execute("SELECT SystemName FROM starchart WHERE SystemID= ?", (ID,)).fetchall()
        # print(SystemName)
        try:
            SystemName = SystemName[0][0]
        except IndexError:
            filenames = file_names(0)
            star_systems_db(filenames)
            SystemName = cursor.execute("SELECT SystemName FROM starchart WHERE SystemID= ?", (ID,)).fetchall()
            SystemName = SystemName[0][0]
        result = cursor.execute("SELECT Faction FROM influence WHERE SystemName = ? and Faction = ?",
                                (SystemName, faction)).fetchall()
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
    DATA = cursor.execute("SELECT * FROM influence WHERE SystemName LIKE ? OR Faction LIKE ? GROUP BY 1, 2, 3",
                          (filter_b, filter_b)).fetchall()
    connection.close()
    return DATA


def starchart_db(ID, SystemName):
    # if log_var > 2:
    #     print('function ' + inspect.stack()[0][3])
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("CREATE table IF NOT EXISTS starchart (SystemID INTEGER, SystemName TEXT)")
    cursor.execute("SELECT SystemID FROM starchart WHERE SystemID= ?", (ID,))
    result = cursor.fetchall()
    if not result:
        if log_var > 2:
            print('DB Else')
        cursor.execute("INSERT INTO starchart VALUES (?, ?)", (ID, SystemName,))
        connection.commit()
    connection.close()


def read_starchart_table(ID):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    if isinstance(ID, int):
        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        cursor.execute("CREATE table IF NOT EXISTS starchart (SystemID INTEGER, SystemName TEXT)")
        SystemName = cursor.execute("SELECT SystemName FROM starchart WHERE SystemID = ?", (ID,)).fetchall()
        try:
            connection.close()
            return SystemName[0][0]
        except IndexError:
            print('SystemAdresss =  ' + str(ID))
            connection.close()


def einfluss_auslesen(journal_file):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    tick_hour = hour.get()
    tick_minute = minute.get()
    tick_time[3] = tick_hour[0:2]
    tick_time[4] = tick_minute[0:2]
    if log_var == 5:
        print(tick_time)
    # print(journal_file)
    datei = open(journal_file, 'r', encoding='UTF8')
    for zeile in datei:
        search_string = "MissionCompleted"
        if (zeile.find(search_string)) > -1:
            data = json.loads(zeile)
            if log_var > 1:
                print(data)
            if check_tick_time(zeile, tick):
                # print(data)
                extract_data(data)

    datei.close()
    # Starchart aktualisieren!
    starsystem(3)
    # =========================================== End of dateien_einlesen()


def check_tick_time(zeile, ea_tick):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

    data = json.loads(zeile)
    timestamp = str(data['timestamp'])
    log_time = log_date(timestamp)
    tick_okay = False
    # print(ea_tick)
    if ea_tick is True:
        if str(tick_time[3]) < str(log_time[3]):
            tick_okay = True
        if (str(tick_time[3]) == str(log_time[3])) and (str(tick_time[4]) < str(log_time[4])):
            tick_okay = True
    else:
        if str(tick_time[3]) > str(log_time[3]):
            tick_okay = True
        if (str(tick_time[3]) == str(log_time[3])) and (str(tick_time[4]) > str(log_time[4])):
            tick_okay = True
    return tick_okay


def multi_sell_exploration_data(journal_file):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

    datei = open(journal_file, 'r', encoding='UTF8')
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
    datei.close()


def is_json_key_present(json, key):
    try:
        buf = json[key]
    except KeyError:
        return False

    return True


def market_sell(journal_file):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

    datei = open(journal_file, 'r', encoding='UTF8')
    line = 0
    for zeile in datei:
        line += 1
        search_string = "MarketSell"
        if (zeile.find(search_string)) > -1:
            if check_tick_time(zeile, tick):
                # print(zeile)
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
                    # if is_json_key_present(data, 'Blackmarket'):
                    if data['BlackMarket']:
                        vouchers_db('BlackMarket', system_name, str(faction), int(data["TotalSale"]))
                    else:
                        print('MarketSell')
                        vouchers_db('MarketSell', system_name, str(faction), int(data["TotalSale"]))
                except KeyError:
                    print('KeyError BlackMarket')
                    vouchers_db('MarketSell', system_name, str(faction), profit)
    datei.close()


def find_last_docked(journal_file, data_found):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

    datei = open(journal_file, 'r', encoding='UTF8')
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
    datei.close()
    return faction, star_system


def redeem_voucher(journal_file):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

    datei = open(journal_file, 'r', encoding='UTF8')
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
    Item = cursor.execute("SELECT Amount FROM vouchers WHERE SystemName = ? and Faction = ? and Vouchers = ?",
                          (systemname, faction, vouchers)).fetchall()
    if not Item:
        cursor.execute("INSERT INTO vouchers VALUES (?, ?, ?, ?)", (vouchers, systemname, faction, amount))
        connection.commit()
    else:
        Item = cursor.execute("SELECT Amount FROM vouchers WHERE SystemName = ? and Faction = ? and Vouchers = ?",
                              (systemname, faction, vouchers)).fetchone()
        # print(Item[0])
        amount += int(Item[0])
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
    DATA = cursor.execute("""SELECT * FROM vouchers 
                                WHERE SystemName = ? 
                                OR Faction LIKE ? 
                                OR Vouchers LIKE ? GROUP BY 1, 2, 3""",
                          (filter_b, filter_b, filter_b)).fetchall()
    connection.close()
    return DATA


def ticktrue():
    global tick
    tick = True


def tickfalse():
    global tick
    tick = False


starsystem(20)


# threading.Thread(target=(starsystem(10))).start()


def autorefresh():
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    if CODEX != 1:

        while check_auto_refresh.get() != 0:
            print('while autorefresh')
            if check_auto_refresh.get() != 0:
                print(check_auto_refresh.get())
                time.sleep(10.0)
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
    if CODEX != 1:
        auswertung()


def threading_auto():
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    if CODEX == 1:
        print('AUTO CODEX = 1 ')
        tree.destroy()
        auswertung()
    elif check_auto_refresh.get() != 0:
        threading.Thread(target=autorefresh).start()
    else:
        threading.Thread(target=refreshing).start()


def logging():
    global log_var
    log_var += 1
    print(log_var)


def mats_auslesen(journal_file):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

    mats_table.clear_rows()
    datei = open(journal_file, 'r', encoding='UTF8')
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
    datei = open(journal_file, 'r', encoding='UTF8')
    for zeile in datei:
        search_string = 'BackpackChange'
        if (zeile.find(search_string)) > -1:
            data = json.loads(zeile)
            # print(data)
            try:
                for xx in data['Added']:
                    print(xx)
                    state = 1
                    extract_engi_stuff(xx, state)
            except KeyError:
                state = (-1)
                for xx in data['Removed']:
                    extract_engi_stuff(xx, state)
                print('failed')

    # ===========================  GUI erstellung  ==============================


def older_logs(log_time, lauf):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    datum = date(year=int(log_time[0]), month=int(log_time[1]), day=int(log_time[2]))
    update_eleven = datetime(2022, 3, 14)
    new_date = str(datum - timedelta(days=lauf))
    print(new_date)
    ol_year = str(new_date[2:4])
    ol_month = str(new_date[5:7])
    ol_day = str(new_date[8:10])
    new_date = str(new_date[2:4] + new_date[5:7] + new_date[8:10])
    print(ol_year, ol_month, ol_day)
    search_date = datetime(int("20" + ol_year), int(ol_month), int(ol_day))
    if search_date > update_eleven:
        Date = ("20" + str(Jahr2) + "-" + str(Monat2) + "-" + str(Tag2) + "T")
        print(Date)
        filenames = glob.glob(path + "\\Journal." + Date + "*.log")
        return filenames
    else:
        filenames = glob.glob(path + "\\Journal." + new_date + "*.log")
        print(filenames)
        return filenames

    return filenames


def create_codex_entry():
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

        regions = RegionMapData.regions

        select = cursor.execute("SELECT * from codex_entry").fetchall()
        # print(select)
        if not select:
            lauf = 0
            for a in regions:
                if a != None:
                    for i in bio_worth:
                        cursor.execute("INSERT INTO codex_entry VALUES (?, ?, ?, ?)", (i[0], i[1], 0, a))
            connection.commit()
create_codex_entry()

def insert_codex_db(logtime, codex_name, cmdr, codex_entry, category, region, system):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

    log_time = (log_date(logtime))
    date_log = (log_time[0] + "-" + log_time[1] + "-" + log_time[2])
    time_log = (log_time[3] + ":" + log_time[4] + ":" + log_time[5])

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
                                """, (date_log, time_log, cmdr, codex_name, region)).fetchall()
        if not select:
            cursor.execute("INSERT INTO codex_data VALUES (?,?,?,?,?,?,?,?)",
                           (date_log, time_log, cmdr, codex_name, codex_entry, category, system, region))


def read_log_codex(journal_file):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

    cmdr = check_cmdr(journal_file)

    with open(journal_file, 'r', encoding='UTF8') as datei:
        for zeile in datei:
            search_string = '"event":"CodexEntry"'
            if zeile.find(search_string) > -1:
                data = json.loads(zeile)
                logtime = data['timestamp']
                codex_name = (data['Name'])
                codex_entry  = (data['Name_Localised'])
                category = data['Category_Localised']
                region = data['Region_Localised']
                system = data['System']
                # print(logtime, codex_name, codex_entry, cmdr, category, region, system)
                insert_codex_db(logtime, codex_name, cmdr, codex_entry, category, region, system)


def read_bio_data(journal_file):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
        print('aktueles  LOG' + str(journal_file))
    bio_color = ['blank']
    region_cmdr = ""
    datei = open(journal_file, 'r', encoding='UTF8')
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
            log_time = (log_date(timestamp))
            date_log = (log_time[0] + "-" + log_time[1] + "-" + log_time[2])
            time_log = (log_time[3] + ":" + log_time[4] + ":" + log_time[5])
            zeilenr = (i + 1)
            bio_cmdr = check_cmdr(journal_file)
            system_infos = check_system(journal_file, zeilenr)
            system = system_infos[0]
            body = system_infos[1]
            bio_color = find_codex(journal_file, zeilenr, biodata)
            if bio_color == '':
                lauf = 1
                while lauf < 1000:
                    filenames = older_logs(log_time, lauf)
                    for filename in reversed(filenames):
                        region_cmdr = check_cmdr(filename)
                        if str(bio_cmdr) == str(region_cmdr):
                            bio_color = find_codex(filename, 99999, biodata)
                        if bio_color != '':
                            # print('codex info in ' + str(filename) + ' gefunden; break')
                            break
                    if bio_color != '':
                        # print('codex info gefunden; break')
                        break
                    if not filenames:
                        bio_color = ''
                        print('break ' + str(lauf))
                        break
                    if lauf == 999:
                        bio_color = ''
                        print('break ' + str(lauf))
                        break
                    lauf = lauf + 1
            else:
                region_cmdr = bio_cmdr

            if system == "blank":
                lauf = 1
                while lauf < 1000:
                    filenames = older_logs(log_time, lauf)
                    for filename in reversed(filenames):
                        system_cmdr = check_cmdr(filename)
                        if str(bio_cmdr) == str(system_cmdr):
                            system_infos = check_system(filename, 99999)
                            system = system_infos[0]
                            body = system_infos[1]
                            if system != 'blank':
                                print('if system != blank:')
                                break
                    if system != 'blank':
                        print('if system != blank:')
                        break
                    if not filenames:
                        system = "no System found"
                        body = "no Body found"
                        print('if system != blank:')
                        break
                    lauf = lauf + 1
            codex_into_db(date_log, time_log, bio_cmdr, biodata, bio_color,system, body,
                          region)


def read_log(filename, search_string, item):
    global success
    # print(search_string, item)
    temp = []
    datei = open(filename, 'r', encoding='UTF8')
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


def codex_into_db(date_log, time_log, cmdr, data, bio_color,systemname, body, region):
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
                            """, (cmdr, data, bio_color, region)).fetchall()
    if not select:
        codex_boolean = 1
    else:
        codex_boolean = 0
        bio_color = ''

    if bio_color == '':
        codex_boolean = 0
    else:
        codex_boolean = 1


    Item = cursor.execute("""SELECT date_log, time_log, cmdr FROM codex WHERE
                            date_log = ? and
                            time_log = ? and
                            cmdr = ?
                            """, (date_log, time_log, cmdr)).fetchall()

    if not Item:
        cursor.execute("INSERT INTO codex VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (date_log, time_log, cmdr, data, bio_color, systemname, body, region, codex_boolean, 0))
        # sql = "INSERT INTO codex VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"

    connection.commit()


def insert_into_death_db(date_log, time_log, cmdr):
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
                            date_log = ? and time_log = ? and cmdr = ?""", (date_log, time_log, cmdr)).fetchall()
    print(select)
    if not select:
        cursor.execute("INSERT INTO player_death VALUES (?, ?, ?)", (date_log, time_log, cmdr))
    connection.commit()


def insert_into_last_sell(date_log, time_log, sell, cmdr):
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
                            date_log = ? and time_log = ? and sell = ?""", (date_log, time_log, sell)).fetchall()
    # print(select)
    if not select:
        cursor.execute("INSERT INTO selling VALUES (?, ?, ?, ?)", (date_log, time_log, sell, cmdr))
    connection.commit()


def read_player_death(filename):
    cmdrs = ''
    cmdr = ''
    date_log = ''
    time_log = ''
    logtimes = read_log(filename, '"event":"Died"', 'timestamp')
    # print(logtimes, success)
    if logtimes:
        # print('Test')
        cmdrs = read_log(filename, '"event":"Commander"', 'Name')
        cmdrs = cmdrs[0]
        # print(logtimes)
        for log_time in logtimes:
            timestamp = log_time
            log_time = (log_date(timestamp))
            date_log = (log_time[0] + "-" + log_time[1] + "-" + log_time[2])
            time_log = (log_time[3] + ":" + log_time[4] + ":" + log_time[5])
            # print(date_log, time_log, cmdrs)
            insert_into_death_db(date_log, time_log, cmdrs)
    multisell(filename)



def multisell(filename):
    cmdrs = ''
    cmdr = ''
    date_log = ''
    time_log = ''
    multi_sell_expo_data = read_log(filename, '"event":"MultiSellExplorationData"', 'timestamp')
    if multi_sell_expo_data:
        for i in multi_sell_expo_data:
            log_time = (log_date(i))
            date_log = (log_time[0] + "-" + log_time[1] + "-" + log_time[2])
            time_log = (log_time[3] + ":" + log_time[4] + ":" + log_time[5])
            sell_type = 'Multisell ExplorationData'
            # print(date_log, time_log, sell_date)
            if success:
                cmdrs = read_log(filename, '"event":"Commander"', 'Name')
                cmdrs = cmdrs[0]
            insert_into_last_sell(date_log, time_log, sell_type, cmdrs)



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
        refresh_treeview()


    def codex_stars():
        global normal_view
        if log_var > 2:
            print('function ' + inspect.stack()[0][3])
        normal_view = 3
        refresh_treeview()


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
        sell_combo = ttk.Combobox(death_frame, value=sell)
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
        death_date_combo = ttk.Combobox(death_frame, value=death_date)
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
        cmdr = combo_cmdr.get()
        # print(cmdr)
        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        data = []
        if cmdr:
            data = cursor.execute("SELECT * FROM codex where cmdr = ? "
                                  "AND date_log BETWEEN ? AND ? "
                                  "ORDER by cmdr, region, data, date_log, time_log",
                                  (cmdr, b_date, e_date)).fetchall()
            if data:
                cursor.execute("UPDATE codex SET player_death = 1 where cmdr = ? "
                               "AND date_log BETWEEN ? AND ? ",
                               (cmdr, b_date, e_date)).fetchall()
                print('DEATH between ' + str(b_date) + ' and '  + str(e_date))
                connection.commit()


    menu_tree = Menu(tree)
    tree.config(menu=menu_tree)
    file_menu = Menu(menu_tree, tearoff=False)
    menu_tree.add_cascade(label="More", menu=file_menu)
    file_menu.add_command(label="Switch View", command=switch_view)
    file_menu.add_command(label="Player Death", command=player_death)
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
        refresh_treeview()
        # print(filter_cmdr + " " + filter_region + " " + filter_bdata)


    def death_selected(event):
        global begin_time, end_time

        filter_sday = sell_combo.get()
        if filter_sday != '':
            b_date = filter_sday
            begin_time.delete(0, END)
            begin_time.insert(0, b_date)

        filter_dday = death_date_combo.get()
        if filter_dday != '':
            e_date = filter_dday
            end_time.delete(0, END)
            end_time.insert(0, e_date)
        refresh_combo()


    def worth_it(search_data):
        if log_var > 2:
            print('function ' + inspect.stack()[0][3])
        # print(search_data[3])
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            select = cursor.execute("SELECT worth FROM codex_entry WHERE data = ? ", (search_data[3],)).fetchone()
        new = str(select[0])
        x = new.replace(',','')
        y = int(x)
        return y



    def read_codex_data():
        if log_var > 2:
            print('function ' + inspect.stack()[0][3])
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            select = cursor.execute("SELECT * FROM codex_data WHERE category = 'Astronomical Bodies' ", ).fetchall()
        # print(select)
        return select


    def codex_treeview():
        if log_var > 2:
            print('function ' + inspect.stack()[0][3])
        sum = 0

        if normal_view == 0:
            if sorting.get() != 0:
                update = 3
            else:
                update = 0
            data = select_filter(filter_cmdr, filter_region, filter_bdata, update)

        elif normal_view == 1:
            data = missing_codex(filter_cmdr, filter_region)
            update = 0
        elif normal_view == 2:
            update = 2
            data = select_filter(filter_cmdr, filter_region, filter_bdata, update)

        elif normal_view == 3:
            data = read_codex_data()
            update = 0

        # if sorting.get() != 0:
        #     data = select_filter(filter_cmdr, filter_region, filter_bdata, sorting.get())

        if not data:
            data = [('DATE', 'TIME', 'COMMANDER', 'SPECIES',
                     'VARIANT', 'SYSTEM', 'BODY', "REGION", 1)]
            sum = 0
        elif normal_view == 2 or normal_view == 0:
            sum = 0
            for i in data:
                sum += worth_it(i)

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

        # insert Data in treeview

        count = 0
        counter = 'a'
        worth = ''
        for record in data:
            if normal_view == 2 or normal_view == 0:
                worth = worth_it(record)
            if update == 3:
                # Wenn nach Datum sortiert wird darf kein Subrow erstellt werden!
                record = (record[0],record[1],record[2],record[3],record[4],record[5],record[6],record[7],1,record[9])
            if normal_view == 3:
                print(record)
                record = (record[0], record[1], record[2], record[4], '', record[6], '',
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
                    else:
                        codex_tree.insert(parent='', index='end', iid=str(str(count) + counter), text="",
                                          values=(count, record[0], record[1], record[2], record[3], record[4], worth,
                                                  record[5], record[6], record[7]), tags=('subrow',))
                        counter = chr(ord(counter) + 1)
            count += 1
        codex_tree.pack()
        if sum > 0 and (normal_view == 2 or normal_view == 0):
            summen_text = ('Summe  - Anzahl Einträge : ' +  str(count) + '     Wertigkeit :  ' +  str(f"{sum:,}"))
            summe = Label(tree_frame, text=summen_text, bg='black', fg='white')
            summe.pack(fill=X, side=RIGHT)


    def refresh_treeview():
        read_codex_entrys()
        global b_date, e_date, death_frame


        if log_var > 2:
            print('function ' + inspect.stack()[0][3])
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
        print(b_date, e_date)
        create_frame()
        print(normal_view)
        codex_treeview()
        codex_tree.bind("<ButtonRelease-1>", selected_record)
        # refreshin_treeview()


    def refreshin_treeview():
        global refresher
        print('refreshing ' + str(refresher))
        refresher += 1
        time.sleep(10.0)

        threading.Thread(target=refresh_treeview).start()

    global buttons_frame
    buttons_frame = Frame(tree, background='black')
    buttons_frame.pack(fill=X, pady=15)

    create_frame()
    codex_treeview()


    def refresh_combo():
        read_codex_entrys()
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        # 1 FILTER CMDR
        if filter_cmdr and not filter_region and not filter_bdata:
            selection_region = cursor.execute("SELECT DISTINCT region FROM codex "
                                       "where cmdr = ? ORDER BY  region",
                                       (filter_cmdr,)).fetchall()
            selection_bio = cursor.execute("SELECT DISTINCT data FROM codex "
                                       "where cmdr = ? ORDER BY data",
                                       (filter_cmdr,)).fetchall()
            regions = ['']
            for i in selection_region:
                regions = regions + [i[0]]
            combo_regions.configure(values=regions)

            b_data = ['']
            for i in selection_bio:
                b_data = b_data + [i[0]]
            combo_bio_data.configure(values=b_data)

        # 2 FILTER CMDR & REGION
        if filter_cmdr and filter_region and not filter_bdata:
            selection = cursor.execute("SELECT DISTINCT data FROM codex "
                                       "where cmdr = ? and region = ? ORDER BY data",
                                       (filter_cmdr, filter_region)).fetchall()
            b_data = ['']
            for i in selection:
                b_data = b_data + [i[0]]
            combo_bio_data.configure(values=b_data)

        # 3 FILTER CMDR & BIO_DATA
        if filter_cmdr and not filter_region and filter_bdata:
            selection_region = cursor.execute("SELECT DISTINCT region FROM codex "
                                       "where cmdr = ? and data = ? ORDER BY region",
                                       (filter_cmdr, filter_bdata)).fetchall()
            regions = ['']
            for i in selection_region:
                regions = regions + [i[0]]
            combo_regions.configure(values=regions)

        # 4 Filter REGION
        if not filter_cmdr and filter_region and not filter_bdata:
            selection_bio = cursor.execute("SELECT DISTINCT data FROM codex "
                                       "where region = ? ORDER BY data",
                                       (filter_region, )).fetchall()
            b_data = ['']
            for i in selection_bio:
                b_data = b_data + [i[0]]
            combo_bio_data.configure(values=b_data)

            selection_cmdr = cursor.execute("SELECT DISTINCT cmdr FROM codex "
                                       "where region = ?  ORDER BY cmdr",
                                       (filter_region, )).fetchall()

            cmdrs = ['']
            for i in selection_cmdr:
                cmdrs = cmdrs + [i[0]]
            combo_cmdr.configure(values=cmdrs)


        # 5 Filter REGION & BIO
        if not filter_cmdr and filter_region and not filter_bdata:
            selection_cmdr = cursor.execute("SELECT DISTINCT cmdr FROM codex "
                                       "where region = ?  ORDER BY cmdr",
                                       (filter_region, )).fetchall()

            cmdrs = ['']
            for i in selection_cmdr:
                cmdrs = cmdrs + [i[0]]
            combo_cmdr.configure(values=cmdrs)

            selection_bio = cursor.execute("SELECT DISTINCT data FROM codex "
                                           "where region = ? ORDER BY data",
                                           (filter_region,)).fetchall()
            b_data = ['']
            for i in selection_bio:
                b_data = b_data + [i[0]]
            combo_bio_data.configure(values=b_data)


        # 6 Filter BIODATA
        if not filter_cmdr and not filter_region and filter_bdata:
            selection_cmdr = cursor.execute("SELECT DISTINCT cmdr FROM codex "
                                       "where data = ? ORDER BY cmdr",
                                       (filter_bdata, )).fetchall()

            cmdrs = ['']
            for i in selection_cmdr:
                cmdrs = cmdrs + [i[0]]
            combo_cmdr.configure(values=cmdrs)

            selection_region = cursor.execute("SELECT DISTINCT region FROM codex "
                                       "where data = ?  ORDER BY region",
                                       (filter_bdata, )).fetchall()
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

            selection_bio = cursor.execute("SELECT DISTINCT data FROM codex ORDER BY data").fetchall()
            b_data = ['']
            for i in selection_bio:
                b_data = b_data + [i[0]]
            combo_bio_data.configure(values=b_data)

        connection.commit()

        return filter


    def create_button():
        global combo_cmdr, combo_regions, combo_bio_data, refresh_button, death_date_combo, sell_combo, sorting

        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        #Combobo CMDRs
        selection = cursor.execute("SELECT DISTINCT cmdr FROM codex ORDER BY cmdr").fetchall()
        # print(selection)
        connection.commit()
        cmdrs = ['']
        for i in selection:
            cmdrs = cmdrs + [i[0]]
        # print(cmdrs)
        label_tag = Label(buttons_frame, text="Filter:", bg='black', fg='white', font=("Helvetica", 11))
        label_tag.pack(side=LEFT, padx=29)
        combo_cmdr = ttk.Combobox(buttons_frame, value=cmdrs, state='readonly')
        combo_cmdr.current(0)
        combo_cmdr.bind("<<ComboboxSelected>>", selected)
        combo_cmdr.pack(side=LEFT, padx=15)

        #Comnbobox Region
        selection = cursor.execute("SELECT DISTINCT region FROM codex ORDER BY region").fetchall()
        connection.commit()
        regions = ['']
        for i in selection:
            regions = regions + [i[0]]
        combo_regions = ttk.Combobox(buttons_frame, value=regions, state='readonly')
        combo_regions.current(0)
        combo_regions.bind("<<ComboboxSelected>>", selected)
        combo_regions.pack(side=LEFT, padx=15)

        #Comnbobox Biodata
        selection = cursor.execute("SELECT DISTINCT data FROM codex ORDER BY data").fetchall()
        connection.commit()
        b_data = ['']
        for i in selection:
            b_data = b_data + [i[0]]
        combo_bio_data = ttk.Combobox(buttons_frame, value=b_data, state='readonly')
        combo_bio_data.current(0)
        combo_bio_data.bind("<<ComboboxSelected>>", selected)
        combo_bio_data.pack(side=LEFT, padx=10)

        sell_combo = ttk.Combobox(buttons_frame, value='none', state='readonly')
        death_date_combo = ttk.Combobox(buttons_frame, value='none', state='readonly')

        refresh_button = Button(buttons_frame, text='Refresh', command=refresh_treeview)
        refresh_button.pack(side=LEFT, padx=20)

        global begin_time, end_time
        label_tag = Label(buttons_frame, text="Datum - Anfang:", bg='black', fg='white', font=("Helvetica", 11))
        label_tag.pack(side=LEFT, padx=10)
        begin_time = Entry(buttons_frame, width=10, font=("Helvetica", 11))
        begin_time.insert(0, '2021-05-19')
        begin_time.pack(side=LEFT, padx=10)
        b_date = begin_time.get()

        label_tag = Label(buttons_frame, text="Ende: ", bg='black', fg='white', font=("Helvetica", 11))
        label_tag.pack(side=LEFT, padx=10)
        end_time = Entry(buttons_frame, width=10, font=("Helvetica", 11))
        end_time.insert(0, date.today())
        end_time.pack(side=LEFT, padx=10)
        e_date = end_time.get()

        sort_button = Checkbutton(buttons_frame,
                                  text="Sort by Date",
                                  bg='black',
                                  fg='white',
                                  selectcolor='black',
                                  activebackground='black',
                                  activeforeground='white',
                                  variable=sorting,
                                  onvalue=3)
        sort_button.pack(side=LEFT, padx=10)


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
            var = str(values[4]).split()
            png = (var[0] + '_' + var[1] + ".png")
            print(png)
            if Path('images/' + png).is_file():
                photo = "images/" + str(png)
                file = resource_path(photo)
                image = Image.open(file)
                image = image.resize((320,145), Image.ANTIALIAS)
                my_img = ImageTk.PhotoImage(image)
                print("File exist")
            else:
                print("File not exist")
                file = resource_path("images/Kein_Bild.png")
                image = Image.open(file)
                image = image.resize((320, 145), Image.ANTIALIAS)
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
                        if a != None:
                            for i in bio_worth:
                                cursor.execute("INSERT INTO codex_show VALUES (?, ?, ?)", (cmdr[0], i[0], a))
                connection.commit()


            temp = cursor.execute("SELECT DISTINCT cmdr, data, region FROM codex WHERE codex.codex = 1").fetchall()
            if temp:
                # print(temp)
                for i in temp:
                    cmdr_select = cursor.execute("""SELECT * from codex_entry where data = ?
                                                    and region = ?""", (i[1], i[2])).fetchall()
                    delete_cmdr = str(i[0])
                    delete_bio = str(cmdr_select[0][0])
                    delete_region = str(cmdr_select[0][3])

                    cursor.execute("DELETE FROM codex_show WHERE cmdr = ? AND data = ? AND region = ?",
                                   (delete_cmdr, delete_bio, delete_region))
                    # print(i, i[0], cmdr_select[0][0], cmdr_select[0][2])
                connection.commit()

            if filter_cmdr and filter_region:
                select = cursor.execute("SELECT * FROM codex_show WHERE cmdr = ? and region = ?"
                                        "ORDER BY data",
                                        (filter_cmdr, filter_region)).fetchall()

            if filter_cmdr and not filter_region:
                select = cursor.execute("SELECT * FROM codex_show WHERE cmdr = ?"
                                        "ORDER BY data",
                                        (filter_cmdr, )).fetchall()

            if not filter_cmdr and filter_region:
                select = cursor.execute("SELECT * FROM codex_show WHERE region = ?"
                                        "ORDER BY data",
                                        (filter_region, )).fetchall()

            if not filter_cmdr and not filter_region:
                select = cursor.execute("SELECT * FROM codex_show ORDER BY region, data").fetchall()
        lauf = 1
        data = []
        for i in select:
            data.append((' ', ' ', i[0], i[1], ' ', ' ', ' ', i[2], 1))
            lauf += 1
        return data


    tree.mainloop()


def select_filter(cmdr, region, bio_data, update):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    if update != 3:
        order = 'cmdr, region, data, date_log, time_log'
    else:
        order = 'date_log desc, time_log DESC'

    if cmdr and region and bio_data:
        data = cursor.execute("""SELECT * FROM codex where cmdr = ? and region = ? and data = ?
                              AND player_death = 0                              
                              AND date_log BETWEEN ? AND ? 
                              ORDER by """ + order,
                              (cmdr, region, bio_data, b_date,e_date)).fetchall()
    # Fall 2 CMDR & Region
    elif cmdr and region and not bio_data:
        data = cursor.execute("""SELECT * FROM codex where cmdr = ? and region = ?
                              AND player_death = 0                              
                              AND date_log BETWEEN ? AND ? 
                              ORDER by """ + order,
                              (cmdr, region, b_date,e_date)).fetchall()
    # Fall 3 CMDR & Bio
    elif cmdr and not region and bio_data:
        data = cursor.execute("""SELECT * FROM codex where cmdr = ? and data = ?
                              AND player_death = 0                              
                              AND date_log BETWEEN ? AND ?                               
                              ORDER by """ + order,
                              (cmdr,bio_data, b_date,e_date)).fetchall()
    # Fall4 only CMDR
    elif cmdr and not region and not bio_data:
        data = cursor.execute("""SELECT * FROM codex where cmdr = ?
                              AND player_death = 0                              
                              AND date_log BETWEEN ? AND ? 
                              ORDER by """ + order,
                              (cmdr, b_date,e_date)).fetchall()

    # Fall 5 only Region
    elif not cmdr and region and not bio_data:
        data = cursor.execute("""SELECT * FROM codex where region = ?
                              AND player_death = 0                              
                              AND date_log BETWEEN ? AND ?
                              ORDER by """ + order,
                              (region, b_date,e_date)).fetchall()
    # Fall 6 only Biodata
    elif not cmdr and not region and bio_data:
        data = cursor.execute("""SELECT * FROM codex where data = ?
                              AND player_death = 0                              
                              AND date_log BETWEEN ? AND ? 
                              ORDER by """ + order,
                              (bio_data, b_date,e_date)).fetchall()
    # Fall 7 Region & Biodata
    elif not cmdr and region and bio_data:
        data = cursor.execute("""SELECT * FROM codex where region = ? and data = ?
                              AND player_death = 0                              
                              AND date_log BETWEEN ? AND ? 
                              ORDER by """ + order,
                              (region,bio_data, b_date,e_date)).fetchall()
    # Fall 8 no Filter
    elif not cmdr and not region and not bio_data:
        data = cursor.execute("""SELECT * FROM codex 
                              where player_death = 0 AND date_log BETWEEN ? AND ? 
                              ORDER by """ + order, (b_date,e_date)).fetchall()
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
    datei = open(journal_file, 'r', encoding='UTF8')
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
    species = 'blank empty'
    system_address_codex = ''
    tmp = ''
    datei = open(journal_file, 'r', encoding='UTF8')
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
    cmdr = ""
    datei = open(journal_file, 'r', encoding='UTF8')
    for zeile in datei:
        search_string = 'Commander'
        if zeile.find(search_string) > -1:
            data = json.loads(zeile)
            cmdr = data['Name']
            break
    # print(cmdr)
    return cmdr


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
    Item = cursor.execute("SELECT Name FROM odyssey WHERE Name = ?", (name,)).fetchall()

    if not Item:
        cursor.execute("INSERT INTO odyssey VALUES (?, ?)", (name, count))
        connection.commit()
    else:
        Item = cursor.execute("SELECT Count FROM odyssey WHERE Name = ?", (name,)).fetchone()
        count += int(Item[0])
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
    DATA = cursor.execute("SELECT * FROM odyssey WHERE Name LIKE ? ORDER BY Name",
                          (filter_b,)).fetchall()
    connection.close()
    # print(DATA)
    return DATA


def cp_to_clipboard():
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

    root.clipboard_clear()
    if BGS == 1:
        root.clipboard_append(voucher.get_string(sortby="System"))
        root.clipboard_append('\n')
        root.clipboard_append('\n')
        root.clipboard_append(bgs.get_string(sortby="System"))
    elif MATS == 1:
        root.clipboard_append(mats_table.get_string(sortby="Materials"))
    elif ODYS == 1:
        root.clipboard_append(mats_table.get_string(sortby="Materials"))
    root.update()


def codex_menu():
    global BGS, MATS, ODYS, CODEX
    BGS = 0
    ODYS = 0
    MATS = 0
    CODEX = 1
    vortick.config(state=DISABLED)
    nachtick.config(state=DISABLED)
    check_but.deselect()
    check_but.config(state=DISABLED)
    Filter.delete(0, END)
    auswertung()


def mats_menu():
    global BGS, MATS, ODYS, CODEX
    BGS = 0
    ODYS = 0
    MATS = 1
    CODEX = 0
    check_but.config(state=NORMAL)
    vortick.config(state=DISABLED)
    nachtick.config(state=DISABLED)
    Filter.delete(0, END)
    auswertung()


def odys_menu():
    global BGS, MATS, ODYS, CODEX
    BGS = 0
    ODYS = 1
    MATS = 0
    CODEX = 0
    check_but.config(state=NORMAL)
    vortick.config(state=DISABLED)
    nachtick.config(state=DISABLED)
    Filter.delete(0, END)
    auswertung()


def bgs_menu():
    global BGS, MATS, ODYS, CODEX
    BGS = 1
    ODYS = 0
    MATS = 0
    CODEX = 0
    check_but.config(state=NORMAL)
    vortick.config(state=NORMAL)
    nachtick.config(state=NORMAL)
    Filter.delete(0, END)
    threading_auto()


def insert_logfile_in_db(file):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("CREATE table IF NOT EXISTS logfiles (Name TEXT)")
    Item = cursor.execute("SELECT Name FROM logfiles WHERE Name = ?", (file,)).fetchall()
    if not Item:
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
    return file


def check_last_logs(filenames_codex, length):
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    last_log_file = select_last_log_file()[0]
    print('last log files = ' ,last_log_file)
    if last_log_file != '0':
        lauf = 0
        for i in filenames_codex:
            if i != last_log_file:
                lauf += 1
            else:
                break
        i = 0
        # Alle Logfiles vor dem last_log_file werden aus der Liste entfernt
        while i < lauf:
            filenames_codex.pop(0)
            i += 1
    # nur die neuesten Logfiles und die letzen zwei schon eingelesenen werden übergeben.
    return filenames_codex


def read_codex_entrys():
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    system.delete('1.0',END)
    system.insert(END, 'Codex Daten werden gelesen')
    # Lade alle logfiles in die Variable filenames_codex
    # filenames_codex = glob.glob(path + "\\Journal.*.log")
    filenames_codex = file_names(1)
    last_log = (len(filenames_codex))
    check_last_logs(filenames_codex, last_log)
    for filename in filenames_codex:
        read_bio_data(filename)
        read_log_codex(filename)
        read_player_death(filename)
        insert_logfile_in_db(filename)
    # treeview_codex()


def auswertung():
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    if log_var > 2:
        print("lösche tabellen")
    # cursor.execute("DROP TABLE IF EXISTS codex_entry")
    # cursor.execute("DROP TABLE IF EXISTS codex")
    # cursor.execute("DROP TABLE IF EXISTS logfiles")
    cursor.execute("DROP TABLE IF EXISTS influence")
    cursor.execute("DROP TABLE IF EXISTS odyssey")
    cursor.execute("DROP TABLE IF EXISTS vouchers")
    system.delete(.0, END)
    filenames = file_names(0)
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
    if not filenames:
        # Wenn es keine logfiles an diesem Tag gibt, dann
        if CODEX == 1:
            # system.insert(END, 'Codex Daten werden gelesen')
            read_codex_entrys()
            treeview_codex()
        else:
            system.insert(END, 'Keine Log-Files für den Tag vorhanden')
    else:
        if BGS == 1:
            for filename in filenames:
                einfluss_auslesen(filename)
                redeem_voucher(filename)
                multi_sell_exploration_data(filename)
                market_sell(filename)
            b_filter = Filter.get()
            DATA = print_vouchers_db(b_filter)
            if DATA:
                system.insert(END,
                              ('    ----------    Bounty, Bonds, ExplorerData and Trade ...    ----------\n\n'))
                for i in DATA:
                    tmp = (f"{i[3]:,}")
                    tmp = tmp.replace(',', '.')
                    tmp = tmp + ' Cr'
                    system.insert(END, ((str(i[1])[0:15]) + '\t\t' + (str(i[2])[0:25]) + '\t\t\t' + (str(i[0])[0:15])
                                        + '\n\t\t\t\t\t' + tmp + '\n'))
                    voucher.add_row((i[0], i[1], i[2], tmp))
                system.insert(END,
                              (
                                  '\n    -----------------------------------  Influence  -----------------------------------\n'))
                system.insert(END, ('\n'))
            else:
                nodata = 1
                print('NO VOUCHER DATA')
            DATA = print_influence_db(b_filter)
            if DATA:
                for i in DATA:
                    system.insert(END, ((str(i[0])[0:15]) + '\t\t' + (str(i[1])[0:25]) + '\t\t\t\t' + str(i[2]) + '\n'))
                    bgs.add_row((i[0], i[1], i[2]))
            else:
                print('NO INFLUENCE DATA')
                if nodata == 1:
                    system.insert(END, '\n\tKeine Daten vorhanden')

        elif MATS == 1:
            for filename in filenames:
                mats_auslesen(filename)
            b_filter = Filter.get()
            DATA = print_engi_stuff_db(b_filter)
            for i in DATA:
                system.insert(END, ((str(i[0])) + '\t \t \t \t' + (str(i[1])) + '\n'))
                mats_table.add_row((i[0], i[1]))

        elif ODYS == 1:
            print('ODYS == 1')
            for filename in filenames:
                ody_mats_auslesen(filename)
            b_filter = Filter.get()
            DATA = print_engi_stuff_db(b_filter)
            for i in DATA:
                system.insert(END, ((str(i[0])) + '\t \t \t \t' + (str(i[1])) + '\n'))
                mats_table.add_row((i[0], i[1]))

        elif CODEX == 1:
            # system.insert(END, 'Codex Daten werden gelesen')
            read_codex_entrys()
            treeview_codex()

    # if not filenames:
    #     system.insert(END, 'Keine Log-Files für den Tag vorhanden')


def set_language_db(var):
    print('function ' + inspect.stack()[0][3])
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    print('before ' , var)
    if var == 'leer':

        cursor.execute("""CREATE table IF NOT EXISTS lan_db 
        (lang TEXT, switch INTEGER)""")
        item = cursor.execute("SELECT lang FROM lan_db").fetchall()
        print(item)
        if not item:
            cursor.execute("INSERT INTO lan_db VALUES (?, ?)", ('german', '1'))
            connection.commit()
            # print('ttest')
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
        print('TEST')
        cursor.execute("UPDATE lan_db SET lang = ?", (var,))
        connection.commit()
        connection.close()
    print('after ', var)
    return(var)


def main():
    if log_var > 2:
        print('function ' + inspect.stack()[0][3])
    global system, root, Tag, Monat, Jahr, hour, minute, BGS, MATS, ODYS, vortick, nachtick, Filter, \
        tree, check_but #, label_tag, label_monat, label_jahr

    select = set_language_db('leer')
    # print('Language selected:')
    # print(select)
    if not select or select[0][0] == 'german' or select == 'leer':
        text = [('Tag'), ('Monat'), ('Jahr'), ('Der letzte Tick war um:'), ('vor dem Tick'), ('nach dem Tick')]
    else:
        text = [('Day'), ('Month'), ('Year'), ('Last BGS TICK was at  '), ('before Tick'), ('after Tick')]


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
    SNPX = resource_path("SNPX.png")
    Horizon = resource_path("Horizon.png")
    bg = PhotoImage(file=SNPX)
    bg2 = PhotoImage(file=Horizon)

    my_menu = Menu(root)
    root.config(menu=my_menu)

    file_menu = Menu(my_menu, tearoff=False)
    my_menu.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="BGS", command=bgs_menu)
    file_menu.add_command(label="MATS", command=mats_menu)
    file_menu.add_command(label="Odyssey", command=odys_menu)
    file_menu.add_command(label="Codex", command=codex_menu)
    file_menu.add_command(label="Exit", command=root.quit)
    settings_menu = Menu(my_menu, tearoff=False)
    my_menu.add_cascade(label="Setting", menu=settings_menu)


    my_top_logo = Label(root, image=bg, bg='black')
    my_top_logo.pack(fill=X)
    my_bottom_logo = Label(root, image=bg2, bg='black')
    my_bottom_logo.place(x=0, y=100)
    ############################################### my_text_box ##############################################
    my_text_box = Label(root, bg='black', borderwidth=2)
    my_text_box.config(width=280)
    # my_text_box = Label(root)
    my_text_box.place(x=25,y=100)


    #################### my_time_label ###########################

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

    #################### my_time_label ###########################

    global check_auto_refresh

    ############################ bgs_tick_frame ############################

    bgs_tick_frame = Frame(my_text_box, bg='black', borderwidth=2)
    # bgs_tick_frame = Frame(my_text_box, bg='black')
    bgs_tick_frame.pack(side=LEFT, pady=5)

    last_tick_label = Label(bgs_tick_frame, text=text[3], bg='black', fg='white', font=("Helvetica", 12), justify=LEFT)
    last_tick_label.grid(column=0, row=0)

    ############# my_tick ############

    my_tick = Frame(bgs_tick_frame, bg='black')
    my_tick.grid(column=1, row=0)

    hour = Entry(my_tick, width=2, font=("Helvetica", 12))
    hour.insert(0, str(t_hour))
    hour.grid(column=0, row=0)
    label_colon = Label(my_tick,
          text=""":""", bg='black', fg='white', font=("Helvetica", 12),
          justify=LEFT)
    label_colon.grid(column=2, row=0)

    minute = Entry(my_tick, width=2, font=("Helvetica", 12))
    minute.insert(0, str(t_minute))
    minute.grid(column=3, row=0)

    ############# my_tick ############
    my_check_box_place = Frame(root, bg='black', borderwidth=2)
    my_check_box_place.place(x=300, y=100)
    check_auto_refresh = IntVar()
    #
    check_but = Checkbutton(my_check_box_place, text="Autorefresh    "
                            , variable=check_auto_refresh
                            , bg='black'
                            , fg='white'
                            , selectcolor='black'
                            , activebackground='black'
                            , activeforeground='white'
                            , command=threading_auto
                            , font=("Helvetica", 10))
    check_but.pack()

    ################## my_boxes #####################

    my_boxes = Frame(root, bg='black', borderwidth=2)
    my_boxes.place(x=300, y=125)

    v = IntVar()
    vortick = Radiobutton(my_boxes,
                          text=text[4], bg='black', fg='white', selectcolor='black',
                          activebackground='black', activeforeground='white',
                          # padx=10,
                          variable=v,
                          value=1, command=tickfalse)
    vortick.grid(column=0, row=0, sticky=W)


    nachtick = Radiobutton(my_boxes,
                           text=text[5], bg='black', fg='white', selectcolor='black',
                           activebackground='black', activeforeground='white',
                           # padx=10,
                           variable=v,
                           value=2, command=ticktrue)
    nachtick.grid(column=0, row=1, sticky=W)
    nachtick.select()


    ################################### my_folder #######################################

    my_folder = Frame(root, bg='black')
    my_folder.place(x=15, y=180)
    myfolder_grid = Frame(my_folder, bg='black')
    myfolder_grid.grid()

    label_filter = Label(myfolder_grid, text="Filter:", bg='black',
                       fg='white', font=("Helvetica", 12)).grid(column=0, row=0, sticky=W)
    Filter = Entry(myfolder_grid, width=37, font=("Helvetica", 10))

    Filter.insert(0, filter_name)
    Filter.grid(column=0, row=0)

    folder = Entry(myfolder_grid, width=62, bg='black', fg='white', font=("Helvetica", 8))
    folder.insert(END, path)
    folder.grid(column=0, row=1, pady=5)
    ################################### my_folder #######################################

    system = Text(root, height=14, width=54, bg='black', fg='white', font=("Helvetica", 10))
    system.place(x=15, y=235)

    version_but = Button(root,
                         text='Version 0.5.2.0',
                         activebackground='#000050',
                         activeforeground='white',
                         bg='black',
                         fg='white',
                         command=logging,
                         font=("Helvetica", 10))
    version_but.place(x=15, y=465)

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
        threading_auto()

    root.bind('<Return>', callback)

    def refresh_label(data):
        label_tag.config(text=data[0])
        label_monat.config(text=data[1])
        label_jahr.config(text=data[2])
        last_tick_label.config(text=data[3])
        vortick.config(text=data[4])
        nachtick.config(text=data[5])

    def set_language(language):
        if language == 1:
            data = [('Tag'), ('Monat'), ('Jahr'), ('Der letzte TICK war um '), ('vor dem Tick'), ('nach dem Tick')]
            set_language_db('german')
        elif language == 2:
            data = [('Day'), ('Month'), ('Year'), ('Last BGS TICK was at '), ('before Tick'), ('after Tick')]
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

    root.mainloop()


last_tick()

main()
