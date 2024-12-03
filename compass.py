import json
import math
import os
import sqlite3
import sys
import csv
import customtkinter
import pywinstyles
from tkinter import filedialog
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageDraw, ImageFont
from winreg import *
from sys import platform
from gui_positionen import load_position, save_position

# from pathlib import Path
compas_label, label_one, label_two, label_three, label_zero = '', '', '', '', ''

popup_open = False


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# global log_path

database = resource_path("eddc.db")


# db_file = Path(database)


def read_db():
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
            path = result[0][3]
            com_style = result[0][5]
            com_trans = result[0][6]
            com_back = result[0][7]
            com_text = result[0][8]
            exp_upload = result[0][8]
            exp_user = result[0][8]
        else:
            web_hock_user = ''
            webhook_url = ''
            eddc_user = 'anonym'
            path = ''
            com_style = 'mica'
            com_trans = 0.9
            com_back = 'black'
            com_text = 'white'
            exp_user = 'anonym'

        return webhook_url, web_hock_user, eddc_user, path, com_style, com_trans, com_back, com_text


webhook_url, web_hock_user, eddc_user, log_path, com_style, com_trans, com_back, com_text = read_db()

if not log_path:
    # Set Program Path Data to random used Windows temp folder.
    with OpenKey(HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders") as key:
        value = QueryValueEx(key, '{4C5C32FF-BB9D-43B0-B5B4-2D72E54EAAA4}')
    log_path = value[0] + '\\Frontier Developments\\Elite Dangerous\\'


def import_csv_to_sqlite(csv_file):
    # Verbindung zur SQLite-Datenbank herstellen (wird erstellt, falls nicht vorhanden)
    connection = sqlite3.connect(database)

    try:
        cursor = connection.cursor()
        # CSV-Datei öffnen und lesen
        with open(csv_file, newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)  # Überspringe die Header-Zeile, falls vorhanden

            # Daten aus CSV in die Datenbank einfügen
            insert_query = """
            INSERT INTO compass (body_name, Waypoint, latitude, longitude, reached)
            VALUES (?, ?, ?, ?, ?)
            """
            for row in csvreader:
                cursor.execute(insert_query, row)

        # Änderungen in der Datenbank speichern
        connection.commit()

    except Exception as e:
        print(f"Fehler: {e}")
    finally:
        connection.close()


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def get_status_data():
    file = log_path + "\\status.json"
    with open(file, 'r', encoding='UTF8') as datei:
        try:
            data = json.load(datei)
        except:
            latitude, longitude, altitude, radius, body_name, reached = ' ', ' ', 0, ' ', ' ', 0
            return latitude, longitude, altitude, radius, body_name, reached
        timestamp = data.get('timestamp')
        latitude = data.get('Latitude')
        longitude = data.get('Longitude')
        altitude = data.get('Altitude')
        radius = data.get('PlanetRadius')
        if radius:
            radius = round(int(data.get('PlanetRadius')) / 1000)
        body_name = data.get('BodyName')
        reached = 0
        if not body_name:
            latitude, longitude, altitude, radius, body_name, reached = ' ', ' ', 0, ' ', ' ', 0
        return latitude, longitude, altitude, radius, body_name, reached, timestamp


def haversine_distance(lat1, lon1, lat2, lon2, radius):
    # Umrechnung der Breiten- und Längengrade von Grad in Radian
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    # Haversine-Formel
    d_lat = lat2 - lat1
    d_lon = lon2 - lon1
    a = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    # Entfernung auf der Erdoberfläche
    distance = radius * c
    return distance


def get_destination_coordination(body_name):
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


def berechne_sinkflug(radius, lat1, lon1, lat2, lon2, hoehe_start, hoehe_ziel):
    # Erdradius in Kilometern

    # Umwandlung von Grad in Radiant
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Unterschiede in den Koordinaten
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    # Haversine-Formel zur Berechnung der horizontalen Entfernung
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distanz = radius * c * 1000  # Distanz in Metern

    # Höhendifferenz
    delta_h = hoehe_start - hoehe_ziel

    # Berechnung des Anflugwinkels (in Grad)
    anflugwinkel = math.degrees(math.atan(delta_h / distanz))
    anflugwinkel = round(anflugwinkel, 2) * (-1)
    return anflugwinkel


def calculate_course_from_json():
    # Daten aus der status.json
    latitude, longitude, altitude, radius, body_name, reached, s_time = get_status_data()

    if body_name == ' ':
        return

    # Ziehe aus der DB die Breiten und Längengrade, welche noch nicht erreicht sind, mit der kleinsten WP Zahl
    dest_latitude, dest_longitude, waypoint = get_destination_coordination(body_name)

    if dest_latitude == 0 and dest_longitude == 0 and waypoint == 0:
        return 0, 0, 0, 0

    if dest_latitude == 0 and dest_longitude == 0 and waypoint == 0:
        text = f'''Du bist alle Wegpunkte abgeflogen'''
        # return text
    # Berechne den Kurs zum Ziel
    new_course = round(calculate_course(latitude, longitude, dest_latitude, dest_longitude), 2)
    # Berechne die Entfernung zwischen der aktuellen Position und dem Ziel
    distance = round(haversine_distance(latitude, longitude, dest_latitude, dest_longitude, radius), 2)
    if distance < 5:
        # text = f'''Du bist alle Wegpunkte abgeflogen'''
        save_coords(body_name, latitude, waypoint, longitude, 1)
        # return text

    # Annahme: Zielhöhe ist immer 2
    target_altitude = 2000

    # Berechne den Höhenunterschied zwischen aktueller Höhe und Zielhöhe
    altitude_difference = altitude - target_altitude

    # Berechne den Anflugwinkel (in Grad)
    # Verwende Arkustangens: anflugwinkel = atan(altitude_difference / horizontale_distanz)
    if distance != 0:
        approach_angle = berechne_sinkflug(radius, latitude, longitude,
                                           dest_latitude, dest_longitude, altitude, target_altitude)
    else:
        approach_angle = 0  # Falls die Distanz 0 ist (was eigentlich nicht vorkommen sollte)

    # text = f'''Dein neuer Kurs ist der Wegpunkt {waypoint} auf {new_course}° \n
    # Und dein Ziel ist {distance}km entfernt \n Der Anflugwinkel beträgt {round(approach_angle, 2)}'''

    return waypoint, new_course, round(distance), round(approach_angle, 2)
    # create_popup(text, 5000)
    # return text


def close_popup(popup):
    popup.destroy()


def refresh_popup(compas_label):
    new_text = calculate_course_from_json()
    # compas_label.configure(text=new_text)
    if new_text:
        wp = 'WP ' + str(new_text[0])
        grad = str(new_text[1]) + '°'
        kilometer = str(new_text[2]) + ' km'
        print(kilometer)
        # if new_text[3] > -45:
        winkel = str(new_text[3])
        label_three.configure(text=winkel)
        # else:
        #     label_three.configure(text=' ')

        label_zero.configure(text=wp)
        label_one.configure(text=kilometer)
        label_two.configure(text=grad)

    compas_label.after(500, lambda: refresh_popup(compas_label))


def next_wp():
    latitude, longitude, altitude, radius, body_name, reached, s_time = get_status_data()

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        sql = f'''select Waypoint from compass where body_name = "{body_name}" and reached = 0 order by Waypoint ASC'''
        cursor.execute(sql)
        waypoint = cursor.fetchone()
        new_sql = f'''UPDATE compass set reached = 1 where body_name = "{body_name}" and Waypoint = {waypoint[0]}'''
        cursor.execute(new_sql)
        connection.commit()


def open_setting():
    settings = customtkinter.CTkToplevel()
    settings_open = True
    # print(com_style, com_trans)
    pywinstyles.apply_style(settings, com_style)
    settings.title("Kompass Einstellungen")

    settings.minsize(420, 320)
    settings.maxsize(420, 350)
    settings.after(100, lambda: settings.focus_force())
    settings.config(background='black')

    top_blank = customtkinter.CTkFrame(master=settings, bg_color='black', fg_color='black')
    top_blank.pack(fill=X)

    headline = customtkinter.CTkLabel(master=top_blank, text='Kompass Import und Export', text_color='white',
                                      font=("Helvetica", 18))
    headline.grid(column=0, row=0, pady=5, padx=20)

    try:
        img = resource_path("eddc.ico")
        settings.iconbitmap(img)
    except:
        pass

    def select_csv_file():
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            csv_path_entry.delete(0, END)
            csv_path_entry.insert(0, file_path)

    # Label und Eingabefeld für CSV-Pfad
    csv_label = customtkinter.CTkLabel(master=top_blank, text='CSV-Dateipfad:', text_color='white')
    csv_label.grid(column=0, row=1, pady=5, padx=5)

    csv_path_entry = customtkinter.CTkEntry(master=top_blank, width=300)
    csv_path_entry.grid(column=0, row=2, pady=5, padx=20)

    choice_label = customtkinter.CTkLabel(master=top_blank, text='', )
    choice_label.grid(column=0, row=3, pady=5, padx=20)

    browse_button = customtkinter.CTkButton(master=choice_label, text="CSV auswählen", command=select_csv_file)
    browse_button.grid(column=0, row=3, pady=5, padx=20)

    event_label = customtkinter.CTkLabel(master=top_blank, text='')
    event_label.grid(column=0, row=6, pady=5, padx=20)

    def update_label():
        # Vor der Aktualisierung den Text leeren
        event_label.config(text="")  # Text explizit löschen
        event_label.config(text="Kurz")  # Jetzt kürzeren Text einfügen

    # Button zum Importieren der CSV-Daten in die Datenbank
    def import_csv_to_database():
        csv_file = csv_path_entry.get()
        blank_label = customtkinter.CTkLabel(master=top_blank, text='')
        blank_label.grid(column=0, row=6, pady=5, padx=20)
        if csv_file:
            import_csv_to_sqlite(csv_file)
            event_label.configure(text='Import erfolgreich!', text_color='green')
            # success_label = customtkinter.CTkLabel(master=top_blank, text='Import erfolgreich!', text_color='green')
            # success_label.grid(column=0, row=6, pady=5, padx=20)
        else:
            event_label.configure(text='Bitte CSV-Datei auswählen!', text_color='red')
            # error_label = customtkinter.CTkLabel(master=top_blank, text='Bitte CSV-Datei auswählen!',
            #                                      text_color='red')
            # error_label.grid(column=0, row=6, pady=5, padx=20)

    import_button = customtkinter.CTkButton(master=choice_label, text="importieren", command=import_csv_to_database)
    import_button.grid(column=1, row=3, pady=5, padx=20)

    # Dropdown für Export
    export_label = customtkinter.CTkLabel(master=top_blank, text='Export nach Body Name:', text_color='white')
    export_label.grid(column=0, row=4, pady=5, padx=20)

    # Dropdown-Menü für Body Name-Auswahl
    def get_body_names():
        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT body_name FROM compass")
        body_names = [row[0] for row in cursor.fetchall()]
        connection.close()
        return body_names

    body_name_var = StringVar()
    body_names = get_body_names()

    export_label = customtkinter.CTkLabel(master=top_blank, text='', )
    export_label.grid(column=0, row=5, pady=5, padx=20)

    body_name_dropdown = customtkinter.CTkOptionMenu(master=export_label, variable=body_name_var, values=body_names)
    body_name_dropdown.grid(column=0, row=0, pady=5, padx=20)

    # Button zum Exportieren der gefilterten Daten
    def export_filtered_csv():
        selected_body_name = body_name_var.get()
        blank_label = customtkinter.CTkLabel(master=top_blank, text='')
        blank_label.grid(column=0, row=6, pady=5, padx=20)
        if selected_body_name:

            export_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if export_file:
                export_csv_by_body_name(export_file, selected_body_name)
                event_label.configure(text='Export erfolgreich!', text_color='green')
                # export_success_label = customtkinter.CTkLabel(master=top_blank, text='Export erfolgreich!',
                #                                               text_color='green')
                # export_success_label.grid(column=0, row=6, pady=5, padx=20)
        else:
            event_label.configure(text='Bitte einen Body Name auswählen!', text_color='red')
            # export_error_label = customtkinter.CTkLabel(master=top_blank, text='Bitte einen Body Name auswählen!',
            #                                             text_color='red')
            # export_error_label.grid(column=0, row=6, pady=5, padx=20)

    export_button = customtkinter.CTkButton(master=export_label, text="Exportieren", command=export_filtered_csv)
    export_button.grid(column=1, row=0, pady=5, padx=20)


# Funktion zum Exportieren der Daten nach body_name in eine CSV
def export_csv_by_body_name(export_file, body_name):
    connection = sqlite3.connect(database)
    try:
        cursor = connection.cursor()
        query = "SELECT * FROM compass WHERE body_name = ?"
        cursor.execute(query, (body_name,))
        rows = cursor.fetchall()

        # CSV-Datei erstellen und Daten exportieren
        with open(export_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['body_name', 'Waypoint', 'latitude', 'longitude', 'reached'])  # Header schreiben
            writer.writerows(rows)

    except Exception as e:
        print(f"Fehler: {e}")
    finally:
        connection.close()


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

    webhook_url, web_hock_user, eddc_user, log_path, com_style, com_trans, com_back, com_text = read_db()

    popup = customtkinter.CTkToplevel()
    popup_open = True

    pywinstyles.apply_style(popup, com_style)
    popup.wm_attributes('-alpha', com_trans)
    # Einstellen der Transparenz (0.0 vollständig transparent, 1.0 undurchsichtig)
    popup.attributes('-topmost', True)
    popup.title("EDDC Kompass")
    popup_width = 400
    popup_height = 129
    popup.minsize(popup_width, popup_height)
    popup.maxsize(popup_width, popup_height)
    load_position(popup, 3, 400, 150)

    try:
        img = resource_path("eddc.ico")
        popup.iconbitmap(img)
    except:
        pass

    if platform.startswith("win"):
        popup.after(200, lambda: popup.iconbitmap(img))

    global compas_label, label_one, label_two, label_three, label_zero
    pic = 'images/NRNF/kompasslayout.png'
    bg = Image.open(pic)
    bg_treeview = customtkinter.CTkImage(dark_image=bg, size=(popup_width, popup_height))
    background_label = customtkinter.CTkLabel(popup, bg_color='black', image=bg_treeview, text='')
    background_label.pack()
    # print(message)

    def on_closing():
        global popup_open
        popup_open = False
        print('popup closing')
        popup.destroy()

    if not message:
        popup.after(1000, lambda: refresh_popup(compas_label))
    else:
        wp = 'WP ' + str(message[0])
        grad = str(message[1]) + '°'
        kilometer = str(message[2]) + ' km'
        winkel = str(message[3])

        label_zero = customtkinter.CTkLabel(master=popup, text=wp, text_color='white',
                                            fg_color='black', font=("Helvetica", 18))
        label_zero.place(x=40, y=5)

        label_one = customtkinter.CTkLabel(master=popup, text=kilometer, text_color='white',
                                           fg_color='black', font=("Helvetica", 18))
        label_one.place(x=30, y=42)

        label_two = customtkinter.CTkLabel(master=popup, text=grad, text_color='white',
                                           fg_color='black', font=("Helvetica", 18))
        label_two.place(x=170, y=100)

        label_three = customtkinter.CTkLabel(master=popup, text=winkel, text_color='white',
                                             fg_color='black', font=("Helvetica", 18))
        label_three.place(x=330, y=35)

    compas_label = customtkinter.CTkLabel(popup, text=message, font=("Arial Bold", 16),
                                          fg_color=com_back, text_color=com_text)

    save_but = customtkinter.CTkButton(master=popup, width=50, height=10, text='Next',
                                       command=next_wp, font=("Helvetica", 14))
    save_but.place(x=336, y=100)

    close_but = customtkinter.CTkButton(master=popup, width=50, height=10, text='Close',
                                        command=on_closing, font=("Helvetica", 14))
    close_but.place(x=15, y=100)

    popup.bind("<Configure>", lambda event: save_position(popup, 3))

    # Schließe das Popup nach 'timeout' Millisekunden
    popup.after(1000, lambda: refresh_popup(compas_label))

    def on_closing():
        global popup_open
        popup_open = False
        print('popup closing')
        save_position(popup, 3)
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
    latitude, longitude, altitude, radius, body_name, reached, s_time = get_status_data()
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

    c_style = ttk.Style(compass_gui)
    c_style.theme_use('default')
    c_style.configure('Treeview',
                      background="black",
                      foreground="white",
                      rowheight=18,
                      fieldbackground="black"
                      )
    c_style.configure('my.DateEntry',
                      fieldbackground='black',
                      background='black',
                      foreground='white',
                      arrowcolor='white'
                      )
    c_style.map('Treeview', background=[('selected', "#f07b05")])
    compass_gui.after(200, lambda: compass_gui.focus_force())

    load_position(compass_gui, 4, 735, 320)

    tree_compass_frame = Frame(compass_gui, bg='black')
    tree_compass_frame.pack(pady=5)

    tree_compass_scroll = Scrollbar(tree_compass_frame)
    tree_compass_scroll.pack(side=RIGHT, fill=Y)
    compass_tree = ttk.Treeview(tree_compass_frame, yscrollcommand=tree_compass_scroll.set,
                                selectmode="extended", height=10)
    tree_compass_scroll.config(command=compass_tree.yview)

    compass_tree['columns'] = ('Waypoint', 'Body', 'Breitengrad', 'längengrad', 'Erreicht')

    compass_tree.column("#0", width=2, stretch=NO)
    compass_tree.heading("#0", text="", anchor=W)

    compass_tree.column("Waypoint", anchor=W, width=60)
    compass_tree.heading("Waypoint", text="Waypoint", anchor=W)

    compass_tree.column("Body", anchor=W, width=200)
    compass_tree.heading("Body", text="Body", anchor=W)

    compass_tree.column("Breitengrad", anchor=W, width=130)
    compass_tree.heading("Breitengrad", text="Breitengrad", anchor=W)

    compass_tree.column("längengrad", anchor=W, width=130)
    compass_tree.heading("längengrad", text="Längengrad", anchor=W)

    compass_tree.column("Erreicht", anchor=W, width=50)
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
                                          text="Save",
                                          command=lambda: save(entry_waypoint.get(),
                                                               entry_body.get(),
                                                               entry_latitude.get(),
                                                               entry_longitude.get(),
                                                               check_reached.get()
                                                               )
                                          )
    button_save.pack(side=LEFT, padx=10)

    button_refresh = customtkinter.CTkButton(master=second_row, text="Refresh", command=lambda: refresh_entry())
    button_refresh.pack(side=LEFT, padx=10)

    button_delete = customtkinter.CTkButton(master=second_row, text="Delete", command=lambda: delete_entry())
    button_delete.pack(side=LEFT, padx=10)

    button_show = customtkinter.CTkButton(master=second_row, text="Overlay", command=lambda: open_compas())
    button_show.pack(side=LEFT, padx=10)

    button_setting = customtkinter.CTkButton(master=second_row, text="Im & Export", command=lambda: open_setting())
    button_setting.pack(side=LEFT, padx=10)

    def save(waypoint, body_name, latitude, longitude, reached):

        save_coords(body_name=body_name, waypoint=waypoint, latitude=latitude, longitude=longitude, reached=reached)
        refresh_entry()
        # refresh_table()

    def refresh_entry():
        latitude, longitude, altitude, radius, body_name, reached, s_time = get_status_data()
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

    def refresh_table():
        latitude, longitude, altitude, radius, body_name, reached, s_time = get_status_data()
        rowdata = cord_data(body_name)
        compass_tree.delete(*compass_tree.get_children())
        add_entries(rowdata)

    def on_closing():
        save_position(compass_gui, 4)
        compass_gui.destroy()

    compass_gui.protocol("WM_DELETE_WINDOW", on_closing)
    compass_tree.bind("<ButtonRelease-1>", selected_record)

    save_position(compass_gui, 4)

    compass_gui.after(1500, refresh_entry)
    compass_gui.mainloop()


def open_compas():
    text = calculate_course_from_json()
    # thread_rce = threading.Thread(target=create_popup, args=((text, 5000)))
    # thread_rce.start()
    create_popup(text, 5000)
