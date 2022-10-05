import pydotplus
import networkx as nx
import matplotlib.pyplot as plt
import pickle
import json
import math
import sys
import os
#########################################################################################################################################
file_name = ""
node_seq = None
TABLES = []
ACTIONS = []
def get_nodes(path, cnt_blk):
  node_name_label = {}
  dot_graph = pydotplus.graphviz.graph_from_dot_file('SwitchIngress.dot')
  subgraphs = dot_graph.get_subgraphs()
  for subG in subgraphs:
    for n in subG.get_node_list():
      try:
        name = n.obj_dict["attributes"]['label']
      except:
        pass
      if name not in ['__START__','__EXIT__',""]:
        if ';' in name :
          name = name.replace(';','')
        if '"' in name:
          name = name.replace('"','')
        if "()" in name and "." not in name:
          name = name.replace("()",'')
          name = cnt_blk+'.'+name
        node_name_label[n.get_name()] = name
    to_del = 'graph'
    del node_name_label[to_del]

  return node_name_label
#########################################################################################################################################
def get_edges(path, nodes):
  edge_src_details = {}
  edge_src_names = {}
  edges = []
  dot_graph = pydotplus.graphviz.graph_from_dot_file(path)
  count = 0   
  for subGraph in dot_graph.get_subgraphs():
    for e in subGraph.get_edge_list():
      edge_src_details[count] = {"src":e.get_source(),"dst":e.get_destination(), "label":e.obj_dict["attributes"]['label']}
      edge_src_names[count] = {"src":e.get_source(),"dst":e.get_destination(), "label":e.obj_dict["attributes"]['label']}
      count+=1
  for e in edge_src_details.keys():
    #print("\n\tEdges : ",edge_src_details[e]['src'],nodes[edge_src_details[e]['src']], edge_src_details[e]['dst'], nodes[edge_src_details[e]['dst']])
    if(edge_src_details[e]['src'] in nodes.keys() and edge_src_details[e]['dst'] in nodes.keys()):
      edges.append({'src':nodes[edge_src_details[e]['src']], 'dst':nodes[edge_src_details[e]['dst']], 'label': edge_src_details[e]['label'].replace('"','')})
       #edges = edges[1:len(edges)-2]
  return edges
#########################################################################################################################################
def extract_tables(filename):
  data = None
  with open(filename, 'r') as f:
    data = json.load(f)
  node_to_table =[]
  for table in data["tables"]:
    if table["table_type"]=="match" and (cnt_blk+ ".") in table['name'] and "tbl_"+filename not in table["name"]:
      node_to_table.append(table["name"])
  return node_to_table
#########################################################################################################################################
def extract_actions(filename):
  data = None
  with open(filename, 'r') as f:
    data = json.load(f)
  node_to_action =[]
  for table in data["tables"]:
    if table["table_type"]=="match" and (cnt_blk+ ".") in table['name'] and "tbl_"+filename not in table["name"]:
      for actions in table["actions"]:
        node_to_action.append(actions["name"])
  return node_to_action
#########################################################################################################################################
def extract_condition(filename):
  data = None
  with open(filename, 'r') as f:
    data = json.load(f)
  node_to_condition =[]
  for table in data["tables"]:
    if table["table_type"]=="condition":
      node_to_condition.append(table["condition"][1:-1])
  
  return node_to_condition 
#########################################################################################################################################
def extract_table_actions(filepath, nodes):
    data = None
    table_to_action = {}
    with open(filepath, 'r') as f:
        data = json.load(f)

    for table in data['tables']:
        if table['name'] in nodes:
            for action in table['actions']:
                if table['name'] not in table_to_action.keys():
                    table_to_action[table['name']] = [action['name']]
                else:
                    table_to_action[table['name']].append(action['name'])
    return table_to_action
