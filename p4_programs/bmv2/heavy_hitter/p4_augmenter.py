import json
import os
import sys
import math
import pickle
import pydotplus
import networkx as nx
from collections import deque
import matplotlib.pyplot as plt

edge_to_del = []
def get_nodes(path, cnt_blk):
	"""This method takes .dot file path and returns a dictionary having Node Name and Node Label."""
	"""Extracting node information."""
	node_name_label = {}
	dot_graph = pydotplus.graphviz.graph_from_dot_file(path) 
	subgraphs = dot_graph.get_subgraphs()  
	for subG in subgraphs:
		for n in subG.get_node_list():			
			name = n.obj_dict["attributes"]['label']
			if name not in ['__START__','__EXIT__',""]:
				if ';' in name :
					name = name.replace(';','')
				if '"' in name:
					name = name.replace('"','')
				if "()" in name and "." not in name:
					name = name.replace("()",'')
					name = cnt_blk+'.'+name
				if name not in node_name_label.values():
					node_name_label[n.get_name()] = name
				else:
					cnt = 1
					key = node_name_label.keys()
					values = node_name_label.values()
					ind = key[values.index(name)]
					while(1):
						if name+"##"+str(cnt) in node_name_label:
							cnt += 1
						else:
							name = name+"##"+str(cnt)
							break
					node_name_label[n.get_name()] = name
					# if "##" in node_name_label[ind]:
					# 	cnt = int(node_name_label[ind].split("##")[1])
		to_del = 'graph'
		del node_name_label[to_del]
	return node_name_label

def get_edges(path, nodes):
	"""This method takes .dot file path and returns a dictionary having Edge Source Node Name and
		Edge details like destination node name, edge label. Extracting edge information."""
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
		# print("\n\tEdges : ",edge_src_details[e]['src'],nodes[edge_src_details[e]['src']], edge_src_details[e]['dst'], nodes[edge_src_details[e]['dst']])
		if(edge_src_details[e]['src'] in nodes.keys() and edge_src_details[e]['dst'] in nodes.keys()):
			edges.append({'src':nodes[edge_src_details[e]['src']], 'dst':nodes[edge_src_details[e]['dst']], 'label': edge_src_details[e]['label'].replace('"','')})
	# edges = edges[1:len(edges)-2]
	return edges

def extract_conditionals(filename):
	"""This function creates dictionary of conditionals with its 
	corresponding next actions based on the condition 
	evaluation "True or False"."""
	data = None
	with open(filename, 'r') as f:
		data = json.load(f)

	#If any duplicate Conditions present then append "##1", "##2" etc. at the end of the conditionals.
	node_to_condition = {}
	for name in data['pipelines']:
		for condition in name['conditionals']:
			if 'source_info' in condition.keys():
				if str(condition['source_info']['source_fragment']) not in node_to_condition.values():
					node_to_condition[str(condition['name'])] = str(condition['source_info']['source_fragment'])
				else:
					cnt = 1
					key = node_to_condition.keys()
					values = node_to_condition.values()
					# ind = key[values.index(str(condition['source_info']['source_fragment']))]
					while(1):
						if str(condition['source_info']['source_fragment'])+"##"+str(cnt) in node_to_condition:
							cnt += 1
						else:
							node_to_condition[str(condition['name'])] = str(condition['source_info']['source_fragment']) + "##" + str(cnt)
							break

			else:
				if str(condition['true_next']) != 'None' and str(condition['true_next']) not in node_to_condition.values():
					node_to_condition[str(condition['name'])] = str(condition['true_next'])
				else:
					cnt = 1
					key = node_to_condition.keys()
					values = node_to_condition.values()
					# ind = key[values.index(name)]
					while(1):
						if str(condition['true_next'])+"##"+str(cnt) in node_to_condition.values():
							cnt += 1
						else:
							node_to_condition[str(condition['name'])] = str(condition['true_next']) + "##" + str(cnt)
							break
				if str(condition['false_next']) != 'None' and str(condition['false_next']) not in node_to_condition.values():
					node_to_condition[str(condition['name'])] = str(condition['false_next'])
				else:
					cnt = 1
					key = node_to_condition.keys()
					values = node_to_condition.values()
					# ind = key[values.index(name)]
					while(1):
						if str(condition['false_next'])+"##"+str(cnt) in node_to_condition.values():
							cnt += 1
						else:
							node_to_condition[str(condition['name'])] = str(condition['false_next']) + "##" + str(cnt)
							break

	conditions_to_nextstep = {}
	for name in data['pipelines']:
		for condition in name['conditionals']:
			if 'source_info' in condition.keys() and str(condition['source_info']['source_fragment']) not in conditions_to_nextstep.keys():
				conditions_to_nextstep[str(condition['source_info']['source_fragment'])] = {'true_next':str(condition['true_next']), 
																				'false_next':str(condition['false_next'])}
			elif 'source_info' in condition.keys() and str(condition['source_info']['source_fragment']) in conditions_to_nextstep.keys():
				cnt = 1
				while(1):
					if str(condition['source_info']['source_fragment'])+"##"+str(cnt) in conditions_to_nextstep.keys():
						cnt += 1
					else:
						conditions_to_nextstep[str(condition['source_info']['source_fragment'])+ "##" + str(cnt)] = {'true_next':str(condition['true_next']), 
																				'false_next':str(condition['false_next'])}
						break

	to_delete = []
	for node in node_to_condition:
		if node_to_condition[node] in node_to_condition.keys():
			to_delete.append(node)

	if len(to_delete) > 0:
		for n in to_delete:
			del node_to_condition[n]
	return conditions_to_nextstep, node_to_condition

