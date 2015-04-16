def createGraph(dep, code, graph, depth=0):
    if depth == 0:
        graph.append((dep, code))


graph = []
createGraph("ADMN", "1010", graph)
print graph
