poise: parse 
#       g++ ast-tofino.c poise.tab.c lex.yy.c -ll -o ./poise-tofino --std=c++0x
	g++ dbdetector.tab.c lex.yy.c -lfl -o dbdetector

parse:
	bison -d dbdetector.y
	flex dbdetector.l

clean:
	rm -rf dbdetector.tab.c dbdetector.tab.h lex.yy.c dbdetector assertion_tab_def.p4 
	find ./ -name 'assertion_*.txt' -delete

build:
	./dbdetector assertions
