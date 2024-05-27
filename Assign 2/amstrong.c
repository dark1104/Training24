#include <stdio.h>
#include <math.h>
 
int main()
{
    int n;
    printf("Enter a positive number : ");
    scanf("%d",&n);
 
    int temp =n, d=0;
    while(temp!=0)
    {
        temp=temp/10;
        d++;
    }
    int temp2=n, r, ans=0;
    while(temp2!=0)
    {
        r=temp2%10;
        temp2 = temp2/10;
        ans = ans + pow(r,d);
    }
    if(ans == n)
        printf("%d is an Armstrong number",n);
    else
        printf("%d is not an Armstrong number",n);
    printf("\n\n");
    return 0;
}