########################################################################################################################################
def eliminate_edge(edge, edges, nodes):
  global edge_to_del
  if edge['dst'] in nodes:
    return edge['dst']
  else:
    for e in edges:
      if(e['src'] == edge['dst']):
        nxt_node = eliminate_edge(e, edges, nodes)
        edge_to_del.append(e)
        break
      else:
        nxt_node = -1
    return nxt_node
########################################################################################################################################
def append_missing_edges(table_to_action, edges, leaf_nodes):
  new_edges = []
  ed_to_del = []
  #print(table_to_action)
  for e in edges:
    if e['src'] in table_to_action.keys():
      ed_to_del.append(e)
      #print(ed_to_del)
      for ac in table_to_action[e['src']]:
        new_edges.append({'src':e['src'], 'dst':ac, 'label':''})
        new_edges.append({'src':ac, 'dst':e['dst'], 'label':''})
        #print(new_edges)
    if e['dst'] in leaf_nodes and e['dst'] in table_to_action.keys():
      
      for ac_1 in table_to_action[e['dst']]:
        new_edges.append({'src':e['dst'], 'dst':ac_1, 'label':''})
  edges = edges + new_edges
  for de in ed_to_del:
    if de in edges:
      edges.remove(de)
  return edges
########################################################################################################################################
def create_cfg(edges):
  edges_tuples = []
  for e in edges:
    edges_tuples.append((e['src'], e['dst'], 0))
  edges_tuples = list(set(edges_tuples))
  for i in edges_tuples:
    print (i)
  G = nx.DiGraph()
  G.add_weighted_edges_from(edges_tuples)
  pos=nx.spring_layout(G)
  nx.draw_shell(G, with_labels = True, arrows=True)
  labels=nx.get_edge_attributes(G, 'weight')
  nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)
  plt.show()
  try:
    cycle =nx.algorithms.cycles.find_cycle(G, orientation="original")
  except:
    cycle=0
  while cycle :
    try:
      G.remove_edge(cycle[-1][0],cycle[-1][1])
    except:
      pass
    try:
      cycle =nx.algorithms.cycles.find_cycle(G, orientation="original")
    except:
      cycle=0
  topological_order = list(nx.topological_sort(G))
  rev_topological_order = list(reversed(list(nx.topological_sort(G))))
  print(topological_order)
  print( rev_topological_order)
  leaf_vertex = [v for v, d in G.out_degree() if d == 0]
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
  e_list2 =[]
  for i in weighted_edges:
    e_list1 = [(i["src"], i["dst"], i["weight"])]
    print(e_list1)
    e_list2.append(e_list1)
  print(e_list2)
  flat_list = [item for sublist in e_list2 for item in sublist]
  print(flat_list)
  G1 = nx.DiGraph()
  G1.add_weighted_edges_from(flat_list)
  nx.draw(G1, with_labels=True)
  pos=nx.spring_layout(G1)
  labels = nx.get_edge_attributes(G1,'weight')
  nx.draw_networkx_edge_labels(G1,pos,edge_labels=labels)

  return G1, weighted_edges
