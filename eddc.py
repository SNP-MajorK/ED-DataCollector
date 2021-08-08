# Created by MajorK https://github.com/SNP-MajorK/ED-DataCollector

import glob
import json
import threading
import time
import sqlite3
import inspect
from builtins import print
from datetime import date
from tkinter import *
from winreg import *

import requests
from prettytable import PrettyTable

# filter_name = 'Stellanebula Project'
filter_name = ''
BGS = 1
MATS = 0
ODYS = 0
root = ''
log_var = 2
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

with OpenKey(HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders") as key:
    value = QueryValueEx(key, '{4C5C32FF-BB9D-43B0-B5B4-2D72E54EAAA4}')
path = value[0] + '\\Frontier Developments\\Elite Dangerous\\'
# path = value[0] + '\\Frontier Developments\\'

bgs = PrettyTable(['System', 'Faction', 'Influence'])
voucher = PrettyTable(['Voucher', 'System', 'Faction', 'Credits'])
mats_table = PrettyTable(['Materials', 'Count'])


def last_tick():
    if log_var > 0:
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


def file_names():
    print('Get File of GUI Date')
    Tag2 = Tag.get()
    Monat2 = Monat.get()
    Jahr2 = Jahr.get()
    Date = str(Jahr2 + Monat2 + Tag2)
    filenames = glob.glob(path + "\\Journal." + Date + "*.log")
    print(filenames)
    return filenames


def date_for_ma(missionid, gmd_faction, x):
    if log_var > 0:
        print('function ' + inspect.stack()[0][3])
    mission_found = False
    while x < 7:
        Tag2 = str(int(Tag.get()) - x)
        Monat2 = Monat.get()
        Jahr2 = Jahr.get()
        Date = str(Jahr2 + Monat2 + str(Tag2).zfill(2))
        filenames = glob.glob(path + "\\Journal." + Date + "*.log")
        for filename in filenames:
            # print(filename)
            if get_mission_data(missionid, filename, gmd_faction):
                mission_found = True
                return mission_found
        x += 1


def get_mission_data(missionid, journal_file, gmd_faction):
    if log_var > 0:
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
    if log_var > 0:
        print('function ' + inspect.stack()[0][3])
    filenames = file_names()
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
    if log_var > 0:
        print('function ' + inspect.stack()[0][3])
    global log_time
    log_year = (timestamp[:4])
    log_month = (timestamp[5:7])
    log_day = (timestamp[8:10])
    log_hour = (timestamp[11:13])
    log_minute = (timestamp[14:16])
    log_time = [log_year, log_month, log_day, log_hour, log_minute]
    return log_time


def extract_data(data):
    if log_var > 0:
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
    if log_var > 0:
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
    if log_var > 0:
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
    if log_var > 0:
        print('function ' + inspect.stack()[0][3])
    for filename in filenames:
        datei = open(filename, 'r', encoding='UTF8')
        for zeile2 in datei:
            search_string2 = "FSDJump"
            if (zeile2.find(search_string2)) > -1:
                star_systems_data = json.loads(zeile2)
                # print(star_systems_data)
                starchart_db(star_systems_data['SystemAddress'], star_systems_data['StarSystem'])
        datei.close()


def influence_db(ID, Faction, Influence):
    if log_var > 0:
        print('function ' + inspect.stack()[0][3])
    if ID == '':
        # print('NULL')
        ID = 'NONE'
    connection = sqlite3.connect("eddc.db")
    cursor = connection.cursor()
    cursor.execute("CREATE table IF NOT EXISTS influence (SystemName TEXT, Faction TEXT, Influence INTEGER)")
    SystemName = cursor.execute("SELECT SystemName FROM starchart WHERE SystemID= ?", (ID,)).fetchall()
    if not ID == 'NONE':
        SystemName = SystemName[0][0]
        cursor.execute("SELECT SystemName, Faction, Influence FROM influence WHERE SystemName= ? and Faction = ?", (SystemName, Faction,))
        result = cursor.fetchall()
        if not result:
            if log_var > 0:
                print('DB Else')
            cursor.execute("INSERT INTO influence VALUES (?, ?, ?)", (SystemName, Faction, Influence))
            connection.commit()
    connection.close()


def update_influence_db(ID, Faction, Influence):
    if log_var > 0:
        print('function ' + inspect.stack()[0][3])
    if ID == '':
        # print('NULL')
        ID = 'NONE'
    connection = sqlite3.connect("eddc.db")
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
        # imperial = cursor.execute(
        #     "SELECT SystemName, Influence FROM influence WHERE Faction = 'Mainani Empire Party'",
        #     ).fetchall()
        # print(imperial)
    connection.close()


def read_influence_db(ID, faction):
    if log_var > 0:
        print('function ' + inspect.stack()[0][3])
    if isinstance(ID, int):
        connection = sqlite3.connect("eddc.db")
        cursor = connection.cursor()
        cursor.execute("CREATE table IF NOT EXISTS influence (SystemName TEXT, Faction TEXT, Influence INTEGER)")
        SystemName = cursor.execute("SELECT SystemName FROM starchart WHERE SystemID= ?", (ID,)).fetchall()
        # print(SystemName)
        try:
            SystemName = SystemName[0][0]
        except IndexError:
            filenames = file_names()
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
    if log_var > 0:
        print('function ' + inspect.stack()[0][3])
    connection = sqlite3.connect("eddc.db")
    cursor = connection.cursor()
    filter_b = '%' + filter_b + '%'
    cursor.execute("CREATE table IF NOT EXISTS influence (SystemName TEXT, Faction TEXT, Influence INTEGER)")
    DATA = cursor.execute("SELECT * FROM influence WHERE SystemName LIKE ? OR Faction LIKE ? GROUP BY 1, 2, 3",
                          (filter_b, filter_b)).fetchall()
    connection.close()
    return DATA


def starchart_db(ID, SystemName):
    # if log_var > 0:
    #     print('function ' + inspect.stack()[0][3])
    connection = sqlite3.connect("eddc.db")
    cursor = connection.cursor()
    cursor.execute("CREATE table IF NOT EXISTS starchart (SystemID INTEGER, SystemName TEXT)")
    cursor.execute("SELECT SystemID FROM starchart WHERE SystemID= ?", (ID,))
    result = cursor.fetchall()
    if not result:
        if log_var > 0:
            print('DB Else')
        cursor.execute("INSERT INTO starchart VALUES (?, ?)", (ID, SystemName,))
        connection.commit()
    connection.close()


def read_starchart_table(ID):
    if log_var > 0:
        print('function ' + inspect.stack()[0][3])
    if isinstance(ID, int):
        connection = sqlite3.connect("eddc.db")
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
    if log_var > 0:
        print('function ' + inspect.stack()[0][3])
    tick_hour = hour.get()
    tick_minute = minute.get()
    tick_time[3] = tick_hour[0:2]
    tick_time[4] = tick_minute[0:2]
    if log_var == 5:
        print(tick_time)
    print(journal_file)
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
    if log_var > 0:
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
    if log_var > 0:
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
    if log_var > 0:
        print('function ' + inspect.stack()[0][3])

    datei = open(journal_file, 'r', encoding='UTF8')
    line = 0
    for zeile in datei:
        line += 1
        search_string = "MarketSell"
        if (zeile.find(search_string)) > -1:
            if check_tick_time(zeile, tick):
                print(zeile)
                data_found = line
                data = find_last_docked(journal_file, data_found)
                if log_var > 1:
                    print(data)
                faction = data[0]
                system_name = data[1]
                data = json.loads(zeile)

                try:
                    # if is_json_key_present(data, 'Blackmarket'):
                    if data['BlackMarket']:
                        vouchers_db('BlackMarket', system_name, str(faction), int(data["TotalSale"]))
                    else:
                        print(data)
                        vouchers_db('MarketSell', system_name, str(faction), int(data["TotalSale"]))
                except KeyError:
                    print('test2')
                    vouchers_db('MarketSell', system_name, str(faction), int(data["TotalSale"]))
    datei.close()


def find_last_docked(journal_file, data_found):
    if log_var > 0:
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
    if log_var > 0:
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
    if log_var > 0:
        print('function ' + inspect.stack()[0][3])
        print(vouchers, systemname, faction, amount)

    connection = sqlite3.connect("eddc.db")
    cursor = connection.cursor()
    cursor.execute("CREATE table IF NOT EXISTS vouchers (Vouchers TEXT, SystemName Text, Faction TEXT, Amount INTEGER)")
    Item = cursor.execute("SELECT Amount FROM vouchers WHERE SystemName = ? and Faction = ? and Vouchers = ?",
                          (systemname, faction, vouchers)).fetchall()
    print(Item)
    if not Item:
        cursor.execute("INSERT INTO vouchers VALUES (?, ?, ?, ?)", (vouchers, systemname, faction, amount))
        connection.commit()
    else:
        Item = cursor.execute("SELECT Amount FROM vouchers WHERE SystemName = ? and Faction = ? and Vouchers = ?",
                              (systemname, faction, vouchers)).fetchone()
        print(Item[0])
        amount += int(Item[0])
        print(amount)
        cursor.execute("UPDATE vouchers SET Amount = ? where SystemName = ? and Faction = ? and Vouchers = ?",
                       (amount, systemname, faction, vouchers))
        connection.commit()
    connection.close()


def print_vouchers_db(filter_b):
    if log_var > 0:
        print('function ' + inspect.stack()[0][3])

    connection = sqlite3.connect("eddc.db")
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
    if log_var > 0:
        print('function ' + inspect.stack()[0][3])

    while check_var.get() != 0:
        print('while autorefresh')
        if check_var.get() != 0:
            print(check_var.get())
            time.sleep(60.0)
            refreshing()


def refreshing():
    if log_var > 0:
        print('function ' + inspect.stack()[0][3])

    system.delete(1.0, END)
    system.insert(INSERT, 'Auswertung läuft ')
    i = 0
    while i < 4:
        time.sleep(0.4)
        system.insert(INSERT, '.')
        i += 1
    if log_var > 1:
        print('Checkbox an oder aus ' + str(check_var.get()))
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

    auswertung()


def threading_auto():
    if log_var > 0:
        print('function ' + inspect.stack()[0][3])

    if check_var.get() != 0:
        threading.Thread(target=autorefresh).start()
    else:
        threading.Thread(target=refreshing).start()


def logging():
    global log_var
    log_var += 1
    print(log_var)


def mats_auslesen(journal_file):
    if log_var > 0:
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
    if log_var > 0:
        print('function ' + inspect.stack()[0][3])

    mats_table.clear_rows()
    # global name_list, count_list
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


def extract_engi_stuff(data, state):
        try:
            engi_stuff_ody_db(str(data['Name_Localised']), int(data['Count']), state)
        except KeyError:
            engi_stuff_ody_db(str(data['Name']), int(data['Count']), state)


def engi_stuff_ody_db(name, count, state):
    if log_var > 0:
        print('function ' + inspect.stack()[0][3])

    connection = sqlite3.connect("eddc.db")
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
    if log_var > 0:
        print('function ' + inspect.stack()[0][3])

    connection = sqlite3.connect("eddc.db")
    cursor = connection.cursor()
    filter_b = '%' + filter_b + '%'
    cursor.execute("CREATE table IF NOT EXISTS odyssey (Name TEXT, Count INTEGER)")
    DATA = cursor.execute("SELECT * FROM odyssey WHERE Name LIKE ? ORDER BY Name",
                          (filter_b, )).fetchall()
    connection.close()
    # print(DATA)
    return DATA


def cp_to_clipboard():
    if log_var > 0:
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


def mats_menu():
    global BGS, MATS, ODYS
    BGS = 0
    ODYS = 0
    MATS = 1
    vortick.config(state=DISABLED)
    nachtick.config(state=DISABLED)
    Filter.delete(0, END)
    auswertung()


def odys_menu():
    global BGS, MATS, ODYS
    BGS = 0
    ODYS = 1
    MATS = 0
    vortick.config(state=DISABLED)
    nachtick.config(state=DISABLED)
    Filter.delete(0, END)
    auswertung()


def bgs_menu():
    global BGS, MATS, ODYS
    BGS = 1
    ODYS = 0
    MATS = 0
    vortick.config(state=NORMAL)
    nachtick.config(state=NORMAL)
    Filter.delete(0, END)
    threading_auto()


def auswertung():
    if log_var > 0:
        print('function ' + inspect.stack()[0][3])
    connection = sqlite3.connect("eddc.db")
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS influence")
    cursor.execute("DROP TABLE IF EXISTS odyssey")
    cursor.execute("DROP TABLE IF EXISTS vouchers")
    system.delete(.0, END)
    Tag2 = Tag.get()
    Monat2 = Monat.get()
    Jahr2 = Jahr.get()
    Date = str(Jahr2 + Monat2 + Tag2)
    filenames = glob.glob(path + "\\Journal." + Date + "*.log")
    nodata = 0
    if log_var == 2:
        print(filenames)
    auto_refresh = False
    lauf_r = 0
    if auto_refresh is True:
        auto = len(filenames) - 1
        while lauf_r < auto:
            del filenames[lauf_r]
            lauf_r += 1
    if not filenames:
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
                              ('\n    -----------------------------------  Influence  -----------------------------------\n'))
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

    # if not filenames:
    #     system.insert(END, 'Keine Log-Files für den Tag vorhanden')


