#include<stdio.h>
#define PI 3.14

int main(){
	
	float Radius;
	float Area;
	float Circumferance;

	printf("\nEnter Radius\n");
	scanf("%f",&Radius);
	Area = PI*Radius*Radius;
	printf("\n Area is%f",Area);

	Circumferance = 2 * PI * Radius;
	printf("Circumferance is%f", Circumferance);
	return 0;
}
