# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qgis-project/ui_forms/alternative_geometry_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AltGeomDialog(object):
    def setupUi(self, AltGeomDialog):
        AltGeomDialog.setObjectName("AltGeomDialog")
        AltGeomDialog.resize(461, 162)
        self.gridLayout = QtWidgets.QGridLayout(AltGeomDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.updateAlt2 = QtWidgets.QCheckBox(AltGeomDialog)
        self.updateAlt2.setChecked(True)
        self.updateAlt2.setObjectName("updateAlt2")
        self.gridLayout.addWidget(self.updateAlt2, 2, 0, 1, 1)
        self.updateAlt1 = QtWidgets.QCheckBox(AltGeomDialog)
        self.updateAlt1.setChecked(True)
        self.updateAlt1.setTristate(False)
        self.updateAlt1.setObjectName("updateAlt1")
        self.gridLayout.addWidget(self.updateAlt1, 1, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(AltGeomDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 1)
        self.label = QtWidgets.QLabel(AltGeomDialog)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)

        self.retranslateUi(AltGeomDialog)
        self.buttonBox.accepted.connect(AltGeomDialog.accept)
        self.buttonBox.rejected.connect(AltGeomDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AltGeomDialog)
        AltGeomDialog.setTabOrder(self.updateAlt1, self.updateAlt2)
        AltGeomDialog.setTabOrder(self.updateAlt2, self.buttonBox)

    def retranslateUi(self, AltGeomDialog):
        _translate = QtCore.QCoreApplication.translate
        AltGeomDialog.setWindowTitle(_translate("AltGeomDialog", "Dialog"))
        self.updateAlt2.setText(_translate("AltGeomDialog", "mettre à jour la la géométrie alternative 2 (schématique)"))
        self.updateAlt1.setText(_translate("AltGeomDialog", "mettre à jour la la géométrie alternative 1"))
        self.label.setText(_translate("AltGeomDialog", "Les géométries alternatives de la couche éditée sont différentes de la géométrie principale. Voulez-vous les mettre à jour ?"))
