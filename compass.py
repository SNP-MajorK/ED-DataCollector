import json
import math
import os
import sqlite3
import sys
from pathlib import Path
import customtkinter
import pywinstyles
from tkinter import *
from tkinter import ttk
from winreg import *
from sys import platform
global popup_open
popup_open = False

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

global path
# path = ''

database = resource_path("eddc.db")
db_file = Path(database)

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
    path = value[0] + '\\Frontier Developments\\Elite Dangerous\\'


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def get_status_data():
    file = path + "\\status.json"
    with open(file, 'r', encoding='UTF8') as datei:
        try:
            data = json.load(datei)
        except:
            latitude, longitude, radius, body_name, reached = ' ', ' ', ' ', ' ', ' '
            return latitude, longitude, radius, body_name, reached
        latitude = data.get('Latitude')
        longitude = data.get('Longitude')
        radius = data.get('PlanetRadius')
        if radius:
            radius = int(data.get('PlanetRadius')) / 1000
        body_name = data.get('BodyName')
        reached = 0
        if not body_name:
            latitude, longitude, radius, body_name, reached = ' ', ' ', ' ', ' ', ' '
        return latitude, longitude, radius, body_name, reached


def haversine_distance(lat1, lon1, lat2, lon2, radius):
    # Umrechung der Breiten- und Längengrade von Grad in Radian
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    # Haversine-Formel
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    # Entfernung auf der Erdoberfläche
    distance = radius * c
    return distance


def get_destination_coords(body_name):
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        sql = f'''select latitude, longitude, waypoint from compass where body_name = "{body_name}" 
        and reached = 0 order by Waypoint ASC'''
        cursor.execute(sql)
        result = cursor.fetchone()
        if result:
            return result[0], result[1], result[2]
        else:
            return 0, 0, 0


def calculate_course_from_json():
    # Daten aus der status.json
    latitude, longitude, radius, body_name, reached = get_status_data()

    # Ziehe aus der DB die Ziel Breiten und Längengrade welche noch nicht erreicht sind mit der kleinsten WP Zahl
    dest_latitude, dest_longitude, waypoint = get_destination_coords(body_name)

    if dest_latitude == 0 and dest_longitude ==0 and waypoint == 0:
        text = f'''Du bist alle Wegpunkte abgeflogen'''
        return text
    # Berechne den Kurs zum Ziel
    new_course = round(calculate_course(latitude, longitude, dest_latitude, dest_longitude), 2)
    # Berechne die Entfernung zwischen der aktuellen Position und dem Ziel
    distance = round(haversine_distance(latitude, longitude, dest_latitude, dest_longitude, radius), 2)
    text = f'''Dein neuer Kurs ist der Wegpunkt {waypoint} auf {new_course}° \n Und dein Ziel ist {distance}km entfernt '''
    # create_popup(text, 5000)
    return text


def close_popup(popup):
    popup.destroy()


def refresh_popup(compas_label):
    new_text = calculate_course_from_json()
    compas_label.configure(text=new_text)
    compas_label.after(500, lambda: refresh_popup(compas_label))


def next_wp():
    latitude, longitude, radius, body_name, reached = get_status_data()

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        sql = f'''select Waypoint from compass where body_name = "{body_name}" and reached = 0 order by Waypoint ASC'''
        cursor.execute(sql)
        waypoint = cursor.fetchone()
        new_sql = f'''UPDATE compass set reached = 1 where body_name = "{body_name}" and Waypoint = {waypoint[0]}'''
        cursor.execute(new_sql)
        connection.commit()


