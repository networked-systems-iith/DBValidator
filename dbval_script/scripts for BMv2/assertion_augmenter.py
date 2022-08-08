import os, os.path
import re
import sys
from collections import deque
import pickle

p4_file = ""
control_block = ""

BEGIN_MATCH_PATH = "BEGIN MATCH PATH"
END_MATCH_PATH = "END MATCH PATH"
BEGIN_MATCH_EXP = "BEGIN MATCH EXP"
END_MATCH_EXP = "END MATCH EXP"
BEGIN_FILTER_EXP = "BEGIN FILTER EXP"
END_FILTER_EXP = "END FILTER EXP"
BEGIN_FILTER_PATH = "BEGIN FILTER PATH"
END_FILTER_PATH = "END FILTER PATH"
ACTION_DEF_BEGIN = "ACTION DEF BEGIN"
ACTION_DEF_END = "ACTION DEF END"
BEGIN_MATCH_INVOCATION = "BEGIN MATCH INVOCATION"
END_MATCH_INVOCATION = "END MATCH INVOCATION"
BEGIN_FILTER_INVOCATION = "BEGIN FILTER INVOCATION"
END_FILTER_INVOCATION = "END FILTER INVOCATION"
META_VAR_DECLARE_BEGIN = "META VAR DECLARE BEGIN"
META_VAR_DECLARE_END = "META VAR DECLARE END"
META_VAR_INSTANCE = "META_INSTANCE" #Replace this keyword with Instance name for metadata variable.
BEGIN_MEMBERSHIP_INVOCATION = "BEGIN MEMBERSHIP INVOCATION"
END_MEMBERSHIP_INVOCATION = "END MEMBERSHIP INVOCATION"
BEGIN_MEMBERSHIP_EXP = "BEGIN MEMBERSHIP EXP"
END_MEMBERSHIP_EXP = "END MEMBERSHIP EXP"
BLCODE = "BLCODE"

def aug_action_def(code, action_def, cnt_blk):
	pat = re.compile(r'control[\s]+{}[\s]*\('.format(cnt_blk))
	ind_cnt_blk = re.search(pat, code)
	if ind_cnt_blk is not None:
		ind = code.find("{", ind_cnt_blk.span()[1])
		code = code[0:ind+1] + action_def + code[ind+2:]

		print "\nACTION DEF: ", action_def
	else:
		print("1) Control block not found. Please specify correct control block...!!!")
		exit(0)

	return code

def aug_match_path(code, match_path, cnt_blk): # USING MATCH-ACTION TABLES 
	# ind_cnt_blk = code.find("{", code.find(cnt_blk))
	pat = re.compile(r'control[\s]+{}[\s]*\('.format(cnt_blk))
	ind_cnt_blk = re.search(pat, code)
	if ind_cnt_blk is not None:
		ind = ind_cnt_blk.span()[1]
		ind = code.find("{",ind)
		code = code[0:ind+1] + match_path + code[ind+2:]
	else:
		print("1) Control block not found. Please specify correct control block...!!!")
		exit(0)
	# code = code[0:ind_cnt_blk+1] + match_path + code[ind_cnt_blk+2:]

	return code

def aug_filter_path(code, filter_path, cnt_blk): # USING MATCH-ACTION TABLES 
	pat = re.compile(r'control[\s]+{}[\s]*\('.format(cnt_blk))
	ind_cnt_blk = re.search(pat, code)
	if ind_cnt_blk is not None:
		ind = ind_cnt_blk.span()[1]
		ind = code.find("{",ind)
		code = code[0:ind+1] + filter_path + code[ind+2:]
	else:
		print("2) Control block not found. Please specify correct control block...!!!")
		exit(0)

	return code

def aug_apply_block(code, apply_block, cnt_blk):
	#Finding the index of closed curly braces of the apply{} block.
	pat = re.compile(r'control[\s]+{}[\s]*\('.format(cnt_blk))
	ind_cnt_blk = re.search(pat, code)
	ind = None
	ind_apply = None
	if ind_cnt_blk is not None:
		ind = ind_cnt_blk.span()[1]
		ind_apply = code.find("{", code.find('apply {',ind))
		# p = re.compile(r'apply {')
		# ind_apply = re.search(p, code[ind:]).span()
		# code = code[0:ind_apply[1]+1] + apply_block + code[ind_apply[1]+2:]
		print("\n#######1))"+code[ind_apply-50:ind_apply+50])
		
	else:
		print("3) Control block not found. Please specify correct control block...!!!")
		exit(0)
	
	stk = deque()

	for i in range(ind_apply, len(code)-1):
	    if code[i] == '{':
	        stk.append(code[i])
	    elif code[i] == '}':
	        stk.pop()
	    if not stk:
	        ind = i
	        break
	
	code = code[0:ind-1] + apply_block + code[ind:]

	return code

