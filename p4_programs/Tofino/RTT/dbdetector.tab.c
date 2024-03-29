/* A Bison parser, made by GNU Bison 3.0.4.  */

/* Bison implementation for Yacc-like parsers in C

   Copyright (C) 1984, 1989-1990, 2000-2015 Free Software Foundation, Inc.

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.  */

/* As a special exception, you may create a larger work that contains
   part or all of the Bison parser skeleton and distribute that work
   under terms of your choice, so long as that work isn't itself a
   parser generator using the skeleton or a modified version thereof
   as a parser skeleton.  Alternatively, if you modify or redistribute
   the parser skeleton itself, you may (at your option) remove this
   special exception, which will cause the skeleton and the resulting
   Bison output files to be licensed under the GNU General Public
   License without this special exception.

   This special exception was added by the Free Software Foundation in
   version 2.2 of Bison.  */

/* C LALR(1) parser skeleton written by Richard Stallman, by
   simplifying the original so-called "semantic" parser.  */

/* All symbols defined below should begin with yy or YY, to avoid
   infringing on user name space.  This should be done even for local
   variables, as they might otherwise be expanded by user macros.
   There are some unavoidable exceptions within include files to
   define necessary library symbols; they are noted "INFRINGES ON
   USER NAME SPACE" below.  */

/* Identify Bison output.  */
#define YYBISON 1

/* Bison version.  */
#define YYBISON_VERSION "3.0.4"

/* Skeleton name.  */
#define YYSKELETON_NAME "yacc.c"

/* Pure parsers.  */
#define YYPURE 0

/* Push parsers.  */
#define YYPUSH 0

/* Pull parsers.  */
#define YYPULL 1




/* Copy the first part of user declarations.  */
#line 1 "dbdetector.y" /* yacc.c:339  */

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
	cout<<"\nPATH : "<<path<<"\n";
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

