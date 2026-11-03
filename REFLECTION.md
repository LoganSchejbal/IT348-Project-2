# Process Reflection (1-2 pages)

Written by the student. Every answer must cite the transcript file (e.g., transcripts/05_2026-10-20_reviewer_step1.md) or commit hash it refers to.

## 1. What did the reviewer or tester catch that the builder missed? (at least two cases)

In step one, the builder had created the loader, but did not account for the size of the data properly. The tester caught that the data files contained much more than the 1,500 rows that were expected and, as such, the way it was being handled needed to change. In order to accomodate the assignment requiring the dimensions of 1,500 x 1,846, the loading process changed so that a warning would be thrown and the files would be truncated to match what was expected. Additionally, the reviewer agent noticed that split_by_year did not verify that trainign and testing were disjoint. This means that there could have been overlapping training and testing files that may have altered the measurement data in unintended ways. The fix was to add a check to verify that there was not overlapping data.

## 2. One review comment you rejected, and why

In step 6, the reviewer noticed that there was not enough consideration for main.py when creating the step. Since there had been no work put into creating a driver program, I determined that it would not be the best time to begin considering this since the plan did not at this point even include plans for a driver program. I rejected this concluding it would be best to work on this at a later time.

## 3. A prompt that did not work, and how you rewrote it

The very first prompt was not very effective in having the builder agent factor in the need for a driver program into the project. Since I was focussed on evaluating the individual steps, much like the agent, I did not realize that the plan omitted plans for a main.py. To fix this, I decided to wait until the end of the project to create a driver program. To accomplish this, I had the builder agent create a post-step 7 plan to create the driver. To do this, I took a step 7 prompt for the basic structure and replaced the core with instructions to plan this part of the program. Then I had the reviewer review the plan with another modified prompt before I executed another buil/review/test cycle to execute the additions to the plan.

## 4. One other decision where you overrode an agent, and why

In the post-step 7 review, I rejected the reviewer's request alter source code because it was ultimately outside the scope of this inital step. I decided that since the builder was supposed to adjust only the plan, that it would be inappropriate to have it code as well at this point in time. The decision log stated that it was rejected, not because it was wrong, but because it was out of scope.

## 5. How you verified the agents' results (at least two results)

In Step 1, I verified the succesful loading of all data sets into the program. I checked that each set contained the correct amount of rows and colums. Additionally, I also checked for consistency between the static and retrained results. The results of step 7 were as expected based off what was obtained in step 6.

## 6. Parts you wrote or edited by hand

None
