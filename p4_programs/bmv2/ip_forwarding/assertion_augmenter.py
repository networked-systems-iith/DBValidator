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

	else:
		print("Control block not found. Please specify correct control block...!!!")
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
		print("Control block not found. Please specify correct control block...!!!")
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
		print("Control block not found. Please specify correct control block...!!!")
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
	else:
		print("Control block not found. Please specify correct control block...!!!")
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
	p4_code = update_metadata_name(p4_code, meta, cnt_blk)
	with open(file_path+file_name.split('.')[0]+"_assertion.p4",'w') as f:
		f.write(p4_code)
	return p4_code

#This method will get the BL codes from the list of paths.
def get_bl_codes(path_list, path):
	bl_codes = []
	stk_nodes = []
	beg = 0
	end = 0
	
	for i in range(len(path)):

	    if path[i] in ['*','^','@']:
	        stk_nodes.append(path[beg : i])
	        stk_nodes.append(path[i])
	        end = i
	        beg = i+1
	stk_nodes.append(path[beg : i+1])

   	if len(stk_nodes)==0:
   		stk_nodes.append(path)

	for p in path_list:
		nodes_ind = []
		sorted_nodes_ind = []
		last_join = ""
		nodes = []
		for node in stk_nodes:
			if node not in ['^','@','*']:
				nodes.append(node)
				# print "\nnode : ", node
				if last_join == "" or last_join == "*":
					if node in p[0] and len(nodes_ind)==0:
						nodes_ind.append(p[0].index(node))
					elif node in p[0] and len(nodes_ind)>0:
						if p[0].index(node) > nodes_ind[-1]:
							nodes_ind.append(p[0].index(node))
				elif last_join == "^" or last_join == "@" :
					if node in p[0]:
						if len(nodes_ind)>0 and nodes_ind[-1] == p[0].index(node)-1:
							nodes_ind.append(p[0].index(node))							
			else:
				last_join = node

		sorted_nodes_ind = nodes_ind
		sorted_nodes_ind.sort()

		if nodes_ind == sorted_nodes_ind and len(nodes)==len(nodes_ind):
			bl_codes.append(p[1])
			# bl_codes.append(hex(p[1]))
	bl_codes = list(set(bl_codes))

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
	path_list = []
	paths_edges = None
	code = None
	bl_codes = list()
	bl_codes_int = list()
	bl_code_ranges = list()
	str_to_aug = ""
	with open(file_path+wel_paths, 'rb') as f:
		paths_edges = pickle.load(f)

	# Creating paths by merging the edges.[[(A,B),(C,D)],10] to [[A,B,C,D],10]
	for path in paths_edges:
		l = []
		for e in path[0]:
			l.append(str(e[0]))
		l.append(str(e[1]))
		path_list.append([l,path[1]])

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

		path = str_to_replace[len(BLCODE)+1 : len(str_to_replace)-1]

		bl_codes = get_bl_codes(path_list, path)

		bl_code_ranges = get_ranges(bl_codes)
		
		for bl in bl_code_ranges:
			str_to_aug = str_to_aug + line.replace(str_to_replace,str(hex(bl[0]))+".."+str(hex(bl[1]))) + "\n\t"

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
	list_of_files = os.listdir(file_path)
else:
	file_path = ""
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

#### UPDATING BL CODES IN PLACE OF PLACEHOLDERS ####
if 'path_list.pkl' in list_of_files:
	pass
else:
	print("\n\tFILE : path_list.pkl doesnot exist...!!!\n")
	exit(0)
p4_code = update_bl_codes(updated_p4_code,'path_list.pkl')

# file_path = os.path.split(p4filename)[0]
# print "\n\tPATH : ",file_path

with open(p4_file.split('.')[0]+"_assertion.p4",'w') as f:
	f.write(p4_code)
#############################
##### END OF MAIN BLOCK #####
#############################