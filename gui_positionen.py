import sqlite3
import sys
import os
from pathlib import Path

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

global path

database = resource_path("eddc.db")
db_file = Path(database)


def load_position(window, id, x, y):  # load Window Position if stored else load default
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        sql = f'''SELECT x, y FROM eddc_positions where id = {id}'''
        cursor.execute(sql)
        position = cursor.fetchone()
        if position:
            x_win = str(position[0])
            y_win = str(position[1])
            window.geometry(f'{x}x{y}+{x_win}+{y_win}')
        else:
            window.geometry(f'{x}x{y}+130+130')
            cursor.execute("INSERT INTO eddc_positions (x, y) VALUES (130, 130)")
            cursor.execute("INSERT INTO eddc_positions (x, y) VALUES (130, 130)")
            cursor.execute("INSERT INTO eddc_positions (x, y) VALUES (130, 130)")
            cursor.execute("INSERT INTO eddc_positions (x, y) VALUES (130, 130)")
            connection.commit()


def save_position(window, id):
    position = {
        "x": window.winfo_x(),
        "y": window.winfo_y()
    }
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        sql = f'''UPDATE eddc_positions SET x = {position["x"]} , y = {position["y"]} where id = {id}'''
        cursor.execute(sql)
        connection.commit()