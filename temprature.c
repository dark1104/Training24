#include<stdio.h>
#define CON 9/5

int main()
{
	float Celsius;
	float Fahrenheit;

	printf("Enter Celsius:");
	scanf("%f",&Celsius);

	Fahrenheit = (Celsius*CON)+32 ;
	printf("Fahrenheit: %f",Fahrenheit);
	return 0;
}
