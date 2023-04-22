#!/usr/bin/env python

'''
A script to test SwarmJSLevel.
'''

from swarmjs_level import SwarmJSLevel
from wow_tag import WowTag
 
if __name__ == "__main__":

    wow_tags = [WowTag(0, 541, 260, -0.5), WowTag(1, 745, 182, -1.5)]
    level = SwarmJSLevel("IGNORED PARAMS")
    journey_dict = level.get_journey_dict("", wow_tags)
    print(journey_dict)
