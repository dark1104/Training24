#include <stdio.h>
#include <math.h>


int main()
{
    long n;
    printf("enter a number:");
    scanf("%ld",&n);
    
    long sqr;
    sqr=sqrt(n);
    
    long a=sqr+1;
    long b=sqr*sqr;
    long c=a*a;
    long d=n-b;
    long e=c-n;
    
    if(d<=e){
        printf("closet int having whole number sqrt is %ld",b);
    }
    else{
        printf("closet int having whole number sqrt is %ld",c);
    }

    return 0;
}

