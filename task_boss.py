# Task Boss

"""
Task Boss time boxing script
Task Boss takes a text file of tasks and a finish time and automatically breask
the list into time boxes.
It will prompt when to finish the current task and advance to the next one.
You can hit Ctrl-C to interrupt the wait and will get options to finish the 
 task early or continue when ready.
 
TODO: Add 'actual time spent' to post-task step
"""

import csv
import sys
import os
import math
 
from datetime import date
from datetime import datetime
from time import sleep
import time

def wait_in_rest():
     try:
         input("Press Enter to start 5 minute rest.")
         print("Resting. Press Ctrl-c to continue tasks.")
         sleep(60*5)
     except KeyboardInterrupt:
         print("Rest Stopped. Continuing flow.")
     beep()


def beep():
    # Beep twice
    for j in range(2):
        print (chr(7))
        sleep(1)


def wait_in_task(task_seconds, journal):
    defer_task = False    
    time_remaining = task_seconds
    continue_waiting = True
    while (continue_waiting and time_remaining > 0):
        try:
            start_sleep = time.time()
            print("Waiting for:", int(time_remaining), "s (", int(time_remaining/60), "m )")
            print()           
            print("Press Ctrl-c to pause and view options")
            sleep(time_remaining)
            continue_waiting = False
        except KeyboardInterrupt:
            time_remaining = time_remaining - (time.time() - start_sleep)            
            print_and_log("Task Paused", journal)
            action = input("Continue this task, go to Next task, Defer task to end, or Exit? (c/n/d/e) ")
            if action == 'e':
                journal.close()
                sys.exit(1)
            elif action == 'n':
                continue_waiting = False
            elif action == 'd':
                continue_waiting = False
                defer_task = True
            else:
                print_and_log("Continuing task", journal)
                
    return defer_task

def print_and_log( output, journal ):
    print(output)
    journal.write(output + '\n')
    return

def print_seconds_to_minutes( seconds ):
    if (seconds < 60): minutes = "< 1"
    else: minutes = str(int(seconds/60))
    return "Minutes per task: " + minutes

def print_task_time_with_overdrive(task_seconds, min_time_box):
    adjusted_task_seconds = task_seconds
    if adjusted_task_seconds < min_time_box * 60:
        adjusted_task_seconds = min_time_box * 60
    percentage = int(adjusted_task_seconds/task_seconds*100)
    if percentage == 100:
        print("Task time:",adjusted_task_seconds)
    else:
        print("Task time: " + str(adjusted_task_seconds) + " (" + str(percentage) + "% overdrive)")
    return adjusted_task_seconds

def get_seconds_left_to_work(end_time):
    return (end_time - datetime.now()).total_seconds()
    
    
sa = sys.argv
lsa = len(sys.argv)
if lsa != 5:
    print ("Usage: [ python ] task_boss.py working_path file_name minimum_time_box(minutes) end_hour(24hr format) end_minute")
    print ("Example: [ python ] task_boss.py working_path file.txt 15 16 30")
    print ("The program assumes the task list has a header row and will ignore it")
    sa.append(input("Filename: "))
    sa.append(input("Min Time Box: "))
    sa.append(input("End Hour: "))
    sa.append(input("End Minute: "))

os.chdir(os.path.dirname(sa[1]))
journal_path = date.today().isoformat() + "_task_journal.txt"
min_time_box = int(sa[2])

now_time = datetime.now()
end_time = now_time.replace(hour=int(sa[3]), minute=int(sa[4]))

print("It is now", now_time.strftime("%I:%M %p"))
print("Finish tasks at", end_time.strftime("%I:%M %p"))

with open(sa[1]) as f:
    reader = csv.reader(f, delimiter='\t')
    tasks = list(reader)
    
    # Remove the header row
    del tasks[0]
    
journal = open(journal_path, 'w')

# Determine how many tasks to run today
print_and_log("Total tasks: "+str(len(tasks)), journal)

# Determine the minutes per task
task_seconds = int(get_seconds_left_to_work(end_time)/len(tasks))
adjusted_task_seconds = print_task_time_with_overdrive(task_seconds, min_time_box)
print_and_log(print_seconds_to_minutes(adjusted_task_seconds),journal)
print()

# Automatically present the current task
task_id = 0

while len(tasks) > 0 and get_seconds_left_to_work(end_time) > 0:
    task_block_count = math.ceil(adjusted_task_seconds/task_seconds)
    task_id = task_id+1
    task_block = []
    for i in range(task_block_count):
        try: 
            task_block.append(tasks.pop(0))
        except IndexError:
            break
    task_block.sort(reverse=True)
    for this_task in task_block:
        print_and_log ("This task: " + str(task_id) + ". " + this_task[0], journal)
    check_defer = wait_in_task(adjusted_task_seconds, journal)
    if check_defer == True:
        for this_task in task_block:
            tasks.append(this_task)
        
    # Beep when done
    beep()

    # Exit if end of the list is reached (avoids div-by-zero error)
    if len(tasks) == 0:
        main_loop = False
        break
    
    # Take 5 minute rest
    wait_in_rest()
    
    # Advance to the next task only when confirmed
    if len(tasks) > 0: print("Next task:",str(task_id+1)+".", tasks[0][0])
    input("Press Enter to continue")

            
    # Recalculate the new per-task time            
    task_seconds = int(get_seconds_left_to_work(end_time) / len(tasks))
    adjusted_task_seconds = print_task_time_with_overdrive(task_seconds, min_time_box)
    print_and_log(print_seconds_to_minutes(adjusted_task_seconds),journal)                        

print_and_log("All done. Exiting", journal)  
journal.close()
