#include <stdio.h>
#include <stdbool.h>

extern int yet_another(bool enter);


int function(bool enter) {
    if(enter) {
        printf("I'm in!\n");
    } else {
        printf("The answer is 42\n");
    }

    yet_another(enter);
}


int main(int argc, char *argv[])
{
     function(argc>1);
     return 0;
}