#This method will update the user metadata with new variables to be used for tracking Assertions.
def update_metadata(code, var_names, meta):
	ind_meta = code.find("{", code.find("struct "+meta))
	str_to_aug = ""

	for i in var_names:
		str_to_aug = str_to_aug + i
	code = code[:ind_meta+1] + str_to_aug + code[ind_meta+2:]
	return code

#This method will update the user metadata with new variables to be used for tracking Assertions in header.p4 file if exist.
def update_metadata_file(var_names, meta, header):
	str_to_aug = ""

	for i in var_names:
		str_to_aug = str_to_aug + "\n\t" + i
	print "\n\tHEADER : ",str_to_aug
	print "\n\tHEADER : ",header
	with open(header,'r') as h:
		head = h.read()
		index = head.find('{', head.find('struct '+meta)) + 1
		head = head[0:index+1] + str_to_aug + head[index+1 : ]

	with open(header,'w') as h:
		h.write(head)

#This method will update the placeholder with the instance name of the user metadata.
def update_metadata_name(code, meta_name, cnt_blk):
	pat = re.compile(r'control[\s]+{}[\s]*\('.format(cnt_blk))
	ind_cnt_blk = re.search(pat, code)

	print("\n\t SwitchIngress: ",code[ind_cnt_blk.span()[0] : ind_cnt_blk.span()[1]])
	name = ""
	if ind_cnt_blk is not None:
		ind_beg = code.find(meta_name, ind_cnt_blk.span()[1]) + len(meta_name)
		ind_end = code.find(',',ind_beg)
		name = code[ind_beg:ind_end].strip()
	code = code.replace(META_VAR_INSTANCE, name.strip())
	return code


