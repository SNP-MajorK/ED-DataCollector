import json
import os
import sys
from tkinter import *
from datetime import datetime

from tkinter import ttk


def create_json_fsdjump(starsystem, systemaddress, starpos_x, starpos_y, starpos_z, edsm_id):

	now = datetime.now()
	year = now.strftime("%Y")
	month = now.strftime("%m")
	day = now.strftime("%d")
	time = now.strftime("%H:%M:%S")
	timestamp = (year+'-'+month+'-'+day+'T'+time+'Z')
	starpos_xyz = [starpos_x ,starpos_y ,starpos_z]
	print(starpos_xyz)
	my_json = {
					"timestamp": timestamp,
					"event": "FSDJump",
					"Taxi": bool(0),
					"Multicrew": bool(0),
					"StarSystem": starsystem,
					"SystemAddress": systemaddress,
					"StarPos":
						starpos_xyz,
					"SystemAllegiance": "",
					"SystemEconomy": "$economy_None;",
					"SystemEconomy_Localised": "None",
					"SystemSecondEconomy": "$economy_None;",
					"SystemSecondEconomy_Localised": "None",
					"SystemGovernment": "$government_None;",
					"SystemGovernment_Localised": "None",
					"SystemSecurity": "$GAlAXY_MAP_INFO_state_anarchy;",
					"SystemSecurity_Localised": "Anarchy",
					"Population": 0,
					"Body": starsystem +" A",
					"BodyID": 1,
					"BodyType": "Star",
					"JumpDist": 10,
					"FuelUsed": 4,
					"FuelLevel": edsm_id
				}


	with open('data.json', 'a+', encoding='utf-8') as f:
		json.dump(my_json, f)
		f.write('\n')
	my_json = json.dumps(my_json, indent=2)
	text_box.insert(INSERT, my_json)


def resource_path(relative_path):

	""" Get absolute path to resource, works for dev and for PyInstaller """
	base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
	return os.path.join(base_path, relative_path)


def get_data():

	starsystem = system_entry.get()
	systemaddress = int(system_address_entry.get())
	starpos_x = float(starpos_x_entry.get())
	starpos_y = float(starpos_y_entry.get())
	starpos_z = float(starpos_z_entry.get())
	edsm_id = int(edsm_id_entry.get())
	text_box.delete(1.0, END)
	create_json_fsdjump(starsystem, systemaddress, starpos_x, starpos_y, starpos_z, edsm_id)



def main():

	global root, starpos_x_entry, starpos_y_entry, starpos_z_entry, system_address_entry, system_entry, \
		text_box, edsm_id_entry

	root = Tk()
	root.title('ED - JSON Creator')
	# root.configure(background='black')
	root.minsize(415, 400)
	root.maxsize(500, 500)

	try:
		img = resource_path("eddc.ico")
		root.iconbitmap(img)
	except TclError:
		print('Icon not found)')


	my_top_label = Label(root, text="data.json")
	my_top_label.pack()
	system_entry = Entry(root, width=50)
	system_entry.insert(0, 'Systemname')
	system_entry.pack(pady=5)

	system_address_entry = Entry(root, width=50)
	system_address_entry.insert(0, 'Systemaddress')
	system_address_entry.pack(pady=5)

	starpos_x_entry = Entry(root, width=50)
	starpos_x_entry.insert(0, 'X Koordinate')
	starpos_x_entry.pack(pady=5)

	starpos_y_entry = Entry(root, width=50)
	starpos_y_entry.insert(0, 'Y Koordinate')
	starpos_y_entry.pack(pady=5)

	starpos_z_entry = Entry(root, width=50)
	starpos_z_entry.insert(0, 'Z Koordinate')
	starpos_z_entry.pack(pady=5)

	edsm_id_entry = Entry(root, width=50)
	edsm_id_entry.insert(0, 'EDSM ID')
	edsm_id_entry.pack(pady=5)


	ok_but = Button(root,
					# width=4,
					activebackground='#000050',
					activeforeground='white',
					text='OK',
					bg='black',
					fg='white',
					command=get_data,
					font=("Helvetica", 10))
	ok_but.pack()

	text_box = Text(root)
	text_box.pack(padx=3, pady=3)

	root.mainloop()



main()