void new_fun_expr(string op1){	

	if(!str_exp.empty()){
		sub_exp = op1 + "()";
	}
	else{
		str_exp = op1 + "()";
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
	cout<<"\n\tIN EXP LHS : {{"<<lhs<<"}}";
	cout<<"\n\tIN EXP RHS : {{"<<rhs<<"}}";

	if(rhs=="" and lhs==""){
		lhs = table_def_start = (string)"\n//BEGIN MEMBERSHIP EXP\n\ttable assert_"+asr_cnt+"_"+tbl_cnt+"{\n\tkey = {\n\t\t "+op1+" : exact;\n\t}\n\tactions = {\n\t\tassert_check_pass_"+asr_cnt+";\n\t\tassert_check_fail_"+asr_cnt+";\n\t\tNoAction;\n\t}\n\tconst default_action = assert_check_fail_"+asr_cnt+";\n\tconst entries = {\n\t\t " + str_exp + table_def_end;
		cout<<"\n\tTHIS IS LHS\n\t";
	}
	else{
		rhs = table_def_start = (string)"\n//BEGIN MEMBERSHIP EXP\n\ttable assert_"+asr_cnt+"_"+tbl_cnt+"{\n\tkey = {\n\t\t "+op1+" : exact;\n\t\tMETA_INSTANCE.assertion_check_"+asr_cnt+" : exact;\n\t}\n\tactions = {\n\t\tassert_check_pass_"+asr_cnt+";\n\t\tassert_check_fail_"+asr_cnt+";\n\t\tNoAction;\n\t}\n\tconst default_action = assert_check_fail_"+asr_cnt+";\n\tconst entries = {\n\t\t " + str_exp + table_def_end;
		cout<<"\n\tTHIS IS RHS\n\t";
	}

	cout<<"\n\tIN EXP LHS : {{"<<lhs<<"}}";
	cout<<"\n\tIN EXP RHS : {{"<<rhs<<"}}";
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
		if(lhs != ""){
			p4_snip = (string)"\n//BEGIN MATCH EXP\n\t\tif(META_INSTANCE.assertion_check_"+asr_cnt+"==1 && "+str_exp+"){\n\t\t\tassert_check_pass_"+asr_cnt+"();\n\t\t}else{\n\t\t\tassert_check_fail_"+asr_cnt+"();\n\t\t}\n//END MATCH EXP";
		}
		if(lhs == ""){
			p4_snip = (string)"\n//BEGIN MATCH EXP\n\t\tif("+str_exp+"){\n\t\t\tassert_check_pass_"+asr_cnt+"();\n\t\t}else{\n\t\t\tassert_check_fail_"+asr_cnt+"();\n\t\t}\n//END MATCH EXP";
		}
		
		
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
	cout<<p4_action_pass;
	cout<<p4_action_fail;
	cout<<var_declaration;

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

		cout<<"##LHS: "<<lhs;
		cout<<"##RHS: "<<rhs;

		if(lhs.find("BEGIN FILTER EXP") != std::string::npos && rhs.find("BEGIN MATCH PATH") != std::string::npos){
			p4_code = p4_action_pass+p4_action_fail+"\n" + rhs+"\n"+lhs + match_invoc + "\n";
			cout<<p4_code+"THIS IS 1";
			// cout<<lhs.find("BEGIN FILTER EXP");
			// cout<<rhs.find("BEGIN MATCH PATH");
		}
		else if(lhs.find("BEGIN FILTER PATH") != std::string::npos && rhs.find("BEGIN MATCH PATH") != std::string::npos){
			p4_code = p4_action_pass+p4_action_fail+"\n" + lhs+"\n"+rhs + filter_invoc + match_invoc + "\n";
			cout<<p4_code+"THIS IS 2";
		}
		else if(lhs.find("BEGIN FILTER PATH") != std::string::npos && rhs.find("BEGIN MATCH EXP") != std::string::npos){
			p4_code = p4_action_pass+p4_action_fail+"\n" + lhs+"\n"+rhs + filter_invoc + "\n";
			cout<<p4_code+"THIS IS 3";
		}
		else if(lhs.find("BEGIN FILTER EXP") != std::string::npos && rhs.find("BEGIN MATCH EXP") != std::string::npos){
			p4_code = "\n" + lhs+"\n"+rhs+"\n";
			cout<<p4_code+"THIS IS 4";
		}
		else if(lhs == "" && rhs.find("BEGIN MATCH EXP") != std::string::npos){
			p4_code = "\n" + rhs+"\n"+ match_invoc + "\n";
			cout<<p4_code+"THIS IS 5";
		}
		else if(lhs == "" && rhs.find("BEGIN MATCH PATH") != std::string::npos){
			p4_code = p4_action_pass+p4_action_fail+"\n" + rhs+"\n"+lhs + match_invoc + "\n";
			cout<<p4_code+"THIS IS 6";
		}
		else if(lhs.find("BEGIN FILTER PATH") != std::string::npos && rhs.find("BEGIN MEMBERSHIP EXP") != std::string::npos){
			p4_code = p4_action_pass+p4_action_fail+"\n" + rhs+"\n"+lhs + filter_invoc + match_invoc + "\n";
			cout<<p4_code+"THIS IS 7";
		}
		else if(lhs.find("BEGIN FILTER EXP") != std::string::npos && rhs.find("BEGIN MEMBERSHIP EXP") != std::string::npos){
			p4_code = p4_action_pass+p4_action_fail+"\n" + rhs+"\n"+lhs + filter_invoc + match_invoc + "\n";
			cout<<p4_code+"THIS IS 8";
		}
		else if(lhs.find("BEGIN MEMBERSHIP EXP") != std::string::npos && rhs.find("BEGIN MEMBERSHIP EXP") != std::string::npos){
			p4_code = p4_action_pass+p4_action_fail+"\n" + rhs+"\n"+lhs + filter_invoc + match_invoc + "\n";
			cout<<p4_code+"THIS IS 9";
		}
		else if(lhs.find("BEGIN MEMBERSHIP EXP") != std::string::npos && rhs.find("BEGIN MEMBERSHIP EXP") == std::string::npos){
			p4_code = p4_action_pass+p4_action_fail+"\n" + rhs+"\n"+lhs + filter_invoc + match_invoc + "\n";
			cout<<p4_code+"THIS IS 10";
		}
		else{
			cout<<"##################################################################\n";
			cout<<"##LHS: "<<lhs;
			cout<<"##RHS: "<<rhs;
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


#line 492 "dbdetector.tab.c" /* yacc.c:339  */

# ifndef YY_NULLPTR
#  if defined __cplusplus && 201103L <= __cplusplus
#   define YY_NULLPTR nullptr
#  else
#   define YY_NULLPTR 0
#  endif
# endif

/* Enabling verbose error messages.  */
#ifdef YYERROR_VERBOSE
# undef YYERROR_VERBOSE
# define YYERROR_VERBOSE 1
#else
# define YYERROR_VERBOSE 0
#endif

/* In a future release of Bison, this section will be replaced
   by #include "dbdetector.tab.h".  */
#ifndef YY_YY_DBDETECTOR_TAB_H_INCLUDED
# define YY_YY_DBDETECTOR_TAB_H_INCLUDED
/* Debug traces.  */
#ifndef YYDEBUG
# define YYDEBUG 0
#endif
#if YYDEBUG
extern int yydebug;
#endif

/* Token type.  */
#ifndef YYTOKENTYPE
# define YYTOKENTYPE
  enum yytokentype
  {
    INT = 258,
    STRING = 259,
    HEX = 260,
    IPADDR = 261,
    LIST = 262,
    EQ = 263,
    NEQ = 264,
    LT = 265,
    GT = 266,
    LE = 267,
    GE = 268,
    ASSIGN = 269,
    OR = 270,
    AND = 271,
    NOT = 272,
    COMMA = 273,
    LP = 274,
    RP = 275,
    LB = 276,
    RB = 277,
    AT = 278,
    ANY = 279,
    CONCAT = 280,
    TILDE = 281,
    IN = 282,
    MATCH = 283,
    FILTER = 284,
    TRUE = 285,
    FALSE = 286
  };
#endif

/* Value type.  */
#if ! defined YYSTYPE && ! defined YYSTYPE_IS_DECLARED

union YYSTYPE
{
#line 435 "dbdetector.y" /* yacc.c:355  */

  int ival;
  char *sval;
  char *hexval;
  char *ipaddrval;
  char *listval;

#line 572 "dbdetector.tab.c" /* yacc.c:355  */
};

typedef union YYSTYPE YYSTYPE;
# define YYSTYPE_IS_TRIVIAL 1
# define YYSTYPE_IS_DECLARED 1
#endif


extern YYSTYPE yylval;

int yyparse (void);

#endif /* !YY_YY_DBDETECTOR_TAB_H_INCLUDED  */

/* Copy the second part of user declarations.  */

#line 589 "dbdetector.tab.c" /* yacc.c:358  */

#ifdef short
# undef short
#endif

#ifdef YYTYPE_UINT8
typedef YYTYPE_UINT8 yytype_uint8;
#else
typedef unsigned char yytype_uint8;
#endif

#ifdef YYTYPE_INT8
typedef YYTYPE_INT8 yytype_int8;
#else
typedef signed char yytype_int8;
#endif

#ifdef YYTYPE_UINT16
typedef YYTYPE_UINT16 yytype_uint16;
#else
typedef unsigned short int yytype_uint16;
#endif

#ifdef YYTYPE_INT16
typedef YYTYPE_INT16 yytype_int16;
#else
typedef short int yytype_int16;
#endif

#ifndef YYSIZE_T
# ifdef __SIZE_TYPE__
#  define YYSIZE_T __SIZE_TYPE__
# elif defined size_t
#  define YYSIZE_T size_t
# elif ! defined YYSIZE_T
#  include <stddef.h> /* INFRINGES ON USER NAME SPACE */
#  define YYSIZE_T size_t
# else
#  define YYSIZE_T unsigned int
# endif
#endif

#define YYSIZE_MAXIMUM ((YYSIZE_T) -1)

#ifndef YY_
# if defined YYENABLE_NLS && YYENABLE_NLS
#  if ENABLE_NLS
#   include <libintl.h> /* INFRINGES ON USER NAME SPACE */
#   define YY_(Msgid) dgettext ("bison-runtime", Msgid)
#  endif
# endif
# ifndef YY_
#  define YY_(Msgid) Msgid
# endif
#endif

#ifndef YY_ATTRIBUTE
# if (defined __GNUC__                                               \
      && (2 < __GNUC__ || (__GNUC__ == 2 && 96 <= __GNUC_MINOR__)))  \
     || defined __SUNPRO_C && 0x5110 <= __SUNPRO_C
#  define YY_ATTRIBUTE(Spec) __attribute__(Spec)
# else
#  define YY_ATTRIBUTE(Spec) /* empty */
# endif
#endif

#ifndef YY_ATTRIBUTE_PURE
# define YY_ATTRIBUTE_PURE   YY_ATTRIBUTE ((__pure__))
#endif

#ifndef YY_ATTRIBUTE_UNUSED
# define YY_ATTRIBUTE_UNUSED YY_ATTRIBUTE ((__unused__))
#endif

#if !defined _Noreturn \
     && (!defined __STDC_VERSION__ || __STDC_VERSION__ < 201112)
# if defined _MSC_VER && 1200 <= _MSC_VER
#  define _Noreturn __declspec (noreturn)
# else
#  define _Noreturn YY_ATTRIBUTE ((__noreturn__))
# endif
#endif

/* Suppress unused-variable warnings by "using" E.  */
#if ! defined lint || defined __GNUC__
# define YYUSE(E) ((void) (E))
#else
# define YYUSE(E) /* empty */
#endif

#if defined __GNUC__ && 407 <= __GNUC__ * 100 + __GNUC_MINOR__
/* Suppress an incorrect diagnostic about yylval being uninitialized.  */
# define YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN \
    _Pragma ("GCC diagnostic push") \
    _Pragma ("GCC diagnostic ignored \"-Wuninitialized\"")\
    _Pragma ("GCC diagnostic ignored \"-Wmaybe-uninitialized\"")
# define YY_IGNORE_MAYBE_UNINITIALIZED_END \
    _Pragma ("GCC diagnostic pop")
#else
# define YY_INITIAL_VALUE(Value) Value
#endif
#ifndef YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
# define YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
# define YY_IGNORE_MAYBE_UNINITIALIZED_END
#endif
#ifndef YY_INITIAL_VALUE
# define YY_INITIAL_VALUE(Value) /* Nothing. */
#endif


#if ! defined yyoverflow || YYERROR_VERBOSE

/* The parser invokes alloca or malloc; define the necessary symbols.  */

# ifdef YYSTACK_USE_ALLOCA
#  if YYSTACK_USE_ALLOCA
#   ifdef __GNUC__
#    define YYSTACK_ALLOC __builtin_alloca
#   elif defined __BUILTIN_VA_ARG_INCR
#    include <alloca.h> /* INFRINGES ON USER NAME SPACE */
#   elif defined _AIX
#    define YYSTACK_ALLOC __alloca
#   elif defined _MSC_VER
#    include <malloc.h> /* INFRINGES ON USER NAME SPACE */
#    define alloca _alloca
#   else
#    define YYSTACK_ALLOC alloca
#    if ! defined _ALLOCA_H && ! defined EXIT_SUCCESS
#     include <stdlib.h> /* INFRINGES ON USER NAME SPACE */
      /* Use EXIT_SUCCESS as a witness for stdlib.h.  */
#     ifndef EXIT_SUCCESS
#      define EXIT_SUCCESS 0
#     endif
#    endif
#   endif
#  endif
# endif

# ifdef YYSTACK_ALLOC
   /* Pacify GCC's 'empty if-body' warning.  */
#  define YYSTACK_FREE(Ptr) do { /* empty */; } while (0)
#  ifndef YYSTACK_ALLOC_MAXIMUM
    /* The OS might guarantee only one guard page at the bottom of the stack,
       and a page size can be as small as 4096 bytes.  So we cannot safely
       invoke alloca (N) if N exceeds 4096.  Use a slightly smaller number
       to allow for a few compiler-allocated temporary stack slots.  */
#   define YYSTACK_ALLOC_MAXIMUM 4032 /* reasonable circa 2006 */
#  endif
# else
#  define YYSTACK_ALLOC YYMALLOC
#  define YYSTACK_FREE YYFREE
#  ifndef YYSTACK_ALLOC_MAXIMUM
#   define YYSTACK_ALLOC_MAXIMUM YYSIZE_MAXIMUM
#  endif
#  if (defined __cplusplus && ! defined EXIT_SUCCESS \
       && ! ((defined YYMALLOC || defined malloc) \
             && (defined YYFREE || defined free)))
#   include <stdlib.h> /* INFRINGES ON USER NAME SPACE */
#   ifndef EXIT_SUCCESS
#    define EXIT_SUCCESS 0
#   endif
#  endif
#  ifndef YYMALLOC
#   define YYMALLOC malloc
#   if ! defined malloc && ! defined EXIT_SUCCESS
void *malloc (YYSIZE_T); /* INFRINGES ON USER NAME SPACE */
#   endif
#  endif
#  ifndef YYFREE
#   define YYFREE free
#   if ! defined free && ! defined EXIT_SUCCESS
void free (void *); /* INFRINGES ON USER NAME SPACE */
#   endif
#  endif
# endif
#endif /* ! defined yyoverflow || YYERROR_VERBOSE */


#if (! defined yyoverflow \
     && (! defined __cplusplus \
         || (defined YYSTYPE_IS_TRIVIAL && YYSTYPE_IS_TRIVIAL)))

