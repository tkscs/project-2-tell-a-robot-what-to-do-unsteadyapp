I graded `go to click.py` because that's the code with the most recent edits. For the final, please put the code you want me to grade into a file called `main.py`.

Please see my detailed comments on github here:
https://github.com/tkscs/project-2-tell-a-robot-what-to-do-unsteadyapp/pull/1

Thanks!

Overall Rough Draft Score: 50 / 50
 
Basic Functionality (15 points):

* [ 6 / 10 ] Robot can move, and code runs without errors in simulator
    * 4 edits to get `go to click.py` to run
* [ 5 / 5 ] Robot does not crash into walls
    * `go to click.py` does not crash when edited

Control Flow - If/Elif/Else (15 points):

* [ 5 / 5 ] At least one if/elif/else chain with 3+ branches
    * `go to click.py` has this twice
* [ 5 / 5 ] At least one if/else that checks a sonar sensor reading
    * `go to click.py` has this
* [ 5 / 5 ] At least one if/else that checks user input
    * `go to click.py` has this

User Input (15 points):

* [ 2 / 3 ] At least 3 different input() prompts
    * `go to click.py` has 2
* [ 4 / 6 ] At least 6 different user responses are handled (2 per prompt above)
    * in `go to click.py`, the "left or right" question has skeleton code for responding to "left" and full code for responding to "right" which includes a question for an "x coord" for which all positive numbers are possible answers.
* [ 3 / 6 ] Robot behavior changes based on user input at least 6 times (each response above corresponds to a different behavior)
    * each x coordinate goes to a different place, and the right response leads to a different dialogue

Functions (10 points):

* [ 3 / 3 ] Define at least 3 functions
* [ 3 / 3 ] Call each of your functions at least once
* [ 2 / 3 ] For each function, include a doc string explaining the API
    * `forward` and `sign` have docstrings
* [ 1 / 1 ] At least 1 of your functions has at least 1 parameter

Sensors (10 points):

* [ 2 / 5 ] Read a sonar distance at least 5 times
    * `go to click.py` reads sonar twice
* [ 1 / 5 ] Robot behavior changes based on the sonar values
    * `go to click.py` has this once

Loops/Recursion (15 points):

* [ 10 / 10 ] Implements indefinite execution using at least one while loop OR at least one recursive function call
* [ 4 / 5 ] There is an option to terminate your indefinite execution
    * in `go to click.py` when you choose "left" the program quits, but that doesn't seem like a good long-term functionality. add an explicit "quit" option for the user to choose.

