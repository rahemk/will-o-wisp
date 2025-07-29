Will-o-Wisp

This is a slightly improved version of the Will-o-Wisp robotics game, originally developed by https://github.com/avardy. This version includes:

- A new versus mode for player vs player
- Visual and Sound effects
- Improved Performance

## Requirements

- Zumo robots with Light sensors and April tags
- Screen to display and move the robots
- Webcam positioned above and in view of the screen

## How to Run

1. Install dependencies from requirements.txt
2. Run april_tags_calibrate.py for calibrating the tags. Move the files it creates to will-o-wisp-main\tg_calib_lab\delta_1.
3. Run main

Levels can be chosen by commenting out/in the desired level.

For the FirstGameLevel, the player can move their robot with the arrow keys and shoot with the spacebar 

For the versus level, Player1 can move their robot with the arrow keys and shoot with the spacebar. Player2 can move their robot with the WASD keys and shoot 
with Enter. Its best to have Player 1 be on the left side of the screen and Player 2 on the right as should their robots so that the Win text makes sense. 
