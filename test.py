import json

timestamp = "2020-04-20T18:26:29Z"
faction = "Stellanebula Project"
mission_type = "Mission_Courier"
mission_id = 512345678
 

def create_json_ma():
	my_json = 	{"timestamp": "2020-04-20T18:26:29Z",
					 "event": "MissionAccepted",
					 "Faction": faction,
					 "Name": mission_type,
					 "LocalisedName": "Sensitive Data Delivery",
					 "TargetFaction": "Peoples Procyon Values Party",
					 "DestinationSystem": "Procyon",
					 "DestinationStation": "Davy Dock",
					 "Expiry": "2020-04-21T18:25:18Z",
					 "Wing": 'false',
					 "Influence": "++",
					 "Reputation": "+",
					 "Reward": 53764,
					 "MissionID": mission_id } 
	with open('data.json', 'a+', encoding='utf-8') as f:
			json.dump(my_json, f)
			f.write('\n')

create_json_ma()


def create_json_mission_completed():
	my_json = 	{
				  "timestamp": "2021-05-17T02:32:40Z",
				  "event": "MissionCompleted",
				  "Faction": faction,
				  "Name": mission_type,
				  "MissionID": mission_id,
				  "Commodity": "$Bertrandite_Name;",
				  "Commodity_Localised": "Bertrandite",
				  "Count": 624,
				  "DestinationSystem": "Apotanites",
				  "DestinationStation": "Galois Terminal",
				  "Reward": 47604000,
				  "FactionEffects": [
					{
					  "Faction": faction,
					  "Effects": [
						{
						  "Effect": "$MISSIONUTIL_Interaction_Summary_EP_up;",
						  "Effect_Localised": "The economic status of $#MinorFaction; has improved in the $#System; system.",
						  "Trend": "UpGood"
						}
					  ],
					  "Influence": [
						{
						  "SystemAddress": 2793649703291,
						  "Trend": "UpGood",
						  "Influence": "+++++"
						}
					  ],
					  "ReputationTrend": "UpGood",
					  "Reputation": "++"
					}
				  ]
				}
	with open('data.json', 'a+', encoding='utf-8') as f:
		json.dump(my_json, f)
		f.write('\n')

		
create_json_mission_completed()                        
