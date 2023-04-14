import os, pygame
from math import cos, pi, sin

POSE_RADIUS = 65

class GameScreen:
    def __init__(self, width, height):

        os.environ['SDL_VIDEO_WINDOW_POS'] = "1920,0"
        pygame.init()
        self.screen = pygame.display.set_mode((width, height), flags=pygame.SCALED)
        pygame.display.toggle_fullscreen()
        self.terminate = False

    def get_movement(self):
        keys = pygame.key.get_pressed()
        result = ""
        if keys[pygame.K_UP]:
            result = "forward"
        if keys[pygame.K_DOWN]:
            pass
        if keys[pygame.K_LEFT]:
            result = "left"
        if keys[pygame.K_RIGHT]:
            result = "right"
        if keys[pygame.K_q]:
            self.terminate = True

        print(result)
        return result

    def update(self, robot_poses, guide_positions):
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.terminate = True

        # Fill the screen to wipe away anything from last frame
        self.screen.fill("black")

        for pose in robot_poses:
            centre = pygame.Vector2(pose[0], pose[1])
            on_circle = pygame.Vector2(pose[0] + POSE_RADIUS * cos(pose[2]), \
                                       pose[1] + POSE_RADIUS * sin(pose[2]))
            pygame.draw.circle(self.screen, "purple", centre, POSE_RADIUS, width=2)
            pygame.draw.line(self.screen, "purple", centre, on_circle)

        for pos in guide_positions:
            centre = pygame.Vector2(pos[0], pos[1])
            pygame.draw.circle(self.screen, "white", centre, 10)

        # flip() the display to put your work on screen
        pygame.display.flip()

        # TBD: Update self.delta_time to get framerate- independent physics?

        if self.terminate:
            self.close()

    def close(self):
        pygame.display.quit()
        pygame.quit()