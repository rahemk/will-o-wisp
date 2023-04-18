# -P: Display output as it arrives.
# -t 0: Don't timeout
# -O "RequestTTY force": This forces pseudo-terminal behaviour of the underlying ssh process.
#                        The purpose here is so we can hit CTRL-C and have the client process
#                        terminate
parallel-ssh -P -t 0 -O "RequestTTY force" -h robot_addresses cd minion_src \; ./main_with_visual_goal.py
