#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  1 09:19:51 2019

@author: ubuntu
"""

from selenium import webdriver 
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import matplotlib.pyplot as plt
from PIL import Image
import os
import pytesseract
import argparse
import cv2
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException


def Process(CaptchaImage, preprocess = 'blur'):
    image = cv2.imread(CaptchaImage)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    
    if preprocess == "thresh":
    	gray = cv2.threshold(gray, 0, 255,
    		cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    elif preprocess == "blur":
    	gray = cv2.medianBlur(gray, 3)

    filename = "{}.png".format(os.getpid())
    cv2.imwrite(filename, gray)
    
    text = pytesseract.image_to_string(Image.open(filename))
    os.remove(filename)
    print('Cracked Captcha -->', text)
    return (text)

def CaptchaCracker(
        ShowScreenShot = 0,
        District = 25, 
        Assembly = 199, 
        PartMinMax = (1, 1000), 
        cropping = (641, 409, 841, 443), 
        output = 'Pune',
        preprocess = 'blur'):
    
    download_path = os.path.abspath(os.path.join(os.curdir, output))
    
    if not os.path.exists(download_path):
        os.mkdir(download_path)
        
    fp = FirefoxProfile('dg05529x.mumbaiceo')  
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
    fp.set_preference("browser.download.folderList", 2)
    fp.set_preference("browser.download.dir", download_path)
    
    
    geckodriver = 'geckodriver/geckodriver'
    url ="https://ceo.maharashtra.gov.in/SearchList/"
    driver = webdriver.Firefox(executable_path = geckodriver, firefox_profile=fp)
    driver.get(url)
    District =  driver.find_element_by_xpath('//select[@name="ctl00$Content$DistrictList"]')
    District.click()
    MumbaiDistrict = driver.find_element_by_xpath('//option[@value="25"]')
    MumbaiDistrict.click()
    for AssemblyList in range(Assembly, Assembly + 1):

        Assembly =  driver.find_element_by_xpath('//option[@value='+str(AssemblyList)+']')
        Assembly.click()
        PartList = int(PartMinMax[0])
        try:
            while PartList < (int(PartMinMax[1]) + 1):    
                Part =  driver.find_element_by_xpath('//select[@name="ctl00$Content$PartList"]/option[@value='+str(PartList)+']')
                Part.click()
                                
                driver.save_screenshot('captcha/captcha.png')
                image = Image.open('captcha/captcha.png')
                
                if ShowScreenShot == 1:
                    plt.imshow(image)
                    plt.show()
                    ShowScreenShot = 99
                    input('Press any key to continue..')
                
                image = image.crop(cropping)
                image.save('png/captcha.png')
                CaptchaBreak = Process('png/captcha.png', preprocess)
                InputCaptcha =  driver.find_element_by_xpath('//input[@name="ctl00$Content$txtcaptcha"]')
                InputCaptcha.send_keys(CaptchaBreak)
                
                try :
                    Submit =  driver.find_element_by_xpath('//input[@type="submit"]')
                    Submit.click()
                    driver.find_element_by_link_text('View PDF').click()
                    print (driver.window_handles)
                    
                    PartList = PartList + 1
                    print('Part List --> ', PartList, end = '\n\n')
                    
                    
                except:
                    print('Part List --> ', PartList, end = '\n\n')
                    driver.find_element_by_xpath('//input[@name="ctl00$Content$txtcaptcha"]').clear()
                    PartList = PartList
                    
        except NoSuchElementException:
            print('NoSuchElementException Occured')
            driver.close()
            PartList = PartList
            CaptchaCracker(
                    ShowScreenShot = ShowScreenShot,
                    District = District, 
                    Assembly = Assembly, 
                    PartMinMax = (PartList, int(PartMinMax[1])),
                    cropping = cropping, 
                    output = output,
                    preprocess = preprocess
                    )              
            
        except StaleElementReferenceException:
            print('StaleElementReferenceException Occured')
            driver.find_element_by_xpath('//input[@name="ctl00$Content$txtcaptcha"]').clear()
            driver.close()
            PartList = PartList
            CaptchaCracker(
                    ShowScreenShot = ShowScreenShot,
                    District = District, 
                    Assembly = Assembly, 
                    PartMinMax = (PartList, int(PartMinMax[1])),
                    cropping = cropping, 
                    output = output,
                    preprocess = preprocess
                    )
                
                
ap = argparse.ArgumentParser()
ap.add_argument("-ss", "--ShowScreenShot", required=False, type=int, default = 0,
                help = "show the plt plot of the screen short to know the crop dimension")
ap.add_argument("-d", "--District", required=True, type=int,
                help="Define the district number")
ap.add_argument("-a", "--Assembly", required=True, type=int,
                help="Define the Assembly number")
ap.add_argument("-pmm", "--PartMinMax", required=False, nargs='+', type=int, default = [1, 1000],
                help="Maximum and minimum part list")
ap.add_argument("-c", "--cropping", required=True, nargs='+', type=int,
                help="cropping dimension for captcha")
ap.add_argument("-o", "--output", required=True, type=str,
                help="path to the output folder, creates if do not exists")
ap.add_argument("-p", "--preprocess", required=False, type=str, default = 'blur',
                help="Preprocessing technique to use --> blur, thresh")
args = vars(ap.parse_args())


CaptchaCracker(
        ShowScreenShot = args['ShowScreenShot'],
        District = args['District'],
        Assembly = args['Assembly'], 
        PartMinMax = tuple(args['PartMinMax']), 
        cropping = tuple(args['cropping']), 
        output = args['output'],
        preprocess = args['preprocess']
                   )
                    