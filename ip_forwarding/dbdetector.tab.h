/* A Bison parser, made by GNU Bison 3.0.4.  */

/* Bison interface for Yacc-like parsers in C

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
#line 321 "dbdetector.y" /* yacc.c:1909  */

  int ival;
  char *sval;
  char *hexval;
  char *ipaddrval;
  char *listval;

#line 94 "dbdetector.tab.h" /* yacc.c:1909  */
};

typedef union YYSTYPE YYSTYPE;
# define YYSTYPE_IS_TRIVIAL 1
# define YYSTYPE_IS_DECLARED 1
#endif


extern YYSTYPE yylval;

int yyparse (void);

#endif /* !YY_YY_DBDETECTOR_TAB_H_INCLUDED  */
