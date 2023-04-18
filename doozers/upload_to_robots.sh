COPY='parallel-scp -h robot_addresses -r'
COMMAND='parallel-ssh -i -h robot_addresses'
HOME_DIR=/home/instructor

# Erase the current CurveFollow directory on the robots.
$COMMAND rm -fr $HOME_DIR/CurveFollow

# Upload the new one
$COPY CurveFollow $HOME_DIR

# -P: Display output as it arrives.
# -t 0: Don't timeout
# -O "RequestTTY force": This forces pseudo-terminal behaviour of the underlying ssh process.
#                        The purpose here is so we can hit CTRL-C and have the client process
#                        terminate
parallel-ssh -P -t 0 -O "RequestTTY force" -h robot_addresses cd CurveFollow \; ./upload.sh
