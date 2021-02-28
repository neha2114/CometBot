import discord
import os
import requests
import json
from keep_alive import keep_alive

client = discord.Client()
class_dict = {}
attendees_dict = {}
event_dict = {}

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

    #i'm kind of just messing with discord bot documentation
    #but I would like it to have it so: when you react to the event,
    # something happens? kind of like signing up, or it shows 
    #all attendees
    
  # maybe we can create another dict where class names are the keys and the lists of attendees are the values
  # like: "class name" : [attendee 1, attendee 2, etc]
#^ yesss
  # or instead of an attendee list, classes can have events - study sessions/tutoring or something
  
  
@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content

  # $add function
  if msg.startswith("$addClass"):
    class_info = msg.split(" ")
    # Checks for incorrect syntax
    if len(class_info) != 4:
      await message.channel.send("Incorrect number of inputs. Enter in order class name - without spaces, days, time.")
      return
    # Class already in list
    if class_info[1] in class_dict:
      await message.channel.send("This class has already been added.")
      return
    # Add new class to list
    else:
      class_dict[class_info[1]] = (class_info[2], class_info[3])
      attendees_dict[class_info[1]] = []
      await message.channel.send("New class added.")
      return
  
  # $addEvent function
  if msg.startswith("$addEvent"):
    event_info = msg.split(" ")
    if len(event_info) != 4:
      await message.channel.send("Incorrect number of inputs. Enter class name - without spaces, event name, time.")
      return
    #Add a new event to list
    event_dict[event_info[1]] = (event_info[2])
    await message.channel.send("New event added.")
    return
    
  # $del function
  if msg.startswith("$delClass"):
    class_info = msg.split(" ")
    # Checks for incorrect syntax
    if len(class_info) != 2:
      await message.channel.send("Incorrect number of inputs. Enter class name only - without spaces.")
      return
    class_name = class_info[1]
    # Successfully deletes class
    if class_name in class_dict:
      del class_dict[class_name]
      attendees_dict.pop(class_name)
      await message.channel.send(class_name + " deleted from the list.")
    # Could not find class to be deleted
    else:
      await message.channel.send("Class not found in the list.")
  
  # $delEvent function
  if msg.startswith("$delEvent"):
    event_info = msg.split(" ")
    if len(event_info) != 3:
      await message.channel.send("Incorrect number of inputs. Enter class name - without spaces, then event name.")
      return
    event_name = event_info[1]
    #Deletes the event
    if event_name in event_dict:
      del event_dict[event_name]
      # attendees_dict.pop(class_name)
      await message.channel.send(event_name + " deleted from the list.")
    # Could not find class to be deleted
    else:
      await message.channel.send("Event not found in the list.")

  # $listClasses function
  if msg.startswith("$listClasses"):
    input = msg.split(" ")
    # Checks for incorrect syntax
    if len(input) > 2:
      await message.channel.send("Incorrect number of inputs. Enter no input or class name only - without spaces.")
      return
    # Display list of all classes.
    if len(input) == 1:
      # Empty list
      if len(class_dict) == 0:
        await message.channel.send("No classes in list.")
        return
      # Non-empty list
      classes = ""
      for key, value in class_dict.items():
        classes += key + ": " + value[0] + " @" + value[1]
        classes += "\n"
      await message.channel.send(classes)
    # Display list of attendees in specific class
    elif len(input) == 2:
      # Class found.
      class_name = input[1]
      if class_name in attendees_dict:
        student_list_string = ""
        for student in attendees_dict[class_name]:
          if len(student_list_string) > 0:
            student_list_string += ", "
          student_list_string += student[0]
        await message.channel.send("Student(s) in " + class_name + ": " + student_list_string)
      # Class not found.
      else:
        await message.channel.send(class_name + " is not found.")
        
  # $listEvents function
  if msg.startswith("$listEvents"):
    input = msg.split(" ")
    # Checks for incorrect syntax
    if len(input) > 2:
      await message.channel.send("Incorrect number of inputs. Enter no input or class name only - without spaces.")
      return
    # Display list of all classes.
    if len(input) == 1:
      # Empty list
      if len(event_dict) == 0:
        await message.channel.send("No events in list.")
        return
      # Non-empty list
      events = ""
      # PROBLEM: not printing info correctly
      for key, value in event_dict.items():
        events += key + ": " + value[0] + " @" + value[1]
        events += "\n"
      await message.channel.send(events)
  

  # $join function
  if msg.startswith("$join"):
    class_info = msg.split(" ")
    # Checks for incorrect syntax
    if len(class_info) != 3:
      await message.channel.send("Incorrect number of inputs. Enter class name, then full name - without spaces.")
      return
    class_name = class_info[1]
    student_name = class_info[2] 
    # Empty list
    if len(class_dict) == 0:
      await message.channel.send("No classes in list to join.")
      return
    # Adds user to class attendee list
    if class_name in class_dict:
      attendees_dict[class_name].append((student_name, "0"))
      await message.channel.send("User " + student_name + " added to attendees list.")
    # Could not find class to join.
    else:
      await message.channel.send("The class you want to join is not found in the list.")

  # $leave function
  if msg.startswith("$leave"):
    input = msg.split(" ")
    # Checks for incorrect syntax
    if len(input) != 3:
      await message.channel.send("Incorrect number of inputs. Enter class name, then full name - without spaces.")
      return
    class_name = input[1]
    student_name = input[2]  
    # Empty list
    if len(class_dict) == 0:
      await message.channel.send("No classes in list to leave.")
      return
    # Removes user from class attendee list
    if class_name in class_dict:
      # Looks for student in existing class
      for student in attendees_dict[class_name]:
        if str(student[0]) == student_name: 
          attendees_dict[class_name].remove(student)
          await message.channel.send(student_name + " has been removed from " + class_name)
          return
      await message.channel.send(student_name + " could not be found in the class attendees list.")
    # Could not find class to leave.
    else:
      await message.channel.send("The class you want to leave is not found in the list.")
  
  # $streak function (increases a student's streak)
  if msg.startswith("$streak"):
    input = msg.split(" ")
    # Checks for incorrect syntax
    if len(input) != 3:
      await message.channel.send("Incorrect number of inputs. Enter class name, then full name - without spaces.")
      return
    class_name = input[1]
    student_name = input[2]
    # Class is found
    if class_name in attendees_dict:
      # Looks for student in existing class
      for student in attendees_dict[class_name]:
        if student[0] == student_name:# the error is in this line; "int object is not subscriptable" - resolved
          streakInt = int(student[1])# error: invalid literal for int() with base 10 - resolved
          streakInt = streakInt+1
          student = (student[0], str(streakInt))
          await message.channel.send(student_name + "'s streak has been updated to " + student[1])
          return
      await message.channel.send(student_name + " could not be found in the class attendees list.\n Use $join to join the list and start your streak.")
    # Class not found
    else:
      await message.channel.send("Class " + class_name + " cannot be found.")

  # $top function (shows the student with the highest streak)
  if msg.startswith("$top"):
    input = msg.split(" ")
    # Checks for incorrect syntax
    if len(input) != 2:
      await message.channel.send("Incorrect number of inputs. Enter class name only - without spaces.")
      return
    class_name = input[1]
    #search entire list
    streak_top = 0
    student_top_msg = ""
    # Finds highest streak
    for student in attendees_dict[class_name]:
      if int(student[1]) > streak_top:
        streak_top = int(student[1])
    # Finds all students with the top streak
    for student in attendees_dict[class_name]:
      if int(student[1]) == streak_top:
        if len(student_top_msg) > 0:
          student_top_msg += ", "
        student_top_msg += student[0]
    await message.channel.send("Student(s): " + student_top_msg + " have the highest attendance score of " + str(streak_top) + "!")

