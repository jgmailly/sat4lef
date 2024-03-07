import sys

from collections import defaultdict

#import networkx as nx

## Parses the TGF file representing the social network
## Returns the list of agents, the list of edges, and the number of edges
def parse_tgf(social_file):
    social_lines = social_file.read().splitlines()

    end_agents = False
    agents = []
    social = []
    number_of_edges = 0
    for soc_line in social_lines:
        if soc_line != "#":
            if not end_agents:
                agents.append(soc_line)
            else:
                social.append(parse_social_line(soc_line))
                number_of_edges += 1
        else:
            end_agents = True
    return agents, social, number_of_edges

## Parses a line in the preference file
## Returns the name of the agent and the ordered list of items corresponding to the agent's preferences
def parse_preference_line(pref_line):
    splitting = pref_line.split(":")
    agent = splitting[0]
    items = splitting[1]
    return agent, items.split(" ")

## Splits a line from the social network (edges of the graph)
def parse_social_line(soc_line):
    return soc_line.split(" ")

## Provides the list of objects appearing in the preference file
def get_objects_from_preferences(agents,preferences):
    items = []
    for item in preferences[agents[0]]:
        items.append(item)
    items.sort()
    return items


def encode_pref_agent(pref_agent,pref_vars,objects,agents,agent):
    pref_index = 0
    n_constraints = 0
    clauses = []

    for obj_k in objects:
        for obj_l in objects:
            if pref_agent.index(obj_k) < pref_agent.index(obj_l):
                # The agent prefers obj_k to obj_l
                clauses.append([pref_vars[agents.index(agent)][objects.index(obj_k)][objects.index(obj_l)]])
                n_constraints += 1
            else:
                clauses.append([-pref_vars[agents.index(agent)][objects.index(obj_k)][objects.index(obj_l)]])
                n_constraints += 1

    return [clauses,n_constraints]

def parse_model(model, agents, objects, alloc_vars):
    for agent_id in range(len(agents)):
        for obj_id in range(len(objects)):
            if alloc_vars[agent_id][obj_id] in model:
                print(f"alloc_({agents[agent_id]},{objects[obj_id]})")
    #parse_unsat_pref(model, agents, objects, pref_vars)

def parse_unsat_pref(model, agents, objects, pref_vars):
    for agent_id in range(len(agents)):
        for obj_id in range(len(objects)):
            for obj2_id in range(len(objects)):
                if pref_vars[agent_id][obj_id][obj2_id] in model:
                    print(f"pref_({agents[agent_id]}:({objects[obj_id]} > {objects[obj2_id]})")



def decode_clause(clause, agents, objects, alloc_vars):
    result, ids, set_agent, set_obj = parse_better(clause, agents, objects, alloc_vars)
    print(result) if len(result) != 0 else print("False !")
    return ids, set_agent, set_obj 


def parse(model, agents, objects, alloc_vars):
    result = ""
    ids = []
    for agent_id in range(len(agents)):
        for obj_id in range(len(objects)):
            if -alloc_vars[agent_id][obj_id] in model:
                ids.append([agent_id, obj_id])
                result += f"not alloc_({agents[agent_id]},{objects[obj_id]}), "
    for agent_id in range(len(agents)):
        for obj_id in range(len(objects)):
            if alloc_vars[agent_id][obj_id] in model:
                ids.append([agent_id, obj_id])
                result += f"alloc_({agents[agent_id]},{objects[obj_id]}), "
    
    return result, ids

def parse_better(model, agents, objects, alloc_vars):
    result = ""
    ids = []
    set_obj = set()
    set_agent = set()
    
    #if it is a preference clause
    for agent_id in range(len(agents)):
        for obj_id in range(len(objects)):
            if -alloc_vars[agent_id][obj_id] in model:
                ids.append(agent_id)
                result += f"alloc_({agents[agent_id]},{objects[obj_id]}) => "
                set_agent.add(agent_id)
                set_obj.add(obj_id)
    
    for agent_id in range(len(agents)):
        started = False
        for obj_id in range(len(objects)):
            if alloc_vars[agent_id][obj_id] in model:
                if not started:
                    ids.append(agent_id)
                    result += f"alloc_({agents[agent_id]}, {{"
                    set_agent.add(agent_id)
                    started = True
                result += f"{objects[obj_id]},"
                
                set_obj.add(obj_id)
        if started:
            result += "})"
            started = False
    
    

    return result, (ids[0], ids[1]) if len(ids)==2 else (ids[0],), set_agent, set_obj

def print_at_least_one(agents, objects, set_agent, set_obj):
    if len(set_obj) == 1:
        obj_id = list(set_obj)[0]
        toprint = f"Give {objects[obj_id]:3} to one of "
        for agent_id in range(len(agents)):
            if agent_id in set_agent:
                toprint += f"{agents[agent_id]} "
            else:
                toprint += " "*(1+len(str(agents[agent_id])))
        toprint = toprint[:-1]
        print(toprint)
    elif len(set_agent) == 1:
        agent_id = list(set_agent)[0]
        toprint = f"Give to {agents[agent_id]:2} one of "
        for obj_id in range(len(objects)):
            if obj_id in set_obj:
                toprint += f"{objects[obj_id]} "
            else:
                toprint += " "*(1+len(str(objects[obj_id])))
        toprint = toprint[:-1]
        print(toprint)
    
