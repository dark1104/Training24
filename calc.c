#include<stdio.h>
int main()
{
    int n1;
    int n2;
    char op;
    int ans;
    
    printf("\nEnter the operator,+,-,*,/\n");
    scanf("%c",&op);
    
    printf("Enter 2 numbers:");
    scanf("%d%d",&n1,&n2);
    
    
    switch(op){
    
    case'+':
    ans=n1+n2;
    printf("Addition is:%d",ans);
    break;

    
    case'-':
    ans=n1-n2;
    printf("Substraction is:%d",ans);
    break;
    
    
    case'*':
    ans=n1*n2;
    printf("Multiplication is:%d",ans);
    break;
    
    
    case'/':
    ans=n1/n2;
    printf("Division is:%d",ans);
    break;
    
    default:
    printf("error");
    }
    
    return 0;
    
}
