import os
import math

from utils import *
from lef_mus import *
from explanation_graph import *


def min_metric_muses(muses, metric):
    res = []
    min_metric = math.inf
    max_metric = 0
    average_metric = 0
    for mus in muses:
        value_metric = metric(mus) 
        average_metric += value_metric       
        if value_metric == min_metric:
            res.append(mus)      
        elif value_metric < min_metric:
            res.clear()
            res.append(mus)
            min_metric = value_metric
        if value_metric > max_metric:
            max_metric = value_metric
    # print("min: "+str(min_metric))
    # print("average: "+str(average_metric/len(muses)))
    # print("max: "+str(max_metric))
    return (res,(min_metric,average_metric/len(muses),max_metric))

def agents_metric(mus):
    concerned_agents = []
    for clause in mus:
        concerned_agents = list(set(concerned_agents) | set(clause.get_concerned_agents()))       
    return len(concerned_agents)

def variables_metric(mus):
    vars = []
    for clause in mus:
        vars = list(set(vars) | set(clause.get_variables()))  
    return len(vars)

def breadth_metric(mus):
    graph = ExplanationGraph()
    graph.init_from_list_of_clauses(mus)
    activations = graph.activate()
    count = 0
    for activation in activations:
        for index in range(len(activation)):
            if graph.nodes[index].node_type == "bottom":
                if activation[0][index]:
                    count += 1
                break
    return count

def length_metric(mus):
    graph = ExplanationGraph()
    graph.init_from_list_of_clauses(mus)
    #print(graph.activate())
    return len(graph.activate())

def depth_metric(mus):
    graph = ExplanationGraph()
    graph.init_from_list_of_clauses(mus)
    activations = graph.activate()
    max = 0
    for activation in activations:
        for index in range(len(activation)):
            if graph.nodes[index].node_type == "bottom":
                if activation[0][index]:
                    if activation[1] > max:
                        max = activation[1]
                break
    return max
            
