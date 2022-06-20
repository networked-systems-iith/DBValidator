%{
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <iostream>
#include <string.h>
#include <string>
#include <vector>
#include <fstream>

using namespace std;

//Declarations of flex that bison need
extern "C" int yylex();
extern "C" int yyparse();
extern "C" FILE *yyin;
void yyerror(const char *s);

int operand2_int, table_count=1, action_count=1;
static int assertion_count=1;
FILE * fileptr;
string str_exp, sub_exp, filter, comp_oper, log_oper, path, lhs, rhs, p4_snip, p4_code, p4_action_pass, p4_action_fail, join;
string filter_invoc, match_invoc, var_declaration;
bool membership = false;

using namespace std;

void identify_log_opr(string opr){ //To identify logical operators like AND, NOT, OR
	//printf("%s", opr);
	log_oper = opr;

	if(!str_exp.empty() and !sub_exp.empty()){
		str_exp = str_exp + log_oper + sub_exp;
		sub_exp = "";
	}	
}

void identify_comp_opr(string opr){ //To identify comparison operators like <,>,<=,>=,!=,==
	//printf("%s", opr);
	comp_oper = opr;
}

//This Function is for parsing Function calls like: function_call()
void identify_fun_path(string p){
	if(path.length()<=0){
		path = p+"()";
	}
	else{
		path = path + "_JOIN_" + p + "()";
	}
	// cout<<"FUNCTION : "<<path;
}

void identify_path(string p){
	//printf("%s", p);
	if(path.length()<=0){
		path = p;
	}
	else{
		path = path + "_JOIN_" + p;
	}
}

void add_any(){
	string s = "_JOIN_";
	if(path.find("_JOIN_") != std::string::npos){
		path.replace(path.find("_JOIN_"), s.length(), "*");
	}
}

void add_concat(){
	string s = "_JOIN_";
	if(path.find("_JOIN_") != std::string::npos){
		path.replace(path.find("_JOIN_"), s.length(), "^");
	}
	// cout<<"\nPATH : "<<path<<"\n";
}

void identify_path(string tab, string x, string acc){
	//TABLE@ACTION
	if(path.length()<=0){
		path = path + tab + x + acc;
	}
	else{
		path = path + "_JOIN_" + tab + x + acc;
	}
}

void new_fun_expr(string op1, int op2){
	char int_char[100];
	sprintf(int_char, "%d", op2);	

	if(!str_exp.empty()){
		sub_exp = op1 + "()" + comp_oper + int_char;
	}
	else{
		str_exp = op1 + "()" + comp_oper + int_char;
	}

	// cout<<"UPDATED EXPRESSION: "<<str_exp<<"\n";
}

void new_fun_expr(string op1, string op2){	

	if(!str_exp.empty()){
		sub_exp = op1 + "()" + comp_oper + op2;
	}
	else{
		str_exp = op1 + "()" + comp_oper + op2;
	}

	// cout<<"UPDATED EXPRESSION: "<<str_exp<<"\n";
}

void new_expr(string op1, string op2){
	if(!str_exp.empty()){
		sub_exp = op1 + comp_oper + op2;
	}
	else{
		str_exp = op1 + comp_oper + op2;
	}
	
	// cout<<"EXPRESSION: "<<str_exp<<"\n";
}

void new_expr_ip(string op1, string ip){
	string ip_hex;
	char oct_hex[100];
	int c=3, en=0, i=0, oct_int;

	for(i=0 ; i<ip.length() ; i++){
        if(ip[i] == '.'){
            const char *ip_char = ip.substr(en,i-en).c_str();
            sscanf(ip_char, "%d", &oct_int);
            sprintf(oct_hex, "%02X", oct_int);
            ip_hex = ip_hex + oct_hex;
            en = i+1;
        }
        
    }
        
    sscanf(ip.substr(en,i-en).c_str(), "%d", &oct_int);
    sprintf(oct_hex, "%02X", oct_int);
    ip_hex = ip_hex + oct_hex;
	if(comp_oper != "==" and comp_oper != "!="){
		cout<<"\n\nOnly \'==\' and \'!=\' can be used with IP Addresses..!!!\n\n";
		exit(0);
	}
	if(!str_exp.empty()){
		sub_exp = op1 + comp_oper + "0x" + ip_hex;
	}
	else{
		str_exp = op1 + comp_oper + "0x" + ip_hex;
	}
	
	// cout<<"EXPRESSION: "<<str_exp<<"\n";
}

void new_expr(string op1, int op2){
	char int_char[100];
	sprintf(int_char, "%d", op2);	

	if(!str_exp.empty()){
		sub_exp = op1 + comp_oper + int_char;
	}
	else{
		str_exp = op1 + comp_oper + int_char;
	}

	// cout<<"UPDATED EXPRESSION: "<<str_exp<<"\n";
}

void new_in_expr(string list){
	char num_hex[100];
	char asr_cnt[100];
	int c=3, en=0, i=0, num_int;
	string entries;
	if(lhs == ""){
		for(i=0 ; i<list.length() ; i++){
	        if(list[i] == ','){
	            const char *list_char = list.substr(en,i-en).c_str();
	            sscanf(list_char, "%d", &num_int);
	            sprintf(num_hex, "%X", num_int);
	            // ip_hex = ip_hex + oct_hex;
	            str_exp = str_exp + "\n\t0x"+num_hex+" : assert_check_pass_"+asr_cnt+"();";
	            en = i+1;
	        }
	        
	    }
	        
	    sscanf(list.substr(en,i-en).c_str(), "%d", &num_int);
	    sprintf(num_hex, "%X", num_int);
	    entries = entries + "\n\t(0x"+num_hex+",1): assert_check_pass_"+asr_cnt+"();";
	}
	else{
		for(i=0 ; i<list.length() ; i++){
	        if(list[i] == ','){
	            const char *list_char = list.substr(en,i-en).c_str();
	            sscanf(list_char, "%d", &num_int);
	            sprintf(num_hex, "%X", num_int);
	            // ip_hex = ip_hex + oct_hex;
	            str_exp = str_exp + "\n\t(0x"+num_hex+",1): assert_check_pass_"+asr_cnt+"();";
	            en = i+1;
	        }
	        
	    }
	        
	    sscanf(list.substr(en,i-en).c_str(), "%d", &num_int);
	    sprintf(num_hex, "%X", num_int);
	    entries = entries + "\n\t(0x"+num_hex+",1): assert_check_pass_"+asr_cnt+"();";
	}
}

void new_membership(string op1, string list){
	char tbl_cnt[100];
	char asr_cnt[100];
	sprintf(asr_cnt, "%d", assertion_count);
	sprintf(tbl_cnt, "%d", table_count);
	string table_def_start;
	// string entries = "\n\t("+list+",1): assert_check_pass_"+asr_cnt+"();";
	string table_def;
	string table_def_end = "\n\t} \n}\n\n//END MEMBERSHIP EXP";
	match_invoc = match_invoc + (string)"\n//BEGIN MEMBERSHIP INVOCATION \n\t\tassert_"+asr_cnt+"_"+tbl_cnt+".apply();\n\t\n//END MEMBERSHIP INVOCATION\n";
	char num_hex[100];
	int c=3, en=0, i=0, num_int;
	// cout<<"\n\tIN EXP LHS : {{"<<lhs<<"}}";
	// cout<<"\n\tIN EXP RHS : {{"<<rhs<<"}}";

	if(rhs=="" and lhs==""){
		lhs = table_def_start = (string)"\n//BEGIN MEMBERSHIP EXP\n\ttable assert_"+asr_cnt+"_"+tbl_cnt+"{\n\tkey = {\n\t\t "+op1+" : exact;\n\t}\n\tactions = {\n\t\tassert_check_pass_"+asr_cnt+";\n\t\tassert_check_fail_"+asr_cnt+";\n\t\tNoAction;\n\t}\n\tconst default_action = assert_check_fail_"+asr_cnt+";\n\tconst entries = {\n\t\t " + str_exp + table_def_end;
		// cout<<"\n\tTHIS IS LHS\n\t";
	}
	else{
		rhs = table_def_start = (string)"\n//BEGIN MEMBERSHIP EXP\n\ttable assert_"+asr_cnt+"_"+tbl_cnt+"{\n\tkey = {\n\t\t "+op1+" : exact;\n\t\tMETA_INSTANCE.assertion_check_"+asr_cnt+" : exact;\n\t}\n\tactions = {\n\t\tassert_check_pass_"+asr_cnt+";\n\t\tassert_check_fail_"+asr_cnt+";\n\t\tNoAction;\n\t}\n\tconst default_action = assert_check_fail_"+asr_cnt+";\n\tconst entries = {\n\t\t " + str_exp + table_def_end;
		// cout<<"\n\tTHIS IS RHS\n\t";
	}

	// cout<<"\n\tIN EXP LHS : {{"<<lhs<<"}}";
	// cout<<"\n\tIN EXP RHS : {{"<<rhs<<"}}";
	path = "";
	join = "";
	table_def = "";
}


void new_match_exp(){
	char asr_cnt[100];
	sprintf(asr_cnt, "%d", assertion_count);
	// cout<<"\nNEW MATCH EXP : "<<str_exp;
	// string p4_snip = "\n//BEGIN MATCH EXP\n\t\tif("+str_exp+"){\n\t\t\tassert_check_pass_"+asr_cnt+"();\n\t\t}else{\n\t\t\tassert_check_fail_"+asr_cnt+"();\n\t\t}\n//END MATCH EXP";
	if(! membership){
		p4_snip = "\n//BEGIN MATCH EXP\n\t\tif("+str_exp+"){\n\t\t\tassert_check_pass_"+asr_cnt+"();\n\t\t}else{\n\t\t\tassert_check_fail_"+asr_cnt+"();\n\t\t}\n//END MATCH EXP";
		
	}
	str_exp = "";
	rhs = rhs + p4_snip;
	// cout<<"\nNEW MATCH EXP : \n"<<rhs<<"<<<<<<<";
	p4_snip = "";
	path = "";
	join = "";
	
}

void new_match_path(){
	// p4_snip = p4_snip;
	char tbl_cnt[100];
	char asr_cnt[100];
	sprintf(asr_cnt, "%d", assertion_count);
	sprintf(tbl_cnt, "%d", table_count);
	string table_def = (string)"\n//BEGIN MATCH PATH\n\ttable assert_"+asr_cnt+"_"+tbl_cnt+"{\n\tkey = {\n\t\t META_INSTANCE.BL : exact;\n\t\tMETA_INSTANCE.assertion_check_"+asr_cnt+" : exact;\n\t}\n\tactions = {\n\t\tassert_check_pass_"+asr_cnt+";\n\t\tassert_check_fail_"+asr_cnt+";\n\t\tNoAction;\n\t}\n\tconst default_action = assert_check_fail_"+asr_cnt+";\n\tconst entries = {\n\t\t (BLCODE("+path+"),1): assert_check_pass_"+asr_cnt+"();\n\t} \n}\n\n//END MATCH PATH";

	rhs = rhs + table_def;
	match_invoc = (string)"\n//BEGIN MATCH INVOCATION \n\t\tassert_"+asr_cnt+"_"+tbl_cnt+".apply();\n\t\n//END MATCH INVOCATION\n";
	// cout<<"\nNEW MATCH PATH : \n"<<rhs;
	p4_snip = "";
	path = "";
	join = "";
}

void new_filter_exp(){
	// cout<<"\nNEW FILTER EXP : "<<str_exp;
	char asr_cnt[100];
	sprintf(asr_cnt, "%d", assertion_count);
	// cout<<(lhs.find("BEGIN FILTER MEMBERSHIP EXP") == std::string::npos)<<"#######";
	if(!membership){
		p4_snip = (string)"\n//BEGIN FILTER EXP\n\t\tif("+str_exp+"){\n\t\t\tassert_check_pass_"+asr_cnt+"();\n\t\t}else{\n\t\t\tassert_check_fail_"+asr_cnt+"();\n\t\t}\n//END FILTER EXP";
	}
	lhs = lhs + p4_snip;
	str_exp = "";
	// cout<<"\nNEW FILTER EXP : \n"<<lhs<<"<<<<<<<";
	p4_snip = "";
	path = "";
	join = "";
}

void new_filter_path(){
	char tbl_cnt[100];
	char asr_cnt[100];
	sprintf(asr_cnt, "%d", assertion_count);
	sprintf(tbl_cnt, "%d", table_count);
	string table_def = (string)"\n//BEGIN FILTER PATH\n\ttable assert_"+asr_cnt+"_"+tbl_cnt+"{\n\tkey = {\n\t\t META_INSTANCE.BL : exact;\n\t}\n\tactions = {\n\t\tassert_check_pass_"+asr_cnt+";\n\t\tassert_check_fail_"+asr_cnt+";\n\t\tNoAction;\n\t}\n\tconst default_action = assert_check_fail_"+asr_cnt+";\n\tconst entries = {\n\t\t BLCODE("+path+"): assert_check_pass_"+asr_cnt+"();\n\t} \n}\n\n//END FILTER PATH";
	lhs = lhs + table_def ;
	filter_invoc = (string)"\n//BEGIN FILTER INVOCATION \n\t\tassert_"+asr_cnt+"_"+tbl_cnt+".apply();\n\t\n//END FILTER INVOCATION\n";
	// cout<<"NEW FILTER PATH : \n"<<lhs;
	p4_snip = "";
	path = "";
	join = "";
}

void add_action_definition(){

	char acc_cnt[100];
	sprintf(acc_cnt, "%d", assertion_count);

	char asr_cnt[100];
	sprintf(asr_cnt, "%d", assertion_count);

	p4_action_pass = (string)"\n//ACTION DEF BEGIN\naction assert_check_pass_"+asr_cnt+"(){\n\tMETA_INSTANCE.assertion_check_"+asr_cnt+" = 1;\n}\n\n //ACTION DEF END\n";

	p4_action_fail = (string)"\n//ACTION DEF BEGIN\naction assert_check_fail_"+asr_cnt+"(){\n\tMETA_INSTANCE.assertion_check_"+asr_cnt+" = 0;\n}\n\n //ACTION DEF END\n";

	var_declaration = (string)"\n//META VAR DECLARE BEGIN\n\tbit<1> assertion_check_"+asr_cnt+";\n//META VAR DECLARE END";

	//lhs =  p4_action_pass + p4_action_fail + lhs;
	// cout<<p4_action_pass;
	// cout<<p4_action_fail;
	// cout<<var_declaration;

}

void create_p4_table_definition(){
	char asr_cnt[100];
	sprintf(asr_cnt, "%d", assertion_count);
	string file_name = (string)"assertion_"+asr_cnt+".txt";
	fstream file;
	file.open(file_name.c_str(), ios::out);
	// string p4_code;

	if (!file) {
		cout << "File not created!\n";
	}
	else {
		cout << "File created successfully!\n`";

		// cout<<"##LHS: "<<lhs;
		// cout<<"##RHS: "<<rhs;

		if(lhs.find("BEGIN FILTER EXP") != std::string::npos && rhs.find("BEGIN MATCH PATH") != std::string::npos){
			p4_code = p4_action_pass+p4_action_fail+"\n" + rhs+"\n"+lhs + match_invoc + "\n";

		}
		else if(lhs.find("BEGIN FILTER PATH") != std::string::npos && rhs.find("BEGIN MATCH PATH") != std::string::npos){
			p4_code = p4_action_pass+p4_action_fail+"\n" + lhs+"\n"+rhs + filter_invoc + match_invoc + "\n";
			
		}
		else if(lhs.find("BEGIN FILTER PATH") != std::string::npos && rhs.find("BEGIN MATCH EXP") != std::string::npos){
			p4_code = p4_action_pass+p4_action_fail+"\n" + lhs+"\n"+rhs + filter_invoc + "\n";
			
		}
		else if(lhs.find("BEGIN FILTER EXP") != std::string::npos && rhs.find("BEGIN MATCH EXP") != std::string::npos){
			p4_code = "\n" + lhs+"\n"+rhs+"\n";
			
		}
		else if(lhs == "" && rhs.find("BEGIN MATCH EXP") != std::string::npos){
			p4_code = "\n" + rhs+"\n"+ match_invoc + "\n";
			
		}
		else if(lhs == "" && rhs.find("BEGIN MATCH PATH") != std::string::npos){
			p4_code = p4_action_pass+p4_action_fail+"\n" + rhs+"\n"+lhs + match_invoc + "\n";
			
		}
		else if(lhs.find("BEGIN FILTER PATH") != std::string::npos && rhs.find("BEGIN MEMBERSHIP EXP") != std::string::npos){
			p4_code = p4_action_pass+p4_action_fail+"\n" + rhs+"\n"+lhs + filter_invoc + match_invoc + "\n";
			
		}
		else if(lhs.find("BEGIN FILTER EXP") != std::string::npos && rhs.find("BEGIN MEMBERSHIP EXP") != std::string::npos){
			p4_code = p4_action_pass+p4_action_fail+"\n" + rhs+"\n"+lhs + filter_invoc + match_invoc + "\n";
			
		}
		else if(lhs.find("BEGIN MEMBERSHIP EXP") != std::string::npos && rhs.find("BEGIN MEMBERSHIP EXP") != std::string::npos){
			p4_code = p4_action_pass+p4_action_fail+"\n" + rhs+"\n"+lhs + filter_invoc + match_invoc + "\n";
			
		}
		else if(lhs.find("BEGIN MEMBERSHIP EXP") != std::string::npos && rhs.find("BEGIN MEMBERSHIP EXP") == std::string::npos){
			p4_code = p4_action_pass+p4_action_fail+"\n" + rhs+"\n"+lhs + filter_invoc + match_invoc + "\n";
			
		}
		
		p4_code = p4_code + var_declaration;
		file << p4_code;
		p4_snip = "";
		p4_code = "";
		lhs = "";
		rhs = "";
		table_count = 1;
		action_count = 1;
		match_invoc = "";
		var_declaration = "";
		file.close();
	}
	
}

void table_count_up(){
	table_count++;
	action_count++;
}

void assertion_count_up(){
	assertion_count++;
}

%}

