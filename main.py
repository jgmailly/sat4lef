import sys
import argparse
from utils import *

from clauses import *
from explanation_graph import *
from lef_mus import *
from metrics_on_muses import *

from pysat.solvers import Solver
from pysat.examples.rc2 import RC2
from pysat.examples.musx import MUSX
from pysat.examples.optux import OptUx
from pysat.examples.mcsls import MCSls
from pysat.formula import WCNF

parser = argparse.ArgumentParser()
parser.add_argument("pref_file", type=argparse.FileType('r'), help="path to the preference file")
parser.add_argument("social_file", type=argparse.FileType('r'), help="path to the social file")
parser.add_argument("-o", "--out", type=argparse.FileType('a'), help="optional file to print the output (append)")
parser.add_argument("--mus", action="store_true", help="if set compute a mus instead of the allocation (only works if formula is unsat)")
parser.add_argument("--enummin", action="store_true", help="enumerate the min MUSes (must be used in addition to --mus)")
#parser.add_argument("--enumall", action="store_true", help="enumerate all the MUSes")
parser.add_argument("--minagent", action="store_true", help="focuses on minimal MUSes that minimize the number of agents (must be used in addition to --mus)")
parser.add_argument("--verbose", action="store_true", help="print more information")
parser.add_argument("--redundant", action="store_true", help="add redundant structural clauses")



args = parser.parse_args()

preferences = dict()


preferences_lines = args.pref_file.read().splitlines()

for pref_line in preferences_lines:
    agent, pref_list = parse_preference_line(pref_line)
    preferences[agent] = pref_list


agents, social, number_of_edges = parse_tgf(args.social_file)

items = get_objects_from_preferences(agents,preferences)

SAT_variables_meaning = dict()

for agent in agents:
    for item in items:
        #print(f"alloc({agent},{item}) = {get_SAT_variable(agent, agents, item, items)}")
        SAT_variables_meaning[get_SAT_variable(agent, agents, item, items)] = f"alloc({agent},{item})"


#print(SAT_variables_meaning)

clauses = [] # Basic clauses, i.e. lists of literals
clauses_meaning = [] # clauses_meaning[i] corresponds to clauses[i]
clauses_objects = [] # Clause objects

lefmus = LefMus(args.pref_file.name.split(".")[0])
lefmus.sat_encoding(args.redundant)

clauses_objects = lefmus.get_clauses()

for clause in clauses_objects:
    clauses.append(clause.get_clause())
    clauses_meaning.append(clause.get_clause_meaning())
#    print(f"clause = {clause.get_clause()} - clause_meaning = {clause.get_clause_meaning()}")



##for agent in agents:
##    clauses.append(at_least_one_item(agent, agents, items)) # clause \phi_{alloc}^{\geq 1}(i)
##    clauses_meaning.append(f"phi_(alloc)^(>= 1, N)({agent})")
##    clauses_objects.append(AtLeastClause("agent", agent, agents, items))
##    
##    for item in items:
##        other_agents = agents.copy()
##        other_agents.remove(agent)
##        for other_agent in other_agents:
##            if other_agent > agent:
##                clauses.append(agents_do_not_share_items(agent, other_agent, agents, item, items)) # clause \phi_{alloc}^O(o,i,j)
##                clauses_meaning.append(f"phi_(alloc)^(<= 1, O)({item}, {agent}, {other_agent})")
##                clauses_objects.append(AtMostClause("object", item, agent, other_agent, agents, items))
##
##            
##for edge in social:
##    for item in items:
##        clause = [-get_SAT_variable(edge[0], agents, item, items)]
##
##        other_items = items.copy()
##        other_items.remove(item)
##        possible_items = []
##        for other_item in other_items:
##            if agent_prefers(preferences, edge[1], other_item, item) and agent_prefers(preferences, edge[0], item, other_item):
##                clause.append(get_SAT_variable(edge[1], agents, other_item, items))
##                possible_items.append(other_item)
##
##        #print(f"--- phi_LEF({edge[0]},{edge[1]},{item}) = {clause} = {clause_as_text(clause,SAT_variables_meaning)}")
##        clauses.append(clause) # clause \phi_{lef}(i,j,o)
##        clauses_meaning.append(f"phi_(lef)({edge[0]},{edge[1]},{item})")
##        clauses_objects.append(LefClause(edge[0],item,edge[1],possible_items,agents,items)) 
##        
##        # reverse direction of the edge
##        clause = [-get_SAT_variable(edge[1], agents, item, items)]
##
##        other_items = items.copy()
##        other_items.remove(item)
##        possible_items = []
##        for other_item in other_items:
##            if agent_prefers(preferences, edge[0], other_item, item) and agent_prefers(preferences, edge[1], item, other_item):
##                clause.append(get_SAT_variable(edge[0], agents, other_item, items))
##                possible_items.append(other_item)
##
##        #print(f"--- phi_LEF({edge[1]},{edge[0]},{item}) = {clause} = {clause_as_text(clause,SAT_variables_meaning)}")
##        clauses.append(clause) # clause \phi_{lef}(i,j,o)
##        clauses_meaning.append(f"phi_(lef)({edge[1]},{edge[0]},{item})")
##        clauses_objects.append(LefClause(edge[1],item,edge[0],possible_items,agents,items)) 
##
##if args.redundant:
##    for item in items:
##        clauses.append(at_least_one_agent(item, agents, items))
##        clauses_meaning.append(f"phi_(alloc)^(>= 1, 0)({item})")
##        other_items = [other_item for other_item in items if other_item > item]
##        for agent in agents:
##            for other_item in other_items:
##                clauses.append(items_do_not_share_agents(agent, agents, item, other_item, items)) # clause \phi_{alloc}^N(o,i,j)
##                clauses_meaning.append(f"phi_(alloc)^(<= 1,N)({item},{agent},{other_agent})")

      
#for clause in clauses:
#    print(clause, " - ", clause_as_text(clause,SAT_variables_meaning), " - ", clauses_meaning[clauses.index(clause)])



