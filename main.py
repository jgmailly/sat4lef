import sys
import argparse
from utils import *

from pysat.solvers import Glucose4, Minisat22
from pysat.examples.rc2 import RC2
from pysat.examples.musx import MUSX
from pysat.examples.mcsls import MCSls
from pysat.formula import WCNF

parser = argparse.ArgumentParser()
parser.add_argument("pref_file", type=argparse.FileType('r'), help="path to the preference file")
parser.add_argument("social_file", type=argparse.FileType('r'), help="path to the social file")
parser.add_argument("-o", "--out", type=argparse.FileType('a'), help="optional file to print the output (append)")
parser.add_argument("--mus", action="store_true", help="if set compute a mus instead of the allocation (only works if formula is unsat)")

args = parser.parse_args()

preferences = dict()

preferences_lines = args.pref_file.read().splitlines()

for pref_line in preferences_lines:
    agent, pref_list = parse_preference_line(pref_line)
    preferences[agent] = pref_list


agents, social, number_of_edges = parse_tgf(args.social_file)

items = get_objects_from_preferences(agents,preferences)

print(f"agents = {agents}")
print(f"social = {social}")
print(f"number_of_edges = {number_of_edges}")
print(f"items = {items}")
print(f"preferences = {preferences}")

SAT_variables_meaning = dict()

for agent in agents:
    for item in items:
        #print(f"alloc({agent},{item}) = {get_SAT_variable(agent, agents, item, items)}")
        SAT_variables_meaning[get_SAT_variable(agent, agents, item, items)] = f"alloc({agent},{item})"

#print(SAT_variables_meaning)

clauses = []

for agent in agents:
    clauses.append(at_least_one_item(agent, agents, items)) # clause \phi_{alloc}^{\geq 1}(i)
    for item in items:
        other_agents = agents.copy()
        other_agents.remove(agent)
        for other_agent in other_agents:
            clauses.append(agents_do_not_share_items(agent, other_agent, agents, item, items)) # clause \phi_{alloc}^O(o,i,j)

## Determines whether an agent prefers item1 over item2
def agent_prefers(preferences, agent, item1, item2):
    agent_prefs = preferences[agent]
    return agent_prefs.index(item1) < agent_prefs.index(item2)
            
for edge in social:
    for item in items:
        clause = [-get_SAT_variable(edge[0], agents, item, items)]

        other_items = items.copy()
        other_items.remove(item)
        for other_item in other_items:
            if agent_prefers(preferences, other_agent, other_item, item) and agent_prefers(preferences, agent, item, other_item):
                clause.append(get_SAT_variable(edge[1], agents, other_item, items)

        clauses.append(clause) # clause \phi_{lef}(i,j,o)