def create_popup(message, timeout=10000):

    global popup
    global popup_open

    if popup_open:
        popup.after(5000, lambda: refresh_popup(compas_label))

        def on_closing():
            global popup_open
            popup_open = False
            print('popup closing')
            popup.destroy()
        popup.protocol("WM_DELETE_WINDOW", on_closing)
        return

    popup = customtkinter.CTkToplevel()
    popup_open = True
    pywinstyles.apply_style(popup, 'acrylic')
    popup.wm_attributes('-alpha', 0.7)  # Einstellen der Transparenz (0.0 vollständig transparent, 1.0 undurchsichtig)
    popup.attributes('-topmost', True)
    popup.title("EDDC Kompass")

    popup.minsize(400, 150)
    popup.maxsize(400, 150)

    def load_position():  # load Window Position if stored else load default
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT x, y FROM eddc_positions where id = 3")
            position = cursor.fetchone()
            if position:
                x_win = str(position[0])
                y_win = str(position[1])
                popup.geometry(f'400x150+{x_win}+{y_win}')
            else:
                popup.geometry(f'400x150+130+130')
                cursor.execute("INSERT INTO eddc_positions (x, y) VALUES (130, 130)")
                cursor.execute("INSERT INTO eddc_positions (x, y) VALUES (130, 130)")
                cursor.execute("INSERT INTO eddc_positions (x, y) VALUES (130, 130)")
                connection.commit()

    load_position()

    try:
        img = resource_path("eddc.ico")
        popup.iconbitmap(img)
    except:
        pass

    if platform.startswith("win"):
        popup.after(200, lambda: popup.iconbitmap(img))

    global compas_label
    compas_label = customtkinter.CTkLabel(popup, text=message, font=("Arial Bold", 16), fg_color='black')
    compas_label.pack(pady=10)

    save_but = customtkinter.CTkButton(master=popup, text='Next',
                                       command=next_wp, font=("Helvetica", 14))
    save_but.pack(pady=10)

    def save_position():
        position = {
            "x": popup.winfo_x(),
            "y": popup.winfo_y()
        }
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE eddc_positions SET x = ? , y = ? where id = 3",
                           (position["x"], position["y"]))
            connection.commit()

    popup.bind("<Configure>", lambda event: save_position())

    # Schließe das Popup nach 'timeout' Millisekunden
    popup.after(5000, lambda: refresh_popup(compas_label))

    def on_closing():
        global popup_open
        popup_open = False
        print('popup closing')
        save_position()
        popup.destroy()

    popup.protocol("WM_DELETE_WINDOW", on_closing)

    popup.mainloop()


def calculate_course(latitude, longitude, target_latitude, target_longitude):

    # Berechne die Differenzen zwischen den Ziel- und aktuellen Breiten- und Längengraden
    delta_longitude = target_longitude - longitude
    delta_latitude = target_latitude - latitude

    # Verwende die Haversine-Formel, um den Kurs zu berechnen
    radians_latitude1 = math.radians(latitude)
    radians_latitude2 = math.radians(target_latitude)
    radians_delta_longitude = math.radians(delta_longitude)

    y = math.sin(radians_delta_longitude)
    x = math.cos(radians_latitude1) * math.sin(radians_latitude2) - math.sin(radians_latitude1) * math.cos(
        radians_latitude2) * math.cos(radians_delta_longitude)
    initial_course = math.degrees(math.atan2(y, x))

    return (initial_course + 360) % 360


def get_waypoint(body_name):
    waypoint = []
    if body_name:
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            sql = f'''select * from compass where body_name = "{body_name}" order by Waypoint DESC'''
            cursor.execute(sql)
            waypoint = cursor.fetchone()
    if waypoint != [] and waypoint is not None:
        new_waypoint = int(waypoint[1]) + 1
    else:
        new_waypoint = 1
    return new_waypoint


def save_coords(body_name, latitude, waypoint, longitude, reached):

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        select_sql = f'''select * from compass where body_name = "{body_name}" 
                                                and Waypoint = {waypoint}'''
        result = cursor.execute(select_sql).fetchall()
        if result:
            sql = f'''UPDATE compass SET body_name = "{body_name}" ,latitude = {latitude},
            longitude = {longitude}, reached = {reached} where Waypoint = {waypoint}'''
        else:
            sql = f'''INSERT INTO compass VALUES ("{body_name}", {waypoint}, {latitude}, {longitude}, {reached})'''
        cursor.execute(sql)
        connection.commit()


def cord_data(body_name):
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        sql = f'''select waypoint, body_name, latitude, longitude, reached 
                from compass where body_name = "{body_name}" order by Waypoint ASC'''
        cursor.execute(sql)
        waypoint = cursor.fetchall()
        return waypoint