########################################################################################################################################
def augmenter(p4_filename, table_to_action, weighted_edges):
    data = None
    file_name = os.path.split(p4_filename)[1]
    file_path = os.path.split(p4_filename)[0]
    print("\n\t file_name: ",file_name)
    print("\n\t file_path: ",file_path)
    bits = int(math.ceil(math.log(len(weighted_edges),2)) + (8 - (math.ceil(math.log(len(weighted_edges),2)) % 8)))    
    """For Python 3 and above use below line of code and comment above line of code."""
    #bits = math.ceil(math.log2(len(weighted_edges))) + (8 - (math.ceil(math.log2(len(weighted_edges))) % 8))
    with open(p4_filename, 'r') as f:
        data = f.read()
    new_data = data

    """Add BL variable in the the metadata variables."""
    index_metadata = new_data.find('{', new_data.find('struct metadata_t')) + 1
    index_close = new_data.find('}',index_metadata) + 1
    print("\n\t@@ Difference : ",index_close, index_metadata)
    meta_data = "\n\tbit<"+str(bits)+"> BL; \n"
    
    # This code will handle the case where "metadata_t" is empty.
    if(index_close-index_metadata > 1):
        new_data = new_data[0:index_metadata] + meta_data + new_data[index_metadata+1:]
    else:
        new_data = new_data[0:index_metadata] + meta_data +'}' + new_data[index_metadata+1:]

    Ctrl_Ingress_ind = new_data.find("control SwitchIngress(")
    if Ctrl_Ingress_ind == -1:
        Ctrl_Ingress_ind = new_data.find("control SwitchIngress (")

    for we in weighted_edges:
        search_string = ""
        
        """If the BL value is greater than 0 then only annotate."""
        if we['weight'] > 0:
            Ctrl_Ingress_ind = Ctrl_Ingress_ind
            annotate_string = "\n\t\tig_md.BL = ig_md.BL + "+str(we['weight'])+";\n\t"
            
            #If the 'Source' node is a table.
            if we['src'] in table_to_action.keys() and 'tbl_' not in we['src']:
                # print("src : ",we['src'], "dst : ", we['dst'], "keys : ", table_to_action.keys())
                print("\n\t#) CONDITIONS: ",we)
                for ta in table_to_action[we['src']]:
                    if we['dst'] == ta:
                        if len(we['dst'].split('.')) == 2:
                            search_string = "action "+we['dst'].split('.')[1]
                            break
                        else:
                            search_string = "action "+we['dst']
                            break
                
                if new_data.find(search_string) != -1:
                    req_ind = new_data.find('{', new_data.find(search_string)) + 1
                    new_data = new_data[0:req_ind] + annotate_string + new_data[req_ind+1:]
                    print("1) : ",we)
                elif 'noaction' in search_string.lower():
                    """ Creating table specific 'NoAction' """
                    req_ind = new_data.find('{', Ctrl_Ingress_ind)
                    if req_ind == -1:
                        req_ind = new_data.find('{', new_data.find("control SwitchIngress ("))
                    annotate_string = "\n\n\taction "+"NoAction(){ \n\t\t ig_md.BL = ig_md.BL + "+str(we['weight'])+"; \n\t}"
                    new_data = new_data[0:req_ind + 1] + annotate_string + new_data[req_ind+1:]
                    
                #     """ Updating Table Actions """
                #     req_ind = new_data.find('{', new_data.find('actions', new_data.find("table "+we['src'].split('.')[1], Ctrl_Ingress_ind)))
                #     if req_ind == -1:
                #         req_ind = new_data.find('{', new_data.find('actions', new_data.find("table "+we['src'].split('.')[1], new_data.find("control SwitchIngress ("))))
                #     annotate_string = "\n\t\t"+we['src'].split('.')[1]+"_NoAction ;"
                #     new_data = new_data[0:req_ind + 1] + annotate_string + new_data[req_ind+1:]
                #     print("2.1) : ",we)
                
                elif 'nop' in search_string.lower():
                    req_ind = new_data.find('{', Ctrl_Ingress_ind)
                    if req_ind == -1:
                        req_ind = new_data.find('{', Ctrl_Ingress_ind)
                    annotate_string = "\n\n\taction "+we['src'].split('.')[1]+"_nop(){ \n\t\t ig_md.BL = ig_md.BL + "+str(we['weight'])+"; \n\t}"
                    new_data = new_data[0:req_ind + 1] + annotate_string + new_data[req_ind+1:]

                    """ Updating Table Actions """
                    req_ind = new_data.find('{', new_data.find('actions', new_data.find("table "+we['src'].split('.')[1], Ctrl_Ingress_ind)))
                    if req_ind == -1:
                        req_ind = new_data.find('{', new_data.find('actions', new_data.find("table "+we['src'].split('.')[1], new_data.find("control SwitchIngress ("))))
                    annotate_string = "\n\t\t"+we['src'].split('.')[1]+"_nop ;"
                    new_data = new_data[0:req_ind + 1] + annotate_string + new_data[req_ind+1:]
                    print("2.2) : ",we)

            #If the 'Destination' node is a table.
            elif we['dst'] in table_to_action.keys() and 'tbl_' not in we['dst']:
                print('\n\t1) CONDITIONS : ', we)
                if len(we['dst'][0].split('.')) == 2:
                    search_string = "action "+table_to_action[we['dst']][0].split('.')[1]
                else:
                    search_string = "action "+table_to_action[we['dst']][0]
                if new_data.find(search_string) != -1:
                    req_ind = new_data.find('{', new_data.find(search_string)) + 1
                    new_data = new_data[0:req_ind] + annotate_string + new_data[req_ind+1:]
                    print("3) : ",we)
                
                if we['src'] not in ACTIONS and we['src'] not in TABLES:
                    #This means the we['src'] is a condition
                    req_ind = new_data.find('{',new_data.find(we['src'], new_data.find('apply',Ctrl_Ingress_ind)))
                    if req_ind != -1:
                        new_data = new_data[0:req_ind] + annotate_string + new_data[req_ind+1:]
            
            ##If the Source is an Action.
            elif we['src'] in ACTIONS:
                print('\n\t2) CONDITIONS : ', we)
                search_string = "action " + we['src'].split('.')[1]
                req_ind_start = new_data.find('{',  new_data.find(search_string, Ctrl_Ingress_ind))
                req_ind_end = new_data.find('}',req_ind_start)
                
                if new_data.find('ig_md.BL', req_ind_start, req_ind_end) != -1:
                    if we['dst'] not in ACTIONS and we['dst'] not in TABLES: #if the destination node is a condition.
                        search_string = "action " + we['dst'].split('.')[1]
                        req_ind = new_data.find(search_string, Ctrl_Ingress_ind)
                        new_data = new_data[0:req_ind] + annotate_string + new_data[req_ind+1:] + '\n'
                    else:
                        new_data = new_data[0:req_ind_start] + annotate_string + new_data[req_ind_start+1:] + '\n'
                else:
                    new_data = new_data[0:req_ind_start] + annotate_string + new_data[req_ind_start+1:] + '\n'

            ##If the Destination is an Action.
            elif we['dst'] in ACTIONS:
                print('\n\t3) CONDITIONS : ', we)
                search_string = "action " + we['dst'].split('.')[1]
                req_ind_start = new_data.find('{',  new_data.find(search_string, Ctrl_Ingress_ind))
                req_ind_end = new_data.find('}',req_ind_start)

                if new_data.find('ig_md.BL', req_ind_start, req_ind_end) != -1:
                    if we['src'] not in ACTIONS and we['src'] not in TABLES: #if the destination node is a condition.
                        search_string = "action " + we['src'].split('.')[1]
                        req_ind = new_data.find(search_string, Ctrl_Ingress_ind)
                        new_data = new_data[0:req_ind] + annotate_string + new_data[req_ind+1:] + '\n'
                    else:
                        new_data = new_data[0:req_ind_start] + annotate_string + new_data[req_ind_start+1:] + '\n'
                else:
                    new_data = new_data[0:req_ind_start] + annotate_string + new_data[req_ind_start+1:] + '\n'
                        
            ## Else the source node is a condition
            elif we['src'] in CONDITIONS:
                print('\n\t4) CONDITIONS : ', we)
                if '==' not in we['src'] and '!=' not in we['src']:
                    search_string = we['src']
                    req_ind = new_data.find('{',new_data.find(search_string,new_data.find("apply",Ctrl_Ingress_ind)))
                    new_data = new_data[0:req_ind+1] + annotate_string + new_data[req_ind+1:] + '\n'
                elif '==' in we['src']:
                    ind = we['src'].find('==')
                    if (we['src'][ind+2 : ].strip()).isnumeric() :
                        search_string = we['src']                    
                        req_ind = new_data.find('{',new_data.find(search_string,new_data.find("apply",Ctrl_Ingress_ind)))
                        if req_ind != -1:
                            new_data = new_data[0:req_ind+1] + annotate_string + new_data[req_ind+1:] + '\n'
                        else:
                            search_string = we['src'][0:ind+2]
                            req_ind = new_data.find('{',new_data.find(search_string,new_data.find("apply",Ctrl_Ingress_ind)))
                            new_data = new_data[0:req_ind+1] + annotate_string + new_data[req_ind+1:] + '\n'
                elif '!=' in we['src']:
                    ind = we['src'].find('!=')
                    if (we['src'][ind+2 : ].strip()).isnumeric() :
                        search_string = we['src']
                        req_ind = new_data.find('{',new_data.find(search_string,new_data.find("apply",Ctrl_Ingress_ind)))
                        if req_ind != -1:
                            new_data = new_data[0:req_ind+1] + annotate_string + new_data[req_ind+1:] + '\n'
                        else:
                            search_string = we['src'][0:ind+2]
                            req_ind = new_data.find('{',new_data.find(search_string,new_data.find("apply",Ctrl_Ingress_ind)))
                            new_data = new_data[0:req_ind+1] + annotate_string + new_data[req_ind+1:] + '\n'
            
            ## Else the destination node is a condition
            elif we['dst'] in CONDITIONS:
                print('\n\t5) CONDITIONS : ', we)
                if '==' not in we['dst'] and '!=' not in we['dst']:
                    search_string = we['dst']
                    req_ind = new_data.find('{',new_data.find(search_string,new_data.find("apply",Ctrl_Ingress_ind)))
                    new_data = new_data[0:req_ind+1] + annotate_string + new_data[req_ind+1:] + '\n'
                elif '==' in we['dst']:
                    ind = we['dst'].find('==')
                    if (we['dst'][ind+2 : ].strip()).isnumeric() :
                        search_string = we['dst']                  
                        req_ind = new_data.find('{',new_data.find(search_string,new_data.find("apply",Ctrl_Ingress_ind)))
                        if req_ind != -1:
                            new_data = new_data[0:req_ind+1] + annotate_string + new_data[req_ind+1:] + '\n'
                        else:
                            search_string = we['dst'][0:ind+2]
                            req_ind = new_data.find('{',new_data.find(search_string,new_data.find("apply",Ctrl_Ingress_ind)))
                            new_data = new_data[0:req_ind+1] + annotate_string + new_data[req_ind+1:] + '\n'
                elif '!=' in we['dst']:
                    ind = we['dst'].find('!=')
                    if (we['dst'][ind+2 : ].strip()).isnumeric() :
                        search_string = we['dst']
                        req_ind = new_data.find('{',new_data.find(search_string,new_data.find("apply",Ctrl_Ingress_ind)))
                        if req_ind != -1:
                            new_data = new_data[0:req_ind+1] + annotate_string + new_data[req_ind+1:] + '\n'
                        else:
                            search_string = we['dst'][0:ind+2]
                            req_ind = new_data.find('{',new_data.find(search_string,new_data.find("apply",Ctrl_Ingress_ind)))
                            new_data = new_data[0:req_ind+1] + annotate_string + new_data[req_ind+1:] + '\n'

                    
    #Save the updated P4 file with name "<P4 program name>_augmented.p4".
    with open(file_path+"\\"+file_name.split('.')[0]+"_augmented.p4", 'w') as f:
        f.write(new_data)
