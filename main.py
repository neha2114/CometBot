import discord
import os
from keep_alive import keep_alive

client = discord.Client()

class_dict = {}
attendees_dict = {}
event_dict = {}

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
  
@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content

  # $add function
  if msg.startswith("$add "):
    class_info = msg.split(" ")
    # Checks for incorrect syntax
    if len(class_info) != 4:
      await message.channel.send("Incorrect number of inputs. Enter in order class name(without spaces), days, time.")
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
  if msg.startswith("$addEvent "):
    event_info = msg.split(" ")
    if len(event_info) != 5:
      await message.channel.send("Incorrect number of inputs. Enter class name(without spaces), event name(without spaces), date, time.")
      return
    #Add a new event to list
    event_dict[event_info[1]] = (event_info[2], event_info[3], event_info[4])
    await message.channel.send("New event added.")
    return
    
  # $del function
  if msg.startswith("$del "):
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

  # $list function
  if msg.startswith("$list"):
    input = msg.split(" ")
    # Checks for incorrect syntax
    if len(input) > 2:
      await message.channel.send("Incorrect number of inputs. Enter no input or class/event name only - without spaces.")
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
    else:
      # Display list of events
      if input[1] == "events":
        # No events
        if len(event_dict) == 0:
          await message.channel.send("No events in list.")
          return
        # Display list of all events.
        events = ""
        for key, value in event_dict.items():
          events += key + ": " + value[0] + " @" + value[1] + " " + value[2]
          events += "\n"
        await message.channel.send(events)
        return
      # Display list of attendees in specific class
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

  # $join function
  if msg.startswith("$join "):
    class_info = msg.split(" ")
    # Checks for incorrect syntax
    if len(class_info) != 3:
      await message.channel.send("Incorrect number of inputs. Enter class name(without spaces), then full name(without spaces).")
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
  if msg.startswith("$leave "):
    input = msg.split(" ")
    # Checks for incorrect syntax
    if len(input) != 3:
      await message.channel.send("Incorrect number of inputs. Enter class name(without spaces), then full name(without spaces).")
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
  if msg.startswith("$streak "):
    input = msg.split(" ")
    # Checks for incorrect syntax
    if len(input) != 3:
      await message.channel.send("Incorrect number of inputs. Enter class name(without spaces), then full name(without spaces).")
      return
    class_name = input[1]
    student_name = input[2]
    # Class is found
    if class_name in attendees_dict:
      # Looks for student in existing class
      for student in attendees_dict[class_name]:
        if student[0] == student_name:
          streakInt = int(student[1])
          streakInt += 1
          attendees_dict[class_name].append((student_name, streakInt))
          attendees_dict[class_name].remove(student)
          await message.channel.send(student_name + "'s streak has been updated to " + str(streakInt))
          return
      await message.channel.send(student_name + " could not be found in the class attendees list.\n Use $join to join the list and start your streak.")
    # Class not found
    else:
      await message.channel.send("Class " + class_name + " cannot be found.")

  # $top function (shows the student with the highest streak)
  if msg.startswith("$top "):
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
    add_instr = "**To add a class, enter:**\n" + "$add [class name] [weekdays] [time]\n"
    add_event_instr = "**To add an event, enter:**\n" + "$addEvent [class name] [event name] [date] [time]\n"
    del_instr = "**To delete a class, enter:**\n" + "$del [class name]\n"
    list_instr = "**To see a list of all classes, enter:**\n" + "$list\n"
    list_instr2 = "**To see a list of attendees in one class, enter:**\n" + "$list [class name]\n"
    list_instr3 = "**To see a list of all events, enter:**\n" + "$list events\n"
    join_instr = "**To be on a class's attendee list, enter:**\n" + "$join [class name] [your name]\n"
    leave_instr = "**To leave a class's attendee list, enter:**\n" + "$leave [class name] [your name]\n"
    streak_instr = "**To update your streak for attending a class, enter:**\n" + "$streak [class name] [your name]\n"
    top_instr = "**To see the student(s) with the highest attendance score, enter:**\n" + "$top [class name]\n"
    await message.channel.send(add_instr + add_event_instr + del_instr + list_instr + list_instr2 + list_instr3 + join_instr + leave_instr + streak_instr + top_instr)

keep_alive()
client.run(os.getenv("TOKEN"))
