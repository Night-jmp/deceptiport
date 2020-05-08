#!/usr/bin/python

import socket
import threading
import os
import sys
import getopt
import signal

activeConnections = {}

class Attacker:

    def __init__(self, ip):
        self.ip = ip
        self.connections = 0

    def addConnection(self):
        self.connections += 1

    def getConnections(self):
        return self.connections

    def getIP(self):
        return self.ip


############################## createService class ##############################
#
#   Given a port number, this class creates service objects that emulates a
#   real service. If an attacker enumerates enough of these fake services,
#   their IP address is blocked via IPTables rules.
#
#################################################################################
class createService:

    ######################### Constructor #########################
    #
    #   This function sets up the service object and lets the
    #   user know the service has been set up.
    #
    ###############################################################
    def __init__(self, port, MAXCONN):
        try:
            self.MAXCONN = int(MAXCONN)                                     # Set maximum allowable connections before blocking IP
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.port = int(port)
            self.portConnections = []

            print "Opening port: " + str(self.port)
            self.sock.bind(('0.0.0.0', self.port))
            
            while True:                                                # Continuously listen for additional connections
                self.listen(self.sock)

        except IOError as e:
            if e.errno == 13:
                print "You need elevated privileges to open port " + str(port)
                print "Try using sudo if you're a sudoer!"
            else:
                print e
    
    ######################### listen function #########################
    #
    #   Listen function does nothing more than socket.listen and passes
    #   the connection to the handler function
    #
    ###################################################################
    def listen(self, sock):
        self.sock.listen(1)
        self.conn, addr = self.sock.accept()
        self.addr = addr
        
        self.handleConnection(self.conn, addr)

    ######################### connection handler #########################
    #
    #   This function increments the connection counter when a connection is
    #   made. It then decides if the attacker has violated the max connections.
    #   If it has, the address if passed to the IP blocking function.
    #
    ######################################################################
    def handleConnection(self, conn, addr):
        global activeConnections

        if addr[0] not in activeConnections:
            activeConnections[addr[0]] = Attacker(addr[0])

        if addr[0] not in self.portConnections:
            self.portConnections.append(addr[0])
            activeConnections[addr[0]].addConnection()

        print "Connection established with: " + addr[0]
        print "Connections: " + str(activeConnections[addr[0]].getConnections())
        
        if activeConnections[addr[0]].getConnections() >= self.MAXCONN:
            print "TOO MANY CONNECTIONS!"
            self.blockIP(addr)
        
        self.closeConnection()

    ######################### IP Block #########################
    #
    #   This function is responsible for forming the IPtables
    #   rule to block the attacking IP address.
    #
    ############################################################
    def blockIP(self, addr):
        cmd = "iptables -A INPUT -p tcp -s " + addr[0] + " -j DROP"     # Forms the IP tables rule based on the attacker's IP
        print cmd

        ##### Commented out for testing! Please uncomment when in production #####
        os.system(cmd)

    ######################### Connection close ####################
    #
    #   Simple close connection function
    #   
    ###############################################################
    def closeConnection(self):
        print "Closing connection"
        self.conn.close()


def usage():

    print "Deceptiport 1.3"
    print "Usage: "
    print "\t./deceptiport.py -p <ports> -m <max connections>"
    print "\nDeceptiport opens ports on all user specified port numbers.\nIf an attacker connects to greater than or equal to the maximum specified connections, their IP address is blocked."
    print "NOTE: If using port numbers under 1024, you must be a sudoer!"
    print "\nExample: ./deceptiport -p '21,22,80' -m 3"

def exit(signal, frame):
    print "\nExiting!"
    sys.exit(0)

if __name__ == "__main__":

    ######################### Driver #########################
    #
    #   This section sets up the argument options for the
    #   script. If the user needs help, usage information
    #   is provided.
    #
    ##########################################################

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:m:")
    except getopt.GetoptError:
        print "./deceptiport.py -p <ports> -m <max connections>"
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit(2)
        elif opt in '-p':
            ports = arg.split(",")
        elif opt in '-m':
            MAXCONN = arg
    if len(opts) == 0:
        usage()
        sys.exit(2)

    for port in ports:
        t = threading.Thread(target=createService, args=(port,MAXCONN))
        t.daemon = True
        t.start()

    while True:
        signal.signal(signal.SIGINT, exit)
