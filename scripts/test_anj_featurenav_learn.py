#!/usr/bin/python
# -*- coding: utf-8 -*-

import rospy
import actionlib

from lama_interfaces.core_interface import MapAgentInterface
from lama_interfaces.msg import LamaObject
from lama_interfaces.srv import ActOnMap
from lama_interfaces.srv import ActOnMapRequest
from lama_jockeys.msg import LearnAction
from lama_jockeys.msg import LearnGoal


def add_edge_to_map(descriptor_link):
    """Add two vertices and an edge and assign the segment"""
    iface = MapAgentInterface(start=False)
    map_agent = rospy.ServiceProxy(iface.action_service_name,
                                   ActOnMap)
    rospy.loginfo('Waiting for service')
    map_agent.wait_for_service()
    rospy.loginfo('MapAgent ready')

    edge = LamaObject()
    edge.type = edge.EDGE
    edge.references = [-1, -1]
    edge_response = map_agent(object=edge, action=ActOnMapRequest.PUSH_EDGE)
    if not edge_response.objects:
        rospy.logerr('Database error')
        return
    edge_id = edge_response.objects[0].id
    rospy.loginfo('edge {} added'.format(edge_id))

    # Assign segment.
    map_action = ActOnMapRequest()
    map_action.action = map_action.ASSIGN_DESCRIPTOR_EDGE
    map_action.object.id = edge_id
    map_action.descriptor_id = descriptor_link.descriptor_id
    map_action.interface_name = descriptor_link.interface_name
    map_agent(map_action)
    rospy.loginfo('segment {} assigned to edge {}'.format(
        descriptor_link.descriptor_id, edge_id))

if __name__ == '__main__':
    import sys
    rospy.init_node('test_anj_featurenav')
    rospy.loginfo('sys.argv: {}'.format(sys.argv)) # debug
    try:
        learning_time = float(sys.argv[1])
    except (IndexError, ValueError):
        learning_time = 5

    client = actionlib.SimpleActionClient('anj_featurenav_learner', LearnAction)
    client.wait_for_server()

    learn_goal = LearnGoal()
    learn_goal.action = learn_goal.LEARN
    client.send_goal(learn_goal)

    rospy.loginfo('Learning started for {} s'.format(learning_time))

    # Wait for a determined time because action will never stop.
    rospy.sleep(learning_time)

    learn_goal = LearnGoal()
    learn_goal.action = learn_goal.STOP_LEARN
    client.send_goal_and_wait(learn_goal)
    learn_result = client.get_result()
    if not learn_result:
        rospy.logerr('Did not receive segment descriptor')
        exit()
    add_edge_to_map(learn_result.descriptor_links[0])

    rospy.loginfo('Learning finished')

    rospy.spin()
