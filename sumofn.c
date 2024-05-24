#include <stdio.h>
#include <stdlib.h>
int main()
{
    int n;
    printf("enter positive number:");
    scanf("%d",&n);
    if(n<0){
        printf("number invalid");
        exit(0);
    }
    int sum=0;
    int r;
    int i=0;
    
    while(n!=0){
        r = n%10;
        n = n/10;
        sum=sum+r;
        i++;
    }
    
    printf("%d",sum);
    
    return 0;
}

