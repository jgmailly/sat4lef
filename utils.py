import sys

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
