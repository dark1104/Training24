#include <stdio.h>
 
int main()
{
    int l;
    printf("Enter the length of array : ");
    scanf("%d",&l);
    int arr[l];
    printf("\nEnter elements in array : ");
    int i;
    for(i=0;i<l;i++)
    {
        scanf("%d",&arr[i]);
    }
    printf("\nGiven array is : \n");
    for(i=0;i<l;i++)
    {
        printf("%d\t",arr[i]);
    }
    printf("\nArray after removing duplicate elements : \n");
    int j,k;
    for(i=0;i<l;i++)
    {
        for(j=i+1;j<l;j++)
        {
            if(arr[i]==arr[j])
            {
                for(k=j; k <l-1; k++)
                {
                    arr[k] = arr[k+1];
                }
                l--;
                j--;
            }
        }
    }
    for(i=0; i<l; i++)
    {
        printf("%d\t", arr[i]);
    }
    printf("\n\n");
    return 0;
}