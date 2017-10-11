#include <stdlib.h>
#include <stdio.h>
#include <time.h>

// Compile with:
//  gcc -std=c99 -g -Wall -O0 -o vg vg.c
// Run with:
//  valgrind --tool=memcheck --xml=yes --xml-file=memcheck.xml --leak-check=full ./vg

int read_and_write(int* buff, int size, int seed)
{
    // Write something
    for(int i = 0; i < size; i++, seed++) {
        buff[i] = seed;
    }

    // Read something
    int result = 0;
    for(int i = 0; i < size; i++) {
        result += buff[i];
    }

    return result;
}

int main(int argc, char* argv[])
{
    srand(time(NULL));

    int buff_size = 10;
    int* buff = NULL;

    // ERR1 : Memory access violation (read and write)
    buff = (int*) malloc(sizeof(int) * buff_size);
    printf(
        "First error, go beyond memory boundaries {%d}\n",
        read_and_write(buff, buff_size + 10, rand())
    );
    free(buff);

    // ERR2 : Memory leak
    buff = (int*) malloc(sizeof(int) * buff_size);
    printf(
        "Second error, forget to free memory {%d}\n",
        read_and_write(buff, buff_size, rand())
    );

    // ERR3 : Double free
    buff = (int*) malloc(sizeof(int) * buff_size);
    printf(
        "Third error, free memory twice {%d}\n",
        read_and_write(buff, buff_size, rand())
    );
    free(buff);
    free(buff);

    return 0;
}