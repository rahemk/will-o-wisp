'''
A WowTag (will-o-wisp tag) is distinct from one of the tags produced by
Apriltags.
'''

from math import atan2, pi

class WowTag:
    def __init__(self, id, x, y, angle):
        self.id = id
        self.x = x
        self.y = y
        self.angle = angle
    def __str__(self):
        return f"{self.id}, {self.x}, {self.y}, {self.angle}"

def apply_tg_calibration_to_raw_tags(raw_tags, tg_calib_count, tg_calib_x, tg_calib_y):
    '''Apply tag grid calibration data to the center and corners of these
    raw apriltags.  Returns the calibrated tags, excluding any where needed
    calibration data is missing.'''
    calibrated_tags = []
    for raw_tag in raw_tags:

        index = int(raw_tag.center[1]), int(raw_tag.center[0])
        if tg_calib_count[index] == 0:
            print("Rejected center.")
            continue

        raw_tag.center[0] = tg_calib_x[index]
        raw_tag.center[1] = tg_calib_y[index]

        valid = True
        for corner_i in range(4):
            index = int(raw_tag.corners[corner_i, 1]), int(raw_tag.corners[corner_i, 0])
            #if tg_calib_count[index] == 0:
            #    print("Rejected corner.")
            #    valid = False
            #    break

            raw_tag.corners[corner_i, 0] = tg_calib_x[index]
            raw_tag.corners[corner_i, 1] = tg_calib_y[index]

        if valid:
            calibrated_tags.append(raw_tag)

    return calibrated_tags

def raw_tags_to_wow_tags(raw_tags):
    wow_tags = []
    for raw_tag in raw_tags:
        cx = int(raw_tag.center[0])
        cy = int(raw_tag.center[1])
        #cv2.circle(raw_image, (cx, cy), 10, (255,0,255), thickness=5)

        # Estimate the angle, choosing corner 1 as the origin and corner 0
        # as being in the forwards direction, relative to corner 1.
        x = raw_tag.corners[0,0] - raw_tag.corners[1,0]
        y = raw_tag.corners[0,1] - raw_tag.corners[1,1]
        tag_angle = atan2(y, x) + pi/2
        #cv2.putText(raw_image, str(theta), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        wow_tag = WowTag(raw_tag.tag_id, cx, cy, tag_angle)
        wow_tags.append(wow_tag)
    return wow_tags


def raw_tags_to_wow_tags(raw_tags):
    wow_tags = []
    for raw_tag in raw_tags:
        cx = int(raw_tag.center[0])
        cy = int(raw_tag.center[1])
        #cv2.circle(raw_image, (cx, cy), 10, (255,0,255), thickness=5)

        # Estimate the angle, choosing corner 1 as the origin and corner 0
        # as being in the forwards direction, relative to corner 1.
        x = raw_tag.corners[0,0] - raw_tag.corners[1,0]
        y = raw_tag.corners[0,1] - raw_tag.corners[1,1]
        tag_angle = atan2(y, x) + pi/2
        #cv2.putText(raw_image, str(theta), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        wow_tag = WowTag(raw_tag.tag_id, cx, cy, tag_angle)
        wow_tags.append(wow_tag)
    return wow_tags
