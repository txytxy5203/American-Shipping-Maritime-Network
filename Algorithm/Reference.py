import networkx as nx

"""
参考手册
"""
G = nx.DiGraph()
G.add_nodes_from([1,2,3,4])
G.add_edges_from([(1,2), (2,1)])
for u, v, w in G.edges(data=True):
    teu = w.get('total_TEU', 0)
    u_country = G.nodes[u].get('country', 'Unknown')
    v_country = G.nodes[v].get('country', 'Unknown')
    print(u, u_country, v, v_country,teu)

for node, attr in G.nodes(data=True):
    print(node, attr)