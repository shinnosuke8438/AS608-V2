import micropython
import os, uos, machine, io, ujson, json, time, utime, network, gc, esp, sys, re, binascii
from machine import Pin, PWM, reset, Timer
from machine import UART
from micropython import const

# to check passwoard default: 4 byte 0000
cmd_verify_passwoard = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x07\x13\x00\x00\x00\x00\x00\x1B'

# to get image
cmd_get_image = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x03\x01\x00\x05'

# image to text
cmd_image2Tz = b'\xEF\x01\xFF\xFF\xFF\xFF'
cmd_save_image2Tz = b'\x01\x00\x04\x02'

# createModel
cmd_createModel = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x03\x05\x00\x09'

# storeModel
cmd_storeModel = b'\xEF\x01\xFF\xFF\xFF\xFF'
cmd_save_storeModel = b'\x01\x00\x06\x06\x01\x00'

#Pattern-matching the feature files in CharBuffer1 and CharBuffer2
cmd_match = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x03\x03\x00\x07'

#lay ma van tay chua tu flash ra de so sanh voi van tay vua nhan tren bo dem
cmd_search = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x08\x04\x01\x00\x00\x00\x7F\x00\x8D'

# kiem tra van tay vua nhan co phai la van tay goc hay khong
cmd_search_master = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x08\x04\x01\x00\x00\x00\x01\x00\x0F'

#to delete a segment (N) of templates of Flash library started from the specified location (or PageID)
cmd_deleteModel = b'\xEF\x01\xFF\xFF\xFF\xFF'
cmd_save_deleteModel = b'\x01\x00\x07\x0c\x00'

# to clear all finger
cmd_empty_database = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x03\x0D\x00\x11'



class FINGER_PRINT:
	def __init__(self):
		self.uart = UART(2, baudrate=57600, tx=23, rx=19, timeout=500)
		self.fingerID = None
	
	def data_return(self, len):
		self.rx_data = []             
		for i in range(len): 
			self.rx_data.append(0)
	
		self.rx_data = self.uart.read(len)
		time.sleep(0.1)
		try:
			return(self.rx_data[len-3])
		except Exception:
			return(self.rx_data)	
	
	def data_match_return(self, len):
		self.rx_data_match = []
		for i in range(len):
			self.rx_data_match.append(0)
		
		self.rx_data_match = self.uart.read(len)
		time.sleep(0.1)
		try:
			return(self.rx_data_match[len - 5])
		except Exception:
			return(self.rx_data_match)

	def data_search_return(self, len):
		self.rx_data_search = []
		for i in range(len):
			self.rx_data_search.append(0)
		self.rx_data_search = self.uart.read(len)
		time.sleep(0.1)
		try:
			self.fingerID = self.rx_data_search[len-5]
			return(self.rx_data_search[len-7])	
		except Exception:
			return(self.rx_data_search)
	
	def verifyPassword(self):
		self.uart.write(cmd_verify_passwoard)
		time.sleep(0.1)
		return self.data_return(12)
		'''
		Confirm code=00H shows OK;
		Confirm Code=01H shows receiving packet error;
		Confirm Code=13H shows password incorrect;
		Confirm Code=21H shows Must verify password first;
		
		'''
	def getImage(self):
		self.uart.write(cmd_get_image)
		return self.data_return(12)
		'''
		Confirm Code=00H shows getting success;
		Confirm Code=01H shows receiving packet error;
		Confirm Code=02H shows no finger on the sensor;
		Confirm Code=03H shows getting failed; 
		
		'''
	# slot only 1 for buffer 1 and 2 for buffer 2:
	def image2Tz(self, slot = 1):
		sum_image2Tz = cmd_save_image2Tz + bytearray([slot,0,slot+0x7])
		self.uart.write(cmd_image2Tz)
		self.uart.write(sum_image2Tz)
		time.sleep(1)
		return self.data_return(12)
		'''
		Confirm Code=00H shows generating success;
		Confirm Code=01H shows receiving packet error;
		Confirm Code=06H Shows the fingerprint image is too amorphous to generate feature;
		Confirm Code=07H Shows the fingerprint image is in order, but with too little minutiaes to generate
		feature;
		Confirm Code=15H Shows there is no valid original image in buffer to generate image;
		
		'''
	
	def createModel(self):
		self.uart.write(cmd_createModel)
		time.sleep(0.1)
		return self.data_return(12)
		'''
		Confirm Code=00H shows merging success;
		Confirm Code=01H shows receiving packet error;
		Confirm Code=0aH shows merging failed(two fingerprints are not from the same finger)
		
		'''
	
	#default store in buffer 1:
	def storeModel(self, id):
		sum_storeModel = cmd_save_storeModel + bytearray([id,0,id+0x0E])
		self.uart.write(cmd_storeModel)
		self.uart.write(sum_storeModel)
		time.sleep(1)
		return self.data_return(12)
		'''
		Confirm Code=00H shows storing success;
		Confirm Code=01H shows receiving packet error;
		Confirm Code=0bH shows PageID exceeded the range of fingerprint database;
		Confirm Code=18H shows writing FLASH error;
		
		'''
	
	def match(self):
		self.uart.write(cmd_match)
		time.sleep(0.1)
		return self.data_match_return(14)
		'''
		Confirm Code=00H shows fingerprint matched;
		Confirm Code=01H shows receiving packet error;
		Confirm Code=08H shows fingerprint unmatched; 
		
		'''
	
	def search(self):
		self.uart.write(cmd_search)
		time.sleep(2)
		return self.data_search_return(16)
		'''
		Confirm Code=00H shows searching success;
		Confirm Code=01H shows receiving packet error;
		Confirm Code=09H shows unsearched, here the page number and score are “0”;
		
		'''
	def search_master(self):
		self.uart.write(cmd_search_master)
		time.sleep(0.1)
		return self.data_search_return(16)
		'''
		Confirm Code=00H shows searching success;
		Confirm Code=01H shows receiving packet error;
		Confirm Code=09H shows unsearched, here the page number and score are “0”;
		
		'''
	def deleteModel(self, id):
		sum_deleteModel = cmd_save_deleteModel + bytearray([id,0,1,0,id+0x15])
		self.uart.write(cmd_deleteModel)
		self.uart.write(sum_deleteModel)
		time.sleep(0.1)
		return self.data_return(12)
		'''
		Confirm Code=00H shows deleting module success;
		Confirm Code=01H shows receiving packet error;
		Confirm Code=10H shows deleting module failed;
		
		'''
	def emptyDatabase(self):
		self.uart.write(cmd_empty_database)
		time.sleep(0.1)
		return self.data_return(12)
		'''
		Confirm Code=00H shows clearing success;
		Confirm Code=01H shows receiving packet error;
		Confirm Code=11H shows clearing failed; 
		
		'''
	def return_FingerID(self):
		return self.fingerID

fig = FINGER_PRINT()