def extract_actions(filename, cnt_blk):
	global CONTROL
	CONTROL = cnt_blk
	data = None
	action_list = []
	with open(filename, 'r') as f:
		data = json.load(f)

	for action in data['actions']:
		if cnt_blk in str(action):
			action_list.append(str(action['name']))
	
	action_list = list(set(action_list))
	return action_list

def extract_tables_actions(filename, cnt_blk, actions):
	data = None
	name_to_action = {}
	tbl_to_action = {}
	tbl_to_table = {}
	with open(filename, 'r') as f:
		data = json.load(f)

	for name in data['pipelines']:
		for table in name["tables"]:
			if cnt_blk in table["name"]:
				name_to_action[str(table["name"]) if(cnt_blk in table["name"]) else table["name"]] =  [str(x) for x in table["actions"]]
			else:
				tbl_to_action[str(table["name"])] =  [str(x) for x in table["actions"]]
				tbl_to_table[str(table["name"])] = [str(x) for x in table["next_tables"].values()]
				# print "\n\t TBL_TO_ACTION : ",str(table["name"]),table["actions"]
				# print "\n\t TBL_TO_nexttables : ",str(table["name"]),[str(x) for x in table["next_tables"].values()]
	return name_to_action, tbl_to_action, tbl_to_table

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

def append_missing_edges(table_action, edges, leaf_nodes):
	new_edges = []
	ed_to_del = []
	for e in edges:
		if e['src'] in table_actions.keys():
			ed_to_del.append(e)
			for ac in table_actions[e['src']]:
				new_edges.append({'src':e['src'], 'dst':ac, 'label':''})
				new_edges.append({'src':ac, 'dst':e['dst'], 'label':''})
		elif e['dst'] in leaf_nodes and e['dst'] in table_actions.keys():
			for ac_1 in table_actions[e['dst']]:
				new_edges.append({'src':e['dst'], 'dst':ac_1, 'label':''})

	edges = edges + new_edges
	for de in ed_to_del:
		if de in edges:
			edges.remove(de)
	return edges

#This method extracts the instance name of metadata variable.
def get_meta_inst_name(p4_code, cnt_blk, meta):
	meta_inst = ""
	meta_ind_beg = p4_code.find(" ",p4_code.find(meta, p4_code.find("control "+str(cnt_blk))))
	meta_ind_end = p4_code.find(',',meta_ind_beg)

	# print "\n\n@#@##@: ",p4_code[meta_ind_beg: meta_ind_end]

	meta_inst = p4_code[meta_ind_beg: meta_ind_end]
	meta_inst = meta_inst.strip()
	return meta_inst

