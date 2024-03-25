
from XJ.Structs.XJ_GIFMaker import XJ_GIFMaker
from XJ.Widgets.XJQ_NumInput import XJQ_NumInput
from XJ.Widgets.XJQ_SepLine import XJQ_SepLine
from XJ.Widgets.XJQ_PureColorIconButton import XJQ_PureColorIconButton
from XJ.Widgets.XJQ_PictListView import XJQ_PictListView

import os
from PyQt5.QtWidgets import QWidget,QLabel,QMenu,QGridLayout,QFileDialog
from PyQt5.QtGui import QColor,QPalette,QCursor
from PyQt5.QtCore import pyqtSignal,Qt,QPoint,QModelIndex

__all__=['OperationUI']
class OperationUI(QWidget):
	'''
		图片列表操作界面
	'''
	updatePreview=pyqtSignal()#更新预览图
	makeGIF=pyqtSignal()#点击了保存GIF按钮
	scaleChange=pyqtSignal(float)#图片缩放发生了修改
	durationChange=pyqtSignal(float)#帧时间间隔duration发生了修改
	config={
		'loadingGIF':'Icons/加载动画.gif',
		'iconRefresh':'Icons/刷新.png',
		'iconSave':'Icons/保存.png',
		'txHint':'图片数量：$pictCount\n图片分辨率：$resolution',
	}
	def __init__(self):
		super().__init__()
		self.__lb_rate=QLabel('倍率：')
		self.__ni_rate=XJQ_NumInput(None,1,100,1,0.01,0.1)
		self.__lb_scale=QLabel('缩放值：')
		self.__ni_scale=XJQ_NumInput(None,0.01,1,1,0.01,0.1)#应该没人会选择主动放大的吧(而且内存占用挺严重的说实话)
		self.__lb_duration=QLabel('帧时长(s)：')
		self.__lb_hint=QLabel()
		self.__lv=XJQ_PictListView(loadingGIF=self.config['loadingGIF'])
		self.__ni_duration=XJQ_NumInput(None,0.001,100,0.05,0.001,0.01)
		self.__btn_refresh=XJQ_PureColorIconButton()
		self.__btn_makeGIF=XJQ_PureColorIconButton()
		self.__menu=QMenu()
		self.__val_resolution=[0,0]#图片分辨率(宽,高)
		self.__val_pictCount=[0,0]#图片数(选中图片数,图片总数)
		self.__val_clickIndex=-1
		self.config=self.config.copy()

		self.__InitUI()
		self.__InitConfig()
		self.setFocusPolicy(Qt.ClickFocus)
		self.Set_Font(15,QColor(64,64,64,192),hint=True)
		self.Set_Font(18,attr=True,button=True)
		self.Opt_ReloadConfig()
	def __InitUI(self):
		grid=QGridLayout(self)
		grid.setRowStretch(0,1)
		grid.setColumnStretch(1,1)
		grid.setVerticalSpacing(2)
		grid.setContentsMargins(0,0,0,0)
		lastPos=[-1,-1]
		def EasyAppend(wid,colSpan=1,col=None,alignment=Qt.Alignment(),newRow=True):
			if(newRow):
				lastPos[0]+=1
				lastPos[1]=0
			if(col):
				lastPos[1]=col
			grid.addWidget(wid,lastPos[0],lastPos[1],1,colSpan,alignment)
			lastPos[1]+=colSpan
		EasyAppend(self.__lv,4)
		EasyAppend(self.__lb_rate,2)
		EasyAppend(self.__ni_rate,2,newRow=False)
		EasyAppend(self.__lb_scale,2)
		EasyAppend(self.__ni_scale,2,newRow=False)
		EasyAppend(self.__lb_duration,2)
		EasyAppend(self.__ni_duration,2,newRow=False)
		EasyAppend(XJQ_SepLine(Qt.Vertical,1,(10,1),QColor(0,0,0,128)),4)
		EasyAppend(self.__lb_hint,4)
		EasyAppend(self.__btn_refresh)
		EasyAppend(self.__btn_makeGIF,newRow=False)
	def __InitConfig(self):
		policy=self.__lb_scale.sizePolicy()
		policy.setRetainSizeWhenHidden(True)
		self.__lb_scale.setSizePolicy(policy)
		self.__lb_duration.setSizePolicy(policy)
		self.__btn_refresh.setToolTip('刷新动图预览')
		self.__btn_makeGIF.setToolTip('生成GIF')
		self.__btn_refresh.Set_FgColor(QColor(160,160,160),QColor(120,120,120),QColor(160,160,160))
		self.__btn_makeGIF.Set_FgColor(QColor(160,160,160),QColor(120,120,120),QColor(160,160,160))
		self.__btn_refresh.clicked.connect(self.__Action_UpdatePreview)
		self.__btn_makeGIF.clicked.connect(self.__Action_MakeGIF)
		self.__ni_rate.setFixedWidth(100)
		self.__ni_scale.setFixedWidth(100)
		self.__ni_scale.Set_Value(1)
		self.__ni_duration.setFixedWidth(100)
		self.__ni_scale.valueChanged.connect(self.__Action_ChangeScale)
		self.__ni_rate.valueChanged.connect(self.__Action_ChangeRate)
		self.__ni_duration.valueChanged.connect(self.__Action_ChangeDuration)
		self.__lv.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)#右键菜单：https://blog.csdn.net/FL1623863129/article/details/131701852
		self.__lv.customContextMenuRequested.connect(self.__Action_ShowMenu)
		self.__menu.addAction('添加图片',self.__Action_LoadPicts)
		self.__menu.addAction('刷新动图预览',self.__Action_UpdatePreview)
		self.__menu.addAction('清空列表',self.__Action_Clear)
		self.__lv.Get_ListView().model().dataChanged.connect(self.__Action_ItemDataChange)
	def Get_GIFAttribute(self,*attrs):
		'''
			获取与GIF生成相关的数据，
			返回{'frames':<list>,'size':<tuple>,'duration':<int>,'scale':<float>,'scaledSize':<tuple>}
			可以指定特定的键，不指定则返回全部数据。
		'''
		rst={}
		if(not attrs):
			attrs=['frames','size','duration','scale','scaledSize']
		for attr in attrs:
			if(attr=='frames'):
				data=self.__lv.Get_CheckedRow(returnFrame=True)
			elif(attr=='size'):
				data=self.__val_resolution
			elif(attr=='duration'):
				data=self.__ni_duration.Get_Value()
			elif(attr=='scale'):
				data=self.__ni_scale.Get_Value()
			elif(attr=='scaledSize'):
				size=self.__val_resolution
				scale=self.__ni_scale.Get_Value()
				data=[int(size[i]*scale) for i in range(2)]
			rst[attr]=data
		return rst
	def Set_Font(self,font=None,color=None,*,hint:bool=False,attr:bool=False,button:bool=False):
		'''
			font为QFont，也可以传入int只调整字号大小。
			color为QPalette，也可以传入QColor只设置字体颜色。
		'''
		lst_hint=[
			self.__lb_hint,
		]
		lst_attr=[
			self.__lb_duration,
			self.__lb_scale,
			self.__lb_rate,
			self.__ni_rate,
			self.__ni_scale,
			self.__ni_duration,
		]
		lst_button=[
			self.__btn_refresh,
			self.__btn_makeGIF,
		]
		lst=[]
		if(hint):
			lst.extend(lst_hint)
		if(attr):
			lst.extend(lst_attr)
		if(button):
			lst.extend(lst_button)
		for wid in lst:
			if(font):
				if(isinstance(font,int)):
					ft=wid.font()
					ft.setPixelSize(font)
				wid.setFont(ft)
			if(color):
				if(isinstance(color,QColor)):
					pe=wid.palette()
					pe.setColor(QPalette.WindowText,color)
				wid.setPalette(pe)
	def Opt_ReloadConfig(self):
		'''
			重新加载config
		'''
		self.__btn_refresh.setIcon(self.config['iconRefresh'])
		self.__btn_makeGIF.setIcon(self.config['iconSave'])
		self.__lv.Set_LoadingGIF(self.config['loadingGIF'])
		self.__UpdateHint()
	def Opt_Clear(self):
		'''
			清空列表
		'''
		self.__lv.Opt_Clear()
		for i in range(2):
			self.__val_resolution[i]=0
			self.__val_pictCount[i]=0
		self.__UpdateHint()
	def Opt_LoadPicts(self,path:str=None,index:int=None):
		'''
			加载图片资源，并将结果追加到列表中。
			如果path不指定则会弹出文件选择窗口。
			index为None的话则以最后一次右键图片列表时鼠标位置对应的索引为准
		'''
		if(not path):
			path=QFileDialog.getOpenFileName(None,"载入资源文件","",filter='*.png;*.jpg;*.mp4;*.gif;*.webp')[0]
		if(index==None):
			index=self.__val_clickIndex
		if(path and os.path.exists(path)):
			gm=XJ_GIFMaker()
			gm.Opt_Insert(path)
			if(self.__lv.Get_Length()==0):
				self.__ni_duration.Set_Value(gm.duration/1000 if len(gm.frames)>1 else 1)
			self.Opt_InsertPicts(gm.frames,path,index)
			self.__val_pictCount[0]+=len(gm.frames)
			self.__val_pictCount[1]+=len(gm.frames)
			self.__UpdateHint()
			gm.Opt_Clear()
	def Opt_InsertPicts(self,pictLst:list,group:str,index:int=-1):
		'''
			将XJ_Frame列表插入到图片列表中。
			index为负值则添加到末尾。
		'''
		self.__lv.Opt_Insert(pictLst,group,index=index)
		for size in (frame.size() for frame in pictLst):
			for i in range(2):
				self.__val_resolution[i]=max(self.__val_resolution[i],size[i])
		self.__UpdateHint()
	def __UpdateHint(self):
		'''
			更新hint文本
		'''
		rs=self.__val_resolution
		pc=self.__val_pictCount
		rss=[int(val*self.__ni_scale.Get_Value()) for val in rs]
		tx=self.config['txHint']
		tx=tx.replace('$resolution',f'{rss[0]}x{rss[1]} / {rs[0]}x{rs[1]}')
		tx=tx.replace('$pictCount',f'{pc[0]} / {pc[1]}')
		self.__lb_hint.setText(tx)
	def __Action_LoadPicts(self):
		'''
			菜单项——添加图片
		'''
		self.Opt_LoadPicts()
	def __Action_ShowMenu(self,pos:QPoint):
		'''
			操作——显示菜单
		'''
		if(pos==None):
			pos=QCursor.pos()
		else:
			pos=self.__lv.mapToGlobal(pos)
		index=self.__lv.Get_CursorRow(pos).row()
		self.__val_clickIndex=index
		self.__menu.popup(pos)
	def __Action_UpdatePreview(self):
		'''
			操作——更新动图预览
		'''
		self.updatePreview.emit()
	def __Action_MakeGIF(self):
		'''
			操作——保存动图
		'''
		self.makeGIF.emit()
	def __Action_ChangeRate(self,value):
		'''
			操作——参数rate发生变化
		'''
		lvModel=self.__lv.Get_ListView().model()
		lvModel.blockSignals(True)#数据量很大的情况下如果不临时屏蔽信号那么会造成UI界面出现卡顿
		visibleRow=self.__lv.Get_VisibleRow()
		count=int(len(visibleRow)//value)
		checkSet={visibleRow[int(i*value)] for i in range(count)}
		self.__lv.Set_CheckState(*checkSet,check=True)
		self.__lv.Set_CheckState(*(set(range(self.__lv.Get_Length()))-checkSet),check=False)
		self.__val_pictCount[0]=count
		lvModel.blockSignals(False)
		self.__UpdateHint()
		self.__lv.Get_ListView().viewport().update()
	def __Action_ChangeScale(self,value):
		'''
			操作——参数scale发生变化
		'''
		self.__UpdateHint()
		self.scaleChange.emit(value)
	def __Action_ChangeDuration(self,value):
		'''
			操作——参数duration发生变化
		'''
		self.durationChange.emit(value)
	def __Action_ItemDataChange(self,indexA:QModelIndex,indexB:QModelIndex,roles:list):
		'''
			操作——单元格数据发生变化。
			主要记录鼠标点击时复选框的状态切换
		'''
		if(Qt.ItemDataRole.CheckStateRole in roles):
			# 状态发生变化
			i=-1 if indexA.data(Qt.ItemDataRole.CheckStateRole)==Qt.CheckState.Unchecked else 1
			self.__val_pictCount[0]+=i
			self.__UpdateHint()
	def __Action_Clear(self):
		'''
			菜单项——清空列表
		'''
		self.Opt_Clear()
