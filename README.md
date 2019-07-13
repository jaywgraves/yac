yac
===

Young Authors Conference


This is a system that I wrote for a yearly event at my children's elementary school.
The conference organizer lined up ~20 authors (fiction, poetry, sports, reporters, travel, etc) to give a 45 minute presentation.  The eligible students (~320) got to rank their top five author choices in order of desirability and they would get to attend two sessions.  Each author gave the same presentation twice to different groups of students.

There several constraints that had to be met.  Each session could only hold 20 students and they wanted a good mix of 3rd and 4th graders in each session.  They also wanted to give preference to the 4th graders.

To make data entry easier, I got a class list from the school office and each class set aside time to go over the different author bios and then fill out a form with their name, grade level, teacher's name, and their top five choices.  I used a spreadsheet to enter the student choice sheets before exporting to a tab separated file.

The program splits the student list into grade levels and shuffles them separately before re-joining them together. 
It starts by making a pass through the student list and for each student tries to assign their first choice to an open session.  If the first session for their first choice is not open, then check if the second session is open.  If neither are open, go to the student's second choice, etc. A session is considered open if it is not full and if its mix of students is still within limits.

After the first pass through the students, the program starts over from the top, trying to fill in each student's missing session, (it could be either the first or second).  If all of their session choices are full then it gives up and leaves it unassigned.  This can happen on the first or second pass but it is more prevalent in the second when the popular sessions are mostly full.  At the end of the auto assignment routine, we are left with some students who are not complete and we need to start manual assignment.

To help with manual assignment, a score for each student is calculated when they are assigned to a session.
1 point for first choice, 2 for second, and so on up to 5 and 10 points if you are assigned to a session you did not pick.  (This can happen.)  The lower your score, the closer we got to the ideal assignments.  For example, if you got your first and second choice, then your score is 3 which is the best possible score.  (You can't be assigned to your first choice in both sessions.)  If you got your 2nd and 3rd choice your score is a 5.  The worst score you can get while still respecting your choices is a 9. (4th & 5th).  If you score is 10 or over then you got assigned to a session you did not pick.

I look for authors that have a low session count and find students that chose that author but didn't get assigned to them.  The system allows you to arbitrarily assign students to sessions and allows you to 'break the rules' regarding open sessions but it shows a warning.  I move students around while trying to keep their scores low.  For example, if a student picked an unpopular session as their 5th choice, I usually assigned them to it even if they weren't in it before, this usually frees up a slot in a popular talk.  I then made sure to give them their #1 or #2 choice to compensate.

Once everyone is assigned, there are multiple reports that can be printed out.
For the school office, I create a master list report that shows which room each student is in for both sessions.
For each teacher, I create a list of where each of her students are for each session.
Also includeed is a 4up printed sheet for each student that shows what sessions they were assigned to and which room to go to.
Every author has a volunteer host that gets a sheet listing which students will be with that author for each session so they can verify that they have the students they are supposed to.

I've used this program for 4 years with slight improvements/changes made each year.  It replaced a manual process that took a significant amount of time for multiple people and was considered to be unfair.  When you are looking at one student at a time you can't see the big picture of which authors are popular and which authors are less popular.  When assigning a student with a choice sheet that has all the sessions full, you had no choice but to stick in them in something they did not chose.  This happened often enough with the old system that both the teacher and kids were frustrated with what they were eventually assigned.


There is an oppourtunity to use optimization algorithms to find the 'best' configuration of student sessions.
I have explored using some of these so the manual step after auto assignment could be eliminated.  It is not a big problem in practice so I have held off implementing these for now.
