from socket import*
import tkinter as tk
from tkinter import ttk, Canvas, BOTH
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
from tkinter import filedialog
from threading import Thread
import struct
import pickle
import json
import io
import os
import time

def connect(input, window):
    global flag
    IP = input.get()
    addr = (IP, PORT)
    if IP == "" or IP == "Enter IP":
        messagebox.showwarning("Warning", "You have to enter IP's address first")
    else:
        try:
            c.connect(addr)
            messagebox.showinfo("Welcome", "Connected Successfully!")
            Thread(target=appStart, args=(window,)).start()
        except Exception:
            messagebox.showerror("Connection Fail", "Invalid IP address or target actively refused.Try again")

def drawLine(X, Y, Length, border_color, line_color):
    Line = Canvas(window, width=Length, height=0.5, highlightbackground=border_color)
    Line.create_line(0, 2, Length, 2, fill=line_color)
    Line.place(x=X, y=Y)

def toggle_Pass(Password_entry, X, Y):
    if Password_entry.cget('show') == '':
        Password_entry.config(show='.')
        set_hideIcon = tk.Button(image=hidePass_icon, command=lambda: toggle_Pass(Password_entry, X, Y), bd=0, bg="white").place(
            x=X, y=Y)
    else:
        Password_entry.config(show='')
        set_showIcon = tk.Button(image=showPass_icon, command=lambda: toggle_Pass(Password_entry, X, Y), bd=0, bg="white").place(
            x=X, y=Y)

def recvImagesFromServer():
    file_size = c.recv(4)
    file_size = struct.unpack('>I', file_size)[0]  # Convert 4 bytes to integer
    if file_size != 0:
        buf = b''
        recv_size = 0
        print(file_size)
        while recv_size < file_size:
            data_img = c.recv(1024)
            recv_size += len(data_img)
            buf += data_img
        return buf

def getPhoneBookList(window, phoneBook_tree):
    #Clean the Tree
    for i in phoneBook_tree.get_children():
        phoneBook_tree.delete(i)
    window.update()

    #Send order
    c.sendall(bytes("GetList", "utf8"))

    #Recieve all users data
    users_data = []
    users_data = pickle.loads(c.recv(1024))
    #print(users_data)

    #Recieve Avatar
    window.list_avatar = []
    cnt = 0
    for record in users_data:
        buf = recvImagesFromServer()
        c.sendall(bytes("Done", "utf8")) #Sending to reset the buffer -> prevent window from freezing
        Avatar = Image.open(io.BytesIO(buf))
        Avatar = Avatar.resize((40, 40), Image.ANTIALIAS)
        Avatar_obj = ImageTk.PhotoImage(Avatar)
        window.list_avatar.append(Avatar_obj)

        if cnt % 2 == 0:
            phoneBook_tree.insert('', 'end', image=window.list_avatar[cnt],
                                  values=(record[0], record[1], record[2],record[3], record[4]), tags=('evenrow',))
        else:
            phoneBook_tree.insert('', 'end', image=window.list_avatar[cnt],
                                  values=(record[0], record[1], record[2], record[3], record[4]), tags=('oddrow',))
        cnt += 1

def sendImageToServer(filename):
    file_size = os.path.getsize(filename)  # get image's size
    image = open(filename, "rb")
    file_size = struct.pack('>I', file_size)  # convert int -> 4bytes
    c.send(file_size)

    data_image = image.read(1024)
    while (True):
        c.send(data_image)
        data_image = image.read(1024)
        if not data_image:
            break

def upload_Image(window, X, Y, width, height):
    global filename
    filename = filedialog.askopenfilename(initialdir="/C", title="Select Image For Your Avatar")
    showAvatar = Image.open(filename)
    showAvatar = showAvatar.resize((width, height), Image.ANTIALIAS)  # resize the image
    global showAvatar_newImg
    showAvatar_newImg = ImageTk.PhotoImage(showAvatar)
    show = tk.Label(image=showAvatar_newImg).place(x=X, y=Y)

    global changePic_Img
    changePic_Img = tk.PhotoImage(file="images/changePic_btn.png")
    set_btn = tk.Button(image=changePic_Img, bd=0, bg="white",command=lambda: upload_Image(window, X, Y, width, height))
    set_btn.place(x=X-2, y=Y+height+2)

    return filename

def getWarningIcon(window):
    warning_img = Image.open("images/warning_icon.png")
    global warning_icon
    warning_icon = ImageTk.PhotoImage(warning_img)
    return warning_icon

def getErrorIcon(window):
    error_img = Image.open("images/error_icon.png")
    global error_icon
    error_icon = ImageTk.PhotoImage(error_img)
    return error_icon

