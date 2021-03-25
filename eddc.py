#Created by MajorK https://github.com/SNP-MajorK/ED-DataCollector

import glob
import json
import os
# import sys
import threading
import time
from datetime import date
from tkinter import *
from winreg import *

import requests
from prettytable import PrettyTable


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

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

bgs = PrettyTable(['System', 'Faction', 'Influence'])


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


def getmissiondata(missionid, journal_file):
    # print(missionid)
    global inf_data
    datei = open(journal_file, 'r', encoding='UTF8')
    for zeile2 in datei:
        search_string2 = str(missionid)
        search_string = 'MissionAccepted'
        if (zeile2.find(search_string)) > -1:
            if (zeile2.find(search_string2)) > -1:
                data = json.loads(zeile2)
                inf_data = (data['Influence'])
                # print(inf_data)


def log_date(date):
    global log_time
    log_year = (date[:4])
    log_month = (date[5:7])
    log_day = (date[8:10])
    log_hour = (date[11:13])
    log_minute = (date[14:16])
    log_time = [log_year, log_month, log_day, log_hour, log_minute]
    # print(log_time)


def extract_data(journal_file, data, faction_list, influence_list, index_of_list):
    for p in data["FactionEffects"]:
        if p['Faction'] != '':
            if log_var > 2:
                print(p['Influence'])
            if not p['Influence']:
                if log_var > 2:
                    print(p['Influence'])
                missionid = data['MissionID']
                getmissiondata(missionid, journal_file)
                if log_var > 4:
                    print(inf_data)
                p['Influence'] = [{'SystemAddress': 1234567891234, 'Trend': 'UpGood', 'Influence': inf_data}]
            for xx in p['Influence']:
                for i in p["Influence"]:
                    if i['Trend'] == 'UpGood':
                        if (p['Faction'], xx['SystemAddress']) not in index_of_list:
                            if log_var > 2:
                                print(p['Faction'], xx['SystemAddress'], len(i['Influence']))
                            faction_list.append(p['Faction'])
                            system_list.append(xx['SystemAddress'])
                            influence_list.append(len(i['Influence']))
                            temp = p['Faction'], xx['SystemAddress']
                            index_of_list.append(temp)
                        else:
                            temp = p['Faction'], xx['SystemAddress']
                            index = index_of_list.index(temp)
                            influence_list[index] += len(i['Influence'])
                    if i['Trend'] == 'DownBad':
                        if (p['Faction'], xx['SystemAddress']) not in index_of_list:
                            faction_list.append(p['Faction'])
                            system_list.append(xx['SystemAddress'])
                            influence_list.append(len(i['Influence']) * (-1))
                            temp = p['Faction'], xx['SystemAddress']
                            index_of_list.append(temp)
                        else:
                            temp = p['Faction'], xx['SystemAddress']
                            index = index_of_list.index(temp)
                            influence_list[index] += len(i['Influence'] * (-1))

    # ================================ End of extract_data


def starsystem():
    global starsytems_data, SystemAddress_list
    filenames = glob.glob(path + "\\Journal.*.log")
    for filename in filenames:
        datei = open(filename, 'r', encoding='UTF8')
        for zeile2 in datei:
            search_string2 = "FSDJump"
            if (zeile2.find(search_string2)) > -1:
                starsytems_data = json.loads(zeile2)
                # print(data2)
                if starsytems_data['StarSystem'] not in Starsystem_list:
                    Starsystem_list.append(starsytems_data['StarSystem'])
                    SystemAddress_list.append(starsytems_data['SystemAddress'])
        datei.close()
    # print(Starsystem_list)
    # print(SystemAddress_list)


