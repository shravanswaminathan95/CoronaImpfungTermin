import webbrowser
import time
from selenium import webdriver
import os
import sys
import json

from plyer.utils import platform
from plyer import notification
from time import localtime, strftime

timeIntervalBurstNotification = 5
timeImplicitDriverWait = 2
timeVisibilitySecs = 1
flgNotFoundNotification = False
flgStartNotification = False
flgAcceptAllCookies = True
flgVermittlungscodePruefen = True
initNotifCntr = 1000
flgScreenShot = False

#Goeppingen
link1 = "https://229-iz.impfterminservice.de/impftermine/service?plz=73037"
#Waiblingen
link2 = "https://229-iz.impfterminservice.de/impftermine/service?plz=71334"
#Esslingen
link3  = "https://229-iz.impfterminservice.de/impftermine/service?plz=73730"
#Stuttgart Robert Bosch Krankenhaus
link4 = "https://001-iz.impfterminservice.de/impftermine/service?plz=70376"


path = (os.path.abspath(__file__))
wspacepath = os.path.dirname(path)
#pathElements = wspacepath.split(os.sep)[:]
#wspacepath = os.sep.join([wspacepath, "_log"])

dataDump = "AppointmentData.log"
logFile = os.sep.join([wspacepath, "_log", dataDump])


#v0 - reminder trigger
#webbrowser.open(linkGoeppingen, new=1, autoraise=True)
#print("Check the browser. Opened appointments available for Goeppingen.")
#webbrowser.open(linkWaiblingen, new=2, autoraise=True)
#print("Check the browser. Opened appointments available for Waiblingen.")
#webbrowser.open(linkEsslingen, new=2, autoraise=True)
#print("Check the browser. Opened appointments available for Esslingen.")


def verifyEligibility():

    
    #####################################################################################################


    if flgStartNotification:
        notification.notify(
                    title='Corona Vaccination Appointment Finder',
                    message="Searching for appointments..... \n You will be notified when an appointment is found.",
                    app_name='Corona Vaccination Appointment Finder'
                )

    flgAptFound = False
    configData = importConfig(0)
    locations = list(configData.keys())

    for location in locations:

    #for link in links:
        driver = webdriver.Chrome(r"Y:\CoronaImpfTermin\repo\drivers\chromedriver.exe")
        driver.implicitly_wait(timeImplicitDriverWait)
        measdData = ""
        print("Trying to verify eligibility for vaccinations", location)
        elem = []

        while not elem:
            driver.get(configData[location]["Link"])

            cntrVirtualRoomComp = 2
            flgPageWaitElpd = True

            while cntrVirtualRoomComp >= 0:
                if flgAcceptAllCookies:
                    try:
                        cookieElem = driver.find_elements_by_xpath("/html/body/app-root/div/div/div/div[2]/div[2]/div/div[2]/a")
                        cookieElem[0].click()
                        flgPageWaitElpd = False
                        break
                        #/html/body/app-root/div/div/div/div[2]/div[2]/div/div[2]/a
                    except: 
                        try:
                            cookieElem = driver.find_elements_by_xpath("/html/body/app-root/div/div/div/div[3]/div[2]/div/div[2]/a")
                            cookieElem[0].click()
                            flgPageWaitElpd = False
                            break
                        except:
                            time.sleep(10) #compensation of Virtual Waitroom which happens occasionally

                    cntrVirtualRoomComp-=1

            if flgPageWaitElpd:
                driver.close()
                continue

            time.sleep(timeVisibilitySecs) #Currently overridden by implicit driver wait. Can be enabled for visibility.
            elem = driver.find_elements_by_xpath("/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[2]/div/div/label[2]/span/small")#put here the content you have put in Notepad, ie the XPath

        elem[0].click()
        time.sleep(timeVisibilitySecs) #Wait for button click to respond Can be enabled for visibility.

        timeSTr = strftime("%Y-%m-%d %H:%M:%S", localtime())
        measdData = "Failed; " + "Vermittlungscodes; "+ location + ";" + timeSTr + ";\n"
        driver.implicitly_wait(timeImplicitDriverWait)
        try:
            time.sleep(4)
            resp = driver.find_element_by_class_name("alert.alert-danger.text-center") #Throws an exception when the corresponding class can't be found
            #resp = driver.find_elements_by_xpath("/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[3]/div/div/div/div[2]/div/div/div")


            if flgNotFoundNotification:
                notification.notify(
                    title='Eligibility check unsuccessful. (Appointments unavailable)',
                    message=location,
                    app_name='Corona Vaccination Appointment Finder'
                )
            print("Eligibility check unsuccessful")

            if flgScreenShot:
                screenShotName = location + "_" +timeSTr + ".png"
                driver.get_screenshot_as_file(screenShotName)
                #myScreenshot = pyautogui.screenshot()
                
                #screenShotFile = os.sep.join([wspacepath, "_log", screenShotName])
                #myScreenshot.save(r"Y:/CoronaImpfTermin/repo/_log/" + screenShotName)

        except:
            print("ALERT: Eligibility check successful")
            flgAptFound = True
            notifCntr = initNotifCntr

            timeSTr = strftime("%Y-%m-%d %H:%M:%S", localtime())

            measdData = "Success; " + "Vermittlungscodes; "+ location + ";" + timeSTr + ";\n"
            
            if flgScreenShot:
                screenShotName = location + "_" +timeSTr + ".png"
                driver.get_screenshot_as_file(screenShotName)
                #myScreenshot = pyautogui.screenshot()
                
                #screenShotFile = os.sep.join([wspacepath, "_log", screenShotName])
                #myScreenshot.save(r"Y:/CoronaImpfTermin/repo/_log/" + screenShotName)
            
            while notifCntr >= 0:

                notification.notify(
                    title='ALERT: Eligibility check successful. APPOINTMENT FOUND',
                    message=location,
                    app_name='Corona Vaccination Appointment Finder'
                )

                time.sleep(timeIntervalBurstNotification)
                notifCntr -= 1

        

        with open (logFile, 'a', encoding='utf-8') as dumpFile:
            dumpFile.write(measdData)

        dumpFile.close()

        if not flgAptFound:
            driver.close()