// Bison fundamentally works by asking flex to get the next token, which it
// returns as an object of type "yystype".  Initially (by default), yystype
// is merely a typedef of "int", but for non-trivial projects, tokens could
// be of any arbitrary data type.  So, to deal with that, the idea is to
// override yystype's default typedef to be a C union instead.  Unions can
// hold all of the types of tokens that Flex could return, and this means
// we can return ints or floats or strings cleanly.  Bison implements this
// mechanism with the %union directive:
%union {
  int ival;
  char *sval;
  char *hexval;
  char *ipaddrval;
  char *listval;
}

// Define the "terminal symbol" token types we are going to use (in CAPS
// by convention), and associate each with a field of the %union.
%token <ival> INT
%token <sval> STRING
%token <hexval> HEX
%token <ipaddrval> IPADDR
%token <listval> LIST
%token EQ NEQ LT GT LE GE ASSIGN
%token OR AND NOT COMMA
%token LP RP LB RB
%token AT ANY CONCAT TILDE
%token IN MATCH 
%token FILTER
%token TRUE FALSE
%start assertions

%left AND OR NOT TILDE CONCAT COMMA AT ANY
%left EQ NEQ LT GT LE GE FILTER MATCH LP RP

%%

// This is the actual grammar that bison will parse
//dbdetector: assertions {printf("Done-parsing ");}
//	 ;
//assertions: assertion 
//	  ;