def assert_augmenter(p4_file, assert_list, cnt_blk, meta, header):
	str_to_augment = ""
	p4_code = ""
	file_name = os.path.split(p4_file)[1]
	file_path = os.path.split(p4_file)[0]

	if file_path != "":
		file_path = file_path+'/'
	else:
		file_path = ""

	with open(p4_file,'r') as f:
		p4_code = f.read()


	#Augmenting Table Definition for Filter in the P4 code.
	for asser in assert_list:
		with open(file_path+asser,'r') as a:
			a_code = a.read()
			for i,j in zip([m.start() for m in re.finditer(BEGIN_FILTER_PATH, a_code)],[m.start() for m in re.finditer(END_FILTER_PATH, a_code)]):
				str_to_augment = a_code[i+ len(BEGIN_FILTER_PATH) : j-2]				
				
				p4_code = aug_match_path(p4_code, str_to_augment, cnt_blk)

		#Augmenting Table Definition in the P4 code.
		with open(file_path+asser,'r') as a:
			a_code = a.read()
			for i,j in zip([m.start() for m in re.finditer(BEGIN_MATCH_PATH, a_code)],[m.start() for m in re.finditer(END_MATCH_PATH, a_code)]):
				str_to_augment = a_code[i+ len(BEGIN_MATCH_PATH) : j-2]				
				
				p4_code = aug_match_path(p4_code, str_to_augment, cnt_blk)

		#Augmenting Membership Table Definition in the P4 code.
		with open(file_path+asser,'r') as a:
			a_code = a.read()
			for i,j in zip([m.start() for m in re.finditer(BEGIN_MEMBERSHIP_EXP, a_code)],[m.start() for m in re.finditer(END_MEMBERSHIP_EXP, a_code)]):
				str_to_augment = a_code[i+ len(BEGIN_MEMBERSHIP_EXP) : j-2]				
				
				p4_code = aug_action_def(p4_code, str_to_augment, cnt_blk)
	
		#Augmenting Action Definition in the P4 code.
		with open(file_path+asser,'r') as a:
			a_code = a.read()
			for i,j in zip([m.start() for m in re.finditer(ACTION_DEF_BEGIN, a_code)],[m.start() for m in re.finditer(ACTION_DEF_END, a_code)]):
				str_to_augment = a_code[i+ len(ACTION_DEF_BEGIN) : j-2]				
				
				p4_code = aug_action_def(p4_code, str_to_augment, cnt_blk)	

	#Augment Table Invocation and IF/ESE.
	var_to_augment = []
	str_to_augment = ""
	for asser in assert_list[::-1]:
		with open(file_path+asser,'r') as a:
			a_code = a.read()
			
			for i,j in zip([m.start() for m in re.finditer(BEGIN_FILTER_EXP, a_code)],[m.start() for m in re.finditer(END_FILTER_EXP, a_code)]):
				str_to_augment = str_to_augment + a_code[i+ len(BEGIN_FILTER_EXP) : j-2]							
			for i,j in zip([m.start() for m in re.finditer(BEGIN_FILTER_INVOCATION, a_code)],[m.start() for m in re.finditer(END_FILTER_INVOCATION, a_code)]):
				str_to_augment = str_to_augment + a_code[i+ len(BEGIN_FILTER_INVOCATION) : j-2]	
			for i,j in zip([m.start() for m in re.finditer(BEGIN_MATCH_EXP, a_code)],[m.start() for m in re.finditer(END_MATCH_EXP, a_code)]):
				str_to_augment = str_to_augment + a_code[i+ len(BEGIN_MATCH_EXP) : j-2]		
			for i,j in zip([m.start() for m in re.finditer(BEGIN_MATCH_INVOCATION, a_code)],[m.start() for m in re.finditer(END_MATCH_INVOCATION, a_code)]):
				str_to_augment = str_to_augment + a_code[i+ len(BEGIN_MATCH_INVOCATION) : j-2]	
			for i,j in zip([m.start() for m in re.finditer(BEGIN_MEMBERSHIP_INVOCATION, a_code)],[m.start() for m in re.finditer(END_MEMBERSHIP_INVOCATION, a_code)]):
				str_to_augment = str_to_augment + a_code[i+ len(BEGIN_MEMBERSHIP_INVOCATION) : j-2]

			for i,j in zip([m.start() for m in re.finditer(META_VAR_DECLARE_BEGIN, a_code)],[m.start() for m in re.finditer(META_VAR_DECLARE_END, a_code)]):
				var_to_augment.append(a_code[i+ len(META_VAR_DECLARE_BEGIN) : j-2])
	
	## Identify the Variable instance name of User Metadata.

	var_to_augment = list(set(var_to_augment))		
	p4_code = aug_apply_block(p4_code, str_to_augment, cnt_blk)	
	if header == "":
		p4_code = update_metadata(p4_code,var_to_augment, meta)
	else:
		update_metadata_file(var_to_augment, meta, header)
		print "\n\t CALLING : update_metadata_file"
	p4_code = update_metadata_name(p4_code, meta, cnt_blk)
	with open(file_path+file_name.split('.')[0]+"_assertion.p4",'w') as f:
		f.write(p4_code)
	return p4_code

