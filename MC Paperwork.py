#!/usr/bin/python3

import signal
import sys
import re

# This imports the needed PYQT modules for the GUI
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QScrollArea
from PyQt5.QtWidgets import QLabel, QPushButton, QLineEdit
from PyQt5.QtCore import Qt


# Import in the code that implements the actual code
import Paperwork



class PaperworkGUI( QWidget ):

    def __init__( self ):
        super().__init__()
        self.initUI()

    def initUI( self ):
        self.setWindowTitle('MC VersionOne Paperwork Checker')
        self.setWindowIcon( QIcon('icon.jpg') )

        # Now setup for project 1
        vbox = QVBoxLayout()
        self.setLayout( vbox )
        self.scroll = QScrollArea()
        self.input_n = QLineEdit('')
        self.input_n.setMinimumSize(300, 100)
        self.button    = QPushButton('Check Paperwork')
        self.label = QLabel("<i>Enter in story/defect numbers delimited by commas to check paperwork</i>")
        self.label.setWordWrap(True)
        self.label.setFixedWidth(500)
        self.label.setAlignment(Qt.AlignTop)


        # N
        h = QHBoxLayout()
        h.addWidget( QLabel( 'Story/Defect Numbers: ' ) )
        h.addWidget( self.input_n )
        vbox.addLayout(h)

        # Test
        h = QHBoxLayout()
        h.addStretch(1)
        h.addWidget( self.button )
        vbox.addLayout(h)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setMaximumHeight(500)
        scroll.setMinimumHeight(200)
        content = QWidget()
        scroll.setWidget(self.label)
        lay = QVBoxLayout()
        lay.addWidget(scroll)
        # label = QLabel("TEST")
        self.label.setWordWrap(True)
        vbox.addLayout(lay)





        # When the Test button is clicked, call testClicked()
        self.button.clicked.connect(self.testClicked)
        self.input_n.returnPressed.connect(self.testClicked)
        self.show()

#
# This is the method connected to the Test Button.  It calls the actual primality test code
# (which you will implement) from the "fermat.py" file.
#
    def testClicked( self ):
        try:
            assets = self.input_n.text().split(',')
            multiple = False
            if len(assets) > 1:
                multiple = True
            finalOutput = ''
            for asset in assets:
                asset = asset.strip()
                if len(asset) == 0:
                    return
                assetType = asset[0]


                if assetType == 'D' or assetType == 'd':
                    # Check correct defect format
                    if re.match("D-\d{5}$",asset) is None:
                        finalOutput += '<b>Invalid Defect Number:</b><i>' + asset + '</i>'
                    else:
                        finalOutput += Paperwork.getPaperwork(asset, 'Defect')

                elif assetType == 'S' or assetType == 's':
                    # Check Story formats
                    if re.match("S-\d{5}$",asset) is None:
                        finalOutput += '<b>Invalid Story Number:</b>' + '<i>' + asset + '</i>'
                    else:
                        finalOutput += Paperwork.getPaperwork(asset, 'Story')

                else:
                    self.label.setText('<b>Error occurred, please check your story/defect number:</b> <i>' + asset + '</i>')
                    return

                if multiple:
                    finalOutput += "<hr><br/>"


            self.label.setText(finalOutput)

        # If inputs not valid, display an error
        except Exception as e:
            self.label.setText('<i>ERROR:</i> ' + str(e) )




if __name__ == '__main__':
    # This line allows CNTL-C in the terminal to kill the program
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    w = PaperworkGUI()
    sys.exit(app.exec())
