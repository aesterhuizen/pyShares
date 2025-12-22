# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'AppLayout_splitter.ui'
##
## Created by: Qt User Interface Compiler version 6.5.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QFormLayout,
    QFrame, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QLayout, QLineEdit, QListWidget,
    QListWidgetItem, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QSpacerItem, QSplitter,
    QStackedWidget, QStatusBar, QTabWidget, QTableWidget,
    QTableWidgetItem, QToolBar, QVBoxLayout, QWidget)

import modules.resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1221, 788)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.action_Exit = QAction(MainWindow)
        self.action_Exit.setObjectName(u"action_Exit")
        icon = QIcon()
        icon.addFile(u":/res/exit.png", QSize(), QIcon.Normal, QIcon.Off)
        self.action_Exit.setIcon(icon)
        self.action_Exit.setMenuRole(QAction.QuitRole)
        self.actionCredentials_File = QAction(MainWindow)
        self.actionCredentials_File.setObjectName(u"actionCredentials_File")
        icon1 = QIcon()
        icon1.addFile(u":/res/Credentials.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionCredentials_File.setIcon(icon1)
        self.actionBar_plot_Gain_Loss = QAction(MainWindow)
        self.actionBar_plot_Gain_Loss.setObjectName(u"actionBar_plot_Gain_Loss")
        icon2 = QIcon()
        icon2.addFile(u":/res/bar-chart.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionBar_plot_Gain_Loss.setIcon(icon2)
        self.actionBar_plot_Sector_Colors = QAction(MainWindow)
        self.actionBar_plot_Sector_Colors.setObjectName(u"actionBar_plot_Sector_Colors")
        self.actionBar_plot_Sector_Colors.setIcon(icon2)
        self.actionIndividual_plot = QAction(MainWindow)
        self.actionIndividual_plot.setObjectName(u"actionIndividual_plot")
        self.actionIndividual_plot.setIcon(icon2)
        self.actionToggle_Charts = QAction(MainWindow)
        self.actionToggle_Charts.setObjectName(u"actionToggle_Charts")
        self.actionToggle_Charts.setIcon(icon2)
        self.actionRefresh = QAction(MainWindow)
        self.actionRefresh.setObjectName(u"actionRefresh")
        icon3 = QIcon()
        icon3.addFile(u":/res/refresh.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionRefresh.setIcon(icon3)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.splt_horizontal = QSplitter(self.centralwidget)
        self.splt_horizontal.setObjectName(u"splt_horizontal")
        sizePolicy.setHeightForWidth(self.splt_horizontal.sizePolicy().hasHeightForWidth())
        self.splt_horizontal.setSizePolicy(sizePolicy)
        self.splt_horizontal.setMinimumSize(QSize(0, 0))
        self.splt_horizontal.setOrientation(Qt.Horizontal)
        self.frame_left = QFrame(self.splt_horizontal)
        self.frame_left.setObjectName(u"frame_left")
        sizePolicy.setHeightForWidth(self.frame_left.sizePolicy().hasHeightForWidth())
        self.frame_left.setSizePolicy(sizePolicy)
        self.frame_left.setMinimumSize(QSize(300, 0))
        self.frame_left.setMaximumSize(QSize(16777215, 16777215))
        self.frame_left.setFrameShape(QFrame.StyledPanel)
        self.frame_left.setFrameShadow(QFrame.Sunken)
        self.gridLayout_2 = QGridLayout(self.frame_left)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.frame = QFrame(self.frame_left)
        self.frame.setObjectName(u"frame")
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QSize(900, 0))
        self.frame.setFrameShape(QFrame.Box)
        self.frame.setFrameShadow(QFrame.Raised)
        self.frame.setLineWidth(1)
        self.gridLayout_5 = QGridLayout(self.frame)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.formLayout_Left = QFormLayout()
        self.formLayout_Left.setObjectName(u"formLayout_Left")
        self.lblAccount = QLabel(self.frame)
        self.lblAccount.setObjectName(u"lblAccount")

        self.formLayout_Left.setWidget(0, QFormLayout.LabelRole, self.lblAccount)

        self.cmbAccount = QComboBox(self.frame)
        self.cmbAccount.setObjectName(u"cmbAccount")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.cmbAccount.sizePolicy().hasHeightForWidth())
        self.cmbAccount.setSizePolicy(sizePolicy1)
        self.cmbAccount.setMinimumSize(QSize(195, 22))
        self.cmbAccount.setMaximumSize(QSize(171, 22))

        self.formLayout_Left.setWidget(0, QFormLayout.FieldRole, self.cmbAccount)

        self.lblAction = QLabel(self.frame)
        self.lblAction.setObjectName(u"lblAction")

        self.formLayout_Left.setWidget(1, QFormLayout.LabelRole, self.lblAction)

        self.cmbAction = QComboBox(self.frame)
        self.cmbAction.setObjectName(u"cmbAction")
        sizePolicy1.setHeightForWidth(self.cmbAction.sizePolicy().hasHeightForWidth())
        self.cmbAction.setSizePolicy(sizePolicy1)
        self.cmbAction.setMinimumSize(QSize(195, 22))
        self.cmbAction.setMaximumSize(QSize(171, 22))

        self.formLayout_Left.setWidget(1, QFormLayout.FieldRole, self.cmbAction)

        self.lblIteration = QLabel(self.frame)
        self.lblIteration.setObjectName(u"lblIteration")

        self.formLayout_Left.setWidget(2, QFormLayout.LabelRole, self.lblIteration)

        self.ledit_Iteration = QLineEdit(self.frame)
        self.ledit_Iteration.setObjectName(u"ledit_Iteration")
        sizePolicy1.setHeightForWidth(self.ledit_Iteration.sizePolicy().hasHeightForWidth())
        self.ledit_Iteration.setSizePolicy(sizePolicy1)
        self.ledit_Iteration.setMinimumSize(QSize(195, 22))
        self.ledit_Iteration.setMaximumSize(QSize(171, 22))

        self.formLayout_Left.setWidget(2, QFormLayout.FieldRole, self.ledit_Iteration)


        self.gridLayout_5.addLayout(self.formLayout_Left, 0, 0, 1, 1)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.btnStoreAccounts = QPushButton(self.frame)
        self.btnStoreAccounts.setObjectName(u"btnStoreAccounts")
        sizePolicy1.setHeightForWidth(self.btnStoreAccounts.sizePolicy().hasHeightForWidth())
        self.btnStoreAccounts.setSizePolicy(sizePolicy1)
        self.btnStoreAccounts.setMinimumSize(QSize(21, 21))
        self.btnStoreAccounts.setMaximumSize(QSize(21, 21))
        self.btnStoreAccounts.setToolTipDuration(1)

        self.verticalLayout_4.addWidget(self.btnStoreAccounts)

        self.verticalSpacer = QSpacerItem(20, 55, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer)


        self.gridLayout_5.addLayout(self.verticalLayout_4, 0, 1, 1, 1)

        self.stackPage = QStackedWidget(self.frame)
        self.stackPage.setObjectName(u"stackPage")
        self.stackPage.setEnabled(True)
        self.stackPage.setMinimumSize(QSize(400, 102))
        self.AllocationPage = QWidget()
        self.AllocationPage.setObjectName(u"AllocationPage")
        self.layoutWidget = QWidget(self.AllocationPage)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 10, 454, 80))
        self.gridLayout_4 = QGridLayout(self.layoutWidget)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.lblAllocAmount = QLabel(self.layoutWidget)
        self.lblAllocAmount.setObjectName(u"lblAllocAmount")

        self.gridLayout_4.addWidget(self.lblAllocAmount, 0, 0, 1, 1)

        self.edtAllocAmount = QLineEdit(self.layoutWidget)
        self.edtAllocAmount.setObjectName(u"edtAllocAmount")

        self.gridLayout_4.addWidget(self.edtAllocAmount, 0, 1, 1, 1)

        self.lbl_pctpf = QLabel(self.layoutWidget)
        self.lbl_pctpf.setObjectName(u"lbl_pctpf")

        self.gridLayout_4.addWidget(self.lbl_pctpf, 0, 2, 1, 1)

        self.edt_pct_of_portfolio = QLineEdit(self.layoutWidget)
        self.edt_pct_of_portfolio.setObjectName(u"edt_pct_of_portfolio")
        self.edt_pct_of_portfolio.setEnabled(True)

        self.gridLayout_4.addWidget(self.edt_pct_of_portfolio, 0, 3, 1, 1)

        self.lblFromSector = QLabel(self.layoutWidget)
        self.lblFromSector.setObjectName(u"lblFromSector")

        self.gridLayout_4.addWidget(self.lblFromSector, 1, 0, 1, 1)

        self.lblToSector = QLabel(self.layoutWidget)
        self.lblToSector.setObjectName(u"lblToSector")

        self.gridLayout_4.addWidget(self.lblToSector, 2, 0, 1, 1)

        self.cmbFromSector = QComboBox(self.layoutWidget)
        self.cmbFromSector.setObjectName(u"cmbFromSector")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.cmbFromSector.sizePolicy().hasHeightForWidth())
        self.cmbFromSector.setSizePolicy(sizePolicy2)
        self.cmbFromSector.setMinimumSize(QSize(100, 0))
        self.cmbFromSector.setMaximumSize(QSize(150, 16777215))

        self.gridLayout_4.addWidget(self.cmbFromSector, 1, 1, 1, 2)

        self.cmbToSector = QComboBox(self.layoutWidget)
        self.cmbToSector.setObjectName(u"cmbToSector")
        self.cmbToSector.setMinimumSize(QSize(100, 0))
        self.cmbToSector.setMaximumSize(QSize(150, 16777215))

        self.gridLayout_4.addWidget(self.cmbToSector, 2, 1, 1, 2)

        self.lblFromSector_pct = QLabel(self.layoutWidget)
        self.lblFromSector_pct.setObjectName(u"lblFromSector_pct")

        self.gridLayout_4.addWidget(self.lblFromSector_pct, 1, 3, 1, 1)

        self.lblToSector_pct = QLabel(self.layoutWidget)
        self.lblToSector_pct.setObjectName(u"lblToSector_pct")

        self.gridLayout_4.addWidget(self.lblToSector_pct, 2, 3, 1, 1)

        self.stackPage.addWidget(self.AllocationPage)
        self.BuySellExceptPage = QWidget()
        self.BuySellExceptPage.setObjectName(u"BuySellExceptPage")
        self.layoutWidget1 = QWidget(self.BuySellExceptPage)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(9, 23, 343, 82))
        self.gridLayout_7 = QGridLayout(self.layoutWidget1)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.gridLayout_7.setContentsMargins(0, 0, 0, 0)
        self.lblSellAssetExSel = QLabel(self.layoutWidget1)
        self.lblSellAssetExSel.setObjectName(u"lblSellAssetExSel")

        self.gridLayout_7.addWidget(self.lblSellAssetExSel, 0, 0, 1, 1)

        self.edtLstStocksSelected = QLineEdit(self.layoutWidget1)
        self.edtLstStocksSelected.setObjectName(u"edtLstStocksSelected")

        self.gridLayout_7.addWidget(self.edtLstStocksSelected, 0, 1, 1, 1)

        self.lblExceptStocks_in_file = QLabel(self.layoutWidget1)
        self.lblExceptStocks_in_file.setObjectName(u"lblExceptStocks_in_file")

        self.gridLayout_7.addWidget(self.lblExceptStocks_in_file, 1, 0, 1, 1)

        self.edtFileBrowse = QLineEdit(self.layoutWidget1)
        self.edtFileBrowse.setObjectName(u"edtFileBrowse")

        self.gridLayout_7.addWidget(self.edtFileBrowse, 1, 1, 1, 1)

        self.btnBrowse = QPushButton(self.layoutWidget1)
        self.btnBrowse.setObjectName(u"btnBrowse")

        self.gridLayout_7.addWidget(self.btnBrowse, 1, 2, 1, 1)

        self.label_3 = QLabel(self.layoutWidget1)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_7.addWidget(self.label_3, 2, 0, 1, 1)

        self.edtAmountEst = QLineEdit(self.layoutWidget1)
        self.edtAmountEst.setObjectName(u"edtAmountEst")

        self.gridLayout_7.addWidget(self.edtAmountEst, 2, 1, 1, 1)

        self.stackPage.addWidget(self.BuySellExceptPage)
        self.ActionsPage = QWidget()
        self.ActionsPage.setObjectName(u"ActionsPage")
        self.layoutWidget2 = QWidget(self.ActionsPage)
        self.layoutWidget2.setObjectName(u"layoutWidget2")
        self.layoutWidget2.setGeometry(QRect(9, 20, 528, 24))
        self.horizontalLayout_2 = QHBoxLayout(self.layoutWidget2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.lblRaiseAmount = QLabel(self.layoutWidget2)
        self.lblRaiseAmount.setObjectName(u"lblRaiseAmount")

        self.horizontalLayout_2.addWidget(self.lblRaiseAmount)

        self.edtRaiseAmount = QLineEdit(self.layoutWidget2)
        self.edtRaiseAmount.setObjectName(u"edtRaiseAmount")
        sizePolicy1.setHeightForWidth(self.edtRaiseAmount.sizePolicy().hasHeightForWidth())
        self.edtRaiseAmount.setSizePolicy(sizePolicy1)
        self.edtRaiseAmount.setMinimumSize(QSize(171, 22))
        self.edtRaiseAmount.setMaximumSize(QSize(171, 22))

        self.horizontalLayout_2.addWidget(self.edtRaiseAmount)

        self.lblbuyWith = QLabel(self.layoutWidget2)
        self.lblbuyWith.setObjectName(u"lblbuyWith")

        self.horizontalLayout_2.addWidget(self.lblbuyWith)

        self.edtBuyWith = QLineEdit(self.layoutWidget2)
        self.edtBuyWith.setObjectName(u"edtBuyWith")
        sizePolicy1.setHeightForWidth(self.edtBuyWith.sizePolicy().hasHeightForWidth())
        self.edtBuyWith.setSizePolicy(sizePolicy1)
        self.edtBuyWith.setMinimumSize(QSize(171, 22))
        self.edtBuyWith.setMaximumSize(QSize(171, 22))
        self.edtBuyWith.setToolTipDuration(-1)

        self.horizontalLayout_2.addWidget(self.edtBuyWith)

        self.horizontalSpacer_4 = QSpacerItem(28, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_4)

        self.layoutWidget3 = QWidget(self.ActionsPage)
        self.layoutWidget3.setObjectName(u"layoutWidget3")
        self.layoutWidget3.setGeometry(QRect(10, 51, 491, 24))
        self.horizontalLayout_3 = QHBoxLayout(self.layoutWidget3)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.lblBuyWithAmount = QLabel(self.layoutWidget3)
        self.lblBuyWithAmount.setObjectName(u"lblBuyWithAmount")

        self.horizontalLayout_3.addWidget(self.lblBuyWithAmount)

        self.edtBuyWithAmount = QLineEdit(self.layoutWidget3)
        self.edtBuyWithAmount.setObjectName(u"edtBuyWithAmount")
        sizePolicy1.setHeightForWidth(self.edtBuyWithAmount.sizePolicy().hasHeightForWidth())
        self.edtBuyWithAmount.setSizePolicy(sizePolicy1)
        self.edtBuyWithAmount.setMinimumSize(QSize(171, 0))

        self.horizontalLayout_3.addWidget(self.edtBuyWithAmount)

        self.horizontalSpacer_2 = QSpacerItem(158, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.layoutWidget4 = QWidget(self.ActionsPage)
        self.layoutWidget4.setObjectName(u"layoutWidget4")
        self.layoutWidget4.setGeometry(QRect(10, 81, 539, 24))
        self.horizontalLayout_4 = QHBoxLayout(self.layoutWidget4)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.lblDollarValueToSell = QLabel(self.layoutWidget4)
        self.lblDollarValueToSell.setObjectName(u"lblDollarValueToSell")

        self.horizontalLayout_4.addWidget(self.lblDollarValueToSell)

        self.edtDollarValueToSell = QLineEdit(self.layoutWidget4)
        self.edtDollarValueToSell.setObjectName(u"edtDollarValueToSell")
        sizePolicy1.setHeightForWidth(self.edtDollarValueToSell.sizePolicy().hasHeightForWidth())
        self.edtDollarValueToSell.setSizePolicy(sizePolicy1)
        self.edtDollarValueToSell.setMinimumSize(QSize(171, 0))

        self.horizontalLayout_4.addWidget(self.edtDollarValueToSell)

        self.cmbDollarShare = QComboBox(self.layoutWidget4)
        self.cmbDollarShare.setObjectName(u"cmbDollarShare")
        self.cmbDollarShare.setMinimumSize(QSize(90, 0))
        self.cmbDollarShare.setBaseSize(QSize(0, 0))
        self.cmbDollarShare.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.horizontalLayout_4.addWidget(self.cmbDollarShare)

        self.horizontalSpacer_3 = QSpacerItem(158, 21, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)

        self.stackPage.addWidget(self.ActionsPage)
        self.buyLowerPage = QWidget()
        self.buyLowerPage.setObjectName(u"buyLowerPage")
        self.layoutWidget5 = QWidget(self.buyLowerPage)
        self.layoutWidget5.setObjectName(u"layoutWidget5")
        self.layoutWidget5.setGeometry(QRect(9, 20, 579, 54))
        self.gridLayout_6 = QGridLayout(self.layoutWidget5)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setContentsMargins(0, 0, 0, 0)
        self.label_8 = QLabel(self.layoutWidget5)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_6.addWidget(self.label_8, 0, 0, 1, 1)

        self.cmbReInvest = QComboBox(self.layoutWidget5)
        self.cmbReInvest.setObjectName(u"cmbReInvest")

        self.gridLayout_6.addWidget(self.cmbReInvest, 0, 1, 1, 2)

        self.label_5 = QLabel(self.layoutWidget5)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_6.addWidget(self.label_5, 0, 3, 1, 1)

        self.edtReinvestAmount = QLineEdit(self.layoutWidget5)
        self.edtReinvestAmount.setObjectName(u"edtReinvestAmount")

        self.gridLayout_6.addWidget(self.edtReinvestAmount, 0, 4, 1, 3)

        self.label_7 = QLabel(self.layoutWidget5)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_6.addWidget(self.label_7, 0, 7, 1, 2)

        self.edtStocksInFile_Reinvest = QLineEdit(self.layoutWidget5)
        self.edtStocksInFile_Reinvest.setObjectName(u"edtStocksInFile_Reinvest")

        self.gridLayout_6.addWidget(self.edtStocksInFile_Reinvest, 0, 9, 1, 1)

        self.lblbuylower = QLabel(self.layoutWidget5)
        self.lblbuylower.setObjectName(u"lblbuylower")

        self.gridLayout_6.addWidget(self.lblbuylower, 1, 0, 1, 2)

        self.edtFileBrowse_Reinvest = QLineEdit(self.layoutWidget5)
        self.edtFileBrowse_Reinvest.setObjectName(u"edtFileBrowse_Reinvest")

        self.gridLayout_6.addWidget(self.edtFileBrowse_Reinvest, 1, 2, 1, 3)

        self.btnBrowseReInvest = QPushButton(self.layoutWidget5)
        self.btnBrowseReInvest.setObjectName(u"btnBrowseReInvest")

        self.gridLayout_6.addWidget(self.btnBrowseReInvest, 1, 5, 1, 1)

        self.label_6 = QLabel(self.layoutWidget5)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_6.addWidget(self.label_6, 1, 6, 1, 2)

        self.edtReInvestValue = QLineEdit(self.layoutWidget5)
        self.edtReInvestValue.setObjectName(u"edtReInvestValue")

        self.gridLayout_6.addWidget(self.edtReInvestValue, 1, 8, 1, 2)

        self.stackPage.addWidget(self.buyLowerPage)
        self.StockGraphInfoPage = QWidget()
        self.StockGraphInfoPage.setObjectName(u"StockGraphInfoPage")
        self.gridLayout_3 = QGridLayout(self.StockGraphInfoPage)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.tabStock_Info = QTabWidget(self.StockGraphInfoPage)
        self.tabStock_Info.setObjectName(u"tabStock_Info")
        self.tabGraphType = QWidget()
        self.tabGraphType.setObjectName(u"tabGraphType")
        self.layoutWidget_2 = QWidget(self.tabGraphType)
        self.layoutWidget_2.setObjectName(u"layoutWidget_2")
        self.layoutWidget_2.setGeometry(QRect(10, 10, 231, 24))
        self.formLayout = QFormLayout(self.layoutWidget_2)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.label_4 = QLabel(self.layoutWidget_2)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_4)

        self.cmbGraphType = QComboBox(self.layoutWidget_2)
        self.cmbGraphType.setObjectName(u"cmbGraphType")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.cmbGraphType)

        self.tabStock_Info.addTab(self.tabGraphType, "")
        self.tabSectorAnalysis = QWidget()
        self.tabSectorAnalysis.setObjectName(u"tabSectorAnalysis")
        self.verticalLayout_2 = QVBoxLayout(self.tabSectorAnalysis)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.tblSectorAnalytics = QTableWidget(self.tabSectorAnalysis)
        self.tblSectorAnalytics.setObjectName(u"tblSectorAnalytics")
        self.tblSectorAnalytics.setEditTriggers(QAbstractItemView.AnyKeyPressed|QAbstractItemView.EditKeyPressed)
        self.tblSectorAnalytics.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tblSectorAnalytics.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tblSectorAnalytics.setShowGrid(False)

        self.verticalLayout_2.addWidget(self.tblSectorAnalytics)

        self.tabStock_Info.addTab(self.tabSectorAnalysis, "")

        self.gridLayout_3.addWidget(self.tabStock_Info, 0, 0, 1, 1)

        self.stackPage.addWidget(self.StockGraphInfoPage)

        self.gridLayout_5.addWidget(self.stackPage, 0, 2, 1, 1)


        self.gridLayout_2.addWidget(self.frame, 0, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.btnExecute = QPushButton(self.frame_left)
        self.btnExecute.setObjectName(u"btnExecute")
        sizePolicy1.setHeightForWidth(self.btnExecute.sizePolicy().hasHeightForWidth())
        self.btnExecute.setSizePolicy(sizePolicy1)
        self.btnExecute.setCheckable(False)

        self.horizontalLayout.addWidget(self.btnExecute)

        self.btnClearAll = QPushButton(self.frame_left)
        self.btnClearAll.setObjectName(u"btnClearAll")
        sizePolicy1.setHeightForWidth(self.btnClearAll.sizePolicy().hasHeightForWidth())
        self.btnClearAll.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.btnClearAll)

        self.btnSelectAll = QPushButton(self.frame_left)
        self.btnSelectAll.setObjectName(u"btnSelectAll")

        self.horizontalLayout.addWidget(self.btnSelectAll)

        self.lbltblAsset_sum = QLabel(self.frame_left)
        self.lbltblAsset_sum.setObjectName(u"lbltblAsset_sum")
        self.lbltblAsset_sum.setMinimumSize(QSize(80, 0))
        self.lbltblAsset_sum.setAlignment(Qt.AlignCenter)

        self.horizontalLayout.addWidget(self.lbltblAsset_sum)

        self.horizontalSpacer = QSpacerItem(200, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.vertical_splitter = QSplitter(self.frame_left)
        self.vertical_splitter.setObjectName(u"vertical_splitter")
        self.vertical_splitter.setOrientation(Qt.Vertical)
        self.tblAssets = QTableWidget(self.vertical_splitter)
        self.tblAssets.setObjectName(u"tblAssets")
        self.tblAssets.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.vertical_splitter.addWidget(self.tblAssets)
        self.lstTerm = QListWidget(self.vertical_splitter)
        self.lstTerm.setObjectName(u"lstTerm")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.lstTerm.sizePolicy().hasHeightForWidth())
        self.lstTerm.setSizePolicy(sizePolicy3)
        self.vertical_splitter.addWidget(self.lstTerm)

        self.gridLayout_2.addWidget(self.vertical_splitter, 2, 0, 1, 1)

        self.splt_horizontal.addWidget(self.frame_left)
        self.frame_right = QFrame(self.splt_horizontal)
        self.frame_right.setObjectName(u"frame_right")
        self.frame_right.setEnabled(True)
        sizePolicy.setHeightForWidth(self.frame_right.sizePolicy().hasHeightForWidth())
        self.frame_right.setSizePolicy(sizePolicy)
        self.frame_right.setMinimumSize(QSize(0, 0))
        self.frame_right.setMaximumSize(QSize(16777215, 16777215))
        self.frame_right.setBaseSize(QSize(0, 0))
        self.frame_right.setFrameShape(QFrame.StyledPanel)
        self.frame_right.setFrameShadow(QFrame.Sunken)
        self.gridLayout = QGridLayout(self.frame_right)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.grdGraph = QGridLayout()
        self.grdGraph.setObjectName(u"grdGraph")
        self.grdGraph.setSizeConstraint(QLayout.SetNoConstraint)

        self.gridLayout.addLayout(self.grdGraph, 0, 0, 1, 1)

        self.splt_horizontal.addWidget(self.frame_right)

        self.verticalLayout.addWidget(self.splt_horizontal)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1221, 22))
        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuView = QMenu(self.menuBar)
        self.menuView.setObjectName(u"menuView")
        self.menuPlots = QMenu(self.menuView)
        self.menuPlots.setObjectName(u"menuPlots")
        MainWindow.setMenuBar(self.menuBar)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        sizePolicy1.setHeightForWidth(self.statusBar.sizePolicy().hasHeightForWidth())
        self.statusBar.setSizePolicy(sizePolicy1)
        self.statusBar.setSizeGripEnabled(False)
        MainWindow.setStatusBar(self.statusBar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuView.menuAction())
        self.menuFile.addAction(self.actionRefresh)
        self.menuFile.addAction(self.actionCredentials_File)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.action_Exit)
        self.menuView.addAction(self.menuPlots.menuAction())
        self.menuPlots.addAction(self.actionBar_plot_Gain_Loss)
        self.menuPlots.addAction(self.actionBar_plot_Sector_Colors)
        self.menuPlots.addAction(self.actionIndividual_plot)
        self.menuPlots.addSeparator()
        self.menuPlots.addAction(self.actionToggle_Charts)
        self.toolBar.addAction(self.action_Exit)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionCredentials_File)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionToggle_Charts)
        self.toolBar.addAction(self.actionRefresh)

        self.retranslateUi(MainWindow)

        self.stackPage.setCurrentIndex(4)
        self.tabStock_Info.setCurrentIndex(1)
        self.btnExecute.setDefault(False)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.action_Exit.setText(QCoreApplication.translate("MainWindow", u"&Exit", None))
        self.action_Exit.setIconText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionCredentials_File.setText(QCoreApplication.translate("MainWindow", u"&Credentials File", None))
        self.actionBar_plot_Gain_Loss.setText(QCoreApplication.translate("MainWindow", u"Bar plot - (Gain\\Loss)", None))
        self.actionBar_plot_Sector_Colors.setText(QCoreApplication.translate("MainWindow", u"Bar plot - (Sector Colors)", None))
        self.actionIndividual_plot.setText(QCoreApplication.translate("MainWindow", u"Individual plot", None))
        self.actionToggle_Charts.setText(QCoreApplication.translate("MainWindow", u"Toggle Charts", None))
        self.actionRefresh.setText(QCoreApplication.translate("MainWindow", u"Refresh", None))
        self.lblAccount.setText(QCoreApplication.translate("MainWindow", u"Account:", None))
        self.lblAction.setText(QCoreApplication.translate("MainWindow", u"Action:", None))
        self.lblIteration.setText(QCoreApplication.translate("MainWindow", u"Iteration:", None))
        self.ledit_Iteration.setText(QCoreApplication.translate("MainWindow", u"1", None))
