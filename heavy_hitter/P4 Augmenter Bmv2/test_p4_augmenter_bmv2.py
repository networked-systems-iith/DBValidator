import json
import os
import sys
import pickle
import pydotplus
import networkx as nx
import matplotlib.pyplot as plt

TABLES = None
ACTIONS = None
def print_details(data):
    if isinstance(data,(list, tuple,set)):
        for i in data:
            print("\t",i)
    elif isinstance(data,dict):
        for i in data.keys():
            print("\t",i," : ",data[i])

def extract_actions(filename, cnt_blk):
    data = None
    action_list = []
    with open(filename, 'r') as f:
        data = json.load(f)

    for action in data['actions']:
    	if cnt_blk in str(action):
        	action_list.append(action['name'])
    
    action_list = list(set(action_list))
    return action_list

def extract_tables_actions(filename):
    data = None
    name_to_action = {}
    with open(filename, 'r') as f:
        data = json.load(f)

    for name in data['pipelines']:
        for table in name["tables"]:
            if "MyIngress" in table["name"]:
                name_to_action[table["name"] if("MyIngress" in table["name"]) else table["name"]] =  [x for x in table["actions"]]
    return name_to_action


def extract_tables_next_actions(filename):
    """This Function extracts NEXT_ACTIONS associated with
     the table from json file."""
    data = None
    table_to_next_action = {}
    with open(filename, 'r') as f:
        data = json.load(f)

    for name in data['pipelines']:
        for table in name["tables"]:            
            table_to_next_action[table['name']] = table['next_tables']

            # print("@@@@: ",table['name'], ": @@@@:",table['next_tables'])

    return table_to_next_action

def extract_conditionals(filename):
    """This function creates dictionary of conditionals with its 
    corresponding next actions based on the condition 
    evaluation "True or False"."""
    data = None
    with open(filename, 'r') as f:
        data = json.load(f)

    conditions_to_nextstep = {}
    for name in data['pipelines']:
        for condition in name['conditionals']:
            if 'source_info' in condition.keys():
                conditions_to_nextstep[condition['source_info']['source_fragment']] = {'true_next':condition['true_next'], 
                                                                                'false_next':condition['false_next']}
    return conditions_to_nextstep

def get_edges(path, nodes):
    """This method takes .dot file path and returns a dictionary having Edge Source Node Name and 
        Edge details like destination node name, edge label."""
    """Extracting edge information."""
    edge_src_details = {}
    edges = []
    dot_graph = pydotplus.graphviz.graph_from_dot_file(path) 
    count = 0   
    for subGraph in dot_graph.get_subgraphs():
        for e in subGraph.get_edge_list():
            # print(e.get_source(), e.get_destination(), e.obj_dict["attributes"]['label'])
            edge_src_details[count] = {"src":e.get_source(),"dst":e.get_destination(), "label":e.obj_dict["attributes"]['label']}
            count+=1

    # print "\n edge_src_details : ",edge_src_details
    for e in edge_src_details.keys():
    	# print "\n EE : ",edge_src_details[e]
    	if(edge_src_details[e]['src'] in nodes.keys() and edge_src_details[e]['dst'] in nodes.keys()):
    		edges.append({'src':nodes[edge_src_details[e]['src']], 'dst':nodes[edge_src_details[e]['dst']], 'label': edge_src_details[e]['label'].replace('"','')})
    	elif (edge_src_details[e]['src'] in nodes.keys() and edge_src_details[e]['dst'] not in nodes.keys()):
    		for ed in edge_src_details.keys():
    			if edge_src_details[e]['dst'] == edge_src_details[ed]['src'] and edge_src_details[ed]['dst'] in nodes.keys():
    				edges.append({'src':nodes[edge_src_details[e]['src']], 'dst':nodes[edge_src_details[ed]['dst']], 'label': edge_src_details[e]['label'].replace('"','')})

    return edges