/* A type that is properly aligned for any stack member.  */
union yyalloc
{
  yytype_int16 yyss_alloc;
  YYSTYPE yyvs_alloc;
};

/* The size of the maximum gap between one aligned stack and the next.  */
# define YYSTACK_GAP_MAXIMUM (sizeof (union yyalloc) - 1)

/* The size of an array large to enough to hold all stacks, each with
   N elements.  */
# define YYSTACK_BYTES(N) \
     ((N) * (sizeof (yytype_int16) + sizeof (YYSTYPE)) \
      + YYSTACK_GAP_MAXIMUM)

# define YYCOPY_NEEDED 1

/* Relocate STACK from its old location to the new one.  The
   local variables YYSIZE and YYSTACKSIZE give the old and new number of
   elements in the stack, and YYPTR gives the new location of the
   stack.  Advance YYPTR to a properly aligned location for the next
   stack.  */
# define YYSTACK_RELOCATE(Stack_alloc, Stack)                           \
    do                                                                  \
      {                                                                 \
        YYSIZE_T yynewbytes;                                            \
        YYCOPY (&yyptr->Stack_alloc, Stack, yysize);                    \
        Stack = &yyptr->Stack_alloc;                                    \
        yynewbytes = yystacksize * sizeof (*Stack) + YYSTACK_GAP_MAXIMUM; \
        yyptr += yynewbytes / sizeof (*yyptr);                          \
      }                                                                 \
    while (0)

#endif

#if defined YYCOPY_NEEDED && YYCOPY_NEEDED
/* Copy COUNT objects from SRC to DST.  The source and destination do
   not overlap.  */
# ifndef YYCOPY
#  if defined __GNUC__ && 1 < __GNUC__
#   define YYCOPY(Dst, Src, Count) \
      __builtin_memcpy (Dst, Src, (Count) * sizeof (*(Src)))
#  else
#   define YYCOPY(Dst, Src, Count)              \
      do                                        \
        {                                       \
          YYSIZE_T yyi;                         \
          for (yyi = 0; yyi < (Count); yyi++)   \
            (Dst)[yyi] = (Src)[yyi];            \
        }                                       \
      while (0)
#  endif
# endif
#endif /* !YYCOPY_NEEDED */

/* YYFINAL -- State number of the termination state.  */
#define YYFINAL  2
/* YYLAST -- Last index in YYTABLE.  */
#define YYLAST   101

/* YYNTOKENS -- Number of terminals.  */
#define YYNTOKENS  32
/* YYNNTS -- Number of nonterminals.  */
#define YYNNTS  8
/* YYNRULES -- Number of rules.  */
#define YYNRULES  35
/* YYNSTATES -- Number of states.  */
#define YYNSTATES  75

/* YYTRANSLATE[YYX] -- Symbol number corresponding to YYX as returned
   by yylex, with out-of-bounds checking.  */
#define YYUNDEFTOK  2
#define YYMAXUTOK   286

#define YYTRANSLATE(YYX)                                                \
  ((unsigned int) (YYX) <= YYMAXUTOK ? yytranslate[YYX] : YYUNDEFTOK)

/* YYTRANSLATE[TOKEN-NUM] -- Symbol number corresponding to TOKEN-NUM
   as returned by yylex, without out-of-bounds checking.  */
static const yytype_uint8 yytranslate[] =
{
       0,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     1,     2,     3,     4,
       5,     6,     7,     8,     9,    10,    11,    12,    13,    14,
      15,    16,    17,    18,    19,    20,    21,    22,    23,    24,
      25,    26,    27,    28,    29,    30,    31
};

#if YYDEBUG
  /* YYRLINE[YYN] -- Source line where rule number YYN was defined.  */
static const yytype_uint16 yyrline[] =
{
       0,   470,   470,   470,   473,   474,   477,   478,   480,   481,
     484,   485,   486,   487,   488,   491,   492,   493,   494,   495,
     496,   497,   498,   499,   500,   501,   502,   503,   504,   505,
     508,   509,   510,   511,   512,   513
};
#endif

#if YYDEBUG || YYERROR_VERBOSE || 0
/* YYTNAME[SYMBOL-NUM] -- String name of the symbol SYMBOL-NUM.
   First, the terminals, then, starting at YYNTOKENS, nonterminals.  */
static const char *const yytname[] =
{
  "$end", "error", "$undefined", "INT", "STRING", "HEX", "IPADDR", "LIST",
  "EQ", "NEQ", "LT", "GT", "LE", "GE", "ASSIGN", "OR", "AND", "NOT",
  "COMMA", "LP", "RP", "LB", "RB", "AT", "ANY", "CONCAT", "TILDE", "IN",
  "MATCH", "FILTER", "TRUE", "FALSE", "$accept", "assertions", "assertion",
  "filter", "match", "path", "logicalExpr", "logicalOp", YY_NULLPTR
};
#endif

# ifdef YYPRINT
/* YYTOKNUM[NUM] -- (External) token number corresponding to the
   (internal) symbol number NUM (which must be that of a token).  */
static const yytype_uint16 yytoknum[] =
{
       0,   256,   257,   258,   259,   260,   261,   262,   263,   264,
     265,   266,   267,   268,   269,   270,   271,   272,   273,   274,
     275,   276,   277,   278,   279,   280,   281,   282,   283,   284,
     285,   286
};
# endif

#define YYPACT_NINF -36

#define yypact_value_is_default(Yystate) \
  (!!((Yystate) == (-36)))

#define YYTABLE_NINF -1

#define yytable_value_is_error(Yytable_value) \
  0

  /* YYPACT[STATE-NUM] -- Index in YYTABLE of the portion describing
     STATE-NUM.  */
