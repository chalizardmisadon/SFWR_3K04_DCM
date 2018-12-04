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

    #serial communication ========================
    uartPort = {}
    port = False
    pacemakerID = b''
    
    echoIDStr = "\x16\x33" + "\x00"*38
    resetIDStr = "\x16\x35" + "\x00"*38
    
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
            self.createEgram()  #display electrogram
            self.boardDetails() #display board details
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
            self.programFrame = Frame(self.root, padx=20, pady=10, relief=RIDGE)
            self.programFrame.columnconfigure(0, weight=1)
            self.addScreen("programScreen", self.programFrame)

            #styling tk and ttk
            self.createFont("programFont", "TkDefaultFont", 24, "bold")
            self.programTitle = Label(self.programFrame, text="Pacemaker Controller", font=self.fontDictionary["programFont"])
            self.programTitle.grid(row=0)

            #create notebook widget
            self.notebook = ttk.Notebook(self.programFrame)
            self.notebook.grid(row=1, column=0, padx=0, pady=0, sticky=W+E+N+S)

            #create notebook pages
            self.paceSettingFrame = Frame(self.notebook)#, bg="#fff")
            self.paceSettingFrame.columnconfigure((1, 3, 5), weight=1)
            self.notebook.add(self.paceSettingFrame, text="Pace Setting", padding=(10, 10))
            self.egramFrame = Frame(self.notebook)
            self.notebook.add(self.egramFrame, text="Electrogram", padding=(10, 10))
            self.aboutAppFrame = Frame(self.notebook)
            self.notebook.add(self.aboutAppFrame, text="Board Details", padding=(10, 10))

            #create combobox widget frame for Pacing Mode
            self.pacingModeFrame = Frame(self.paceSettingFrame)
            self.programModeLabel = Label(self.pacingModeFrame, text="Select Pacing Mode:", pady=10)#, bg="#fff")
            self.programModeLabel.grid(row=0, column=0, padx=5)
            self.programModeCombobox = ttk.Combobox(self.pacingModeFrame,state="readonly", width=6)
            self.programModeCombobox.grid(row=0, column=1)
            self.programModeCombobox['values'] = ('OFF', 'AAT', 'VVT', 'AOO', 'AAI', 'VOO', 'VVI', 'VDD', 'DOO', 'DDI', 'DDD',
                                                  'AOOR', 'AAIR', 'VOOR', 'VVIR', 'VDDR', 'DOOR', 'DDIR', 'DDDR')

            #create frame for each parameter in parameter frame
            self.lowerRateLimitFrame = Frame(self.paceSettingFrame)
            self.upperRateLimitFrame = Frame(self.paceSettingFrame)
            self.maximumSensorRateFrame = Frame(self.paceSettingFrame)
            self.fixedAVDelayFrame = Frame(self.paceSettingFrame)
            self.dynamicAVDelayFrame = Frame(self.paceSettingFrame)
            self.minimumDynamicAVDelayFrame = Frame(self.paceSettingFrame)
            self.sensedAVDelayOffsetFame = Frame(self.paceSettingFrame)
            self.atrialAmplitudeFrame = Frame(self.paceSettingFrame)
            self.ventricularAmplitudeFrame = Frame(self.paceSettingFrame)
            self.atrialAmplitudeUnregulatedFrame = Frame(self.paceSettingFrame)
            self.ventricularAmplitudeUnregulatedFrame = Frame(self.paceSettingFrame)
            self.atrialPulseWidthFrame = Frame(self.paceSettingFrame)
            self.ventricularPulseWidthFrame = Frame(self.paceSettingFrame)
            self.atrialSensitivityFrame = Frame(self.paceSettingFrame)
            self.ventricularSensitivityFrame = Frame(self.paceSettingFrame)
            self.VRPFrame = Frame(self.paceSettingFrame)
            self.ARPFrame = Frame(self.paceSettingFrame)
            self.PVARPFrame = Frame(self.paceSettingFrame)
            self.PVARPExtensionFrame = Frame(self.paceSettingFrame)
            self.hysteresisFrame = Frame(self.paceSettingFrame)
            self.rateSmoothingFrame = Frame(self.paceSettingFrame)
            self.ATRDurationFrame = Frame(self.paceSettingFrame)
            self.ATRFallbackModeFrame = Frame(self.paceSettingFrame)
            self.ATRFallbackTimeFrame = Frame(self.paceSettingFrame)
            self.ventricularBlankingFrame = Frame(self.paceSettingFrame)
            self.activityThresholdFrame = Frame(self.paceSettingFrame)
            self.reactionTimeFrame = Frame(self.paceSettingFrame)
            self.responseFactorFrame = Frame(self.paceSettingFrame)
            self.recoveryTimeFrame = Frame(self.paceSettingFrame)

            #create label widget
            self.label01 = Label(self.lowerRateLimitFrame, width=18, text="Lower Rate Limit")
            self.label02 = Label(self.upperRateLimitFrame, width=18, text="Upper Rate Limit")
            self.label03 = Label(self.maximumSensorRateFrame, width=18, text="Maximum Sensor Rate")
            self.label04 = Label(self.fixedAVDelayFrame, width=18, text="Fixed AV Delay")
            self.label05 = Label(self.dynamicAVDelayFrame, width=18, text="Dynamic AV Delay")
            self.label06 = Label(self.minimumDynamicAVDelayFrame, width=18, text="Minimum Dynamic\n AV Delay")
            self.label07 = Label(self.sensedAVDelayOffsetFame, width=18, text="Sensed AV Delay Offset")
            self.label08 = Label(self.atrialAmplitudeFrame, width=18, text="Atrial Amplitude")
            self.label09 = Label(self.ventricularAmplitudeFrame, width=18, text="Ventricular Amplitude")
            self.label10 = Label(self.atrialAmplitudeUnregulatedFrame, width=18, text="Atrial Amplitude\n Unregulated")
            self.label11 = Label(self.ventricularAmplitudeUnregulatedFrame, width=18, text="Ventricular Amplitude\n Unregulated")
            self.label12 = Label(self.atrialPulseWidthFrame, width=18, text="Atrial Pulse Width")
            self.label13 = Label(self.ventricularPulseWidthFrame, width=18, text="Ventricular Pulse Width")
            self.label14 = Label(self.atrialSensitivityFrame, width=18, text="Atrial Sensitivity")
            self.label15 = Label(self.ventricularSensitivityFrame, width=18, text="Ventricular Sensitivity")
            self.label16 = Label(self.VRPFrame, width=18, text="VRP")
            self.label17 = Label(self.ARPFrame, width=18, text="ARP")
            self.label18 = Label(self.PVARPFrame, width=18, text="PVARP")
            self.label19 = Label(self.PVARPExtensionFrame, width=18, text="PVARP Extension")
            self.label20 = Label(self.hysteresisFrame, width=18, text="Hysteresis")
            self.label21 = Label(self.rateSmoothingFrame, width=18, text="Rate Smoothing")
            self.label22 = Label(self.ATRDurationFrame, width=18, text="ATR Duration")
            self.label23 = Label(self.ATRFallbackModeFrame, width=18, text="ATR Fallback Mode")
            self.label24 = Label(self.ATRFallbackTimeFrame, width=18, text="ATR Fallback Time")
            self.label25 = Label(self.ventricularBlankingFrame,width=18, text="Ventricular Blanking")
            self.label26 = Label(self.activityThresholdFrame, width=18, text="Activity Threshold")
            self.label27 = Label(self.reactionTimeFrame, width=18, text="Reaction Time")
            self.label28 = Label(self.responseFactorFrame, width=18, text="Response Factor")
            self.label29 = Label(self.recoveryTimeFrame, width=18, text="Recovery Time")

            #create entry variable
            self.entry01Str = StringVar()
            self.entry02Str = StringVar()
            self.entry03Str = StringVar()
            self.entry04Str = StringVar()
            self.entry05Str = StringVar()
            self.entry06Str = StringVar()
            self.entry07Str = StringVar()
            self.entry08Str = StringVar()
            self.entry09Str = StringVar()
            self.entry10Str = StringVar()
            self.entry11Str = StringVar()
            self.entry12Str = StringVar()
            self.entry13Str = StringVar()
            self.entry14Str = StringVar()
            self.entry15Str = StringVar()
            self.entry16Str = StringVar()
            self.entry17Str = StringVar()
            self.entry18Str = StringVar()
            self.entry19Str = StringVar()
            self.entry20Str = StringVar()
            self.entry21Str = StringVar()
            self.entry22Str = StringVar()
            self.entry23Str = StringVar()
            self.entry24Str = StringVar()
            self.entry25Str = StringVar()
            self.entry26Str = StringVar()
            self.entry27Str = StringVar()
            self.entry28Str = StringVar()
            self.entry29Str = StringVar()

            #create entry widget
            self.entry01 = Spinbox(self.lowerRateLimitFrame, state="readonly", values=(list(range(30,51,5))+list(range(51,90,1))+list(range(90,176,5))), width=8, textvariable=self.entry01Str)
            self.entry02 = Spinbox(self.upperRateLimitFrame,state="readonly", values=list(range(50,176,5)), width=8, textvariable=self.entry02Str)
            self.entry03 = Spinbox(self.maximumSensorRateFrame,state="readonly", values=list(range(50,176,5)), width=8, textvariable=self.entry03Str)
            self.entry04 = Spinbox(self.fixedAVDelayFrame,state="readonly", values=list(range(70,301,10)), width=8, textvariable=self.entry04Str)
            self.entry05 = Spinbox(self.dynamicAVDelayFrame,state="readonly", values=["OFF", "ON"], width=8, textvariable=self.entry05Str)
            self.entry06 = Spinbox(self.minimumDynamicAVDelayFrame,state="readonly", values=list(range(30,101,10)), width=8, textvariable=self.entry06Str)
            self.entry07 = Spinbox(self.sensedAVDelayOffsetFame,state="readonly", values=["OFF"] + list(np.arange(-10,-101,-10)), width=8, textvariable=self.entry07Str)
            self.entry08 = Spinbox(self.atrialAmplitudeFrame,state="readonly", values=["OFF"] + list(np.arange(0.5, 3.3, 0.1)) + list(np.arange(3.5, 7.5, 0.5)), width=8, textvariable=self.entry08Str)
            self.entry09 = Spinbox(self.ventricularAmplitudeFrame,state="readonly", values=["OFF"] + list(np.arange(0.5, 3.3, 0.1)) + list(np.arange(3.5, 7.5, 0.5)), width=8, textvariable=self.entry09Str)
            self.entry10 = Spinbox(self.atrialAmplitudeUnregulatedFrame,state="readonly", values=["OFF", 1.25, 2.5, 3.75, 5.0], width=8, textvariable=self.entry10Str)
            self.entry11 = Spinbox(self.ventricularAmplitudeUnregulatedFrame,state="readonly", values=["OFF", 1.25, 2.5, 3.75, 5.0], width=8, textvariable=self.entry11Str)
            self.entry12 = Spinbox(self.atrialPulseWidthFrame, state="readonly", values=[0.05] + list(np.arange(0.1, 2.0, 0.1)), width=8, textvariable=self.entry12Str)
            self.entry13 = Spinbox(self.ventricularPulseWidthFrame, state="readonly", values=[0.05] + list(np.arange(0.1, 2.0, 0.1)), width=8, textvariable=self.entry13Str)
            self.entry14 = Spinbox(self.atrialSensitivityFrame, state="readonly", values=[0.25, 0.5, 0.75] + list(np.arange(1.0, 10.5, 0.5)), width=8, textvariable=self.entry14Str)
            self.entry15 = Spinbox(self.ventricularSensitivityFrame, state="readonly", values=[0.25, 0.5, 0.75] + list(np.arange(1.0, 10.5, 0.5)), width=8, textvariable=self.entry15Str)
            self.entry16 = Spinbox(self.VRPFrame, state="readonly", values=list(range(150,510,10)), width=8, textvariable=self.entry16Str)
            self.entry17 = Spinbox(self.ARPFrame, state="readonly", values=list(range(150,510,10)), width=8, textvariable=self.entry17Str)
            self.entry18 = Spinbox(self.PVARPFrame, state="readonly", values=list(range(150,510,10)), width=8, textvariable=self.entry18Str)
            self.entry19 = Spinbox(self.PVARPExtensionFrame, state="readonly", values=["OFF"] + list(range(50,450,50)), width=8, textvariable=self.entry19Str)
            self.entry20 = Spinbox(self.hysteresisFrame, state="readonly", values=["OFF"] + list(range(30,51,5))+list(range(51,90,1))+list(range(90,176,5)), width=8, textvariable=self.entry20Str)
            self.entry21 = Spinbox(self.rateSmoothingFrame, state="readonly", values=["OFF"] + list(range(3,24,3)) + [25], width=8, textvariable=self.entry21Str)
            self.entry22 = Spinbox(self.ATRDurationFrame, state="readonly", values=["OFF", "ON"], width=8, textvariable=self.entry22Str)
            self.entry23 = Spinbox(self.ATRFallbackModeFrame, state="readonly", values=[10] + list(range(20,100,20)) + list(range(100,2100,100)),width=8, textvariable=self.entry23Str)
            self.entry24 = Spinbox(self.ATRFallbackTimeFrame, state="readonly", values=list(range(1,6,1)), width=8, textvariable=self.entry24Str)
            self.entry25 = Spinbox(self.ventricularBlankingFrame, state="readonly", values=[30,40,50,60], width=8, textvariable=self.entry25Str)
            self.entry26 = Spinbox(self.activityThresholdFrame, state="readonly", values=["V-Low", "Low", "Med-Low", "Med", "Med-High", "High", "V-High"],width=8, textvariable=self.entry26Str)
            self.entry27 = Spinbox(self.reactionTimeFrame, state="readonly", value=list(range(10,60,10)), width=8, textvariable=self.entry27Str)
            self.entry28 = Spinbox(self.responseFactorFrame, state="readonly", value=list(range(1,17,1)), width=8, textvariable=self.entry28Str)
            self.entry29 = Spinbox(self.recoveryTimeFrame, state="readonly", value=list(range(2,17,1)), width=8, textvariable=self.entry29Str)
            
            #display parameter widget
            self.label01.grid(row=0, column=0, padx=5, pady=5, sticky=E)
            self.label02.grid(row=0, column=0, padx=5, pady=5, sticky=E)
            self.label03.grid(row=0, column=0, padx=5, pady=5, sticky=E)
            self.label04.grid(row=0, column=0, padx=5, pady=5, sticky=E)
            self.label05.grid(row=0, column=0, padx=5, pady=5, sticky=E)
            self.label06.grid(row=0, column=0, padx=5, pady=5, sticky=E)
            self.label07.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            self.label08.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            self.label09.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            self.label10.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            self.label11.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            self.label12.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            self.label13.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            self.label14.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            self.label15.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            self.label16.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            self.label17.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            self.label18.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            self.label19.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            self.label20.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            self.label21.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            self.label22.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            self.label23.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            self.label24.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            self.label25.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            self.label26.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            self.label27.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            self.label28.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            self.label29.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            
            self.entry01.grid(row=0, column=1, sticky=E)
            self.entry02.grid(row=0, column=1, sticky=E)
            self.entry03.grid(row=0, column=1, sticky=E)
            self.entry04.grid(row=0, column=1, sticky=E)
            self.entry05.grid(row=0, column=1, sticky=E)
            self.entry06.grid(row=0, column=1, sticky=E)
            self.entry07.grid(row=0, column=1, sticky=E)
            self.entry08.grid(row=0, column=1, sticky=E)
            self.entry09.grid(row=0, column=1, sticky=E)
            self.entry10.grid(row=0, column=1, sticky=E)
            self.entry11.grid(row=0, column=1, sticky=E)
            self.entry12.grid(row=0, column=1, sticky=E)
            self.entry13.grid(row=0, column=1, sticky=E)
            self.entry14.grid(row=0, column=1, sticky=E)
            self.entry15.grid(row=0, column=1, sticky=E)
            self.entry16.grid(row=0, column=1, sticky=E)
            self.entry17.grid(row=0, column=1, sticky=E)
            self.entry18.grid(row=0, column=1, sticky=E)
            self.entry19.grid(row=0, column=1, sticky=E)
            self.entry20.grid(row=0, column=1, sticky=E)
            self.entry21.grid(row=0, column=1, sticky=E)
            self.entry22.grid(row=0, column=1, sticky=E)
            self.entry23.grid(row=0, column=1, sticky=E)
            self.entry24.grid(row=0, column=1, sticky=E)
            self.entry25.grid(row=0, column=1, sticky=E)
            self.entry26.grid(row=0, column=1, sticky=E)
            self.entry27.grid(row=0, column=1, sticky=E)
            self.entry28.grid(row=0, column=1, sticky=E)
            self.entry29.grid(row=0, column=1, sticky=E)

            #create frame for each parameter in parameter frame
            self.pacingModeFrame.grid(row=0, column=0, sticky=N)
            self.lowerRateLimitFrame.grid(row=1, column=0)
            self.upperRateLimitFrame.grid(row=2, column=0)
            self.maximumSensorRateFrame.grid(row=3, column=0)
            self.fixedAVDelayFrame.grid(row=4, column=0)
            self.dynamicAVDelayFrame.grid(row=5, column=0)
            self.minimumDynamicAVDelayFrame.grid(row=6, column=0)
            self.sensedAVDelayOffsetFame.grid(row=7, column=0)
            self.atrialAmplitudeFrame.grid(row=8, column=0)
            self.ventricularAmplitudeFrame.grid(row=9, column=0)
            self.atrialAmplitudeUnregulatedFrame.grid(row=0, column=1)
            self.ventricularAmplitudeUnregulatedFrame.grid(row=1, column=1)
            self.atrialPulseWidthFrame.grid(row=2, column=1)
            self.ventricularPulseWidthFrame.grid(row=3, column=1)
            self.atrialSensitivityFrame.grid(row=4, column=1)
            self.ventricularSensitivityFrame.grid(row=5, column=1)
            self.VRPFrame.grid(row=6, column=1)
            self.ARPFrame.grid(row=7, column=1)
            self.PVARPFrame.grid(row=8, column=1)
            self.PVARPExtensionFrame.grid(row=9, column=1)
            self.hysteresisFrame.grid(row=0, column=2)
            self.rateSmoothingFrame.grid(row=1, column=2)
            self.ATRDurationFrame.grid(row=2, column=2)
            self.ATRFallbackModeFrame.grid(row=3, column=2)
            self.ATRFallbackTimeFrame.grid(row=4, column=2)
            self.ventricularBlankingFrame.grid(row=5, column=2)
            self.activityThresholdFrame.grid(row=6, column=2)
            self.reactionTimeFrame.grid(row=7, column=2)
            self.responseFactorFrame.grid(row=8, column=2)
            self.recoveryTimeFrame.grid(row=9, column=2)

            #buttons
            self.resetButton = ttk.Button(self.paceSettingFrame, text="Reset", command=lambda:self.resetUserData(self.currentUsername))
            self.resetButton.grid(row=10, column=0, padx=5, sticky=W+E)
            self.confirmButton = ttk.Button(self.paceSettingFrame, text="Save", command=lambda:self.writeUserData(self.currentUsername))
            self.confirmButton.grid(row=10, column=1, padx=5, sticky=W+E)
            self.uploadButton = ttk.Button(self.paceSettingFrame, text="Upload")
            self.uploadButton.grid(row=10, column=2, padx=5, sticky=W+E)

            #display stored user data
            self.readUserData(self.currentUsername)
            
            #display screen
            self.displayScreen("programScreen")
            print("program screen created successfully")
            return True
        
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
            self.port = serial.Serial(port=p, baudrate=115200)
            self.port.timeout = 1
            self.serialEchoID(self.port)
            self.pacemakerID = self.serialReadData(self.port)
