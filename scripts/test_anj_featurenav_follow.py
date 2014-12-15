#!/usr/bin/python
# -*- coding: utf-8 -*-

import rospy
import actionlib

from lama_jockeys.msg import NavigateAction
from lama_jockeys.msg import NavigateGoal

_edge_id = 1

if __name__ == '__main__':
    import sys
    try:
        edge_id = int(sys.argv[1])
    except (IndexError, ValueError):
        edge_id = _edge_id
    rospy.init_node('test_anj_featurenav')

    client = actionlib.SimpleActionClient('anj_featurenav_navigator',
                                          NavigateAction)
    while not client.wait_for_server(rospy.Duration(5)):
        rospy.loginfo(('waiting for action server "{}"').format(
            'anj_featurenav_navigator'))

    navigate_goal = NavigateGoal()
    navigate_goal.action = navigate_goal.TRAVERSE
    navigate_goal.edge.id = edge_id
    rospy.loginfo('Starting following segment on edge {}'.format(edge_id))
    client.send_goal_and_wait(navigate_goal)
    result = client.get_result()

    if result.final_state != result.DONE:
        rospy.logerr('Navigation error')
        exit()

    rospy.loginfo('Navigation successful')

    rospy.spin()
