#include <stdio.h>
 
int main()
{
    int n;
    printf("Enter the size of array : ");
    scanf("%d",&n);
    int arr[n];
    printf("Enter the elements of array : ");
    int i,j;
    for(i=0;i<n;i++)
        scanf("%d",&arr[i]);
    printf("\nLeaders in array is/are : ");
    for(i=0;i<n;i++)
    {
        int count =0;
        for(j=i+1;j<n;j++)
        {
            if(arr[i]>arr[j])
            {
                count++;
            }
        }
        if(count==n-i-1)
        {
            printf("%d ",arr[i]);
        }
    }
    printf("\n\n");
    return 0;
}
has context menu