# This method extract all the paths and saves the all paths in text file and save pickle file for further use.
def extract_paths(G, file_path):
	leaf_nodes = [v for v, d in G.out_degree() if d == 0]
	start_node = [v for v, d in G.in_degree() if d == 0]
	# print "\n\t LEAF NODES: ", leaf_nodes
	# print "\n\t START NODE : ",start_node

	path_list = []
	for leaf in leaf_nodes:
	    for path in nx.all_simple_paths(G, source=start_node[0], target=leaf ):
	        path_list.append(path)
	        # print "\n\t path: ",path

	# Extract edges in the path.
	path_list_edges = []
	for path in map(nx.utils.pairwise, path_list):
	    path_list_edges.append(list(path)) 

	path_list_edges_weights = []
	for path in path_list_edges:
	    weighted_path = list()
	    weight_sum = 0
	    for edge in path:
	        # find the edge in weighted_edges and update the edge including weight in "path_list_edges_weights"
	        matched_edge = list(filter(lambda e: e['src'] == edge[0] and e['dst'] == edge[1], weighted_edges))
	        weight_sum = weight_sum + int(matched_edge[0]['weight'])
	    path_list_edges_weights.append([path,weight_sum])

	# Creating paths by merging the edges.[[(A,B),(C,D)],10] to [[A,B,C,D],10]
	all_paths = []
	for path in path_list_edges_weights:
		l = []
		for e in path[0]:
			l.append(str(e[0]))
		l.append(str(e[1]))
		all_paths.append([l,path[1]])

	with open(file_path+"path_list.pkl",'wb') as f:
	    pickle.dump(path_list_edges_weights, f, protocol=2)

	new_file=open(file_path+'all_paths.txt','w')
	data = ""
	for p in all_paths:
		data = data + ' --> '.join(p[0]) + ' ## '+str(p[1])+"\n\n"
		# print("\n\tPATHS: ",p)

	new_file.write(data)
	new_file.close()

def create_cfg(edges):

	edges_tuples = []

	for e in edges:
		edges_tuples.append((e['src'], e['dst'], 0))
	edges_tuples = list(set(edges_tuples))


	G = nx.DiGraph()
	G.add_weighted_edges_from(edges_tuples)
	
	nx.draw_shell(G, with_labels = True, arrows=True, font_size=5, node_size=80, node_color='orange')
	plt.savefig(file_path+'graph.pdf', dpi = 300, format='pdf', bbox_inches="tight")
	plt.show(block=False)

	G = nx.DiGraph()
	G.add_weighted_edges_from(edges_tuples)

	topological_order = list(nx.topological_sort(G))
	rev_topological_order = list(reversed(list(nx.topological_sort(G))))

	leaf_vertex = [v for v, d in G.out_degree() if d == 0]

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

def get_next_same_con(new_data,node,req_ind):
	#This function identifies the index of next similar condition in the code.
	cnt = int(node.split("##")[1])
	search_string = node.split("##")[0]
	req_ind = 0
	for i in range(cnt+1):
		req_ind = new_data.find(search_string, req_ind+len(search_string))
		# print "\n\t>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<",req_ind, new_data[req_ind:req_ind+100]
	return req_ind

