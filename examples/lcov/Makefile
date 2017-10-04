all:
	${CC} hello.c hello2.c -fprofile-arcs -ftest-coverage --coverage -o hello
	./hello

clean:
	rm -rf hello cov *gcda *gcno coverage.xml