static const yytype_int8 yypact[] =
{
     -36,     1,   -36,   -17,    -7,   -36,   -12,   -36,    31,    31,
      -6,    34,    37,    45,    51,    58,    59,    65,   -36,   -36,
     -36,   -36,   -36,   -36,   -36,     3,    21,    10,     2,     7,
      45,   -36,    71,   -36,    36,    36,    45,    45,   -36,   -36,
     -36,    57,   -36,    56,   -36,   -36,   -36,   -36,   -36,    38,
      73,    -5,    32,   -36,   -36,   -36,   -36,     6,    30,    57,
     -36,    53,    63,    70,   -36,   -36,   -36,   -36,    45,    45,
     -36,    79,    81,   -36,   -36
};

  /* YYDEFACT[STATE-NUM] -- Default reduction number in state STATE-NUM.
     Performed when YYTABLE does not specify something else to do.  Zero
     means the default is an error.  */
static const yytype_uint8 yydefact[] =
{
       2,     0,     1,     0,     0,     3,     0,     5,     0,     0,
       0,    10,     0,     0,     0,     0,     0,     0,     4,    34,
      35,    31,    30,    33,    32,     0,     0,     0,     0,     0,
       0,    29,     0,     9,     0,     0,     0,     0,     8,     7,
       6,    11,    12,     0,    15,    21,    22,    19,    20,     0,
       0,     0,    10,    13,    14,    24,    25,     0,     0,     0,
      28,     0,     0,     0,    16,    17,    18,    23,     0,     0,
      11,     0,     0,    26,    27
};

  /* YYPGOTO[NTERM-NUM].  */
static const yytype_int8 yypgoto[] =
{
     -36,   -36,   -36,   -36,    67,     4,    -9,   -35
};

  /* YYDEFGOTO[NTERM-NUM].  */
static const yytype_int8 yydefgoto[] =
{
      -1,     1,     5,     6,     7,    14,    15,    28
};

  /* YYTABLE[YYPACT[STATE-NUM]] -- What to do in state STATE-NUM.  If
     positive, shift that token.  If negative, reduce the rule whose
     number is the opposite.  If YYTABLE_NINF, syntax error.  */
static const yytype_uint8 yytable[] =
{
      17,     2,     8,    31,    32,    44,    57,    45,    46,    64,
      61,    62,     9,    16,    10,    19,    20,    21,    22,    23,
      24,    50,     3,    41,    57,    42,    49,    55,    56,     3,
       4,    43,    47,    48,    27,    11,    65,    66,    53,    54,
      52,    29,    19,    20,    21,    22,    23,    24,    12,    29,
      13,    63,    67,    25,    12,    26,    30,    26,    59,    71,
      72,    27,    12,    58,    13,    19,    20,    21,    22,    23,
      24,    33,    68,    36,    37,    34,    35,    18,    38,    39,
      36,    37,    69,    34,    35,    40,    36,    37,    36,    37,
      70,    51,     0,    60,    36,    37,    36,    37,     0,    73,
       0,    74
};

static const yytype_int8 yycheck[] =
{
       9,     0,    19,    12,    13,     3,    41,     5,     6,     3,
      15,    16,    19,     9,    26,     8,     9,    10,    11,    12,
      13,    30,    28,    20,    59,     4,    19,    36,    37,    28,
      29,    21,    30,    31,    27,     4,    30,    31,    34,    35,
       4,     4,     8,     9,    10,    11,    12,    13,    17,     4,
      19,    19,    22,    19,    17,    23,    19,    23,    20,    68,
      69,    27,    17,     7,    19,     8,     9,    10,    11,    12,
      13,    20,    19,    15,    16,    24,    25,    10,    20,    20,
      15,    16,    19,    24,    25,    20,    15,    16,    15,    16,
      20,    20,    -1,    20,    15,    16,    15,    16,    -1,    20,
      -1,    20
};

  /* YYSTOS[STATE-NUM] -- The (internal number of the) accessing
     symbol of state STATE-NUM.  */
static const yytype_uint8 yystos[] =
{
       0,    33,     0,    28,    29,    34,    35,    36,    19,    19,
      26,     4,    17,    19,    37,    38,    37,    38,    36,     8,
       9,    10,    11,    12,    13,    19,    23,    27,    39,     4,
      19,    38,    38,    20,    24,    25,    15,    16,    20,    20,
      20,    20,     4,    21,     3,     5,     6,    30,    31,    19,
      38,    20,     4,    37,    37,    38,    38,    39,     7,    20,
      20,    15,    16,    19,     3,    30,    31,    22,    19,    19,
      20,    38,    38,    20,    20
};

  /* YYR1[YYN] -- Symbol number of symbol that rule YYN derives.  */
static const yytype_uint8 yyr1[] =
{
       0,    32,    33,    33,    34,    34,    35,    35,    36,    36,
      37,    37,    37,    37,    37,    38,    38,    38,    38,    38,
      38,    38,    38,    38,    38,    38,    38,    38,    38,    38,
      39,    39,    39,    39,    39,    39
};

  /* YYR2[YYN] -- Number of symbols on the right hand side of rule YYN.  */
static const yytype_uint8 yyr2[] =
{
       0,     2,     0,     2,     3,     1,     4,     4,     4,     4,
       1,     3,     3,     3,     3,     3,     5,     5,     5,     3,
       3,     3,     3,     5,     3,     3,     7,     7,     4,     2,
       1,     1,     1,     1,     1,     1
};


#define yyerrok         (yyerrstatus = 0)
#define yyclearin       (yychar = YYEMPTY)
#define YYEMPTY         (-2)
#define YYEOF           0

#define YYACCEPT        goto yyacceptlab
#define YYABORT         goto yyabortlab
#define YYERROR         goto yyerrorlab


#define YYRECOVERING()  (!!yyerrstatus)

#define YYBACKUP(Token, Value)                                  \
do                                                              \
  if (yychar == YYEMPTY)                                        \
    {                                                           \
      yychar = (Token);                                         \
      yylval = (Value);                                         \
      YYPOPSTACK (yylen);                                       \
      yystate = *yyssp;                                         \
      goto yybackup;                                            \
    }                                                           \
  else                                                          \
    {                                                           \
      yyerror (YY_("syntax error: cannot back up")); \
      YYERROR;                                                  \
    }                                                           \
while (0)

/* Error token number */
#define YYTERROR        1
#define YYERRCODE       256



/* Enable debugging if requested.  */
#if YYDEBUG

# ifndef YYFPRINTF
#  include <stdio.h> /* INFRINGES ON USER NAME SPACE */
#  define YYFPRINTF fprintf
# endif

# define YYDPRINTF(Args)                        \
do {                                            \
  if (yydebug)                                  \
    YYFPRINTF Args;                             \
} while (0)

/* This macro is provided for backward compatibility. */
#ifndef YY_LOCATION_PRINT
# define YY_LOCATION_PRINT(File, Loc) ((void) 0)
#endif


# define YY_SYMBOL_PRINT(Title, Type, Value, Location)                    \
do {                                                                      \
  if (yydebug)                                                            \
    {                                                                     \
      YYFPRINTF (stderr, "%s ", Title);                                   \
      yy_symbol_print (stderr,                                            \
                  Type, Value); \
      YYFPRINTF (stderr, "\n");                                           \
    }                                                                     \
} while (0)


/*----------------------------------------.
| Print this symbol's value on YYOUTPUT.  |
`----------------------------------------*/

static void
yy_symbol_value_print (FILE *yyoutput, int yytype, YYSTYPE const * const yyvaluep)
{
  FILE *yyo = yyoutput;
  YYUSE (yyo);
  if (!yyvaluep)
    return;
# ifdef YYPRINT
  if (yytype < YYNTOKENS)
    YYPRINT (yyoutput, yytoknum[yytype], *yyvaluep);
# endif
  YYUSE (yytype);
}


