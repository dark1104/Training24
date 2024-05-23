#include<stdio.h>

int main()
{
    float weight;
    float height;
    float BMI;
    
    printf("Enter Weight in KG:");
    scanf("%f",&weight);
    
    printf("Enter Height in m:");
    scanf("%f",&height);
    
    BMI = weight/(height*height);
    printf("Your BMI is:%f",BMI);
    
    if(BMI>18.5){
        printf("\nUnderweight\n");
    }
    
    else if(BMI>=18.5 && BMI<=24.9){
        printf("Normal weight");
    }
    else if(BMI>=25 && BMI<=29.9){
        printf("Overweight");
    }
    else{
        printf("Obesity");
    }
    printf("/n");
    return 0;

}
