from tkinter import *
from tkinter import ttk
import json
import os

class appDCM:
    #create dictionary
    screenDictionary = {"top":None, "mid":None, "bot":None}
    fontDictionary = {}
    
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

        #create login screen
        self.createLoginScreen()
        
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

            if os.path.exists("./images"):
                self.MacEngLogoImg = PhotoImage(file="./images/MacFireball.png").subsample(2, 2)
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

            self.loginButton = ttk.Button(self.loginFrame, text="Login", style="loginButton.TButton")
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

            self.displayScreen("loginScreen")
            print("login screen created successfully")
            return True

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

            self.registerButton = ttk.Button(self.registerFrame, text="Create Account", style="loginButton.TButton")
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

            self.displayScreen("registerScreen")
            print("register screen created successfully")
            return True

    def checkRowValue(self, row):
        if not (row=="top" or row=="mid" or row=="bot"):
            raise ValueError('<row> value must be either "top", "mid", or "bot"')
        else:
            if (row=="top"):
                return 0
            if (row=="bot"):
                return 2
            return 1 #return mid

    def displayScreen(self, screenName, row="mid"):
        self.checkRowValue(row)
        if self.screenDictionary.get(row) is not None:
            self.screenDictionary[row].grid_forget()
        self.screenDictionary[row] = self.screenDictionary[screenName]
        self.screenDictionary[row].grid(row=self.checkRowValue(row), column=0, sticky=W+E+N+S)
        self.rootWindowResize()

    def rootWindowResize(self):
        self.root.update()
        self.root.minsize(self.root.winfo_reqwidth(), self.root.winfo_reqheight())
        self.root.geometry(str(self.root.winfo_reqwidth())+"x"+str(self.root.winfo_reqheight()))
        self.root.resizable(1, 1)

    def createDefaultUser(self, username=""):
        self.userDirectory = "./user"
        self.userloginFile = "/userlogin.json"
        with open(self.userDirectory+self.userloginFile, "w") as fileOut:
            json.dump("", fileOut)
            print("create defaultUser.json file")

##    def 

    def readDefaultUser(self):
        self.userDirectory = "./user"
        self.userloginFile = "/userlogin.json"
        if not os.path.exists(self.userDirectory):
            os.mkdir(self.userDirectory)
            print("make "+self.userDirectory+" subdirectory")
##        if not os.path.isfile(self.userDirectory+self.userloginFile):


            
        if os.path.isfile(self.userDirectory+self.userloginFile):
            print("default.json file exists")
            with open(self.userDirectory+self.userloginFile, "r") as fileIn:
                self.jsonDefaultUser = json.load(fileIn)

            
login = appDCM()
##login.createDefaultUser()
