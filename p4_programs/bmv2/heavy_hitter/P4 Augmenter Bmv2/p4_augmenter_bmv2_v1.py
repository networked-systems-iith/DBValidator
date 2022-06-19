import json
import os
import networkx as nx
import sys
import pickle
# import matplotlib.pyplot as plt
#import graphviz
#import pydotplus

# filename = "./dot files/09-Traceroutable/traceroutable.json"
# filename = "./dot files/03-L2_Flooding/Other ports/l2_flooding_other_ports.json"
# filename = "./dot files/02-Repeater/repeater_without_table.json"
# filename = "./dot files/11-Packet-Loss-Detection/loss-detection.json"
# filename = "./firewall_tofino/prog_firewall_tofino.p4"

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

def extract_nodename_condition(filename):
    """This function creates dictionary of node
    names with its corresponding conditions."""
    data = None
    node_to_condition_map = {}
    with open(filename, 'r') as f:
        data = json.load(f)
    node_to_condition_map = {}
    for name in data['pipelines']:
        for condition in name['conditionals']:
            if 'source_info' in condition.keys():
                node_to_condition_map[condition['name']] = condition['source_info']['source_fragment']
    return node_to_condition_map

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

##############################
#### START CREATING NODES ####
##############################

def create_nodes(filename):
    nodes = []
    table_actions = extract_tables_actions(filename)
    conditionals_nextstep = extract_conditionals(filename)

    for conditional in conditionals_nextstep.keys():
        if conditional not in nodes:
            nodes.append(conditional)
    for table in table_actions.keys():
        if table not in nodes:
            nodes.append(table)
    for ac in table_actions.values():
        if not isinstance(ac,(tuple,set,list)):
            nodes.append(ac)
        else:
            for acc in ac:
                nodes.append(acc)
    # Removing Duplicates:
    nodes = list(set(nodes))
    return nodes

##############################
#### END CREATING NODES ####
##############################

#This is a utility function. Input: Dictionary
# Returns: list of keys and values where value != None
def get_notNone_values(data):
    val = []
    key = []
    for k in data.keys():
        if data[k] is not None and data[k] != 'None' and (data[k] != 'Null' and data[k] != 'null'):
            val.append(data[k])
            key.append(k)
    
    # print("\n\t # get_notNone_values: ")
    # print_details(data)
    return key, val