#This method will get the BL codes from the list of paths.
def get_bl_codes(wel_paths, paths):
	bl_codes = []
	stk_nodes = []
	beg = 0
	end = 0
	for i in range(len(paths)):
		if paths[i] in ['*','^','@']:
			stk_nodes.append(paths[beg : i])
			stk_nodes.append(paths[i])
			end = i
			beg = i+1
	stk_nodes.append(paths[beg : i+1])
	print("\nPATH NODE LIST : ",stk_nodes)
	if len(stk_nodes)==0:
		stk_nodes.append(paths)
	intermediate_nodes= []
	intermediate_nodes= stk_nodes

	with open(file_path+wel_paths, 'rb') as f:
		paths_edges= pickle.load(f)
	labels=nx.get_edge_attributes(paths_edges, 'weight')
	#print(labels)


	leaf_nodes1 = [v for v, d in paths_edges.out_degree() if d == 0]
	print ("\n\t LEAF NODES: ", leaf_nodes1)
	print(type(leaf_nodes1))
	start_node = [v for v, d in paths_edges.in_degree() if d == 0]
	print("start node",start_node)
	source_node = start_node[0]
	destination_node =leaf_nodes1
	final_list = [[source_node]]
	
	if len(intermediate_nodes)==0:
		for destination_node in destination_nodes:
			for path in nx.all_simple_paths(paths_edges, source= source_node, target= destination_node):
				print(path)
			final_list.append(path)
	else:
		consecutive_symbols = False
		no_symbol_in_start_end = False
		for node in source_node:
			if node in ['@',"*","^"]:
				no_symbol_in_start_end = True
				print("Error : Starting node cannot be symbol")
				break
		for node in destination_node:
			if node in ['@',"*","^"]:
				print("Error : Leaf node cannot be symbol")
				break
		length_intermediate_nodes = len(intermediate_nodes)
		
		if length_intermediate_nodes>1:
			i=0
			while(i<length_intermediate_nodes-1):
				if (intermediate_nodes[i] in ['@',"*","^"]) and (intermediate_nodes[(i+1)] in ['@',"*","^"]):
					print("Error : Two consecutive nodes cannot be symbol, ",intermediate_nodes[i]," at position ",i,", ",intermediate_nodes[i+1]," at position ",i+1)
					consecutive_symbols = True
					break
				i+=1
		if(consecutive_symbols==False and no_symbol_in_start_end==False):
			all_nodes = []
			all_nodes.append(source_node)
			for intermediate_node in intermediate_nodes:
				all_nodes.append(intermediate_node)
			all_nodes.append(destination_node)
			print("all_nodes", all_nodes)
			
			length_all_nodes = len(all_nodes)
			
			i = 0
			is_path_broken = False
			is_multiple_path_exist_in_at_sign = False
			while(i<length_all_nodes-1):

				if all_nodes[(i+1)] in ['@','*','^']:
					if all_nodes[(i+1)] == '@':
						direct_path_exist = False
						temporary_list_1 =[]
						temporary_list_2 = []
						temporary_no_of_paths = 0
						temporary_no_of_paths2 = 0
						if type(all_nodes[i+2])==list:
							for index_of_list_in_all_nodes in all_nodes[i+2]:
								for path in nx.all_simple_paths(paths_edges, source= all_nodes[i], target= index_of_list_in_all_nodes, cutoff=1):
									direct_path_exist = True
									path.remove(all_nodes[i])
									temporary_list_1.append(path)
									temporary_no_of_paths += 1
								if direct_path_exist == True:
									for path in nx.all_simple_paths(paths_edges, source= all_nodes[i], target= index_of_list_in_all_nodes):
										temporary_no_of_paths2 += 1
									if (temporary_no_of_paths == temporary_no_of_paths2):
										for j in final_list:
											for k in temporary_list_1:
												temp_path = j+k
												temporary_list_2.append(temp_path)
										final_list = temporary_list_2
									else:
										is_multiple_path_exist_in_at_sign = True
										break
								else:
									is_path_broken = True
									break
							i+=2
						else:
							for path in nx.all_simple_paths(paths_edges, source= all_nodes[i], target= all_nodes[i+2], cutoff=1):
								direct_path_exist = True
								path.remove(all_nodes[i])
								temporary_list_1.append(path)
								temporary_no_of_paths += 1
							if direct_path_exist == True:
								for path in nx.all_simple_paths(paths_edges, source= all_nodes[i], target= all_nodes[i+2]):
									temporary_no_of_paths2 += 1
								if (temporary_no_of_paths == temporary_no_of_paths2):
									for j in final_list:
										for k in temporary_list_1:
											temp_path = j+k
											temporary_list_2.append(temp_path)
									final_list = temporary_list_2
								else:
									is_multiple_path_exist_in_at_sign = True
									break
							else:
								is_path_broken = True
								break
							i+=2
					elif all_nodes[(i+1)] == "*":
						
						temporary_list_1 =[]
						temporary_list_2 = []
						if type(all_nodes[i+2])==list:
							
							for index_of_list_in_all_nodes in all_nodes[i+2]:
								for path in nx.all_simple_paths(paths_edges, source= all_nodes[i], target= index_of_list_in_all_nodes):
									path.remove(all_nodes[i])
									temporary_list_1.append(path)
							for j in final_list:
								for k in temporary_list_1:
									temp_path = j+k
									temporary_list_2.append(temp_path)
							final_list = temporary_list_2
							i+=2
						else:
							
							for path in nx.all_simple_paths(paths_edges, source= all_nodes[i], target= all_nodes[i+2]):
								path.remove(all_nodes[i])
								temporary_list_1.append(path)
							for j in final_list:
								for k in temporary_list_1:
									temp_path = j+k
									temporary_list_2.append(temp_path)
							final_list = temporary_list_2
							print("temp_final_list", final_list)
							i+=2
					elif all_nodes[(i+1)] == '^':
						direct_path_exist = False
						temporary_list_1 =[]
						temporary_list_2 = []
						if type(all_nodes[i+2])==list:
							for index_of_list_in_all_nodes in all_nodes[i+2]:
								for path in nx.all_simple_paths(paths_edges, source= all_nodes[i], target= index_of_list_in_all_nodes, cutoff=1):
									direct_path_exist = True
									path.remove(all_nodes[i])
									temporary_list_1.append(path)
							if direct_path_exist == True:
								for j in final_list:
									for k in temporary_list_1:
										temp_path = j+k
										temporary_list_2.append(temp_path)
								final_list = temporary_list_2
							else:
								is_path_broken = True
								break
							i+=2
						else:
							for path in nx.all_simple_paths(paths_edges, source= all_nodes[i], target= all_nodes[i+2], cutoff=1):
								direct_path_exist = True
								path.remove(all_nodes[i])
								temporary_list_1.append(path)
							if direct_path_exist == True:
								for j in final_list:
									for k in temporary_list_1:
										temp_path = j+k
										temporary_list_2.append(temp_path)
								final_list = temporary_list_2
							else:
								is_path_broken = True
								break
							i+=2
				else:
					temporary_list_1 =[]
					temporary_list_2 = []
					if type(all_nodes[i+1])==list:
						for index_of_list_in_all_nodes in all_nodes[i+1]:
							for path in nx.all_simple_paths(paths_edges, source= all_nodes[i], target= index_of_list_in_all_nodes):
								path.remove(all_nodes[i])
								temporary_list_1.append(path)
						for j in final_list:
							for k in temporary_list_1:
								temp_path = j+k
								temporary_list_2.append(temp_path)
						final_list = temporary_list_2
						i+=1
					else:
						
						for path in nx.all_simple_paths(paths_edges, source= all_nodes[i], target= all_nodes[i+1]):
							path.remove(all_nodes[i])
							temporary_list_1.append(path)
						for j in final_list:
							for k in temporary_list_1:
								temp_path = j+k
								temporary_list_2.append(temp_path)
						final_list = temporary_list_2
						
						i+=1	
	if (not is_path_broken) and (not is_multiple_path_exist_in_at_sign):
		print(final_list)
	else:
		if is_path_broken:
			final_list = []
			print("Path Not Exist between ",all_nodes[i]," and ",all_nodes[i+2])
		if is_multiple_path_exist_in_at_sign:
			final_list = []
			print("Multiple Path Exist between ",all_nodes[i]," and ",all_nodes[i+2]," in the @ clouse")


	print("\n\n\nFinal List that contains intermediate nodes :\n\n", final_list)
	path_list_edges = []
	for path in map(nx.utils.pairwise, final_list):
		path_list_edges.append(list(path))
	path_list1 =[]
	for i in path_list_edges:
		weight_sum =0
		in_list =[]
		for j in i:
			weight_sum += labels[j]
			in_list.append(j)
		in_list2=[]
		in_list2.append(in_list)
		in_list2.append(weight_sum)
		path_list1.append(in_list2)
	final_path_list = []
	for path in path_list1:
		l = []
		for e1 in path[0]:
			l.append(str(e1[0]))
		l.append(str(e1[1]))
		final_path_list.append([l,path[1]])
	print( "\nPATHS : ", final_path_list)
	list5=[]
	for i in final_path_list:
		list5.append(i[1])
	bl_codes = list(set(list5))
	print(type(bl_codes))
	print(len(bl_codes))
	return bl_codes
	