/*--------------------------------.
| Print this symbol on YYOUTPUT.  |
`--------------------------------*/

static void
yy_symbol_print (FILE *yyoutput, int yytype, YYSTYPE const * const yyvaluep)
{
  YYFPRINTF (yyoutput, "%s %s (",
             yytype < YYNTOKENS ? "token" : "nterm", yytname[yytype]);

  yy_symbol_value_print (yyoutput, yytype, yyvaluep);
  YYFPRINTF (yyoutput, ")");
}

/*------------------------------------------------------------------.
| yy_stack_print -- Print the state stack from its BOTTOM up to its |
| TOP (included).                                                   |
`------------------------------------------------------------------*/

static void
yy_stack_print (yytype_int16 *yybottom, yytype_int16 *yytop)
{
  YYFPRINTF (stderr, "Stack now");
  for (; yybottom <= yytop; yybottom++)
    {
      int yybot = *yybottom;
      YYFPRINTF (stderr, " %d", yybot);
    }
  YYFPRINTF (stderr, "\n");
}

# define YY_STACK_PRINT(Bottom, Top)                            \
do {                                                            \
  if (yydebug)                                                  \
    yy_stack_print ((Bottom), (Top));                           \
} while (0)


/*------------------------------------------------.
| Report that the YYRULE is going to be reduced.  |
`------------------------------------------------*/

static void
yy_reduce_print (yytype_int16 *yyssp, YYSTYPE *yyvsp, int yyrule)
{
  unsigned long int yylno = yyrline[yyrule];
  int yynrhs = yyr2[yyrule];
  int yyi;
  YYFPRINTF (stderr, "Reducing stack by rule %d (line %lu):\n",
             yyrule - 1, yylno);
  /* The symbols being reduced.  */
  for (yyi = 0; yyi < yynrhs; yyi++)
    {
      YYFPRINTF (stderr, "   $%d = ", yyi + 1);
      yy_symbol_print (stderr,
                       yystos[yyssp[yyi + 1 - yynrhs]],
                       &(yyvsp[(yyi + 1) - (yynrhs)])
                                              );
      YYFPRINTF (stderr, "\n");
    }
}

# define YY_REDUCE_PRINT(Rule)          \
do {                                    \
  if (yydebug)                          \
    yy_reduce_print (yyssp, yyvsp, Rule); \
} while (0)

/* Nonzero means print parse trace.  It is left uninitialized so that
   multiple parsers can coexist.  */
int yydebug;
#else /* !YYDEBUG */
# define YYDPRINTF(Args)
# define YY_SYMBOL_PRINT(Title, Type, Value, Location)
# define YY_STACK_PRINT(Bottom, Top)
# define YY_REDUCE_PRINT(Rule)
#endif /* !YYDEBUG */


/* YYINITDEPTH -- initial size of the parser's stacks.  */
#ifndef YYINITDEPTH
# define YYINITDEPTH 200
#endif

/* YYMAXDEPTH -- maximum size the stacks can grow to (effective only
   if the built-in stack extension method is used).

   Do not make this value too large; the results are undefined if
   YYSTACK_ALLOC_MAXIMUM < YYSTACK_BYTES (YYMAXDEPTH)
   evaluated with infinite-precision integer arithmetic.  */

#ifndef YYMAXDEPTH
# define YYMAXDEPTH 10000
#endif


#if YYERROR_VERBOSE

# ifndef yystrlen
#  if defined __GLIBC__ && defined _STRING_H
#   define yystrlen strlen
#  else
/* Return the length of YYSTR.  */
static YYSIZE_T
yystrlen (const char *yystr)
{
  YYSIZE_T yylen;
  for (yylen = 0; yystr[yylen]; yylen++)
    continue;
  return yylen;
}
#  endif
# endif

# ifndef yystpcpy
#  if defined __GLIBC__ && defined _STRING_H && defined _GNU_SOURCE
#   define yystpcpy stpcpy
#  else
/* Copy YYSRC to YYDEST, returning the address of the terminating '\0' in
   YYDEST.  */
static char *
yystpcpy (char *yydest, const char *yysrc)
{
  char *yyd = yydest;
  const char *yys = yysrc;

  while ((*yyd++ = *yys++) != '\0')
    continue;

  return yyd - 1;
}
#  endif
# endif

# ifndef yytnamerr
/* Copy to YYRES the contents of YYSTR after stripping away unnecessary
   quotes and backslashes, so that it's suitable for yyerror.  The
   heuristic is that double-quoting is unnecessary unless the string
   contains an apostrophe, a comma, or backslash (other than
   backslash-backslash).  YYSTR is taken from yytname.  If YYRES is
   null, do not copy; instead, return the length of what the result
   would have been.  */
static YYSIZE_T
yytnamerr (char *yyres, const char *yystr)
{
  if (*yystr == '"')
    {
      YYSIZE_T yyn = 0;
      char const *yyp = yystr;

      for (;;)
        switch (*++yyp)
          {
          case '\'':
          case ',':
            goto do_not_strip_quotes;

          case '\\':
            if (*++yyp != '\\')
              goto do_not_strip_quotes;
            /* Fall through.  */
          default:
            if (yyres)
              yyres[yyn] = *yyp;
            yyn++;
            break;

          case '"':
            if (yyres)
              yyres[yyn] = '\0';
            return yyn;
          }
    do_not_strip_quotes: ;
    }

  if (! yyres)
    return yystrlen (yystr);

  return yystpcpy (yyres, yystr) - yyres;
}
# endif

/* Copy into *YYMSG, which is of size *YYMSG_ALLOC, an error message
   about the unexpected token YYTOKEN for the state stack whose top is
   YYSSP.

   Return 0 if *YYMSG was successfully written.  Return 1 if *YYMSG is
   not large enough to hold the message.  In that case, also set
   *YYMSG_ALLOC to the required number of bytes.  Return 2 if the
   required number of bytes is too large to store.  */
