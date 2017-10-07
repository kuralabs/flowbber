#include <stdio.h>
#include <stdbool.h>

int function(bool enter) {
    printf("The answer is 42\n");
}


int main(int argc, char *argv[])
{
     function(argc>1);
     return 0;
}
