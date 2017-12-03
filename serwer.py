from serial import Serial
import os
import sys

#file_name = os.getcwd() + '/file.txt'


def write_file(data):
    file_name = os.getcwd() + '/file.txt'
    with open(file_name, 'wb') as x_file:
        x_file.write('{}'.format(data))



ser = Serial('/dev/ttyUSB1', sys.argv[1]) 
readline = lambda : iter(lambda:ser.read(1),"\n")
while "".join(readline()) != "<<SENDFILE>>":
    pass

ser.write(open(sys.argv[2],"rb").read()) #send file
ser.write("\n<<EOF>>\n") #send message indicating file transmission complete
