import inspect
import sqlite3
import os
import RegionMapData
from RegionMap import *


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

database = resource_path("eddc.db")


def check_table(var):

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    tables = cursor.execute("SELECT name FROM sqlite_schema WHERE type='table'").fetchall()
    for i in tables:
        if var in i:
            return 1
    return 0


def create_codex_entry():

    if check_table('codex_entry') == 1:
        return

    bio_worth = [('Albidum Sinuous Tubers', '111,300'), ('Aleoida Arcus', '7252,500'),
                 ('Aleoida Coronamus', '6,284,600'), ('Aleoida Gravis', '12,934,900'),
                 ('Aleoida Laminiae', '3,385,200'), ('Aleoida Spica', '3,385,200'),
                 ('Amphora Plant', '117,900'), ('Aureum Brain Tree', '115,900'),
                 ('Bacterium Acies', '1,000,000'), ('Bacterium Alcyoneum', '1,658,500'),
                 ('Bacterium Aurasus', '1,000,000'), ('Bacterium Bullaris', '1,152,500'),
                 ('Bacterium Cerbrus', '1,689,800'), ('Bacterium Informem', '8,418,000'),
                 ('Bacterium Nebulus', '5,289,900'), ('Bacterium Omentum', '4,638,900'),
                 ('Bacterium Scopulum', '4,934,500'), ('Bacterium Tela', '1,949,000'),
                 ('Bacterium Verrata', '3,897,000'), ('Bacterium Vesicula', '1,000,000'),
                 ('Bacterium Volu', '7,774,700'), ('Bark Mounds', '108,900'),
                 ('Blatteum Bioluminescent Anemone', '110,500'), ('Blatteum Sinuous Tubers', '111,300'),
                 ('Cactoida Cortexum', '3,667,600'), ('Cactoida Lapis', '2,483,600'),
                 ('Cactoida Peperatis', '2,483,600'), ('Cactoida Pullulanta', '3,667,600'),
                 ('Cactoida Vermis', '16,202,800'), ('Caeruleum Sinuous Tubers', '111,300'),
                 ('Clypeus Lacrimam', '8,418,000'), ('Clypeus Margaritus', '11,873,200'),
                 ('Clypeus Speculumi', '16,202,800'), ('Concha Aureolas', '7,774,700'),
                 ('Concha Biconcavis', '19,010,800'), ('Concha Labiata', '2,352,400'),
                 ('Concha Renibus', '4,572,400'), ('Croceum Anemone', '110,500'),
                 ('Crystalline Shards', '117,900'), ('Electricae Pluma', '6,284,600'),
                 ('Electricae Radialem', '6,284,600'), ('Fonticulua Campestris', '1,000,000'),
                 ('Fonticulua Digitos', '1,804,100'), ('Fonticulua Fluctus', '20,000,000'),
                 ('Fonticulua Lapida', '3,111,000'), ('Fonticulua Segmentatus', '19,010,800'),
                 ('Fonticulua Upupam', '5,727,600'), ('Frutexa Acus', '7,774,700'),
                 ('Frutexa Collum', '1,639,800'), ('Frutexa Fera', '1,632,500'),
                 ('Frutexa Flabellum', '1,808,900'), ('Frutexa Flammasis', '10,326,000'),
                 ('Frutexa Metallicum', '1,632,500'), ('Frutexa Sponsae', '5,988,000'),
                 ('Fumerola Aquatis', '6,284,600'), ('Fumerola Carbosis', '6,284,600'),
                 ('Fumerola Extremus', '16,202,800'), ('Fumerola Nitris', '7,500,900'),
                 ('Fungoida Bullarum', '3,703,200'), ('Fungoida Gelata', '3,330,300'),
                 ('Fungoida Setisis', '1,670,100'), ('Fungoida Stabitis', '2,680,300'),
                 ('Gypseeum Brain Tree', '115,900'), ('Lindigoticum Brain Tree', '115,900'),
                 ('Lindigoticum Sinuous Tubers', '111,300'), ('Lividum Brain Tree', '115,900'),
                 ('Luteolum Anemone', '110,500'), ('Osseus Cornibus', '1,483,000'), ('Osseus Discus', '12,934,900'),
                 ('Osseus Fractus', '4,027,800'), ('Osseus Pellebantus', '9,739,000'), ('Osseus Pumice', '3,156,300'),
                 ('Osseus Spiralis', '2,404,700'), ('Ostrinum Brain Tree', '115,900'),
                 ('Prasinum Bioluminescent Anemone', '110,500'), ('Prasinum Sinuous Tubers', '111,300'),
                 ('Puniceum Anemone', '110,500'), ('Puniceum Brain Tree', '115,900'),
                 ('Recepta Conditivus', '14,313,700'), ('Recepta Deltahedronix', '16,202,800'),
                 ('Recepta Umbrux', '12,934,900'), ('Roseum Anemone', '110,500'),
                 ('Roseum Bioluminescent Anemone', '110,500'), ('Roseum Brain Tree', '115,900'),
                 ('Roseum Sinuous Tubers', '111,300'), ('Rubeum Bioluminescent Anemone', '110,500'),
                 ('Stratum Araneamus', '2,448,900'), ('Stratum Cucumisis', '16,202,800'),
                 ('Stratum Excutitus', '2,448,900'), ('Stratum Frigus', '2,637,500'),
                 ('Stratum Laminamus', '2,788,300'), ('Stratum Limaxus', '1,362,000'), ('Stratum Paleas', '1,362,000'),
                 ('Stratum Tectonicas', '19,010,800'), ('Tubus Cavas', '11,873,200'), ('Tubus Compagibus', '7,774,700'),
                 ('Tubus Conifer', '2,415,500'), ('Tubus Rosarium', '2,637,500'), ('Tubus Sororibus', '5,727,600'),
                 ('Tussock Albata', '3,252,500'), ('Tussock Capillum', '7,025,800'), ('Tussock Caputus', '3,472,400'),
                 ('Tussock Catena', '1,766,600'), ('Tussock Cultro', '1,766,600'), ('Tussock Divisa', '1,766,600'),
                 ('Tussock Ignis', '1,849,000'), ('Tussock Pennata', '5,853,800'), ('Tussock Pennatis', '1,000,000'),
                 ('Tussock Propagito', '1,000,000'), ('Tussock Serrati', '4,447,100'),
                 ('Tussock Stigmasis', '19,010,800'), ('Tussock Triticum', '7,774,700'),
                 ('Tussock Ventusa', '3,227,700'), ('Tussock Virgam', '14,313,700'),
                 ('Violaceum Sinuous Tubers', '111,300'), ('Viride Brain Tree', '115,900'),
                 ('Viride Sinuous Tubers', '111,300')]

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cce_regions = RegionMapData.regions
        cursor.execute("""CREATE table IF NOT EXISTS codex_entry (
                        data TEXT,
                        worth INTEGER,
                        type INTEGER, 
                        region TEXT)
                        """)
        select = cursor.execute("SELECT * from codex_entry").fetchall()
        if not select:
            for a in cce_regions:
                if a is not None:
                    for i in bio_worth:
                        cursor.execute("INSERT INTO codex_entry VALUES (?, ?, ?, ?)", (i[0], i[1], 0, a))
            connection.commit()