def checkAppointment():

    pageError = True #Flag for jumping out when page thorws "unhandled error"

    configData = importConfig(1)
    locations = list(configData.keys())

    

    if flgVermittlungscodePruefen:

        for location in locations:

            listCodes = configData[location]["RefCodes"]

            for Code in listCodes:

                driver = webdriver.Chrome(r"Y:\CoronaImpfTermin\repo\drivers\chromedriver.exe")
                driver.implicitly_wait(timeImplicitDriverWait)
                flgAptFound = False

                measdData = ""
                print("Vermittlungscodes - Searching for appointments ")
                elem = []

                while not elem:
                    driver.get(configData[location]["Link"])

                    if flgAcceptAllCookies:
                        try:
                            cookieElem = driver.find_elements_by_xpath("/html/body/app-root/div/div/div/div[2]/div[2]/div/div[2]/a")
                            cookieElem[0].click()
                            #/html/body/app-root/div/div/div/div[2]/div[2]/div/div[2]/a
                        except: 
                            cookieElem = driver.find_elements_by_xpath("/html/body/app-root/div/div/div/div[3]/div[2]/div/div[2]/a")
                            cookieElem[0].click()

                    time.sleep(timeVisibilitySecs) #Currently overridden by implicit driver wait. Can be enabled for visibility.
                    #elem = driver.find_elements_by_xpath("/html/body/app-root/div/app-page-its-search/div/div/div[2]/div/div/div[5]/div/div[1]/div[2]/div[2]/button")#put here the content you have put in Notepad, ie the XPath
                    elem = driver.find_elements_by_xpath("/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[2]/div/div/label[1]/span/small")
                    #/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[2]/div/div/label[1]/span/small

                elem[0].click()
                time.sleep(timeVisibilitySecs) #Wait for button click to respond Can be enabled for visibility.
                
                codeField = driver.find_elements_by_xpath("/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[3]/div/div/div/div[1]/app-corona-vaccination-yes/form/div[1]/label/app-ets-input-code/div/div[1]/label/input")#.send_keys("YUL5")
                codeField[0].send_keys(Code[0])

                time.sleep(1)

                codeField = driver.find_elements_by_xpath("/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[3]/div/div/div/div[1]/app-corona-vaccination-yes/form/div[1]/label/app-ets-input-code/div/div[3]/label/input")#.send_keys("AFMC")
                codeField[0].send_keys(Code[1])

                time.sleep(1)

                codeField = driver.find_elements_by_xpath("/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[3]/div/div/div/div[1]/app-corona-vaccination-yes/form/div[1]/label/app-ets-input-code/div/div[5]/label/input")#.send_keys("B7ZZ")
                codeField[0].send_keys(Code[2])           

                time.sleep(4)

                cntrTrialButtons = 20
                
                while cntrTrialButtons>=0:
                    try:
                        goButton = driver.find_elements_by_xpath("/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[3]/div/div/div/div[1]/app-corona-vaccination-yes/form/div[3]/button")
                        goButton[0].click()
                        time.sleep(1)
                    except: 
                        try:
                            goButton = driver.find_elements_by_xpath("/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[3]/div/div/div/div[1]/app-corona-vaccination-yes/form/div[2]/button")
                            goButton[0].click()
                            time.sleep(1)
                        except:
                            None

                    try:
                        TerminSuchenButton = driver.find_elements_by_xpath("/html/body/app-root/div/app-page-its-search/div/div/div[2]/div/div/div[5]/div/div[1]/div[2]/div[2]/button")
                        TerminSuchenButton[0].click()
                        time.sleep(1)
                        pageError = False
                        break
                    except:
                        try:
                            goButton = driver.find_elements_by_xpath("/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[3]/div/div/div/div[1]/app-corona-vaccination-yes/form/div[3]/button")
                            goButton[0].click()
                            time.sleep(1)
                        except:None

                    cntrTrialButtons-=1

                if pageError:
                    driver.close()
                    continue

                time.sleep(timeVisibilitySecs)

                measdData = "Failed; " + "Appointment; " + location + ";" + strftime("%Y-%m-%d %H:%M:%S", localtime()) + ";\n"
                driver.implicitly_wait(timeImplicitDriverWait)

                try:
                    resp = driver.find_element_by_class_name("its-slot-pair-search-no-results") #Throws an exception when the corresponding class can't be found
                    print("No appointments available for the given Vermittlungscode")
                    time.sleep(timeVisibilitySecs)
                    if flgNotFoundNotification:
                        notification.notify(
                            title='No Appointment found for the Vermittlungscode',
                            message="XXXXX",
                            app_name='Corona Vaccination Appointment Finder'
                        )

                    if flgScreenShot:
                        screenShotName = timeSTr + ".png"
                        driver.save_screenshot("C:/temp/TerminScr/" + screenShotName)

                except:
                    print("ALERT: Appointment found for the Vermittlungscode")
                    flgAptFound = True
                    notifCntr = initNotifCntr

                    #measdData = "Success; " + "Appointment; " + messageDict[link].replace(" in ", "") + ";" + strftime("%Y-%m-%d %H:%M:%S", localtime()) + ";\n"
                    measdData = "Success; " + "Appointment; " + location + ";" + strftime("%Y-%m-%d %H:%M:%S", localtime()) + ";\n"
                    while notifCntr >= 0:

                        notification.notify(
                            title='ALERT: APPOINTMENT FOUND for the Vermittlungscode. Please check to choose time.',
                            message= "XXXXX",
                            app_name='Corona Vaccination Appointment Finder'
                        )

                        time.sleep(timeIntervalBurstNotification)
                        notifCntr -= 1

                with open (logFile, 'a', encoding='utf-8') as dumpFile:
                    dumpFile.write(measdData)

                dumpFile.close()

                if not flgAptFound:
                    driver.close()