def checkUserInput(window, string, entry):
    #Check Empty Field
    if(entry.get() == "" or entry.get() == string):
        entry.config(highlightthickness=0.5, highlightbackground="red", highlightcolor="red")
        show_warning_text = tk.Label(text="*Empty field detected*", fg="red", bg="white")
        show_warning_text.place(x=690, y=400)
        entry.bind("<Button-1>", lambda e: [entry.delete(0, tk.END),entry.config(highlightthickness=0),
                                                        show_warning_text.place_forget(),entry.unbind("<Button-1>")])
        return False
    return True

def verifyLogin(window, username_entry, password_entry):
    warning_img = getWarningIcon(window)
    check = 1

    if(username_entry.get() == "Enter username" or username_entry.get() == ""):
        warning1 = tk.Label(image=warning_img, bd=0, bg="white")
        warning1.place(x=610, y=205)
        drawLine(355, 250, 290, None, "red")
        username_entry.bind("<Button-1>", lambda e: [username_entry.delete(0, tk.END),warning1.place_forget(),
                                        drawLine(355, 250, 290, None, "black"),username_entry.unbind("<Button-1>")])
        check = 0
    if(password_entry.get() == "Enter password" or password_entry.get() == ""):
        warning2 = tk.Label(image=warning_img, bd=0, bg="white")
        warning2.place(x=610, y=310)
        drawLine(355, 350, 290, None, "red")
        password_entry.bind("<Button-1>", lambda e: [password_entry.delete(0, tk.END), warning2.place_forget(),
                                        drawLine(355, 350, 290, None, "black"),password_entry.unbind("<Button-1>")])
        check = 0
    if(check == 1):
        c.sendall(bytes("Login", "utf8"))
        list = [username_entry.get(), password_entry.get()]
        c.send(pickle.dumps(list))

        server_response = c.recv(1024).decode("utf8")
        if server_response == "Fail":
            show_warning_text = tk.Label(text="*Wrong Username or Password**", fg="red", bg="white")
            show_warning_text.place(x=370, y=367)
            drawLine(355, 250, 290, None, "red")
            drawLine(355, 350, 290, None, "red")
            username_entry.bind("<Button-1>", lambda e: [show_warning_text.place_forget(), drawLine(355, 250, 290, None, "black"),
                                                                                username_entry.unbind("<Button-1>")])
            password_entry.bind("<Button-1>", lambda e: [show_warning_text.place_forget(), drawLine(355, 350, 290, None, "black"),
                                                                                password_entry.unbind("<Button-1>")])
        else:
            phoneBook_GUI(window, username_entry.get())

def verifySignUp(window, username_entry, password_entry, confirm_password_entry):
    warning_img = getWarningIcon(window)
    show_warning_text = tk.Label(text="*Empty field detected*", fg="red", bg="yellow")
    check = 1 #SignUp Successfully

    if (username_entry.get() == "Enter username" or username_entry.get() == ""):
        check = 0
        warning1 = tk.Label(image=warning_img, bd=0, bg="white")
        warning1.place(x=730, y=205)
        show_warning_text.place(x=650, y=400)
        drawLine(475, 250, 290, None, "red")
        username_entry.bind("<Button-1>", lambda e: [username_entry.delete(0, tk.END), warning1.place_forget(),
                                                    drawLine(475, 250, 290, None, "black"), show_warning_text.place_forget(),
                                                    username_entry.unbind("<Button-1>")])
    if (password_entry.get() == "Enter password" or password_entry.get() == ""):
        check = 0
        warning2 = tk.Label(image=warning_img, bd=0, bg="white")
        warning2.place(x=730, y=307)
        show_warning_text.place(x=650, y=400)
        drawLine(475, 350, 290, None, "red")
        password_entry.bind("<Button-1>", lambda e: [password_entry.delete(0, tk.END), warning2.place_forget(),
                                                     drawLine(475, 350, 290, None, "black"),show_warning_text.place_forget(),
                                                     password_entry.unbind("<Button-1>")])
    if (confirm_password_entry.get() == "Confirm password" or confirm_password_entry.get() == ""):
        check = 0
        warning3 = tk.Label(image=warning_img, bd=0, bg="white")
        warning3.place(x=730, y=355)
        show_warning_text.place(x=650, y=400)
        drawLine(475, 350, 290, None, "red")
        confirm_password_entry.bind("<Button-1>", lambda e: [confirm_password_entry.delete(0, tk.END), warning3.place_forget(),
                                                    drawLine(475, 350, 290, None, "black"),show_warning_text.place_forget(),
                                                    confirm_password_entry.unbind("<Button-1>")])
    if(check == 1):
        if(password_entry.get() != confirm_password_entry.get()):
            drawLine(475, 350, 290, None, "#ebd513")
            show_warning_text = tk.Label(text="*Confirm password does not match*", fg="red", bg="yellow")
            show_warning_text.place(x=640, y=400)
            confirm_password_entry.bind("<Button-1>",lambda e: [drawLine(475, 350, 290, None, "black"),show_warning_text.place_forget(),
                                                                            confirm_password_entry.unbind("<Button-1>")])

        else: PersonalInfo(window, username_entry.get())

