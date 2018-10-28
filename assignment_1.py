from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import json
import os
import base64

class appDCM:
    #create dictionary
    screenDictionary = {"top":None, "mid":None, "bot":None}
    fontDictionary = {}

    #image file and directory
    imageDirectory = "./images"
    logoFile = "/MacFireball.png"

    #userdata file and directory
    userDirectory = "./user"
    userloginFile = "/userlogin.json"
    jsonUserlogin = {}
    
    def __init__(self):
        #create new window ================================
        self.root = Tk()
        self.root.title("SFWR 3K04 - DCM")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure((0, 2), weight=1)
        self.root.rowconfigure(1, weight=3)

        #create header and logo
        self.createHeaderScreen()
        self.createLogoScreen()

        #check and fix user database
        self.checkUserDirectory() #should be called before createLoginScreen()
        
        #create login screen
        self.createLoginScreen()

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

    def checkRowValue(self, rowValue):
        if not (rowValue=="top" or rowValue=="mid" or rowValue=="bot"):
            raise ValueError('<row> value must be either "top", "mid", or "bot"')
        else:
            if (rowValue=="top"):
                return 0
            if (rowValue=="bot"):
                return 2
            return 1 #return mid

    def displayScreen(self, screenName, rowValue="mid"):
        if screenName in self.screenDictionary:
            self.checkRowValue(rowValue)
            if self.screenDictionary.get(rowValue) is not None:
                self.screenDictionary[rowValue].grid_forget()
            self.screenDictionary[rowValue] = self.screenDictionary[screenName]
            self.screenDictionary[rowValue].grid(row=self.checkRowValue(rowValue), column=0, sticky=W+E+N+S)
            self.rootWindowResize()
            return True
        else:
            print(screenName+" does not exist")
            return False

    def rootWindowResize(self):
        self.root.update()
        self.root.minsize(self.root.winfo_reqwidth(), self.root.winfo_reqheight())
        self.root.geometry('%dx%d' % (self.root.winfo_reqwidth(), self.root.winfo_reqheight()))
        self.root.resizable(1, 1)
        
    def createFont(self, name, fontName, size, weight="normal"):
        self.fontDictionary[name] = (fontName, size, weight)
        
    def createHeaderScreen(self):
        if "headerScreen" in self.screenDictionary:
            print("header screen already exist")
            self.displayScreen("headerScreen", "top")
            return False
        else:
            self.headerFrame = Frame(self.root, padx=20, pady=0)
            self.screenDictionary["headerScreen"] = self.headerFrame

            self.headerSoftwareName = Label(self.headerFrame, text="Pacemaker Controller-Monitor")
            self.headerSoftwareName.grid(row=0, sticky=W)

            self.displayScreen("headerScreen", "top")
            print("header screen created successfully")
            return True
        
    def createLogoScreen(self):
        if "logoScreen" in self.screenDictionary:
            print("logo screen already exist")
            self.displayScreen("logoScreen", "bot")
            return False
        else:
            self.logoFrame = Frame(self.root, padx=0, pady=10)
            self.logoFrame.columnconfigure(0, weight=1)
            self.screenDictionary["logoScreen"] = self.logoFrame

            if os.path.exists(self.imageDirectory):
                self.MacEngLogoImg = PhotoImage(file=self.imageDirectory+self.logoFile).subsample(2, 2)
                self.MacEngLogoLabel = Label(self.logoFrame, image=self.MacEngLogoImg)
                self.MacEngLogoLabel.grid(row=0, pady=5)
            
            self.companyName = Label(self.logoFrame, text="Spontaneous Cardiac Arrest Ltd.")
            self.companyName.grid(row=1)

            self.displayScreen("logoScreen", "bot")
            print("logo screen created successfully")
            return True

    def createLoginScreen(self):
        if "loginScreen" in self.screenDictionary:
            print("login screen already exist")
            self.displayScreen("loginScreen")
            return False
        else:
            self.loginFrame = Frame(self.root, padx=20, pady=10)
            self.loginFrame.columnconfigure((1, 2), weight=1)
            self.loginFrame.rowconfigure((0, 1, 3), weight=1)
            self.screenDictionary["loginScreen"] = self.loginFrame

            #title widget
            self.createFont("loginTitleFont", "TkDefaultFont", 30, "bold")
            self.loginTitle = Label(self.loginFrame, text="Welcome Back", font=self.fontDictionary["loginTitleFont"], height=2)
            self.loginTitle.grid(row=0, columnspan=3, sticky=N)

            #styling tk and ttk
            self.createFont("loginFont", "TkDefaultFont", 12)
            self.ttkStyle = ttk.Style()
            self.ttkStyle.configure("loginButton.TButton", font=("TkDefaultFont", 20, "bold"))
            
            #create widget
            self.usernameLabel = Label(self.loginFrame, text="Username", font=self.fontDictionary["loginFont"])
            self.passwordLabel = Label(self.loginFrame, text="Password", font=self.fontDictionary["loginFont"])
            self.usernameEntry = ttk.Entry(self.loginFrame, font=self.fontDictionary["loginFont"])
            self.passwordEntry = ttk.Entry(self.loginFrame, font=self.fontDictionary["loginFont"], show="*")

            self.loginButton = ttk.Button(self.loginFrame, text="Login", style="loginButton.TButton", command=lambda:self.loginUser())
            self.rememberMeButton = ttk.Checkbutton(self.loginFrame, text="Remember Me")
            self.smallRegisterButton = ttk.Button(self.loginFrame, text="Register", command=lambda:self.createRegisterScreen())
            
            #display widget
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
            self.usernameStr.set(self.getUserData("default"))
            if (self.usernameStr.get() == ""):
                self.setButtonState(self.rememberMeButton, '!selected')
            else:
                self.setButtonState(self.rememberMeButton)

            self.displayScreen("loginScreen")
            print("login screen created successfully")
            return True

    def passwordHiding(self, string):               
        if not isinstance(string, str):
            raise TypeError('<string> parameter must be type "str"')
        else: #hide plain-text password by using base64 encode
            return str(base64.b64encode(string.encode()))

    def loginUser(self):
        tempPassword = self.passwordHiding(self.passwordStr.get()) #temp value gets cleared when exit function
        self.passwordStr.set("") #clear password entry for login safety

        if (self.usernameStr.get() in self.jsonUserlogin and tempPassword == self.jsonUserlogin[self.usernameStr.get()]):
            if not (self.rememberMeButton.state() == ()): #if button is checked
                self.setUserData("default", self.usernameStr.get()) #remember username
            else:
                self.setUserData("default", "")
                self.usernameStr.set("") #clear username entry
            self.createProfileScreen()
            self.createProgramScreen()
        else:
            messagebox.showerror("Login Error", "Invalid username or password")
    
    def getUserData(self, username):
        with open(self.userDirectory+self.userloginFile, "r") as fileIn:
            self.jsonUserlogin = json.load(fileIn)
        return self.jsonUserlogin[username]

    def setUserData(self, username, password):
        self.jsonUserlogin[username] = password
        with open(self.userDirectory+self.userloginFile, "w") as fileOut:
            json.dump(self.jsonUserlogin, fileOut) #write to .json file
    
    def setButtonState(self, button, state='selected'):
        if not ("alternate" in state):
            button.state(['!alternate'])
        button.state([state])

    def createRegisterScreen(self):
        if "registerScreen" in self.screenDictionary:
            print("register screen already exist")
            self.displayScreen("registerScreen")
            return False
        else:
            self.registerFrame = Frame(self.root, padx=20, pady=10)
            self.registerFrame.columnconfigure((1, 2), weight=1)
            self.registerFrame.rowconfigure((0, 1, 4), weight=1)
            self.screenDictionary["registerScreen"] = self.registerFrame

            #styling tk and ttk
            self.createFont("loginFont", "TkDefaultFont", 12)
            self.ttkStyle = ttk.Style()
            self.ttkStyle.configure("loginButton.TButton", font=("TkDefaultFont", 20, "bold"))

            #title widget
            self.createFont("loginTitleFont", "TkDefaultFont", 30, "bold")
            self.registerTitle = Label(self.registerFrame, text="Register", font=self.fontDictionary["loginTitleFont"], height=2)
            self.registerTitle.grid(row=0, columnspan=3, sticky=N)
            
            #create widget
            self.createFont("loginFont", "TkDefaultFont", 12)
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
            
            self.displayScreen("registerScreen")
            print("register screen created successfully")
            return True

    def registerUser(self):
        if (self.registerUsernameStr.get() in self.jsonUserlogin or self.registerUsernameStr.get() == "default"):
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
            self.setUserData(self.registerUsernameStr.get(), self.passwordHiding(self.registerPasswordStr.get()))
            self.registerUsernameStr.set("")
            self.registerPasswordStr.set("")
            self.registerPasswordReStr.set("")
            messagebox.showinfo("Account created", "You can now login using that account")

    def createProgramScreen(self):
        if "programScreen" in self.screenDictionary:
            print("program screen already exist")
            self.displayScreen("programScreen")
            return False
        else:
            self.programFrame = Frame(self.root, padx=20, pady=10)
            self.programFrame.columnconfigure(0, weight=1)
            self.screenDictionary["programScreen"] = self.programFrame

            #styling tk and ttk
            self.createFont("programFont", "TkDefaultFont", 30, "bold")

            self.programTitle = Label(self.programFrame, text="Program Goes Here", font=self.fontDictionary["programFont"])
            self.programTitle.grid(row=0)

            self.displayScreen("programScreen")
            print("program screen created successfully")
            return True

    def createProfileScreen(self):
        if "profileScreen" in self.screenDictionary:
            print("profile screen already exist")
            self.displayScreen("profileScreen", "top")
            return False
        else:
            self.profileFrame = Frame(self.root, padx=20, pady=10)
            self.profileFrame.columnconfigure(0, weight=1)
            self.screenDictionary["profileScreen"] = self.profileFrame

            self.profileSoftwareName = Label(self.profileFrame, text="Pacemaker Controller-Monitor")
            self.profileSoftwareName.grid(row=0, sticky=W)

            self.profileButton = ttk.Button(self.profileFrame, text="Logout", command=lambda:self.logoutUser())
            self.profileButton.grid(row=0, sticky=E)

            self.displayScreen("profileScreen", "top")
            print("profile screen created successfully")
            return True

    def logoutUser(self):
        self.createLoginScreen()
        self.createHeaderScreen()



            
login = appDCM()
