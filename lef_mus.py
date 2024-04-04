import sys
import argparse
import os
from utils import *
from random_instances import *

from pysat.solvers import Solver
from pysat.examples.rc2 import RC2
from pysat.examples.musx import MUSX
from pysat.examples.optux import OptUx
from pysat.examples.mcsls import MCSls
from pysat.formula import WCNF



class LefMus:
    def __init__(self, location):
        self.soc_file = open(location + ".soc",'r')
        self.pref_file = open(location + ".pref",'r')
        self.preferences = dict()
        self.agents = []
        self.pref_parser()
        self.agents, self.social, self.number_of_edges = parse_tgf(self.soc_file)
        self.items = get_objects_from_preferences(self.agents,self.preferences)
        self.SAT_variables_meaning = dict()
        self.get_variable_meaning()
        self.redundant = False
        self.clauses = []
        self.minimum_muses = []
        self.all_muses = []
        self.pref_file.close()
        self.soc_file.close()
    

    def pref_parser(self):
        preferences_lines = self.pref_file.read().splitlines()
        for pref_line in preferences_lines:
            agent, pref_list = parse_preference_line(pref_line)
            self.preferences[agent] = pref_list

    def get_variable_meaning(self):
        for agent in self.agents:
            for item in self.items:
                #print(f"alloc({agent},{item}) = {get_SAT_variable(agent, agents, item, items)}")
                self.SAT_variables_meaning[get_SAT_variable(agent, self.agents, item, self.items)] = f"alloc({agent},{item})"

    def get_agents(self):
        return self.agents

    def get_items(self):
        return self.items

    def get_preferences(self):
        return self.preferences    

    def get_clauses(self):
        return self.clauses    
    
    def get_nb_clauses(self):
        return len(self.clauses)
    
    def get_minimum_muses(self):
        return self.minimum_muses
    
    def get_all_muses(self):
        return self.all_muses

    def sat_encoding(self, redundant):
        if len(self.clauses) > 0: 
            if self.redundant == redundant:
                return
            else:
                self.clauses.clear()
                self.minimum_muses.clear()
                self.all_muses.clear()
        self.redundant = redundant
        for agent in self.agents:
            self.clauses.append(at_least_one_item(agent, self.agents, self.items)) # clause \phi_{alloc}^{\geq 1}(i)
            other_agents = [other_agent for other_agent in self.agents if other_agent > agent]
            for item in self.items:
                for other_agent in other_agents:
                    self.clauses.append(agents_do_not_share_items(agent, other_agent, self.agents, item, self.items)) # clause \phi_{alloc}^O(o,i,j)
        
        if redundant:
            for item in self.items:
                self.clauses.append(at_least_one_agent(item, self.agents, self.items))
                other_items = [other_item for other_item in self.items if other_item > item]
                for agent in self.agents:
                    for other_item in other_items:
                        self.clauses.append(items_do_not_share_agents(agent, self.agents, item, other_item, self.items)) # clause \phi_{alloc}^O(o,i,j)

            
        for edge in self.social:
            for item in self.items:
                clause = [-get_SAT_variable(edge[0], self.agents, item, self.items)]

                other_items = self.items.copy()
                other_items.remove(item)
                for other_item in other_items:
                    if agent_prefers(self.preferences, edge[1], other_item, item) and agent_prefers(self.preferences, edge[0], item, other_item):
                        clause.append(get_SAT_variable(edge[1], self.agents, other_item, self.items))

                #print(f"--- phi_LEF({edge[0]},{edge[1]},{item}) = {clause} = {clause_as_text(clause,SAT_variables_meaning)}")
                self.clauses.append(clause) # clause \phi_{lef}(i,j,o)
        
                # reverse direction of the edge
                clause = [-get_SAT_variable(edge[1], self.agents, item, self.items)]

                for other_item in other_items:
                    if agent_prefers(self.preferences, edge[0], other_item, item) and agent_prefers(self.preferences, edge[1], item, other_item):
                        clause.append(get_SAT_variable(edge[0], self.agents, other_item, self.items))

                #print(f"--- phi_LEF({edge[1]},{edge[0]},{item}) = {clause} = {clause_as_text(clause,SAT_variables_meaning)}")
                self.clauses.append(clause) # clause \phi_{lef}(i,j,o)



    def compute_mus(self,mus,enum,enumall,verbose=False):
        if len(self.clauses) == 0 or len(self.minimum_muses) > 0:
            return True, None
        s = Solver(name='g4', bootstrap_with=self.clauses)
        if s.solve():
            model = s.get_model()
            s.delete()
            return True, decode_model_into_alloc(model,self.SAT_variables_meaning)      
        elif mus:
            s.delete()
            cnf = WCNF()
            for clause in self.clauses:
                cnf.append(clause, weight=1)
            #print(cnf)
            #musx = MUSX(cnf,verbosity=0)
            with OptUx(cnf) as optux:
                MUS = optux.compute()
                if verbose:
                    print("after optux compute")
            if MUS == None:
                return True, None 
            else:
                res = []
                for index in MUS:
                    res.append(clause_as_text(self.clauses[index-1],self.SAT_variables_meaning))
            if enum: 
                nb_mus=0
                min_cost=0
                min = True
                with OptUx(cnf) as optux:
                    if verbose:
                        print("enumeration...")
                    for mus in optux.enumerate():
                        if enum and min_cost !=0 and min_cost!=optux.cost:
                            min = False
                            break
                        nb_mus+=1
                        min_cost = optux.cost
                        if (min):
                            self.minimum_muses.append((mus,optux.cost))
                            self.all_muses.append((mus,optux.cost))
                        elif (enumall):
                            self.all_muses.append((mus,optux.cost))
            return False, res #clause_as_text(self.clauses[self.minimum_muses[0][0]-1],self.SAT_variables_meaning)
        else:
            return False, None

    



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("nb_agents", type=int, help="specify the number of agents")
    parser.add_argument("sample_size", type=int, help="specify the number of generated instances")
    parser.add_argument("model", help="specify the statistical model for graph generation")
    parser.add_argument("parameter", type=float, help="specify the statistical model for graph generation")
    parser.add_argument("--verbose", action="store_true", help="print the details of MUSes ")
    parser.add_argument("--mus", action="store_true", help="if set compute a mus instead of the allocation (only works if formula is unsat)")
    parser.add_argument("--enummin", action="store_true", help="enumerate the min MUSes")
    parser.add_argument("--enumall", action="store_true", help="enumerate all the MUSes")
    args = parser.parse_args()
    n_args = len(sys.argv)
    path = os.getcwd()
    nb_false_instances = 0

    nb_clauses = 0
    nb_clauses_redundant = 0

    nb_mus = 0
    nb_min_mus = 0
    min_mus_size = 0
    max_mus_size = 0

    nb_mus_redundant = 0
    nb_min_mus_redundant = 0
    min_mus_size_redundant = 0
    max_mus_size_redundant = 0
    for i in range(args.sample_size):
        print("\ncounter: "+str(i+1))
        filename = args.model+"/test_par"+str(args.parameter)+"_"+str(args.nb_agents)+"ag_"+str(i+1)
        location = os.path.join(path, "tests/random/"+filename)
        if (not os.path.exists(location+".soc")):
            graph = generate_graph(args.model,args.nb_agents,n_args)
            print_social_network(graph,location,filename)
        if (not os.path.exists(location+".pref")):
            print_preferences(location,args.nb_agents)
        encoding = LefMus(location)
        encoding.sat_encoding(False)
        if args.verbose:
            print("basic encoding done")
        #print("number of clauses: "+str(encoding.get_nb_clauses()))
        nb_clauses += encoding.get_nb_clauses()
        #print(encoding.compute_mus(True,False)) 
        if not encoding.compute_mus(args.mus,args.enummin,args.enumall,args.verbose)[0]:
            nb_false_instances += 1
            nb_mus += len(encoding.get_all_muses())
            nb_min_mus += len(encoding.get_minimum_muses())
            if (len(encoding.get_minimum_muses()) > 0):
                min_mus_size += encoding.get_minimum_muses()[0][1]
                max_mus_size += encoding.get_all_muses()[-1][1]     
        #if (len(encoding.get_minimum_muses()) > 0):
            #print(encoding.get_minimum_muses())
            #print("number of minimum MUSes: "+str(len(encoding.get_minimum_muses())))
            #print("total number of MUSes: "+str(len(encoding.get_all_muses())))
            #print("minimum size of a MUS: "+str(encoding.get_minimum_muses()[0][1]))
            #print("maximum size of a MUS: "+str(encoding.get_all_muses()[-1][1]))
        encoding.sat_encoding(True)
        if args.verbose:
            print("redundant encoding done")
        #print("number of clauses: "+str(encoding.get_nb_clauses()))
        nb_clauses_redundant += encoding.get_nb_clauses()
        #print(encoding.compute_mus(True,False))   
        if not encoding.compute_mus(args.mus,args.enummin,args.enumall,args.verbose)[0]:
            nb_mus_redundant += len(encoding.get_all_muses())
            nb_min_mus_redundant += len(encoding.get_minimum_muses())
            if (len(encoding.get_minimum_muses()) > 0):
                min_mus_size_redundant += encoding.get_minimum_muses()[0][1]
                max_mus_size_redundant += encoding.get_all_muses()[-1][1]      
        #if (len(encoding.get_minimum_muses()) > 0):
            #print(encoding.get_minimum_muses())
            #print("number of minimum MUSes: "+str(len(encoding.get_minimum_muses())))
            #print("total number of MUSes: "+str(len(encoding.get_all_muses())))
            #print("minimum size of a MUS: "+str(encoding.get_minimum_muses()[0][1]))
            #print("maximum size of a MUS: "+str(encoding.get_all_muses()[-1][1]))
        #print(redundant_encoding.get_nb_clauses())
        #print(redundant_encoding.get_mus(False,False))
                
    output_name = "results_"+str(args.model)+str(args.parameter)
    output_location = os.path.join(path, "tests/random/"+output_name)
    output_file = open(output_location + ".txt",'a')
    output_file.write("\n\n===================================")
    output_file.write("\nn = "+str(args.nb_agents))
    output_file.write("\nsample size = "+str(args.sample_size))
    output_file.write("\nnb false instances = "+str(nb_false_instances))
    output_file.write("\n===================================")
    output_file.write("\n----------BASIC ENCODING----------")
    output_file.write("\naverage number of clauses: "+str(nb_clauses / args.sample_size))
    output_file.write("\naverage number of minimum MUSes: "+str(nb_min_mus / nb_false_instances))
    output_file.write("\naverage total number of MUSes: "+str(nb_mus / nb_false_instances))
    output_file.write("\naverage minimum size of a MUS: "+str(min_mus_size / nb_false_instances))
    output_file.write("\naverage maximum size of a MUS: "+str(max_mus_size / nb_false_instances))
    output_file.write("\n----------REDUNDANT ENCODING----------")
    output_file.write("\naverage number of clauses: "+str(nb_clauses_redundant / args.sample_size))
    output_file.write("\naverage number of minimum MUSes: "+str(nb_min_mus_redundant / nb_false_instances))
    output_file.write("\naverage total number of MUSes: "+str(nb_mus_redundant / nb_false_instances))
    output_file.write("\naverage minimum size of a MUS: "+str(min_mus_size_redundant / nb_false_instances))
    output_file.write("\naverage maximum size of a MUS: "+str(max_mus_size_redundant / nb_false_instances))
    output_file.close()



if __name__ == "__main__":
    main()