def einfluss_auslesen(journal_file, system_list, faction_list, influence_list, index_of_list, tick):
    print('dateien_einlesen')
    tick_hour = hour.get('1.0', '2.0')
    tick_minute = minute.get('1.0', '2.0')
    tick_time[3] = tick_hour[0:2]
    tick_time[4] = tick_minute[0:2]
    if log_var > 1:
        print(tick_time)
    datei = open(journal_file, 'r', encoding='UTF8')
    for zeile in datei:
        search_string = "MissionCompleted"
        if (zeile.find(search_string)) > -1:
            data = json.loads(zeile)
            date = str(data['timestamp'])
            log_date(date)
            if tick is True:
                if str(tick_time[3]) < str(log_time[3]):
                    extract_data(journal_file, data, faction_list, influence_list, index_of_list)
                if (str(tick_time[3]) == str(log_time[3])) and (str(tick_time[4]) < str(log_time[4])):
                    extract_data(journal_file, data, faction_list, influence_list, index_of_list)
            else:
                if str(tick_time[3]) > str(log_time[3]):
                    extract_data(journal_file, data, faction_list, influence_list, index_of_list)
                if (str(tick_time[3]) == str(log_time[3])) and (str(tick_time[4]) > str(log_time[4])):
                    extract_data(journal_file, data, faction_list, influence_list, index_of_list)
    datei.close()
    lauf = 0
    while lauf < len(system_list):
        if system_list[lauf] in SystemAddress_list:
            index = SystemAddress_list.index(system_list[lauf])
            system_list[lauf] = (Starsystem_list[index])
            lauf += 1
        else:
            system_list[lauf] = 'None'
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


def auswertung():
    if log_var > 0:
        print('auswertung')
    system.delete(1.0, END)

    global system_list, faction_list, influence_list, index_of_list, Starsystem_list, SystemAddress_list
    Tag2 = Tag.get()
    Monat2 = Monat.get()
    Jahr2 = Jahr.get()
    Date = str(Jahr2 + Monat2 + Tag2)
    filenames = glob.glob(path + "\\Journal." + Date + "*.log")
    if log_var > 2:
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

            while lauf < len(faction_list):
                system.insert(END, str((system_list[lauf])) + '\t \t ' + str((faction_list[lauf])[0:28]) +
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
    if BGS == 1:
        print(bgs.get_string(sortby="System"))


starsystem()


def autorefresh():
    print('autorefresh')
    while check_var.get() != 0:
        print('while autorefresh')
        if check_var.get() != 0:
            print(check_var.get())
            time.sleep(15.0)
            refreshing()


def refreshing():
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
    if log_var > 0:
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
    print('mats_auslesen')
    global name_list, count_list
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
        system.insert(END, str((name_list[lauf] + '\t \t')))
        system.insert(END, count_list[lauf])
        system.insert(END, '\n')
        lauf += 1

    # ===========================  GUI erstellung  ==============================


def cp_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(bgs.get_string(sortby="System"))
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
    global system, root, Tag, Monat, Jahr, hour, minute, BGS, MATS, vortick, nachtick
    root = Tk()
    root.title('Elite Dangerous Data Collector')
    root.iconbitmap(resource_path('eddc.ico'))
    root.configure(background='black')
    root.minsize(380, 460)
    root.maxsize(380, 460)
    bg = PhotoImage(file=(resource_path("SNPX.png")))
    bg2 = PhotoImage(file=(resource_path("Horizon.png")))

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
    my_bottom_logo.place(x=0, y=80)
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

    folder = Text(myfolder_grid, height=1, width=55, bg='black', fg='white', font=("Helvetica", 8))
    folder.insert(END, path)
    folder.grid(column=0, row=0, pady=10)

    system = Text(root, height=11, width=50, bg='black', fg='white', font=("Helvetica", 10))

    system.pack(padx=20)

    version_but = Button(root,
                         text='Version 0.0.4.1',
                         activebackground='#000050',
                         activeforeground='white',
                         bg='black',
                         fg='white',
                         command=logging,
                         font=("Helvetica", 10))
    version_but.place(x=20, y=415)

    clipboard = Button(root,
                       text='Copy to Clipboard',
                       activebackground='#000050',
                       activeforeground='white',
                       bg='black',
                       fg='white',
                       command=cp_to_clipboard,
                       font=("Helvetica", 10))
    clipboard.place(x=150, y=415)

    ok_but = Button(root,
                    # width=4,
                    activebackground='#000050',
                    activeforeground='white',
                    text='OK',
                    bg='black',
                    fg='white',
                    command=threading_auto,
                    font=("Helvetica", 10))
    ok_but.place(x=325, y=415)

    def callback(event):
        threading_auto()

    root.bind('<Return>', callback)

    root.mainloop()


main()
