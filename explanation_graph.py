from graphviz import Digraph
import sys
from clauses import *
from utils import *

class ClauseNode:
    def __init__(self, node_type):
        self.node_type = node_type
        # node types are: top, bottom, var, at-least-one-object-per-agent, at-most-one-agent-per-object, lef-clause
        self.literals = []
        self.clause_meaning = None

    def set_clause_meaning(self, meaning):
        self.clause_meaning = meaning

    def get_clause_meaning(self):
        return self.clause_meaning

    def get_node_type(self):
        return self.node_type

    def get_literals(self):
        return self.literals

    def add_literal(self, literal):
        self.literals.append(literal)

    def content(self):
        if self.node_type in ["top", "bottom"]:
            return self.node_type
        
        string_result = ""
        if self.get_clause_meaning() != None:
            string_result = self.get_clause_meaning() + " : "
        for literal in self.literals[:-1]:
            string_result += literal + ","
        string_result += self.literals[-1]
        return string_result
        
    def to_string(self):
        if self.node_type == "top":
            return "top"
        if self.node_type == "bottom":
            return "bottom"

        return f"{self.node_type} : [" + self.content() + "]"


    def __eq__(self, other):
        if not isinstance(other, ClauseNode):
            # don't attempt to compare against unrelated types
            return NotImplemented

        if self.node_type != other.node_type:
            return False

        for literal in self.literals:
            if literal not in other.literals:
                return False
        for literal in other.literals:
            if literal not in self.literals:
                return False
        
        return True

    def get_node_id_in_graph(self, graph):
        return graph.get_nodes().index(self)

