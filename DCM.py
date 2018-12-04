from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import time
from datetime import datetime
import serial.tools.list_ports      #for serial communication
import serial                       #for serial communication
import json     #for user data storage
import os       #for directory pathing
import base64   #for password hiding

class appDCM:
    #DCM version number ==========================
    versionNumber = "2.0"
    
    #image file and directory ====================
    imageDirectory = "./images"
    logoFile = "/MacFireball.png"
    connected = "/connected.png"
    disconnected = "/disconnected.png"

    #userdata file and directory =================
    userDirectory = "./user"
    userloginFile = "/userlogin.json"

    #program screen variables ====================
    parameterDictionary = {}
    defaultParameterDictionary = {}
    fieldDictionary = {}

    #serial communication ========================
    uartPort = {}
    port = False
    pacemakerID = b''
    pacemakerMode = b''
    
    echoIDStr = "\x16\x33" + "\x00"*38
    resetIDStr = "\x16\x35" + "\x00"*38
    echoParameterStr = "\x16\x22" + "\x00"*38
    
    def __init__(self):
        #pre-program check for necessary files and variables ==================
        self.checkUserDirectory() #check and fix user database, must be called before createLoginScreen()
        
        #create new window =====================================================================================================================
        self.root = Tk()
        self.root.title("SFWR 3K04 - DCM")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure((0, 2), weight=1)
        self.root.rowconfigure(1, weight=3)

        #create header and logo
        self.createHeaderScreen()
        self.createLogoScreen()
        
        #create login screen
        self.createLoginScreen()

        #mainloop() makes code stuck in a "while (True)" loop
        self.root.mainloop()

    #user database related methods =============================================================================================================
    def checkUserDirectory(self, defaultUsername=""): #check, set, and return default username
        self.jsonUserlogin = {}
        if not os.path.exists(self.userDirectory): #check if subdirectory exist
            print("make "+self.userDirectory+" subdirectory")
            os.mkdir(self.userDirectory)

        if os.path.isfile(self.userDirectory+self.userloginFile): #check if userlogin file exist
            with open(self.userDirectory+self.userloginFile, "r") as fileIn:
                try:
                    self.jsonUserlogin = json.load(fileIn) #try to load file data
                    print("able to read .json file")
                    if ("default" not in self.jsonUserlogin or not isinstance(self.jsonUserlogin["default"], str)):
                        self.jsonUserlogin["default"] = defaultUsername
                except: #file is corrupted or not in .json format
                    print("cannot load .json file")
                    self.jsonUserlogin["default"] = defaultUsername
        else:
            self.jsonUserlogin["default"] = defaultUsername
        with open(self.userDirectory+self.userloginFile, "w") as fileOut:
            json.dump(self.jsonUserlogin, fileOut) #set default username in .json file
        return self.jsonUserlogin["default"] #return default username

    #screen display related methods ============================================================================================================
    def checkRowValue(self, rowValue): #split window into 3 rows
        if not (rowValue=="top" or rowValue=="mid" or rowValue=="bot"):
            raise ValueError('<row> value must be either "top", "mid", or "bot"')
        else:
            if (rowValue=="top"):
                return 0
            if (rowValue=="bot"):
                return 2
            return 1 #return mid

    def checkScreenExist(self, screenName): #check if screen exist in dictionary
        try:
            return screenName in self.screenDictionary
        except: #if dictionary does not yet exist
            self.screenDictionary = {"top":None, "mid":None, "bot":None}
            return False

    def addScreen(self, screenName, frame):
        if not self.checkScreenExist(screenName): #check for screen dictionary
            self.screenDictionary[screenName] = frame

    def displayScreen(self, screenName, rowValue="mid"): #display screen on window
        if screenName in self.screenDictionary:
            self.checkRowValue(rowValue)
            if self.screenDictionary.get(rowValue) is not None: #check if row is occupied
                self.screenDictionary[rowValue].grid_forget()
            self.screenDictionary[rowValue] = self.screenDictionary[screenName]  #set new screen
            self.screenDictionary[rowValue].grid(row=self.checkRowValue(rowValue), column=0, sticky=W+E+N+S)
            self.rootWindowResize()
            return True
        else:
            print(screenName+" does not exist")
            return False

    def rootWindowResize(self): #resize window according to current displayed screens
        self.root.update()
        self.root.minsize(self.root.winfo_reqwidth(), self.root.winfo_reqheight())
        self.root.geometry('%dx%d' % (self.root.winfo_reqwidth(), self.root.winfo_reqheight()))
        self.root.resizable(1, 1)

    #styling related methods =================================================================================================================
    def createFont(self, name, fontName, size, weight="normal"):
        try:
            self.fontDictionary[name] = (fontName, size, weight)
        except: #if dictionary does not yet exist
            self.fontDictionary = {}
            self.fontDictionary[name] = (fontName, size, weight)

    def ttkCreateFont(self, name, fontName, size, weight="normal"):
        try:
            self.ttkStyle.configure(name, font=(fontName, size, weight))
        except: #if ttkStyle variable does not yet exist
            self.ttkStyle = ttk.Style()
            self.ttkStyle.configure(name, font=(fontName, size, weight))
            

    #login header screen =====================================================================================================================
    def createHeaderScreen(self):
        if self.checkScreenExist("headerScreen"):
            print("header screen already exist")
            self.displayScreen("headerScreen", "top")
            return False
        else:
            self.headerFrame = Frame(self.root, padx=20, pady=0)
            self.addScreen("headerScreen", self.headerFrame)

            self.headerSoftwareName = Label(self.headerFrame, text="Pacemaker Controller-Monitor")
            self.headerSoftwareName.grid(row=0, sticky=W)

            #display screen
            self.displayScreen("headerScreen", "top")
            print("header screen created successfully")
            return True

    #logo screen =============================================================================================================================
    def createLogoScreen(self):
        if self.checkScreenExist("logoScreen"):
            print("logo screen already exist")
            self.displayScreen("logoScreen", "bot")
            return False
        else:
            self.logoFrame = Frame(self.root, padx=0, pady=10)
            self.logoFrame.columnconfigure(0, weight=1)
            self.addScreen("logoScreen", self.logoFrame)

            if os.path.exists(self.imageDirectory): #if img directory exist
                self.MacEngLogoImg = PhotoImage(file=self.imageDirectory+self.logoFile).subsample(2, 2)
                self.MacEngLogoLabel = Label(self.logoFrame, image=self.MacEngLogoImg)
                self.MacEngLogoLabel.grid(row=0, pady=5)
            
            self.companyName = Label(self.logoFrame, text="Spontaneous Cardiac Arrest Ltd.")
            self.companyName.grid(row=1)

            #display screen
            self.displayScreen("logoScreen", "bot")
            print("logo screen created successfully")
            return True

    #login screen =============================================================================================================================
    def createLoginScreen(self):
        if self.checkScreenExist("loginScreen"):
            print("login screen already exist")
            self.displayScreen("loginScreen")
            return False
        else:
            self.loginFrame = Frame(self.root, padx=20, pady=10)
            self.loginFrame.columnconfigure((1, 2), weight=1)
            self.loginFrame.rowconfigure((0, 1, 3), weight=1)
            self.addScreen("loginScreen", self.loginFrame)

            #styling tk and ttk
            self.createFont("loginTitleFont", "TkDefaultFont", 30, "bold")
            self.createFont("loginFont", "TkDefaultFont", 12)
            self.ttkCreateFont("loginButton.TButton", "TkDefaultFont", 20, "bold")
            
            #create widget
            self.loginTitle = Label(self.loginFrame, text="Welcome Back", font=self.fontDictionary["loginTitleFont"], height=2)

            self.usernameLabel = Label(self.loginFrame, text="Username", font=self.fontDictionary["loginFont"])
            self.passwordLabel = Label(self.loginFrame, text="Password", font=self.fontDictionary["loginFont"])
            self.usernameEntry = ttk.Entry(self.loginFrame, font=self.fontDictionary["loginFont"])
            self.passwordEntry = ttk.Entry(self.loginFrame, font=self.fontDictionary["loginFont"], show="*")

            self.loginButton = ttk.Button(self.loginFrame, text="Login", style="loginButton.TButton", command=lambda:self.loginUser())
            self.rememberMeButton = ttk.Checkbutton(self.loginFrame, text="Remember Me")
            self.smallRegisterButton = ttk.Button(self.loginFrame, text="Register", command=lambda:self.createRegisterScreen())
            
            #display widget
            self.loginTitle.grid(row=0, columnspan=3, sticky=N)
                        
            self.usernameLabel.grid(row=1, sticky=E+S)
            self.passwordLabel.grid(row=2, sticky=E+N)
            self.usernameEntry.grid(row=1, column=1, columnspan=2, padx=5, pady=2, sticky=W+E+S)
            self.passwordEntry.grid(row=2, column=1, columnspan=2, padx=5, pady=2, sticky=W+E+N)

            self.loginButton.grid(row=3, columnspan=3, sticky=W+E+N+S, pady=10)
            self.rememberMeButton.grid(row=4, column=0, columnspan=2, sticky=W)
            self.smallRegisterButton.grid(row=4, column=1, columnspan=2, sticky=E)

            #assign variable to entry
            self.usernameStr = StringVar()
            self.passwordStr = StringVar()
            self.usernameEntry.configure(textvariable=self.usernameStr)
            self.passwordEntry.configure(textvariable=self.passwordStr)

            #check for Remember Me username
            self.usernameStr.set(self.getUserlogin("default"))
            if (self.usernameStr.get() == ""):
                self.setButtonState(self.rememberMeButton, '!selected')
            else:
                self.setButtonState(self.rememberMeButton)

            #display screen
            self.displayScreen("loginScreen")
            print("login screen created successfully")
            return True

    #userlogin related methods ================================================================================================================
    def passwordHiding(self, string):               
        if not isinstance(string, str):
            raise TypeError('<string> parameter must be type "str"')
        else: #hide plain-text password by using base64 encode
            return str(base64.b64encode(string.encode()))

    def loginUser(self):
        tempPassword = self.passwordHiding(self.passwordStr.get()) #temp value gets cleared when exit function
        self.passwordStr.set("") #clear password entry for login safety

        if (self.usernameStr.get() in self.jsonUserlogin and tempPassword == self.jsonUserlogin[self.usernameStr.get()]):
            self.currentUsername = self.usernameStr.get()#store current user
            
            if not (self.rememberMeButton.state() == ()): #if button is checked
                self.setUserlogin("default", self.usernameStr.get()) #remember username
            else:
                self.setUserlogin("default", "")
                self.usernameStr.set("") #clear username entry

            self.createProfileScreen() #log into program
            self.createProgramScreen() #log into program
            self.rootWindowResize()
        else:
            messagebox.showerror("Login Error", "Invalid username or password")

    def registerUser(self):
        if 11 <= len(self.jsonUserlogin):
            messagebox.showerror("Max users reached", "Can only register a maximum of 10 users")
        elif (self.registerUsernameStr.get() in self.jsonUserlogin or self.registerUsernameStr.get() == "default"):
            messagebox.showerror("Invalid username", "Username already exists")
        elif (len(self.registerUsernameStr.get()) < 3 or 16 < len(self.registerUsernameStr.get())):
            messagebox.showwarning("Invalid username", "Username must be 3 to 16 characters long")
        elif (len(self.registerPasswordStr.get()) < 3 or 32 < len(self.registerPasswordStr.get())):
            messagebox.showwarning("Invalid password", "Password must be 3 to 32 characters long")
        elif (self.registerPasswordStr.get() == self.registerUsernameStr.get()):
            messagebox.showwarning("Invalid password", "Password cannot be the same as username")
        elif not (self.registerPasswordStr.get() == self.registerPasswordReStr.get()):
            messagebox.showerror("Invalid password", "Retype Password does not match")
        else:
            self.setUserlogin(self.registerUsernameStr.get(), self.passwordHiding(self.registerPasswordStr.get()))
            self.usernameStr.set(self.registerUsernameStr.get())
            self.registerUsernameStr.set("")
            self.registerPasswordStr.set("")
            self.registerPasswordReStr.set("")
            messagebox.showinfo("Account created", "You can now login using that account")
    
    def getUserlogin(self, username):
        with open(self.userDirectory+self.userloginFile, "r") as fileIn:
            self.jsonUserlogin = json.load(fileIn)
        return self.jsonUserlogin[username]

    def setUserlogin(self, username, password):
        self.jsonUserlogin[username] = password
        with open(self.userDirectory+self.userloginFile, "w") as fileOut:
            json.dump(self.jsonUserlogin, fileOut) #write to .json file
    
    def setButtonState(self, button, state='selected'):
        if not ("alternate" in state):
            button.state(['!alternate'])
        button.state([state])

    # register screen =========================================================================================================================
    def createRegisterScreen(self):
        if self.checkScreenExist("registerScreen"):
            print("register screen already exist")
            self.displayScreen("registerScreen")
            return False
        else:
            self.registerFrame = Frame(self.root, padx=20, pady=10)
            self.registerFrame.columnconfigure((1, 2), weight=1)
            self.registerFrame.rowconfigure((0, 1, 4), weight=1)
            self.addScreen("registerScreen", self.registerFrame)

            #styling tk and ttk
            self.createFont("loginFont", "TkDefaultFont", 12)
            self.ttkCreateFont("loginButton.TButton", "TkDefaultFont", 20, "bold")
            self.createFont("loginTitleFont", "TkDefaultFont", 30, "bold")

            #create widget
            self.registerTitle = Label(self.registerFrame, text="Register", font=self.fontDictionary["loginTitleFont"], height=2)
            
            self.registerUsernameLabel = Label(self.registerFrame, text="New Username", font=self.fontDictionary["loginFont"])
            self.registerPasswordLabel = Label(self.registerFrame, text="New Password", font=self.fontDictionary["loginFont"])
            self.registerPasswordReLabel = Label(self.registerFrame, text="Retype Password", font=self.fontDictionary["loginFont"])
            
            self.registerUsernameEntry = ttk.Entry(self.registerFrame, font=self.fontDictionary["loginFont"])
            self.registerPasswordEntry = ttk.Entry(self.registerFrame, font=self.fontDictionary["loginFont"], show="*")
            self.registerPasswordReEntry = ttk.Entry(self.registerFrame, font=self.fontDictionary["loginFont"], show="*")

            self.registerButton = ttk.Button(self.registerFrame, text="Create Account", style="loginButton.TButton", command=lambda:self.registerUser())
            self.smallLoginLabel = Label(self.registerFrame, text="Already have an account?")
            self.smallLoginButton = ttk.Button(self.registerFrame, text="Login", command=lambda:self.createLoginScreen())
            
            #display widget
            self.registerTitle.grid(row=0, columnspan=3, sticky=N)
            
            self.registerUsernameLabel.grid(row=1, padx=5, sticky=E+S)
            self.registerPasswordLabel.grid(row=2, padx=5, sticky=E)
            self.registerPasswordReLabel.grid(row=3, padx=5, sticky=E+N)
            
            self.registerUsernameEntry.grid(row=1, column=1, columnspan=2, pady=2, sticky=W+E+S)
            self.registerPasswordEntry.grid(row=2, column=1, columnspan=2, pady=2, sticky=W+E)
            self.registerPasswordReEntry.grid(row=3, column=1, columnspan=2, pady=2, sticky=W+E+N)

            self.registerButton.grid(row=4, columnspan=3, sticky=W+E+N+S, pady=10)
            self.smallLoginLabel.grid(row=5, column=0, columnspan=2, sticky=W)
            self.smallLoginButton.grid(row=5, column=1, columnspan=2, sticky=E)

            #assign variable to entry
            self.registerUsernameStr = StringVar()
            self.registerPasswordStr = StringVar()
            self.registerPasswordReStr = StringVar()

            self.registerUsernameEntry.configure(textvariable=self.registerUsernameStr)
            self.registerPasswordEntry.configure(textvariable=self.registerPasswordStr)
            self.registerPasswordReEntry.configure(textvariable=self.registerPasswordReStr)

            #display screen
            self.displayScreen("registerScreen")
            print("register screen created successfully")
            return True

    #program screen ============================================================================================================================
    def createProgramScreen(self):
        if self.checkScreenExist("programScreen"):
            print("program screen already exist")
            self.displayScreen("programScreen")

            #display stored user data
            self.readUserData(self.currentUsername)
            return False
        else:
            self.programFrame = Frame(self.root, padx=20, pady=10)
            self.programFrame.columnconfigure(0, weight=1)
            self.addScreen("programScreen", self.programFrame)

            #styling tk and ttk
            self.createFont("programFont", "TkDefaultFont", 30, "bold")
            self.programTitle = Label(self.programFrame, text="Program Name Filler", font=self.fontDictionary["programFont"])
            self.programTitle.grid(row=0)

            #create notebook widget
            self.notebook = ttk.Notebook(self.programFrame)
            self.notebook.grid(row=1, column=0, padx=0, pady=0, sticky=W+E+N+S)

            #create notebook pages
            self.paceSettingFrame = Frame(self.notebook)#, bg="#fff")
            self.paceSettingFrame.columnconfigure((0, 1, 2), weight=1)
            self.notebook.add(self.paceSettingFrame, text="Pace Setting", padding=(10, 10))
            self.egramFrame = Frame(self.notebook)
            self.notebook.add(self.egramFrame, text="Electrogram", padding=(10, 10))
            self.aboutAppFrame = Frame(self.notebook)
            self.notebook.add(self.aboutAppFrame, text="Board Details", padding=(10, 10))

            #create pace setting notebook
            self.createPaceSettingNotebook()
            self.createEgram()              #display electrogram
            self.createBoardDetails()       #display board details
            
            #display screen
            self.displayScreen("programScreen")
            print("program screen created successfully")
            return True


    def createPaceSettingNotebook(self):
        #create combobox widget frame for Pacing Mode
        self.pacingModeFrame = Frame(self.paceSettingFrame)
        self.programModeLabel = Label(self.pacingModeFrame, text="Select Pacing Mode:", pady=10)#, bg="#fff")
        self.programModeLabel.grid(row=0, column=0, padx=13)
        self.programModeCombobox = ttk.Combobox(self.pacingModeFrame,state="readonly", width=6)
        self.programModeCombobox.grid(row=0, column=1)
        self.pacingModeFrame.grid(row=0, column=0)

        self.programModeCombobox['values'] = ('OFF', 'AAT', 'VVT', 'AOO', 'AAI', 'VOO', 'VVI', 'VDD', 'DOO', 'DDI', 'AOOR', 'AAIR', 'VOOR', 'VVIR', 'DOOR', 'DDIR')
        
        #parameters range
        self.parameterDictionary["Lower Rate Limit"] = list(range(30, 50, 5)) + list(range(50, 90, 1)) + list(range(90, 176, 5))
        self.parameterDictionary["Upper Rate Limit"] = list(range(50, 176, 5))
        self.parameterDictionary["Maximum Sensor Rate"] = list(range(50, 176, 5))
        self.parameterDictionary["Fixed AV Delay"] = list(range(70, 301, 10))
        self.parameterDictionary["Atrial Amplitude"] = list(range(5, 33)) + list(range(35, 51, 5))
        self.parameterDictionary["Atrial Pulse Width"] = [5] + list(range(10, 191, 10))
        self.parameterDictionary["Ventricular Amplitude"] = list(range(5, 33)) + list(range(35, 51, 5))
        self.parameterDictionary["Ventricular Pulse Width"] = [5] + list(range(10, 191, 10))
        self.parameterDictionary["Atrial Sensitivity"] = list(range(15, 33))
        self.parameterDictionary["Ventricular Sensitivity"] = list(range(15, 33))
        self.parameterDictionary["Atrial Refractory"] = list(range(50, 501, 10))
        self.parameterDictionary["Ventricular Refractory"] = list(range(50, 501, 10))
        self.parameterDictionary["Post VA Refractory"] = list(range(50, 501, 10))
        self.parameterDictionary["Activity Threshold"] = list(range(0, 8))
        self.parameterDictionary["Reaction Time"] = list(range(0, 51, 10))
        self.parameterDictionary["Response Factor"] = list(range(0, 17))
        self.parameterDictionary["Recovery Time"] = list(range(0, 7))

        self.defaultParameterDictionary["Lower Rate Limit"] = 60
        self.defaultParameterDictionary["Upper Rate Limit"] = 120
        self.defaultParameterDictionary["Maximum Sensor Rate"] = 120
        self.defaultParameterDictionary["Fixed AV Delay"] = 150
        self.defaultParameterDictionary["Atrial Amplitude"] = 35
        self.defaultParameterDictionary["Ventricular Amplitude"] = 45
        self.defaultParameterDictionary["Atrial Pulse Width"] = 100
        self.defaultParameterDictionary["Ventricular Pulse Width"] = 100
        self.defaultParameterDictionary["Atrial Sensitivity"] = 27
        self.defaultParameterDictionary["Ventricular Sensitivity"] = 27
        self.defaultParameterDictionary["Atrial Refractory"] = 100
        self.defaultParameterDictionary["Ventricular Refractory"] = 100
        self.defaultParameterDictionary["Post VA Refractory"] = 100
        self.defaultParameterDictionary["Activity Threshold"] = 1
        self.defaultParameterDictionary["Reaction Time"] = 1
        self.defaultParameterDictionary["Response Factor"] = 1
        self.defaultParameterDictionary["Recovery Time"] = 1
        
        #display all parameters
        rowGrid = 1
        columnGrid = 0
        for param in self.parameterDictionary:
            self.createField(param, self.parameterDictionary[param])
            self.fieldDictionary[param]['frame'].grid(row=rowGrid, column=columnGrid)
            rowGrid = rowGrid + 1
            if (rowGrid >= 7):
                rowGrid = 1
                columnGrid = columnGrid + 1

        #buttons
        self.resetButton = ttk.Button(self.paceSettingFrame, text="Reset", command=lambda:self.resetUserData())
        self.resetButton.grid(row=7, column=0, padx=5, sticky=W+E+N+S)
        self.confirmButton = ttk.Button(self.paceSettingFrame, text="Save", command=lambda:self.writeUserData(self.currentUsername))
        self.confirmButton.grid(row=7, column=1, padx=5, sticky=W+E)
        self.uploadButton = ttk.Button(self.paceSettingFrame, text="Upload")
        self.uploadButton.grid(row=7, column=2, padx=5, sticky=W+E)

        #display stored user data
        self.readUserData(self.currentUsername)

    #pace setting notebook ======================================================================================================================================
    def createField(self, string, array, extra=""):
        self.fieldDictionary[string] = {}
        self.fieldDictionary[string]['frame'] = Frame(self.paceSettingFrame)
        self.fieldDictionary[string]['label'] = Label(self.fieldDictionary[string]['frame'], width=18, text=string+extra)
        self.fieldDictionary[string]['variable'] = StringVar()
        self.fieldDictionary[string]['spinbox'] = Spinbox(self.fieldDictionary[string]['frame'], values=array, width=8, textvariable=self.fieldDictionary[string]['variable'])
        self.fieldDictionary[string]['label'].grid(row=0, column=0, padx=5, pady=5)
        self.fieldDictionary[string]['spinbox'].grid(row=0, column=1, padx=5, pady=5)

    def validCheck(self):
        errorMsg = ""
        for param in self.fieldDictionary:
            if not self.fieldDictionary[param]['variable'].get().isdigit():
                errorMsg = errorMsg + param + " value is not a number. Please try again.\n"
            else:
                intVar = int(self.fieldDictionary[param]['variable'].get())
                if not (self.parameterDictionary[param][0] <= intVar and intVar <= self.parameterDictionary[param][-1]):
                    errorMsg = errorMsg+param+" out of bound. Range from "+str(self.parameterDictionary[param][0])+" to "+str(self.parameterDictionary[param][-1])+"\n"
        if not (errorMsg == ""):
            messagebox.showerror("Value Error", errorMsg)
            return False
        return True

    def readUserData(self, username):
        self.userDataFile = "/"+username+".json"
        self.jsonUserData = {}
        try:
            with open(self.userDirectory+self.userDataFile, "r") as fileIn:
                self.jsonUserData = json.load(fileIn) #read user data

                self.programModeCombobox.set(self.jsonUserData["paceMode"])

                for param in self.fieldDictionary:
                    self.fieldDictionary[param]['variable'].set(self.jsonUserData[param])

                print("read user data successfully")
        except:
            print("user data is corrupted or does not yet exist")
            self.programModeCombobox.set("DOOR")
            for param in self.fieldDictionary:
                self.fieldDictionary[param]['variable'].set(self.defaultParameterDictionary[param])

    def writeUserData(self, username):
        if self.validCheck():
            self.jsonUserData = {} #reset json variable
            self.userDataFile = "/"+username+".json"
            with open(self.userDirectory+self.userDataFile, "w") as fileOut:
                self.jsonUserData["paceMode"] = self.programModeCombobox.get()

                for param in self.fieldDictionary:
                    self.jsonUserData[param] = self.fieldDictionary[param]['variable'].get()

                json.dump(self.jsonUserData, fileOut) #write to .json file
                print("write user data successfully")
        else:
            print("invalid data")
            
    def resetUserData(self):
        self.programModeCombobox.set("DOOR")
        for param in self.fieldDictionary:
            self.fieldDictionary[param]['variable'].set(self.defaultParameterDictionary[param])
        print("user data has been reset to default values")
        