def augmenter(p4_filename, jsonfile, dotfile, cnt_blk, meta, weighted_edges, file_path):
	import re

	file_name = os.path.split(p4_filename)[1]

	conditions, node_to_condition = extract_conditionals(jsonfile)
	actions = extract_actions(jsonfile, cnt_blk)
	table_actions, tbl_to_action, tbl_to_table = extract_tables_actions(jsonfile, cnt_blk, actions)
	tables = table_actions

	data = None
	with open(p4_filename, 'r') as f:
		data = f.read()
		meta_inst = get_meta_inst_name(data, cnt_blk, meta)
		meta_inst = meta_inst + '.BL'
		new_data = data
		nodes_and_weights = {}
		bits = int(math.ceil(math.log(len(weighted_edges),2)) + (8 - (math.ceil(math.log(len(weighted_edges),2)) % 8)))    
		index_metadata = new_data.find('{', new_data.find('struct '+meta)) + 1
		meta_data = "\n\tbit<"+str(bits)+"> BL; \n"
		if index_metadata != -1:
			new_data = new_data[0:index_metadata] + meta_data + new_data[index_metadata+1:]
		else:
			print "\n\t Declaration of <"+meta+"> is not present in this file."
			exit(0)

		for we in weighted_edges:
			src = we['src']
			dst = we['dst']

			weight = int(we['weight'])

			#If the "src" Node is an action then annotate the BL valriable to the Action.
			if src in actions:
				# print("\n\t ####1) ",we)
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
					if req_ind != -1:
						new_data = new_data[0:req_ind] + annotate_string + new_data[req_ind+1:]
				# print("\n\tindex: ",req_ind," : ", src)
			#If the "dst" Node is an action then annotate the BL valriable to the Action.
			elif dst in actions:
				# print("\n\t ####2) ",we)
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
					if req_ind != -1:
						new_data = new_data[0:req_ind] + annotate_string + new_data[req_ind+1:]
			elif src in conditions.keys() and dst in tables.keys():
				# print("\n\t ####3) ",we)
				search_string = dst.split('.')[1]
				nodes_and_weights[src] = weight
				annotate_string = "\n\t"+meta_inst+" = "+meta_inst+" + "+str(weight)+";\n"
				req_ind = new_data.find(cnt_blk)
				req_ind = new_data.find("apply",req_ind)
				req_ind = new_data.find(search_string+".apply()", req_ind)
				req_ind = new_data.find(";",req_ind)
				# print("\n\t req_ind: ",req_ind, new_data[req_ind:req_ind+20])
				
				if int(weight) > 0 and req_ind != -1:
						new_data = new_data[0:req_ind+1] + annotate_string + new_data[req_ind+1:]

			elif src in tables.keys() and dst in conditions.keys():
				# print("\n\t ####4) ",we)
				nodes_and_weights[src] = weight
				annotate_string = "\n\t"+meta_inst+" = "+meta_inst+" + "+str(weight)+";\n"
				if '##' not in dst:
					search_string = dst
					req_ind = new_data.find(cnt_blk)
					req_ind = new_data.find(search_string, req_ind)
					# req_ind = new_data.rfind("{",0,req_ind)
					# print("\n\t >>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<req_ind: ",new_data[req_ind-10:req_ind])
					# req_ind = new_data.find("}", req_ind)
				elif '##' in dst:
					cnt = int(dst.split('##')[1])
					search_string = dst.split('##')[0]
					req_ind = new_data.find(cnt_blk)
					req_ind = get_next_same_con(new_data,dst,req_ind)
					# print("\n\t >>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<req_ind: ",new_data[req_ind-10:req_ind])
					# for i in range(cnt):
					# 	req_ind = new_data.find(search_string, req_ind+len(search_string))
					# req_ind = new_data.find("{",0,req_ind)

				if int(weight) > 0 and req_ind != -1:
					new_data = new_data[0:req_ind+1] + annotate_string + new_data[req_ind+1:]
			elif src in conditions.keys() and dst in conditions.keys():
				
				src_con_ind = 0
				dst_con_ind = 0
				search_string = dst
				nodes_and_weights[src] = weight
				annotate_string = "\n\t\t "+meta_inst+" = "+meta_inst+" + "+str(weight)+";\n"
				req_ind = new_data.find(cnt_blk)
				req_ind = new_data.find("apply")

				if "##" not in src:
					src_con_ind = new_data.find(src, req_ind)
				else:
					search = src.split("##")[0]
					src_con_ind = get_next_same_con(new_data,src,req_ind)

				
				if "##" not in dst:
					dst_con_ind = new_data.find(dst, req_ind)
				else:
					dst_con_ind = get_next_same_con(new_data,dst,req_ind)

				# print("\n\t >>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<SRC req_ind: ",new_data[src_con_ind-10:src_con_ind])
				# print("\n\t >>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<DST req_ind: ",new_data[dst_con_ind-10:dst_con_ind])

				if "elif" not in new_data[src_con_ind-10:src_con_ind] and "if" in new_data[src_con_ind-10:src_con_ind]:
					if "elif" not in new_data[dst_con_ind-10:dst_con_ind] and "if" in new_data[dst_con_ind-10:dst_con_ind]:
						#If src and dst are IF conditions then augment in between them.
						req_ind = new_data.find("{",src_con_ind)

				if "elif" in new_data[src_con_ind-10:src_con_ind]:
					if "elif" in new_data[dst_con_ind-10:dst_con_ind]:
						#If src and dst are ELIF conditions then augment inside both of them.
						req_ind = new_data.find("{",dst_con_ind)

				if "elif" in new_data[src_con_ind-10:src_con_ind]:
					if "elif" not in new_data[dst_con_ind-10:dst_con_ind] and "if" in new_data[dst_con_ind-10:dst_con_ind]:
						#If src is ELIF and dst is IF conditions then augment in between them.
						req_ind = new_data.find("{",src_con_ind)

				if "elif" not in new_data[src_con_ind-10:src_con_ind] and "if" in new_data[src_con_ind-10:src_con_ind]:
					if "elif" in new_data[dst_con_ind-10:dst_con_ind]:
						#If src is ELIF and dst is IF conditions then augment in between them.
						req_ind = new_data.find("{",dst_con_ind)
				# req_ind = new_data.find(search_string, req_ind)
				# req_ind = new_data.find("{",req_ind)
				# req_ind = new_data.rfind("{",0,req_ind)
				# print "@@@@ : ", req_ind, new_data[req_ind : req_ind+20]
				stk = deque()
				ind = 0
				for i in range(req_ind, len(new_data)-1):
				    if new_data[i] == '{':
				        stk.append(new_data[i])
				    elif new_data[i] == '}':
				        stk.pop()
				    if not stk:
				        ind = i
				        break
				req_ind = ind
				if int(weight) > 0 and req_ind != -1:
					new_data = new_data[0:req_ind+1] + annotate_string + new_data[req_ind+1:]

	with open(file_path+file_name.split('.')[0]+"_augmented.p4", 'w') as f:
		f.write(new_data)
	