##This method convert list of BL code into ranges.
def get_ranges(bl):
	bl_int = list()
	for i in bl:
		bl_int.append(int(i))

	bl_int = sorted(set(bl_int))
	gaps = [[s, e] for s, e in zip(bl_int, bl_int[1:]) if s+1 < e]
	edges = iter(bl_int[:1] + sum(gaps, []) + bl_int[-1:])
	return list(zip(edges, edges))

#### UPDATE BLCODES ##
def update_bl_codes(p4_code, wel_paths):
	import networkx as nx
	

	for x in range(p4_code.count("BLCODE")):
		# i = re.search(BLCODE, p4_code)
		# i = i.span()
		i = p4_code.find(BLCODE)
		j = p4_code.find(';',i)
		str_to_aug = ""

		if p4_code[i-1] == '(':
			line = p4_code[i-1:j+1]
			x = line.rfind(')',0,line.rfind(',',0,line.find(':',i)))
			str_to_replace = line[line.find(BLCODE):x+1]
		else:
			line = p4_code[i:j+1]
			x = line.find(')',0,line.find(':',i))
			str_to_replace = line[line.find(BLCODE):x+1]

		print "\n LINE : ", line,"\n"
		
		
		print "\nstr_to_replace : ",str_to_replace ,'\n'

		path = str_to_replace[len(BLCODE)+1 : len(str_to_replace)-1]

		bl_codes = get_bl_codes(wel_paths, path)

		bl_code_ranges = get_ranges(bl_codes)
		
		#print("\n\tBL CODES: ", type(bl_codes[0]), bl_codes)

		# for bl in bl_codes:
		# 	str_to_aug = str_to_aug + line.replace(str_to_replace,str(bl)) + "\n\t"
		
		for bl in bl_code_ranges:
			str_to_aug = str_to_aug + line.replace(str_to_replace,str(hex(bl[0]))+".."+str(hex(bl[1]))) + "\n\t"

		print(str_to_aug)

		p4_code = p4_code[0:i-2] + str_to_aug + p4_code[j+1:]
	return p4_code
	
