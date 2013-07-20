# Import the module and instantiate a graph object
from pygraph.classes.graph import graph
from pygraph.algorithms.searching import depth_first_search

class Region2D(list):
    def __init__(self):
        self.z = None


def connected(gr, node1, node2):

    toDoSet = {node1:True}
    doneSet = {}
     
    while True:
      if len(toDoSet) == 0:
          break
      n = toDoSet.keys()[0]
      del toDoSet[n]
      doneSet[n] = True
      for neighbor in gr.neighbors(n):
        if neighbor == node2:
           return True
        if not(neighbor in doneSet):
           toDoSet[neighbor] = True 

    return False


if __name__ == "__main__":

    gr = graph()
    # Add nodes
    gr.add_nodes(['X','Y','Z'])
    gr.add_nodes(['A','B','C', 'D'])
    # Add edges
    gr.add_edge(('A','B'))
    gr.add_edge(('B','C'))
    gr.add_edge(('C','D'))
    gr.add_edge(('A','Y'))
    gr.add_edge(('B','Z'))
    # Depth first search rooted on node X
    st, pre, post = depth_first_search(gr, root='X')
    # Print the spanning tree
    print st


    print connected('A', 'D')
    print connected('A', 'X')