def sendUserInfo(window):
    list = [input_username.get(),
            input_password.get(),
            first_Name.get(),
            last_Name.get(),
            user_email.get(),
            phone_number.get(), 0]
    if 'filename' in globals(): # SendWithAvatar
        list[6] = 1 #With Avatar

    c.sendall(bytes("SignUp", "utf8"))
    data = pickle.dumps(list)
    c.send(data)
    if 'filename' in globals():
        sendImageToServer(filename)

    server_response = c.recv(1024).decode("utf8")
    if server_response == "duplicated_user":
        messagebox.showerror("Sorry!", "Username is already registered.Change another one")
        Register(window)
    elif server_response == "duplicated_email":
        messagebox.showerror("Sorry!", "Email is already in use by another account")
    elif server_response == "Success":
        #WelcomeToApp()
        phoneBook_GUI(window)

def verifySubmitUserInfo(window, list):
    cnt_check = 0
    for i in list:
        check = checkUserInput(window, i[1], i[0])
        if(check == 1):
            cnt_check += 1
    if(cnt_check == len(list)):
        sendUserInfo(window)


def showInput(entry, string, DATA):
    if (entry.get() == ""):
        entry.insert(0, string)
        entry.bind("<Button-1>",lambda e: [entry.delete(0, tk.END), entry.unbind("<Button-1>")])
    elif(entry.get() == string):
        entry.bind("<Button-1>", lambda e: [entry.delete(0, tk.END), entry.unbind("<Button-1>")])
    else:
        DATA = entry.get()
        entry.delete(0, tk.END)
        entry.insert(0, DATA)

def Register(window):
    Frame_right = tk.Frame(bg="white").place(x=400, y=100, width=500, height=500)
    SignUp_Text = tk.Label(text="Sign Up", font=("Poppins-Bold", 25, "bold"), fg="black", bg="white")
    SignUp_Text.place(x=580, y=110)

    #Username
    Username = tk.Label(text="Username", font=("Poppins-Regular", 11, "bold"), fg="black", bg="white")
    Username.place(x=478, y=180)
    username_entry = tk.Entry(font=("Poppins-Regular", 12, "bold"),fg="grey", bg="white", textvariable=input_username, bd=0)
    username_entry.place(x=510, y=215, width=250)

    username_img = Image.open("images/username_icon.png")
    global username_icon
    username_icon = ImageTk.PhotoImage(username_img)
    set_icon = tk.Label(image=username_icon, bd=0).place(x=470, y=205)

    #Password
    Password = tk.Label(text="Password", font=("Poppins-Regular", 11, "bold"), fg="black", bg="white")
    Password.place(x=478, y=280)
    Password_entry = tk.Entry(font=("Poppins-Regular", 12, "bold"), show='.', fg="grey", bg="white",
                                  textvariable=input_password, bd=0)
    Password_entry.place(x=510, y=315, width=250)

    password_img = Image.open("images/password_icon.png")
    global password_icon
    password_icon = ImageTk.PhotoImage(password_img)
    set_icon = tk.Label(image=password_icon, bd=0).place(x=470, y=309)

    #Confirm Password
    confirm_Password_entry = tk.Entry(font=("Poppins-Regular", 12, "bold"), show='.', fg="grey", bg="white",
                                          textvariable=confirm_password, bd=0)
    confirm_Password_entry.place(x=510, y=365, width=250)

    confirm_password_img = Image.open("images/password_icon.png")
    global confirm_password_icon
    confirm_password_icon = ImageTk.PhotoImage(confirm_password_img)
    set_icon = tk.Label(image=confirm_password_icon, bd=0).place(x=470, y=360)

    #showInputOnGUI
    USERNAME = input_username.get()
    PASSWORD = input_password.get()
    CONFIRM_PASSWORD = confirm_password.get()

    showInput(username_entry, "Enter username", USERNAME)
    showInput(Password_entry, "Enter password", PASSWORD)
    showInput(confirm_Password_entry, "Confirm password", CONFIRM_PASSWORD)

    #DrawLines
    drawLine(475, 250, 290, None, "black")
    drawLine(475, 350, 290, None, "black")
    drawLine(475, 530, 290, None, "black")

    # Already a member -> Login
    AlreadyAMember = tk.Label(text="Already a member?", font=("Poppins-Bold", 11, "bold"), fg="black", bg="white")
    AlreadyAMember.place(x=550, y=520)

    ButtonToLogin = tk.Button(text="Log In", bg="white", fg="black", bd=0, command=lambda: Login_GUI(window),
                                   font=("Poppins-Regular", 12, "bold", "underline")).place(x=590, y= 550)

    # Toggle_Pass(Show/Hide)
    show_passImg = Image.open("images/showPass.png")
    show_passImg = show_passImg.resize((25, 15), Image.ANTIALIAS)  # resize the image
    global showPass_icon
    showPass_icon = ImageTk.PhotoImage(show_passImg)

    hide_passImg = Image.open("images/hidePass.png")
    hide_passImg = hide_passImg.resize((25, 15), Image.ANTIALIAS)  # resize the image
    global hidePass_icon
    hidePass_icon = ImageTk.PhotoImage(hide_passImg)

    set_hideIcon = tk.Button(image=hidePass_icon, command=lambda: toggle_Pass(Password_entry, 770,317), bd=0,
                                                                                        bg="white").place(x=770,y=317)
    set_hideIcon = tk.Button(image=hidePass_icon, command=lambda: toggle_Pass(confirm_Password_entry,770,365), bd=0,
                                                                                       bg="white").place(x=770, y=365)
    # SignUp Button
    SignUp_btnImg = Image.open("images/signUp_button.png")
    SignUp_btnImg = SignUp_btnImg.resize((170, 60), Image.ANTIALIAS)  # resize the image
    global SignUp_btn
    SignUp_btn = ImageTk.PhotoImage(SignUp_btnImg)
    set_btn = tk.Button(image=SignUp_btn, command=lambda: [verifySignUp(window, username_entry, Password_entry, confirm_Password_entry)], bd=0, bg="white").place(x=535, y=430)

