#!/usr/bin/python3

import sys
from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QTextBrowser, QLineEdit, QFileDialog, QAction,
							 QGridLayout, QFormLayout, QHBoxLayout, QVBoxLayout, QComboBox, QLabel,
							 QRadioButton, QPushButton, QCalendarWidget, QDoubleSpinBox, QSpinBox,
                             QAbstractSpinBox, QDialog)
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
		super(TideWidget, self).__init__()

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
		self.sepCB.addItems(['Tab', 'Comma', 'Space', 'Semicolon'])

		self.dataFrame = QTextBrowser()

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
		self.latDSB.setDecimals(6)
		# self.latDSB.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)

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


		# vploadButton = QPushButton('Load Valeport Data')
		howToButton = QPushButton('How To Use')
		howToButton.clicked.connect(self.howToDialog)
		aboutButton = QPushButton('About')
		aboutButton.clicked.connect(self.aboutDialog)

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
		grid.addWidget(howToButton, 21, 1, 1, 2)
		grid.addWidget(aboutButton, 21, 3, 1, 2)
		self.setLayout(grid)


	def inputPathDialog(self):

		home_dir = str(Path.home())
		fname = QFileDialog.getOpenFileName(self, 'Load file', home_dir)
		filePath = str(Path(fname[0]))
		self.locLineForm.setText(filePath)

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
		sepDict = {'Tab':'\t', 'Comma':',', 'Space':' ', 'Semicolon':';'}
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

		save_file = self.saveLocLineForm.text()

		input_dict = {'depth':depth_array, 'time':time_array, 'latitude':lat, 'predicted time':time_predic, 'save':save_file}

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


	def plotPredic(self, water_level):

		input_dict = self.inputDict()

		ad = water_level
		at = input_dict['predicted time']
		data_label = 'Predicted Data using ' + self.methodLabel.text()

		plt.figure(figsize=(10, 5))
		plt.plot(at, ad, label=data_label)
		plt.xlabel('Time')
		plt.ylabel('Water Level')
		plt.legend(loc='best')
		plt.show()


	def methodButton(self):

		method_button = self.sender()
		if method_button.isChecked():
			self.methodLabel.setText(method_button.text())


	def analyse(self):

		input_dict = self.inputDict()
		save_file = input_dict['save']

		method_dict = {'T Tide':self.ttide, 'U Tide':self.utide}
		method = self.methodLabel.text()
		result = method_dict[method]()
		coef_dict = result['coefficient']

		method = method.replace(' ', '-')
		text_edit = '_' + method + '_report.txt'
		save_file = save_file.replace('.txt', text_edit)

		if method == 'T Tide':
			print_coef = t_utils.pandas_style(coef_dict)
			report = open(save_file, 'w')
			report.write(print_coef)
		elif method == 'U Tide':
			init_print = pd.DataFrame((coef_dict.diagn), index=coef_dict.diagn['name'])


	def predict(self):

		input_dict = self.inputDict()
		save_file = input_dict['save']

		method_dict = {'T Tide':self.ttide, 'U Tide':self.utide}
		method = self.methodLabel.text()
		result = method_dict[method]()

		time = input_dict['predicted time']
		prediction_dict = result['prediction']
		
		if method == 'T Tide':
			water_level = prediction_dict
		elif method == 'U Tide':
			water_level = prediction_dict['h']

		method = method.replace(' ', '-')
		text_edit = '_' + method + '.txt'
		save_file = save_file.replace('.txt', text_edit)

		predic_out = pd.DataFrame({'Depth':water_level,'Time':time})
		predic_out.index = predic_out['Time']
		predic_out = predic_out.iloc[:, 0:1]

		predic_out.to_csv(save_file, sep='\t')

		self.plotPredic(water_level)


	def ttide(self):

		input_dict = self.inputDict()
		ad = input_dict['depth']
		at = input_dict['time']
		latitude = input_dict['latitude']
		time_diff = np.timedelta64(at[1]-at[0], 'm').astype('float64') / 60
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

		time_num = date2num(at.to_pydatetime())
		latitude = input_dict['latitude']

		time_predic = input_dict['predicted time']
		time_predic_num = date2num(time_predic.to_pydatetime())

		coef = solve(time_num, ad, lat=latitude)
		predic = reconstruct(time_predic_num, coef, min_SNR=0)

		output_dict = {'coefficient':coef, 'prediction':predic}

		return output_dict


	def howToDialog(self):

		howTo = QDialog()
		howTo.setWindowTitle('How to Use')
		closeButton = QPushButton("Close")
		closeButton.clicked.connect(howTo.close)

		how_to_use = open('how_to_use.txt', 'r')
		howToLabel = QLabel('The details of how to use this tide analysis GUI is as follows:')
		howToTextBrowser = QTextBrowser()
		howToTextBrowser.setText(how_to_use.read())

		grid = QGridLayout()
		grid.addWidget(howToLabel, 1, 1, 1, 4)
		grid.addWidget(howToTextBrowser, 2, 1, 50, 4)
		grid.addWidget(closeButton, 52, 4, 1, 1)
		howTo.setLayout(grid)

		howTo.exec_()


	def aboutDialog(self):

		# about = QMessageBox()
		about = QDialog()
		about.setWindowTitle('About')
		closeButton = QPushButton("Close")
		closeButton.clicked.connect(about.close)
		# about.setText('This is a tidal analysis GUI using T Tide and U Tide (both Python version)')

		aboutText = '''<body>
		This is a tidal analysis GUI using T Tide and U Tide (both Python version).
		<br><\br><br><\br>
		The GUI itself was developed by 
		<a href=\'https://github.com/rifqiharrys/tide_pyqt5'>Rifqi Muhammad Harrys</a> 
		using PyQt5, a python GUI library.
		<br><\br><br><\br>
		Both T Tide and U Tide developed by two different entities.
		<br><\br>
		The original versions of <a href=\'https://www.eoas.ubc.ca/~rich/#T_Tide'>T Tide</a> and 
		<a href=\'https://www.mathworks.com/matlabcentral/fileexchange/46523-utide-unified-tidal-analysis-and-prediction-functions?w.mathworks.com'>U Tide</a> 
		are in MATLAB language developed by R. Pawlowicz et. al (T Tide) and Daniel Codiga (U Tide).<br><\br><br><\br>
		The python version of <a href=\'https://github.com/moflaher/ttide_py'>T Tide</a> and 
		<a href=\'https://github.com/wesleybowman/UTide'>U Tide</a> were developed by moflaher (T Tide) and Wesley Bowman (U Tide).
		<br><\br><br><\br>
		A description of the theoretical basis of the analysis and some implementation details 
		of T Tide and U Tide Matlab version can be found in:
		</body>'''

		tideCite = '''
		<cite>R. Pawlowicz, B. Beardsley, and S. Lentz, 
		"Classical tidal harmonic analysis including error estimates in MATLAB using 
		T_TIDE", Computers and Geosciences 28 (2002), 929-937.</cite>
		<br><\br><br><\br>
		<cite>Codiga, Daniel. (2011). Unified tidal analysis and prediction using 
		the UTide Matlab functions. 10.13140/RG.2.1.3761.2008. </cite>
		'''

		aboutLabel1 = QLabel(aboutText)
		aboutLabel1.setWordWrap(True)
		aboutLabel1.setOpenExternalLinks(True)
		aboutLabel2 = QLabel(tideCite)
		aboutLabel2.setTextInteractionFlags(Qt.TextSelectableByMouse)
		aboutLabel2.setWordWrap(True)
		aboutTB = QTextBrowser()
		aboutTB.setText(tideCite)
		grid = QGridLayout()
		grid.addWidget(aboutLabel1, 1, 1, 1, 4)
		grid.addWidget(aboutTB, 2, 1, 1, 4)
		grid.addWidget(closeButton, 3, 4, 1, 1)

		about.setLayout(grid)

		about.exec_()



def main():

	app = QApplication(sys.argv)
	tide = TideWidget()
	tide.show()
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()