def main():
    global system, root, Tag, Monat, Jahr, hour, minute, BGS, MATS, ODYS, vortick, nachtick, Filter
    root = Tk()
    root.title('Elite Dangerous Data Collector')
    try:
        img = ("eddc.ico")
        root.iconbitmap(img)
    except TclError:
        print('Icon not found)')

    root.configure(background='black')
    root.minsize(415, 500)
    root.maxsize(415, 500)
    bg = PhotoImage(file=("SNPX.png"))
    bg2 = PhotoImage(file=("Horizon.png"))

    my_menu = Menu(root)
    root.config(menu=my_menu)

    file_menu = Menu(my_menu, tearoff=False)
    my_menu.add_cascade(label="Datei", menu=file_menu)
    file_menu.add_command(label="BGS", command=bgs_menu)
    file_menu.add_command(label="MATS", command=mats_menu)
    file_menu.add_command(label="Odyssey", command=odys_menu)
    file_menu.add_command(label="Exit", command=root.quit)

    my_top_logo = Label(root, image=bg, bg='black')
    my_top_logo.pack()
    my_bottom_logo = Label(root, image=bg2, bg='black')
    my_bottom_logo.place(x=0, y=100)
    my_text_box = Label(root, bg='black')
    my_text_box.pack()
    my_time = Frame(my_text_box, bg='black')
    my_time.grid()
    my_time_label = Frame(my_time, bg='black')
    my_time_label.grid()

    label_Tag = Label(my_time_label, text="Tag:", bg='black',
                      fg='white', font=("Helvetica", 12)).grid(column=0, row=0, sticky=W)
    Tag = Entry(my_time_label, width=2, font=("Helvetica", 12))
    Tag.insert(0, Day)
    Tag.grid(column=1, row=0, padx=5)

    label_Tag2 = Label(my_time_label, text="Monat:", bg='black',
                       fg='white', font=("Helvetica", 12)).grid(column=2, row=0)
    Monat = Entry(my_time_label, width=2, font=("Helvetica", 12))
    Monat.insert(0, Month)
    Monat.grid(column=3, row=0, padx=5)

    label_Tag3 = Label(my_time_label, text="Jahr:", bg='black',
                       fg='white', font=("Helvetica", 12)).grid(column=4, row=0)
    Jahr = Entry(my_time_label, width=2, font=("Helvetica", 12))
    Jahr.insert(0, Year)
    Jahr.grid(column=5, row=0, padx=5)
    global check_var

    my_frame = Frame(my_time, bg='black')
    my_frame.grid(column=0, row=1)
    Label(my_frame,
          text=""" Der letzte Tick war um:    """, bg='black', fg='white', font=("Helvetica", 12),
          justify=LEFT).grid(column=0, row=0)

    my_tick = Frame(my_frame, bg='black')
    my_tick.grid(column=1, row=0)

    hour = Entry(my_tick, width=2, font=("Helvetica", 12))
    hour.insert(0, str(t_hour))
    hour.grid(column=0, row=0)
    Label(my_tick,
          text=""":""", bg='black', fg='white', font=("Helvetica", 12),
          justify=LEFT).grid(column=2, row=0)
    minute = Entry(my_tick, width=2, font=("Helvetica", 12))
    minute.insert(0, str(t_minute))
    minute.grid(column=3, row=0)

    check_var = IntVar()

    check_but = Checkbutton(my_time, text="Autorefresh    "
                            , variable=check_var
                            , bg='black'
                            , fg='white'
                            , selectcolor='black'
                            , activebackground='black'
                            , activeforeground='white'
                            , command=threading_auto
                            , font=("Helvetica", 10))
    check_but.grid(column=1, row=0)

    my_boxes = Frame(my_time, bg='black')
    my_boxes.grid(column=1, row=1)

    v = IntVar()
    vortick = Radiobutton(my_boxes,
                          text="vor dem Tick", bg='black', fg='white', selectcolor='black',
                          activebackground='black', activeforeground='white',
                          padx=10,
                          variable=v,
                          value=1, command=tickfalse)
    vortick.grid(column=0, row=0, sticky=W)

    nachtick = Radiobutton(my_boxes,
                           text="nach dem Tick", bg='black', fg='white', selectcolor='black',
                           activebackground='black', activeforeground='white',
                           padx=10,
                           variable=v,
                           value=2, command=ticktrue)
    nachtick.grid(column=0, row=1)
    nachtick.select()

    my_folder = Frame(root, bg='black')
    my_folder.pack()
    myfolder_grid = Frame(my_folder, bg='black')
    myfolder_grid.grid()

    label_Tag2 = Label(myfolder_grid, text="Filter:", bg='black',
                       fg='white', font=("Helvetica", 12)).grid(column=0, row=0, sticky=W)
    Filter = Entry(myfolder_grid, width=37, font=("Helvetica", 10))

    # print(' HIER KOMMT DAS Dropdown Menu hin')

    Filter.insert(0, filter_name)
    Filter.grid(column=0, row=0)

    folder = Entry(myfolder_grid, width=62, bg='black', fg='white', font=("Helvetica", 8))
    folder.insert(END, path)
    folder.grid(column=0, row=1, pady=5)

    system = Text(root, height=13, width=70, bg='black', fg='white', font=("Helvetica", 10))
    system.pack(padx=15, pady=5)

    version_but = Button(root,
                         text='Version 0.2.2.6',
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
    ok_but.place(x=360, y=465)

    def callback(event):
        threading_auto()


    root.bind('<Return>', callback)

    root.mainloop()


last_tick()

main()