def PersonalInfo(window):
    Frame_right = tk.Frame(bg="white").place(x=400, y=100, width=500, height=500)
    SignUp_Text = tk.Label(text="Personal Information", font=("Poppins-Bold", 18, "bold"), fg="black", bg="white")
    SignUp_Text.place(x=530, y=110)

    #First_Name
    firstName_entry = tk.Entry(font=("Poppins-Regular", 10, 'bold'),justify='center',bg="white", textvariable=first_Name,bd = 1)
    firstName_entry.place(x=450, y=190, width=150, height=35)
    firstName = tk.Label(text="First Name", font=("Poppins-Regular", 9, 'bold'), fg="grey", bg="white")
    firstName.place(x=470, y=178)

    #Last_Name
    lastName_entry = tk.Entry(font=("Poppins-Regular", 10, 'bold'), justify='center', bg="white", textvariable=last_Name, bd=1)
    lastName_entry.place(x=700, y=190, width=150, height=35)
    lastName = tk.Label(text="Last Name", font=("Poppins-Regular", 9, 'bold'), fg="grey", bg="white")
    lastName.place(x=720, y=178)

    #Email
    email_entry = tk.Entry(font=("Poppins-Regular", 10, 'bold'), bg="white",textvariable=user_email, bd=1)
    email_entry.place(x=450, y=250, width=400, height=40)
    email_label = tk.Label(text="Your Email", font=("Poppins-Regular", 9, 'bold'), fg="grey", bg="white")
    email_label.place(x=470, y=240)

    #Phone Number
    phoneNum_entry = tk.Entry(font=("Poppins-Regular", 10, 'bold'), bg="white", textvariable=phone_number, bd=1)
    phoneNum_entry.place(x=450, y=320, width=400, height=40)
    phoneNum_label = tk.Label(text="Phone Number", font=("Poppins-Regular", 9, 'bold'), fg="grey", bg="white")
    phoneNum_label.place(x=470, y=310)

    #Upload Avatar
    Frame_setAvatar = tk.Frame(highlightbackground="grey", highlightcolor="grey",highlightthickness=2).place(x=450, y=390, width=200, height=173)
    UploadImg_label = tk.Label(text="Your Avatar", font=("Poppins-Regular", 9, 'bold'), fg="grey", bg="white").place(x=470, y=367)

    upload_btnImg = Image.open("images/Upload_Img_btn.png")
    upload_btnImg = upload_btnImg.resize((80, 25), Image.ANTIALIAS)  # resize the image
    global uploadImg_btn
    uploadImg_btn = ImageTk.PhotoImage(upload_btnImg)
    set_btn = tk.Button(image=uploadImg_btn, command=lambda: upload_Image(window,450,390,200,173), bd=0, bg="white").place(x=510, y=460)

    #showInputOnGUI
    FIRSTNAME = first_Name.get()
    LASTNAME = last_Name.get()
    EMAIL = user_email.get()
    PHONENUMBER = phone_number.get()

    showInput(firstName_entry, "First Name", FIRSTNAME)
    showInput(lastName_entry, "Last Name", LASTNAME)
    showInput(email_entry, "example@gmail.com", EMAIL)
    showInput(phoneNum_entry, "+84 1234 5678", PHONENUMBER)

    list = [(firstName_entry,"First Name"), (lastName_entry, "Last Name"), (email_entry, "example@gmail.com"), (phoneNum_entry,"+84 1234 5678")]
    #Submit button
    Submit_btnImg = Image.open("images/Submit_icon.png")
    Submit_btnImg = Submit_btnImg.resize((130, 50), Image.ANTIALIAS)  # resize the image
    global Submit_btn
    Submit_btn = ImageTk.PhotoImage(Submit_btnImg)
    set_btn = tk.Button(image=Submit_btn, command=lambda: verifySubmitUserInfo(window,list), bd=0, bg="white").place(x=720, y=450)

