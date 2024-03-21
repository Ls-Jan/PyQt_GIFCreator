
from XJ.Structs.XJ_GIFMaker import XJ_GIFMaker

import os
import io
import time
from PyQt5.QtCore import pyqtSignal,QThread

__all__=['GIFSavingWorker']
class GIFSavingWorker(QThread):
	updated=pyqtSignal()
	def __init__(self):
		super().__init__()
		self.__gm=XJ_GIFMaker()
		self.__status=0#取值0、1、2，分别对应等待操作、图片生成中、图片保存中
		self.__lastStatus=0
		self.__data=b''#GIF数据
		self.__writtenSize=0#文件写入大小
		self.__path=''#保存路径
	def Get_Status(self,current:bool=True):
		return self.__status if current else self.__lastStatus
	def Get_Path(self):
		return self.__path
	def Get_GIFSize(self):
		return self.__gm.Get_SavingSize()
	def Get_MemorySize(self):
		return self.__gm.Get_MemorySize()
	def Get_WrittenSize(self):
		return self.__writtenSize
	def Opt_MakeGIF(self,frames:list,duration:int,size:tuple,quality:int=85):
		if(self.__status==0):
			if(len(frames)>0):
				self.__gm.frames=frames
				self.__gm.duration=duration
				self.__gm.size=size
				self.__gm.Opt_SaveGif(quality=quality,callback=self.__Action_MakeGIF_Finish)
				self.__writtenSize=0
				self.__status=1
				self.start()
			else:
				self.finished.emit()
	def Opt_SaveGIF(self,path:str):
		if(path):
			if(self.__status==0):
				self.__path=path
				self.__status=2
				self.__writtenSize=0
				self.start()
	def Opt_Stop(self):
		if(self.__status==1):
			self.__gm.Opt_StopOperation()
		elif(self.__status==2):
			self.__status=0
			self.wait()
			if(os.path.exists(self.__path)):
				os.remove(self.__path)
	def run(self):
		self.__lastStatus=self.__status
		time.sleep(0.5)
		if(self.__status==1):
			while(self.__status!=0):
				time.sleep(0.1)
				self.updated.emit()
		elif(self.__status==2):
			if(self.__data):
				file=open(self.__path,'wb')
				bio=io.BytesIO(self.__data)
				sizeT=len(self.__data)
				sizeW=0
				sizeP=1024
				mTime=time.time()
				while(self.__status==2):
					size=min(sizeT,sizeP)
					if(size==0):
						self.__status=0
						break
					file.write(bio.read(size))
					sizeW+=size
					sizeT-=size
					self.__writtenSize=sizeW
					cTime=time.time()
					if(cTime-mTime<0.05):#加大剂量，药不能停
						sizeP*=2
					self.updated.emit()
				file.close()
	def __Action_MakeGIF_Finish(self,data):
		self.__status=0
		self.__data=data

