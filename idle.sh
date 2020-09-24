#!/bin/bash                                                                
                                                                           
cleanup ()                                                                 
{                                                                          
  kill -s SIGTERM $!                                                         
  exit 0                                                                     
}                                                                          

# Make sure all ports are in Output mode
# you can still read even when in output mode
# but you can't write in input mode
echo "out" > /dev/dio-1
echo "out" > /dev/dio-2
echo "out" > /dev/dio-3
echo "out" > /dev/dio-4

# Start the Python Modbus server here. If the server dies on purpose or not, 
# this script will continue to run giving you an option to start the server
# manually or perform troubleshooting
python3 /modbus_server.py &                                                                                                                                                                                  
                                                                           
trap cleanup SIGINT SIGTERM                                                
                                                                           
while [ 1 ]                                                                
do                                                                         
  sleep 60 &                                                             
  wait $!                                                                
done