def SignUp_GUI(window):
    window.geometry('1100x650')
    window.bg = ImageTk.PhotoImage(file="images/SignUp_bg.png")
    window.bg_Img = tk.Label(image=window.bg).place(x=0, y=0, relwidth=1, relheight=1)

    Frame_left = tk.Frame(bg="#3d3f60").place(x=150, y=100, width=250, height=500)

    drawLine(150, 170, 246, "#3d3f60","grey")
    drawLine(150, 240, 246, "#3d3f60","grey")

    # Step 1:Register an account
    global input_username
    input_username = tk.StringVar()
    global input_password
    input_password = tk.StringVar()
    global confirm_password
    confirm_password = tk.StringVar()

    Register(window)
    Step01_Img = Image.open("images/Step01.png")
    Step01_Img = Step01_Img.resize((45, 45), Image.ANTIALIAS)  # resize the image
    global Step01_icon
    Step01_icon = ImageTk.PhotoImage(Step01_Img)
    set_Icon = tk.Button(image=Step01_icon, command=lambda: Register(window), bd=0, bg="#3d3f60").place(x=160, y= 110)

    Register_Step = tk.Button(text="Register An Account", command=lambda: Register(window),
                              fg='white', bg='#3d3f60', font=("open sans,sans-serif", 12, "bold"), borderwidth=0)
    Register_Step.place(x= 210, y=120)

    #Step 2:Personal Information
    global first_Name
    first_Name = tk.StringVar()
    global last_Name
    last_Name = tk.StringVar()
    global user_email
    user_email = tk.StringVar()
    global phone_number
    phone_number = tk.StringVar()

    Step02_Img = Image.open("images/Step02.png")
    Step02_Img = Step02_Img.resize((45, 50), Image.ANTIALIAS)  # resize the image
    global Step02_icon
    Step02_icon = ImageTk.PhotoImage(Step02_Img)
    set_Icon = tk.Button(image=Step02_icon, command=lambda: PersonalInfo(window), bd=0, bg="#3d3f60").place(x=160, y=180)

    GetInfo_Step = tk.Button(text="Personal Information", command=lambda: PersonalInfo(window),fg='white',bg='#3d3f60',
                                                            font=("open sans,sans-serif", 12, "bold"), bd=0)
    GetInfo_Step.place(x=210, y=190)

def Login_GUI(window):
    window.geometry('1000x600')
    window.bg = ImageTk.PhotoImage(file="images/Login_bg.jpg")
    window.bg_Img = tk.Label(image=window.bg).place(x=0, y=0, relwidth=1, relheight=1)

    Frame_login = tk.Frame(bg="white").place(x=330, y=100, width=350, height=400)

    #Login Title
    Login_Text = tk.Label(text="Login", font=("Poppins-Bold", 25, "bold"), fg="black", bg="white")
    Login_Text.place(x=460, y=110)

    #Username_area
    input_username = tk.StringVar()
    Username = tk.Label(text="Username", font=("Poppins-Regular", 11, "bold"), fg="black", bg="white")
    Username.place(x=358, y=180)
    username_entry = tk.Entry(font=("Poppins-Regular", 12, "bold"), bg="white",textvariable=input_username, bd=0)
    username_entry.place(x=390, y=215, width=250)

    username_img = Image.open("images/username_icon.png")
    global username_icon
    username_icon = ImageTk.PhotoImage(username_img)
    set_icon = tk.Label(image=username_icon, bd=0).place(x=350, y=205)

    #Password_area
    input_password = tk.StringVar()
    Password = tk.Label(text="Password", font=("Poppins-Regular", 11, "bold"), fg="black", bg="white")
    Password.place(x=358, y=280)
    password_entry = tk.Entry(font=("Poppins-Regular", 12, "bold"),show='.', bg="white",textvariable=input_password, bd=0)
    password_entry.place(x=390, y=315, width=250)

    password_img = Image.open("images/password_icon.png")
    global password_icon
    password_icon = ImageTk.PhotoImage(password_img)
    set_icon = tk.Label(image=password_icon, bd=0).place(x=350, y=309)

    #ShowInput
    USERNAME = input_username.get()
    PASSWORD = input_password.get()
    showInput(username_entry, "Enter username", USERNAME)
    showInput(password_entry, "Enter password", PASSWORD)

    #Toggle_Pass(Show/Hide)
    show_passImg = Image.open("images/showPass.png")
    show_passImg = show_passImg.resize((25, 15), Image.ANTIALIAS)  # resize the image
    global showPass_icon
    showPass_icon = ImageTk.PhotoImage(show_passImg)

    hide_passImg = Image.open("images/hidePass.png")
    hide_passImg = hide_passImg.resize((25, 15), Image.ANTIALIAS)  # resize the image
    global hidePass_icon
    hidePass_icon = ImageTk.PhotoImage(hide_passImg)

    set_hideIcon = tk.Button(image=hidePass_icon, command=lambda: toggle_Pass(password_entry,620,317), bd=0, bg="white").place(x=620, y=317)

    # LogIn Button
    login_btnImg = Image.open("images/login_button.png")
    login_btnImg = login_btnImg.resize((300, 55), Image.ANTIALIAS)  # resize the image
    window.login_btn = ImageTk.PhotoImage(login_btnImg)
    window.set_btn = tk.Button(image=window.login_btn, command=lambda: [verifyLogin(window,username_entry,password_entry)], bd=0, bg="white").place(x=350, y=380)

    #Not A member -> SignUp?
    Signup_choice = tk.Label(text="Not a member?", font=("Poppins-Regular", 10, "bold"), fg="black", bg="white")
    Signup_choice.place(x=450, y=440)
    ButtonToSignUp = tk.Button(text="Sign Up", bg="white", fg="black", bd=0, command=lambda: SignUp_GUI(window),
                                            font=("Poppins-Regular", 10, "bold", "underline")).place(x=470, y=465)

    #Draw a line
    drawLine(355, 250, 290, None, "black")
    drawLine(355, 350, 290, None, "black")