def get_graph_metric(muses):
    mus = muses[0]
    #for mus in muses:
    print("mus: ")
    print(mus)
    graph = ExplanationGraph()
    graph.init_from_list_of_clauses(mus)
    print("graph: ")
    print(graph.to_string())
    print("activation: ")
    print(graph.activate())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("nb_agents", type=int, help="specify the number of agents")
    parser.add_argument("sample_size", type=int, help="specify the number of generated instances")
    parser.add_argument("model", help="specify the statistical model for graph generation")
    parser.add_argument("parameter", type=float, help="specify the statistical model for graph generation")
    parser.add_argument("--verbose", action="store_true", help="print the details of MUSes ")
    parser.add_argument("--write", action="store_true", help="write in the output file")
    parser.add_argument("--agents", action="store_true", help="focus on min MUSes minimizing the number of concerned agents")
    args = parser.parse_args()
    n_args = len(sys.argv)
    path = os.getcwd()

    counter = 0
    last_instance = False

    nb_min_mus = 0
    nb_min_agents_min_mus = 0
    nb_min_var_min_mus = 0
    nb_min_length_min_mus = 0
    nb_min_breadth_min_mus = 0
    nb_min_depth_min_mus = 0

    average_agents_min_mus = 0
    average_var_min_mus = 0
    average_length_min_mus = 0
    average_breadth_min_mus = 0
    average_depth_min_mus = 0

    min_agents_min_mus = 0
    min_var_min_mus = 0
    min_length_min_mus = 0
    min_breadth_min_mus = 0
    min_depth_min_mus = 0

    max_agents_min_mus = 0
    max_var_min_mus = 0
    max_length_min_mus = 0
    max_breadth_min_mus = 0
    max_depth_min_mus = 0

    nb_min_mus_redundant = 0
    nb_min_agents_min_mus_redundant = 0
    nb_min_var_min_mus_redundant = 0
    nb_min_length_min_mus_redundant = 0
    nb_min_breadth_min_mus_redundant = 0
    nb_min_depth_min_mus_redundant = 0

    average_agents_min_mus_redundant = 0
    average_var_min_mus_redundant = 0
    average_length_min_mus_redundant = 0
    average_breadth_min_mus_redundant = 0
    average_depth_min_mus_redundant = 0

    min_agents_min_mus_redundant = 0
    min_var_min_mus_redundant = 0
    min_length_min_mus_redundant = 0
    min_breadth_min_mus_redundant = 0
    min_depth_min_mus_redundant = 0

    max_agents_min_mus_redundant = 0
    max_var_min_mus_redundant = 0
    max_length_min_mus_redundant = 0
    max_breadth_min_mus_redundant = 0
    max_depth_min_mus_redundant = 0

    global_average_var_chosen = 0
    global_average_length_chosen = 0
    global_average_breadth_chosen = 0
    global_average_depth_chosen = 0

    global_average_var_chosen_redundant = 0
    global_average_length_chosen_redundant = 0
    global_average_breadth_chosen_redundant = 0
    global_average_depth_chosen_redundant = 0

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
            (min_agents_min_muses,(min_agents,average_agents,max_agents)) = min_metric_muses(min_muses,agents_metric)
            nb_min_agents_min_mus += len(min_agents_min_muses)
            min_agents_min_mus += min_agents
            average_agents_min_mus += average_agents
            max_agents_min_mus += max_agents

            if args.agents:
                chosen_muses = min_agents_min_muses
                average_var_chosen = 0
                average_length_chosen = 0
                average_breadth_chosen = 0
                average_depth_chosen = 0
                for mus in chosen_muses:
                    average_var_chosen += variables_metric(mus)
                    average_length_chosen += length_metric(mus)
                    average_breadth_chosen += breadth_metric(mus)
                    average_depth_chosen += depth_metric(mus)
                global_average_var_chosen += average_var_chosen / len(chosen_muses)
                global_average_length_chosen += average_length_chosen / len(chosen_muses)
                global_average_breadth_chosen += average_breadth_chosen / len(chosen_muses)
                global_average_depth_chosen += average_depth_chosen / len(chosen_muses)
            else:
                # print(str(len(min_agents_min_muses))+" min agents min muses:")
                # print(min_agents_min_muses)
                (min_var_min_muses,(min_var,average_var,max_var)) = min_metric_muses(min_muses,variables_metric)
                nb_min_var_min_mus +=  len(min_var_min_muses)
                min_var_min_mus += min_var
                average_var_min_mus += average_var
                max_var_min_mus += max_var
                #print(str(len(min_var_min_muses))+" min variables min muses:")
                #print(min_var_min_muses)
                (min_length_min_muses,(min_length,average_length,max_length)) = min_metric_muses(min_muses,length_metric)
                nb_min_length_min_mus +=  len(min_length_min_muses)
                min_length_min_mus += min_length
                average_length_min_mus += average_length
                max_length_min_mus += max_length
                #print(str(len(min_length_min_muses))+" min length min muses:")
                #print(min_length_min_muses)
                (min_breadth_min_muses,(min_breadth,average_breadth,max_breadth)) = min_metric_muses(min_muses,breadth_metric)
                nb_min_breadth_min_mus +=  len(min_breadth_min_muses)
                min_breadth_min_mus += min_breadth
                average_breadth_min_mus += average_breadth
                max_breadth_min_mus += max_breadth
                #print(str(len(min_breadth_min_muses))+" min breadth min muses:")
                #print(min_breadth_min_muses)
                (min_depth_min_muses,(min_depth,average_depth,max_depth)) = min_metric_muses(min_muses,depth_metric)
                nb_min_depth_min_mus +=  len(min_depth_min_muses)
                min_depth_min_mus += min_depth
                average_depth_min_mus += average_depth
                max_depth_min_mus += max_depth
                #print(str(len(min_depth_min_muses))+" min depth min muses:")
                #print(min_depth_min_muses)
                #print(min_muses)
                #get_graph_metric(min_muses)
        else:
            last_instance = True
            continue
        
        # print()
        # print("redundant")
        # print()
        
        encoding.sat_encoding(True)

        if args.verbose:
            print("redundant encoding done")

        if not encoding.compute_mus(True,True,False,args.verbose)[0]:
            min_muses_redundant = encoding.get_minimum_muses()
            nb_min_mus_redundant += len(min_muses_redundant) 
            #print(str(len(min_muses))+" min muses:")
            #print(min_muses)
            (min_agents_min_muses_redundant,(min_agents,average_agents,max_agents)) = min_metric_muses(min_muses_redundant,agents_metric)
            nb_min_agents_min_mus_redundant += len(min_agents_min_muses_redundant)
            min_agents_min_mus_redundant += min_agents
            average_agents_min_mus_redundant += average_agents
            max_agents_min_mus_redundant += max_agents
            #print(str(len(min_agents_min_muses_redundant))+" min agents min muses:")
            #print(min_agents_min_muses_redundant)

            if args.agents:
                chosen_muses_redundant = min_agents_min_muses_redundant
                average_var_chosen_redundant = 0
                average_length_chosen_redundant = 0
                average_breadth_chosen_redundant = 0
                average_depth_chosen_redundant = 0
                for mus in chosen_muses_redundant:
                    average_var_chosen_redundant += variables_metric(mus)
                    average_length_chosen_redundant += length_metric(mus)
                    average_breadth_chosen_redundant += breadth_metric(mus)
                    average_depth_chosen_redundant += depth_metric(mus)
                global_average_var_chosen_redundant += average_var_chosen_redundant / len(chosen_muses_redundant)
                global_average_length_chosen_redundant += average_length_chosen_redundant / len(chosen_muses_redundant)
                global_average_breadth_chosen_redundant += average_breadth_chosen_redundant / len(chosen_muses_redundant)
                global_average_depth_chosen_redundant += average_depth_chosen_redundant / len(chosen_muses_redundant)
            else:
                (min_var_min_muses_redundant,(min_var,average_var,max_var)) = min_metric_muses(min_muses_redundant,variables_metric)
                nb_min_var_min_mus_redundant +=  len(min_var_min_muses_redundant)
                min_var_min_mus_redundant += min_var
                average_var_min_mus_redundant += average_var
                max_var_min_mus_redundant += max_var
                #print(str(len(min_var_min_muses))+" min variables min muses:")
                #print(min_var_min_muses)
                (min_length_min_muses_redundant,(min_length,average_length,max_length)) = min_metric_muses(min_muses_redundant,length_metric)
                nb_min_length_min_mus_redundant +=  len(min_length_min_muses_redundant)
                min_length_min_mus_redundant += min_length
                average_length_min_mus_redundant += average_length
                max_length_min_mus_redundant += max_length
                #print(str(len(min_length_min_muses))+" min length min muses:")
                #print(min_length_min_muses)
                (min_breadth_min_muses_redundant,(min_breadth,average_breadth,max_breadth)) = min_metric_muses(min_muses_redundant,breadth_metric)
                nb_min_breadth_min_mus_redundant +=  len(min_breadth_min_muses_redundant)
                min_breadth_min_mus_redundant += min_breadth
                average_breadth_min_mus_redundant += average_breadth
                max_breadth_min_mus_redundant += max_breadth
                #print(str(len(min_breadth_min_muses))+" min breadth min muses:")
                #print(min_breadth_min_muses)
                (min_depth_min_muses_redundant,(min_depth,average_depth,max_depth)) = min_metric_muses(min_muses_redundant,depth_metric)
                nb_min_depth_min_mus_redundant +=  len(min_depth_min_muses_redundant)
                min_depth_min_mus_redundant += min_depth
                average_depth_min_mus_redundant += average_depth
                max_depth_min_mus_redundant += max_depth
                #print(str(len(min_depth_min_muses))+" min depth min muses:")
                #print(min_depth_min_muses)
                #print(min_muses)
                #get_graph_metric(min_muses_redundant)


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
            if args.agents:
                output_file.write("\naverage number variables in min agents minimum MUSes: "+str(global_average_var_chosen / nb_false_instances))
                output_file.write("\naverage length in min agents minimum MUSes: "+str(global_average_length_chosen / nb_false_instances))
                output_file.write("\naverage breadth in min agents minimum MUSes: "+str(global_average_breadth_chosen / nb_false_instances))
                output_file.write("\naverage depth in min agents minimum MUSes: "+str(global_average_depth_chosen / nb_false_instances))
            else:
                output_file.write("\naverage number of min variables minimum MUSes: "+str(nb_min_var_min_mus / nb_false_instances))
                output_file.write("\naverage number of min length minimum MUSes: "+str(nb_min_length_min_mus / nb_false_instances))
                output_file.write("\naverage number of min breadth minimum MUSes: "+str(nb_min_breadth_min_mus / nb_false_instances))
                output_file.write("\naverage number of min depth minimum MUSes: "+str(nb_min_depth_min_mus / nb_false_instances))
                output_file.write("\n--------------------------------------")
                output_file.write("\n(min, average, max) number of agents in minimum MUSes: ("+str(min_agents_min_mus / nb_false_instances)+\
                                ", "+str(average_agents_min_mus / nb_false_instances)+", "+str(max_agents_min_mus / nb_false_instances)+")")
                output_file.write("\n(min, average, max) number of variables in minimum MUSes: ("+str(min_var_min_mus / nb_false_instances)+\
                                ", "+str(average_var_min_mus / nb_false_instances)+", "+str(max_var_min_mus / nb_false_instances)+")")
                output_file.write("\n(min, average, max) length in minimum MUSes: ("+str(min_length_min_mus / nb_false_instances)+\
                                ", "+str(average_length_min_mus / nb_false_instances)+", "+str(max_length_min_mus / nb_false_instances)+")")
                output_file.write("\n(min, average, max) breadth in minimum MUSes: ("+str(min_breadth_min_mus / nb_false_instances)+\
                                ", "+str(average_breadth_min_mus / nb_false_instances)+", "+str(max_breadth_min_mus / nb_false_instances)+")")
                output_file.write("\n(min, average, max) depth in minimum MUSes: ("+str(min_depth_min_mus / nb_false_instances)+\
                                ", "+str(average_depth_min_mus / nb_false_instances)+", "+str(max_depth_min_mus / nb_false_instances)+")")
        output_file.write("\n----------REDUNDANT ENCODING----------")
        if nb_false_instances > 0:
            output_file.write("\naverage number of minimum MUSes: "+str(nb_min_mus_redundant / nb_false_instances))
            if args.agents: 
                output_file.write("\naverage number variables in min agents minimum MUSes: "+str(global_average_var_chosen_redundant / nb_false_instances))
                output_file.write("\naverage length in min agents minimum MUSes: "+str(global_average_length_chosen_redundant / nb_false_instances))
                output_file.write("\naverage breadth in min agents minimum MUSes: "+str(global_average_breadth_chosen_redundant / nb_false_instances))
                output_file.write("\naverage depth in min agents minimum MUSes: "+str(global_average_depth_chosen_redundant / nb_false_instances))
            else:
                output_file.write("\naverage number of min agents minimum MUSes: "+str(nb_min_agents_min_mus_redundant / nb_false_instances))
                output_file.write("\naverage number of min variables minimum MUSes: "+str(nb_min_var_min_mus_redundant / nb_false_instances))
                output_file.write("\naverage number of min length minimum MUSes: "+str(nb_min_length_min_mus_redundant / nb_false_instances))
                output_file.write("\naverage number of min breadth minimum MUSes: "+str(nb_min_breadth_min_mus_redundant / nb_false_instances))
                output_file.write("\naverage number of min depth minimum MUSes: "+str(nb_min_depth_min_mus_redundant / nb_false_instances))
                output_file.write("\n--------------------------------------")
                output_file.write("\n(min, average, max) number of agents in minimum MUSes: ("+str(min_agents_min_mus_redundant / nb_false_instances)+\
                                ", "+str(average_agents_min_mus_redundant / nb_false_instances)+", "+str(max_agents_min_mus_redundant / nb_false_instances)+")")
                output_file.write("\n(min, average, max) number of variables in minimum MUSes: ("+str(min_var_min_mus_redundant / nb_false_instances)+\
                                ", "+str(average_var_min_mus_redundant / nb_false_instances)+", "+str(max_var_min_mus_redundant / nb_false_instances)+")")
                output_file.write("\n(min, average, max) length in minimum MUSes: ("+str(min_length_min_mus_redundant / nb_false_instances)+\
                                ", "+str(average_length_min_mus_redundant / nb_false_instances)+", "+str(max_length_min_mus_redundant / nb_false_instances)+")")
                output_file.write("\n(min, average, max) breadth in minimum MUSes: ("+str(min_breadth_min_mus_redundant / nb_false_instances)+\
                                ", "+str(average_breadth_min_mus_redundant / nb_false_instances)+", "+str(max_breadth_min_mus_redundant / nb_false_instances)+")")
                output_file.write("\n(min, average, max) depth in minimum MUSes: ("+str(min_depth_min_mus_redundant / nb_false_instances)+\
                                ", "+str(average_depth_min_mus_redundant / nb_false_instances)+", "+str(max_depth_min_mus_redundant / nb_false_instances)+")")



    # output_name = "results_"+str(args.model)+str(args.parameter)
    # output_location = os.path.join(path, "tests/random/"+output_name)
    # output_file = open(output_location + ".txt",'a')
    # output_file.write("\n\n===================================")



if __name__ == "__main__":
    main()