p4filename = ""
jsonfile = ""
dotfile = ""
cnt_blk = ""
meta = ""
if len(sys.argv) != 6:
	print("\n\t Please provide <p4filename.p4> <dot_file_name.dot> <json_file_name.json> <control block name(eg: \"MyIngress\")> <struct metadata name(eg: \"metadata_t\")>")
	exit(0)
else:
	p4filename = str(sys.argv[1])
	dotfile = str(sys.argv[2])
	jsonfile = str(sys.argv[3])
	cnt_blk = str(sys.argv[4])
	meta = str(sys.argv[5])

file_path = os.path.split(p4filename)[0]
if file_path != "":
	file_path = file_path+'/'
	# print "\n\tPATH : ",'/'+file_path
else:
	file_path = ""
	# print "\n\tPATH : ",os.getcwd()+'/'+file_path

nodes_dict = get_nodes(dotfile, cnt_blk)
nodes = nodes_dict.values()

edges = get_edges(dotfile, nodes_dict)
# print "\n\tEDGES : ",len(edges)
# for e in edges:
# 	print e

"""Extracting Conditionals to nextNode and Controller generated to Conditionals from the json file."""
conditions_to_nextstep, node_to_condition = extract_conditionals(jsonfile)
# print "\n\t CONDITION TO NEXTSTEP: ",conditions_to_nextstep
# print "\n\t NODE TO CONDITION: ",node_to_condition

actions = extract_actions(jsonfile, cnt_blk)
# print "\n\t ACTIONS:",len(actions), actions

table_actions, tbl_to_action, tbl_to_table = extract_tables_actions(jsonfile, cnt_blk, actions)
# print "\n\t TABLES: ", table_actions.keys()
# print "\n\t TABLE ACTIONS: ", table_actions

actual_nodes = []
table_conditions = []
actual_nodes = conditions_to_nextstep.keys() + table_actions.keys() + actions
table_conditions = conditions_to_nextstep.keys() + table_actions.keys()

# print "\n\tNODES(Before Removing) : ",len(nodes),nodes
# print "\n\tACTUAL NODES : ",len(actual_nodes), actual_nodes
# print "\n\t TABLE CONDITIONS: ", len(table_conditions), table_conditions
to_del=[]
for n in nodes:
	if n not in actual_nodes:
		to_del.append(n)

for d in to_del:
	nodes.remove(d)

nodes = nodes + actions
# print "\n\tNODES(After Removing + actions) : ",len(nodes),nodes

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

# print "\n\t EDGE TO DELETE : ", len(edge_to_del),edge_to_del

# print "\n\t EDGES AFTER ELIMINATING: ",len(rel_edge)
# for i in rel_edge:
# 	print(i)

edges_tuples = []
for e in edges:
	edges_tuples.append((e['src'], e['dst'], 0))
edges_tuples = list(set(edges_tuples))

##Create CFG only to get the leaf nodes.
G = nx.DiGraph()
# G.add_nodes_from(nodes)
G.add_weighted_edges_from(edges_tuples)

leaf_nodes = [v for v, d in G.out_degree() if d == 0]
start_node = [v for v, d in G.in_degree() if d == 0]
updates_edges = append_missing_edges(table_actions, edges, leaf_nodes)

# print "\n\t UPDATED EDGES: ",len(updates_edges)
# for u in updates_edges:
	# print u

G1, weighted_edges = create_cfg(updates_edges)
nx.write_gpickle(G1, file_path+"cfg.pkl")

# print "\n\t Weighted Edges:"
# for i in weighted_edges:
# 	print(weighted_edges)

extract_paths(G1, file_path)

with open(file_path+"weighted_edges.pkl",'wb') as f:
	pickle.dump(weighted_edges, f, protocol=2)

# print "\n\t WEIGHTED EDGES: ",len(weighted_edges)
# for we in weighted_edges:
# 	print(we)

augmenter(p4filename, jsonfile, dotfile, cnt_blk, meta, weighted_edges,file_path)
# nx.draw_shell(G1, with_labels = True, arrows=True) 
# plt.show()