class ExplanationGraph:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.activations = []

    def init_from_list_of_clauses(self, list_clauses):
        # top, bottom, var, at-least-one-object-per-agent, at-most-one-agent-per-object, lef-clause

        top = ClauseNode("top")
        bottom = ClauseNode("bottom")
        self.nodes.append(top)
        self.nodes.append(bottom)
        
        for clause in list_clauses:
            if isinstance(clause, AtLeastClause):
                if clause.orientation == "agent":
                    node_type = "at-least-one-object-per-agent"
                else:
                    sys.exit("Redundant encoding not supported (1)")
                node = ClauseNode(node_type)

            elif isinstance(clause, AtMostClause):
                if clause.orientation == "object":
                    node_type = "at-most-one-agent-per-object"
                else:
                    sys.exit("Redundant encoding not supported (2)")
                node  = ClauseNode(node_type)
            elif isinstance(clause, LefClause):
                node = ClauseNode("lef-clause")
            else:
                sys.exit("Unknown type of clause")
            for literal in clause.get_translated_clause():
                node.add_literal(literal)
            node.set_clause_meaning(clause.get_clause_meaning())
            self.nodes.append(node)

        variables = set()
        for node in self.nodes:
            for literal in node.get_literals():
                if literal[0] == "-":
                    variables.add(literal[1:])
                else:
                    variables.add(literal)
        for variable in variables:
            node = ClauseNode("var")
            node.add_literal(variable)
            self.nodes.append(node)

        for node1 in self.get_nodes():
            if node1.get_node_type() == "at-least-one-object-per-agent":
                self.add_edge(top, node1)
            if node1.get_node_type() == "at-most-one-agent-per-object":
                self.add_edge(node1, bottom)
            if node1.get_node_type() == "lef-clause" and len(node1.get_literals()) == 1:
                self.add_edge(node1, bottom)
            for node2 in self.get_nodes():
                if node1.get_node_type() == "at-least-one-object-per-agent" and node2.get_node_type() == "var":
                    if node2.get_literals()[0] in node1.get_literals():
                        self.add_edge(node1,node2)
                if node1.get_node_type() == "var" and node2.get_node_type() == "at-most-one-agent-per-object":
                    literal = node1.get_literals()[0]
                    if "-" + literal in node2.get_literals():
                        self.add_edge(node1, node2)
                if node1.get_node_type() == "lef-clause" and node2.get_node_type() == "var":
                    if node2.get_literals()[0] in node1.get_literals():
                        self.add_edge(node1, node2)
                if node1.get_node_type() == "var" and node2.get_node_type() == "lef-clause":
                    literal = node1.get_literals()[0]
                    if "-" + literal in node2.get_literals():
                        self.add_edge(node1, node2)

        
            
        
    def get_edges(self):
        return self.edges

    def get_nodes(self):
        return self.nodes

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.append(node)

    def add_edge(self, node_from, node_to):
        self.edges.append([node_from, node_to])

    def get_clause_nodes(self):
        clause_nodes = []
        for node in self.nodes:
            if node.get_node_type() in ["at-least-one-object-per-agent", "at-most-one-agent-per-object", "lef-clause"]:
                clause_nodes.append(node)
        return clause_nodes
        
    def get_predecessors(self, node):
        predecessors = []
        for edge in self.edges:
            if edge[1] == node:
                predecessors.append(edge[0])
        return predecessors

    def get_successors(self, node):
        successors = []
        for edge in self.edges:
            if edge[0] == node:
                successors.append(edge[1])
        return successors

    def to_string(self):
        str_result = ""
        for node in self.nodes:
            str_result += f"node({node.to_string()}).\n"
        for edge in self.edges:
            str_result += f"edge({edge[0].to_string()},{edge[1].to_string()}).\n"
        return str_result

    def to_dot(self):
        str_result = "digraph G {\n"
        for node in self.nodes:
            str_result += "n" + str(node.get_node_id_in_graph(self)) + " "
            if node.get_node_type() in ["top", "bottom", "var"]:
                str_result += f"[shape=ellipse, label=\"{node.content()}\"];\n"
            else:
                str_result += f"[shape=box, label=\"{node.content()}\"];\n"
        for edge in self.edges:
            str_result += "n" + str(edge[0].get_node_id_in_graph(self)) + " -> " + "n" + str(edge[1].get_node_id_in_graph(self)) + " ;\n"
        str_result += "}"
        return str_result

    def to_dot_with_activation(self, activation):
        str_result = "digraph G {\n"
        for node in self.nodes:
            index = node.get_node_id_in_graph(self)
            str_result += "n" + str(node.get_node_id_in_graph(self)) + " "
            if node.get_node_type() in ["top", "bottom", "var"]:
                str_result += f"[shape=ellipse, label=\"{node.content()}\""
            else:
                str_result += f"[shape=box, label=\"{node.content()}\""

            if activation[index]:
                str_result += ", style=filled, fillcolor=green"

            str_result += "];\n"
        for edge in self.edges:
            str_result += "n" + str(edge[0].get_node_id_in_graph(self)) + " -> " + "n" + str(edge[1].get_node_id_in_graph(self)) + " ;\n"
        str_result += "}"
        return str_result

    def to_graphviz(self, activation, act_index):
        graph = Digraph()

        for node in self.nodes:
            index = node.get_node_id_in_graph(self)
            node_name = "n" + str(node.get_node_id_in_graph(self))

            if node.get_node_type() in ["top", "bottom", "var"]:
                if activation[0][index]:
                    graph.node(name=node_name, shape="ellipse", label=f"{node.content()}", style="filled", fillcolor="green")
                else:
                    graph.node(name=node_name, shape="ellipse", label=f"{node.content()}")
            else:
                if activation[0][index]:
                    graph.node(name=node_name, shape="box", label=f"{node.content()}", style="filled", fillcolor="green")
                else:
                    graph.node(name=node_name, shape="box", label=f"{node.content()}")

        for edge in self.edges:
            graph.edge("n" + str(edge[0].get_node_id_in_graph(self)), "n" + str(edge[1].get_node_id_in_graph(self)))

        graph.render(filename=f"Activation-{str(act_index).zfill(3)}", cleanup=True, view=False, format='png')

    def get_successor_activations(self, activation):
        successors = []
        successor = activation[0].copy()
        hasActivatedClause = False
        indexes = []
        for node in self.get_clause_nodes():
            index = node.get_node_id_in_graph(self)
            if not activation[0][index]:
                predecessors = self.get_predecessors(node)
                all_pred_activated = True
                for predecessor in predecessors:
                    pred_index = predecessor.get_node_id_in_graph(self)
                    if not activation[0][pred_index]:
                        all_pred_activated = False
                if all_pred_activated:
                    successor[index] = True
                    hasActivatedClause = True
                    indexes.append(index)
        if not hasActivatedClause:
            return []   
        successors.append((successor,activation[1]+1))      
        new_successors = self.get_all_successors(indexes,0,successor,[],activation[1]+2) 
        return successors + new_successors
    
    def get_all_successors(self, indexes, index, successor, all_successors, depth):
        if index == len(indexes):
            all_successors.append((successor,depth))
            return all_successors
        successor_nodes = self.get_successors(self.nodes[indexes[index]])
        for successor_node in successor_nodes:
            successor_index = successor_node.get_node_id_in_graph(self)
            new_successor = successor.copy()
            new_successor[successor_index] = True
            all_successors = self.get_all_successors(indexes,index+1,new_successor,all_successors,depth)
        return all_successors

    
    def activate(self, save=False):
        new_activation = []
        for node in self.nodes:
            if node.get_node_type() ==  "top":
                new_activation.append(True)
            else:
                new_activation.append(False)
            
        next_activations = [(new_activation,0)]
        while next_activations != []:
            next_activation = next_activations.pop(0)
            if next_activation not in self.activations:
                self.activations.append(next_activation)
                successor_activations = self.get_successor_activations(next_activation)
                next_activations = successor_activations + next_activations

        if save:
            act_index = 0
            for activation in self.activations:
                self.to_graphviz(activation, act_index)

                #print("-------------")
                #print(f"Activation-{str(act_index).zfill(3)}")
                #print(activation)
                #for index in range(len(activation)):
                #    if activation[index]:
                #        print(f"index: {index} - node: {self.nodes[index].content()}")
                #print("-------------\n")

                act_index += 1

        return self.activations

    