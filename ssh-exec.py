#!/usr/bin/env python

'''
Author: James Simpson
Version: 1.0

This script will allow the user to execute multiple commands against multiple SSH enabled devices. 
In its current state, it's used for connecting to Cisco switches / routers - but with a bit of tweaking could be applied to any number of other devices. 

The output can either be displayed in your terminal screen, written to a file, or sent via email (with a bit of extra configuration)


Uses the following modules:
	Paramiko to handle SSH
	Getpass for secure password entry 
	Time to allow for send delay
	Readline to prevent input errors
	Re for regex matches
	Socket to handle socket exceptions
	Smtplib to handle email
	OS to remove temporary file created for email output


'''
import paramiko
import getpass
import time
import readline
import re
import socket
import smtplib
import os

############################
#                          #
#        FUNCTIONS         #
#                          #
############################

#Function to open a user-specified file and extract a list of hosts
def get_devicenames():
	hosts = []

	#Loop to ensure that the script doesn't crash out if it can't find the specified file.
	while True:
		try:
			filename = raw_input("Which file contains your host list: ")
			openfile = open(filename, 'r')

		#The specific error we're most likely to see is "IOError: [Errno 2]"
		except IOError, reason:
			print "Error: %s" % reason
			continue

		#This tells the script to continue as normal if no IOError is raised, as the input has been accepted.
		else:
			break

	print "Reading hosts from \'%s\'" % filename
	for line in openfile:
        line = line.replace('\n','')
        line = line.replace('\r','')
        hosts.append(line)
	return hosts

#Create a list of commands from user input
def get_commands(prompt):
	
	commands = []
	while True:
		command = raw_input(prompt)
		if command == "":
			break
		else:
			commands.append(command)

	return commands	

#Called by "process_screen" function to assist with processing commands.
def print_command(command, console, device):
	length = len(command)
	print command
	print "*" * 10
	console.send("\n")
	console.send(command+"\n")
	time.sleep(4)
	output = console.recv(4096)
	
	try:
		start = output.index(command)
		output = output.replace(device + '#', ' ' * 13) 
		output = output.replace(command, ' ' * length)
		print output[start:]

	except ValueError, reason:
		streason = str(reason)
		if "substring not found" in streason:
			print "Couldn't see your command anywhere in the output - could be a slow or congested link?"
		else:
			print "There was some kind of error: %s" % reason	

#Called by "process_file" function to assist with processing commands.
def write_command(command, console, device, openfile):
	length = len(command)
	openfile.write(command + "\n")
	openfile.write("*" * 10 + "\n") 
	console.send("\n")
	console.send(command+"\n")
	time.sleep(4)
	output = console.recv(4096)
	
	try:
		start = output.index(command)
		output = output.replace(device + '#', ' ' * 13) 
		output = output.replace(command, ' ' * length)
		openfile.write(output[start:] + "\n")
	except ValueError, reason:
		streason = str(reason)
		if "substring not found" in streason:
			openfile.write("Couldn't see your command anywhere in the output - could be a slow or congested link?\n")
		else:
			openfile.write("There was some kind of error: %s\n" % reason)

#Used to process commands when output method is set to "screen"
def process_screen(devicenames, username, password, commands):
	for device in devicenames:

		print '-' * 10
		print device
		print '-' * 10

		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		#try / except loop - prevents script from aborting due to socket error. 
		try:
			client.connect(device, username=username, password=password, timeout=5, look_for_keys=False)
			#print "SSH connection established to %s" % device

		except (socket.error, paramiko.AuthenticationException), reason:
			print "Error: %s" % reason
			continue

		#Invoke remote shell
		console = client.invoke_shell()

		#Enter enable mode using provided credentials
		console.send("en \n")
		console.send(str(password)+"\n")

		#Set terminal length to 0
		console.send("terminal length 0\n")
		time.sleep(1)

		for command in commands:
			print_command(command, console, device)
		
		console.close()

#Used to process commands when output method is set to "file", or called by 'process_email'
def process_file(devicenames, username, password, commands):
	print "Working..."
	openfile = open(filename, 'a')

	for device in devicenames:

		openfile.write('-' * 10 + "\n")
		openfile.write(device + "\n")
		openfile.write('-' * 10 + "\n")

		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		#try / except loop - prevents script from aborting due to socket error. 
		try:
			client.connect(device, username=username, password=password, timeout=5, look_for_keys=False)
			#print "SSH connection established to %s" % device

		except (socket.error, paramiko.AuthenticationException), reason:
			openfile.write("Error: %s\n" % reason)
			continue

		#Invoke remote shell
		console = client.invoke_shell()

		#Enter enable mode using provided credentials
		console.send("en \n")
		console.send(str(password)+"\n")

		#Set terminal length to 0
		console.send("terminal length 0\n")
		time.sleep(1)

		for command in commands:
			write_command(command, console, device, openfile)
		
		console.close()

#Used to process commands when output method is set to "email"
def process_email(devicenames, username, password, commands):
	process_file(devicenames, username, password, commands)
	openfile = open("tempforemail", 'r')

	FROM = "sender@example.com"
	TO = ["recipient1@example.com"]
	SUBJECT = "Example Subject"
	TEXT = openfile.read()
	message = """\
From: %s
To: %s
Subject: %s

%s

""" % (FROM, ", ".join(TO), SUBJECT, TEXT)

	sendmail(FROM, TO, message)
	openfile.close()
	os.remove("tempforemail")

#Function used to obtain the user's output method of choice (screen, file, or email)
def get_output_method(prompt):
	while True:
		method = raw_input(prompt)
		if not re.match ("^screen$|^file$|^email$", method):
			print ("Please enter \"screen\", \"email\" or \"file\"")
			continue

		elif method == "file":
			filename = raw_input("Filename to write to: ")
			break

		elif method == "email":
			filename = "tempforemail"
			break

		else:
			filename = ""
			break

	return method, filename

#Function used for sending mail via an unauthenticated or open SMTP relay
def sendmail(FROM, TO, message):
	server = smtplib.SMTP('your.open.relay')
	server.sendmail(FROM, TO, message)
	server.quit(
)beechinbeechin
#Function used for sending mail via an SMTP relay requiring SSL
def sendmail_ssl(FROM, TO, message):
	server = smtplib.SMTP_SSL('ssl.smtp.server:465')
	server.login('username' 'password')
	server.sendmail(FROM, TO, message)
	server.quit()

############################
#                          #
#        VARIABLES         #
#                          #
############################
devicenames = get_devicenames()
username = raw_input("Username: ")
password = getpass.getpass("Password: ")
commands = get_commands("Enter Commands, press enter when finished: ")
method, filename = get_output_method("Output to screen, to file, or via email: ")

############################
#                          #
#        EXECUTION         #
#                          #
############################
# Open the "tempforemail" file ready for writing. Script will truncate the file if it exists, and will create it if it doesn't. 
f = open("tempforemail", 'w')
f.close()

if method == "screen":
	process_screen(devicenames, username, password, commands)
	print "Script has completed successfully!"

elif method == "file":
	process_file(devicenames, username, password, commands)
	print "Output written to %s" % filename

elif method == "email":
	process_email(devicenames, username, password, commands)
	print "Email sent!"

else:
	print "Some kind of error, output method set to incorrect value."
