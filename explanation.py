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

#print(lines)

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
    


print(f"lines = {lines}")

print("--------------------------------\n")

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
    
#print(graph.to_string())
print(graph.to_dot())

sys.exit("Closing")
            
if cli_args.verbose:
#    print("Positive clauses:", positive_clauses)
    print("Number of positive clauses:", len(positive_clauses))
    for pc in positive_clauses:
        print("Length of positive clause:", len(pc))
#    print("Not both clauses:", not_both_clauses)
#    print("Not clauses:", not_clauses)
#    print("Implication clauses:",implication_clauses)

## Garder les informations suivantes :
## - nombre de clauses positives
## - nombre de clauses du MUS
## - nombre d'agents impliqués
## - nombre d'objets impliqués (longueur de la clause positive initiale ?)
## - longueur des branches
## - nombre de fois qu'une clause est utilisée


def get_agent_from_negative_literal(literal):
    return literal[8:].split(",")[0]

def get_agent_from_literal(literal):
    if literal[0] == "-":
        return get_agent_from_negative_literal(literal)
    return literal[7:].split(",")[0]

def get_object_from_literal(literal):
    return literal.split(",")[1][:-1]

def get_indentation(k):
    indent = ""
    for i in range(k):
        indent += "\t"
    return indent

def print_with_indent(text, indentation = 0):
    print(f"{get_indentation(indentation)}{text}", end='')

def println_with_indent(text, indentation = 0):
    print(f"{get_indentation(indentation)}{text}")    

involved_objects = set()
involved_agents = set()

def add_involved(literal):
    global involved_objects
    global involved_agents
    involved_objects.add(get_object_from_literal(literal))
    involved_agents.add(get_agent_from_literal(literal))

def propagate(positive_clauses, not_clauses, not_both_clauses, implication_clauses, indentation):
    global involved_objects
    global involved_agents
    indentation_level = indentation
    for pc in positive_clauses:
        print_with_indent("We ", indentation_level)
        for literal in pc[:-1]:
            add_involved(literal)
            print_with_indent(f"must allocate {get_object_from_literal(literal)} to {get_agent_from_literal(literal)}, or we ")
        println_with_indent(f"must allocate {get_object_from_literal(pc[-1])} to {get_agent_from_literal(pc[-1])}.")
        add_involved(pc[-1])
        positive_clauses.remove(pc)

        for literal in pc:
            add_involved(literal)
            pos_clauses = copy.deepcopy(positive_clauses)
            n_clauses = copy.deepcopy(not_clauses)
            nb_clauses = copy.deepcopy(not_both_clauses)
            imp_clauses = copy.deepcopy(implication_clauses)

            #pos_clauses.remove(pc)
            
            println_with_indent(f"If we allocate object {get_object_from_literal(literal)} to agent {get_agent_from_literal(literal)}, then ", indentation_level)
            indentation_level += 1
            negated_literal = "-" + literal
            if [negated_literal] in n_clauses:
                println_with_indent(f"there is a contradiction with the fact that we must not allocate object {get_object_from_literal(negated_literal)} to agent {get_agent_from_literal(negated_literal)}.", indentation_level)

            for nbc in nb_clauses:
                if negated_literal in nbc:
                    nb_clauses.remove(nbc)
                    print_with_indent(f"since we cannot allocate both object {get_object_from_literal(nbc[0])} to agent {get_agent_from_literal(nbc[0])} and object {get_object_from_literal(nbc[1])} to agent {get_agent_from_literal(nbc[1])},", indentation_level)
                    nbc.remove(negated_literal)
                    new_not_clause = nbc
                    println_with_indent(f" then we cannot allocate object {get_object_from_literal(new_not_clause[0])} to agent {get_agent_from_literal(new_not_clause[0])}")
                    n_clauses.append(new_not_clause)

            for imp in imp_clauses:
                if negated_literal in imp:
                    imp_clauses.remove(imp)
                    print_with_indent(f"since allocating object {get_object_from_literal(negated_literal)} to agent {get_agent_from_literal(negated_literal)} implies that we ", indentation_level)
                    imp.remove(negated_literal)
                    new_pos_clause = imp
                    for literal in new_pos_clause[:-1]:
                        print_with_indent(f"must allocate {get_object_from_literal(literal)} to {get_agent_from_literal(literal)}, or we ")
                    print_with_indent(f"must allocate {get_object_from_literal(new_pos_clause[-1])} to {get_agent_from_literal(new_pos_clause[-1])}, then it is the case that we ")
                    for literal in new_pos_clause[:-1]:
                        print_with_indent(f"must allocate {get_object_from_literal(literal)} to {get_agent_from_literal(literal)}, or we ")
                    println_with_indent(f"must allocate {get_object_from_literal(new_pos_clause[-1])} to {get_agent_from_literal(new_pos_clause[-1])}.")
                    pos_clauses.append(new_pos_clause)

                propagate(pos_clauses, n_clauses, nb_clauses, imp_clauses, indentation_level)
            indentation_level -= 1

                    
                    
                    
start_time = time.time()
propagate(positive_clauses, not_clauses, not_both_clauses, implication_clauses,0)
end_time = time.time()

if cli_args.verbose:
    print(f"Time:{end_time-start_time},nb_agents:{len(list(involved_agents))},nb_objects:{len(list(involved_objects))}")
