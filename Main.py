from Widgets import *

from XJ.Structs.XJQ_PictLoader import XJQ_PictLoader
from XJ.Widgets.XJQ_PictCarousel import XJQ_PictCarousel
from XJ.Widgets.XJQ_LoadingMask import XJQ_LoadingMask

from PyQt5.QtWidgets import QWidget,QApplication,QHBoxLayout
from PyQt5.QtGui import QPixmap

class Main(QWidget):
	config={
		'previewMaxCount':100,#预览图最大数量
		'ouiConfig':None,#OperationUI的配置属性
	}
	def __init__(self):
		super().__init__()
		self.__oui=OperationUI()
		self.__sui=SavingUI()
		self.__pc=XJQ_PictCarousel()
		self.__pl=XJQ_PictLoader()
		self.__mask=XJQ_LoadingMask(parent=self.__pc,iconSize=(80,80))

		self.__oui.durationChange.connect(self.__UpdatePreview_ChangeDuration)
		self.__oui.updatePreview.connect(self.__UpdatePreview_Start)
		self.__oui.makeGIF.connect(self.__Action_SaveGIF)
		self.__pl.loaded.connect(self.__UpdatePreview_AddPict)
		self.__pl.finished.connect(self.__UpdatePreview_Finish)
		self.__oui.setMinimumWidth(300)
		self.__mask.hide()

		hbox=QHBoxLayout(self)
		hbox.addWidget(self.__oui)
		hbox.addWidget(self.__pc)
		hbox.setStretch(1,1)
		
		self.config=self.config.copy()
		self.config['ouiConfig']=self.__oui.config
		self.Opt_ReloadConfig()
	def Opt_SaveGIF(self):
		'''
			手动保存动图，将返回np.ndarray动图数据
		'''
		self.__Action_SaveGIF()
	def Opt_UpdatePreview(self):
		'''
			手动更新预览图
		'''
		self.__UpdatePreview_Start()
	def Opt_LoadPicts(self,path:str=None,index:int=None):
		'''
			加载图片资源，并将结果追加到列表中。
			如果path不指定则会弹出文件选择窗口。
			index为None的话则以最后一次右键图片列表时鼠标位置对应的索引为准
		'''
		self.__oui.Opt_LoadPicts(path,index)
	def Opt_InsertPicts(self,pictLst:list,group:str,index:int=-1):
		'''
			将XJ_Frame列表插入到图片列表中。
			index为负值则添加到末尾。
		'''
		self.__oui.Opt_InsertPicts(pictLst,group,index)
	def Opt_ReloadConfig(self):
		self.__oui.Opt_ReloadConfig()
	def __UpdatePreview_Start(self):
		data=self.__oui.Get_GIFAttribute()
		self.__pl.Opt_Clear()
		self.__pc.Opt_Play(False)
		self.__pc.Set_Frames([])
		self.__UpdatePreview_ChangeDuration(data['duration'])
		if(data['frames']):
			self.__pl.Opt_Append(*[(i,data['frames'][i],data['scaledSize'],False) for i in range(min(len(data['frames']),self.config['previewMaxCount']))])
			self.__mask.show()
	def __UpdatePreview_ChangeDuration(self,sec:float):
		msec=sec*1000
		self.__pc.Set_Loop(msec)
		self.__pc.Set_Duration(msec)
	def __UpdatePreview_AddPict(self,id:int,pixmap:QPixmap):
		frames=self.__pc.Get_Frames()
		frames.append(pixmap)
		self.__pc.Set_Frames(frames)
	def __UpdatePreview_Finish(self):
		self.__mask.hide()
		self.__pc.Opt_Play()
	def __Action_SaveGIF(self):
		data=self.__oui.Get_GIFAttribute()
		self.__sui.Opt_Start(data['frames'],data['duration']*1000,data['scaledSize'])


if True:
	app = QApplication([])

	file='2024-01-09 00-15-45.mp4'
	# file='Clock_JE3_BE3.webp'
	file='XJ/Widgets/icons/加载动画-7.gif'
	# file=os.path.join('F:/文档/Videos',file)
	# file=os.path.join('F:/文档/Videos',file)

	win=Main()
	win.Opt_LoadPicts(file)
	# win.Opt_UpdatePreview()
	win.show()
	win.resize(1200,800)

	app.exec_()

