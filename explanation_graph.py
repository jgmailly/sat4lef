class ClauseNode:
    def __init__(self, node_type):
        self.node_type = node_type
        # node types are: top, bottom, var, at-least-one-object-per-agent, at-most-one-agent-per-object, lef-clause
        self.literals = []

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

    def get_edges(self):
        return self.edges

    def get_nodes(self):
        return self.nodes

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.append(node)

    def add_edge(self, node_from, node_to):
        self.edges.append([node_from, node_to])

    def to_string(self):
        str_result = ""
        for node in self.nodes:
            str_result += f"node({node.to_string()}).\n"
        for edge in self.edges:
            str_result += f"edge({edge[0].to_string()},{edge[1].to_string()}).\n"
        return str_result

    def to_dot_basic(self):
        str_result = "digraph G {\n"
        for node in self.nodes:
            str_result += node.content() + " "
            if node.get_node_type() in ["top", "bottom", "var"]:
                str_result += "[shape=box];\n"
            else:
                str_result += "[shape=ellipse];\n"
        for edge in self.edges:
            str_result += edge[0].content() + " -> " + edge[1].content() + " ;\n"
        str_result += "}"
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


if __name__ == "__main__":
    graph = ExplanationGraph()
    top = ClauseNode("top")
    graph.add_node(top)
    bottom = ClauseNode("bottom")
    graph.add_node(bottom)
    graph.add_edge(top, bottom)
    print(graph.to_string())
    