########################################################################################################################################
"""__MAIN__"""
p4_file_path = ""
jsonfile = ""
dotfile = ""
cnt_blk = ""
if len(sys.argv) < 5 or len(sys.argv) > 5:
    print("\n\t Please provide <path of p4_program> <path of dot_file> <path of json_file> <control_block>")
    exit(0)
else:
    p4_file_path = str(sys.argv[1])
    dotfile = str(sys.argv[2])
    jsonfile = str(sys.argv[3])
    cnt_blk = str(sys.argv[4])
file_name = os.path.split(p4_file_path)[1].split('.')[0]
file_path = os.path.split(p4_file_path)[0]
if file_path != "":
	file_path = file_path+'/'
	print "\n\tPATH : ",'/'+file_path
else:
	file_path = ""
	print "\n\tPATH : ",os.getcwd()+'/'+file_path
nodes_dict = get_nodes(dotfile, cnt_blk)
nodes = nodes_dict.values()
edges = get_edges(dotfile, nodes_dict)
print "\n\tEDGES : ",len(edges)
for e in edges:
	print e
table = extract_tables(jsonfile)
print(table)
action = extract_actions(jsonfile)
print(action)
condition = extract_condition(jsonfile)
print(condition)
table_to_action = extract_table_actions(jsonfile, table)
print(table_to_action)
actual_nodes = []
table_conditions = []
actual_nodes = condition + table + (action)
table_conditions = condition + table