def create_DB_Bio_color():

    if check_table('Bio_color') == 1:
        return

    file = resource_path("bio_color_distance.txt")
    with open(file, 'r', encoding='UTF8') as datei:
        for zeile in datei.readlines():
            zeile = zeile.rstrip('\n')
            zeile = zeile.split(';')
            zeile[3] = (zeile[3].split(','))
            for count, i in enumerate(zeile[3]):
                if count % 2 == 0:
                    insert_into_db_bio_color(zeile[0], zeile[1], zeile[2], zeile[3][count], zeile[3][count + 1])


def insert_into_db_bio_color(name, distance, criteria, criterium, color):

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute("""CREATE table IF NOT EXISTS Bio_color (
                    Name TEXT,
                    Distance INTEGER,
                    Criteria TEXT,
                    Criterium TEXT,
                    COLOR TEXT)""")
    cursor.execute("INSERT INTO Bio_color VALUES (?,?,?,?,?)", (name, distance, criteria, criterium, color))
    connection.commit()


def create_DB_Bio_prediction():

    if check_table('Bio_prediction') == 1:
        return

    file = resource_path("bio_data2.txt")
    with open(file, 'r', encoding='UTF8') as datei:
        for zeile in datei.readlines():
            # print(zeile)
            zeile = zeile.rstrip('\n')
            zeile = zeile.split(';')
            try:
                zeile[1] = (zeile[1].split(','))  # Stars
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
                print(zeile)
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