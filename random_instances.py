import sys
import random
import networkx as nx
import os
import argparse



def print_social_network(graph,location,filename):    
    soc_file = open(location + ".soc",'w')
    for node in graph.nodes():
        print("A"+str(node+1),file = soc_file)
    print("#",file = soc_file)
    for edge in graph.edges():
        print(f"A{str(edge[0]+1)} A{str(edge[1]+1)}",file = soc_file)
    soc_file.close()

def usage():
    sys.exit("Usage: python3 random_instances.py nb_agents sample_size model [params...] where\n\tnb_agents is the number of agents/objects\n\tsample_size is the number of generated instances\n\tmodel is the generation model: er for Erdos-Renyi, line for lines, ba for Barabasi-Albert, ws for Watts-Strogatz\n\tparams are optional parameters, e.g. the probability for ER, the attachment value for BA, the number of joint nodes and the probability of rewiring for WS")


def print_preferences(location,n):
    pref_file = open(location + ".pref", 'w')
    objects = ["o" + str(i) for i in range(1,n+1)]
    for i in range(n):
        objects_bis = objects.copy()
        random.shuffle(objects_bis)
        pref_string = "A"+str(i+1)+":"+objects_bis.pop()
        for obj in objects_bis:
            pref_string += " "+obj
        print(pref_string, file = pref_file)
    pref_file.close()


def generate_graph(model,n,n_args):
    graph = None
    if model == "er":
        if n_args < 5:
            usage()
        proba = float(sys.argv[4])
        graph = nx.erdos_renyi_graph(n,proba)
    elif model == "LINE":
        graph = nx.path_graph(n)
    elif model == "ba":
        if n_args < 5:
            usage()
        attachment = int(sys.argv[4])
        graph=nx.barabasi_albert_graph(n,attachment)
    elif model == "ws":
        if n_args < 6:
            usage()
        joint = int(sys.argv[4])
        rewiring = float(sys.argv[5])
        graph = nx.watts_strogatz_graph(n,joint,rewiring)
    return graph

def main(): 
    parser = argparse.ArgumentParser()
    parser.add_argument("nb_agents", type=int, help="specify the number of agents")
    parser.add_argument("sample_size", type=int, help="specify the number of generated instances")
    parser.add_argument("model", help="specify the statistical model for graph generation")
    parser.add_argument("parameter", type=float, help="specify the statistical model for graph generation")
    args = parser.parse_args()
    n_args = len(sys.argv)
    path = os.getcwd()
    for i in range(args.sample_size):
        filename = args.model+"/test_par"+str(args.parameter)+"_"+str(args.nb_agents)+"ag_"+str(i+1)
        graph = generate_graph(args.model,args.nb_agents,n_args)
        location = os.path.join(path, "tests/random/"+filename)
        print_social_network(graph,location,filename)
        print_preferences(location,args.nb_agents)


if __name__ == "__main__":
    main()

