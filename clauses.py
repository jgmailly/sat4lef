
from abc import ABC
from utils import *

class Clause(ABC,object):

    def __init__(self, agents):
        self.clause = []
        self.agents = agents

    def get_clause(self):
        return self.clause
    
    def get_translated_clause(self):
        return translated_clause(self.clause,self.agents)
    
    def get_clause_meaning(self):
        pass
    
    def get_concerned_agents(self):
        pass

    def get_concerned_objects(self):
        pass

    def get_variables(self):
        res = []
        for lit in self.clause:
            if lit < 0:
                res.append(-lit)
            else:
                res.append(lit)
        return list(set(res))

    def text_translation(self):
        pass

    def __str__(self):
        return self.clause_meaning()
    
    __repr__ = __str__
    

class AtLeastClause(Clause):
    def __init__(self, orientation, element, agents, items):
        Clause.__init__(self,agents)
        self.orientation = None
        self.elements_to_match = None
        self.clause = []
        if orientation == "agent":
            self.orientation = "agent"
            self.elements_to_match = "object"
            self.all_elements = items
            self.clause = at_least_one_item(element,agents,items)
        elif orientation == "object":
            self.orientation = "object"
            self.elements_to_match = "agent"
            self.all_elements = agents
            self.clause = at_least_one_agent(element,agents,items)
        self.central_element = element

    # def __init__(self, clause, agents, items):
    #     self.orientation = None
    #     self.elements_to_match = None
    #     self.all_elements = None
    #     self.central_element = None
    #     self.clause = clause
    #     vars = []
    #     for lit in clause:
    #         if lit < 0:
    #             return
    #         vars.append(get_alloc_variable(lit,agents))
    #     if vars[0[0]] == vars[1[0]]:
    #         self.orientation = "agent"
    #         self.elements_to_match = "object"
    #         self.central_element = vars[0[0]]
    #         self.all_elements = items
    #     elif vars[0[1]] == vars[1[1]]:
    #         self.orientation = "object"
    #         self.elements_to_match = "agent"
    #         self.central_element = vars[0[1]]
    #         self.all_elements = agents
            

    def get_concerned_agents(self):
        if self.orientation == "agent":
            return [self.central_element]
        else:
            return self.all_elements
        
    def get_concerned_objects(self):
        if self.orientation == "object":
            return [self.central_element]
        else:
            return self.all_elements

    def text_translation(self):
        return self.orientation+" "+str(self.central_element)+" should be matched with at least one "+self.elements_to_match
    
    def clause_meaning(self):
        return "at_least("+str(self.central_element)+")"
    

    
    
    

class AtMostClause(Clause):
    def __init__(self, orientation, element_to_not_share, competing_element1, competing_element2, agents, items):
        Clause.__init__(self,agents)
        self.orientation = None
        self.elements_to_match = None
        self.clause = []
        if orientation == "agent":
            self.orientation = "agent"
            self.elements_to_match = "objects"
            self.clause = items_do_not_share_agents(element_to_not_share,agents,competing_element1,competing_element2,items)
        elif orientation == "object":
            self.orientation = "object"
            self.elements_to_match = "agents"
            self.clause = agents_do_not_share_items(competing_element1,competing_element2,agents,element_to_not_share,items)
        self.element_to_not_share = element_to_not_share
        self.competing_element1 = competing_element1
        self.competing_element2 = competing_element2

    # def __init__(self, clause, agents):
    #     self.clause = clause
    #     self.orientation = None
    #     self.elements_to_match = None
    #     self.element_to_not_share = None
    #     self.competing_element1 = None
    #     self.competing_element2 = None
    #     if (len(clause) != 2 or clause[0] >= 0 or clause[1] >= 0):
    #         return 
    #     (a1,o1) = get_alloc_variable(-clause[0],agents)
    #     (a2,o2) = get_alloc_variable(-clause[1],agents)
    #     if a1 == a2:
    #         self.orientation = "agent"
    #         self.elements_to_match = "objects"
    #         self.element_to_not_share = a1
    #         self.competing_element1 = o1
    #         self.competing_element2 = o2
    #     elif o1 == o2:
    #         self.orientation = "object"
    #         self.elements_to_match = "agents"
    #         self.element_to_not_share = o1
    #         self.competing_element1 = a1
    #         self.competing_element2 = a2


    def get_concerned_agents(self):
        if self.orientation == "agent":
            return [self.element_to_not_share]
        else:
            return [self.competing_element1,self.competing_element2]
        
    def get_concerned_objects(self):
        if self.orientation == "object":
            return [self.element_to_not_share]
        else:
            return [self.competing_element1,self.competing_element2]

    def text_translation(self):
        return "However, "+self.orientation+" "+str(self.element_to_not_share)+" cannot be matched with both "+str(self.elements_to_match)+\
            " "+str(self.competing_element1)+" and "+str(self.competing_element2)+", a contradiction."
    
    def clause_meaning(self):
        return "at_most("+str(self.element_to_not_share)+", for "+str(self.competing_element1)+", "+str(self.competing_element2)+")"
    

