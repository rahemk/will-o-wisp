import pygame
from math import pi

MAX_FORWARD = 30
MAX_ANGULAR = pi/3

class GameScreen:
    def __init__(self, width, height):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        self.delta_time = 1
        self.terminate = False

    def get_movement(self):
        forward = 0
        angular = 0

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            forward = MAX_FORWARD * self.delta_time
        if keys[pygame.K_DOWN]:
            pass
        if keys[pygame.K_LEFT]:
            forward = MAX_FORWARD * self.delta_time
            angular = -MAX_ANGULAR * self.delta_time
        if keys[pygame.K_RIGHT]:
            forward = MAX_FORWARD * self.delta_time
            angular = MAX_ANGULAR * self.delta_time
        if keys[pygame.K_q]:
            self.terminate = True
        print(f"forward, angular: {forward, angular}")

        return forward, angular

    def update(self, robot_poses, guide_positions):
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.terminate = True

        # Fill the screen to wipe away anything from last frame
        self.screen.fill("black")

        for pose in robot_poses:
            centre = pygame.Vector2(pose[0], pose[1])
            pygame.draw.circle(self.screen, "purple", centre, 80, width=1)

        for pos in guide_positions:
            centre = pygame.Vector2(pos[0], pos[1])
            pygame.draw.circle(self.screen, "white", centre, 40)

        # flip() the display to put your work on screen
        pygame.display.flip()

        # TBD: Update self.delta_time to get framerate- independent physics?

        if self.terminate:
            self.close()

    def close(self):
        pygame.display.quit()
        pygame.quit()