static int
yysyntax_error (YYSIZE_T *yymsg_alloc, char **yymsg,
                yytype_int16 *yyssp, int yytoken)
{
  YYSIZE_T yysize0 = yytnamerr (YY_NULLPTR, yytname[yytoken]);
  YYSIZE_T yysize = yysize0;
  enum { YYERROR_VERBOSE_ARGS_MAXIMUM = 5 };
  /* Internationalized format string. */
  const char *yyformat = YY_NULLPTR;
  /* Arguments of yyformat. */
  char const *yyarg[YYERROR_VERBOSE_ARGS_MAXIMUM];
  /* Number of reported tokens (one for the "unexpected", one per
     "expected"). */
  int yycount = 0;

  /* There are many possibilities here to consider:
     - If this state is a consistent state with a default action, then
       the only way this function was invoked is if the default action
       is an error action.  In that case, don't check for expected
       tokens because there are none.
     - The only way there can be no lookahead present (in yychar) is if
       this state is a consistent state with a default action.  Thus,
       detecting the absence of a lookahead is sufficient to determine
       that there is no unexpected or expected token to report.  In that
       case, just report a simple "syntax error".
     - Don't assume there isn't a lookahead just because this state is a
       consistent state with a default action.  There might have been a
       previous inconsistent state, consistent state with a non-default
       action, or user semantic action that manipulated yychar.
     - Of course, the expected token list depends on states to have
       correct lookahead information, and it depends on the parser not
       to perform extra reductions after fetching a lookahead from the
       scanner and before detecting a syntax error.  Thus, state merging
       (from LALR or IELR) and default reductions corrupt the expected
       token list.  However, the list is correct for canonical LR with
       one exception: it will still contain any token that will not be
       accepted due to an error action in a later state.
  */
  if (yytoken != YYEMPTY)
    {
      int yyn = yypact[*yyssp];
      yyarg[yycount++] = yytname[yytoken];
      if (!yypact_value_is_default (yyn))
        {
          /* Start YYX at -YYN if negative to avoid negative indexes in
             YYCHECK.  In other words, skip the first -YYN actions for
             this state because they are default actions.  */
          int yyxbegin = yyn < 0 ? -yyn : 0;
          /* Stay within bounds of both yycheck and yytname.  */
          int yychecklim = YYLAST - yyn + 1;
          int yyxend = yychecklim < YYNTOKENS ? yychecklim : YYNTOKENS;
          int yyx;

          for (yyx = yyxbegin; yyx < yyxend; ++yyx)
            if (yycheck[yyx + yyn] == yyx && yyx != YYTERROR
                && !yytable_value_is_error (yytable[yyx + yyn]))
              {
                if (yycount == YYERROR_VERBOSE_ARGS_MAXIMUM)
                  {
                    yycount = 1;
                    yysize = yysize0;
                    break;
                  }
                yyarg[yycount++] = yytname[yyx];
                {
                  YYSIZE_T yysize1 = yysize + yytnamerr (YY_NULLPTR, yytname[yyx]);
                  if (! (yysize <= yysize1
                         && yysize1 <= YYSTACK_ALLOC_MAXIMUM))
                    return 2;
                  yysize = yysize1;
                }
              }
        }
    }

  switch (yycount)
    {
# define YYCASE_(N, S)                      \
      case N:                               \
        yyformat = S;                       \
      break
      YYCASE_(0, YY_("syntax error"));
      YYCASE_(1, YY_("syntax error, unexpected %s"));
      YYCASE_(2, YY_("syntax error, unexpected %s, expecting %s"));
      YYCASE_(3, YY_("syntax error, unexpected %s, expecting %s or %s"));
      YYCASE_(4, YY_("syntax error, unexpected %s, expecting %s or %s or %s"));
      YYCASE_(5, YY_("syntax error, unexpected %s, expecting %s or %s or %s or %s"));
# undef YYCASE_
    }

  {
    YYSIZE_T yysize1 = yysize + yystrlen (yyformat);
    if (! (yysize <= yysize1 && yysize1 <= YYSTACK_ALLOC_MAXIMUM))
      return 2;
    yysize = yysize1;
  }

  if (*yymsg_alloc < yysize)
    {
      *yymsg_alloc = 2 * yysize;
      if (! (yysize <= *yymsg_alloc
             && *yymsg_alloc <= YYSTACK_ALLOC_MAXIMUM))
        *yymsg_alloc = YYSTACK_ALLOC_MAXIMUM;
      return 1;
    }

  /* Avoid sprintf, as that infringes on the user's name space.
     Don't have undefined behavior even if the translation
     produced a string with the wrong number of "%s"s.  */
  {
    char *yyp = *yymsg;
    int yyi = 0;
    while ((*yyp = *yyformat) != '\0')
      if (*yyp == '%' && yyformat[1] == 's' && yyi < yycount)
        {
          yyp += yytnamerr (yyp, yyarg[yyi++]);
          yyformat += 2;
        }
      else
        {
          yyp++;
          yyformat++;
        }
  }
  return 0;
}
#endif /* YYERROR_VERBOSE */

/*-----------------------------------------------.
| Release the memory associated to this symbol.  |
`-----------------------------------------------*/

static void
yydestruct (const char *yymsg, int yytype, YYSTYPE *yyvaluep)
{
  YYUSE (yyvaluep);
  if (!yymsg)
    yymsg = "Deleting";
  YY_SYMBOL_PRINT (yymsg, yytype, yyvaluep, yylocationp);

  YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
  YYUSE (yytype);
  YY_IGNORE_MAYBE_UNINITIALIZED_END
}




/* The lookahead symbol.  */
int yychar;

/* The semantic value of the lookahead symbol.  */
YYSTYPE yylval;
/* Number of syntax errors so far.  */
int yynerrs;


/*----------.
| yyparse.  |
`----------*/

