# Created by MajorK https://github.com/SNP-MajorK/ED-DataCollector

import glob
import json
# import os
# import sys
import threading
import time
from datetime import date
from tkinter import *
from winreg import *

import requests
from prettytable import PrettyTable


#Generate resource file directory access path
# def resource_path(relative_path):
#     if getattr(sys, 'frozen', False):
#         base_path = sys._MEIPASS
#     else:
#         base_path = os.path.abspath(".")
#     return os.path.join(base_path, relative_path)

# def resource_path(relative_path):
#     if hasattr(sys, '_MEIPASS'):
#         return os.path.join(sys._MEIPASS, relative_path)
#     return os.path.join(os.path.abspath("."), relative_path)


filter_name = 'Stellanebula Project'
# filter_name = ''
BGS = 1
MATS = 0
root = ''
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
with OpenKey(HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders") as key:
    value = QueryValueEx(key, '{4C5C32FF-BB9D-43B0-B5B4-2D72E54EAAA4}')
path = value[0] + '\\Frontier Developments\\Elite Dangerous\\'
# path = value[0] + '\\Frontier Developments\\'

bgs = PrettyTable(['System', 'Faction', 'Influence'])
mats_table = PrettyTable(['Materials', 'Count'])


def last_tick():
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


def date_for_ma(missionid, gmd_faction, x):
    print('date_for_MA')
    mission_found = False
    while x < 7:
        print('In While Schleife')
        Tag2 = str(int(Tag.get()) - x)
        print(str(Tag2).zfill(2))
        Monat2 = Monat.get()
        Jahr2 = Jahr.get()
        Date = str(Jahr2 + Monat2 + str(Tag2).zfill(2))
        filenames = glob.glob(path + "\\Journal." + Date + "*.log")
        for filename in filenames:
            print(filename)
            if get_mission_data(missionid, filename, gmd_faction, mission_found):
                mission_found = True
                return mission_found
        x += 1


def get_mission_data(missionid, journal_file, gmd_faction, mission_found):
    print('get_mission_data')
    if log_var > 1:
        print('get_mission_data ' + journal_file)
    global inf_data, docked
    docked = ''
    inf_data = ''
    MA_ZEILE = 0
    D_ZEILE = 0
    D_system = []
    print(journal_file)
    datei = open(journal_file, 'r', encoding='UTF8')
    D_datei = open(journal_file, 'r', encoding='UTF8')
    for MA_zeile in datei:
        MA_ZEILE += 1
        gmd_mission_id = str(missionid)
        gmd_search_string = 'MissionAccepted'
        if (MA_zeile.find(gmd_search_string)) > -1:
            print('suche nach Mission ID ' + gmd_mission_id)
            if (MA_zeile.find(gmd_mission_id)) > -1:
                mission_found = True
                print('gefunden ' + gmd_mission_id)
                data = json.loads(MA_zeile)
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
                        return docked
                else:
                    print(str(data['Faction']) + ' ' + str(gmd_faction))
                    # print('not Found ' + gmd_mission_id)
                    docked = ''
                    return docked
            else:
                # print('nicht gefunden ' + gmd_mission_id)
                mission_found = False
    if not mission_found:
        print('mission_found false ' + gmd_mission_id)
        # return mission_found


def log_date(timestamp):
    global log_time
    log_year = (timestamp[:4])
    log_month = (timestamp[5:7])
    log_day = (timestamp[8:10])
    log_hour = (timestamp[11:13])
    log_minute = (timestamp[14:16])
    log_time = [log_year, log_month, log_day, log_hour, log_minute]


def extract_data(journal_file, data, ed_faction_list, ed_influence_list, ed_index_of_list):
    print('Odyssey Missions has FactionEffects missing')

    if log_var > 1:
        print('extract_data')
        print(data['MissionID'])
    try:
        for p in data["FactionEffects"]:
            if log_var == 3:
                print(data['timestamp'])
            if p['Faction'] != '':
                if log_var == 3:
                    print('MissionID ' + str(data['MissionID']))
                ed_faction = (p['Faction'])
                missionid = data['MissionID']
                try:
                    if str(data['Faction']) == str(data['TargetFaction']):
                        if log_var == 7:
                            print('Fraktion ist gleich bei Mission ' + str(missionid))
                            print(data)
                        mission_found = False
                        date_for_ma(missionid, ed_faction, 0)
                        # get_mission_data(missionid, journal_file, ed_faction, mission_found)
                        p['Influence'] = [{'SystemAddress': docked, 'Trend': 'UpGood', 'Influence': inf_data}]
                        print(p['Influence'])
                        if log_var == 3:
                            print(p['Influence'])
                except KeyError:
                    print('No TargetFaction in JSON')
                if not p['Influence']:
                    if log_var == 3:
                        print(p['Influence'])
                    mission_found = False
                    date_for_ma(missionid, ed_faction, 0)
                    # get_mission_data(missionid, journal_file, ed_faction, mission_found)
                    if log_var == 3:
                        print('In extraxt data ' + inf_data)
                        print('In extraxt data ' + str(docked))
                        print('In extraxt data ' + str(missionid))
                    if docked:
                        p['Influence'] = [{'SystemAddress': docked, 'Trend': 'UpGood', 'Influence': inf_data}]
                    else:
                        p['Influence'] = [{'SystemAddress': docked, 'Trend': 'UpGood', 'Influence': ''}]
                    if log_var == 3:
                        print(p['Influence'])
                extract_influence(p, ed_faction_list, ed_influence_list, ed_index_of_list)
    except KeyError:
        ed_faction = (data['Faction'])
        missionid = data['MissionID']
        date_for_ma(missionid, ed_faction, 0)
        # get_mission_data(missionid, journal_file, ed_faction, mission_found)
        data['Influence'] = [{'SystemAddress': docked, 'Trend': 'UpGood', 'Influence': inf_data}]
        if log_var == 3:
            print(data['Influence'])
        extract_influence(data, ed_faction_list, ed_influence_list, ed_index_of_list)
        # print(data)

    # ================================ End of extract_data


def extract_influence(data, ei_faction_list, ei_influence_list, ei_index_of_list):
    if log_var > 1:
        print('extract_influence')
    for xx in data['Influence']:
        for i in data["Influence"]:
            if i['Trend'] == 'UpGood':
                if (data['Faction'], xx['SystemAddress']) not in ei_index_of_list:
                    if log_var == 3:
                        print(data['Faction'], xx['SystemAddress'], len(i['Influence']))
                    ei_faction_list.append(data['Faction'])
                    system_list.append(xx['SystemAddress'])
                    ei_influence_list.append(len(i['Influence']))
                    temp = data['Faction'], xx['SystemAddress']
                    ei_index_of_list.append(temp)
                else:
                    temp = data['Faction'], xx['SystemAddress']
                    index = ei_index_of_list.index(temp)
                    ei_influence_list[index] += len(i['Influence'])
            if i['Trend'] == 'DownBad':
                if (data['Faction'], xx['SystemAddress']) not in ei_index_of_list:
                    ei_faction_list.append(data['Faction'])
                    system_list.append(xx['SystemAddress'])
                    ei_influence_list.append(len(i['Influence']) * (-1))
                    temp = data['Faction'], xx['SystemAddress']
                    ei_index_of_list.append(temp)
                else:
                    temp = data['Faction'], xx['SystemAddress']
                    index = ei_index_of_list.index(temp)
                    ei_influence_list[index] += len(i['Influence'] * (-1))


def starsystem():
    if log_var > 1:
        print('starsystem')
    global starsytems_data, SystemAddress_list
    files = glob.glob(path + "\\Journal.*.log")
    filenames = []
    # es werden die letzen 30 Logfiles eingelesen um eine DB der zuletzt besuchten Sternensysteme zu erstellen
    start = ((len(files)) - 180)
    while start < len(files):
        filenames.append(files[start])
        start += 1
    for filename in filenames:
        datei = open(filename, 'r', encoding='UTF8')
        for zeile2 in datei:
            search_string2 = "FSDJump"
            if (zeile2.find(search_string2)) > -1:
                starsytems_data = json.loads(zeile2)
                # print(starsytems_data)
                if starsytems_data['StarSystem'] not in Starsystem_list:
                    Starsystem_list.append(starsytems_data['StarSystem'])
                    SystemAddress_list.append(starsytems_data['SystemAddress'])
        datei.close()
    print(Starsystem_list)
    print(SystemAddress_list)


def einfluss_auslesen(journal_file, ea_system_list, ea_faction_list, ea_influence_list, ea_index_of_list, ea_tick):
    if log_var > 1:
        print('dateien_einlesen')
    tick_hour = hour.get('1.0', '2.0')
    tick_minute = minute.get('1.0', '2.0')
    tick_time[3] = tick_hour[0:2]
    tick_time[4] = tick_minute[0:2]
    if log_var == 5:
        print(tick_time)
    datei = open(journal_file, 'r', encoding='UTF8')
    for zeile in datei:
        search_string = "MissionCompleted"
        if (zeile.find(search_string)) > -1:
            data = json.loads(zeile)
            timestamp = str(data['timestamp'])
            log_date(timestamp)
            if ea_tick is True:
                if str(tick_time[3]) < str(log_time[3]):
                    extract_data(journal_file, data, ea_faction_list, ea_influence_list, ea_index_of_list)
                if (str(tick_time[3]) == str(log_time[3])) and (str(tick_time[4]) < str(log_time[4])):
                    extract_data(journal_file, data, ea_faction_list, ea_influence_list, ea_index_of_list)
            else:
                if str(tick_time[3]) > str(log_time[3]):
                    extract_data(journal_file, data, ea_faction_list, ea_influence_list, ea_index_of_list)
                if (str(tick_time[3]) == str(log_time[3])) and (str(tick_time[4]) > str(log_time[4])):
                    extract_data(journal_file, data, ea_faction_list, ea_influence_list, ea_index_of_list)
    datei.close()
    lauf = 0
    while lauf < len(ea_system_list):
        if ea_system_list[lauf] in SystemAddress_list:
            index = SystemAddress_list.index(ea_system_list[lauf])
            ea_system_list[lauf] = (Starsystem_list[index])
            lauf += 1
        else:
            if ea_system_list:
                lauf += 1
            else:
                ea_system_list[lauf] = 'None'
                lauf += 1
    # =========================================== End of dateien_einlesen()


def ticktrue():
    global tick
    tick = True


def tickfalse():
    global tick
    tick = False


today = date.today()
# print(today)
today = str(today)
Year = (today[2:4])
Month = (today[5:7])
Day = (today[8:10])

last_tick()


def file_names():
    Tag2 = Tag.get()
    Monat2 = Monat.get()
    Jahr2 = Jahr.get()
    Date = str(Jahr2 + Monat2 + Tag2)
    return (Date)


def auswertung():
    if log_var > 1:
        print('auswertung')
    system.delete(.0, END)
    global system_list, faction_list, influence_list, index_of_list, Starsystem_list, SystemAddress_list
    Tag2 = Tag.get()
    Monat2 = Monat.get()
    Jahr2 = Jahr.get()
    Date = str(Jahr2 + Monat2 + Tag2)
    filenames = glob.glob(path + "\\Journal." + Date + "*.log")
    if log_var == 2:
        print(filenames)
    auto_refresh = False
    lauf_r = 0
    if auto_refresh is True:
        auto = len(filenames) - 1
        while lauf_r < auto:
            del filenames[lauf_r]
            lauf_r += 1
    if BGS == 1:
        for filename in filenames:
            einfluss_auslesen(filename, system_list, faction_list, influence_list, index_of_list, tick)
        lauf = 0
        if log_var == 4:
            print(faction_list)
        while lauf < len(faction_list):
            a_filter = Filter.get()
            a_filter = str.lower(a_filter)
            if log_var == 4:
                print('Filter = ' + a_filter)
            if influence_list[lauf] != 0:
                print('')
                # print(type(str(system_list[lauf])))
                # print(str((faction_list[lauf])[0:20]))
                # print(str(influence_list[lauf]))
                if (a_filter in str.lower((faction_list[lauf]))) or (a_filter in str.lower((system_list[lauf]))):
                    system.insert(END, ((str(system_list[lauf]))[0:15]) + '\t \t ' + str((faction_list[lauf])[0:20]) +
                                  '\t \t \t' + str(influence_list[lauf]) + '\n')
                    bgs.add_row([system_list[lauf], faction_list[lauf], influence_list[lauf]])
            lauf += 1
        faction_list = []
        system_list = []
        influence_list = []
        index_of_list = []
    elif MATS == 1:
        for filename in filenames:
            mats_auslesen(filename)
            # system.insert(END, 'MATS')
    if not filenames:
        system.insert(END, 'Keine Daten für den Tag vorhanden')

threading.Thread(target=starsystem).start()
# starsystem()


def autorefresh():
    if log_var > 1:
        print('autorefresh')
    while check_var.get() != 0:
        print('while autorefresh')
        if check_var.get() != 0:
            print(check_var.get())
            time.sleep(60.0)
            refreshing()


def refreshing():
    if log_var > 1:
        print('refreshing')
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
    auswertung()


def threading_auto():
    if log_var > 1:
        print('threading_auto')
    if check_var.get() != 0:
        threading.Thread(target=autorefresh).start()
    else:
        threading.Thread(target=refreshing).start()


def logging():
    global log_var
    log_var += 1
    print(log_var)


def mats_auslesen(journal_file):
    if log_var > 1:
        print('mats_auslesen')
    mats_table.clear_rows()
    # global name_list, count_list
    name_list = []
    count_list = []
    datei = open(journal_file, 'r', encoding='UTF8')
    for zeile in datei:
        search_string = 'MaterialCollected'
        if (zeile.find(search_string)) > -1:
            data = json.loads(zeile)
            try:
                if data['Name_Localised'] not in name_list:
                    name_list.append(str(data['Name_Localised']))
                    count_list.append(data['Count'])
                else:
                    temp = data['Name_Localised']
                    index = name_list.index(temp)
                    count_list[index] += data['Count']
            except KeyError:
                if log_var > 3:
                    print(data['Name'], end=' ')
                    print(data['Count'])
                if data['Name'] not in name_list:
                    name_list.append(str(data['Name']))
                    count_list.append(data['Count'])
                else:
                    temp = data['Name']
                    index = name_list.index(temp)
                    count_list[index] += data['Count']
    lauf = 0
    while lauf < len(name_list):
        if log_var > 3:
            print(name_list, end=' ')
            print(count_list)
        mats_filter = Filter.get()
        mats_filter = str.lower(mats_filter)
        # print(mats_filter)
        if mats_filter in str.lower((name_list[lauf])):
            system.insert(END, str((name_list[lauf] + '\t \t')))
            system.insert(END, count_list[lauf])
            system.insert(END, '\n')
            mats_table.add_row((name_list[lauf], count_list[lauf]))
        lauf += 1

    # ===========================  GUI erstellung  ==============================


def cp_to_clipboard():
    root.clipboard_clear()
    if BGS == 1:
        root.clipboard_append(bgs.get_string(sortby="System"))
    else:
        root.clipboard_append(mats_table.get_string(sortby="Materials"))
    root.update()


def mats():
    global BGS, MATS
    BGS = 0
    MATS = 1
    vortick.config(state=DISABLED)
    nachtick.config(state=DISABLED)
    auswertung()


def bgs_menu():
    global BGS, MATS
    BGS = 1
    MATS = 0
    vortick.config(state=NORMAL)
    nachtick.config(state=NORMAL)
    threading_auto()


def main():
    global system, root, Tag, Monat, Jahr, hour, minute, BGS, MATS, vortick, nachtick, Filter
    root = Tk()
    root.title('Elite Dangerous Data Collector')
    try:
        # img = resource_path("eddc.ico")
        img = ("eddc.ico")
        root.iconbitmap(img)
    except TclError:
        print('Icon not found)')
    root.configure(background='black')
    root.minsize(380, 460)
    root.maxsize(380, 460)
    bg = PhotoImage(file=("SNPX.png"))
    # bg = PhotoImage(file=(resource_path("SNPX.png")))
    # bg2 = PhotoImage(file=(resource_path("Horizon.png")))
    bg2 = PhotoImage(file=("Horizon.png"))

    my_menu = Menu(root)
    root.config(menu=my_menu)

    # file_menu = Menu(my_menu)
    file_menu = Menu(my_menu, tearoff=False)
    my_menu.add_cascade(label="Datei", menu=file_menu)
    file_menu.add_command(label="BGS", command=bgs_menu)
    file_menu.add_command(label="MATS", command=mats)
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
          text="""Der letzte Tick war um:    """, bg='black', fg='white', font=("Helvetica", 12),
          justify=LEFT).grid(column=0, row=0)

    my_tick = Frame(my_frame, bg='black')
    my_tick.grid(column=1, row=0)

    hour = Text(my_tick, height=1, width=2)
    hour.insert(INSERT, (str(t_hour)))
    hour.get(1.0, END)
    hour.delete(3.0)
    hour.grid(column=0, row=0)
    Label(my_tick,
          text=""":""", bg='black', fg='white', font=("Helvetica", 12),
          justify=LEFT).grid(column=2, row=0)
    minute = Text(my_tick, height=1, width=2)
    minute.insert(INSERT, (str(t_minute)))
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
    Filter = Entry(myfolder_grid, width=30, font=("Helvetica", 10))
    print(' HIER KOMMT DAS Dropdown Menu hin')

    Filter.insert(0, filter_name)
    Filter.grid(column=0, row=0)

    folder = Text(myfolder_grid, height=1, width=55, bg='black', fg='white', font=("Helvetica", 8))
    folder.insert(END, path)
    folder.grid(column=0, row=1, pady=5)

    system = Text(root, height=11, width=50, bg='black', fg='white', font=("Helvetica", 10))
    system.pack(padx=20, pady=5)

    version_but = Button(root,
                         text='Version 0.1.0.0',
                         activebackground='#000050',
                         activeforeground='white',
                         bg='black',
                         fg='white',
                         command=logging,
                         font=("Helvetica", 10))
    version_but.place(x=20, y=425)

    clipboard = Button(root,
                       text='Copy to Clipboard',
                       activebackground='#000050',
                       activeforeground='white',
                       bg='black',
                       fg='white',
                       command=cp_to_clipboard,
                       font=("Helvetica", 10))
    clipboard.place(x=150, y=425)

    ok_but = Button(root,
                    # width=4,
                    activebackground='#000050',
                    activeforeground='white',
                    text='OK',
                    bg='black',
                    fg='white',
                    command=threading_auto,
                    font=("Helvetica", 10))
    ok_but.place(x=325, y=425)

    def callback(event):
        threading_auto()

    root.bind('<Return>', callback)

    root.mainloop()


main()
