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

// Standard include
#include <stdio.h>
// For sleep()
#include <unistd.h>
#include <time.h>
#include <math.h>
#include <string.h>

//time_t start_real_time;// = time(NULL); // Get starting real time

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
      //printf("\nFound divisor: %d + %d (%d)", i, (num2Check / i), (i + (num2Check / i)));
      nDivSum += i + (num2Check / i);
    }
  }
  return nDivSum;
}

int main() {

  // // Variable for iteration counter
  // int idx = 0;
  
  // // INT test variable for the disasseblers "Variable" view
  // int testVar = 1;

  // // Another test variable (char array) for the disasseblers "Variable" view
  // char hardcoded_string[] = "S3CR3T";
  
//start_real_time = time(NULL); // Get starting real time
  
  // This msg will prompt the user to enter his / her secret
  //printf("Welc0me to calc test!\nPlease solve the following calculations:");
  printf("#==================================================#\n");
  printf("| W3lc0m4 to AMICABLE NUMBER GENERATOR             |\n");
  printf("| This app lets you generate amicable number pairs |\n");
  printf("|                                                  |\n");
  printf("| v 0.0.1, (c.) 1991-2025 by kimhauser.ch          |\n");
  printf("#==================================================#\n");
  printf("\n");
  fflush(stdout);

  // int nVar3 = dividerSum(283);
  // int nVar1 = dividerSum(220);
  // int nVar2 = dividerSum(nVar1);
  // int nVar4 = dividerSum(283);
  // printf("\nFound amicable number pair: %d / %d / %d / %d ...", nVar1, nVar2, nVar3, nVar4);
  // return 0;

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
          
          // This msg will prompt the user to enter his / her secret
          printf("Do you want to continue your search? [Y/n]:");
          fflush(stdout);
          // Will wait for user input and store the input in the variable "input"
          scanf("%s", input);
          if(strcmp(input, "Y") != 0 && strcmp(input, "y") != 0){
            break;
          }
        }
        //printf("\nChecking %d...", i);
        int nDivSum = dividerSum(i);
        if(dividerSum(nDivSum) == i && i < nDivSum){
            printf("\nFound amicable number pair: %d / %d ...", i, nDivSum);
            fflush(stdout);
        }
      }
      searching = 0;
    }else{
      printf("\nThe numbers for the search range are invalid!");
      fflush(stdout);
    }
  }
  printf("\nApp exited normally!");
  fflush(stdout);
  
//   while(1)
//     {
//       /*if(idx % 3 == 0){
// //      printf("\n%d", idx);
//         subfunc(idx, testVar);
//       }*/
//       printf("What is the sum of: %d and %d?\n", testVar, (testVar + 1));
//       fflush(stdout);
//       // Variable to hold the user input
//       //char input[256];
//       int number = 0;
      
//       // This msg will prompt the user to enter his / her secret
//       //printf("Please enter your secret: ");
      
//       // Will wait for user input and store the input in the variable "input"
//       scanf("%d", &number);
//       if(number == (testVar + (testVar + 1))){
//         printf("Your result is correct! Proceeding to next calculation ....\n");
//         testVar *= 2;
//       }else{
//         printf("Your result is NOT correct! Try again ....\n");
//       }
//       fflush(stdout);
//       sleep(1);
//       idx++;
//     }
  return 0;
}