##############################
#### START CREATING EDGES ####
##############################
switch_case = {}
def create_edges(filename):
    edges = []
    table_actions = extract_tables_actions(filename)
    table_next_actions = extract_tables_next_actions(filename)
    nodename_condition = extract_nodename_condition(filename)
    conditionals_nextstep = extract_conditionals(filename)

    for key in conditionals_nextstep.keys():
        if isinstance(conditionals_nextstep[key]['true_next'],(list, set, tuple)):
            for k1 in conditionals_nextstep[key]['true_next']:
                if k1 is not None and key != 'NoAction':
                    edges.append({"src":key,"dst":k1,"weight":0})
        else:
            if conditionals_nextstep[key]['true_next'] is not None and key != 'NoAction':
                edges.append({"src":key,"dst":conditionals_nextstep[key]['true_next'],"weight":0})

        if isinstance(conditionals_nextstep[key]['false_next'],(list, set, tuple)):
            for k1 in conditionals_nextstep[key]['false_next']:
                if k1 is not None and key != 'NoAction':
                    edges.append({"src":key,"dst":k1,"weight":0})
        else:
            if conditionals_nextstep[key]['false_next'] is not None and key != 'NoAction':
                edges.append({"src":key,"dst":conditionals_nextstep[key]['false_next'],"weight":0})

    """If Switch case is used we have to extract it from Next_action of the table."""
    for key in table_next_actions.keys():
        if "MyIngress" in key:
            if key in table_actions.keys():
                for ac in table_actions[key]:
                    if key != 'NoAction':
                        edges.append({'src':key, 'dst':ac, 'weight':0})
    
    # table_next_actions = extract_tables_next_actions(filename)
    # print("\n\tSwitch Case@@: ", table_next_actions)
    
    for key in table_next_actions.keys():
        vals = []
        keys, vals = get_notNone_values(table_next_actions[key])
        # print("\n\t#### Keys:",keys,"\n\tvals:",vals)

        # vals = list(set(vals))
        # keys = list(set(keys))
        for k,v in zip(keys, vals):
            # print("\n\t@@Keys:",k,"\n\t@@vals:",v)
            ##Write code if there are multiple values in "k"

            if "MyIngress" in k and (k!=v) :
                edges.append({'src':k, 'dst':v, 'weight':0})
                switch_case[key] = {'src':k, 'dst':v, 'weight':0}
            else:
                edges.append({'src':key, 'dst':v, 'weight':0})
                switch_case[key] = {'src':key, 'dst':v, 'weight':0}
               
    """Replace Node name in the edges with exact P4 code snippet."""
    for e in edges:
        if e['src'] in nodename_condition.keys():
            e['src'] = nodename_condition[e['src']]
        
        if e['dst'] in nodename_condition.keys():
            e['dst'] = nodename_condition[e['dst']]
        
        # Remove the edges with such nodes which has next actions as 'None'.
        if e['dst'] in table_next_actions.keys() and 'MyIngress' not in e['dst']:
            for key in table_next_actions[e['dst']].keys():
                if all(x is None for x in table_next_actions[e['dst']].values()):
                    edges.remove(e)

        # If the 'dst' of edge has a Custom table created by compiler(i.e. starts with 'tbl_'), then replace it with the MyIngress Table.
        if 'tbl_' in e['dst']:
            keys, dst = get_notNone_values(table_next_actions[e['dst']])
            # print("\n\t Keys@@:",keys, "\t dst@@:",dst)
            if len(dst) != 0:
                for d in dst:
                    if d != 'null' and d != 'Null' and d != "None":
                        e['dst'] = d
                    else:
                        edges.remove(e)

        # If the 'src' of edge has a Custom table created by compiler(i.e. starts with 'tbl_'), then replace it with the MyIngress Table.
        if 'tbl_' in e['src']:
            # print("\n\t Keys$$:",keys, "\t dst$$:",dst)
            keys, src = get_notNone_values(table_next_actions[e['src']])
            if len(src) != 0:
                for s in src:
                    e['src'] = s  
        
        # Remove the edges with source and destination nodes as Table.
        if ((e['src'] in table_actions.keys() or e['src'] in table_next_actions.keys())
         and (e['dst'] in table_actions.keys() or e['dst'] in table_next_actions.keys())):
            edges.remove(e)
    #Remove such elements with similar 'src' and 'dst'
    for e in edges:
        if e['src'] == e['dst']:
            # print("\n\t@@@@ BEFORE: ",edges)
            edges.remove(e)
            # print("\n\t@@@@ AFTER: ",edges)

    for e in edges:
        if e['src'] in nodename_condition.keys():
            e['src'] = nodename_condition[e['src']]
        
        if e['dst'] in nodename_condition.keys():
            e['dst'] = nodename_condition[e['dst']]
    
    #Remove such tables created by compiler with destination = "None"
    for e in edges:
        if "tbl_" in e['dst']:
            for k in table_next_actions[e['dst']].keys():
                if table_next_actions[e['dst']][k] == None:
                    edges.remove(e)
               
                   
    return edges

##############################
##### END CREATING EDGES #####
##############################

def create_cfg(filename):

    # nodes = create_nodes(filename)
    nodes = []
    weighted_edges = create_edges(filename)    
    edge_list = []

    for e in weighted_edges:
        edge_list.append((e["src"], e["dst"], e["weight"]))
    
    """Remove duplicate edges"""
    edge_list = list(set(edge_list))
    
    """Remove such elements with similar 'src' and 'dst'."""
    for e in edge_list:
        if e[0] == e[1]:
            edge_list.remove(e)

    """Remove Such edges in which source and destination nodes are conditionals"""
    conditionals_nextstep = extract_conditionals(filename)
    for e in edge_list:
        if e[0] in conditionals_nextstep.keys() and e[1] in conditionals_nextstep.keys():
            edge_list.remove(e)

    #Create Nodes using the extracted edges to prevent adding unwanted nodes.
    for e in edge_list:
        nodes.append(e[0])
        nodes.append(e[1])
    nodes = list(set(nodes))

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_weighted_edges_from(edge_list)

    #Graph Layout
    # pos = nx.shell_layout(G) 
    nx.draw_shell(G, with_labels = True, arrows=True) 
    #plt.show()

    print("\n\t Nodes: ")
    print_details(nodes)

    print("\n\t Weighted Edges: ",type(edge_list))
    print_details(edge_list)

    # cycle = nx.find_cycle(G)
    # print("\n\t cycle: ",cycle)

    topological_order = list(nx.topological_sort(G))
    rev_topological_order = list(reversed(list(nx.topological_sort(G))))
    
    leaf_vertex = [v for v, d in G.out_degree() if d == 0]
    path_list = []

    # paths = nx.all_simple_paths(G, source=topological_order[0], target= topological_order[len(topological_order)-1])

    for leaf in leaf_vertex:
        for path in nx.all_simple_paths(G, source=topological_order[0], target=leaf ):
            path_list.append(path)

    ####################################
    #### START BALL-LARUS ALGORITHM ####
    ####################################
    weighted_edges = []
    for e in edge_list:
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
    
    ####################################
    #### END BALL-LARUS ALGORITHM ######
    ####################################

    print("\n\t weighted_edges: ")
    print_details(weighted_edges)

    return weighted_edges, G

