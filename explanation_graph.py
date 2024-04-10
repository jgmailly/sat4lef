from graphviz import Digraph

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
                if activation[index]:
                    graph.node(name=node_name, shape="ellipse", label=f"{node.content()}", style="filled", fillcolor="green")
                else:
                    graph.node(name=node_name, shape="ellipse", label=f"{node.content()}")
            else:
                if activation[index]:
                    graph.node(name=node_name, shape="box", label=f"{node.content()}", style="filled", fillcolor="green")
                else:
                    graph.node(name=node_name, shape="box", label=f"{node.content()}")

        for edge in self.edges:
            graph.edge("n" + str(edge[0].get_node_id_in_graph(self)), "n" + str(edge[1].get_node_id_in_graph(self)))

        graph.render(filename=f"Activation-{str(act_index).zfill(3)}", cleanup=True, view=False, format='png')

    def get_successor_activations(self, activation):
        successors = []
        successor = activation.copy()
        hasActivatedClause = False

        index = -1
        for node in self.get_clause_nodes():
            index = node.get_node_id_in_graph(self)
            if not activation[index]:
                predecessors = self.get_predecessors(node)
                all_pred_activated = True
                for predecessor in predecessors:
                    pred_index = predecessor.get_node_id_in_graph(self)
                    if not activation[pred_index]:
                        all_pred_activated = False
                if all_pred_activated:
                    successor[index] = True
                    hasActivatedClause = True
                    break
                    

        if not hasActivatedClause:
            return []
        
        #print(f"Activation of clause node {index}: {self.nodes[index].content()}")

        successor_nodes = self.get_successors(self.nodes[index])
        for successor_node in successor_nodes:
            successor_index = successor_node.get_node_id_in_graph(self)
            new_successor = successor.copy()
            new_successor[successor_index] = True
            successors.append(new_successor)
            #print(f"Activation of var node {successor_index}: {self.nodes[successor_index].content()} - successor of node {index}: {self.nodes[index].content()}")
            #print(f"Successor without var node: {successor}")
            #print(f"Successor with var node: {new_successor}")
        
        return successors
    
    def activate(self, save=False):
        new_activation = []
        for node in self.nodes:
            if node.get_node_type() ==  "top":
                new_activation.append(True)
            else:
                new_activation.append(False)
            
        next_activations = [new_activation]
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