#======================================================================================================================================        
    #serial communication ===============================================================================================================================
    def listValidComPort(self):
        portDescription = "UART"
        comPort = serial.tools.list_ports.grep(portDescription)
        self.uartPort = {}
        for p in comPort:
            self.uartPort[p.device] = p.description
        return bool(self.uartPort)
    
    def getValidPacemaker(self):
        for p in self.uartPort:
            try:
                self.port = serial.Serial(port=p, baudrate=115200)
                self.port.timeout = 1
                self.serialEchoID()
                self.pacemakerID = self.serialReadData()
                print(self.pacemakerID, type(self.pacemakerID))
                if str.encode("42069") in self.pacemakerID:
                    print(p, "is a valid pacemaker")
                    return True
                else:
                    print(p, "is not valid pacemaker")
            except:
                print(p, "is not a valid serial port")
        self.port = False
        return False
    
    def serialReadData(self):
        return self.port.read(40)

    def serialEchoID(self):
        try:
            echoIDByte = str.encode(echoIDStr)
            self.port.write(echoIDByte)
        except:
            echoIDStr = "\x16\x33" + "\x00"*38
            echoIDByte = str.encode(echoIDStr)
            port.write(echoIDByte)

    def serialEchoParameter(self):
        try:    
            echoParameterByte = str.encode(echoParameterStr)
            self.port.write(echoParameterByte)
        except:
            echoParameterStr = "\x16\x22" + "\x00"*38
            echoParameterByte = str.encode(echoParameterStr)
            port.write(echoParameterByte)
        
        

    
    #egram ==============================================================================================================================================
    pulseplot = False
    def change_state(self):
        if appDCM.pulseplot == True:
            appDCM.pulseplot = False
        else:
            appDCM.pulseplot = True

    style.use("ggplot")
    xar = [0, 0.1]
    yar = [0, 0]
    def createEgram(self):
        self.fig = plt.Figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.grid()
        self.line, = self.ax.plot(appDCM.xar, appDCM.yar)
        self.ax.set_ylim(-1, 1) 
        self.graph = FigureCanvasTkAgg(self.fig, master=self.egramFrame)
        self.graph.get_tk_widget().pack(side=BOTTOM, fill=X)

        self.stopstartButton = ttk.Button(self.egramFrame, text="Start/Stop", command=lambda:self.gui_handler())
        self.stopstartButton.pack(side=TOP)
        self.graph.draw()
    
    def refresh(self):
        if appDCM.pulseplot == True:
            appDCM.xar = np.append(appDCM.xar, appDCM.xar[-1]+0.1)
            appDCM.yar = np.append(appDCM.yar, np.sin(appDCM.xar[-1]))
            self.ax.set_xlim(appDCM.xar[-1]-10, appDCM.xar[-1])
            self.line.set_data(appDCM.xar,appDCM.yar)       
            self.graph.draw()
            self.root.after(10, self.refresh)

    def gui_handler(self):
        self.change_state()
        self.refresh()

    #board details ======================================================================================================================================
    def createBoardDetailsNotebook(self):
        self.DCM_version_label = Label(self.aboutAppFrame, width=20, text="DCM version: "+appDCM.versionNumber, font=self.fontDictionary["loginFont"], relief=RIDGE)
        self.TelemetryStatusFrame = Frame(self.aboutAppFrame, relief=GROOVE)
        self.TelemetryStatusFrame.pack(padx=30, pady=30, side=TOP)
        self.TelemetryStatusFrame.columnconfigure(0, weight=2)
        self.TelemetryStatusFrame.columnconfigure(1, weight=3)
        self.TelemetryStatusFrame.columnconfigure(2, weight=1)

        self.TelemetryStatusTitle = Label(self.TelemetryStatusFrame, text="Telemetry Status", font='Arial 18 bold')
        self.COM_Port_label = Label(self.TelemetryStatusFrame, text="COM Port:")
        self.Pacemaker_Connection_label = Label(self.TelemetryStatusFrame, text="Pacemaker:")
        self.Last_Program_Time_label = Label(self.TelemetryStatusFrame, text="Last Program Time:")
        self.Current_Pacing_Mode_label = Label(self.TelemetryStatusFrame, text="Current Pacing Mode:")

        self.comport_description = Label(self.TelemetryStatusFrame, text="No device was found.", fg='#f44336', justify=LEFT)
        self.pacemaker_description = Label(self.TelemetryStatusFrame, text="No pacemaker was detected.", fg='#f44336', justify=LEFT)
        self.lastProgramTime_description = Label(self.TelemetryStatusFrame, text="N/A", fg='#A0A0A0', justify=LEFT)
        self.currentPacingMode_description = Label(self.TelemetryStatusFrame, text="N/A", fg='#A0A0A0', justify=LEFT)

        if os.path.exists(self.imageDirectory): #if img directory exist
            self.connectedImg = PhotoImage(file=self.imageDirectory+self.connected)
            self.disconnectedImg = PhotoImage(file=self.imageDirectory+self.disconnected)
            self.comport_connectionImgLabel = Label(self.TelemetryStatusFrame, image=self.disconnectedImg)
            self.pacemaker_connectionImgLabel = Label(self.TelemetryStatusFrame, image=self.disconnectedImg)
        
        #display labels
        self.DCM_version_label.pack(pady=20)
        self.TelemetryStatusTitle.grid(row=0, columnspan=3, sticky=N)
        self.COM_Port_label.grid(row=1, column=1, pady=5)
        self.Pacemaker_Connection_label.grid(row=2, column=1, pady=5)
        self.Last_Program_Time_label.grid(row=3, column=1, pady=5)
        self.Current_Pacing_Mode_label.grid(row=4, column=1, pady=5)

        self.comport_description.grid(row=1, column=2, pady=5)
        self.pacemaker_description.grid(row=2, column=2, pady=5)
        self.lastProgramTime_description.grid(row=3, column=2, pady=5)
        self.currentPacingMode_description.grid(row=4, column=2, pady=5)

        self.comport_connectionImgLabel.grid(row=1, column=0, pady=5)
        self.pacemaker_connectionImgLabel.grid(row=2, column=0, pady=5)

