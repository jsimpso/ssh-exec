# ssh-exec
####Author: James Simpson
####Version: 1.0

This script will allow the user to execute multiple commands against multiple SSH enabled devices. 
In its current state, it's used for connecting to Cisco switches / routers - but with a bit of tweaking could be applied to any number of other devices. 

The output can either be displayed in your terminal screen, written to a file, or sent via email (with a bit of extra configuration)


Uses the following modules:
+ Paramiko to handle SSH
+ Getpass for secure password entry 
+ Time to allow for send delay
+ Readline to prevent input errors
+ Re for regex matches
+ Socket to handle socket exceptions
+ Smtplib to handle email
+ OS to remove temporary file created for email output
