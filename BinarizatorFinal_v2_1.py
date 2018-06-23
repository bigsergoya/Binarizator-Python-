# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 23:21:09 2018

@author: neksta
"""

#ПАКЕТНАЯ ОБРАБОТКА
#ПОДПУНКТ МЕНЮ С ПРОИЗВЕДЕННЫМИ ОПЕРАЦИЯМИ

import sys
import os
import numpy
import ctypes
import traceback
import logging

from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QTextEdit, QGridLayout
from PyQt5.QtWidgets import QWidget, QFrame, QLabel, QAction, QFileDialog, QDialog, QRadioButton
from PyQt5.QtWidgets import QLineEdit, QLayout, QListWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui, QtWidgets
from enum import Enum
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from copy import deepcopy
from PIL import Image
from pylab import *
from skimage import filters as skfilters
from scipy.ndimage import filters as ndfilters
from scipy.ndimage import measurements, morphology


class BinaryAlg:
    _operations = {     
    'Isodata': lambda x : 1*((abs(x) > skfilters.threshold_isodata(x))),    
    'Li': lambda x : 1*((abs(x) > skfilters.threshold_li(x))), 
    'Mean': lambda x : 1*((abs(x) > skfilters.threshold_mean(x))),
    'Minimum': lambda x : 1*((abs(x) > skfilters.threshold_minimum(x))),
    'Otsu': lambda x : 1*((abs(x) > skfilters.threshold_otsu(x))),
    'Triangle': lambda x : 1*((abs(x) > skfilters.threshold_triangle(x))),
    'Yen': lambda x : 1*((abs(x) > skfilters.threshold_yen(x)))
    }   
    
        
class BinaryData:
    DEFAULT_VALUE = 'Mean'
    
    def __init__(self,selectedOperation = DEFAULT_VALUE):
        self.___selectedOperation = selectedOperation

    def Compute(self, data):
        return BinaryAlg._operations[self.___selectedOperation](data)
    
    def ToString(self):
        line = 'Bin Alg - {} '.format(self.___selectedOperation)
        return line
    

    @property
    def OperationName(self):
        return self.___selectedOperation

    @OperationName.setter
    def OperationName(self, operationName):
        if operationName:
            print(operationName)
            self.___selectedOperation = operationName            
            
            
   
class MorphologyAlg:
    _operations = {        
    'Empty': lambda inputData, sizeX, sizeY, iterations : inputData,  
    'Gaussian Filter': lambda inputData, sizeX, sizeY, iterations \
    : ndfilters.median_filter(inputData, iterations),   
    'Opening': lambda inputData, sizeX, sizeY, iterations \
    : morphology.binary_opening(inputData, numpy.ones((sizeX,sizeY)), iterations),
    'Closing': lambda inputData, sizeX, sizeY, iterations \
    : morphology.binary_closing(inputData, numpy.ones((sizeX,sizeY)), iterations),  
    'Fill Holes': lambda inputData, sizeX, sizeY, iterations \
    : morphology.binary_fill_holes(inputData)      
    }

class MorphologyInput(Enum):
    NoInput = 'No Input'
    MatrixSize = 'Matrix size'
    IterationCount = 'Iteration count'
    MatrixSizeAndIterationCount = 'Matrix size and iteration count'
       
class MorphologyData:
    DEFAULT_VALUE = 'Empty'
    
    def __init__(self, selectedOperation = DEFAULT_VALUE, matrixHeight = 3, \
                 matrixWidth = 3, iteration = 1 ):
        self.___selectedOperation = selectedOperation        
        
        self._matrixHeight = matrixHeight
        self._matrixWidth = matrixWidth
        self._iteration = iteration    
    
    
    def GetGUIInputType(self):
        if((self.___selectedOperation == 'Opening') or (self.___selectedOperation == 'Closing')):
            return MorphologyInput.MatrixSizeAndIterationCount
        
        if(self.___selectedOperation == 'Fill Holes' or \
           self.___selectedOperation == self.DEFAULT_VALUE):
            return MorphologyInput.NoInput
       
        if(self.___selectedOperation == 'Gaussian Filter'):
            return MorphologyInput.IterationCount
        
    def Compute(self, data):
        return MorphologyAlg._operations[self.___selectedOperation](data, self._matrixHeight, self._matrixWidth, \
                                  self._iteration)
        
    def ToString(self):
        line = 'Morph Alg - {}.'.format(self.___selectedOperation)
        
        if(self.GetGUIInputType() == MorphologyInput.MatrixSizeAndIterationCount):
            line += ' MatrSizeX - {}, MatrSizeY - {}.'.format(self._matrixHeight, self._matrixWidth)
            line += ' Iterations - {}.'.format(self._iteration)
        elif(self.GetGUIInputType() == MorphologyInput.IterationCount):
            line += ' Iterations - {}.'.format(self._iteration)
        elif(self.GetGUIInputType() == MorphologyInput.MatrixSize):
            line += ' MatrSizeX - {}, MatrSizeY - {}.'.format(self._matrixHeight, self._matrixWidth)
        else:
            line += ' No parameters'
        return line
    
    @property
    def OperationName(self):
        return self.___selectedOperation

    @OperationName.setter
    def OperationName(self, operationName):
        if operationName:
            print(operationName)
            self.___selectedOperation = operationName           

class OperationStack:    
    def __init__(self):
        self.___list = []
        
    def AddOperation(self, dataClass):
        x = deepcopy(dataClass)
        self.___list.append(x)
        
    def IsValid(self):
        print('Len of Operation Stack - '+str(len(self.___list)))
        return len(self.___list) > 0 
    
    def ApplyOperationsToCurrent(self, data):
        result = data
        
        for operation in self.___list:
            result = operation.Compute(result)  
        
        return result
    
    def GetOperationsDescription(self):
        
        result = []
        
        for operation in self.___list:
            result.append(operation.ToString())
            
        return result

    def ApplyOperationsToFolder(self,currentPictureFileName:str):
        data = []
        input_path:str
        output_path:str
        
        print('currentPictureFile - '+currentPictureFileName)
        folderPath = os.path.dirname(os.path.abspath(currentPictureFileName))
        
        baseCurPictureName = os.path.basename(currentPictureFileName)
        print('BaseName - '+baseCurPictureName)
        
        print(folderPath)
        files = os.listdir(folderPath)
        
        
        print('Folder contains:')
        print(files)
        print('---Batch cycle start---')
        for fileName in files:  
            print('---Iteration---')
            path = os.path.join(folderPath, fileName)
            print('Element - '+path)
            if os.path.isdir(path):
                print('Element skipped (not a file - '+path)
                continue
            
            if fileName==baseCurPictureName:
                print('Element skipped (equals startPic) - '+fileName)
                continue
            
            print('filename - '+fileName)
            if Example.BIN_FILE_MARK in fileName:
                print('Element skipped (BIN index) - '+fileName)
                continue
            
            extenshion = os.path.splitext(fileName)[-1].lower()
            print('extenshion - '+extenshion)
            
            if extenshion not in Example.AVAILABLE_PICTURE_EXTENSHIONS:
                print('Element skipped (Extenshion not of picture) - '+fileName)
                continue
            
            data = array(Image.open(path).convert('L'), 'f')
            data = self.ApplyOperationsToCurrent(data)

            Example.SaveImageToFile(Binarizator.ConvertExternalToImage(data), folderPath, fileName)
            
        print('---Batch cycle end---')
        
        MessageBox.show(MessageBox.WARNING_MESSAGE_TITLE, MessageBox.BUTCH_FINAL_MESSAGE)


class MessageBox:  
    ERROR_MESSAGE_TITLE = 'Ошибка!'
    WARNING_MESSAGE_TITLE = 'Внимание!'
    BAD_FILE_MESSAGE = 'Ошибка чтения данных из файла.'
    CANNOT_PREPARE_MESSAGE = 'Невозможно осуществить операцию препарирования. Ошибка исх. данных.'
    BUTCH_FINAL_MESSAGE = 'Применение пакета операций завершено.'
    OPERATION_FINAL_MESSAGE = 'Операция применяется. Ожидайте.'
    
    @staticmethod
    def show(title, text):
        return ctypes.windll.user32.MessageBoxW(0, text, title, 0)

class Binarizator:
    ___morhpSettings:MorphologyData
    ___pathToFile = ''
    ___binAlgorithm:BinaryData
    _binImage = None 
    ___opStack:OperationStack
    ___needReCompute:bool
    
    @property
    def PathToFile(self):
        return self.___pathToFile

    @PathToFile.setter
    def PathToFile(self, path):
        if path:
            print('New path - ' + path)
            self.___pathToFile = path            
            self.binarizeData()
    
    @property
    def BinSettings(self):
        return self.___binAlgorithm

    @BinSettings.setter
    def BinSettings(self, settings):
        if settings:
            
            isError = (self.___binAlgorithm.OperationName == settings.OperationName)
            self.___needReCompute = not isError
            
            if(isError): 
                print('New bin alg is equals previous')
                return
            
            self.___binAlgorithm = settings
            self.binarizeData()
    
    
    @property
    def MorhpSettings(self):
        return self.___morhpSettings

    @MorhpSettings.setter
    def MorhpSettings(self, settings):
        if settings:
            self.___morhpSettings = settings
            self.___needReCompute = True
            self.prepareImage()
            
    @property
    def CleanedMorhpSettings(self):
        cleanedMorphSettings = self.___morhpSettings
        cleanedMorphSettings.OperationName = MorphologyData.DEFAULT_VALUE
        
        return cleanedMorphSettings
    
    
    @property
    def OpStack(self):
        return self.___opStack
    
    @property
    def NeedReCompute(self):
        return self.___needReCompute
    
    def __init__(self):
        self.___morhpSettings = MorphologyData()
        self.___pathToFile = ''
        self.___binAlgorithm = BinaryData()
        self.___opStack = OperationStack()
        self.___needReCompute = True
        
    def IsValid(self):
        
        if not self.PathToFile:
            result = False
        else:
            result = True
        
        
        print('Bin is valid - '+str(result))
        
        return result
        
    def IsReadyToWork(self):
        result = (self.OpStack.IsValid() and self.IsValid())
        
        print('Binarizator ready - '+ str(result))
        return result
    
    def ConvertToImage(self):
        MessageBox.show(MessageBox.WARNING_MESSAGE_TITLE, MessageBox.OPERATION_FINAL_MESSAGE)
        return self.ConvertExternalToImage(self._binImage)
            
    @staticmethod
    def ConvertExternalToImage(boolData):
        BORDER_DISPLACEMENT = 1
        
        lenX, lenY = boolData.shape
        print(type(boolData))
        image = QtGui.QImage(lenY, lenX, QtGui.QImage.Format_Mono)
        image.fill(0)
        p = QtGui.QPainter()
        p.begin(image)
        
        p.setPen(QtGui.QPen(QtGui.QColor(QtCore.Qt.white)));                
        
        for (i) in range(0+BORDER_DISPLACEMENT, lenX-BORDER_DISPLACEMENT):
            for (j) in range(0+BORDER_DISPLACEMENT, lenY-BORDER_DISPLACEMENT):
                if(boolData[i][j]):
                    p.drawPoint(j,i)
        p.end()         
                      
        return image
    
    def getDefaultImage(self):
        WINDOW_HEIGHT = 400
        WINDOW_WIDTH = 400
        
        image = QtGui.QImage(WINDOW_HEIGHT, WINDOW_WIDTH, QtGui.QImage.Format_Mono)
        image.fill(1)  
        
        return image
    
    def getImage(self):          
        if(self.___pathToFile):         
            return self.ConvertToImage()
        else:
            return self.getDefaultImage()
        
    def ClearOpStack(self):
        self.___opStack = OperationStack()
    
    def binarizeData(self):
        if (not self.___pathToFile):
            MessageBox.show(MessageBox.ERROR_MESSAGE_TITLE, MessageBox.BAD_FILE_MESSAGE)
            return
        
        self.ClearOpStack()
        
        grayPicture = numpy.array(Image.open(self.___pathToFile).convert('L'), 'f')
       
        self._binImage = BinaryAlg._operations[self.___binAlgorithm.OperationName](grayPicture)

        self.___opStack.AddOperation(self.BinSettings)

        print((self._binImage.shape))
        
    def prepareImage(self):
        if(not self.___pathToFile):
            MessageBox.show(MessageBox.ERROR_MESSAGE_TITLE, MessageBox.CANNOT_PREPARE_MESSAGE)
            return
        
        self.___opStack.AddOperation(self.MorhpSettings)
        self._binImage = MorphologyAlg._operations[self.___morhpSettings.OperationName](self._binImage, self.___morhpSettings._matrixHeight, self.___morhpSettings._matrixWidth, self.___morhpSettings._iteration)


class BinAlgWindow(QDialog):
    def __init__(self, binaryData, parent=None):
        super(BinAlgWindow, self).__init__(parent)
        
        _heigt = 200
        _width = 200
        _left = 100
        _top = 100
        
        self.binaryData = binaryData
        self.initUI(_heigt, _width, _left, _top)

        #self.setupUi(self)
        
    def initUI(self, _heigt, _width, _left, _top):
        
        layout = QGridLayout()
        self.setLayout(layout)
        
        position = 0
        
        for alg in BinaryAlg._operations.keys():
            radiobutton = QRadioButton(alg)
            
            if(alg==self.binaryData.OperationName):
                radiobutton.setChecked(True)      

            radiobutton.algValue = alg
            radiobutton.toggled.connect(self.on_radio_button_toggled)
            layout.addWidget(radiobutton, position, 0)
            
            position+=1            
        
        
        self.setGeometry(_left, _top, _heigt, _width)
        self.setWindowTitle('Binary Algorithm selection')
        self.show()
    
    def on_radio_button_toggled(self):
        radiobutton = self.sender()
        if (not radiobutton.isChecked()):
            return 
        
        self.binaryData.OperationName = radiobutton.algValue
        print("Selected Binary Algorithm is %s" % (radiobutton.algValue))


class MorpSettingsWindow(QDialog):
    def __init__(self, morphologySettings:MorphologyData, inputType:MorphologyInput, parent=None):
        super(MorpSettingsWindow, self).__init__(parent)
        
        _heigt = 200
        _width = 200
        _left = 100
        _top = 100
        
        self.MorphologySettings = morphologySettings
        
        self.InputType = inputType
        
        print( self.MorphologySettings.OperationName)
        print(self.InputType)
        
        self.initUI(_heigt, _width, _left, _top)
        
    def initUI(self, _heigt, _width, _left, _top):
        maxArraySize = 20
        maxIteration = 50
        layout = QGridLayout()
        self.setLayout(layout)
        self.position = 0
        
        if(self.InputType == MorphologyInput.MatrixSize or self.InputType == MorphologyInput.MatrixSizeAndIterationCount):
            qlMatSizeTitle = QLabel()
            qlXDim = QLabel()
            qlYDim = QLabel()
            
            qleXDim = QLineEdit()
            qleYDim = QLineEdit()
            
            qlMatSizeTitle.setText("Размеры матрицы.")
            qlMatSizeTitle.setAlignment(Qt.AlignCenter)
            
            qlXDim.setText("Размерность X. [1;"+str(maxArraySize)+"]")
            qlXDim.setAlignment(Qt.AlignCenter)            
            
            qlYDim.setText("Размерность У. [1;"+str(maxArraySize)+"]")
            qlYDim.setAlignment(Qt.AlignCenter)  
            
            qleXDim.setText(str(self.MorphologySettings._matrixHeight))
            qleYDim.setText(str(self.MorphologySettings._matrixWidth))
            
            qleXDim.textChanged.connect(self.XDimValueChanged)
            qleYDim.textChanged.connect(self.YDimValueChanged)
            
            inputValidator = QIntValidator(1,maxArraySize)
            qleXDim.setValidator(inputValidator)
            qleYDim.setValidator(inputValidator)
            
            self.addWidget(qlMatSizeTitle,layout)
            self.addWidget(qlXDim,layout)
            self.addWidget(qleXDim,layout)
            self.addWidget(qlYDim,layout)
            self.addWidget(qleYDim,layout)            
            
        if(self.InputType == MorphologyInput.IterationCount or self.InputType == MorphologyInput.MatrixSizeAndIterationCount):
            qlIterationsTitle = QLabel()
            qleIterations = QLineEdit()
        
            qlIterationsTitle.setText("Число итераций.[1;"+str(maxIteration)+"]")
            qlIterationsTitle.setAlignment(Qt.AlignCenter)
            
            qleIterations.textChanged.connect(self.IterationsValueChanged)
            qleIterations.setText(str(self.MorphologySettings._iteration))
            
            inputValidator = QIntValidator(1,maxIteration)
            qleIterations.setValidator(inputValidator)
            
            self.addWidget(qlIterationsTitle,layout)
            self.addWidget(qleIterations,layout)
        
        if(self.InputType == MorphologyInput.NoInput):  
            qlEmptyWindow = QLabel()
            qlEmptyWindow.setText("Нет вводимых параметров")
            qlEmptyWindow.setAlignment(Qt.AlignCenter)
            
            self.addWidget(qlEmptyWindow,layout)
        
        self.setGeometry(_left, _top, _heigt, _width)
        self.setWindowTitle(self.MorphologySettings.OperationName + 'settings')
        self.show()    
    
    def addWidget(self,widget:QWidget, layout:QLayout):
        layout.addWidget(widget, self.position, 0)
        self.position+=1 
    
    def XDimValueChanged(self,text):
        self.MorphologySettings._matrixHeight = int(text)
    
    def YDimValueChanged(self,text):
        self.MorphologySettings._matrixWidth = int(text)
                                           
    def IterationsValueChanged(self,text):
        self.MorphologySettings._iteration = int(text)                                       
                        

class MorphAlgWindow(QDialog):
    def __init__(self, morphology:MorphologyData, parent=None):
        super(MorphAlgWindow, self).__init__(parent)
        
        _heigt = 200
        _width = 200
        _left = 100
        _top = 100
        
        self.Morphology = morphology
        self.initUI(_heigt, _width, _left, _top)
        
    def initUI(self, _heigt, _width, _left, _top):

        layout = QGridLayout()
        self.layout = layout
        self.setLayout(layout)
        
        self.position = 0
                
        for alg in MorphologyAlg._operations.keys():
            radiobutton = QRadioButton(alg)
            
            if(alg==self.Morphology.OperationName):
                radiobutton.setChecked(True)      

            radiobutton.algValue = alg
            radiobutton.toggled.connect(self.on_radio_button_toggled)
            self.addWidget(radiobutton,layout)
                    
        
        qbSettings = QPushButton("Settings",self)
        qbSettings.clicked.connect(self.settingsClicked)
        self.switchButtonEnabled(qbSettings)
        
        self.addWidget(qbSettings,layout)
        
        self.setGeometry(_left, _top, _heigt, _width)
        self.setWindowTitle('Binary Algorithm selection')
        self.show()
    
    def on_radio_button_toggled(self):        
        radiobutton = self.sender()
        
        if(not radiobutton.isChecked()):
            return

        self.Morphology.OperationName = radiobutton.algValue        
        print("Selected Morphology Algorithm is %s" % (self.Morphology.OperationName))
        
        settButton = self.getSettingsButton()
        self.switchButtonEnabled(settButton)
    
    def getSettingsButton(self):
        return self.layout.itemAt(self.position-1).widget()    
         
    def addWidget(self,widget:QWidget, layout:QLayout):
        layout.addWidget(widget, self.position, 0)
        self.position+=1 

    def switchButtonEnabled(self, button:QPushButton):
        IsButtonEnabled = self.Morphology.GetGUIInputType() != MorphologyInput.NoInput
        print(IsButtonEnabled)
        button.setEnabled(IsButtonEnabled)

    def settingsClicked(self):
        inputType = self.Morphology.GetGUIInputType()

        widget = MorpSettingsWindow(self.Morphology,inputType)
        widget.exec_()
        
        self.Morphology = widget.MorphologySettings
        self.statusBar().showMessage('MorphologySettings' + ' selected')
        
        
class OperationListWindow(QDialog):
    def __init__(self, operationStack:OperationStack, parent=None):
        super(OperationListWindow, self).__init__(parent)
        
        _heigt = 200
        _width = 200
        _left = 100
        _top = 100
        
        self.operationStack = operationStack
        self.initUI(_heigt, _width, _left, _top)

        
    def initUI(self, _heigt, _width, _left, _top):
        
        layout = QGridLayout()
        self.setLayout(layout)
        
        listWidget = QListWidget(self)
        
        descriptions = self.operationStack.GetOperationsDescription()
        listWidget.addItems(descriptions)          

        layout.addWidget(listWidget, 0, 0)       
        
        self.setGeometry(_left, _top, _heigt, _width)
        self.setWindowTitle('Operations list')
        self.show()
    
    def on_radio_button_toggled(self):
        radiobutton = self.sender()
        if (not radiobutton.isChecked()):
            return 
        
        self.binaryData.OperationName = radiobutton.algValue
        print("Selected Binary Algorithm is %s" % (radiobutton.algValue))        
        
class Example(QMainWindow):

    BIN_FILE_MARK = 'BIN'
    AVAILABLE_PICTURE_EXTENSHIONS = ['.png','.jpg']
    
    def __init__(self):
        super().__init__()
        
        self.PICTURE_WINDOW_HEIGHT= 600
        self.PICTURE_WINDOW_WIDTH = 600
        
        _heigt = 1024
        _width = 768
        _left = 10
        _top = 10
        self.initUI(_heigt, _width, _left, _top)

    def initUI(self, _heigt, _width, _left, _top):
        self.PreviousFolder = "";
        
        self.binarizator = Binarizator()
        
        #-----------------------------------------
        openFile = QAction('Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open picture')
        openFile.triggered.connect(self.openFileClick)

        selectBinaryAlgorithm = QAction('Binary', self)
        #openFile.setShortcut('Ctrl+S')
        selectBinaryAlgorithm.setStatusTip('Select BinaryAlgorithm')
        selectBinaryAlgorithm.triggered.connect(self.selectBinaryAlgorithmClick)
        
        selectMorphologyAlgorithm = QAction('Morphology', self)
        #openFile.setShortcut('Ctrl+S')
        selectMorphologyAlgorithm.setStatusTip('Select MorphologyAlgorithm')
        selectMorphologyAlgorithm.triggered.connect(self.selectMorphologyAlgorithmClick)

        applyBatchOperations = QAction('Apply', self)
        #openFile.setShortcut('Ctrl+S')
        applyBatchOperations.setStatusTip('Apply list of batch operations for all other pictures in current image folder')
        applyBatchOperations.triggered.connect(self.toApplyBatchOperations)
        
        openApplyedOperationsList = QAction('List', self)
        #openFile.setShortcut('Ctrl+S')
        openApplyedOperationsList.setStatusTip('Display list of used operations for current image')
        openApplyedOperationsList.triggered.connect(self.displayListOfOperations)

        #-----------------------------------------
        menubar = self.menuBar()
        
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)

        AlgMenu = menubar.addMenu('&Algoritm')
        AlgMenu.addAction(selectBinaryAlgorithm)
        AlgMenu.addAction(selectMorphologyAlgorithm)
        
        BatchOpMenu = menubar.addMenu('&Batch Operations')
        BatchOpMenu.addAction(applyBatchOperations)
        BatchOpMenu.addAction(openApplyedOperationsList)
        
        #------------------------------------------
        choosedPath = QTextEdit(self)
        #choosedPathLab.move()
        choosedPath.setGeometry(60, 50, 200,30)
        choosedPath.setReadOnly(True)
        choosedPath.setText("empty")
        self.choosedPath = choosedPath
        
        pathDescrp = QTextEdit(self)
        #choosedPathLab.move()
        pathDescrp.setGeometry(0, 50, 50,30)
        pathDescrp.setReadOnly(True)
        pathDescrp.setText("File:")
        self.pathDescrp = pathDescrp
        
        self.pictureLabel = QLabel(self)
        self.pictureLabel.setGeometry(100,100,self.PICTURE_WINDOW_HEIGHT,self.PICTURE_WINDOW_WIDTH)
        self.printImage()

        self.statusBar()
        self.setGeometry(_left, _top, _heigt, _width)
        self.setWindowTitle('EasyBin')
        self.show()

    def printImage(self):      
        
        if not self.binarizator.NeedReCompute:
            return
        
        image = self.binarizator.getImage()
        self.saveImageToFile(image)
        pixmap = QtGui.QPixmap(image)
        pixmap = pixmap.scaled(self.PICTURE_WINDOW_HEIGHT, self.PICTURE_WINDOW_WIDTH, QtCore.Qt.KeepAspectRatio)

        self.pictureLabel.setPixmap(pixmap)

    
    def applyBinarizatorChanges(self):
        self.printImage()
        
    def saveImageToFile(self, image):
        SAVE_FORMAT = 'png'
        
        if(not self.binarizator.PathToFile):
            return
        
        newFileName = os.path.splitext(self.fileDialog.filename[1])[0]+self.BIN_FILE_MARK+'.'+SAVE_FORMAT
             
        print()
        savePath = self.fileDialog.filename[0] +'/'+ newFileName
        savePath = os.path.normpath(savePath)
        print(savePath)

        image.save(savePath, SAVE_FORMAT)
    
    @staticmethod
    def SaveImageToFile(image, folderPath, pathToFile):
        
        SAVE_FORMAT = 'png'
        
        if(not pathToFile):
            return

        newFileName = os.path.splitext(pathToFile)[0]+Example.BIN_FILE_MARK+'.'+SAVE_FORMAT
             
        print('new file name - ' + newFileName)
        
        print('folder path - ' + folderPath)
        savePath = os.path.join(folderPath, newFileName)
        
        print('save path - ' + savePath)

        image.save(savePath, SAVE_FORMAT)
    
    
    def openFileClick(self):  
        self.fileDialog = Dialog(self)
        
        self.fileDialog.filters = ['Raster image (*.bmp)', 'Images (*{} *{})'.format(self.AVAILABLE_PICTURE_EXTENSHIONS[0], self.AVAILABLE_PICTURE_EXTENSHIONS[1])]
       
        self.fileDialog.default_filter_index = 1
        
        if not self.PreviousFolder:
            self.fileDialog.directory = self.PreviousFolder
            
        self.fileDialog.exec()
        
        self.binarizator.PathToFile = self.fileDialog.path
        self.applyBinarizatorChanges()
        
        self.PreviousFolder = self.fileDialog.directory
        self.choosedPath.setText(self.binarizator.PathToFile)
        self.statusBar().showMessage(self.binarizator.PathToFile + ' selected')
    
    def selectBinaryAlgorithmClick(self):  
        sender = self.sender()

        if not self.binarizator.IsReadyToWork():
            return

        widget = BinAlgWindow(deepcopy(self.binarizator.BinSettings))
        widget.exec_()
        
        self.binarizator.BinSettings = widget.binaryData
        self.applyBinarizatorChanges()
        self.statusBar().showMessage('BinaryAlgorithm' +self.binarizator.BinSettings.OperationName +' selected')
   
    def selectMorphologyAlgorithmClick(self):  
        sender = self.sender()

        if not self.binarizator.IsReadyToWork():
            return 

        widget = MorphAlgWindow(deepcopy(self.binarizator.CleanedMorhpSettings))
        widget.exec_()
        
        self.binarizator.MorhpSettings = widget.Morphology
        self.applyBinarizatorChanges()
        
        self.statusBar().showMessage('MorphologyAlgorithm' + self.binarizator.MorhpSettings.OperationName+' selected')
       
    def toApplyBatchOperations(self):  
        sender = self.sender()
        
        if not self.binarizator.IsReadyToWork():
            return
        
        self.binarizator.OpStack.ApplyOperationsToFolder(self.binarizator.PathToFile)
        
    def displayListOfOperations(self):  
        sender = self.sender()
        
        if not self.binarizator.IsReadyToWork():
            return
        
        widget = OperationListWindow(self.binarizator.OpStack)
        widget.exec_()
        
class Dialog():

    def __init__(self, mainform):
        self.__mainform = mainform
        self.__dialog = QFileDialog()
        self.__directory = ''
        self.__filename = ['', '', '']
        self.__filters = []
        self.__default_filter_index = 0
        self.__path = ''

    @property
    def path(self):
        return self.__path

    @property
    def filename(self):
        return self.__filename

    @property
    def directory(self):
        return self.__directory

    @directory.setter
    def directory(self, value):
        self.__directory = value

    @property
    def filters(self):
        return self.__filters

    @filters.setter
    def filters(self, value):
        self.__filters = value

    @property
    def default_filter_index(self):
        return self.__default_filter_index

    @default_filter_index.setter
    def default_filter_index(self, value):
        self.__default_filter_index = value

    def exec(self, load =True):
        self.__dialog.setNameFilters(self.__filters)
        self.__dialog.selectNameFilter(self.__filters[self.__default_filter_index])
        self.__dialog.setDirectory(self.__directory)
        
        if load == True:
            self.__dialog.setLabelText(QFileDialog.Accept, 'Yes')
            self.__dialog.setWindowTitle('Yes')
        else:
            self.__dialog.setLabelText(QFileDialog.Accept, 'Save as')
            self.__dialog.setWindowTitle('Save as')
            
        if self.__dialog.exec() == QDialog.Accepted:
            self.__path = self.__dialog.selectedFiles()[0]
            fn = os.path.split(self.__path)
            ex = os.path.splitext(self.__path)[1]
            self.__filename = [fn[0], fn[1], ex[1:len(ex)]] 
            print(self.__filename)
            print(os.pathsep)

            
if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        ex = Example()
        sys.exit(app.exec_())
    except Exception as e:
        print(e.__doc__)