def get_nodes(path, nodes):
    """This method takes .dot file path and returns a dictionary having Node Name and Node Label."""
    """Extracting node information."""
    node_name_label = {}
    dot_graph = pydotplus.graphviz.graph_from_dot_file(path) 
    subgraphs = dot_graph.get_subgraphs()  
    # print(type(dot_graph), type(subgraphs))
    # node_list =  subgraphs.get_node_list()
    # print("\n\t node_list : ", node_list)
    for subG in subgraphs:
        for n in subG.get_node_list():
            # print(n.get_name(), n.obj_dict["attributes"]['label'])
            # print("\n\t EEEEEE : ",e.obj_dict["attributes"].get("shape"))
            name = n.obj_dict["attributes"]['label']
            if ';' in name :
                name = name.replace(';','')
            if '"' in name:
            	name = name.replace('"','')
            if name in nodes:
            	node_name_label[n.get_name()] = name
    return node_name_label

def create_all_edges(edges, tab_actions):
	all_edges = []

	for table in table_actions.keys():
		for acc in table_actions[table]:
			all_edges.append({'src':str(table),'dst':str(acc),'label':''})		
	all_edges = edges + all_edges
	return all_edges

# This function will create CFG with the provided Nodes and Edges.
def create_cfg(nodes, edges, tables, actions):
	global ACTIONS
	global TABLES

	ACTIONS = actions
	TABLES = tables
	edges_tuples = []

	for e in edges:
		edges_tuples.append((e['src'], e['dst'], 0))

	print "\n\t nodes : ",nodes
	print "\n\t edges_tuples : ",edges_tuples
    # nodes = get_nodes(dot_file_path)
    # edges = get_edges(dot_file_path)

    # clean_nodes, clean_edges = clean_data(nodes, edges)

    # table_to_action = extract_table_actions(json_file_path, clean_nodes)
    
    # global ACTIONS
    # global TABLES

    # for t in table_to_action.keys():
    #     ACTIONS = ACTIONS + table_to_action[t]
    
    # ACTIONS = list(set(ACTIONS))
    # TABLES = list(set(table_to_action.keys()))

    # all_clean_nodes = create_nodes(clean_nodes, table_to_action)
    # all_clean_edges = create_edges(clean_edges, table_to_action)    

    # Remove edges with compiler generated table to any other node accept it's own action.
    # for edge in all_clean_edges:
    #     if 'tbl_' in edge[0] :
    #         action_name = "SwitchIngress."+str(edge[0]).replace("tbl_","")
    #         if str(edge[1]) != action_name:
    #             all_clean_edges.remove(edge)
    
    # for i in all_clean_edges:
    #     print("\n\t all_clean_edges : ",i)
    
    # for i in all_clean_nodes:
    #     print("\n\t all_clean_nodes : ",i)

	G = nx.DiGraph()
	G.add_nodes_from(nodes)
	G.add_weighted_edges_from(edges_tuples)
    
    # This code is for detecting cycle in the Graph in case of any error.
	"""cycle = []
	try:
		cycle = nx.algorithms.cycles.find_cycle(G, orientation="original")
	except:
		pass
	topological_order = list()
	rev_topological_order = list()
	try:
		topological_order = list(nx.topological_sort(G))
		rev_topological_order = list(reversed(list(nx.topological_sort(G))))
	except:
		print("\n\t Cycle found in the graph...!!!", cycle)
	finally:
		for e in cycle:
			if (e[0] in ACTIONS and e[1] not in TABLES) or ("tbl_" in e[0] and e[1] not in TABLES):
				tmp_edge = (e[0],e[1],0)
				if tmp_edge in all_clean_edges:
					print("\n\t tmp_edge : ", tmp_edge)
					edges_tuples.remove(tmp_edge)
					break
			elif(e[1].lower() == 'noaction'):
				tmp_edge = (e[0],e[1],0)
				if tmp_edge in edges_tuples:
					print("\n\t tmp_edge : ", tmp_edge)
					edges_tuples.remove(tmp_edge)
					break
		G = nx.DiGraph()
		G.add_nodes_from(nodes)
		G.add_weighted_edges_from(edges_tuples)

        # nx.draw_shell(G, with_labels = True, arrows=True) 
		plt.figure(figsize =(12, 12)) 
		nx.draw_networkx(G, with_label = True, node_color ='green', arrows=True) 
		plt.show()

		print("\n\t All clean edges: ", len(edges_tuples), edges_tuples)
		topological_order = list(nx.topological_sort(G))
		rev_topological_order = list(reversed(list(nx.topological_sort(G))))"""
    
	nx.draw_shell(G, with_labels = True, arrows=True) 
	plt.show()


	topological_order = list(nx.topological_sort(G))
	rev_topological_order = list(reversed(list(nx.topological_sort(G))))

	leaf_vertex = [v for v, d in G.out_degree() if d == 0]
	print "\n\t leaf_vertex: ",leaf_vertex
	print "\n\t topological_order : ", len(topological_order)
	for t in topological_order:
		print t
    
	print "\n\t rev_topological_order : ", len(rev_topological_order)
	for t in rev_topological_order:
		print t 

    ####################################
    #### START BALL-LARUS ALGORITHM ####
    ####################################
	weighted_edges = []
	for e in edges_tuples:
		weighted_edges.append({'src':e[0], 'dst':e[1], 'weight':e[2]})

	num_path = {}
	for v in rev_topological_order:
		if v in leaf_vertex:
			num_path[v] = 1
		else:
			num_path[v] = 0
			for e in G.out_edges(v):
				ind = weighted_edges.index({'src':e[0], 'dst':e[1],'weight': 0})
				weighted_edges[ind]['weight'] = num_path[v]
				num_path[v] = num_path[v] + num_path[e[1]]
    
    ###################################
    #### END BALL-LARUS ALGORITHM ######
    ####################################

	return G, weighted_edges