#if QT_CONFIG(tooltip)
        self.btnStoreAccounts.setToolTip(QCoreApplication.translate("MainWindow", u"Add account(s)", None))
#endif // QT_CONFIG(tooltip)
        self.btnStoreAccounts.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.lblAllocAmount.setText(QCoreApplication.translate("MainWindow", u"Allocate Amount (USD):", None))
        self.lbl_pctpf.setText(QCoreApplication.translate("MainWindow", u"% of portfolio:", None))
        self.lblFromSector.setText(QCoreApplication.translate("MainWindow", u"From Sector:", None))
        self.lblToSector.setText(QCoreApplication.translate("MainWindow", u"To Sector:", None))
        self.lblFromSector_pct.setText("")
        self.lblToSector_pct.setText("")
        self.lblSellAssetExSel.setText(QCoreApplication.translate("MainWindow", u"Sell Asset Except sellected:", None))
        self.lblExceptStocks_in_file.setText(QCoreApplication.translate("MainWindow", u"Except stocks in file:", None))
        self.btnBrowse.setText(QCoreApplication.translate("MainWindow", u"Browse ...", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Amount (est.) (USD):", None))
        self.lblRaiseAmount.setText(QCoreApplication.translate("MainWindow", u"Raise Amount (USB):", None))
        self.edtRaiseAmount.setText("")
        self.lblbuyWith.setText(QCoreApplication.translate("MainWindow", u"with", None))
#if QT_CONFIG(tooltip)
        self.edtBuyWith.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.edtBuyWith.setText("")
        self.lblBuyWithAmount.setText(QCoreApplication.translate("MainWindow", u"Dollar Value to Buy of Stock:", None))
        self.lblDollarValueToSell.setText(QCoreApplication.translate("MainWindow", u"Dollar Value to Sell:", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Reinvest:", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"of Amount (USD):", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"in selected stocks:", None))
        self.lblbuylower.setText(QCoreApplication.translate("MainWindow", u"Or Stocks in file:", None))
        self.btnBrowseReInvest.setText(QCoreApplication.translate("MainWindow", u"Browse ...", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Reinvest Value:", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Graph Type:", None))
        self.tabStock_Info.setTabText(self.tabStock_Info.indexOf(self.tabGraphType), QCoreApplication.translate("MainWindow", u"Graph Type", None))
        self.tabStock_Info.setTabText(self.tabStock_Info.indexOf(self.tabSectorAnalysis), QCoreApplication.translate("MainWindow", u"Sector Analytics", None))
        self.btnExecute.setText(QCoreApplication.translate("MainWindow", u"Execute ...", None))
        self.btnClearAll.setText(QCoreApplication.translate("MainWindow", u"Clear All", None))
        self.btnSelectAll.setText(QCoreApplication.translate("MainWindow", u"Select All", None))
        self.lbltblAsset_sum.setText("")
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"&File", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
        self.menuPlots.setTitle(QCoreApplication.translate("MainWindow", u"Plots", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