def print_not_both(clause,agents, objects,  alloc_vars):
    to_print = "not both "
    for agent_id in range(len(agents)):
        for obj_id in range(len(objects)):
            if -alloc_vars[agent_id][obj_id] in clause:
                to_print += f"alloc_({agents[agent_id]},{objects[obj_id]}) and "
    to_print = to_print[:-5]
    print(to_print) 

def decode_mus(clause_mus, agents, objects, alloc_vars, skip_ones=False):
    ids = set()
    two = 0
    one = 0
    set_ag = set()
    set_ob = set()
    for clause in clause_mus:
        if clause == []:
            print("False !")
            continue
        elif all([lit > 0 for lit in clause]):
            set_agent = set()
            set_obj = set()
            for agent_id in range(len(agents)):
                for obj_id in range(len(objects)):
                    if alloc_vars[agent_id][obj_id] in clause:
                        set_agent.add(agent_id)
                        set_obj.add(obj_id)
            set_ag = set_ag.union(set_agent)
            set_ob = set_ob.union(set_obj)
            print_at_least_one(agents, objects, set_agent, set_obj)
        elif len(clause) == 2 and all([lit < 0 for lit in clause]):
            print_not_both(clause, agents, objects,  alloc_vars)
        else:
            if skip_ones and len(clause) == 1:
                one += 1
                continue
            ids_clause, set_agent, set_obj  = decode_clause(clause, agents, objects, alloc_vars)
            set_ag = set_ag.union(set_agent)
            set_ob = set_ob.union(set_obj)
            if ids_clause != None and len(ids_clause) == 2:
                two += 1
            elif ids_clause != None and len(ids_clause) == 1:
                one += 1
            ids.add(ids_clause)
        
    return ids, one, two, set_ag, set_ob

def reduce_MUS(clause_mus, clause2meaning):
    acc = []
    ones = [clause for clause in clause_mus if (len(clause)==1 and not all(lit>0 for lit in clause))]
    clause_mus = [clause for clause in clause_mus if (len(clause)>1 or all(lit>0 for lit in clause))]
    while len(ones)>0:
        for one_clause in ones:
            for i in range(len(clause_mus)):
                if -one_clause[0] in clause_mus[i]:
                    tmp = clause2meaning[tuple(clause_mus[i])] 
                    clause_mus[i].remove(-one_clause[0])
                    clause2meaning[tuple(clause_mus[i])] = tmp
        #print(len(clause_mus), clause_mus)
        acc.extend(ones)
        ones = [clause for clause in clause_mus if (len(clause)==1 and not all(lit>0 for lit in clause))]
        ##FORCE ASSIGNEMENT WHEN JUST POSITIVE
        #forced_assginment = [clause for clause in clause_mus if (len(clause)==1 and all(lit>0 for lit in clause))]
        clause_mus = [clause for clause in clause_mus if(len(clause)>1 or all(lit>0 for lit in clause))]
    return clause_mus, acc

## Returns the integer which encodes the Boolean variable
## alloc_agent_item
## For agent i and item j (with i and j in [0,n-1]), we return i * n + j + 1
def get_SAT_variable(agent, agents, item, items):
    agent_index = agents.index(agent)
    item_index = items.index(item)

    return (agent_index) * len(agents) +  (item_index) + 1

## Builds the clause expressing that an agent must receive at least one item
def at_least_one_item(agent, agents, items):
    clause = []
    for item in items:
        clause.append(get_SAT_variable(agent, agents, item, items))
    return clause

## Builds the clause expressing that an item cannot be shared by two agents
def agents_do_not_share_items(agent, other_agent, agents, item, items):
    return [-get_SAT_variable(agent, agents, item, items), -get_SAT_variable(other_agent, agents, item, items)]

## Determines whether an agent prefers item1 over item2
def agent_prefers(preferences, agent, item1, item2):
    agent_prefs = preferences[agent]
    return agent_prefs.index(item1) < agent_prefs.index(item2)

## Builds a text representation of a clause
def clause_as_text(clause,SAT_variables_meaning):
    result = ""
    if len(clause) == 0:
        return "empty clause"
    for lit in clause:
        if lit > 0:
            result += SAT_variables_meaning[lit] + " "
        else:
            result += "-" + SAT_variables_meaning[-lit] + " "
    return result

# Builds a text representation of a model
def decode_model_into_alloc(model,SAT_variables_meaning):
    result = ""
    for lit in model:
        if lit > 0:
            result += SAT_variables_meaning[lit] + " "
    return result
