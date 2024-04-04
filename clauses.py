class Clause:
    def text_translation(self):
        pass

class AtLeastClause(Clause):
    def __init__(self, orientation, element):
        self.orientation = None
        self.elements_to_match = None
        if orientation == "agent":
            self.orientation = "agent"
            self.elements_to_match = "object"
        elif orientation == "object":
            self.orientation = "object"
            self.elements_to_match = "agent"
        self.central_element = element

    def text_translation(self):
        return self.orientation+" "+str(self.central_element)+" should be matched with at least one "+self.elements_to_match
    

class AtMostClause(Clause):
    def __init__(self, orientation, element_to_not_share, competing_element1, competing_element2):
        self.orientation = None
        self.elements_to_match = None
        if orientation == "agent":
            self.orientation = "agent"
            self.elements_to_match = "objects"
        elif orientation == "object":
            self.orientation = "object"
            self.elements_to_match = "agents"
        self.element_to_not_share = element_to_not_share
        self.competing_element1 = competing_element1
        self.competing_element2 = competing_element2

    def text_translation(self):
        return "However, "+self.orientation+" "+str(self.element_to_not_share)+" cannot be matched with both "+str(self.elements_to_match)+\
            " "+str(self.competing_element1)+" and "+str(self.competing_element2)+", a contradiction."
    
class LefClause(Clause):
    def __init__(self, implicant_agent, implicant_object, implied_agent, possible_objects):
        self.implicant_agent = implicant_agent
        self.implicant_object = implicant_object
        self.implied_agent = implied_agent
        self.possible_objects = possible_objects

    def text_translation(self):
        res = "If agent "+str(self.implicant_agent)+" is assigned object "+str(self.implicant_object)+" then, to avoid local envy, her neighbor agent "+\
            str(self.implied_agent)+" must be assigned to an object that agent "+str(self.implied_agent)+" prefers to "+str(self.implicant_object)+\
                " and that agent "+str(self.implicant_agent)+" likes less than "+str(self.implicant_object)
        if (len(self.possible_objects) == 0):
            return res+" However, such an object does not exist according to their preferences, a contradiction."
        res += ", i.e., one object among objects: "
        for object in self.possible_objects:
            res += object + ", "
        return res[:-2]
    