class LefClause(Clause):
    def __init__(self, implicant_agent, implicant_object, implied_agent, possible_objects, agents, items):
        Clause.__init__(self,agents)
        self.implicant_agent = implicant_agent
        self.implicant_object = implicant_object
        self.implied_agent = implied_agent
        self.possible_objects = possible_objects
        self.clause = [-get_SAT_variable(implicant_agent, agents, implicant_object, items)]
        for item in self.possible_objects:
            self.clause.append(get_SAT_variable(implied_agent, agents, item, items))

    # def __init__(self, clause, agents):
    #     self.clause = clause
    #     self.implicant_agent = None
    #     self.implicant_object = None
    #     self.implied_agent = None
    #     self.possible_objects = None
    #     implicant = []
    #     implied = []
    #     for lit in clause:
    #         if lit < 0:
    #             implicant.append(lit)
    #         else:
    #             implied.append(lit)
    #     if len(lit) != 1:
    #         return
    #     (self.implicant_agent,self.implicant_object) = get_alloc_variable(implicant[0],agents)
    #     self.possible_objects = []
    #     for lit in implied:
    #         (agent,item) = get_alloc_variable(lit,agents)
    #         if self.implied_agent == None:
    #             self.implied_agent = agent
    #         elif agent != self.implied_agent:
    #             return 
    #         self.possible_objects.append(item)

    def get_concerned_agents(self):
        return [self.implicant_agent,self.implied_agent]
        
    def get_concerned_objects(self):
        return [self.implicant_object]+self.possible_objects

    def text_translation(self):
        res = "If agent "+str(self.implicant_agent)+" is assigned object "+str(self.implicant_object)+" then, to avoid local envy, her neighbor agent "+\
            str(self.implied_agent)+" must be assigned to an object that agent "+str(self.implied_agent)+" prefers to "+str(self.implicant_object)+\
                " and that agent "+str(self.implicant_agent)+" likes less than "+str(self.implicant_object)
        if (len(self.possible_objects) == 0):
            return res+". However, such an object does not exist according to their preferences, a contradiction."
        res += ", i.e., one object among objects: "
        for object in self.possible_objects:
            res += object + ", "
        return res[:-2]
    
    def clause_meaning(self):
        return "lef("+str(self.implicant_agent)+": "+str(self.implicant_object)+")->("+str(self.implied_agent)+": "+str(self.possible_objects)+")"

    

def recognize_clause(clause, agents, items):
    if len(clause) == 2 and clause[0] < 0 and clause[1] < 0:
        return AtMostClause(clause,agents)
    all_positive = True
    for lit in clause:
        if lit < 0:
            all_positive = False
    if all_positive:
        return AtLeastClause(clause,agents,items)
    return LefClause(clause, agents)


