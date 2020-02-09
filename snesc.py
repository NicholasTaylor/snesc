#! /Users/nicholas/py-sandbox/snesc/env/bin/python3.7
import requests, json
from bs4 import BeautifulSoup

def checkStatus():
	page = requests.get('https://snesc.nintendo.com/super-nintendo-entertainment-system-controllers')
	soup = BeautifulSoup(page.text, 'html.parser')
	targetElem = soup.find(class_='shipping-message')
	targetElemText = targetElem.find_all('strong')
	return targetElemText[0].contents[0]

def checkMeta():
	try:
		return checkStatus()
	except:
		return 'Status changed'

def sendMessage(msg):
	discordRaw = ''
	with open('discord.json','r') as discordFile:
		discordRaw = discordFile.read()
		discord = json.loads(discordRaw)
		url = discord['url']
	headers = {'Content-Type':'application/x-www-form-urlencoded'}
	data = {'content':msg}
	r = requests.post(url, data=data, headers=headers)
	print(str(r.text))

def fileUpload(fileName):
	import ftplib, os, json
	from ftplib import FTP
	fileCredentials = 'ftp.json'
	fileUpload = fileName
	with open(fileCredentials,'r') as fileOpenCredentials:
		fileContents = fileOpenCredentials.read()
		credentialsJson = json.loads(fileContents)
		username = credentialsJson['username']
		password = credentialsJson['password']
		server = credentialsJson['server']
		outputDir = credentialsJson['path']
	ftp = FTP('ftp.nicholastaylor.org')
	ftp.login(username,password)
	ftp.cwd(outputDir)
	fileUploadObject = open(fileUpload,'rb')
	ftp.storbinary('STOR ' +fileUpload, fileUploadObject)
	ftp.quit()
	fileUploadObject.close()

def logToFile(msg):
	import csv, datetime, os
	flagCreateFile = False if os.path.isfile('snesc.csv') else True
	if flagCreateFile == True:
			writeMode = 'w+'
	else:
		writeMode = 'a'
	with open('snesc.csv',writeMode) as eventWriter:
		currentDatetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		fieldnames = ['date','status']
		data = {'date':currentDatetime,'status':msg}
		writer = csv.DictWriter(eventWriter, fieldnames = fieldnames, delimiter = ',', quotechar = '"')
		if flagCreateFile == True:
			writer.writeheader()
			flagCreateFile = False
		writer.writerow(data)
	fileUpload('snesc.csv')

def runChecks():
	currentStatus = checkMeta()
	logToFile(currentStatus)
	if currentStatus != 'Currently unavailable. Please check back later.':
		sendMessage('SNESC site messaging changed. This is what we know:\n' +currentStatus +'\nhttps://snesc.nintendo.com/super-nintendo-entertainment-system-controllers')

runChecks()