# $help function
  if msg.startswith("$help"):
    await message.channel.send("Welcome to the Class Helper Bot! Instructions: \n")
    add_instr = "**To add a class, enter:**\n" + "$addClass [class name] [weekdays] [time]\n"
    add_instr_two = "**To add an event, enter:**\n" + "$addEvent [class name] [event name] [time]\n"
    del_instr = "**To delete a class, enter:**\n" + "$delClass [class name]\n"
    del_instr_two = "**To delete an event, enter:**\n" + "$delEvent [event name]\n"
    list_instr = "**To see a list of all classes, enter:**\n" + "$listClasses\n"
    list_instr2 = "**To see a list of attendees in one class, enter:**\n" + "$list [class name]\n"
    list_instr3 = "**To see a list of events in a class, enter:**\n" + "$listEvents [class name]\n"
    join_instr = "**To be on a class's attendee list, enter:**\n" + "$join [class name] [your name]\n"
    leave_instr = "**To leave a class's attendee list, enter:**\n" + "$leave [class name] [your name]\n"
    streak_instr = "**To update your streak for attending a class, enter:**\n" + "$streak [class name] [your name]\n"
    top_instr = "**To see the student(s) with the highest attendance score, enter:**\n" + "$top [class name]\n"
    event_instr = "**To add an event for your class, enter:**\n" + "$addEvent [class name]\n"
    await message.channel.send(add_instr + add_instr_two + del_instr + del_instr_two + list_instr + list_instr2 + join_instr + leave_instr + streak_instr + top_instr + event_instr)

keep_alive()
client.run(os.getenv("TOKEN"))