#This method extracts the instance name of metadata variable.
def get_meta_inst_name(p4_code, cnt_blk, meta):
	meta_inst = ""
	meta_ind_beg = p4_code.find(" ",p4_code.find(meta, p4_code.find("control "+str(cnt_blk))))
	meta_ind_end = p4_code.find(',',meta_ind_beg)

	print "\n\n@#@##@: ",p4_code[meta_ind_beg: meta_ind_end]

	meta_inst = p4_code[meta_ind_beg: meta_ind_end]
	meta_inst = meta_inst.strip()
	return meta_inst

def augmenter(p4_filename, json_filename, dotfile, cnt_blk, meta):
    import re

    # jsonfile = "./dot files/03-L2_Flooding/Other ports/l2_flooding_other_ports.json"
    # jsonfile = "./dot files/09-Traceroutable/traceroutable.json"
    file_name = os.path.split(p4_filename)[1]
    file_path = os.path.split(p4_filename)[0]
    jsonfile = json_filename

    table_actions = extract_tables_actions(jsonfile)

    actions = extract_actions(jsonfile, cnt_blk)

    for ta in table_actions.keys():
		for ac in table_actions[ta]:
			if ac not in actions:
				actions.append(ac)

    conditions = extract_conditionals(jsonfile)
    nodes = actions + table_actions.keys() + conditionals.keys()
    all_nodes = get_nodes(dotfile, nodes)
    edges = get_edges(dotfile, all_nodes)
    all_edges = create_all_edges(edges, table_actions)
    graph,weighted_edges = create_cfg(nodes, all_edges, table_actions.keys(), actions)
    tables = table_actions

    print("\n\tTables :")
    print(tables.keys())


    print("\n\t@@Weighted Edges :")
    print_details(weighted_edges)

    data = None
    with open(p4_filename, 'r') as f:
        data = f.read()
        meta_inst = get_meta_inst_name(data, cnt_blk, meta)
        meta_inst = meta_inst + '.BL'
        new_data = data
        nodes_and_weights = {}

        index_metadata = new_data.find('{', new_data.find('struct metadata')) + 1
        meta_data = "\n\tbit<16> BL; \n"
        new_data = new_data[0:index_metadata] + meta_data + new_data[index_metadata+1:]

        for we in weighted_edges:
            src = we['src']
            dst = we['dst']

            weight = int(we['weight'])

            #If the "src" Node is an action then annotate the BL valriable to the Action.
            if src in actions:
                # if 'NoAction' in src:
                #     continue
                nodes_and_weights[src] = weight
                if len(src.split('.')) > 1:
                    src = src.split('.')[1]
                    search_string = "action "+ str(src)
                else:
                    search_string = "action "+ str(src)

                annotate_string = "\n\t "+meta_inst+" = "+meta_inst+" + "+str(weight)+";\n"

                if new_data.find(search_string) != -1 and int(weight) > 0:
                    req_ind = new_data.find('{', new_data.find(search_string)) + 1
                    new_data = new_data[0:req_ind] + annotate_string + new_data[req_ind+1:]
                # print("\n\tindex: ",req_ind," : ", src)
            #If the "dst" Node is an action then annotate the BL valriable to the Action.
            elif dst in actions:
                # if 'NoAction' in dst:
                #     continue
                nodes_and_weights[dst] = weight
                if len(dst.split('.')) > 1:
                    dst = dst.split('.')[1]
                    search_string = "action "+ str(dst)
                else:
                    search_string = "action "+ str(dst)
                annotate_string = "\n\t\t "+meta_inst+" = "+meta_inst+" + "+str(weight)+";\n"
                if new_data.find(search_string) != -1 and int(weight) > 0:
                    req_ind = new_data.find('{', new_data.find(search_string)) + 1
                    new_data = new_data[0:req_ind] + annotate_string + new_data[req_ind+1:]
            elif src in conditions.keys() and dst in tables.keys():
                search_string = src
                nodes_and_weights[src] = weight
                annotate_string = "\n\t"+meta_inst+" = "+meta_inst+" + "+str(weight)+";\n"
                req_ind = new_data.find(cnt_blk)
                req_ind = new_data.find(search_string, req_ind)
                req_ind = new_data.rfind("{",0,req_ind)
                # req_ind = new_data.find("}", req_ind)

                print "\n\tHEREEEEEEE : ",src ,req_ind
                if int(weight) > 0:
                    new_data = new_data[0:req_ind+1] + annotate_string + new_data[req_ind+1:]
            elif src in conditions.keys():
                search_string = src
                nodes_and_weights[src] = weight
                annotate_string = "\n\t\t "+meta_inst+" = "+meta_inst+" + "+str(weight)+";\n"
                req_ind = new_data.find(search_string) + len(search_string)-1
                req_ind = new_data.find(search_string, req_ind)
                req_ind = new_data.find("{", req_ind)
                if int(weight) > 0:
                    new_data = new_data[0:req_ind] + annotate_string + new_data[req_ind+1:]
    
    with open(file_name.split('.')[0]+"_augmented.p4", 'w') as f:
        f.write(new_data)
    nx.write_gpickle(graph, "cfg.txt")

    with open("weighted_edges.txt",'wb') as f:
    	pickle.dump(weighted_edges, f, protocol=2)

    topological_order = list(nx.topological_sort(graph))    
    leaf_vertex = [v for v, d in graph.out_degree() if d == 0]

    # leaf_vertex = [v for v, d in G.out_degree() if d == 0]
    print "\n\t leaf_vertex: ",leaf_vertex
    print "\n\t topological_order : ", len(topological_order)
    for t in topological_order:
    	print t

    path_list = []

    for leaf in leaf_vertex:
        for path in nx.all_simple_paths(graph, source=topological_order[0], target=leaf ):
            path_list.append(path)

    print("\n\t path_list: ")
    print_details(path_list)


