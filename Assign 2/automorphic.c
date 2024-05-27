#include <stdio.h>
#include<math.h>
 
int main()
{
    int n;
    printf("Enter the number : ");
    scanf("%d",&n);
    int sq = n*n;
    int temp =n;
    int digit=0;
    while(temp!=0)
    {
        temp = temp/10;
        digit++;
    }
    int temp2 = pow(10,digit);
    int temp3 = sq%temp2;
    if(temp3 == n)
        printf("%d is an automorphic number",n);
    else 
        printf("%d is not an automorphic number",n);
    printf("\n\n");
    return 0;
}