int
yyparse (void)
{
    int yystate;
    /* Number of tokens to shift before error messages enabled.  */
    int yyerrstatus;

    /* The stacks and their tools:
       'yyss': related to states.
       'yyvs': related to semantic values.

       Refer to the stacks through separate pointers, to allow yyoverflow
       to reallocate them elsewhere.  */

    /* The state stack.  */
    yytype_int16 yyssa[YYINITDEPTH];
    yytype_int16 *yyss;
    yytype_int16 *yyssp;

    /* The semantic value stack.  */
    YYSTYPE yyvsa[YYINITDEPTH];
    YYSTYPE *yyvs;
    YYSTYPE *yyvsp;

    YYSIZE_T yystacksize;

  int yyn;
  int yyresult;
  /* Lookahead token as an internal (translated) token number.  */
  int yytoken = 0;
  /* The variables used to return semantic value and location from the
     action routines.  */
  YYSTYPE yyval;

#if YYERROR_VERBOSE
  /* Buffer for error messages, and its allocated size.  */
  char yymsgbuf[128];
  char *yymsg = yymsgbuf;
  YYSIZE_T yymsg_alloc = sizeof yymsgbuf;
#endif

#define YYPOPSTACK(N)   (yyvsp -= (N), yyssp -= (N))

  /* The number of symbols on the RHS of the reduced rule.
     Keep to zero when no symbol should be popped.  */
  int yylen = 0;

  yyssp = yyss = yyssa;
  yyvsp = yyvs = yyvsa;
  yystacksize = YYINITDEPTH;

  YYDPRINTF ((stderr, "Starting parse\n"));

  yystate = 0;
  yyerrstatus = 0;
  yynerrs = 0;
  yychar = YYEMPTY; /* Cause a token to be read.  */
  goto yysetstate;

/*------------------------------------------------------------.
| yynewstate -- Push a new state, which is found in yystate.  |
`------------------------------------------------------------*/
 yynewstate:
  /* In all cases, when you get here, the value and location stacks
     have just been pushed.  So pushing a state here evens the stacks.  */
  yyssp++;

 yysetstate:
  *yyssp = yystate;

  if (yyss + yystacksize - 1 <= yyssp)
    {
      /* Get the current used size of the three stacks, in elements.  */
      YYSIZE_T yysize = yyssp - yyss + 1;

#ifdef yyoverflow
      {
        /* Give user a chance to reallocate the stack.  Use copies of
           these so that the &'s don't force the real ones into
           memory.  */
        YYSTYPE *yyvs1 = yyvs;
        yytype_int16 *yyss1 = yyss;

        /* Each stack pointer address is followed by the size of the
           data in use in that stack, in bytes.  This used to be a
           conditional around just the two extra args, but that might
           be undefined if yyoverflow is a macro.  */
        yyoverflow (YY_("memory exhausted"),
                    &yyss1, yysize * sizeof (*yyssp),
                    &yyvs1, yysize * sizeof (*yyvsp),
                    &yystacksize);

        yyss = yyss1;
        yyvs = yyvs1;
      }
#else /* no yyoverflow */
# ifndef YYSTACK_RELOCATE
      goto yyexhaustedlab;
# else
      /* Extend the stack our own way.  */
      if (YYMAXDEPTH <= yystacksize)
        goto yyexhaustedlab;
      yystacksize *= 2;
      if (YYMAXDEPTH < yystacksize)
        yystacksize = YYMAXDEPTH;

      {
        yytype_int16 *yyss1 = yyss;
        union yyalloc *yyptr =
          (union yyalloc *) YYSTACK_ALLOC (YYSTACK_BYTES (yystacksize));
        if (! yyptr)
          goto yyexhaustedlab;
        YYSTACK_RELOCATE (yyss_alloc, yyss);
        YYSTACK_RELOCATE (yyvs_alloc, yyvs);
#  undef YYSTACK_RELOCATE
        if (yyss1 != yyssa)
          YYSTACK_FREE (yyss1);
      }
# endif
#endif /* no yyoverflow */

      yyssp = yyss + yysize - 1;
      yyvsp = yyvs + yysize - 1;

      YYDPRINTF ((stderr, "Stack size increased to %lu\n",
                  (unsigned long int) yystacksize));

      if (yyss + yystacksize - 1 <= yyssp)
        YYABORT;
    }

  YYDPRINTF ((stderr, "Entering state %d\n", yystate));

  if (yystate == YYFINAL)
    YYACCEPT;

  goto yybackup;

/*-----------.
| yybackup.  |
`-----------*/
yybackup:

  /* Do appropriate processing given the current state.  Read a
     lookahead token if we need one and don't already have one.  */

  /* First try to decide what to do without reference to lookahead token.  */
  yyn = yypact[yystate];
  if (yypact_value_is_default (yyn))
    goto yydefault;

  /* Not known => get a lookahead token if don't already have one.  */

  /* YYCHAR is either YYEMPTY or YYEOF or a valid lookahead symbol.  */
  if (yychar == YYEMPTY)
    {
      YYDPRINTF ((stderr, "Reading a token: "));
      yychar = yylex ();
    }

  if (yychar <= YYEOF)
    {
      yychar = yytoken = YYEOF;
      YYDPRINTF ((stderr, "Now at end of input.\n"));
    }
  else
    {
      yytoken = YYTRANSLATE (yychar);
      YY_SYMBOL_PRINT ("Next token is", yytoken, &yylval, &yylloc);
    }

  /* If the proper action on seeing token YYTOKEN is to reduce or to
     detect an error, take that action.  */
  yyn += yytoken;
  if (yyn < 0 || YYLAST < yyn || yycheck[yyn] != yytoken)
    goto yydefault;
  yyn = yytable[yyn];
  if (yyn <= 0)
    {
      if (yytable_value_is_error (yyn))
        goto yyerrlab;
      yyn = -yyn;
      goto yyreduce;
    }

  /* Count tokens shifted since error; after three, turn off error
     status.  */
  if (yyerrstatus)
    yyerrstatus--;

  /* Shift the lookahead token.  */
  YY_SYMBOL_PRINT ("Shifting", yytoken, &yylval, &yylloc);

  /* Discard the shifted token.  */
  yychar = YYEMPTY;

  yystate = yyn;
  YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
  *++yyvsp = yylval;
  YY_IGNORE_MAYBE_UNINITIALIZED_END

  goto yynewstate;


/*-----------------------------------------------------------.
| yydefault -- do the default action for the current state.  |
`-----------------------------------------------------------*/
yydefault:
  yyn = yydefact[yystate];
  if (yyn == 0)
    goto yyerrlab;
  goto yyreduce;


/*-----------------------------.
| yyreduce -- Do a reduction.  |
`-----------------------------*/
yyreduce:
  /* yyn is the number of a rule to reduce with.  */
  yylen = yyr2[yyn];

  /* If YYLEN is nonzero, implement the default value of the action:
     '$$ = $1'.

     Otherwise, the following line sets YYVAL to garbage.
     This behavior is undocumented and Bison
     users should not rely upon it.  Assigning to YYVAL
     unconditionally makes the parser a bit smaller, and it avoids a
     GCC warning that YYVAL may be used uninitialized.  */
  yyval = yyvsp[1-yylen];


  YY_REDUCE_PRINT (yyn);
  switch (yyn)
    {
        case 3:
#line 470 "dbdetector.y" /* yacc.c:1646  */
    {printf("\nDone-parsing...!!!\n"); create_p4_table_definition(); assertion_count_up(); }
#line 1713 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 4:
#line 473 "dbdetector.y" /* yacc.c:1646  */
    {}
#line 1719 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 5:
#line 474 "dbdetector.y" /* yacc.c:1646  */
    {}
#line 1725 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 6:
#line 477 "dbdetector.y" /* yacc.c:1646  */
    {new_filter_exp(); membership=false;}
#line 1731 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 7:
#line 478 "dbdetector.y" /* yacc.c:1646  */
    {add_action_definition(); new_filter_path();table_count_up();}
#line 1737 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 8:
#line 480 "dbdetector.y" /* yacc.c:1646  */
    {new_match_exp();  membership=false;}
#line 1743 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 9:
#line 481 "dbdetector.y" /* yacc.c:1646  */
    {add_action_definition(); new_match_path(); table_count_up(); }
#line 1749 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 10:
#line 484 "dbdetector.y" /* yacc.c:1646  */
    {identify_path((yyvsp[0].sval)); cout<<"\n\tSTRING\t";}
#line 1755 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 11:
#line 485 "dbdetector.y" /* yacc.c:1646  */
    {identify_fun_path((yyvsp[-2].sval));}
#line 1761 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 12:
#line 486 "dbdetector.y" /* yacc.c:1646  */
    {identify_path((yyvsp[-2].sval),"@",(yyvsp[0].sval)); cout<<"\n\tAT\t";}
#line 1767 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 13:
#line 487 "dbdetector.y" /* yacc.c:1646  */
    {add_any(); cout<<"\n\tANY\t";}
#line 1773 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 14:
#line 488 "dbdetector.y" /* yacc.c:1646  */
    {add_concat(); cout<<"\n\tCONCAT\t";}
#line 1779 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 15:
#line 491 "dbdetector.y" /* yacc.c:1646  */
    {new_expr((yyvsp[-2].sval), (yyvsp[0].ival)); }
#line 1785 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 16:
#line 492 "dbdetector.y" /* yacc.c:1646  */
    {new_fun_expr((yyvsp[-4].sval), (yyvsp[0].ival));}
#line 1791 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 17:
#line 493 "dbdetector.y" /* yacc.c:1646  */
    {new_fun_expr((yyvsp[-4].sval));}
#line 1797 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 18:
#line 494 "dbdetector.y" /* yacc.c:1646  */
    {new_fun_expr((yyvsp[-4].sval));}
#line 1803 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 19:
#line 495 "dbdetector.y" /* yacc.c:1646  */
    { new_expr((yyvsp[-2].sval), "1"); }
#line 1809 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 20:
#line 496 "dbdetector.y" /* yacc.c:1646  */
    { new_expr((yyvsp[-2].sval), "0"); }
#line 1815 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 21:
#line 497 "dbdetector.y" /* yacc.c:1646  */
    { new_expr((yyvsp[-2].sval), (yyvsp[0].hexval)); }
#line 1821 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 22:
#line 498 "dbdetector.y" /* yacc.c:1646  */
    {new_expr_ip((yyvsp[-2].sval), (yyvsp[0].ipaddrval)); }
#line 1827 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 23:
#line 499 "dbdetector.y" /* yacc.c:1646  */
    {cout<<"LIST = "<<(yyvsp[-1].listval); membership=true; add_action_definition(); new_in_expr((yyvsp[-1].listval));new_membership((yyvsp[-4].sval), (yyvsp[-1].listval));table_count_up();}
#line 1833 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 24:
#line 500 "dbdetector.y" /* yacc.c:1646  */
    {identify_log_opr(" || "); }
#line 1839 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 25:
#line 501 "dbdetector.y" /* yacc.c:1646  */
    {identify_log_opr(" && "); }
#line 1845 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 30:
#line 508 "dbdetector.y" /* yacc.c:1646  */
    {identify_comp_opr((char *)">"); }
#line 1851 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 31:
#line 509 "dbdetector.y" /* yacc.c:1646  */
    {identify_comp_opr("<"); }
#line 1857 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 32:
#line 510 "dbdetector.y" /* yacc.c:1646  */
    {identify_comp_opr(">="); }
#line 1863 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 33:
#line 511 "dbdetector.y" /* yacc.c:1646  */
    {identify_comp_opr("<="); }
#line 1869 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 34:
#line 512 "dbdetector.y" /* yacc.c:1646  */
    {identify_comp_opr((char *)"=="); }
#line 1875 "dbdetector.tab.c" /* yacc.c:1646  */
    break;

  case 35:
#line 513 "dbdetector.y" /* yacc.c:1646  */
    {identify_comp_opr("!="); }
#line 1881 "dbdetector.tab.c" /* yacc.c:1646  */
    break;


#line 1885 "dbdetector.tab.c" /* yacc.c:1646  */
      default: break;
    }
  /* User semantic actions sometimes alter yychar, and that requires
     that yytoken be updated with the new translation.  We take the
     approach of translating immediately before every use of yytoken.
     One alternative is translating here after every semantic action,
     but that translation would be missed if the semantic action invokes
     YYABORT, YYACCEPT, or YYERROR immediately after altering yychar or
     if it invokes YYBACKUP.  In the case of YYABORT or YYACCEPT, an
     incorrect destructor might then be invoked immediately.  In the
     case of YYERROR or YYBACKUP, subsequent parser actions might lead
     to an incorrect destructor call or verbose syntax error message
     before the lookahead is translated.  */
  YY_SYMBOL_PRINT ("-> $$ =", yyr1[yyn], &yyval, &yyloc);

  YYPOPSTACK (yylen);
  yylen = 0;
  YY_STACK_PRINT (yyss, yyssp);

  *++yyvsp = yyval;

  /* Now 'shift' the result of the reduction.  Determine what state
     that goes to, based on the state we popped back to and the rule
     number reduced by.  */

  yyn = yyr1[yyn];

  yystate = yypgoto[yyn - YYNTOKENS] + *yyssp;
  if (0 <= yystate && yystate <= YYLAST && yycheck[yystate] == *yyssp)
    yystate = yytable[yystate];
  else
    yystate = yydefgoto[yyn - YYNTOKENS];

  goto yynewstate;


/*--------------------------------------.
| yyerrlab -- here on detecting error.  |
`--------------------------------------*/
yyerrlab:
  /* Make sure we have latest lookahead translation.  See comments at
     user semantic actions for why this is necessary.  */
  yytoken = yychar == YYEMPTY ? YYEMPTY : YYTRANSLATE (yychar);

  /* If not already recovering from an error, report this error.  */
  if (!yyerrstatus)
    {
      ++yynerrs;
#if ! YYERROR_VERBOSE
      yyerror (YY_("syntax error"));
#else
# define YYSYNTAX_ERROR yysyntax_error (&yymsg_alloc, &yymsg, \
                                        yyssp, yytoken)
      {
        char const *yymsgp = YY_("syntax error");
        int yysyntax_error_status;
        yysyntax_error_status = YYSYNTAX_ERROR;
        if (yysyntax_error_status == 0)
          yymsgp = yymsg;
        else if (yysyntax_error_status == 1)
          {
            if (yymsg != yymsgbuf)
              YYSTACK_FREE (yymsg);
            yymsg = (char *) YYSTACK_ALLOC (yymsg_alloc);
            if (!yymsg)
              {
                yymsg = yymsgbuf;
                yymsg_alloc = sizeof yymsgbuf;
                yysyntax_error_status = 2;
              }
            else
              {
                yysyntax_error_status = YYSYNTAX_ERROR;
                yymsgp = yymsg;
              }
          }
        yyerror (yymsgp);
        if (yysyntax_error_status == 2)
          goto yyexhaustedlab;
      }
# undef YYSYNTAX_ERROR
#endif
    }



  if (yyerrstatus == 3)
    {
      /* If just tried and failed to reuse lookahead token after an
         error, discard it.  */

      if (yychar <= YYEOF)
        {
          /* Return failure if at end of input.  */
          if (yychar == YYEOF)
            YYABORT;
        }
      else
        {
          yydestruct ("Error: discarding",
                      yytoken, &yylval);
          yychar = YYEMPTY;
        }
    }

  /* Else will try to reuse lookahead token after shifting the error
     token.  */
  goto yyerrlab1;


