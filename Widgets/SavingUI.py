
from .GIFSavingWorker import GIFSavingWorker
from XJ.Functions.GetProcMemSize import GetProcMemSize

import os
from PyQt5.QtWidgets import QWidget,QLabel,QGridLayout,QMessageBox,QPushButton,QProgressBar,QFileDialog
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtCore import Qt

__all__=['SavingUI']

class SavingUI(QWidget):
	config={
		'hintCreate':'文件生成中',
		'hintSave':'文件保存中',
		'hintStop':'操作取消中',
		'hintSize':'文件大小：{size}',
		'hintMemory':'内存占用：{size}',
		'hintProgress':'{percent:.1f}%'
	}
	def __init__(self):
		super().__init__()
		self.__hintStatus=QLabel()
		self.__hintMemory=QLabel(self.config['hintMemory'])
		self.__hintSize=QLabel(self.config['hintSize'])
		self.__btnSave=QPushButton('保存')
		self.__pbar=QProgressBar()
		self.__worker=GIFSavingWorker()
		self.__hintStatus.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.__mbox=QMessageBox(QMessageBox.Icon.Information,"图片保存成功","点击确认查看文件")

		grid=QGridLayout(self)
		grid.addWidget(self.__hintStatus,0,0,1,2)
		grid.addWidget(self.__hintMemory,1,0,1,2)
		grid.addWidget(self.__hintSize,2,0,1,2)
		grid.addWidget(self.__pbar,3,0,1,1)
		grid.addWidget(self.__btnSave,3,1,1,1)
		grid.setRowStretch(1,1)

		self.__pbar.setRange(0,0)
		self.__pbar.setValue(0)
		self.__pbar.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.__btnSave.clicked.connect(self.__Action_SaveGIF_Start)
		self.__worker.updated.connect(self.__Action_UpdateHint)
		self.__worker.completed.connect(self.__Action_Worker_Finish)
		self.__mbox.addButton('确认',QMessageBox.ButtonRole.AcceptRole)
		self.__mbox.accepted.connect(lambda:os.system(f'start {self.__worker.Get_Path()}'))
		self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint)
		self.setWindowTitle('GIF生成')
		self.setFixedSize(400,125)
		self.setWindowModality(Qt.ApplicationModal)#作为弹窗屏蔽其他窗口
		self.hide()
	def Opt_Save(self,path:str):
		self.__Action_SaveGIF_Start(path)
	def Opt_Start(self,frames:list,duration:int,size:tuple,quality:int=85):
		'''
			frames为XJ_Frames列表；
			duration是帧时长，单位ms；
			size为图片分辨率；
			quality为GIF保存质量
		'''
		self.__worker.Opt_MakeGIF(frames,duration,size,quality)
		self.__btnSave.setEnabled(False)
		self.__pbar.setMaximum(0)
		self.__Action_UpdateHint()
		self.show()
	def __Action_SaveGIF_Start(self,path:str=None):
		path=QFileDialog.getSaveFileName(None,"保存GIF文件","",filter='*.gif')[0]
		self.__worker.Opt_SaveGIF(path)
	def __Action_Worker_Finish(self,success:bool):
		if(success):
			self.__btnSave.setEnabled(True)
			status=self.__worker.Get_Status(False)
			self.__Action_UpdateHint()
			if(status==2):
				self.__mbox.show()
		else:
			self.close()
	def __Action_UpdateHint(self):
		status=self.__worker.Get_Status()
		gifSize=self.__worker.Get_GIFSize()
		memSize=GetProcMemSize()#self.__worker.Get_MemorySize返回的是不准确的图片内存占用，因此索性返回整个程序的运行内存占用
		writtenSize=self.__worker.Get_WrittenSize()

		percent=writtenSize/gifSize*100 if gifSize!=0 else 0
		self.__hintMemory.setText(self.config['hintMemory'].format(size=self.__CalcSize(memSize)))
		self.__hintSize.setText(self.config['hintSize'].format(size=self.__CalcSize(gifSize)))
		self.__hintStatus.setText('' if status==0 else self.config['hintCreate'] if status==1 else self.config['hintSave'] if status==2 else self.config['hintStop'])
		self.__pbar.setMaximum(gifSize)
		self.__pbar.setValue(writtenSize)
		self.__pbar.setFormat(self.config['hintProgress'].format(percent=percent))
	@staticmethod
	def __CalcSize(size):
		i=0
		units=['B','KB','MB','GB']
		while(size>10240 and i<len(units)):
			size/=1024
			i+=1
		size=round(size,2)
		return f'{size} {units[i]}'
	def closeEvent(self,event:QCloseEvent) -> None:
		if(self.__worker.Get_Status()!=0):
			self.__worker.Opt_Stop()
			event.ignore()
