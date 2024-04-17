import os
import math

from utils import *
from lef_mus import *
from explanation_graph_bis import *


def min_agents_muses(muses):
    res = []
    min_agents = math.inf
    for mus in muses:
        concerned_agents = []
        for clause in mus:
            concerned_agents = list(set(concerned_agents) | set(clause.get_concerned_agents()))
        if len(concerned_agents) == min_agents:
            res.append(mus)      
        elif len(concerned_agents) < min_agents:
            res.clear()
            res.append(mus)
            min_agents = len(concerned_agents)
    return res

def min_variables_muses(muses):
    res = []
    min_var = math.inf
    for mus in muses:
        vars = []
        for clause in mus:
            vars = list(set(vars) | set(clause.get_variables()))  
        if len(vars) == min_var:
            res.append(mus)      
        elif len(vars) < min_var:
            res.clear()
            res.append(mus)
            min_var = len(vars)
    return res
            
def get_graph_metric(muses):
    for mus in muses:
        print(mus)
        graph = ExplanationGraphBis()
        graph.init_from_list_of_clauses(mus)
        print(graph.to_string())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("nb_agents", type=int, help="specify the number of agents")
    parser.add_argument("sample_size", type=int, help="specify the number of generated instances")
    parser.add_argument("model", help="specify the statistical model for graph generation")
    parser.add_argument("parameter", type=float, help="specify the statistical model for graph generation")
    parser.add_argument("--verbose", action="store_true", help="print the details of MUSes ")
    parser.add_argument("--write", action="store_true", help="write in the output file")
    args = parser.parse_args()
    n_args = len(sys.argv)
    path = os.getcwd()

    counter = 0
    last_instance = False

    nb_min_mus = 0
    nb_min_agents_min_mus = 0
    nb_min_var_min_mus = 0

    nb_min_mus_redundant = 0
    nb_min_agents_min_mus_redundant = 0
    nb_min_var_min_mus_redundant = 0

    nb_false_instances = 0

    while counter < args.sample_size:
        print("\ncounter: "+str(counter))
        filename = args.model+"/test_par"+str(args.parameter)+"_"+str(args.nb_agents)+"ag_"+str(counter+1)
        location = os.path.join(path, "tests/random/"+filename)
        if (not os.path.exists(location+".soc") or last_instance):
            graph = generate_graph(args.model,args.nb_agents,n_args)
            print_social_network(graph,location,filename)
        if (not os.path.exists(location+".pref") or last_instance):
            print_preferences(location,args.nb_agents)
        encoding = LefMus(location)

        encoding.sat_encoding(False)

        if args.verbose:
            print("basic encoding done")

        if not encoding.compute_mus(True,True,False,args.verbose)[0]:
            last_instance = False
            counter += 1
            nb_false_instances += 1
            min_muses = encoding.get_minimum_muses()
            nb_min_mus += len(min_muses) 
            #print(str(len(min_muses))+" min muses:")
            #print(min_muses)
            min_agents_min_muses = min_agents_muses(min_muses)
            nb_min_agents_min_mus += len(min_agents_min_muses)
            # print(str(len(min_agents_min_muses))+" min agents min muses:")
            # print(min_agents_min_muses)
            min_var_min_muses = min_variables_muses(min_muses)
            nb_min_var_min_mus +=  len(min_var_min_muses)
            #print(str(len(min_var_min_muses))+" min variables min muses:")
            #print(min_var_min_muses)
            #get_graph_metric(min_muses)
        else:
            last_instance = True
            continue


        
        encoding.sat_encoding(True)

        if args.verbose:
            print("redundant encoding done")

        if not encoding.compute_mus(True,True,False,args.verbose)[0]:
            min_muses_redundant = encoding.get_minimum_muses()
            nb_min_mus_redundant += len(min_muses_redundant) 
            #print(str(len(min_muses))+" min muses:")
            #print(min_muses)
            min_agents_min_muses_redundant = min_agents_muses(min_muses_redundant)
            nb_min_agents_min_mus_redundant += len(min_agents_min_muses_redundant)
            # print(str(len(min_agents_min_muses))+" min agents min muses:")
            # print(min_agents_min_muses)
            min_var_min_muses_redundant = min_variables_muses(min_muses_redundant)
            nb_min_var_min_mus_redundant +=  len(min_var_min_muses_redundant)

    if args.write: 
        output_name = "metrics_"+str(args.model)+str(args.parameter)
        output_location = os.path.join(path, "tests/random/"+output_name)
        output_file = open(output_location + ".txt",'a')
        output_file.write("\n\n===================================")
        output_file.write("\nn = "+str(args.nb_agents))
        output_file.write("\nsample size = "+str(args.sample_size))
        output_file.write("\nnb false instances = "+str(nb_false_instances))
        output_file.write("\n----------BASIC ENCODING----------")
        if nb_false_instances > 0:
            output_file.write("\naverage number of minimum MUSes: "+str(nb_min_mus / nb_false_instances))
            output_file.write("\naverage number of min agents minimum MUSes: "+str(nb_min_agents_min_mus / nb_false_instances))
            output_file.write("\naverage number of min variables minimum MUSes: "+str(nb_min_var_min_mus / nb_false_instances))
        output_file.write("\n----------REDUNDANT ENCODING----------")
        if nb_false_instances > 0:
            output_file.write("\naverage number of minimum MUSes: "+str(nb_min_mus_redundant / nb_false_instances))
            output_file.write("\naverage number of min agents minimum MUSes: "+str(nb_min_agents_min_mus_redundant / nb_false_instances))
            output_file.write("\naverage number of min variables minimum MUSes: "+str(nb_min_var_min_mus_redundant / nb_false_instances))



    # output_name = "results_"+str(args.model)+str(args.parameter)
    # output_location = os.path.join(path, "tests/random/"+output_name)
    # output_file = open(output_location + ".txt",'a')
    # output_file.write("\n\n===================================")



if __name__ == "__main__":
    main()