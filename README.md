Deceptiport v. 1.3
=====

Deceptiport is a Python based cyber-deception tool meant to detect and act on reconnaissance and enumeration attempts

## About

  Deceptiport opens ports on a machine as fake services. If the attacker connects to the maximum allowed number of services, an iptables rule is generated to drop all traffic from the machine. The user is able to configure deceptiport to fake whatever service they would like; even multiple services at a time. Additionally, they can also set the maximum number of connections allowable before the attacker's traffic is filtered by the firewall.
  
  For attackers doing a full TCP connect scan of the machine, the IP address will automatically be filtered provided the maximum number of connections is not greater than the number of spoofed services running on the machine. It is important to note that connections to services running outside of the context of deceptiport are not counted against the attacker.
  
## Usage

  Deceptiport was designed with ease of use in mind. Configuring deceptiport is done via terminal with command line arguments.
  
    -p    List the ports you wish to spoof. i.e. "80,21,22"
    -m    Maximum number of connections before adding an iptables rule for the offending IP address
    
    example:  sudo ./deceptiport.py -p "80,21,22" -m 3

## Dependencies
  
  Deceptiport was developed and tested in Ubuntu 18.04. It should work in any linux distribution provided it has iptables installed.
  
  Python2 was used to develop deceptiport despite it being retired. Minor changes could be made to update it.
  
  All modules used are built into python2. Easy!

## Support scripts
 
  During testing, you may want to comment out the os.system function call enacting the iptables rule. If you don't, and inadvertently find yourself trying to get the IP address of the machine you've created a firewalll rule for back into the testing loop, you can use a script I created to quickly reverse the damage.

## Version 1.3 updates

  Added a method to catch a sigint to close out the application. Previous version deadlocked due to service object threads not getting the memo from the main thread.