s = Solver(name='g4', bootstrap_with=clauses)

if s.solve():
    model = s.get_model()
    print(decode_model_into_alloc(model,SAT_variables_meaning))
    s.delete()
elif args.mus: 
    s.delete()
    cnf = WCNF()
    for clause in clauses:
        cnf.append(clause, weight=1)

    if not args.minagent: # Compute only one minimal MUS, any MUS (no use of metrics)

        with OptUx(cnf) as optux:
            MUS = optux.compute()
        if MUS == None:
            print("NO")
        else:
            #        print("First minimal MUS found:")
            #        print(f"MUS = {MUS}")
            MUS_clauses = []

            if args.verbose:
                print("============== Clauses in the MUS ==============")
            
            for index in MUS:
                ## printing clauses
                if args.verbose:
                    print(f"{clause_as_text_with_meaning(clauses[index-1],clauses_meaning[index-1], SAT_variables_meaning)}")

                MUS_clauses.append(clauses_objects[index-1])

            if args.verbose:
                print("=================================================")
                
            graph = ExplanationGraph()
            graph.init_from_list_of_clauses(MUS_clauses)

            if args.verbose:
                print("============== Explanation graph in DOT ==============")                
                print(graph.to_dot())
                print("======================================================")                

            activations = graph.activate()
            i = 1
            if args.verbose:
                print(f"There are {len(activations)} activation steps.")
                
            already_activated = [False for i in range(len(activations[0][0]))]

            for activation in activations:
                node_index = 0
                for activated_node in activation[0]:
                    if activated_node and not already_activated[node_index]:
                        text_translation = graph.get_nodes()[node_index].get_text_translation()
                        if text_translation != None:
                            print(text_translation)
                    node_index += 1
                already_activated = activation[0]

    else: # Focus on a minimal MUS with minimal number of agents
        min_cost=0
        min_MUSes = []
        with OptUx(cnf) as optux:
            for mus in optux.enumerate():
                if min_cost !=0 and min_cost!=optux.cost:
                    break
                min_cost = optux.cost
                min_MUSes.append(mus)

        # Arbitrarily choose the first one
        min_MUSes_clauses = []
        for min_MUS in min_MUSes:
            MUS_clauses = []
            for index in min_MUS:
                MUS_clauses.append(clauses_objects[index-1])
            min_MUSes_clauses.append(MUS_clauses)
        
        min_agent_MUS = min_metric_muses(min_MUSes_clauses,agents_metric)[0][0]


        graph = ExplanationGraph()
        graph.init_from_list_of_clauses(MUS_clauses)

        if args.verbose:
            print("============== Explanation graph in DOT ==============")                
            print(graph.to_dot())
            print("======================================================")                

        activations = graph.activate()
        i = 1
        if args.verbose:
            print(f"There are {len(activations)} activation steps.")
            
        already_activated = [False for i in range(len(activations[0][0]))]

        for activation in activations:
            node_index = 0
            for activated_node in activation[0]:
                if activated_node and not already_activated[node_index]:
                    text_translation = graph.get_nodes()[node_index].get_text_translation()
                    if text_translation != None:
                        print(text_translation)
                node_index += 1
                        
            already_activated = activation[0]
        

    if args.enummin: # or args.enumall: 
        print("==============================================================")
        print("=== MUS enumeration ")
        print("==============================================================")
        nb_mus=0
        min_cost=0
        with OptUx(cnf) as optux:
            for mus in optux.enumerate():
                if args.enummin and min_cost !=0 and min_cost!=optux.cost:
                    break
                nb_mus+=1
                min_cost = optux.cost
                print('mus {0} has cost {1}'.format(mus, optux.cost))
                if args.verbose:
                    print("==============================================================")
                    for index in mus:
                        print(f"{clause_as_text_with_meaning(clauses[index-1], clauses_meaning[index-1],SAT_variables_meaning)}")

        print("==============================================================")
        print("Found ", nb_mus, "MUS")

else:
    print("NON-LEF")
        