def compass_gui():
    latitude, longitude, radius, body_name, reached = get_status_data()
    waypoint = str(get_waypoint(body_name))
    compass_gui = customtkinter.CTkToplevel()
    compass_gui.title('EDDC COMPASS')
    compass_gui.config(background='black')
    try:
        img = resource_path("eddc.ico")
        compass_gui.iconbitmap(img)
    except:
        pass
    # Because CTkToplevel currently is bugged on windows
    # and doesn't check if a user specified icon is set
    # we need to set the icon again after 200ms
    if platform.startswith("win"):
        compass_gui.after(200, lambda: compass_gui.iconbitmap(img))
    if body_name:
        rowdata = cord_data(body_name)
    else:
        rowdata = []

    style = ttk.Style(compass_gui)
    style.theme_use('default')
    style.configure('Treeview',
                    background="black",
                    foreground="white",
                    rowheight=18,
                    fieldbackground="black"
                    )
    style.map('Treeview', background=[('selected', "#f07b05")])

    tree_compass_frame = Frame(compass_gui, bg='black')
    tree_compass_frame.pack(pady=5)

    tree_compass_scroll = Scrollbar(tree_compass_frame)
    tree_compass_scroll.pack(side=RIGHT, fill=Y)
    compass_tree = ttk.Treeview(tree_compass_frame, yscrollcommand=tree_compass_scroll.set,
                              selectmode="extended", height=10)
    tree_compass_scroll.config(command=compass_tree.yview)

    compass_tree['columns'] = ('Waypoint', 'Body', 'Breitengrad', 'längengrad', 'Erreicht')

    compass_tree.column("#0", width=15, stretch=NO)
    compass_tree.heading("#0", text="", anchor=W)

    compass_tree.column("Waypoint", anchor=W, width=60)
    compass_tree.heading("Waypoint", text="Waypoint", anchor=W)

    compass_tree.column("Body", anchor=W, width=200)
    compass_tree.heading("Body", text="Body", anchor=W)

    compass_tree.column("Breitengrad", anchor=W, width=150)
    compass_tree.heading("Breitengrad", text="Breitengrad", anchor=W)

    compass_tree.column("längengrad", anchor=W, width=150)
    compass_tree.heading("längengrad", text="längengrad", anchor=W)

    compass_tree.column("Erreicht", anchor=W, width=30)
    compass_tree.heading("Erreicht", text="Erreicht", anchor=W)


    def add_entries(entries):
        for idx, entry in enumerate(entries):
            # print(idx, entry)
            if idx % 2 == 1:
                row_color = ('odd',)
            else:
                row_color = ('even',)
            compass_tree.insert('', 'end', values=entry, tags=row_color)
    #
    compass_tree.tag_configure('odd', background='#569fe3', foreground='white', font=('Arial', 9, 'bold'))
    compass_tree.tag_configure('even', background='white', foreground='black', font=('Arial', 9, 'bold'))
    add_entries(rowdata)
    compass_tree.pack()
    first_row = customtkinter.CTkFrame(master=compass_gui, fg_color='black', bg_color='black')
    first_row.pack(pady=5)
    second_row = customtkinter.CTkFrame(master=compass_gui, fg_color='black', bg_color='black')
    second_row.pack(pady=5)

    label_waypoint = customtkinter.CTkLabel(first_row, text="WP : ", font=("Helvetica", 11))
    label_waypoint.pack(side=LEFT, padx=5)
    entry_waypoint = customtkinter.CTkEntry(first_row, width=3, font=("Helvetica", 11))
    entry_waypoint.insert(0, waypoint)
    entry_waypoint.pack(side=LEFT, padx=5)

    label_body = customtkinter.CTkLabel(first_row, text="BodyName: ", font=("Helvetica", 11))
    label_body.pack(side=LEFT, padx=5)
    entry_body = customtkinter.CTkEntry(first_row, width=150, font=("Helvetica", 11))
    entry_body.insert(0, body_name)
    entry_body.pack(side=LEFT, padx=5)

    label_latitude = customtkinter.CTkLabel(first_row, text="Breitengrad: ", font=("Helvetica", 11))
    label_latitude.pack(side=LEFT, padx=5)
    entry_latitude = customtkinter.CTkEntry(first_row, width=70, font=("Helvetica", 11))
    entry_latitude.insert(0, latitude)
    entry_latitude.pack(side=LEFT, padx=5)

    label_longitude = customtkinter.CTkLabel(first_row, text="Längengrad: ", font=("Helvetica", 11))
    label_longitude.pack(side=LEFT, padx=5)
    entry_longitude = customtkinter.CTkEntry(first_row, width=70, font=("Helvetica", 11))
    entry_longitude.insert(0, longitude)
    entry_longitude.pack(side=LEFT, padx=10)

    check_reached = IntVar()

    check_but_reached = customtkinter.CTkCheckBox(master=first_row,
                                       text="Erreicht   ",
                                       variable=check_reached,
                                       onvalue=1,
                                       offvalue=0)
    check_but_reached.pack(side=LEFT, padx=10)

    button_save = customtkinter.CTkButton(master=second_row,
                            text="SAVE",
                            command=lambda: save(entry_waypoint.get(),
                                                 entry_body.get(),
                                                 entry_latitude.get(),
                                                 entry_longitude.get(),
                                                 check_reached.get()
                                                 )
                            )
    button_save.pack(side=LEFT, padx=10)

    button_refresh = customtkinter.CTkButton(master=second_row,
                               text="Refresh",
                               command=lambda:refresh_entry())
    button_refresh.pack(side=LEFT, padx=10)

    button_delete = customtkinter.CTkButton(master=second_row,
                               text="Delete",
                               command=lambda:delete_entry())
    button_delete.pack(side=LEFT, padx=10)

    button_show = customtkinter.CTkButton(master=second_row,
                               text="Overlay",
                               command=lambda:open_compas())
    button_show.pack(side=LEFT, padx=10)

    def save(waypoint, bodyname, latitude, longitude, reached):

        save_coords(body_name=bodyname, waypoint=waypoint, latitude=latitude,
                    longitude=longitude, reached=reached)
        refresh_entry()
        # refresh_table()

    def refresh_entry():
        latitude, longitude, radius, body_name, reached = get_status_data()
        waypoint = get_waypoint(body_name)
        refresh_labels(latitude, longitude, body_name, waypoint, reached)
        refresh_table()

    def delete_entry():
        waypoint = entry_waypoint.get(),
        body_name = entry_body.get(),
        latitude = entry_latitude.get(),
        longitude = entry_longitude.get(),
        reached = check_reached.get()

        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            del_sql = f'''DELETE from compass where body_name = "{body_name[0]}" and Waypoint = {waypoint[0]} and 
                                    latitude = {latitude[0]} and longitude = {longitude[0]} and reached = {reached}'''

            cursor.execute(del_sql)
            connection.commit()
            refresh_table()


    def refresh_labels(latitude, longitude, body_name, waypoint, reached):
        entry_waypoint.delete(0, END)
        entry_waypoint.insert(0, waypoint)

        entry_body.delete(0, END)
        entry_body.insert(0, body_name)
        entry_latitude.delete(0, END)
        entry_latitude.insert(0, latitude)
        entry_longitude.delete(0, END)
        entry_longitude.insert(0, longitude)
        if reached == '1':
            check_but_reached.select()
        elif reached == '0':
            check_but_reached.deselect()


    def selected_record(e):  # Shows Picture of selected Item and store Data in Clipboard

        selected_tree = compass_tree.focus()
        values = compass_tree.item(selected_tree, 'values')
        print('|', values, '|')
        if values:
            refresh_labels(values[2], values[3], values[1], values[0], values[4])

    #
    def refresh_table():
        latitude, longitude, radius, body_name, reached = get_status_data()
        rowdata = cord_data(body_name)
        compass_tree.delete(*compass_tree.get_children())
        add_entries(rowdata)


    compass_tree.bind("<ButtonRelease-1>", selected_record)

    compass_gui.after(1500, refresh_entry)
    compass_gui.mainloop()

def open_compas():
    text = calculate_course_from_json()
    # thread_rce = threading.Thread(target=create_popup, args=((text, 5000)))
    # thread_rce.start()
    create_popup(text, 5000)
