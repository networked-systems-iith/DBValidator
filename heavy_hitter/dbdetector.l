%{
#include <stdio.h>
#include "dbdetector.tab.h"  // to get the token types that we return
#define YY_DECL extern "C" int yylex()
%}
%option noyywrap
digit [0-9]+
string [a-zA-Z0-9_.]+
list [0-9]+,+[0-9, ]+
%%
[ \t\n]                    ;
"match"                   { return MATCH; }
"filter"                  { return FILTER; }
"in"                      { printf("\n\tGot IN "); return IN;}
"("                       { return LP; }
")"                       { return RP; }
"["                       { printf("\n\tGot [ ");return LB;}
"]"                       { printf("\n\tGot ]");return RB; }
"="                       { return ASSIGN; }
"=="                      { return EQ; }
"!="                      { return NEQ; }
"<"                       { return LT; }
">"                       { return GT; }
"<="                      { return LE; }
">="                      { return GE; }
"|"                       { return OR; }
"&"                       { return AND; }
","                       { return COMMA; }
"!"                       { return NOT; }
"@"                       { return AT; }
"*"                       { return ANY;}
"^"                       { return CONCAT;}
"~"                       { return TILDE;}
"true"                    { return TRUE; }
"false"                   { return FALSE; }
{list}			  { yylval.listval = strdup(yytext); printf("\n\tGot a list");return LIST;}
{digit}                   { yylval.ival = atoi(yytext); return INT;}
([1-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(\.([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])){3}   {yylval.ipaddrval = strdup(yytext); return IPADDR;}
0[xX][0-9a-fA-F]+         { yylval.hexval = strdup(yytext); return HEX;}
{string}                  { yylval.sval = strdup(yytext); return STRING;}
.                         { printf("unrecognized input "); }
%%
/*int main(int argc, char **argv)
{
FILE *fp = NULL;
fp = fopen("assertions.txt","r");
if (fp == NULL)
{
	printf("Unable to open the file");
	return 0;
}
yyin = fp;
while(yylex());
}
*/