##            print(self.pacemakerID, type(self.pacemakerID))
            if str.encode("42069") in self.pacemakerID:
                print(p, "is a valid pacemaker")
                return True
            else:
                print(p, "is not valid pacemaker")
        return False

    def serialEchoID(self, port):
        try:
            echoIDByte = str.encode(echoIDStr)
            port.write(echoIDByte)
        except:
            echoIDStr = "\x16\x33" + "\x00"*38
            echoIDByte = str.encode(echoIDStr)
            port.write(echoIDByte)

    def serialReadData(self, port):
        return port.read(40)

    
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
    def boardDetails(self):
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

        self.refreshBoardInfo()

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
##        if something:
##            self.currentPacingMode_description.config(text="(This will state the current pacing mode)", fg='#4caf50')



    #display setting
    def displaySetting(self):
        print("\ndisplay value ==============================")
        print(self.label01.cget("text"), self.entry01Str.get())
        print(self.label02.cget("text"), self.entry02Str.get())
        print(self.label03.cget("text"), self.entry03Str.get())
        print(self.label04.cget("text"), self.entry04Str.get())
        print(self.label05.cget("text"), self.entry05Str.get())
        print(self.label06.cget("text"), self.entry06Str.get())
        print(self.label07.cget("text"), self.entry07Str.get())
        print(self.label08.cget("text"), self.entry08Str.get())
        print(self.label09.cget("text"), self.entry09Str.get())
        print(self.label10.cget("text"), self.entry10Str.get())
        print(self.label11.cget("text"), self.entry11Str.get())
        print(self.label12.cget("text"), self.entry12Str.get())
        print(self.label13.cget("text"), self.entry13Str.get())
        print(self.label14.cget("text"), self.entry14Str.get())
        print(self.label15.cget("text"), self.entry15Str.get())
        print(self.label16.cget("text"), self.entry16Str.get())
        print(self.label17.cget("text"), self.entry17Str.get())
        print(self.label18.cget("text"), self.entry18Str.get())
        print(self.label19.cget("text"), self.entry19Str.get())
        print(self.label20.cget("text"), self.entry20Str.get())
        print(self.label21.cget("text"), self.entry21Str.get())
        print(self.label22.cget("text"), self.entry22Str.get())
        print(self.label23.cget("text"), self.entry23Str.get())
        print(self.label24.cget("text"), self.entry24Str.get())
        print(self.label25.cget("text"), self.entry25Str.get())
        print(self.label26.cget("text"), self.entry26Str.get())
        print(self.label27.cget("text"), self.entry27Str.get())
        print(self.label28.cget("text"), self.entry28Str.get())
        print(self.label29.cget("text"), self.entry29Str.get())
        print("============================================\n")

    def readUserData(self, username):
        self.userDataFile = "/"+username+".json"
        self.jsonUserData = {}
        try:
            with open(self.userDirectory+self.userDataFile, "r") as fileIn:
                self.jsonUserData = json.load(fileIn) #read user data

                self.programModeCombobox.set(self.jsonUserData["paceMode"])
                self.entry01Str.set(self.jsonUserData["entry01"])
                self.entry02Str.set(self.jsonUserData["entry02"])
                self.entry03Str.set(self.jsonUserData["entry03"])
                self.entry04Str.set(self.jsonUserData["entry04"])
                self.entry05Str.set(self.jsonUserData["entry05"])
                self.entry06Str.set(self.jsonUserData["entry06"])
                self.entry07Str.set(self.jsonUserData["entry07"])
                self.entry08Str.set(self.jsonUserData["entry08"])
                self.entry09Str.set(self.jsonUserData["entry09"])
                self.entry10Str.set(self.jsonUserData["entry10"])
                self.entry11Str.set(self.jsonUserData["entry11"])
                self.entry12Str.set(self.jsonUserData["entry12"])
                self.entry13Str.set(self.jsonUserData["entry13"])
                self.entry14Str.set(self.jsonUserData["entry14"])
                self.entry15Str.set(self.jsonUserData["entry15"])
                self.entry16Str.set(self.jsonUserData["entry16"])
                self.entry17Str.set(self.jsonUserData["entry17"])
                self.entry18Str.set(self.jsonUserData["entry18"])
                self.entry19Str.set(self.jsonUserData["entry19"])
                self.entry20Str.set(self.jsonUserData["entry20"])
                self.entry21Str.set(self.jsonUserData["entry21"])
                self.entry22Str.set(self.jsonUserData["entry22"])
                self.entry23Str.set(self.jsonUserData["entry23"])
                self.entry24Str.set(self.jsonUserData["entry24"])
                self.entry25Str.set(self.jsonUserData["entry25"])
                self.entry26Str.set(self.jsonUserData["entry26"])
                self.entry27Str.set(self.jsonUserData["entry27"])
                self.entry28Str.set(self.jsonUserData["entry28"])
                self.entry29Str.set(self.jsonUserData["entry29"])

                print("read user data successfully")
        except:
            self.programModeCombobox.set("DDD")
            self.entry01Str.set("60")
            self.entry02Str.set("120")
            self.entry03Str.set("120")
            self.entry04Str.set("150")
            self.entry05Str.set("OFF")
            self.entry06Str.set("50")
            self.entry07Str.set("OFF")
            self.entry08Str.set("3.5")
            self.entry09Str.set("3.5")
            self.entry10Str.set("3.75")
            self.entry11Str.set("3.75")
            self.entry12Str.set("0.4")
            self.entry13Str.set("0.4")
            self.entry14Str.set("0.75")
            self.entry15Str.set("2.5")
            self.entry16Str.set("320")
            self.entry17Str.set("250")
            self.entry18Str.set("250")
            self.entry19Str.set("OFF")
            self.entry20Str.set("OFF")
            self.entry21Str.set("OFF")
            self.entry22Str.set("OFF")
            self.entry23Str.set("20")
            self.entry24Str.set("1")
            self.entry25Str.set("40")
            self.entry26Str.set("Med")
            self.entry27Str.set("30")
            self.entry28Str.set("8")
            self.entry29Str.set("5")
            print("user data is corrupted or does not yet exist")

    def writeUserData(self, username):
        self.displaySetting()
        self.jsonUserData = {} #reset json variable

        self.userDataFile = "/"+username+".json"
        with open(self.userDirectory+self.userDataFile, "w") as fileOut:
            self.jsonUserData["paceMode"] = self.programModeCombobox.get()
            self.jsonUserData["entry01"] = self.entry01Str.get()
            self.jsonUserData["entry02"] = self.entry02Str.get()
            self.jsonUserData["entry03"] = self.entry03Str.get()
            self.jsonUserData["entry04"] = self.entry04Str.get()
            self.jsonUserData["entry05"] = self.entry05Str.get()
            self.jsonUserData["entry06"] = self.entry06Str.get()
            self.jsonUserData["entry07"] = self.entry07Str.get()
            self.jsonUserData["entry08"] = self.entry08Str.get()
            self.jsonUserData["entry09"] = self.entry09Str.get()
            self.jsonUserData["entry10"] = self.entry10Str.get()
            self.jsonUserData["entry11"] = self.entry11Str.get()
            self.jsonUserData["entry12"] = self.entry12Str.get()
            self.jsonUserData["entry13"] = self.entry13Str.get()
            self.jsonUserData["entry14"] = self.entry14Str.get()
            self.jsonUserData["entry15"] = self.entry15Str.get()
            self.jsonUserData["entry16"] = self.entry16Str.get()
            self.jsonUserData["entry17"] = self.entry17Str.get()
            self.jsonUserData["entry18"] = self.entry18Str.get()
            self.jsonUserData["entry19"] = self.entry19Str.get()
            self.jsonUserData["entry20"] = self.entry20Str.get()
            self.jsonUserData["entry21"] = self.entry21Str.get()
            self.jsonUserData["entry22"] = self.entry22Str.get()
            self.jsonUserData["entry23"] = self.entry23Str.get()
            self.jsonUserData["entry24"] = self.entry24Str.get()
            self.jsonUserData["entry25"] = self.entry25Str.get()
            self.jsonUserData["entry26"] = self.entry26Str.get()
            self.jsonUserData["entry27"] = self.entry27Str.get()
            self.jsonUserData["entry28"] = self.entry28Str.get()
            self.jsonUserData["entry29"] = self.entry29Str.get()
            json.dump(self.jsonUserData, fileOut) #write to .json file
            print("write user data successfully")
            
    def resetUserData(self, username):
        self.programModeCombobox.set("DDD")
        self.entry01Str.set("60")
        self.entry02Str.set("120")
        self.entry03Str.set("120")
        self.entry04Str.set("150")
        self.entry05Str.set("OFF")
        self.entry06Str.set("50")
        self.entry07Str.set("OFF")
        self.entry08Str.set("3.5")
        self.entry09Str.set("3.5")
        self.entry10Str.set("3.75")
        self.entry11Str.set("3.75")
        self.entry12Str.set("0.4")
        self.entry13Str.set("0.4")
        self.entry14Str.set("0.75")
        self.entry15Str.set("2.5")
        self.entry16Str.set("320")
        self.entry17Str.set("250")
        self.entry18Str.set("250")
        self.entry19Str.set("OFF")
        self.entry20Str.set("OFF")
        self.entry21Str.set("OFF")
        self.entry22Str.set("OFF")
        self.entry23Str.set("20")
        self.entry24Str.set("1")
        self.entry25Str.set("40")
        self.entry26Str.set("Med")
        self.entry27Str.set("30")
        self.entry28Str.set("8")
        self.entry29Str.set("5")
        self.writeUserData(username)

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
