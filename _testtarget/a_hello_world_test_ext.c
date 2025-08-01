// NO DEBUG-INFO:
// clang -target x86_64-apple-macos -arch x86_64 -o a_hello_world_test_ext a_hello_world_test_ext.c
//
// WITH DEBUG-INFO:
// clang -g -target x86_64-apple-macos -arch x86_64 -o a_hello_world_test_ext a_hello_world_test_ext.c
//
// Make executable:
// chmod u+x a_hello_world_test_ext
//
// Codesign for MacOS
// codesign --verbose=4 --timestamp --strict --options runtime -s "<YOUR SIGNING CERTIFICATE NAME>" a_hello_world_test_ext --force

// Standard include
#include <stdio.h>
// For sleep()
#include <unistd.h>
#include <time.h>

//time_t start_real_time;// = time(NULL); // Get starting real time
void subfuncThree(int idx, int var);

void subfunc(int idx, int var) {
  printf("\n%d -> %d", idx, var);
  fflush(stdout);
}

void subfuncTwo(int idx, int var) {
  printf("\n==>> Idx: %d is Var: %d", idx, var);
  fflush(stdout);
}

int main() {

  // Variable for iteration counter
  int idx = 0;
  
  // INT test variable for the disasseblers "Variable" view
  int testVar = 123;

  // Another test variable (char array) for the disasseblers "Variable" view
  char hardcoded_string[] = "S3CR3T";
  
//start_real_time = time(NULL); // Get starting real time
  
  // This msg will prompt the user to enter his / her secret
  printf("Hello test: %d / %s", testVar, hardcoded_string);
  fflush(stdout);
  
  while(1)
    {
      if(idx % 3 == 0){
//      printf("\n%d", idx);
        subfunc(idx, testVar);
      }else if(idx % 5 == 0){
//      printf("\n%d", idx);
        subfuncTwo(idx, testVar);
      }
      printf("...");
      fflush(stdout);
      if(idx % 9 == 0){
        subfuncThree(idx, testVar);
      }else{
        sleep(1);
      }
      idx++;
    }
  return 0;
}

void subfuncThree(int idx, int var){
    printf("\n===>>> We are in subfuncThree! ==>> Idx: %d is Var: %d", idx, var);
}