#############################
#### START OF MAIN BLOCK ####
#############################
p4_file = ""
control_block = ""
meta_name = ""

if len(sys.argv) != 5 and len(sys.argv) != 4:
	print("\n\tPLEASE SPECIFY <P4 FILE NAME> <CONTROL BLOCK NAME> <USER METADATA NAME(eg: metadata_t)> <header.p4> or \"\"")
	exit(0)
else:
	print("P4 FILE NAME = ",sys.argv[1])
	p4_file = sys.argv[1]
	control_block = sys.argv[2]
	meta_name = sys.argv[3]
	if len(sys.argv) == 5:
		header = str(sys.argv[4])
	else:
		header = ""

file_path = os.path.split(p4_file)[0]
if file_path != "":
	file_path = file_path+'/'
	print "\n\tPATH : ",'/'+file_path
	list_of_files = os.listdir(file_path)
else:
	file_path = ""
	print "\n\tPATH : ",os.getcwd()+'/'+file_path
	list_of_files = os.listdir(os.getcwd())



if len(list_of_files) == 0:
	print("\n\tNo Assertions created...!!!\n")
	exit(0)

dict_of_files = {}
sorted_list_of_files = []

p = re.compile('assertion_[0-9]+')
for l in list_of_files:
	m = p.match(l)
	if m is not None:
		dict_of_files[int(((l.split('.')[0]).split('_')[1]))] = l


for k in sorted(dict_of_files.keys()):
	sorted_list_of_files.append(dict_of_files[k])

#### AUGMENTINg ASSERTIONS ####
updated_p4_code = ""
updated_p4_code = assert_augmenter(p4_file, sorted_list_of_files[::-1], control_block, meta_name, header)
import networkx as nx
#### UPDATING BL CODES IN PLACE OF PLACEHOLDERS ####
if 'cfg.pkl' in list_of_files:
	print("\n\tcfg.pkl EXIST....!!!!\n")
else:
	print("\n\tFILE : cfg.pkl doesnot exist...!!!\n")
	exit(0)
infile = open("cfg.pkl",'rb')
new_dict1 = pickle.load(infile)

labels=nx.get_edge_attributes(new_dict1, 'weight')
#print(labels)


p4_code = update_bl_codes(updated_p4_code,'cfg.pkl')

# file_path = os.path.split(p4filename)[0]
# print "\n\tPATH : ",file_path

with open(p4_file.split('.')[0]+"_assertion.p4",'w') as f:
	f.write(p4_code)
#############################
##### END OF MAIN BLOCK #####
#############################