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
import math
import random

from datetime import date
from datetime import datetime
from time import sleep
import time

def wait_in_rest(task_seconds):
     try:
         rest_seconds = 300
         rest_minutes = 5 
         input("Press Enter to start " + str(rest_minutes) + " minute rest.")
         print("Resting. Press Ctrl-c to continue tasks.")
         sleep(rest_seconds)
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
    return "Minutes per task block: " + minutes

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

def get_tasks_per_block(end_time, min_time_box, tasks):
    null_seconds = int(input("How many minutes are unavailable (meetings, etc)? ")) * 60
    total_task_seconds = int((end_time - datetime.now()).total_seconds()-null_seconds)
    task_seconds = int(total_task_seconds/len(tasks))
    # Determine how many tasks fit in a work block
    # Increase the time block by 25% to account for rest time
    tasks_per_block = len(tasks)
    if (task_seconds > 0):
        tasks_per_block = math.ceil((min_time_box*1.25*60)/task_seconds)
    print('Tasks per block:',tasks_per_block)
    print('Minutes per task block:',min_time_box)
    expected_blocks = math.ceil(total_task_seconds/(min_time_box*60))
    print('Expected task blocks:',expected_blocks)
    return tasks_per_block
    

    
sa = sys.argv
lsa = len(sys.argv)
if lsa != 6:
    print ("Usage: [ python ] task_boss.py file_name minimum_time_box(minutes) end_hour(24hr format) end_minute output_folder")
    print ("Example: [ python ] task_boss.py working_path file.txt 15 16 30 output_path")
    print ("The program assumes the task list has a header row and will ignore it")
    sa.append(input("Filename: "))
    sa.append(input("Min Time Box: "))
    sa.append(input("End Hour: "))
    sa.append(input("End Minute: "))
    sa.append(input("Output file location: "))

journal_path = str(sa[5]) + "-" + date.today().isoformat() + ".txt"
min_time_box = int(sa[2])

now_time = datetime.now()
end_time = now_time.replace(hour=int(sa[3]), minute=int(sa[4]))

print("It is now", now_time.strftime("%I:%M %p"))
print("Finish tasks at", end_time.strftime("%I:%M %p"))

# Read the tasks list
tasks = []
with open(sa[1]) as f:
    reader = csv.reader(f, delimiter='\t')
    tasks = list(reader)
    
    # Remove the header row
    del tasks[0]

# Shuffle the task list
random.shuffle(tasks)
    
journal = open(journal_path, 'w')

# Determine how many tasks to run today
print_and_log("Total tasks: "+str(len(tasks)), journal)
print()

# Automatically present the current task block
task_id = 0

while len(tasks) > 0:
        
    task_id = task_id+1
    task_block = []
    tasks_per_block = get_tasks_per_block(end_time, min_time_box, tasks)
    for i in range(tasks_per_block):
        try: 
            task_block.append(tasks.pop(0))
        except IndexError:
            print('ERROR: Index ERROR')
            break
    task_block.sort(reverse=True)
    for this_task in task_block:
        print_and_log ("This task: " + str(task_id) + ". " + this_task[0], journal)
    check_defer = wait_in_task(min_time_box * 60, journal)
    if check_defer == True:
        for this_task in task_block:
            tasks.append(this_task)
        
    # Beep when done
    beep()
    
    #if get_seconds_left_to_work(end_time) > 0:
    # Take 5 minute rest if there is still time left
    if (datetime.now() < end_time):
        wait_in_rest(min_time_box)
    else:
        print('End reached. Setting up overflow')
    
    # Advance to the next task only when confirmed
    if len(tasks) > 0:
        print("Preparing next task block")
        input("Press Enter to continue")
    else:
        print("Task list is now empty")
        break

print_and_log("All done. Exiting", journal)  
journal.close()
print("Journal closed")