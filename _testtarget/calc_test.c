// NO DEBUG-INFO:
// clang -target x86_64-apple-macos -arch x86_64 -o hello_world_test hello_world_test.c
//
// WITH DEBUG-INFO:
// clang -g -target x86_64-apple-macos -arch x86_64 -o hello_world_test hello_world_test.c
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

//time_t start_real_time;// = time(NULL); // Get starting real time

void subfunc(int idx, int var) {
  printf("\n%d -> %d", idx, var);
  fflush(stdout);
}

int main() {

  // Variable for iteration counter
  int idx = 0;
  
  // INT test variable for the disasseblers "Variable" view
  int testVar = 1;

  // Another test variable (char array) for the disasseblers "Variable" view
  char hardcoded_string[] = "S3CR3T";
  
//start_real_time = time(NULL); // Get starting real time
  
  // This msg will prompt the user to enter his / her secret
  printf("Welc0me to calc test!\nPlease solve the following calculations:");
  // fflush(stdout);
  
  while(1)
    {
      /*if(idx % 3 == 0){
//      printf("\n%d", idx);
        subfunc(idx, testVar);
      }*/
      printf("What is the sum of: %d and %d?\n", testVar, (testVar + 1));
      fflush(stdout);
      // Variable to hold the user input
      //char input[256];
      int number = 0;
      
      // This msg will prompt the user to enter his / her secret
      //printf("Please enter your secret: ");
      
      // Will wait for user input and store the input in the variable "input"
      scanf("%d", &number);
      if(number == (testVar + (testVar + 1))){
        printf("Your result is correct! Proceeding to next calculation ....\n");
        testVar *= 2;
      }else{
        printf("Your result is NOT correct! Try again ....\n");
      }
      fflush(stdout);
      sleep(1);
      idx++;
    }
  return 0;
}