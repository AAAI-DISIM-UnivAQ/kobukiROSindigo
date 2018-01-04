#!/usr/bin/env python

import rospy
import math
import time
from pyswip import Prolog
from geometry_msgs.msg import Twist
from kobukiROSindigo.msg import Status

pubKobukiVelocity = rospy.Publisher('kobuki_velocity', Twist, queue_size=1)
kobukiStatus = Status()  # The updated status of the robot
prologEngine = Prolog()
kobukiDecisionVelocity = Twist()

def learn(prologFilePath):  # Function not used because Pyswip is not compatible
    '''
    Learns from a SWI Prolog file.
    :param prologFilePath: The path of the Prolog (.pl or .txt) file we need to use.
    :return:
    '''
    print 'Learning started...'
    assert isinstance(prologFilePath, str)
    prologEngine.consult(prologFilePath)
    print 'Learning finished'


# The following function gives the "Segmentation fault (core dumped)" error because of Pyswip
def decisionCallback(kobukiStatus):
    print 'Decision taking started...'
    west = kobukiStatus.bumperW
    north = kobukiStatus.bumperN
    east = kobukiStatus.bumperE
    perceptionBumper = [['bumperW', west], ['bumperN', north], ['bumperE', east]]
    print(perceptionBumper)
    prologEngine.assertz('perceptionBumper(' + str(perceptionBumper).replace('"', "'") + ')')
    print 'New knowledge taken...'
    rospy.loginfo('west: {}, north: {}, est: {}'.format(west, north, east))
    try:
        out = list(prologEngine.query('takeDecision(D)'))
    except:  # If Prolog doesn't work (maybe because it can't receive data from sensors) the robot has to stay
        out = []
    # print(out)  # test
    if len(out) > 0 :  # If we can take more than one decision, we take the 1st one
        # print(out[0]['D'])  # Test
        toDo = out[0]['D']
    else:
        toDo = 'Stay'
    if toDo == 'GoStraight':
        kobukyDecisionVelocity.linear.x = 0.0
        kobukyDecisionVelocity.linear.y = 0.25  # Go forward at 0.25 m/s
        kobukyDecisionVelocity.angular.z = 0.0
    elif toDo == 'TurnEast':
        kobukyDecisionVelocity.linear.x = 0.0
        kobukyDecisionVelocity.linear.y = -0.25  # Go back at 0.25 m/s
        kobukyDecisionVelocity.angular.z = 0.25  # Turn Right at 0.25 rad/s
    elif toDo == 'TurnWest':
        kobukyDecisionVelocity.linear.x = 0.0
        kobukyDecisionVelocity.linear.y = -0.25  # Go back at 0.25 m/s
        kobukyDecisionVelocity.angular.z = -0.25  # Turn Left at 0.25 rad/s
    elif toDo == 'TurnSouth':
        kobukyDecisionVelocity.linear.x = 0.0
        kobukyDecisionVelocity.linear.y = -0.25  # Go back at 0.25 m/s
        kobukyDecisionVelocity.angular.z = 1.0  # Turn Left at 0.25 rad/s
    else:  # toDo == 'Stay'
        kobukyDecisionVelocity.linear.x = 0.0
        kobukyDecisionVelocity.linear.y = 0.0  
        kobukyDecisionVelocity.angular.z = 0.0
    pubKobukiVelocity.publish(kobukiDecisionVelocity)
    rospy.loginfo('decisionVelocity.x: {}, decisionVelocity.y: {}, decisionVelocity.z: {}'.format(kobukyDecisionVelocity.linear.x , kobukyDecisionVelocity.linear.y, kobukyDecisionVelocity.angular.z))
    prologEngine.retractall('perceptionBumper(_)')
    print 'Previous knowledge retracted...'

def decisionCallbackPy(kobukiStatus):
    print 'Decision taking started...'
    west = kobukiStatus.bumperW
    north = kobukiStatus.bumperN
    east = kobukiStatus.bumperE
    rospy.loginfo('west: {}, north: {}, est: {}'.format(west, north, east))
    if north is False:
        kobukyDecisionVelocity.linear.x = 0.0
        kobukyDecisionVelocity.linear.y = 0.25  # Go forward at 0.25 m/s
        kobukyDecisionVelocity.angular.z = 0.0
    elif east is False:
        kobukyDecisionVelocity.linear.x = 0.0
        kobukyDecisionVelocity.linear.y = -0.25  # Go back at 0.25 m/s
        kobukyDecisionVelocity.angular.z = 0.25  # Turn Right at 0.25 rad/s
    elif west is False:
        kobukyDecisionVelocity.linear.x = 0.0
        kobukyDecisionVelocity.linear.y = -0.25  # Go back at 0.25 m/s
        kobukyDecisionVelocity.angular.z = -0.25  # Turn Left at 0.25 rad/s
    elif (north and east and west):
        kobukyDecisionVelocity.linear.x = 0.0
        kobukyDecisionVelocity.linear.y = -0.25  # Go back at 0.25 m/s
        kobukyDecisionVelocity.angular.z = 1.0  # Turn Left at 0.25 rad/s
    else:  # stay
        kobukyDecisionVelocity.linear.x = 0.0
        kobukyDecisionVelocity.linear.y = 0.0  
        kobukyDecisionVelocity.angular.z = 0.0
    pubKobukiVelocity.publish(kobukiDecisionVelocity)
    rospy.loginfo('decisionVelocity.x: {}, decisionVelocity.y: {}, decisionVelocity.z: {}'.format(kobukyDecisionVelocity.linear.x , kobukyDecisionVelocity.linear.y, kobukyDecisionVelocity.angular.z))
    
def think():
    # learn('behaviour.pl')  # Pyswip is not compatible
    rospy.init_node('act')
    rospy.Subscriber("/kobuki_status", Status, decisionCallbackPy)
    rospy.spin()

if __name__ == '__main__':
    try:
        think()
    except rospy.ROSInterruptException:
        pass
