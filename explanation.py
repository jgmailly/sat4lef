import sys
import time
import copy
import argparse
from explanation_graph import *


argparser = argparse.ArgumentParser()
argparser.add_argument("mus_file", help="the file containing the enforcement query")
argparser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
cli_args = argparser.parse_args()


MUS_file = sys.argv[1]
    
with open(MUS_file) as f:
    lines = [line.rstrip() for line in f]

positive_clauses = []
not_both_clauses = []
not_clauses = []
implication_clauses = []

def format_clause(clause_line):
    return clause_line.split(" ")

def is_negative_literal(literal):
    return literal[0] == "-"

def is_positive_clause(clause):
    for literal in clause:
        if is_negative_literal(literal):
            return False
    return True

def is_not_both_clause(clause):
    return len(clause) == 2 and is_negative_literal(clause[0]) and is_negative_literal(clause[1])

def is_not_clause(clause):
    return len(clause) == 1
    


#print(f"lines = {lines}")

for line in lines:
    if line != '':
        clause = format_clause(line)
        if is_positive_clause(clause):
            positive_clauses.append(clause)
        elif is_not_both_clause(clause):
            not_both_clauses.append(clause)
        elif is_not_clause(clause):
            not_clauses.append(clause)
        else:
            implication_clauses.append(clause)

if cli_args.verbose:
    print("--------------------------------\n")
    print(f"positive_clauses = {positive_clauses}") # at-least-one-object-per-agent
    print("--------------------------------\n")
    print(f"not_both_clauses = {not_both_clauses}")  # at-most-one-agent-per-object
    print("--------------------------------\n")
    print(f"not_clauses = {not_clauses}") # lef-clauses
    print("--------------------------------\n")
    print(f"implication_clauses = {implication_clauses}") # lef-clauses
    print("--------------------------------\n")


graph = ExplanationGraph()
top = ClauseNode("top")
graph.add_node(top)
bottom = ClauseNode("bottom")
graph.add_node(bottom)

all_literals = set()

for clause in positive_clauses:
    node = ClauseNode("at-least-one-object-per-agent")
    for literal in clause:
        all_literals.add(literal)
        node.add_literal(literal)
    graph.add_node(node)

for clause in not_both_clauses:
    node = ClauseNode("at-most-one-agent-per-object")
    for literal in clause:
        all_literals.add(literal)
        node.add_literal(literal)
    graph.add_node(node)

for clause in not_clauses:
    node = ClauseNode("lef-clause")
    for literal in clause:
        all_literals.add(literal)
        node.add_literal(literal)
    graph.add_node(node)

for clause in implication_clauses:
    node = ClauseNode("lef-clause")
    for literal in clause:
        all_literals.add(literal)
        node.add_literal(literal)
    graph.add_node(node)

for literal in all_literals:
    node = ClauseNode("var")
    if literal[0] == "-":
        node.add_literal(literal[1:])
    else:
        node.add_literal(literal)
    graph.add_node(node)

for node1 in graph.get_nodes():
    if node1.get_node_type() == "at-least-one-object-per-agent":
        graph.add_edge(top, node1)
    if node1.get_node_type() == "at-most-one-agent-per-object":
        graph.add_edge(node1, bottom)
    if node1.get_node_type() == "lef-clause" and len(node1.get_literals()) == 1:
        graph.add_edge(node1, bottom)
    for node2 in graph.get_nodes():
        if node1.get_node_type() == "at-least-one-object-per-agent" and node2.get_node_type() == "var":
            if node2.get_literals()[0] in node1.get_literals():
                graph.add_edge(node1,node2)
        if node1.get_node_type() == "var" and node2.get_node_type() == "at-most-one-agent-per-object":
            literal = node1.get_literals()[0]
            if "-" + literal in node2.get_literals():
                graph.add_edge(node1, node2)
        if node1.get_node_type() == "lef-clause" and node2.get_node_type() == "var":
            if node2.get_literals()[0] in node1.get_literals():
                graph.add_edge(node1, node2)
        if node1.get_node_type() == "var" and node2.get_node_type() == "lef-clause":
            literal = node1.get_literals()[0]
            if "-" + literal in node2.get_literals():
                graph.add_edge(node1, node2)
    
print(graph.to_dot())

            
if cli_args.verbose:
    print("Number of positive clauses:", len(positive_clauses))
    for pc in positive_clauses:
        print("Length of positive clause:", len(pc))
#    print("Number of Not both clauses:", len(not_both_clauses))
#    print("Number of Not clauses:", len(not_clauses))
#    print("Number of Implication clauses:",len(implication_clauses))
    print("Number of clauses:", len(positive_clauses + not_both_clauses + not_clauses + implication_clauses))

## Garder les informations suivantes :
## - nombre de clauses positives
## - nombre de clauses du MUS
## - nombre d'agents impliqués
## - nombre d'objets impliqués (longueur de la clause positive initiale ?)




involved_objects = set()
involved_agents = set()




                    
                    
                    
start_time = time.time()
graph.activate()
end_time = time.time()

if cli_args.verbose:
    print(f"Time:{end_time-start_time},nb_agents:{len(list(involved_agents))},nb_objects:{len(list(involved_objects))}")