assertions: | assertions assertion {printf("\nDone-parsing...!!!\n"); create_p4_table_definition(); assertion_count_up(); }
			;

assertion: filter TILDE match {}
	 | match {}
	 ;

filter: FILTER LP logicalExpr RP {new_filter_exp(); membership=false;}
      | FILTER LP path RP {add_action_definition(); new_filter_path();table_count_up();}
	;
match: MATCH LP logicalExpr RP {new_match_exp();  membership=false;}
     | MATCH LP path RP {add_action_definition(); new_match_path(); table_count_up(); }
	;

path: STRING {identify_path($1);}
   | STRING LP RP {identify_fun_path($1);}
   | STRING AT STRING  {identify_path($1,"@",$3); }
   | path ANY path {add_any(); cout<<"\n\tANY\t";}
   | path CONCAT path {add_concat(); }
   ;
  
logicalExpr: STRING logicalOp INT {new_expr($1, $3); }
	   | STRING LP RP logicalOp INT{new_fun_expr($1, $5);}
	   | STRING LP RP logicalOp TRUE{new_fun_expr($1, "(bool)1");}
	   | STRING LP RP logicalOp FALSE{new_fun_expr($1, "(bool)0");}
	   | STRING logicalOp TRUE 	{ new_expr($1, "(bool)1"); }
	   | STRING logicalOp FALSE { new_expr($1, "(bool)0"); }
	   | STRING logicalOp HEX { new_expr($1, $3); }
	   | STRING logicalOp IPADDR {new_expr_ip($1, $3); }
	   | STRING IN LB LIST RB {cout<<"LIST = "<<$4; membership=true; add_action_definition(); new_in_expr($4);new_membership($1, $4);table_count_up();}
           | logicalExpr  OR  logicalExpr {identify_log_opr(" || "); }
           | logicalExpr AND logicalExpr {identify_log_opr(" && "); }
           | LP logicalExpr RP  OR  LP logicalExpr RP
           | LP logicalExpr RP AND LP logicalExpr RP
	   | NOT LP logicalExpr RP
	   | NOT logicalExpr 
	   ;

logicalOp:GT {identify_comp_opr((char *)">"); }
	 |LT {identify_comp_opr("<"); }
     |GE {identify_comp_opr(">="); }
     |LE {identify_comp_opr("<="); }
     |EQ {identify_comp_opr((char *)"=="); }
	 |NEQ {identify_comp_opr("!="); }
	 ;

%%

int main(int argc, char **argv)
{
FILE *fp = NULL;
if (argc >= 2)
{
//printf("file name is %s", argv[1]);
fp = fopen(argv[1],"r");
}
if(fp == NULL)
{
	printf("Errror in opening file");
	return 0;
}
	
yyin = fp;
do{
yyparse();
}while(!feof(yyin));
}

void yyerror(const char *s)
{
printf("\n Parse Error \n");
exit(-1);
}
