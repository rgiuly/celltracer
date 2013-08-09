import numpy


def diffusion(gr, initialConcentration, constantNodes, numClasses):
    
    print "graph:", gr

    concentration = {}

    # set concentration of each
    for currentNode in gr.nodes():
        print "setting to zero:", currentNode
        concentration[currentNode] = numpy.zeros(numClasses)

    print "initial concentrations", initialConcentration
    print "concentation:", concentration
    for c in initialConcentration:
        if c not in concentration:
            concentration[c] = numpy.zeros(numClasses)
        concentration[c] += initialConcentration[c]

    flows = {}

    # do not add transitive_edges(graph)

    iterations = 1600
    #iterations = 100
    for i in range(iterations):

        for currentNode in gr.nodes():
            for otherNode in gr.neighbors(currentNode):
                # flow from other node to current node
                flows[(otherNode, currentNode)] = 0.1 * (concentration[otherNode] - concentration[currentNode])

        for flowKey, flow in flows.items():
            sourceNode = flowKey[0]
            sinkNode = flowKey[1]
            if not sourceNode in constantNodes:
                for index in range(numClasses):
                    concentration[sourceNode][index] -= flow[index]
                    #if concentration[sourceNode][index] < 0: concentration[sourceNode][index] = 0
            if not sinkNode in constantNodes:
                for index in range(numClasses):
                    concentration[sinkNode][index] += flow[index]
                    #if concentration[sinkNode][index] > 1: concentration[sinkNode][index] = 1
                
    
        #print concentration
        print i, "total", iterations

    return concentration

    # consider all adjacent nodes
    # for every node
    #   get other adjacent nodes
    #    flows[from other node to this node] = (concentration other node) - (concentration this node)
    # update all concentrations
    # for every flow in flows:
    #    (destination node)[concentration] += flow
    #    (source node)[concentration] -= flow  (unless it's the main source, which never changes concentration)


if __name__ == "__main__":

    import os
    import cPickle
    
    outputFolder = "/home/rgiuly/output/paper_cerebellum/dseg_test_z"
    
    filename = os.path.join(outputFolder, "request_loop_data")
    file = open(filename, 'rb')
    dict = cPickle.load(file)
    gr = dict['gr']

    diffusion(gr, {'120_7': numpy.array([1.0, 0, 0]), '111_30':numpy.array([0, 0, 1.0])},
              {'120_7': True, '111_30': True}, 3)




