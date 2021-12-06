from socket import*
import tkinter as tk
from threading import Thread
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
import sqlite3
import io
import struct
import pickle
import json


conn = sqlite3.connect('phoneBook.db')
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS members ( 
        ID INTEGER,
        username TEXT,
        password TEXT,
        firstName TEXT,
        lastName TEXT,
        email TEXT,
        phoneNumber TEXT,
        Avatar BLOB
    )""")

#cur.execute("DELETE FROM members WHERE username != :username", {'username': 'RionGamer'})
#cur.execute("SELECT * FROM members ORDER BY id DESC LIMIT 1")
#cur.execute("UPDATE members SET Avatar = 'None' WHERE ID = '20127005'")
print(cur.execute("SELECT username, password FROM members").fetchall())

#image_data = cur.execute("SELECT Avatar FROM members WHERE username = 'c' ").fetchone() # byte values of the image

#img = image_data[0]
#avatar_image = Image.open(io.BytesIO(img))
#avatar_image = avatar_image.resize((170, 60), Image.ANTIALIAS)

#newAva = ImageTk.PhotoImage(avatar_image)
#avatar = tk.Label(image=newAva).place(x = 0, y = 0)
#avatar_image.show()
#list = cur.execute("SELECT username,password FROM members").fetchall()

#print(list)
conn.commit()
conn.close()

#..........Functions.........
def verifySignUp(c, cur, list):
    signUpData = cur.execute("SELECT username, email FROM members").fetchall()
    Username = list[0]
    Email = list[4]

    for account in signUpData:
        if(Username == account[0]):
            c.sendall(bytes("duplicated_user", "utf8"))
            return False
        if(Email == account[1]):
            c.sendall(bytes("duplicated_email", "utf8"))
            return False
    c.sendall(bytes("Success", "utf8"))
    return True

def verifyLogin(c, cur):
    list=[]
    list = pickle.loads(c.recv(1024))
    Username = list[0]
    Password = list[1]

    #print(Password)
    login_Data = cur.execute("SELECT username,password FROM members").fetchall()
    for account in login_Data:
        if(Username == account[0] and Password == account[1]):
            return c.sendall(bytes("Success", "utf8"))
    return c.sendall(bytes("Fail", "utf8"))

def SendPersonalInfo(c, cur):
    get_username = c.recv(1024).decode("utf8")
    userInfo = cur.execute("SELECT ID, Avatar FROM members WHERE username == :username", {'username': get_username}).fetchone()
    c.sendall(bytes(str(userInfo[0]), "utf8"))  #Send user's ID
    Avatar = userInfo[1]                        #Send Avatar
    file_size = struct.pack('>I', len(Avatar))  #Convert int -> 4bytes
    c.sendall(file_size)
    c.send(Avatar)
    print("Done")

def SendAvatarFromID(c, cur):
    ID = c.recv(1024).decode("utf8")
    getAvatar = cur.execute("SELECT Avatar FROM members WHERE ID == :ID",{'ID': ID}).fetchone()
    Avatar = getAvatar[0]
    file_size = struct.pack('>I', len(Avatar))  # Convert int -> 4bytes
    c.sendall(file_size)
    c.send(Avatar)
    print("Done")

def showDataFromDB(cur):
    cur.execute("SELECT * FROM members")
    members = cur.fetchall()
    for member in members:
        print(member)

def recvAvatarFromUser(c, conn, cur):
    file_size = c.recv(4)
    file_size = struct.unpack('>I', file_size)[0]  # Convert 4 bytes to integer
    if file_size != 0:
        recv_size = 0
        buf = b''
        while recv_size < file_size:
            data_image = c.recv(1024)
            recv_size += len(data_image)
            buf += data_image
        print("Done")
        return buf

def recvSignUpDaTa(c, cur, conn):
    list = []
    list = pickle.loads(c.recv(1024))
    buf = None          #buffer contains image bytes
    if list[6] == 1:    #Client sent info including Avatar
        buf = recvAvatarFromUser(c, conn, cur)

    checkSignUp = verifySignUp(c, cur, list)
    if(checkSignUp == True):
        cur.execute("SELECT * FROM members ORDER BY id DESC LIMIT 1")
        last_member = cur.fetchone()
        if(last_member == None):
            assign_id = 20127000 #First member
        else:
            assign_id = last_member[0] + 1 #ID increases automatically

        cur.execute("INSERT INTO members VALUES (:ID, :username, :password, :firstName, :lastName, :email, :phoneNumber, :Avatar)",
                                                                    {'ID': assign_id,'username': list[0], 'password': list[1],
                                                                     'firstName': list[2], 'lastName': list[3],
                                                                     'email': list[4],'phoneNumber': list[5], 'Avatar':buf})
        conn.commit()

def sendPhoneBookList(c, cur):
    users_data = cur.execute("SELECT ID, firstName, lastName , email, phoneNumber FROM members").fetchall()
    send_data = pickle.dumps(users_data)
    c.send(send_data)
    for record in users_data:
        checkAvatar = cur.execute("SELECT Avatar FROM members WHERE ID == :ID", {'ID': record[0]}).fetchone()
        Avatar = checkAvatar[0] #fetchone() fetched a tuple
        file_size = struct.pack('>I', len(Avatar))  # convert int -> 4bytes
        c.send(file_size)
        c.send(Avatar)
        c.recv(1024).decode("utf8")

#-----------------Server main-----------------

def openServer():
    HOST = "127.0.0.1"
    PORT = 65331
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((HOST, PORT))
    print("..................Server.................")
    print("Waiting for a Connection...")
    s.listen(3)
    clientNum = 0
    while True:
        c, a = s.accept()
        clientNum += 1
        print("%s:%s has connected." % a)
        t = Thread(target=server, args=(c,))
        t.start()

def server(c):
    #Connect to Database
    conn = sqlite3.connect('phoneBook.db')
    cur = conn.cursor()

    try:
        while True:
            data = c.recv(1024).decode("utf8")

            if data == "quit":
                c.sendall(bytes("Thank you!", "utf8"))
                print("Client off detected")
                break
            if data == "SignUp":
                recvSignUpDaTa(c, cur, conn)
            if data == "Login":
                verifyLogin(c, cur)
            if data == "GetList":
                sendPhoneBookList(c, cur)
            if data == "SendMyData":
                SendPersonalInfo(c, cur)
            if data == "SendAvatarWithID":
                SendAvatarFromID(c, cur)
    except ConnectionResetError:
        print("Client lost connection")
    except (KeyboardInterrupt, OSError):
        c. close()
    finally:
        conn.close()
        c.close()

def Server_GUI():
    window = tk.Tk()
    window.geometry('620x400')
    window.title("Server")
    window.resizable(0, 0)  # window lock(can't be resize() )

    btn_Open = tk.Button(window, text="Open Server", width=10, height=2, fg="black", bg="#42c5f5",
                          font=("Helvetica",15, 'bold'), command=lambda: Thread(target=openServer).start())
    btn_Open.pack()


    window.mainloop()

Server_GUI()