def SignInOrUp(window):
    window.geometry('340x500')
    Frame = tk.Frame(bg="white", width = 340, height=500).place(x=0, y=0)

    #Icon
    icon = Image.open("images/location_icon.jpg")
    icon = icon.resize((50, 50), Image.ANTIALIAS)  # resize the image
    window.resized_icon = ImageTk.PhotoImage(icon)
    window.new_icon = tk.Label(image=window.resized_icon, borderwidth=0).place(x = 150, y = 80)

    #LogIn bar
    LogIn_button = tk.Button(text="Log In", command=lambda:Login_GUI(window),
                                             fg = 'white', bg = '#2508c9', font = ("Arial", 12, 'bold'), bd=0)
    LogIn_button.place(x=50, y=250, width=250, height=35)

    #SignUp bar
    SignUp_button = tk.Button(text="Sign Up", command=lambda:SignUp_GUI(window),
                                                   fg='black', bg='#f2ebeb', font=("Arial", 12, 'bold'), bd=0)
    SignUp_button.place(x=50, y=290, width=250, height=35)

    #Text
    text1 = tk.Label(text="Stay Connected With Your Friends", font=("Helvetica", 10, "bold"), fg="black", bg="white")
    text1.place(x=60, y=150)

    #Draw_Line
    my_canvas = Canvas(window, width = 400, height = 1, bd=0)
    my_canvas.create_line(0, 2, 400, 2, fill = "blue")
    my_canvas.place(x = 2, y = 400)

def appStart(window):
    window.bg = ImageTk.PhotoImage(file="images/phoneBook_bg.jpg")
    window.bg_Img = tk.Label(image=window.bg).place(x=0, y=0, relwidth=1, relheight=1)

    s = ttk.Style()
    s.theme_use('default')
    s.configure("blue.Horizontal.TProgressbar", foreground='white', background='#066fd1', thickness = 17)

    #Banner
    phone_Word = tk.Label(text="PHONE", font=("Helvetica",50,"bold","italic"),fg="gray",bg="white")
    phone_Word.place(x = 50, y = 80)

    book_Word = tk.Label(text="BOOK", font=("Helvetica", 50, "bold", "italic"), fg="gray", bg="white")
    book_Word.place(x=350, y=160)

    #Progress bar effect
    progress = ttk.Progressbar(window, style = "blue.Horizontal.TProgressbar", orient=tk.HORIZONTAL, length=621, mode='determinate')
    progress.place(x = 0, y = 380)

    #Receive data's text
    revc_data_text = tk.Label(window, text="Receiving data......", font=("Goudy old style",15,"bold"),bg = "white")
    revc_data_text.place(x=0, y=350)

    #Loading
    progress.start(10)
    time.sleep(2)
    progress.stop()
    SignInOrUp(window)

