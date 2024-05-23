#include<stdio.h>

int main()
{
    float temp;
    
    printf("Input Temprature:");
    scanf("%f", &temp);
    
    if(temp>30){
    printf("It's hot outside,stay hydrated!");
    }
    else if(temp>=20 && temp<=30){
    printf("The weather is nice and warm");
    }
    else if(temp>=10 && temp<=19){
    printf("It's a bit chilly,wear a jacket");
    }
    
    else{
    printf("it's cold outside,stay warm");
    }
    
    return 0;
    
}