#This method extracts the instance name of metadata variable.
def get_meta_inst_name(p4_code, cnt_blk, meta):
	meta_inst = ""
	meta_ind_beg = p4_code.find(" ",p4_code.find(meta, p4_code.find("control "+str(cnt_blk))))
	meta_ind_end = p4_code.find(',',meta_ind_beg)

	print "\n\n@#@##@: ",p4_code[meta_ind_beg: meta_ind_end]

	meta_inst = p4_code[meta_ind_beg: meta_ind_end]
	meta_inst = meta_inst.strip()
	return meta_inst

def augmenter(p4_filename, json_filename, cnt_blk, meta):
    import re

    # jsonfile = "./dot files/03-L2_Flooding/Other ports/l2_flooding_other_ports.json"
    # jsonfile = "./dot files/09-Traceroutable/traceroutable.json"
    file_name = os.path.split(p4_filename)[1]
    file_path = os.path.split(p4_filename)[0]
    jsonfile = json_filename
    

    weighted_edges, graph = create_cfg(jsonfile)
    actions = extract_actions(jsonfile, cnt_blk)
    tables = extract_tables_actions(jsonfile)
    conditions = extract_conditionals(jsonfile)

    print("\n\tTables :")
    print(tables.keys())

    print("\n\tConditions :")
    print(conditions.keys())

    print("\n\t@@Weighted Edges :")
    print_details(weighted_edges)

    # print("\n\tSwitch Case:", switch_case)

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
                annotate_string = "\n\telse{ "+meta_inst+" = "+meta_inst+" + "+str(weight)+";}\n"
                req_ind = new_data.find(search_string) + len(search_string)-1
                req_ind = new_data.find(search_string, req_ind)
                req_ind = new_data.find("}", req_ind)
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
                    
                # print("\n\treq_ind: ", req_ind, "\t search_string: ", search_string)
    # print("\n\t nodes_and_weights: ")
    # print_details(nodes_and_weights)
    
    # with open(file_path+"\\"+file_name.split('.')[0]+"_augmented.p4", 'w') as f:
    
    with open(file_name.split('.')[0]+"_augmented.p4", 'w') as f:
        f.write(new_data)
    nx.write_gpickle(graph, "cfg.txt")

    with open("weighted_edges.txt",'wb') as f:
    	pickle.dump(weighted_edges, f, protocol=2)

    topological_order = list(nx.topological_sort(graph))    
    leaf_vertex = [v for v, d in graph.out_degree() if d == 0]
    path_list = []

    for leaf in leaf_vertex:
        for path in nx.all_simple_paths(graph, source=topological_order[0], target=leaf ):
            path_list.append(path)

    print("\n\t path_list: ")
    print_details(path_list)

    # path_weight = {}
    # count = 'A'
    # for path in path_list:
    #     w = 0
    #     for p in path:
    #         if p in nodes_and_weights:
    #             w = w + nodes_and_weights[p]
    #         else:
    #             w = w + 0
    #     path_weight[count] = {'path':path, 'weight':w}
    #     count = chr(ord(count) + 1)
        
    
    # print("\n\t path_weight: ")
    # print_details(path_weight)
# jsonfile = "./dot files/09-Traceroutable/traceroutable.json"
# jsonfile = "./dot files/03-L2_Flooding/Other ports/l2_flooding_other_ports.json"
# jsonfile = "./dot files/02-Repeater/repeater_without_table.json"
# jsonfile = "./dot files/11-Packet-Loss-Detection/loss-detection.json"

# p4filename = "./dot files/03-L2_Flooding/Other ports/l2_flooding_other_ports.p4"

# jsonfile = "./dot files/firewall_tofino/prog_firewall_tofino.json"
# p4filename = "./dot files/firewall_tofino/prog_firewall_tofino.p4"

# jsonfile = "./dot files/firewall_production_NoActions_added/prog_firewall_tofino.json"
# p4filename = "./dot files/firewall_production_NoActions_added/prog_firewall_tofino.p4"

# p4filename = "./dot files/09-Traceroutable/traceroutable.p4"

p4filename = ""
jsonfile = ""
if len(sys.argv) != 5:
    print("\n\t Please provide <p4filename.p4> <json_file_name.json> <control block name(eg: \"MyIngress\")> <struct metadata name(eg: \"metadata_t\")>")
    exit(0)
else:
    p4filename = str(sys.argv[1])
    jsonfile = str(sys.argv[2])
    cnt_blk = str(sys.argv[3])
    meta = str(sys.argv[4])

print(sys.argv)
augmenter(p4filename, jsonfile, cnt_blk, meta)