/*---------------------------------------------------.
| yyerrorlab -- error raised explicitly by YYERROR.  |
`---------------------------------------------------*/
yyerrorlab:

  /* Pacify compilers like GCC when the user code never invokes
     YYERROR and the label yyerrorlab therefore never appears in user
     code.  */
  if (/*CONSTCOND*/ 0)
     goto yyerrorlab;

  /* Do not reclaim the symbols of the rule whose action triggered
     this YYERROR.  */
  YYPOPSTACK (yylen);
  yylen = 0;
  YY_STACK_PRINT (yyss, yyssp);
  yystate = *yyssp;
  goto yyerrlab1;


/*-------------------------------------------------------------.
| yyerrlab1 -- common code for both syntax error and YYERROR.  |
`-------------------------------------------------------------*/
yyerrlab1:
  yyerrstatus = 3;      /* Each real token shifted decrements this.  */

  for (;;)
    {
      yyn = yypact[yystate];
      if (!yypact_value_is_default (yyn))
        {
          yyn += YYTERROR;
          if (0 <= yyn && yyn <= YYLAST && yycheck[yyn] == YYTERROR)
            {
              yyn = yytable[yyn];
              if (0 < yyn)
                break;
            }
        }

      /* Pop the current state because it cannot handle the error token.  */
      if (yyssp == yyss)
        YYABORT;


      yydestruct ("Error: popping",
                  yystos[yystate], yyvsp);
      YYPOPSTACK (1);
      yystate = *yyssp;
      YY_STACK_PRINT (yyss, yyssp);
    }

  YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
  *++yyvsp = yylval;
  YY_IGNORE_MAYBE_UNINITIALIZED_END


  /* Shift the error token.  */
  YY_SYMBOL_PRINT ("Shifting", yystos[yyn], yyvsp, yylsp);

  yystate = yyn;
  goto yynewstate;


/*-------------------------------------.
| yyacceptlab -- YYACCEPT comes here.  |
`-------------------------------------*/
yyacceptlab:
  yyresult = 0;
  goto yyreturn;

/*-----------------------------------.
| yyabortlab -- YYABORT comes here.  |
`-----------------------------------*/
yyabortlab:
  yyresult = 1;
  goto yyreturn;

#if !defined yyoverflow || YYERROR_VERBOSE
/*-------------------------------------------------.
| yyexhaustedlab -- memory exhaustion comes here.  |
`-------------------------------------------------*/
yyexhaustedlab:
  yyerror (YY_("memory exhausted"));
  yyresult = 2;
  /* Fall through.  */
#endif

yyreturn:
  if (yychar != YYEMPTY)
    {
      /* Make sure we have latest lookahead translation.  See comments at
         user semantic actions for why this is necessary.  */
      yytoken = YYTRANSLATE (yychar);
      yydestruct ("Cleanup: discarding lookahead",
                  yytoken, &yylval);
    }
  /* Do not reclaim the symbols of the rule whose action triggered
     this YYABORT or YYACCEPT.  */
  YYPOPSTACK (yylen);
  YY_STACK_PRINT (yyss, yyssp);
  while (yyssp != yyss)
    {
      yydestruct ("Cleanup: popping",
                  yystos[*yyssp], yyvsp);
      YYPOPSTACK (1);
    }
#ifndef yyoverflow
  if (yyss != yyssa)
    YYSTACK_FREE (yyss);
#endif
#if YYERROR_VERBOSE
  if (yymsg != yymsgbuf)
    YYSTACK_FREE (yymsg);
#endif
  return yyresult;
}
#line 516 "dbdetector.y" /* yacc.c:1906  */


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
cout<<s;
exit(-1);
}
