all:
	gcc -std=c99 -g -Wall -O0 -o vg vg.c
	valgrind --tool=memcheck --xml=yes --xml-file=memcheck.xml --leak-check=full ./vg

clean:
	rm vg
