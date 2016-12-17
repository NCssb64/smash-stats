import requests
import json
from collections import *


smash_games = {1: "Melee", 3: "Smash 4"}
smash_formats = defaultdict(str, {1: "Singles", 2: "Doubles", 5: "Crews"})
api_prefix = 'https://api.smash.gg/'
api_entrant_postfix = '?expand[]=entrants'
api_sets_postfix = '?expand[]=sets'
smash_games = {1: "Melee", 3: "Smash 4"}

def sanatize_name(name):
    return (name.split('|', 1)[-1]).lstrip().lower().replace('"', '')

class event:
    def __init__(self, event_id, event_name, gameId, _format):
        self.event_id = event_id
        self.event_name = event_name
        self.game = smash_games[gameId]
        self.format_id = _format
        self.format = smash_formats[_format]
        self.phases = []
        self.groups = []
        self.entrants = {}

    def add_phases(self, phases):
        self.phases = phases

    def add_groups(self, groups):
        for group in groups:
            self.groups.append(group)


    def add_entrants(self, entrants):
        for entrant in entrants:
            self.entrants[entrant["id"]] = sanatize_name(entrant["name"])


r = requests.get('https://api.smash.gg/tournament/the-big-house-6?expand[]=phase&expand[]=groups&expand[]=event')
#r = requests.get('https://api.smash.gg/phase_group/76016?expand[]=sets&expand[]=standings&expand[]=selections')
data = json.loads(r.text)
phase_ids = []
event_ids = []
event_phases = defaultdict(list)
phase_groups = defaultdict(list)

#Get all event IDs
#Get all the phase IDs
#Assign each phase to its event
for phase in data["entities"]["phase"]:
    event_phases[phase["eventId"]].append(phase["id"])
    phase_ids.append(phase["id"])

#Assign each group to its phase.
for group in data["entities"]["groups"]:
    phase_groups[group["phaseId"]].append(group["id"])

#Separate each phase by game
events = {}
for event_id in event_phases:
    r = requests.get(api_prefix + 'event/' + str(event_id) + api_entrant_postfix)
    evnt_data = json.loads(r.text)
    events[evnt_data["entities"]["event"]["id"]] = event(event_id, evnt_data["entities"]["event"]["name"], evnt_data["entities"]["event"]["videogameId"], evnt_data["entities"]["event"]["type"])
    tmp = evnt_data["entities"]["entrants"]
    events[evnt_data["entities"]["event"]["id"]].add_entrants(tmp)

print("Retrieved events")

for event in events:
    events[event].add_phases(event_phases[event])
    for phase in events[event].phases:
        events[event].add_groups(phase_groups[phase])
    
    #print(events[event].event_name, events[event].groups)

#print(events[12830].entrants[288001])
#print(events[12830].entrants[282600])
f = open("tbh6_ms.csv", "w")
f.write("P1, P2, set winner\n")
for group in events[12830].groups:
    results = requests.get(api_prefix + 'phase_group/' +  str(group) + api_sets_postfix)
    result_data = json.loads(results.text)
    print("Retrieving sets from group #:" + str(group))
    for _set in result_data["entities"]["sets"]:
        p1 = _set["entrant1Id"]
        p2 = _set["entrant2Id"]
        if(p1 == None or p2 == None):
            continue
        result = 0
        if _set["winnerId"] == p2:
            result = 1
        try:
            f.write(events[12830].entrants[p1] + ',' + events[12830].entrants[p2] + ',' + str(result) + '\n')
        except:
            f.write((events[12830].entrants[p1] + ',' + events[12830].entrants[p2] + ',' + str(result) + '\n').encode('utf-8'))

print("Wrote Results to file")
f.close()

#At this point we have every event with all group numbers, so we can use each one to look up set information.
#Once we have set information, we can output to csv (after translating entrantId -> name)




#   Get the game / event via request
#   r = requests.get(api_prefix + 'event/' + str(event_phases.key))
#   Save the game name, type, phase ids and groups to one object

#   Event Contains:
#       Several Phases
#       Phase Contains:
#           Several Groups
#           Group Contains:
#               Sets
#               Set contains:
#                   Players
#                   Winner


#======
#=TODO=
#======
#Create a class for event
#Create a class for phase
#Create a class for group
#Create a class of set
#Create a lookup table from entrantID to player name

#After we get the results, spit them out into a csv
#Read the CSV into the glicko calc




#print(phase_groups)
#for event in data["entities"]["phase"]:
#    r = requests.get(api_prefix + 'event/' + str(event["eventId"]))
#    evnt_data = json.loads(r.text)
#    if(evnt_data["entities"]["event"]["name"] == "Melee Singles"):
#        print(evnt_data["entities"]["event"]["id"])
   # print(evnt_data["entities"]["event"]["name"])