print ("\n\tNODES(Before Removing) : ",len(nodes),nodes)
print ("\n\tACTUAL NODES : ",len(actual_nodes), actual_nodes)
print ("\n\t TABLE CONDITIONS: ", len(table_conditions), table_conditions)
to_del=[]
for n in nodes:
	if n not in actual_nodes:
		to_del.append(n)
for d in to_del:
  nodes.remove(d)
nodes = nodes + action
print(nodes)
edge_to_del = []
rel_edge = edges
for e in rel_edge:
  dst = eliminate_edge(e,edges,nodes)
  if dst != -1:
    e['dst'] = dst
  else:
    edge_to_del.append(e)
for e in edge_to_del:
  if e in rel_edge:
    rel_edge.remove(e)

for i in rel_edge:
  if i["src"] not in nodes:
    rel_edge.remove(i)
for i in rel_edge:
  print(i)
print ("\n\t EDGES TO DELETE : ", len(edge_to_del),edge_to_del)
print ("\n\t EDGES AFTER ELIMINATION: ",len(rel_edge)) 
edges_tuples = []
for e in edges:
  edges_tuples.append((e['src'], e['dst'], 0))
edges_tuples = list(set(edges_tuples))
print(edges_tuples)
G = nx.DiGraph()
# G.add_nodes_from(nodes)
G.add_weighted_edges_from(edges_tuples)
nx.draw(G, with_labels=True)
leaf_nodes = [v for v, d in G.out_degree() if d == 0]
print ("\n\t LEAF NODES: ", leaf_nodes)
start_node = [v for v, d in G.in_degree() if d == 0]
print ("\n\t start node: ", start_node)
updates_edges = append_missing_edges(table_to_action, edges, leaf_nodes)
print ("\n\t UPDATED EDGES: ",len(updates_edges))
for u in updates_edges:
  print (u)
G1, weighted_edges = create_cfg(updates_edges)

print ("\n\t WEIGHTED EDGES: ",len(weighted_edges))
print(weighted_edges)
for we in weighted_edges:
  print(we)
nx.write_gpickle(G1, "cfg.pkl")
infile = open("cfg.pkl",'rb')
new_dict1 = pickle.load(infile)
print(new_dict1)
nx.draw(new_dict1, with_labels=True)
pos=nx.spring_layout(G)
labels=nx.get_edge_attributes(new_dict1, 'weight')


print(labels)
plt.show()
node_seq = None
TABLES = []
ACTIONS = []
CONDITIONS = []
TABLES = TABLES + table
print(TABLES)
ACTIONS = ACTIONS + action
print(ACTIONS)
CONDITIONS = CONDITIONS + condition
print(CONDITIONS)
augmenter(p4_file_path, table_to_action, weighted_edges)

