#Internet Downtime Emailer

import time, smtplib, configparser, sys, socket, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def getUsername():
    config = configparser.ConfigParser()
    config.read(sys.path[0] + '/config.cfg')
    return config.get('GMAIL', 'username')

def getPassword():
    config = configparser.ConfigParser()
    config.read(sys.path[0] + '/config.cfg')
    return config.get('GMAIL', 'password')

def getMachineName():
    config = configparser.ConfigParser()
    config.read(sys.path[0] + '/config.cfg')
    return config.get('OTHER', 'machine_name')

def getInterval():
    config = configparser.ConfigParser()
    config.read(sys.path[0] + '/config.cfg')
    return int(config.get('OTHER', 'interval'))

def getSendAddress():
    config = configparser.ConfigParser()
    config.read(sys.path[0] + '/config.cfg')
    return config.get('OTHER', 'send_email')

def isConnected():
    """Tries to create a connection to google.com, if this fails return False"""
    try:
        socket.create_connection(("www.google.com", 80))
        print("Online!")
        return True
    except:
        print("Offline :(")
        return False

def generateEmail(timeOffline, starTimeStr, endTimeStr, machine_name):
    contents = machine_name + " offline for " + str(int(timeOffline)) + " seconds"
    subject = machine_name + " was offline from " + startTimeStr + " until " + endTimeStr + " for a total of " + str(int(timeOffline)) + " seconds."
    return contents, subject

def sendEmail(subject, contents, username, send_address):
    from_email = username + "@gmail.com"
    print("From:", from_email)
    print("To:", send_address)
    print("Subject:", subject)
    print("Contents:", contents, end = "\n")

    message = MIMEMultipart()
    message['From'] = username + "@gmail.com"
    message['To'] = send_address
    message['Subject'] = subject
    message.attach(MIMEText(contents, 'plain'))

    try:
        server = smtplib.SMTP_SSL('smtp.googlemail.com', 465)
        server.ehlo()
        server.login(from_email, password)
        #print(from_email, send_address, message.as_string())
        server.sendmail(from_email, send_address, message.as_string())
        server.close()
        print("Email sent!")
        
    except Exception as e:
        print(e)
        print("Email failed to send")
    
if __name__ == "__main__":
    emailToSend = False
    if os.path.isfile(sys.path[0] + '/config.cfg'):
        username = getUsername()
        password = getPassword()
        machine_name = getMachineName()
        interval = getInterval()
        send_address = getSendAddress()

        print("Username: ", username, "\n",
              "Machine Name: ", machine_name, "\n",
              "Interval (secs): ", interval, "\n",
              "Recieving Address: ", send_address, sep = "")

        if len(username) == 0 or len(password) == 0:
            print("Error: Incorrectly set up config file.")

    else:
        print("Error: 'config.cfg' is missing.")

    tick_start = int(time.time())
    next_tick = tick_start + interval
        
    while True:
        if int(time.time()) > next_tick:
            print("Current time has gone past next_tick without hitting it" +
                  ", reccomend increasing interval.")
            #we've taken longer than interval to get back here
            
        if int(time.time()) >= next_tick:
            tick_start = next_tick
            next_tick = tick_start + interval
            connected = isConnected()
            if not connected:
                if not emailToSend:
                    emailToSend = True
                    startTimeFloat = time.time()
                    startTimeStr = time.strftime("%d/%m/%Y, %H:%M:%S")
            else:
                if emailToSend:
                    endTimeFloat = time.time()
                    endTimeStr = time.strftime("%d/%m/%Y, %H:%M:%S")
                    timeOffline = endTimeFloat - startTimeFloat
                    subject, contents = generateEmail(timeOffline, startTimeStr, endTimeStr, machine_name)
                    sendEmail(subject, contents, username, send_address)
                    emailToSend = False
                    #emails take time to send, and its likely to be over the next tick that its done by
                    tick_start = int(time.time())
                    next_tick = tick_start + interval
                else: #internet up, no email to send
                    pass
                