p4filename = ""
jsonfile = ""
if len(sys.argv) != 6:
    print("\n\t Please provide <p4filename.p4> <dot_file_name.dot> <json_file_name.json> <control block name(eg: \"MyIngress\")> <struct metadata name(eg: \"metadata_t\")>")
    exit(0)
else:
    p4filename = str(sys.argv[1])
    dotfile = str(sys.argv[2])
    jsonfile = str(sys.argv[3])
    cnt_blk = str(sys.argv[4])
    meta = str(sys.argv[5])


table_actions = extract_tables_actions(jsonfile)
print "\n\t TABLE ACTIONS : ",table_actions

actions = extract_actions(jsonfile, cnt_blk)

for ta in table_actions.keys():
	for ac in table_actions[ta]:
		if ac not in actions:
			actions.append(ac)
print "\n\t ACTIONS : ",actions

conditionals = extract_conditionals(jsonfile)
print "\n\t CONDITIONS : ",conditionals

nodes = actions + table_actions.keys() + conditionals.keys()
print "\n\t NODES : ",nodes

all_nodes = get_nodes(dotfile, nodes)
print "\n\t ALL NODES : ",all_nodes

edges = get_edges(dotfile, all_nodes)
print "\n\t EDGES : ",edges

all_edges = create_all_edges(edges, table_actions)
print "\n\t ALL EDGES: ",all_edges

graph,weighted_edges = create_cfg(nodes, all_edges, table_actions.keys(), actions)
print "\n\t weighted_edges : ",weighted_edges

augmenter(p4filename, jsonfile, dotfile, cnt_blk, meta)