def importConfig(caller):
    configFileName = "Config.json"
    configFile = os.sep.join([wspacepath, configFileName])   

    jsonFile = open(configFile, "r")
    fileContent = jsonFile.read()
    x = eval(fileContent)
    jStr = json.dumps(x)
    configData = json.loads(jStr)

    jsonFile.close()

    retConfigData = configData.copy()
    configLocations = list(configData.keys())

    for configLocation in configLocations:
        if caller == 0:
            if configData[configLocation]["CodeSearchEnable"] != True:
                retConfigData.pop(configLocation)

        elif caller == 1:
            if configData[configLocation]["AppointmentSearchEnable"] != True:
                retConfigData.pop(configLocation)

    return retConfigData



if (__name__ == "__main__"):
    inp = int(sys.argv[1])
    if inp == 0: 
        verifyEligibility()
    elif inp == 1: 
        checkAppointment()
    else:
        exit()




#<span _ngcontent-nfa-c125="" class="its-slot-pair-search-no-results"><span _ngcontent-nfa-c125="" class="icon-ets icon-ets-warning"></span>&nbsp; Derzeit stehen leider keine Termine zur Verfügung. <br _ngcontent-nfa-c125=""><br _ngcontent-nfa-c125=""> Die Impfzentren stellen regelmäßig neue Termine ein. Bitte prüfen Sie zu einem späteren Zeitpunkt mit Hilfe Ihres Vermittlungscodes, ob wieder Termine zur Verfügung stehen. </span>
#body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(2) > div > div > label:nth-child(2) > span
#/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[2]/div/div/label[2]/span/small
#<div _ngcontent-nfa-c115="" class="alert alert-danger text-center"> Es wurden keine freien Termine in Ihrer Region gefunden. Bitte probieren Sie es später erneut. <br _ngcontent-nfa-c115=""><br _ngcontent-nfa-c115=""> Sobald genügend Impfstoff und die entsprechenden Kapazitäten vorhanden sind, werden die Impfzentren weitere Termine einstellen. </div>
#/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[3]/div/div/div/div[1]/app-corona-vaccination-yes/form/div[3]/button