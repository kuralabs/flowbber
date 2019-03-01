all:
	${CC} coverage_1/hello.c -fprofile-arcs -ftest-coverage --coverage -o coverage_1/hello
	$ mv *.gc* coverage_1/
	./coverage_1/hello
	$ mv *.gc* coverage_1/
	${CC} coverage_2/hello.c -fprofile-arcs -ftest-coverage --coverage -o coverage_2/hello
	$ mv *.gc* coverage_2/
	./coverage_2/hello
	$ mv *.gc* coverage_2/

clean:
	rm -rf coverage_*/hello coverage_*/*.gc*
