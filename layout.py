# Form implementation generated from reading ui file '.\AppLayout_splitter.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1112, 985)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.splt_horizontal = QtWidgets.QSplitter(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splt_horizontal.sizePolicy().hasHeightForWidth())
        self.splt_horizontal.setSizePolicy(sizePolicy)
        self.splt_horizontal.setMinimumSize(QtCore.QSize(0, 0))
        self.splt_horizontal.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.splt_horizontal.setObjectName("splt_horizontal")
        self.frame_left = QtWidgets.QFrame(parent=self.splt_horizontal)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_left.sizePolicy().hasHeightForWidth())
        self.frame_left.setSizePolicy(sizePolicy)
        self.frame_left.setMinimumSize(QtCore.QSize(650, 0))
        self.frame_left.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.frame_left.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_left.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.frame_left.setObjectName("frame_left")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_left)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.formLayout_Left = QtWidgets.QFormLayout()
        self.formLayout_Left.setObjectName("formLayout_Left")
        self.label = QtWidgets.QLabel(parent=self.frame_left)
        self.label.setObjectName("label")
        self.formLayout_Left.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label)
        self.cmbAccount = QtWidgets.QComboBox(parent=self.frame_left)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbAccount.sizePolicy().hasHeightForWidth())
        self.cmbAccount.setSizePolicy(sizePolicy)
        self.cmbAccount.setMinimumSize(QtCore.QSize(195, 22))
        self.cmbAccount.setMaximumSize(QtCore.QSize(171, 22))
        self.cmbAccount.setObjectName("cmbAccount")
        self.formLayout_Left.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.cmbAccount)
        self.label_2 = QtWidgets.QLabel(parent=self.frame_left)
        self.label_2.setObjectName("label_2")
        self.formLayout_Left.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_2)
        self.cmbAction = QtWidgets.QComboBox(parent=self.frame_left)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbAction.sizePolicy().hasHeightForWidth())
        self.cmbAction.setSizePolicy(sizePolicy)
        self.cmbAction.setMinimumSize(QtCore.QSize(195, 22))
        self.cmbAction.setMaximumSize(QtCore.QSize(171, 22))
        self.cmbAction.setObjectName("cmbAction")
        self.cmbAction.addItem("")
        self.cmbAction.addItem("")
        self.cmbAction.addItem("")
        self.cmbAction.addItem("")
        self.cmbAction.addItem("")
        self.cmbAction.addItem("")
        self.cmbAction.addItem("")
        self.cmbAction.addItem("")
        self.cmbAction.addItem("")
        self.cmbAction.addItem("")
        self.cmbAction.addItem("")
        self.formLayout_Left.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.cmbAction)
        self.label_3 = QtWidgets.QLabel(parent=self.frame_left)
        self.label_3.setObjectName("label_3")
        self.formLayout_Left.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_3)
        self.ledit_Iteration = QtWidgets.QLineEdit(parent=self.frame_left)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ledit_Iteration.sizePolicy().hasHeightForWidth())
        self.ledit_Iteration.setSizePolicy(sizePolicy)
        self.ledit_Iteration.setMinimumSize(QtCore.QSize(195, 22))
        self.ledit_Iteration.setMaximumSize(QtCore.QSize(171, 22))
        self.ledit_Iteration.setObjectName("ledit_Iteration")
        self.formLayout_Left.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.ledit_Iteration)
        self.horizontalLayout_2.addLayout(self.formLayout_Left)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.btnStoreAccounts = QtWidgets.QPushButton(parent=self.frame_left)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnStoreAccounts.sizePolicy().hasHeightForWidth())
        self.btnStoreAccounts.setSizePolicy(sizePolicy)
        self.btnStoreAccounts.setMinimumSize(QtCore.QSize(21, 21))
        self.btnStoreAccounts.setMaximumSize(QtCore.QSize(21, 21))
        self.btnStoreAccounts.setToolTipDuration(1)
        self.btnStoreAccounts.setObjectName("btnStoreAccounts")
        self.verticalLayout_4.addWidget(self.btnStoreAccounts)
        spacerItem = QtWidgets.QSpacerItem(20, 55, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        self.verticalLayout_4.addItem(spacerItem)
        self.horizontalLayout_2.addLayout(self.verticalLayout_4)
        self.frmLayout_MetaData = QtWidgets.QFormLayout()
        self.frmLayout_MetaData.setObjectName("frmLayout_MetaData")
        self.lblRaiseAmount = QtWidgets.QLabel(parent=self.frame_left)
        self.lblRaiseAmount.setObjectName("lblRaiseAmount")
        self.frmLayout_MetaData.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.lblRaiseAmount)
        self.edtRaiseAmount = QtWidgets.QLineEdit(parent=self.frame_left)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtRaiseAmount.sizePolicy().hasHeightForWidth())
        self.edtRaiseAmount.setSizePolicy(sizePolicy)
        self.edtRaiseAmount.setMinimumSize(QtCore.QSize(171, 22))
        self.edtRaiseAmount.setMaximumSize(QtCore.QSize(171, 22))
        self.edtRaiseAmount.setObjectName("edtRaiseAmount")
        self.frmLayout_MetaData.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.edtRaiseAmount)
        self.lblBuyWithAmount = QtWidgets.QLabel(parent=self.frame_left)
        self.lblBuyWithAmount.setObjectName("lblBuyWithAmount")
        self.frmLayout_MetaData.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.lblBuyWithAmount)
        self.edtBuyWithAmount = QtWidgets.QLineEdit(parent=self.frame_left)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBuyWithAmount.sizePolicy().hasHeightForWidth())
        self.edtBuyWithAmount.setSizePolicy(sizePolicy)
        self.edtBuyWithAmount.setMinimumSize(QtCore.QSize(171, 0))
        self.edtBuyWithAmount.setObjectName("edtBuyWithAmount")
        self.frmLayout_MetaData.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.edtBuyWithAmount)
        self.lblDollarValueToSell = QtWidgets.QLabel(parent=self.frame_left)
        self.lblDollarValueToSell.setObjectName("lblDollarValueToSell")
        self.frmLayout_MetaData.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.lblDollarValueToSell)
        self.edtDollarValueToSell = QtWidgets.QLineEdit(parent=self.frame_left)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtDollarValueToSell.sizePolicy().hasHeightForWidth())
        self.edtDollarValueToSell.setSizePolicy(sizePolicy)
        self.edtDollarValueToSell.setMinimumSize(QtCore.QSize(171, 0))
        self.edtDollarValueToSell.setObjectName("edtDollarValueToSell")
        self.frmLayout_MetaData.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.edtDollarValueToSell)
        self.horizontalLayout_2.addLayout(self.frmLayout_MetaData)
        spacerItem1 = QtWidgets.QSpacerItem(408, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnExecute = QtWidgets.QPushButton(parent=self.frame_left)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnExecute.sizePolicy().hasHeightForWidth())
        self.btnExecute.setSizePolicy(sizePolicy)
        self.btnExecute.setCheckable(False)
        self.btnExecute.setDefault(False)
        self.btnExecute.setObjectName("btnExecute")
        self.horizontalLayout.addWidget(self.btnExecute)
        self.btnClearSelec = QtWidgets.QPushButton(parent=self.frame_left)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnClearSelec.sizePolicy().hasHeightForWidth())
        self.btnClearSelec.setSizePolicy(sizePolicy)
        self.btnClearSelec.setObjectName("btnClearSelec")
        self.horizontalLayout.addWidget(self.btnClearSelec)
        spacerItem2 = QtWidgets.QSpacerItem(200, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.vertical_splitter = QtWidgets.QSplitter(parent=self.frame_left)
        self.vertical_splitter.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.vertical_splitter.setObjectName("vertical_splitter")
        self.tblAssets = QtWidgets.QTableWidget(parent=self.vertical_splitter)
        self.tblAssets.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.SelectedClicked)
        self.tblAssets.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblAssets.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblAssets.setShowGrid(False)
        self.tblAssets.setObjectName("tblAssets")
        self.tblAssets.setColumnCount(0)
        self.tblAssets.setRowCount(0)
        self.lstTerm = QtWidgets.QListWidget(parent=self.vertical_splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lstTerm.sizePolicy().hasHeightForWidth())
        self.lstTerm.setSizePolicy(sizePolicy)
        self.lstTerm.setObjectName("lstTerm")
        self.verticalLayout.addWidget(self.vertical_splitter)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.frame_right = QtWidgets.QFrame(parent=self.splt_horizontal)
        self.frame_right.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_right.sizePolicy().hasHeightForWidth())
        self.frame_right.setSizePolicy(sizePolicy)
        self.frame_right.setMinimumSize(QtCore.QSize(0, 0))
        self.frame_right.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.frame_right.setBaseSize(QtCore.QSize(0, 0))
        self.frame_right.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_right.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.frame_right.setObjectName("frame_right")
        self.gridLayout = QtWidgets.QGridLayout(self.frame_right)
        self.gridLayout.setObjectName("gridLayout")
        self.grdGraph = QtWidgets.QGridLayout()
        self.grdGraph.setObjectName("grdGraph")
        self.gridLayout.addLayout(self.grdGraph, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.splt_horizontal, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1112, 22))
        self.menuBar.setObjectName("menuBar")
        self.menuFile = QtWidgets.QMenu(parent=self.menuBar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menuBar)
        self.statusBar = QtWidgets.QStatusBar(parent=MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.statusBar.sizePolicy().hasHeightForWidth())
        self.statusBar.setSizePolicy(sizePolicy)
        self.statusBar.setSizeGripEnabled(False)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.toolBar = QtWidgets.QToolBar(parent=MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, self.toolBar)
        self.action_Exit = QtGui.QAction(parent=MainWindow)
        self.action_Exit.setMenuRole(QtGui.QAction.MenuRole.QuitRole)
        self.action_Exit.setObjectName("action_Exit")
        self.actionCredentials_File = QtGui.QAction(parent=MainWindow)
        self.actionCredentials_File.setObjectName("actionCredentials_File")
        self.menuFile.addAction(self.actionCredentials_File)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.action_Exit)
        self.menuBar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Account:"))
        self.label_2.setText(_translate("MainWindow", "Action:"))
        self.cmbAction.setItemText(0, _translate("MainWindow", "stock_info"))
        self.cmbAction.setItemText(1, _translate("MainWindow", "sell_gains"))
        self.cmbAction.setItemText(2, _translate("MainWindow", "sell_todays_return"))
        self.cmbAction.setItemText(3, _translate("MainWindow", "sell_selected"))
        self.cmbAction.setItemText(4, _translate("MainWindow", "sell_gains_except_x"))
        self.cmbAction.setItemText(5, _translate("MainWindow", "sell_todays_return_except_x"))
        self.cmbAction.setItemText(6, _translate("MainWindow", "buy_selected"))
        self.cmbAction.setItemText(7, _translate("MainWindow", "buy_selected_with_x"))
        self.cmbAction.setItemText(8, _translate("MainWindow", "buy_lower_with_gains"))
        self.cmbAction.setItemText(9, _translate("MainWindow", "raise_x_sell_y_dollars"))
        self.cmbAction.setItemText(10, _translate("MainWindow", "raise_x_sell_y_dollars_except_z"))
        self.label_3.setText(_translate("MainWindow", "Iteration:"))
        self.ledit_Iteration.setText(_translate("MainWindow", "1"))
        self.btnStoreAccounts.setToolTip(_translate("MainWindow", "Add account(s)"))
        self.btnStoreAccounts.setText(_translate("MainWindow", "..."))
        self.lblRaiseAmount.setText(_translate("MainWindow", "Raise Amount (USB):"))
        self.edtRaiseAmount.setText(_translate("MainWindow", "1"))
        self.lblBuyWithAmount.setText(_translate("MainWindow", "Dollar Value to Buy of Stock:"))
        self.lblDollarValueToSell.setText(_translate("MainWindow", "Dollar Value to Sell:"))
        self.btnExecute.setText(_translate("MainWindow", "Execute ..."))
        self.btnClearSelec.setText(_translate("MainWindow", "Clear Selection"))
        self.tblAssets.setSortingEnabled(True)
        self.menuFile.setTitle(_translate("MainWindow", "&File"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.action_Exit.setText(_translate("MainWindow", "&Exit"))
        self.action_Exit.setIconText(_translate("MainWindow", "Exit"))
        self.actionCredentials_File.setText(_translate("MainWindow", "&Credentials File"))
