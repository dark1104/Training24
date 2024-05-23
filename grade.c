#include <stdio.h>

int main()
{
    int Score;
    
    printf("input your score:");
    scanf("%d",&Score);
    
    if(Score>=90 && Score<=100){
    printf("Your Grade is A");
    }
    
    else if(Score>=80 && Score<=89){
    printf("Your Grade is B");
    }
    else if (Score>=70 && Score<=79){
    printf("Your Grade is C");
    }
    else if (Score>=60 && Score<=69){
    printf("Your Grade is D");
    }
    else{
    printf("Your Grade is F");
}
    return 0;
}