def SelectRecord(phoneBook_tree):
    sub_window = tk.Toplevel()
    sub_window.geometry('400x450')
    sub_window.resizable(0,0)

    #Extract data from selected row
    selected = phoneBook_tree.focus()
    values = phoneBook_tree.item(selected, 'values')
    print(values)

    #Show in new window
    Frame = tk.Frame(sub_window, bg="white").place(x=0, y=0, width=500, height=500)
    Banner = tk.Frame(sub_window, bg="lightblue").place(x=0, y=0, width=500, height=150)
    Avatar_frame = tk.Frame(sub_window, bg="grey", highlightthickness=10).place(x=90, y = 40, width=170, height=170)

    #Get Avatar Base On ID
    c.sendall(bytes("SendAvatarWithID", "utf8"))
    c.sendall(bytes(values[0], "utf8")) #Send ID
    buf = recvImagesFromServer()

    Avatar = Image.open(io.BytesIO(buf))
    resized_Avatar = Avatar.resize((185, 170), Image.ANTIALIAS)
    sub_window.Avatar_obj = ImageTk.PhotoImage(resized_Avatar)
    #showAvatar = tk.Label(sub_window, image=sub_window.Avatar_obj).place(x=110, y=60)
    showAvatar = tk.Button(sub_window, image=sub_window.Avatar_obj,bd=0, command=lambda:Avatar.show()).place(x=110, y=60)

    def do_popup(event):
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    menu = tk.Menu(sub_window, tearoff=0)
    menu.add_command(label="Save As", command=lambda:[Avatar.save(filedialog.asksaveasfilename(initialdir="/C", title="Save Avatar")),Avatar.show()])

    sub_window.bind("<Button-3>", do_popup)
    #ID
    ID = tk.Label(sub_window, text="ID : "+values[0], font=("Helvetica","10","bold"), bg="white").place(x=70, y = 270)
    #Name
    Name = tk.Label(sub_window, text="Full Name : "+values[1]+' '+values[2],font=("Helvetica","10","bold")
                                                                                ,bg="white").place(x=70, y = 300)
    #Email
    Email = tk.Label(sub_window, text="Email : " + values[3], font=("Helvetica", "10", "bold"), bg="white").place(x=70, y=330)
    #phoneNumber
    phoneNum = tk.Label(sub_window, text="Phone Number : " + values[4], font=("Helvetica", "10", "bold"), bg="white").place(x=70, y=360)

def phoneBook_GUI(window, username):
    window.geometry('1000x550')

    Frame_Img = Image.open("images/phoneBook_bg_Frame.png")
    Frame_Img = Frame_Img.resize((1000, 200), Image.ANTIALIAS)  # resize the image
    global Top_Frame
    Top_Frame = ImageTk.PhotoImage(Frame_Img)
    setFrame = tk.Label(image=Top_Frame, borderwidth=0).place(x=0, y=0)

    Bottom_Frame = tk.Frame(bg="white").place(x=0, y = 200, width = 1000, height = 350)

    #Style Config
    style = ttk.Style()
    style.theme_use('default')
    style.configure("Treeview", bg= '#D3D3D3', fg= 'black', rowheight=40, fieldbg = '#D3D3D3')
    style.map('Treeview', background = [('selected', '#347083')])

    tree_Frame = tk.Frame(window).pack(pady=100)#.place(x = 0, y = 200, width = 1000, height= 400)

    #Create Scrollbar
    tree_scroll = tk.Scrollbar(tree_Frame, orient=tk.VERTICAL)
    tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    #Create Treeview
    phoneBook_tree = ttk.Treeview(tree_Frame, yscrollcommand=tree_scroll.set, selectmode="extended")
    phoneBook_tree.place(x = 0, y = 200, width = 751, height=350)

    #Configure Scrollbar
    tree_scroll.config(command = phoneBook_tree.yview)

    #Columns
    phoneBook_tree.config(column=('ID', 'First Name', 'Last Name', 'Email', 'Phone Number'))
    #Format the columns
    phoneBook_tree.column('#0', anchor=tk.CENTER, width=41)
    phoneBook_tree.column('#1', anchor=tk.CENTER, width=85)
    phoneBook_tree.column('#2', anchor=tk.CENTER, width=80)
    phoneBook_tree.column('#3', anchor=tk.CENTER, width=80)
    phoneBook_tree.column('#4', anchor=tk.CENTER, width=180)
    phoneBook_tree.column('#5', anchor=tk.CENTER, width=180)
    #Headings
    phoneBook_tree.heading('#1',text="ID", anchor=tk.CENTER)
    phoneBook_tree.heading('#2',text="First Name", anchor=tk.CENTER)
    phoneBook_tree.heading('#3',text="Last Name", anchor=tk.CENTER)
    phoneBook_tree.heading('#4',text="Email", anchor=tk.CENTER)
    phoneBook_tree.heading("#5",text="Phone Number", anchor=tk.CENTER)

    # Row tags effect
    phoneBook_tree.tag_configure('oddrow', background="white")
    phoneBook_tree.tag_configure('evenrow', background="lightblue")

    #Get The List After Login
    getPhoneBookList(window, phoneBook_tree)

    # Recieve Users Data To Show on GUI
    Avatar_Frame = tk.Frame(bg="white", highlightthickness=10).place(x=750, y=0, width=200, height=200)
    c.sendall(bytes("SendMyData", "utf8"))
    c.sendall(bytes(username,"utf8"))
    print(username)
    ID = c.recv(1024).decode("utf8")

    buf = recvImagesFromServer()
    Avatar = Image.open(io.BytesIO(buf))
    Avatar = Avatar.resize((150, 130), Image.ANTIALIAS)
    window.Avatar_obj = ImageTk.PhotoImage(Avatar)
    showAvatar = tk.Label(image=window.Avatar_obj).place(x=774, y=20)

    #ID = "20127459"
    showUsername = tk.Label(window,text=username,font=("Helvetica","11","bold"),fg="#347083",bg="white").place(x=775,y=150)
    showId = tk.Label(window,text='#'+ID,font=("Helvetica","9",'bold'),fg="black",bg="white").place(x=775,y=170)

    #Bind The Treeview - detect user select record
    phoneBook_tree.bind("<ButtonRelease-1>", lambda e:SelectRecord(phoneBook_tree))

    #Buttons
    #View
    view_button = tk.Button(window, text="VIEW LIST",font=('Helvetica', 10,'bold'), bd =0, fg="white", bg="#347083",
                     command=lambda: getPhoneBookList(window, phoneBook_tree),width=20, height=2).place(x=780, y = 300)
    #Edit Profile
    EditProfile_button = tk.Button(window, text="EDIT MY PROFILE", font=('Helvetica', 10, 'bold'), bd=0, fg="white",
                                                                    bg="#347083",width=20, height=2).place(x=780, y=350)
    #New Account
    createNewAcc_button = tk.Button(window, text="CREATE NEW ACCOUNT", font=('Helvetica', 10, 'bold'), bd=0, fg="white",
                                command=lambda: SignUp_GUI(window),bg="#347083",width=20, height=2).place(x=780, y=400)
    #LogOut
    logOut_btnImg = Image.open("images/LogOut_icon.png")
    logOut_btnImg = logOut_btnImg.resize((30, 30), Image.ANTIALIAS)  # resize the image
    window.logOut_btn = ImageTk.PhotoImage(logOut_btnImg)
    set_btn = tk.Button(image=window.logOut_btn, command=lambda: Login_GUI(window), bd=0, bg="white").place(x=895, y=155)

