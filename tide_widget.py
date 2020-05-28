#!/usr/bin/python3

import sys
from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QTextBrowser, QLineEdit, QFileDialog, QAction,
							 QGridLayout, QFormLayout, QHBoxLayout, QVBoxLayout, QComboBox, QLabel,
							 QRadioButton, QPushButton, QCalendarWidget, QDoubleSpinBox, QSpinBox)
from PyQt5.QtGui import QIcon
# from tdr_py.vp_tide import v_merge, v_dirmerge
import pandas as pd
import numpy as np
from ttide import t_tide, t_utils
from utide import solve, reconstruct
from matplotlib.dates import date2num
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()



class TideWidget(QWidget):

	def __init__(self):
		super().__init__()

		self.initUI()


	def initUI(self):

		self.setGeometry(300, 100, 480, 640)
		self.setWindowTitle('Tide')
		self.setWindowIcon(QIcon('wave-pngrepo-com.png'))

		fileLocButton = QPushButton('Open File Location')
		fileLocButton.clicked.connect(self.inputPathDialog)
		plotObsButton = QPushButton('Plot Observation Data')
		plotObsButton.clicked.connect(self.plotLoad)
		self.locLineForm = QLineEdit()

		timeHeaderLabel = QLabel('Time Header:')
		self.timeHeaderLineForm = QLineEdit()

		depthHeaderLabel = QLabel('Depth Header:')
		self.depthHeaderLineForm = QLineEdit()

		dayFirstLabel = QLabel('Day First:')
		self.dayFirstCB = QComboBox()
		self.dayFirstCB.addItems(['True', 'False'])

		sepLabel = QLabel('Separator:')
		self.sepCB = QComboBox()
		self.sepCB.addItems(['Tab', 'Space', 'Semicolon'])

		self.dataFrame = QTextBrowser()
		vploadButton = QPushButton('Load Valeport Data')
		plotButton = QPushButton('Plot Loaded Data')

		self.methodLabel = QLabel()
		self.methodLabel.setAlignment(Qt.AlignRight)
		tideAnalysisLabel = QLabel()
		tideAnalysisLabel.setText('Tidal Analysis Method')
		tideAnalysisLabel.setAlignment(Qt.AlignLeft)
		self.ttideButton = QRadioButton('T Tide')
		self.ttideButton.toggled.connect(self.methodButton)
		self.utideButton = QRadioButton('U Tide')
		self.utideButton.toggled.connect(self.methodButton)
		self.utideButton.setChecked(True)

		latLabel = QLabel('Latitude (dd.ddddd):')
		self.latDSB = QDoubleSpinBox()
		self.latDSB.setRange(-90.0, 90.0)
		self.latDSB.setDecimals(5)

		self.saveLocLineForm = QLineEdit()
		saveLocButton = QPushButton('Save File Location')
		saveLocButton.clicked.connect(self.savePathDialog)

		startcalLabel = QLabel('Start Date')
		startcalLabel.setAlignment(Qt.AlignHCenter)
		self.startcal = QCalendarWidget()

		endcalLabel = QLabel('End Date')
		endcalLabel.setAlignment(Qt.AlignHCenter)
		self.endcal = QCalendarWidget()

		freqLabel = QLabel('Time Interval:')
		self.freqSB = QSpinBox()
		self.freqUnitCB = QComboBox()
		self.freqUnitCB.addItems(['hours', 'minutes'])

		solveButton = QPushButton('Analyse Tide')
		solveButton.clicked.connect(self.analyse)
		predicButton = QPushButton('Predict Tide')
		predicButton.clicked.connect(self.predict)


		# plotButton.clicked.connect(self.plotLoad(dfRaw))



		aboutButton = QPushButton('About')

		grid = QGridLayout()
		vbox = QVBoxLayout()
		
		grid.addWidget(fileLocButton, 1, 1, 1, 1)
		grid.addWidget(self.locLineForm, 1, 2, 1, 2)
		grid.addWidget(plotObsButton, 1, 4, 1, 1)
		grid.addWidget(timeHeaderLabel, 2, 1, 1, 1)
		grid.addWidget(self.timeHeaderLineForm, 2, 2, 1, 1)
		grid.addWidget(depthHeaderLabel, 2, 3, 1, 1)
		grid.addWidget(self.depthHeaderLineForm, 2, 4, 1, 1)
		grid.addWidget(dayFirstLabel, 3, 1, 1, 1)
		grid.addWidget(self.dayFirstCB, 3, 2, 1, 1)
		grid.addWidget(sepLabel, 3, 3, 1, 1)
		grid.addWidget(self.sepCB, 3, 4, 1, 1)
		grid.addWidget(self.dataFrame, 4, 1, 4, 4)
		grid.addWidget(self.methodLabel, 8, 1, 1, 2)
		grid.addWidget(tideAnalysisLabel, 8, 3, 1, 2)
		grid.addWidget(self.ttideButton, 9, 1, 1, 2)
		grid.addWidget(self.utideButton, 9, 3, 1, 2)
		grid.addWidget(latLabel, 10, 1, 1, 1)
		grid.addWidget(self.latDSB, 10, 2, 1, 1)
		grid.addWidget(saveLocButton, 10, 3, 1, 1)
		grid.addWidget(self.saveLocLineForm, 10, 4, 1, 1)
		grid.addWidget(startcalLabel, 11, 1, 1, 2)
		grid.addWidget(endcalLabel, 11, 3, 1, 2)
		grid.addWidget(self.startcal, 12, 1, 1, 2)
		grid.addWidget(self.endcal, 12, 3, 1, 2)
		grid.addWidget(freqLabel, 13, 1, 1, 1)
		grid.addWidget(self.freqSB, 13, 2, 1, 2)
		grid.addWidget(self.freqUnitCB, 13, 4, 1, 1)
		grid.addWidget(solveButton, 14, 1, 1, 2)
		grid.addWidget(predicButton, 14, 3, 1, 2)


		vbox.addStretch(1)
		grid.addLayout(vbox, 20, 1)
		self.setLayout(grid)


	def inputPathDialog(self):

		home_dir = str(Path.home())
		fname = QFileDialog.getOpenFileName(self, 'Load file', home_dir)
		filePath = str(Path(fname[0]))
		self.locLineForm.setText(filePath)
		# raw = self.convertLoad(filePath)

		if fname[0]:
			f = open(fname[0], 'r')

			with f:
				data = f.read()
				self.dataFrame.setText(data)


	def savePathDialog(self):

		home_dir = str(Path.home())
		fname = QFileDialog.getSaveFileName(self, 'Save File', home_dir, "Text files (*.txt)")
		filePath = (str(Path(fname[0])))
		self.saveLocLineForm.setText(filePath)


	def str2bool(self, v):
		
		return v in ('True')


	def inputDict(self):

		location = self.locLineForm.text()
		time = self.timeHeaderLineForm.text()
		depth = self.depthHeaderLineForm.text()
		dayF = self.str2bool(self.dayFirstCB.currentText())
		sepDict = {'Tab':'\t', 'Space':' ', 'Semicolon':';'}
		sepSelect = sepDict[self.sepCB.currentText()]

		raw = pd.read_csv(location, sep=sepSelect, index_col=time)
		raw.index = pd.to_datetime(raw.index, dayfirst=dayF)

		depth_array = raw[depth].values
		time_array = raw.index

		lat = self.latDSB.value()
		if lat == 0.0:
			lat = None
		else:
			lat = self.latDSB.value()

		startcal_string = self.startcal.selectedDate().toString(Qt.ISODate)
		endcal_string = self.endcal.selectedDate().toString(Qt.ISODate)

		freq_unit_dict = {'hours':'H', 'minutes':'min'}
		freq_unit_value = freq_unit_dict[self.freqUnitCB.currentText()]
		frequency = str(self.freqSB.value()) + freq_unit_value

		time_predic = pd.date_range(start=startcal_string, end=endcal_string, freq=frequency)

		input_dict = {'depth':depth_array, 'time':time_array, 'latitude':lat, 'predicted time':time_predic}

		return input_dict


	def plotLoad(self):

		input_dict = self.inputDict()

		ad = input_dict['depth']
		at = input_dict['time']

		plt.figure(figsize=(10, 5))
		plt.plot(at, ad, label='Tide Observation Data')
		plt.xlabel('Time')
		plt.ylabel('Water Level')
		plt.legend(loc='best')
		plt.show()


	def methodButton(self):

		method_button = self.sender()
		if method_button.isChecked():
			self.methodLabel.setText(method_button.text())


	def analyse(self):

		method_dict = {'T Tide':self.ttide, 'U Tide':self.utide}
		method = self.methodLabel.text()
		method_dict[method]()


	def predict(self):

		method_dict = {'T Tide':self.ttide, 'U Tide':self.utide}
		method = self.methodLabel.text()
		result = method_dict[method]()
		prediction_dict = result['prediction']
		water_level = prediction_dict['h']
		print(water_level)

	def ttide(self):

		input_dict = self.inputDict()
		ad = input_dict['depth']
		at = input_dict['time']
		latitude = input_dict['latitude']
		time_diff = np.timedelta64(at[1]-at[0], 'm').astype('float64') / 60
		# demeaned_ad = ad - np.nanmean(ad)
		time_num = date2num(at.to_pydatetime())

		time_predic = input_dict['predicted time']
		time_predic_num = date2num(time_predic.to_pydatetime())

		coef = t_tide(ad, dt=time_diff, stime=time_num[0], lat=latitude, synth=0)
		predic = coef(time_predic_num) + np.nanmean(ad)

		output_dict = {'coefficient':coef, 'prediction':predic}

		return output_dict


	def utide(self):

		input_dict = self.inputDict()
		ad = input_dict['depth']
		at = input_dict['time']

		# demeaned_ad = ad - np.nanmean(ad)
		time_num = date2num(at.to_pydatetime())
		latitude = input_dict['latitude']

		time_predic = input_dict['predicted time']
		time_predic_num = date2num(time_predic.to_pydatetime())


		coef = solve(time_num, ad, lat=latitude)
		predic = reconstruct(time_predic_num, coef)

		output_dict = {'coefficient':coef, 'prediction':predic}

		return output_dict

	
	# def methodSelect(self, button):
	# 	if button.text == 'T Tide':


	# def dayFirst(self, i):

	# 	for count in range (self.dayFirstCB.count()):



# class TideAnalysis():


# 	def _init_(self):




def main():

	app = QApplication(sys.argv)
	tide = TideWidget()
	tide.show()
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()