##        self.refreshBoardInfo()

    def refreshBoardInfo(self):
        if self.listValidComPort():
            self.comport_description.config(text="UART device detected", fg='#4caf50')
            self.comport_connectionImgLabel.config(image=self.connectedImg)

        if self.getValidPacemaker():
            displayID = self.pacemakerID[5:30].decode("utf-8").rstrip('\0')
            print(displayID, type(displayID))
            self.pacemaker_description.config(text="Detected: " + displayID, fg='#4caf50')
            self.pacemaker_connectionImgLabel.config(image=self.connectedImg)

            displayTimeInt = int.from_bytes(self.pacemakerID[31:-2], 'little')
            displayTimeStr = datetime.fromtimestamp(displayTimeInt).strftime('%Y-%m-%d %H:%M:%S')
            self.lastProgramTime_description.config(text=displayTimeStr, fg='#4caf50')

            #get pacemaker parameters
            self.serialEchoParameter()
            self.pacemakerMode = serialReadData()
            
##        if something:
##            self.currentPacingMode_description.config(text="(This will state the current pacing mode)", fg='#4caf50')



    #profile screen ===============================================================================================================================
    def createProfileScreen(self):
        if self.checkScreenExist("profileScreen"):
            print("profile screen already exist")
            self.displayScreen("profileScreen", "top")
            return False
        else:
            self.profileFrame = Frame(self.root, padx=20, pady=10)
            self.profileFrame.columnconfigure(0, weight=1)
            self.addScreen("profileScreen", self.profileFrame)

            self.profileSoftwareName = Label(self.profileFrame, text="Pacemaker Controller-Monitor")
            self.profileSoftwareName.grid(row=0, sticky=W)

            self.profileButton = ttk.Button(self.profileFrame, text="Logout", command=lambda:self.logoutUser())
            self.profileButton.grid(row=0, sticky=E)

            #display screen
            self.displayScreen("profileScreen", "top")
            print("profile screen created successfully")
            return True

    def logoutUser(self):
        self.root.config(menu="")
        self.createLoginScreen()
        self.createHeaderScreen()



            
login = appDCM()