def WelcomeToApp(window):
    window.geometry('1000x600')
    window.bg = ImageTk.PhotoImage(file="images/Login_bg.jpg")
    window.bg_Img = tk.Label(image=window.bg).place(x=0, y=0, relwidth=1, relheight=1)

    Frame_login = tk.Frame(bg="white").place(x=330, y=100, width=350, height=400)

    # Login Title
    Login_Text = tk.Label(text="Login", font=("Poppins-Bold", 25, "bold"), fg="black", bg="white")
    Login_Text.place(x=460, y=110)

def Client_GUI():
    window.bg = ImageTk.PhotoImage(file="images/connect_img.jpg")
    window.bg_Img = tk.Label(image=window.bg).place(x=0, y=0, relwidth=1, relheight=1)

    inputIP = tk.StringVar()
    Enter_IP = tk.Entry(font=("times new roman", 15), bg="lightgray", textvariable=inputIP)
    Enter_IP.place(x=190, y=190, width=250)
    Enter_IP.insert(0,"Enter IP")

    button = tk.Button(text="Connect", fg='black',bg='purple',font = ("times new roman", 13,'bold')
            ,command= lambda:connect(inputIP, window), width = 8).place(x = 270, y = 216)

    window.mainloop()


def client():
    while True:
        HOST = input("Enter an IP address to connect:")
        '''HOST = "127.0.0.1" '''
        addr = (HOST, PORT)
        try:
            c.connect(addr)
            break
        except Exception:
            print("Connection fail!Invalid IP address or target actively refused.Try again")

    try:
        print("Connected to ",  str(addr))
        while True:
            data = c.recv(1024).decode("utf8")
            if data == "-1":
                print("Server:Exceeded number of times for login\nDisconnect from server in 5 seconds for security purpose")
                t = 5
                while t:
                    time.sleep(1)
                    print(t)
                    t -= 1
                print("")
                break

            print("Server:" + data)
            while True:
                msg = input("Client:")
                if msg != "":
                    break
                else:print("Please type something")
            c.sendall(bytes(msg, "utf8"))

            if msg == "quit":
                print("Server:" + str(c.recv(1024).decode("utf8")))
                break;
    except KeyboardInterrupt:
        c.close()
    except ConnectionResetError:
        print("Server:Oops!We regret to announce that our server was closed by host")
        print("Server:We will be back as soon as possible so keep it in track")
        print("Disconnected")
        c.close()
    finally:
        c.close()

######Client######
print("---------------------Client---------------------")
PORT = 65331
c = socket(AF_INET, SOCK_STREAM)

#Có GUI
#client()
#Không có GUI - Chưa hoàn thành
window = tk.Tk()
window.geometry('620x400')
window.title("Client")
window.resizable(0, 0)  # window lock(can't be resize() )

Client_GUI()
window.mainloop()