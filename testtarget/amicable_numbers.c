// NO DEBUG-INFO:
// clang -target x86_64-apple-macos -arch x86_64 -o amicable_numbers amicable_numbers.c
//
// WITH DEBUG-INFO:
// clang -g -target x86_64-apple-macos -arch x86_64 -o amicable_numbers amicable_numbers.c
//
// Make executable:
// chmod u+x hello_world
//
// Codesign for MacOS
// codesign --verbose=4 --timestamp --strict --options runtime -s "<YOUR SIGNING CERTIFICATE NAME>" hello_world --force

#include <stdio.h>
#include <unistd.h>
#include <time.h>
#include <math.h>
#include <string.h>

void subfunc(int idx, int var) {
  printf("\n%d -> %d", idx, var);
  fflush(stdout);
}

int dividerSum(int num2Check){
  int nDivSum = 1;
  int rangeTop = (int)sqrt((double)num2Check);
  for (int i = 2; i <= rangeTop; i++)
  {
    int dividend = num2Check % i;
    if(dividend == 0){
      nDivSum += i + (num2Check / i);
    }
  }
  return nDivSum;
}

int main() {

  printf("#==================================================#\n");
  printf("| W3lc0m4 to AMICABLE NUMBER GENERATOR             |\n");
  printf("| This app lets you generate amicable number pairs |\n");
  printf("|                                                  |\n");
  printf("| v 0.0.1, (c.) 1991-2025 by kimhauser.ch          |\n");
  printf("#==================================================#\n");
  printf("\n");
  fflush(stdout);

  int searching = 1;
  while(searching)
  {
    int nStart = 0;
    int nEnd = 0;
    printf("\nStart of search range:");
    fflush(stdout);
    scanf("%d", &nStart);

    printf("\nEnd of search range:");
    fflush(stdout);
    scanf("%d", &nEnd);

    if(nStart >= 0 && nEnd > nStart){
      for (int i = nStart; i < nEnd; ++i)
      {
        if(i % 1000000 == 0){
          // Variable to hold the user input
          char input[256];

          printf("Do you want to continue your search? [Y/n]:");
          fflush(stdout);
          // Will wait for user input and store the input in the variable "input"
          scanf("%s", input);
          if(strcmp(input, "Y") != 0 && strcmp(input, "y") != 0){
            break;
          }
        }
        int nDivSum = dividerSum(i);
        if(dividerSum(nDivSum) == i && i < nDivSum){
            printf("\nFound amicable number pair: %d / %d ...", i, nDivSum);
            fflush(stdout);
        }
      }
      searching = 0;
    }else{
      printf("\nThe numbers for the search range are invalid! Try again ...");
      fflush(stdout);
    }
  }

  printf("\nApp exited normally!");
  fflush(stdout);

  return 0;
}