import datetime
import hashlib
import os
import subprocess
import sys
import time
import io


from serial import Serial


def print_menu():       
    print 30 * "-" , "BADANIE" , 30 * "-"
    print "1. Test na pliku tekstowym"
    print "2. Test na pliku dowolnym pliku"
    print "3. Menu Option 3"
    print "4. Menu Option 4"
    print "5. Exit"
    print 67 * "-"
  
def md5(file_name):
    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def write_file(data):
    file_name = os.getcwd() + '/file.txt'
    with open(file_name, 'wb') as x_file:
        x_file.write('{}'.format(data))


def dodaj_do_logu(append_text):
    log_name = os.getcwd()+'/log.txt'
    with open(log_name, 'a') as myfile:
        myfile.write('{}'.format(append_text))

def dodaj_do_logu_err(append_text):
    log_name = os.getcwd()+'/log_err.txt'
    with open(log_name, 'a') as myfile:
        myfile.write('{}'.format(append_text))


loop=True      
  
while loop:          
    print_menu()   
    choice = input("Enter your choice [1-5]: ")
     
    if choice==1:     
        print "Wybrano badanie bazujace na pliku tekstowym"
        start_baud = raw_input("Wprowadz predkosc poczatkowa: ")
        stop_baud = raw_input("Wprowadz predkosc koncowa: ")
        krok = raw_input("Wprowadz krok do iteracji: ")
        tresc_pliku = ""
        tresc_pliku = raw_input("Wprowadz tekst: ")
        file_name = os.getcwd() + '/file.txt'
        #########################################################################################################
        write_file(tresc_pliku)
        start_baud = int(start_baud)
        stop_baud = int(stop_baud)
        krok = int(krok)
        stop_baud = int(stop_baud)+krok

        for i in xrange(start_baud, stop_baud, krok):

            start_time = datetime.datetime.now()
            print ("uruchamiam serwer")
            subprocess.Popen(['python', os.getcwd() + '/serwer.py', str(i), file_name],
                shell=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            print ("serwer uruchomiony")
            time.sleep(0.05) #50 milisekund
            ser = Serial('/dev/ttyUSB0', i)
            ser.write("<<SENDFILE>>\n") 
            readline = lambda : iter(lambda:ser.read(1), "\n")
            with open(os.getcwd() + '/file_out.txt', "wb") as outfile:
                while True:
                    line = "".join(readline())
                    if line == "<<EOF>>":
                        break  # done so stop accumulating lines
                    print >> outfile, line
            f = open(file_name)
            contents = f.read()
            f.close()
            new_contents = contents.replace('\n', '')
            f = open('file'+str(i)+'.txt', 'w')
            
            f.write(new_contents)
            f.close()
            os.remove('file_out.txt')
            print "wykonano test z baudem:", i
            suma_nadanego = md5(os.getcwd()+"/file.txt")
            suma_odebranego = md5(os.getcwd()+'/file'+str(i)+'.txt')
            print "md5 pliku nadanego:   ", suma_nadanego
            print "md5 pliku odebranego: ", suma_odebranego
            print "Sa takie same?", 
            bool_md5 = suma_nadanego==suma_odebranego
            print suma_nadanego==suma_odebranego
            stop_time = datetime.datetime.now()
            delta = stop_time-start_time
            delta = int(delta.total_seconds() * 1000)
            delta = delta - 50 #odjac czas czekania na spawn procesu serwera
            print "Test na tym baudzie zajal:", delta, "milisekund"
            dodaj_do_logu('-------------------------\n')
            dodaj_do_logu('Baud: ' + str(i) + '\n')
            dodaj_do_logu('Czas [ms]: ' + str(delta)+'\n')
            dodaj_do_logu('Suma kontrolna nadanego = suma kontrolna odebranego : ' + str(bool_md5) + '\n')
        if bool_md5 == False:
            dodaj_do_logu_err("Baud:", str(i) + '\n')
        
        

        #########################################################################################################
        
        ## You can add your code or functions here
    elif choice==2:
        print "Wybrano badanie bazujace na pliku graficznym"
        start_baud = raw_input("Wprowadz predkosc poczatkowa: ")
        stop_baud = raw_input("Wprowadz predkosc koncowa: ")
        krok = raw_input("Wprowadz krok do iteracji: ")
        file_name = os.getcwd() + r'/' + raw_input("Wprowadz nazwe pliku wraz z rozszerzeniem: ")
        
        start_baud = int(start_baud)
        stop_baud = int(stop_baud)
        krok = int(krok)
        stop_baud = int(stop_baud)+krok
        
        for i in xrange(start_baud, stop_baud, krok):

            start_time = datetime.datetime.now()
            print ("uruchamiam serwer")
            subprocess.Popen(['python', os.getcwd() + '/serwer.py', str(i), str(file_name)],
                shell=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            print ("serwer uruchomiony")
            time.sleep(0.05) #50 milisekund
            ser = Serial('/dev/ttyUSB0', i)
            ser.write("<<SENDFILE>>\n") 
            readline = lambda : iter(lambda:ser.read(1), "\n")
            with open(file_name + str(i), "wb") as outfile:
                while True:
                    line = "".join(readline())
                    if line == "<<EOF>>":
                        break 
                    print >> outfile, line
            fp = open(file_name + str(i), "rb")
            data = fp.read()
            fp.close()

            fp = open(file_name + str(i), "wb")
            fp.write(data[0:-1])
            fp.close()       
            print "wykonano test z baudem:", i
            suma_nadanego = md5(file_name)
            suma_odebranego = md5(file_name + str(i))
            print "md5 pliku nadanego:   ", suma_nadanego
            print "md5 pliku odebranego: ", suma_odebranego
            print "Sa takie same?", 
            bool_md5 = suma_nadanego==suma_odebranego
            print suma_nadanego==suma_odebranego
            stop_time = datetime.datetime.now()
            delta = stop_time-start_time
            delta = int(delta.total_seconds() * 1000)
            delta = delta - 50 #odjac czas czekania na spawn procesu serwera
            print "Test na tym baudzie zajal:", delta, "milisekund"
            dodaj_do_logu('-------------------------\n')
            dodaj_do_logu('Baud: ' + str(i) + '\n')
            dodaj_do_logu('Czas [ms]: ' + str(delta)+'\n')
            dodaj_do_logu('Suma kontrolna nadanego = suma kontrolna odebranego : ' + str(bool_md5) + '\n')
            if bool_md5 == False:
                dodaj_do_logu_err("Baud:" + str(i) + '\n')
        
        
        
        ## You can add your code or functions here
    elif choice==3:
        print "Menu 3 has been selected"
        ## You can add your code or functions here
    elif choice==4:
        print "Menu 4 has been selected"
        ## You can add your code or functions here
    elif choice==5:
        print "Menu 5 has been selected"
        ## You can add your code or functions here
        loop=False # This will make the while loop to end as not value of loop is set to False
    else:
        # Any integer inputs other than values 1-5 we print an error message
        raw_input("Wrong option selection. Enter any key to try again..")
