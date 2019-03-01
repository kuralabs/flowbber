#include <stdio.h>
#include <stdbool.h>

int yet_another(bool enter) {
    if (false) {
        printf("The idea is that this code will never be called");
    }
}

int main(int argc, char *argv[])
{
     yet_another(argc>1);
     return 0;
}
