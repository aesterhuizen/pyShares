from datetime import datetime
import os
import sys,traceback # type: ignore
import time
import pyotp
import robin_stocks.robinhood as r


import matplotlib.colors as mcolors
import matplotlib
import pandas as pd
import mplfinance as mpf
import yfinance as yf

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.patches import Patch
import matplotlib.gridspec as gridspec

matplotlib.use('QtAgg')

import re
from PyQt6.QtGui import QPalette

from dotenv import load_dotenv, set_key


from PyQt6.QtWidgets import QWidget, QApplication, QMainWindow, QMessageBox,QLabel, \
    QPushButton, QTableWidget, QTableWidgetItem,QVBoxLayout, QFileDialog, \
    QScrollArea, QSizePolicy
                            
from PyQt6.QtGui import QAction, QIcon, QCursor, QColor,QFont
from PyQt6.QtCore import QSize,Qt,QPoint, QTimer

from layout import Ui_MainWindow

from PopupWindows import msgBoxGetCredentialFile, msgBoxGetAccounts,confirmMsgBox
from WorkerThread import CommandThread, UpdateThread

class MainWindow(QMainWindow):

    
    def __init__(self):
        super().__init__()

        #class variabled
        # self.quantity = []

        
     
        self.ver_string = "v1.0.42"
        self.icon_path = ''
        self.base_path = ''
        self.env_file = ''
        self.data_path = ''
        self.env_path = ''
        #variable to hold list of shares from file
        self.lstShares_in_file = []
        self.update_thread = None
        self.command_thread = None
        self.monitor_thread = None

        #Item[0] =  tickers
        #Item[1]= Total_return
        #Item[2] = stock_quantity_to_sell/buy
        #Item[3]= last price
        #item[4]= your quantities
        #item[5]=today's return
        #item[6]= average buy price
        #item[7]=%change in price
        #item[8]=change in price since previous close
        #items to be updated ["Ticker","Price","Change","Quantity","Today's Return","Total Return"]
        #updated_items = update_current_assets()
        #item[9] = stock name
        self.totalGains = 0.0
        self.todayGains = 0.0
        self.selected_stocks = []
        
        self.current_account_num = ""
        self.account_info = ''
        #main list of tickers and performance metrics
        self.ticker_lst = []
        self.fundamentals = []
        self.dict_sectors = {}
        self.portfolio  = {}
        self.portfolio_tvalue = 0.0
        self.plot_type = {0: "Bar (Gain/Loss)", 
                                  1: "Bar (Sector Colors)", 
                                  2: "Bar (Individual Stocks)"}
        self.current_plot_type = self.default_plot_type = self.plot_type[1]
       

        self.lstupdated_tblAssets = []
        self.setGeometry(300, 300, 1000, 1000)
        #variable allocations to hold the lists stocks in the selected sectors with percentagesof poerfoli
        self.alloc_from = []
        self.alloc_to = []
        self.symbols_from = []
        self.symbols_to = []
        self.raised_amount = ""
        #new lst of shares to buy
        self.new_lstShares = []

        # setup UI
        self.ui = Ui_MainWindow()       
        self.tooltip = None
        
        #shutdown flag, select all flag
        self._shutting_down = False
        self._selectAll_in_progress = False
        # sequence runner
        self.op_queue = []
        self._seq_num_iter = 1
        self.seq_timer = QTimer(self)
        self.seq_timer.setInterval(200)
        self.seq_timer.timeout.connect(self._check_and_run_next)

        self.ui.setupUi(self)
        self.ui.splt_horizontal.setSizes([10, 550])
        self.ui.vertical_splitter.setSizes([450, 50])
        self.plot = MpfCanvas(self,8,4)
        self.plot_scroll = QScrollArea(self)
        self.plot_scroll.setWidgetResizable(True)
        self.plot_scroll.setWidget(self.plot)
        self.ui.grdGraph.addWidget(self.plot_scroll)
        self.ui.grdGraph.setContentsMargins(0, 0, 0, 0)
        self.ui.grdGraph.setSpacing(0)
        

        #add combo box items to the action combobox
        self.ui.cmbAction.addItem("stock_info")
        self.ui.cmbAction.addItem("sell_selected")
        self.ui.cmbAction.addItem("sell_gains_except_x")
        self.ui.cmbAction.addItem("sell_todays_return_except_x")
        self.ui.cmbAction.addItem("buy_selected_with_x")
        self.ui.cmbAction.addItem("reinvest_with_gains")
        self.ui.cmbAction.addItem("allocate_reallocate_to_sectors")
        self.ui.cmbAction.addItem("raise_x_sell_y_dollars_except_z")
        #add items to cmbGraphType
        self.ui.cmbGraphType.addItem("Bar (Gain/Loss)")
        self.ui.cmbGraphType.addItem("Bar (Sector Colors)")
        self.ui.cmbGraphType.addItem("Bar (Individual Stocks)")
        
        self.ui.cmbGraphType.activated.connect(self.cmbGraphType_clicked)
        #sret default graph type to Sector colors
        self.ui.cmbGraphType.setCurrentIndex(1)
        self.ui.cmbGraphType.setCurrentText("Bar (Sector Colors)")
        #add combo box items to Dollar Share selector
        self.ui.cmbDollarShare.addItem("Buy in USD")
        self.ui.cmbDollarShare.addItem("Buy in Shares")
        
        self.ui.cmbDollarShare.setVisible(False)

        # set the meta data textboxes and labels to invisible
        self.ui.edtRaiseAmount.setVisible(False)
        self.ui.lblRaiseAmount.setVisible(False)
        self.ui.edtDollarValueToSell.setVisible(False)
        self.ui.lblDollarValueToSell.setVisible(False)
        self.ui.lblBuyWithAmount.setVisible(False)
        self.ui.edtBuyWithAmount.setVisible(False)
        self.ui.lblbuyWith.setVisible(False)
        self.ui.edtBuyWith.setVisible(False)

        
        # #show the stack Page default to index 1
        if self.ui.stackPage.count() > 0:
            self.ui.stackPage.setCurrentIndex(4)
            self.ui.stackPage.setVisible(True)

      

        #load credentials file
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        #bundle, the PyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app 
        # path into variable _MEIPASS'.
            self.base_path = sys._MEIPASS
           
        else:
            self.base_path = os.path.abspath(".")

        #set the program paths
        self.icon_path = os.path.join(self.base_path,"icons")
        self.data_path = os.path.join(os.environ['LOCALAPPDATA'], "pyShares")
        self.env_file = os.path.join(self.data_path,"env_path.txt")
      
        
        if os.path.exists(self.env_file):
            #write env_path to file
            with open(self.env_file,"r") as open_file:
                self.env_path = open_file.read()
        
            
        

            
            #load credentials file
            load_dotenv(self.env_path, override=True)
            
            if os.environ['debug'] == '1':
                self.setWindowTitle(f"PyShares - {self.ver_string} - Debug ({self.env_path})")
            else:
                self.setWindowTitle(f"PyShares - {self.ver_string} - ({self.env_path})")

           
            #login to Robinhood
            try:
                otp = pyotp.TOTP(os.environ['robin_mfa']).now()
                result = r.login(os.environ['robin_username'],os.environ['robin_password'], mfa_code=otp)
            except Exception as e:
                self.ui.lstTerm.addItem(f"Error: {e.args[0]}")
                
            
            #Get account numers and populate comboboxes
            self.account_info = os.environ['account_number']
            self.ui.cmbAccount.clear()
            #There is an account number
            if self.account_info != '':
                if self.account_info.find(',') != -1:
                    slice_account = self.account_info.split(',')
                    for item in slice_account:
                        self.ui.cmbAccount.addItem(item)
                else:
                    self.ui.cmbAccount.addItem(self.account_info)
                
                self.current_account_num = self.ui.cmbAccount.currentText().split(' ')[0]    
                
                try:
                    self.ticker_lst = self.get_stocks_from_portfolio(self.current_account_num)
                     
                except Exception as e:
                    if e.args[0]:
                        self.ui.lstTerm.addItem(f"Error!: {e.args[0]}")
                        
                        
            
                self.print_cur_protfolio(self.ticker_lst)
                #get total gains for the day
                self.totalGains = sum(item[1] for item in self.ticker_lst)
                self.todayGains = sum(item[5] for item in self.ticker_lst)               
        else: #self.data_path is empty create path and file
            get_cred_file = msgBoxGetCredentialFile()
            button = get_cred_file.exec() #show the popup box for the user to enter account number

            if button == 1:
                self.env_path = get_cred_file.edtCred_path.text()
             

                #load credentials file                                     
                load_dotenv(self.env_path,override=True,)
                if os.environ['debug'] == '1':
                    self.setWindowTitle(f"PyShares - {self.ver_string} - Debug ({self.env_path})")
                else:
                    self.setWindowTitle(f"PyShares - {self.ver_string} - ({self.env_path})")

                #create temp path #write env_path to file
                os.makedirs(self.data_path,exist_ok=True)
                os.chmod(self.data_path,0o777)

                
                with open(self.env_file,"x") as open_file:
                    open_file.write(self.env_path)
                os.chmod(self.env_file,0o666)

                #try and see if we are already logged in, if not login
               
                try:
                    self.ticker_lst = self.get_stocks_from_portfolio(self.current_account_num)  # Sort by the 10th element (index 9)
                except Exception as e:
                    if e.args[0] == "Invalid account number":
                        self.ui.lstTerm.addItem(f"Error: {e.args[0]}")
                    elif e.args[0] == "No stocks in account":
                        self.ui.lstTerm.addItem(f"Error: {e.args[0]}")
                    else:
                   
                        #login to Robinhood
                        try:
                            otp = pyotp.TOTP(os.environ['robin_mfa']).now()
                            r.login(os.environ['robin_username'],os.environ['robin_password'], mfa_code=otp)
                        except Exception as e:
                            self.ui.lstTerm.addItem(f"Error: {e.args[0]}")
                            return
                
                #Get account numers and populate comboboxes
                self.account_info = os.environ['account_number']
                self.ui.cmbAccount.clear()
                #There is an account number
                if self.account_info != '':
                    if self.account_info.find(',') != -1:
                        slice_account = self.account_info.split(',')
                        for item in slice_account:
                            self.ui.cmbAccount.addItem(item)
                    else:
                        self.ui.cmbAccount.addItem(self.account_info)
                    
                    self.current_account_num = self.ui.cmbAccount.currentText().split(' ')[0]       
                    
                    try:
                        self.ticker_lst = self.get_stocks_from_portfolio(self.current_account_num)  # Sort by the 10th element (index 9)
                        
                    except Exception as e:
                        if e.args[0] == "Invalid account number":
                            self.ui.lstTerm.addItem(f"Error: {e.args[0]}")
                            return
                    
                    self.print_cur_protfolio(self.ticker_lst)
                    #get total gains for the day
                    self.totalGains = sum(item[1] for item in self.ticker_lst)
                    self.todayGains = sum(item[5] for item in self.ticker_lst)   
                   
            else: #user pressed cancel at credential dialog
                self.setWindowTitle(f"PyShares - {self.ver_string}")

        #Setup signals / Slots
    
        
        #menu Qaction_exit
        self.ui.action_Exit.triggered.connect(self.closeMenu_clicked)
        self.ui.actionCredentials_File.triggered.connect(self.Show_msgCredentials)

        #menu actions Plot menu
        self.ui.actionBar_plot_Gain_Loss.triggered.connect(self.showGainLossChart)
        self.ui.actionBar_plot_Sector_Colors.triggered.connect(self.showSectorChart)
        self.ui.actionIndividual_plot.triggered.connect(self.showIndividualChart)
        
        #Toolbar
        self.ui.toolBar.setIconSize(QSize(32,32))
        button_action = QAction(QIcon(self.icon_path +'/exit.png'), "Exit", self)
        button_action.triggered.connect(self.closeMenu_clicked)
        button_action = self.ui.toolBar.addAction(button_action)
        
        self.ui.toolBar.addSeparator()

        #add credentials button
        button_cred_action = QAction(QIcon(self.icon_path +'/Credentials.png'), "Credentials", self)
        button_cred_action.triggered.connect(self.Show_msgCredentials)
        button_cred_action = self.ui.toolBar.addAction(button_cred_action)

        #add charts button
        button_chart_action = QAction(QIcon(self.icon_path +'/bar-chart.png'), "View Bar Chart (Sector Colors)", self)
        button_chart_action.triggered.connect(self.toggleChart_clicked)
        button_chart_action.setToolTip("Toggle Graph Type")
        button_chart_action = self.ui.toolBar.addAction(button_chart_action)
        
        # set tooltip for edtBuyWith textbox
        self.ui.edtBuyWith.setToolTip("Optional, If entered will iterate through selected list and buy stocks until the (buy with) amount is reached\nIf left blank then will only buy amount as indicated in (Buy in USD) or (Buy in Shares)")
        #connect edtBuyWith textbox 
        self.ui.edtBuyWith.textChanged.connect(self.edtBuyWith_changed)
        #connect function to combo dollar/value selector
        self.ui.cmbDollarShare.activated.connect(self.cmbDollarShare_clicked)
        #connect sigals and slots Account combo box
        self.ui.cmbAccount.activated.connect(self.account_clicked)
        #connect sigals and slots Actions combo box
        self.ui.cmbAction.activated.connect(self.cmbAction_clicked)
        self.ui.cmbAction.currentIndexChanged.connect(self.cmbAction_clicked)
        #connect signal/slot for label Iteration button
        #connect selectAll button
        self.ui.btnSelectAll.clicked.connect(self.SelectAll_clicked)
        #tbl default sellection mode to multi selection
        self.ui.tblAssets.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)    
        #connect signal/slot for ledit_Iteration
        self.ui.ledit_Iteration.textChanged.connect(self.ledit_Iteration_textChanged)
        
        #connect signal/slot for Execute button
        self.ui.btnExecute.clicked.connect(self.btnExecute_clicked)
        self.ui.btnExecute.setStyleSheet("background-color: grey; color: white;")  # Change background to grey             
        self.ui.btnExecute.setEnabled(False)  # Disable the button initially
        self.ui.btnExecute.setText("Execute ...")
      

        #connect GetAccount button
        self.ui.btnStoreAccounts.clicked.connect(self.StoreAccounts)
        #connect signal/slot for edtRaiseAmount
        self.ui.edtRaiseAmount.textChanged.connect(self.edtRaiseAmount_changed)
        #connect signal/slot for edtDollarValueToSell
        self.ui.edtDollarValueToSell.textChanged.connect(self.edtDollarValueToSell_changed)
        self.ui.edtBuyWithAmount.textChanged.connect(self.edtBuyWithAmount_changed)   
        #connect clear selection button
        self.ui.btnClearAll.clicked.connect(self.clear_all_clicked)  
        #connect the Asset table box
        self.ui.tblAssets.itemClicked.connect(self.tblAsset_clicked)
        #connect cmbReinvest combo box
        self.ui.cmbReInvest.activated.connect(self.cmbReInvest_clicked)
        #connect edtFileBrowse_buyLower textbox
        self.ui.edtFileBrowse_buyLower.textChanged.connect(self.edtFileBrowse_buyLower_changed)
        #setup allocation page connections
        self.ui.edtAllocAmount.textChanged.connect(self.edtAllocAmount_changed)
        #setup from sector combo box
        self.ui.cmbFromSector.activated.connect(self.cmbFromSector_clicked)
        #setup to sector combo box
        self.ui.cmbToSector.activated.connect(self.cmbToSector_clicked)

        #setup buySell Page connections
        self.ui.btnBrowse.clicked.connect(self.btnBrowseBuySell_clicked)
        #connect buy lower with gains page buttons
        self.ui.btnBrowseReInvest.clicked.connect(self.btnBrowseReInvest_clicked)
        #setup list Term to always scroll to bottom when new item is added
        self.ui.lstTerm.model().rowsInserted.connect(lambda parent, first, last: QTimer.singleShot(0, self.ui.lstTerm.scrollToBottom))
        #create an update worker thread to update the asset list every 10 seconds
        self.update_thread = UpdateThread(self.updateLstAssets)
        self.update_thread.daemon = True
        self.update_thread.start()

        #Monitor to see if command thread is currently running and if it is not then change the button to green
        self.monitor_thread = UpdateThread(self.monitor_command_thread)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        self.setupStatusbar()
        #setup plot widget
        self.setup_plot(self.ticker_lst,plot_type=self.current_plot_type)
        # show the Mainwindow
        self.show()

    def toggleChart_clicked(self):
        
        
        current_index = self.ui.cmbGraphType.currentIndex()
        current_index += 1

        if current_index // 3 == 1:
            current_index = 0
     
        self.clear_all_clicked()
        match current_index:
            case 0:
                self.showGainLossChart()
            case 1:
                self.showSectorChart()
            case 2:
                self.showIndividualChart()
      
        return
    def showGainLossChart(self):
        cursor = QCursor()
        cursor.setShape(cursor.shape().WaitCursor)
        QApplication.setOverrideCursor(cursor)
        
        self.current_plot_type = self.plot_type[0]
        self.ui.cmbGraphType.setCurrentIndex(0)
        self.ui.cmbGraphType.setCurrentText("Bar (Gain/Loss)")

        self.setup_plot(self.ticker_lst,plot_type=self.current_plot_type)

        QApplication.restoreOverrideCursor()
    
    def showSectorChart(self):
        cursor = QCursor()
        cursor.setShape(cursor.shape().WaitCursor)
        QApplication.setOverrideCursor(cursor)
        
        self.current_plot_type = self.plot_type[1]
        self.ui.cmbGraphType.setCurrentIndex(1)
        self.ui.cmbGraphType.setCurrentText("Bar (Sector Colors)")
        self.setup_plot(self.ticker_lst,plot_type=self.current_plot_type)

        QApplication.restoreOverrideCursor()
        return
    def showIndividualChart(self):
        cursor = QCursor()
        cursor.setShape(cursor.shape().WaitCursor)
        QApplication.setOverrideCursor(cursor)
        
        self.current_plot_type = self.plot_type[2]
        self.ui.cmbGraphType.setCurrentIndex(2)
        self.ui.cmbGraphType.setCurrentText("Bar (Individual Stocks)")
        self.setup_plot(self.ticker_lst,plot_type=self.current_plot_type)

        QApplication.restoreOverrideCursor()
        return
  

    def cmbGraphType_clicked(self):
        #redraw the plot based on the selected graph type
        cursor = QCursor()
        cursor.setShape(cursor.shape().WaitCursor)
        QApplication.setOverrideCursor(cursor)
        
        current_index = self.ui.cmbGraphType.currentIndex()
        self.current_plot_type = self.plot_type[current_index]
        self.clear_all_clicked()
        self.setup_plot(self.ticker_lst, plot_type=self.current_plot_type)
        self.updateStatusBar(self.selected_stocks)
        QApplication.restoreOverrideCursor()
        return
    def edtFileBrowse_buyLower_changed(self):
        if os.path.isfile(self.ui.edtFileBrowse_buyLower.text()):
            self.ui.edtReinvestAmount_buyLower.setEnabled(False)
            self.ui.edtStocksInFile_BuyLower.setEnabled(False)
            self.ui.tblAssets.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            self.ui.tblAssets.viewport().setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
       

    def cmbReInvest_clicked(self):
        ReInverst_amount = 0.0
        total_amount = 0.0
        if os.path.isfile(self.ui.edtFileBrowse_buyLower.text()):
            total_amount = sum([float(item[1])*float(item[2]) for item in self.lstShares_in_file])
        else:
            if self.ui.edtReinvestAmount_buyLower.text() != '':
                try:
                    total_amount = float(self.ui.edtReinvestAmount_buyLower.text())
                    
                except Exception as e:
                    self.ui.lstTerm.addItem(f"Error: Reinvest amount not valid")
                    self.ui.edtReInvestValue.setText("")

        cmb_amount = self.ui.cmbReInvest.currentText().replace('%','')
        match cmb_amount:
            case "10":
                ReInverst_amount = total_amount * 0.10
            case "20":
                ReInverst_amount = total_amount * 0.20
            case "30":
                ReInverst_amount = total_amount * 0.30
            case "40":  
                ReInverst_amount = total_amount * 0.40
            case "50":
                ReInverst_amount = total_amount * 0.50
            case "60":
                ReInverst_amount = total_amount * 0.60
            case "70":
                ReInverst_amount = total_amount * 0.70
            case "80":
                ReInverst_amount = total_amount * 0.80
            case "90":  
                ReInverst_amount = total_amount * 0.90
            case "100":
                ReInverst_amount = total_amount * 1.00
                
        self.ui.edtReInvestValue.setText(f"${ReInverst_amount:,.2f}")            

        return
    def btnBrowseReInvest_clicked(self):
        options = QFileDialog.Option.DontUseNativeDialog
        lst_shares = []
        ReInverst_amount = 0.0
        total_amount = 0.0
        file_name, _ = QFileDialog.getOpenFileName(None, "Open File", f"{self.data_path}", "CSV Files (*.csv);;Text Files (*.txt);;All Files (*)", options=options)

        if os.path.isfile(file_name):
            self.ui.edtFileBrowse_buyLower.setText(file_name)
            self.ui.edtReinvestAmount_buyLower.setEnabled(False)
            self.ui.edtStocksInFile_BuyLower.setEnabled(False)
            self.ui.tblAssets.clearSelection()
            
            try:
                with open(file_name,"r") as open_file:
                    lines = open_file.readlines()
                    for line in lines:
                        line = line.strip()
                        share_name,share_quantity,share_price = line.split(':')
                        lst_shares.append((share_name,share_quantity,share_price))   
            except Exception as e:
                self.ui.lstTerm.addItem(f"Error: File not in correct format")
                self.ui.edtFileBrowse_buyLower.setText("")
                self.ui.edtStocksInFile_BuyLower.setReadOnly(False)
                self.ui.edtStocksInFile_BuyLower.setStyleSheet("background-color: white;")
                self.ui.edtStocksInFile_BuyLower.setText("")
                self.ui.edtAmountEst.setText("")
                return
            #sort the list of shares Alphabetically
            self.lstShares_in_file = sorted(lst_shares, key=lambda x: x[0])
            str_stock_names = ','.join([item[0] for item in self.lstShares_in_file])  
            self.ui.edtStocksInFile_BuyLower.setText(str_stock_names)

            stocks = [item[0] for item in self.lstShares_in_file]
            self.highlight_stocks_in_table(stocks)
            self.setup_plot(self.ticker_lst,sellected_tickets=stocks,plot_type=self.current_plot_type)
            total_amount = sum([float(item[1])*float(item[2]) for item in self.lstShares_in_file])
            self.ui.edtReinvestAmount_buyLower.setText(f"${total_amount:,.2f}")
            cmb_amount = self.ui.cmbReInvest.currentText().replace('%','')
            match cmb_amount:
                case "10":
                    ReInverst_amount = total_amount * 0.10
                case "20":
                    ReInverst_amount = total_amount * 0.20
                case "30":
                    ReInverst_amount = total_amount * 0.30
                case "40":  
                    ReInverst_amount = total_amount * 0.40
                case "50":
                    ReInverst_amount = total_amount * 0.50
                case "60":
                    ReInverst_amount = total_amount * 0.60
                case "70":
                    ReInverst_amount = total_amount * 0.70
                case "80":
                    ReInverst_amount = total_amount * 0.80
                case "90":  
                    ReInverst_amount = total_amount * 0.90
                case "100":
                    ReInverst_amount = total_amount * 1.00
                
            self.ui.edtReInvestValue.setText(f"${ReInverst_amount:,.2f}")

    def btnBrowseBuySell_clicked(self):
        options = QFileDialog.Option.DontUseNativeDialog
        lstShares = []
        total_amount = 0.0
        file_name, _ = QFileDialog.getOpenFileName(None, "Open File", f"{self.data_path}", "CSV Files (*.csv);;Text Files (*.txt);;All Files (*)", options=options)

        if os.path.isfile(file_name):
            self.ui.edtFileBrowse.setText(file_name)
            self.ui.edtLstStocksSellected.setReadOnly(True)
            self.ui.edtLstStocksSellected.setStyleSheet("background-color: lightgrey;")
            try:
                with open(file_name,"r") as open_file:
                    lines = open_file.readlines()
                    for line in lines:
                        line = line.strip()
                        share_name,share_quantity,share_price = line.split(':')
                        lstShares.append((share_name,share_quantity,share_price))   
            except Exception as e:
                self.ui.lstTerm.addItem(f"Error: File not in correct format")
                self.ui.edtFileBrowse.setText("")
                self.ui.edtLstStocksSellected.setReadOnly(False)
                self.ui.edtLstStocksSellected.setStyleSheet("background-color: white;")
                self.ui.edtLstStocksSellected.setText("")
                self.ui.edtAmountEst.setText("")
                return
            
            str_stock_names = ','.join([item[0] for item in lstShares])  
            stocks = [item[0] for item in lstShares]
            self.highlight_stocks_in_table(stocks)
            self.setup_plot(self.ticker_lst,plot_type=self.current_plot_type)
            total_amount = sum([float(item[1])*float(item[2]) for item in lstShares])
            cur_amount = self.ui.edtAmountEst.text()
            strip_dollarsign = cur_amount.replace('$','')
            _ = strip_dollarsign.replace(',','')
            
            if self.ui.cmbAction.currentText() == "sell_gains_except_x" :
                #new list with stocks excluded
                lst_share_name = self.find_and_remove(self.ticker_lst, stocks,0)
                total_amount, _ = self.cal_today_total_gains(lst_share_name)
                
            elif self.ui.cmbAction.currentText() == "sell_todays_return_except_x":
                lst_share_name = self.find_and_remove(self.ticker_lst, stocks,0)
                _,total_amount = self.cal_today_total_gains(lst_share_name)

            self.ui.edtAmountEst.setText(f"${total_amount:,.2f}")
            self.ui.edtLstStocksSellected.setText(str_stock_names)
            self.ui.btnExecute.setEnabled(True)
            self.ui.btnExecute.setStyleSheet("background-color: green; color: white;")  # Change background to green             
        else:
            self.ui.edtFileBrowse.setText("")
            self.ui.edtLstStocksSellected.setReadOnly(False)
            self.ui.edtLstStocksSellected.setStyleSheet("background-color: white;")
            self.ui.edtLstStocksSellected.setText("")
            self.ui.edtAmountEst.setText("")
            

        
        return
    def cmbToSector_clicked(self):
        tot_pct = 0.0
        lst_to_sector = self.get_symbols_To_sectors()
        for item in lst_to_sector:
                pct = item.split(":")[1]
                tot_pct += float(pct)

        self.ui.lblToSector_pct.setText(f'{tot_pct:.2f}% of Portfolio')
        # highlist the lst_to_sector stocks in the asset table
        self.highlight_stocks_in_table(lst_to_sector)
        return
    
    def cmbFromSector_clicked(self):
        
        tot_pct = 0.0
        lst_from_sector = self.get_symbols_From_sectors()
        for item in lst_from_sector:
                pct = item.split(":")[1]
                tot_pct += float(pct)
            
        self.ui.lblFromSector_pct.setText(f'{tot_pct:.2f}% of Portfolio')
        # highlist the lst_from_sector stocks in the asset table
        self.highlight_stocks_in_table(lst_from_sector)
        return

    def highlight_stocks_in_table(self,lst_stocks):
        #clear all previous selections
        self.ui.tblAssets.clearSelection()
        self.ui.tblAssets.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
        #loop over the list of stocks and highlight them in the table
        symbols = [stock.split(':')[0] for stock in lst_stocks]
        for symbol in symbols:
            index = self.ui.tblAssets.findItems(symbol, Qt.MatchFlag.MatchContains)
            if index:
                self.ui.tblAssets.selectRow(index[0].row())
                
        return

    def get_symbols_From_sectors(self) -> list[str]:
        # Get the selected sector
        sectorFrom = self.ui.cmbFromSector.currentText()
        # Get the symbols in the selected sector
        symbolsFromSector = self.get_symbols_pct_in_sector(sectorFrom)

      
        return symbolsFromSector

    def get_symbols_To_sectors(self) -> list[str]:
        # Get the selected sector
        sectorTo = self.ui.cmbToSector.currentText()
        # Get the symbols in the selected sector
        symbolsToSector = self.get_symbols_pct_in_sector(sectorTo)

      
        return symbolsToSector
    
    def get_symbols_in_5pct_sector(self) -> list[str]:
        # Get the list of stocks in the 5% sector
        newlst = self.reduce_position_to_5pct_of_portfolio(self.portfolio)
        return newlst

    def reduce_position_to_5pct_of_portfolio(self, dict_stocks):
        # Reduce the position of each stock to 5% of the portfolio
        lst_stockReduce = []
        pct_5 = self.portfolio_tvalue * 0.05
        for key,value in dict_stocks.items():
            if float(value['equity']) > pct_5:
                reduce_by = pct_5 - float(value['equity'])
                frm_reduce_by = "{0:-.2f}".format(reduce_by)
                lst_stockReduce.append(f'{key}:{frm_reduce_by}')
            elif float(value['equity']) < pct_5:
                increase_by = pct_5 - float(value['equity'])
                frm_increase_by = "{0:+.2f}".format(increase_by)
                lst_stockReduce.append(f'{key}:{frm_increase_by}')

        return lst_stockReduce

    def get_symbols_pct_in_sector(self, name):
        # Get the list of stocks in sector
        lst_stocks_pct_in_sector = self.dict_sectors[name]
        
        
        return lst_stocks_pct_in_sector

    def monitor_command_thread(self):
        while not self._shutting_down:
            time.sleep(0.1)
            if self.command_thread is not None and not self.command_thread.is_alive():
                # update UI on the main thread
               
                self.ui.btnExecute.setText("Execute ..."),
                self.ui.btnExecute.setStyleSheet("background-color: green; color: white;")
                self.ui.btnExecute.setEnabled(True)
                
        

    def eventFilter(self, obj, event):
       cursor = QCursor()
       cursor.setShape(cursor.shape().WaitCursor)
       if event.type() == event.Type.MouseButtonPress:
            QApplication.setOverrideCursor(cursor)
            if isinstance(obj, QPushButton):
                if event.button() == Qt.MouseButton.LeftButton:
                    if self.tooltip:
                        self.tooltip.close()
                        self.tooltip = None
                        self.clear_all_clicked()
                    else:
                        self.showTableTooltip(obj)
                        lst_stocks = self.get_symbols_pct_in_sector(obj.objectName())
                        symbols = [stock.split(':')[0] for stock in lst_stocks]
                        symbols_label = ','.join(symbols)
                        self.highlight_stocks_in_table(lst_stocks)
                        self.selected_stocks = self.find_and_remove(self.ticker_lst, symbols,1)
                        self.setup_plot(self.ticker_lst,sellected_tickets=symbols,plot_type=self.current_plot_type)
                        self.ui.edtLstStocksSellected.setText(symbols_label) 
                        self.ui.edtRaiseAmount.setText(symbols_label)
                        self.updateStatusBar(self.selected_stocks)
                        total_equity = 0.0
                        total_equity = sum(float(self.portfolio[sym]['equity']) for sym in symbols if sym in self.portfolio)
                        self.ui.lbltblAsset_sum.setText(f"Equity: ${total_equity:,.2f}")
                        self.ui.tblAssets.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
                        self.ui.tblAssets.viewport().setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

            
            QApplication.restoreOverrideCursor()
       return super().eventFilter(obj, event)
    
    def showTableTooltip(self,button):
        if self.tooltip:
            self.tooltip.close()
        self.tooltip = TableToolTip(button,self)
        tt_hight = self.tooltip.height()
        pos = button.mapToGlobal(QPoint(0, -tt_hight))
        self.tooltip.move(pos)
        self.tooltip.show()

    def setupStatusbar(self):

        #remove all statusbar childern
        
        for child in self.ui.statusBar.children():
            if not isinstance(child, QVBoxLayout):
                self.ui.statusBar.removeWidget(child)

        lblStatusBar = QLabel(f"Total Assets: {self.ui.tblAssets.rowCount()}")
        lblStatusBar.setMinimumWidth(100)
        lblStatusBar.setObjectName("lblStatusBar")
        self.ui.statusBar.addWidget(lblStatusBar,1)

        frm_TotalGains = "{0:,.2f}".format(self.totalGains)
        lblStatusBar_pctT = QLabel(f"Total Return: ${frm_TotalGains}")
        lblStatusBar_pctT.setObjectName("lblStatusBar_pctT")
        lblStatusBar_pctT.setMinimumWidth(150)
        self.ui.statusBar.addWidget(lblStatusBar_pctT,1)

        frm_TodayGains = "{0:,.2f}".format(self.todayGains)
        lblStatusBar_pctToday = QLabel(f"Todays Return: ${frm_TodayGains}")
        lblStatusBar_pctToday.setObjectName("lblStatusBar_pctToday")

        lblStatusBar_pctToday.setMinimumWidth(150)
        self.ui.statusBar.addWidget(lblStatusBar_pctToday,1)

        
            
        tbl_Index = QTableWidget()
       
        tbl_Index.setObjectName("tbl_Index")
        tbl_Index.setMaximumHeight(25)
        tbl_Index.setMinimumWidth(495)
       
        tbl_Index.setRowCount(1)
        tbl_Index.horizontalHeader().setVisible(False)
        tbl_Index.verticalHeader().setVisible(False)
        tbl_Index.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        tbl_Index.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        tbl_Index.setShowGrid(False)
        
        lst_SPY = []
        count = 0
        SPY_value = r.get_quotes("IVV","last_trade_price")[0]
        SPY_prev_close = r.get_quotes("IVV","previous_close")[0]
        SPY_Gains = (float(SPY_value) - float(SPY_prev_close)) * 100 / float(SPY_prev_close)

        QQQ_value = r.get_quotes("QQQ","last_trade_price")[0]
        QQQ_prev_close = r.get_quotes("QQQ","previous_close")[0]
        QQQ_Gains = (float(QQQ_value) - float(QQQ_prev_close)) * 100 / float(QQQ_prev_close)

        Dow_value = r.get_quotes("DIA","last_trade_price")[0]
        Dow_prev_close = r.get_quotes("DIA","previous_close")[0]
        Dow_Gains = (float(Dow_value) - float(Dow_prev_close)) * 100 / float(Dow_prev_close)

        lst_SPY.append(["QQQ", float(QQQ_value),float(QQQ_Gains)])
        lst_SPY.append(["S&P", float(SPY_value)*10,float(SPY_Gains)])
        lst_SPY.append(["DOW", float(Dow_value)*100,float(Dow_Gains)])


        tbl_Index.setColumnCount(3*len(lst_SPY))
        SPY_icon_up = QIcon(f"{self.icon_path}\\up.png")
        SPY_icon_down = QIcon(f"{self.icon_path}\\down.png")
        SPY_icon_equal = QIcon(f"{self.icon_path}\\equal.png")
        
        
        for row in range(len(lst_SPY)):
            for col in range(0,3):
                table_item = QTableWidgetItem()
                if col == 2 and lst_SPY[row][col] > 0.0:
                    # found change item add up/down arrow depending on the value
                    table_item.setText("{0:+.2f}".format(lst_SPY[row][col]))
                    table_item.setIcon(SPY_icon_up)
                elif col == 2 and lst_SPY[row][col] < 0.0:
                    table_item.setText("{0:-.2f}".format(lst_SPY[row][col]))
                    table_item.setIcon(SPY_icon_down)
                elif col == 2 and lst_SPY[row][col] == 0.0:
                    table_item.setText("{0:.2f}".format(lst_SPY[row][col]))
                    table_item.setIcon(SPY_icon_equal)
                else:
                    if col == 0:
                        table_item.setText(lst_SPY[row][col])
                    else:
                        table_item.setText("{0:,.2f}".format(lst_SPY[row][col]))

                
                table_item.setFont(QFont("Arial",8,QFont.Weight.Bold))
                table_item.setBackground(QColor("White"))
                table_item.setForeground(QColor("Black"))
                if row > 0:
                    count += 1
                    tbl_Index.setColumnWidth(2+count, 55)
                    tbl_Index.setItem(0,2+count, table_item)
                elif row == 0:
                    tbl_Index.setItem(0,col, table_item)
                    tbl_Index.setColumnWidth(col, 55)

        tbl_Index.resizeColumnsToContents()
        tbl_Index.width = tbl_Index.horizontalHeader().length()
        tbl_Index.setMinimumWidth(tbl_Index.width+ 20)
        self.ui.statusBar.addWidget(tbl_Index,1)


        
        self.setupSectorButtons()
       
      
        
        

        return

                    
    def setupSectorButtons(self):

        tot_pct = 0.0   
        if len(self.dict_sectors) != 0:
            self.dict_sectors = {}

        #loop over the dictionary fundamentals and create a new dicrionary of all the sectors and stock symbols in those sectors
        for symbol in self.portfolio:
            sector = self.portfolio[symbol]['sector']
            pct_portfolio = (float(self.portfolio[symbol]['equity']) / self.portfolio_tvalue * 100) if self.portfolio_tvalue > 0 else 0
            if sector not in self.dict_sectors:
                self.dict_sectors[sector] = [f'{symbol}:{pct_portfolio}']
            else:
                self.dict_sectors[sector].append(f'{symbol}:{pct_portfolio}')
        #sort dictionary keys according to pct_portfolio
        self.dict_sectors = dict(sorted(self.dict_sectors.items(), key=lambda item: sum(float(x.split(':')[1]) for x in item[1]), reverse=True))

       #remove all sector button if it exist
        remove_buttons = [child for child in self.ui.statusBar.children() if isinstance(child, QPushButton)]

        #remove old buttons that are not necessary
        for button in remove_buttons:
            self.ui.statusBar.removeWidget(button)
            
        #add buttons to statusbar
        for sector in self.dict_sectors.keys():
            button = QPushButton(QIcon(self.icon_path +'/application--arrow.png'), sector, self)
            button.setObjectName(sector)
            button.installEventFilter(self) #listen to mouse movement events for the buttons
            self.ui.statusBar.addWidget(button, 1)
            #load sectors into comboSectors in stackpage
            self.ui.cmbFromSector.addItem(sector)
            self.ui.cmbToSector.addItem(sector)

        #set the from and to sector to the first item in the list
        self.ui.cmbFromSector.setCurrentIndex(0)
        self.ui.cmbToSector.setCurrentIndex(0)

        from_sector_symbols = self.get_symbols_From_sectors()
        for item in from_sector_symbols:
            pct = item.split(":")[1]
            tot_pct += float(pct)
        self.ui.lblFromSector_pct.setText(f'{tot_pct:.2f}% of Portfolio')

        tot_pct = 0.0
        to_sector_symbols = self.get_symbols_To_sectors()
        for item in to_sector_symbols:
            pct = item.split(":")[1]
            tot_pct += float(pct)
        self.ui.lblToSector_pct.setText(f'{tot_pct:.2f}% of Portfolio')


                    
                        

        return

    def closeEvent(self, event):
        # Perform any cleanup or save operations here
        try:
            if self.monitor_thread is not None:
                self.monitor_thread.stop()
                self.monitor_thread.join(timeout=1.0)
            if self.update_thread is not None:
                self.update_thread.stop()
                self.update_thread.join(timeout=1.0)
            if self.command_thread is not None:
                self.command_thread.stop()
                self.command_thread.join(timeout=2.0)
           
        except Exception as e:
            print(e)
        finally:
            event.accept()  # Accept the event to close the window

  



    def lstTerm_update_progress_fn(self, n):
        t_now = datetime.now()
        frm_date = t_now.strftime("%Y-%m-%d %H:%M:%S")
        if os.environ['debug'] == '1':
            self.ui.lstTerm.addItem("Debug - " + frm_date + " - " + n)
        else:
            self.ui.lstTerm.addItem(frm_date + " - " + n)
        

    def updateStatusBar(self, selected_stocks=[]):
        
        #Item[0] =  tickers
        #Item[1]= Total_return
        #Item[2] = stock_quantity_to_sell/buy
        #Item[3]= last price
        #item[4]= your quantities
        #item[5]=today's return
       
       
        # if tblAssets has stocks sellected then only calculate gains for those stocks
        if len(selected_stocks) > 0:
            self.totalGains = sum(item[1] for item in self.selected_stocks)
            self.todayGains = sum(item[5] for item in self.selected_stocks)

        else:
            self.totalGains = sum(item[1] for item in self.ticker_lst)
            self.todayGains = sum(item[5] for item in self.ticker_lst)

        frm_TotalGains = "{0:,.2f}".format(self.totalGains)
        frm_TodayGains = "{0:,.2f}".format(self.todayGains)
        lblGainToday = self.ui.statusBar.findChild(QLabel, "lblStatusBar_pctToday")
        lblGainToday.setText(f"Todays Gains: ${frm_TodayGains}")
        lblGainTotal = self.ui.statusBar.findChild(QLabel, "lblStatusBar_pctT")
        lblGainTotal.setText(f"Total Gains: ${frm_TotalGains}")

     

        lbltotal = self.ui.statusBar.findChild(QLabel, "lblStatusBar")
        lbltotal.setText(f"Total Assets: {self.ui.tblAssets.rowCount()}")

        
        #setup the status table widget
        tbl_Index = self.ui.statusBar.findChild(QTableWidget, "tbl_Index")
       
        
        lst_SPY = []
        count = 0
        SPY_value = r.get_quotes("IVV","last_trade_price")[0]
        SPY_prev_close = r.get_quotes("IVV","previous_close")[0]
        SPY_Gains = (float(SPY_value) - float(SPY_prev_close)) * 100 / float(SPY_prev_close)

        QQQ_value = r.get_quotes("QQQ","last_trade_price")[0]
        QQQ_prev_close = r.get_quotes("QQQ","previous_close")[0]
        QQQ_Gains = (float(QQQ_value) - float(QQQ_prev_close)) * 100 / float(QQQ_prev_close)

        Dow_value = r.get_quotes("DIA","last_trade_price")[0]
        Dow_prev_close = r.get_quotes("DIA","previous_close")[0]
        Dow_Gains = (float(Dow_value) - float(Dow_prev_close)) * 100 / float(Dow_prev_close)

        lst_SPY.append(["QQQ", float(QQQ_value),float(QQQ_Gains)])
        lst_SPY.append(["S&P", float(SPY_value)*10,float(SPY_Gains)])
        lst_SPY.append(["Dow", float(Dow_value)*100,float(Dow_Gains)])


        
        SPY_icon_up = QIcon(f"{self.icon_path}\\up.png")
        SPY_icon_down = QIcon(f"{self.icon_path}\\down.png")
        SPY_icon_equal = QIcon(f"{self.icon_path}\\equal.png")
        
        
        for row in range(len(lst_SPY)):
            for col in range(0,3):
                table_item = QTableWidgetItem()
                if col == 2 and lst_SPY[row][col] > 0.0:
                    # found change item add up/down arrow depending on the value
                    table_item.setText("{0:+.2f}".format(lst_SPY[row][col]))
                    table_item.setIcon(SPY_icon_up)
                elif col == 2 and lst_SPY[row][col] < 0.0:
                    table_item.setText("{0:-.2f}".format(lst_SPY[row][col]))
                    table_item.setIcon(SPY_icon_down)
                elif col == 2 and lst_SPY[row][col] == 0.0:
                    table_item.setText("{0:.2f}".format(lst_SPY[row][col]))
                    table_item.setIcon(SPY_icon_equal)
                else:
                    if col == 0:
                        table_item.setText(lst_SPY[row][col])
                    else:
                        table_item.setText("{0:,.2f}".format(lst_SPY[row][col]))

                
                table_item.setFont(QFont("Arial",8,QFont.Weight.Bold))
                table_item.setBackground(QColor("White"))
                table_item.setForeground(QColor("Black"))
                if row > 0:
                    count += 1
                    tbl_Index.setColumnWidth(2+count, 55)
                    tbl_Index.setItem(0,2+count, table_item)
                elif row == 0:
                    tbl_Index.setItem(0,col, table_item)
                    tbl_Index.setColumnWidth(col, 55)

        tbl_Index.resizeColumnsToContents()
        tbl_Index.width = tbl_Index.horizontalHeader().length()
        tbl_Index.setMinimumWidth(tbl_Index.width+ 20)

        

        return
    
    def updateLstAssets(self):        
        
        #setup timer for status bar and lstAssets
        
        #Item 0 =  tickers
        #Item 1 = Total_return
        #Item 2 = stock_quantity_to_sell/buy
        #Item 3 = last price
        #item[4]= your quantities
        #item[5]=today's return
        #item[6]= average buy price
        #item[7]=%change in price
        #item[8]=change in price since previous close
        #item[9]=stock_name
        #item[10]=% of portfolio
        
        lst_assets = []
        lst_elements_to_update = []
        get_selected_tickers = []
        last_price = ''
        
        #update the list every 10 seconds
        
        # poll shutdown flag during what used to be a fixed 10-second sleep
        for _ in range(100):
            if self._shutting_down or self._selectAll_in_progress:
                return
            if self.command_thread is not None and self.command_thread.is_alive():
                return
            time.sleep(0.1)
        # if there is stocks in list update it every 10 seconds if there is something to update
        if self._shutting_down or self._selectAll_in_progress:
            return
        
        # if there is stocks in list update it every 10 seconds if there is something to update
        if len(self.ticker_lst) != 0: 
            
            # update the table if there is a change in the number of stocks

            
           
            
          
            for idx,item in enumerate(self.ticker_lst):
                if self._shutting_down:
                    return
                last_price = r.get_quotes(item[0], "last_trade_price")[0]
                #only update self.ticker_lst item[3]
                ticker_entry = list(self.ticker_lst[idx])
                ticker_entry[3] = str(last_price) if last_price is not None else '0'
                self.ticker_lst[idx] = ticker_entry
                prev_close = r.get_quotes(item[0], "previous_close")[0]
                if last_price is None or prev_close is None:
                    self.ui.lstTerm.addItem(f"Error: Could not retrieve price for {item[0]}")
                    last_price = 0.0
                    prev_close = 0.0
                    total_return = 0.0
                    todays_return = 0.0
                    quantity = item[4]
                    change = float(last_price) - float(prev_close) 
                    equity = float(item[4]) * float(last_price)   
                    lst_elements_to_update.append([f"{item[9]} ({item[0]})",float(last_price),change,item[4],todays_return,total_return,equity,item[10]])
                    continue
                else:
                    total_return = (float(last_price) - float(item[6])) * float(item[4])
                    todays_return = (float(last_price) - float(prev_close)) * float(item[4]) 
                    quantity = item[4]
                    change = float(last_price) - float(prev_close) 
                    equity = float(item[4]) * float(last_price)   
                    lst_elements_to_update.append([f"{item[9]} ({item[0]})",float(last_price),change,item[4],todays_return,total_return,equity,item[10]])

            #update table
            for row in range(len(lst_elements_to_update)):
                for col in range(len(lst_elements_to_update[row])):
                    table_item = QTableWidgetItem()
                        
                    if col == 2 and lst_elements_to_update[row][col] > 0.0:
                        # found change item add up/down arrow depending on the value
                        table_item.setText("{0:+.2f}".format(lst_elements_to_update[row][col]))
                        table_item.setIcon(QIcon(f"{self.icon_path}\\up.png"))
                        
                    elif col ==2 and lst_elements_to_update[row][col] < 0.0:
                        table_item.setText("{0:-.2f}".format(lst_elements_to_update[row][col]))
                        table_item.setIcon(QIcon(f"{self.icon_path}\\down.png"))
                        
                    elif col == 2 and lst_elements_to_update[row][col] == 0.0:
                        table_item.setText("{0:.2f}".format(lst_elements_to_update[row][col]))
                        table_item.setIcon(QIcon(f"{self.icon_path}\\equal.png"))
                        
                    else:
                        if col == 0:
                            
                            table_item.setText(lst_elements_to_update[row][col])
                        elif col == 7 or col == 8: #percentage column
                            table_item.setText("{0:.2f}".format(lst_elements_to_update[row][col]))
                        else:
                            table_item.setText("{0:,.2f}".format(lst_elements_to_update[row][col]))   
                            
                    #set the table item properties   
                    table_item.setForeground(QColor("white"))
                    table_item.setBackground(QColor("black"))
                    table_item.setFlags(table_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    table_item.setFont(QFont("Arial",12,QFont.Weight.Bold))
                    self.ui.tblAssets.setItem(row,col,table_item)
                

            self.ui.tblAssets.resizeColumnsToContents()
            
            #self.lstupdated_tblAssets = lst_elements_to_update
            
        
            self.updateStatusBar(self.ticker_lst)
            if os.environ["debug"] == '1':
                print("thread running...LstAssets Updated!")
        
        
        
        return
        

    def Show_msgCredentials(self):
        get_cred_file = msgBoxGetCredentialFile()
        button = get_cred_file.exec() #show the popup box for the user to enter account number
        if button == 1:
            wait_cursor = QCursor()
            wait_cursor.setShape(wait_cursor.shape().WaitCursor)

            QApplication.setOverrideCursor(wait_cursor)
            try:
                self.env_path = get_cred_file.edtCred_path.text()
                

                if os.path.exists(self.env_file):
                    #read env_path file
                    with open(self.env_file,"w") as open_file:
                        open_file.write(self.env_path)
                else:
                    os.makedirs(self.data_path,exist_ok=True)
                    os.chmod(self.data_path,0o777)

                    with open(self.env_file,"x") as open_file:
                        open_file.write(self.env_path)
                    os.chmod(self.env_file,0o666)
            
                #load credentials file                                     
                load_dotenv(self.env_path, override=True)
                 #Get account numers and populate comboboxes
                self.account_info = os.environ['account_number']
                self.ui.cmbAccount.clear()
                #There is an account number
                if self.account_info != '':
                    if self.account_info.find(',') != -1:
                        slice_account = self.account_info.split(',')
                        for item in slice_account:
                            self.ui.cmbAccount.addItem(item)
                    else:
                        self.ui.cmbAccount.addItem(self.account_info)
                    
                    self.current_account_num = self.ui.cmbAccount.currentText().split(' ')[0]  
                
                if os.environ['debug'] == '1':
                    self.setWindowTitle(f"PyShares - {self.ver_string} - Debug ({self.env_path})")
                else:
                    self.setWindowTitle(f"PyShares - {self.ver_string} - ({self.env_path})")

                #check to see if the account number has changed
                try:
                    self.ticker_lst = self.get_stocks_from_portfolio(self.current_account_num )
                except Exception as e:
                    if e.args[0] == "Invalid account number":
                        self.ui.lstTerm.addItem(f"Error: {e.args[0]}")
                        return
                    else:
                        
                        #login to Robinhood
                        try:
                            otp = pyotp.TOTP(os.environ['robin_mfa']).now()
                            r.login(os.environ['robin_username'],os.environ['robin_password'], mfa_code=otp)
                        except Exception as e:
                            QMessageBox.critical(self,"Error",f"Error: {e.args[0]}",QMessageBox.StandardButton.Ok)
                            return
                
                #Get account numers and populate comboboxes
                self.account_info = os.environ['account_number']
                self.ui.cmbAccount.clear()
                #There is an account number
                if self.account_info != '':
                    if self.account_info.find(',') != -1:
                        slice_account = self.account_info.split(',')
                        for item in slice_account:
                            self.ui.cmbAccount.addItem(item)
                    else:
                        self.ui.cmbAccount.addItem(self.account_info)
                    
                    self.current_account_num = self.ui.cmbAccount.currentText().split(' ')[0]    
                    try:   
                        self.ticker_lst = self.get_stocks_from_portfolio(self.current_account_num)
                    except Exception as e:
                        if e.args[0] == "Invalid account number":
                            self.ui.lstTerm.addItem(f"Error: {e.args[0]}")
                            return
                        
                    self.print_cur_protfolio(self.ticker_lst)
                    if self.ui.lstTerm.count() > 0:
                        self.ui.lstTerm.clear()

                    #get total gains for the day
                    self.totalGains = sum(item[1] for item in self.ticker_lst if item[1] > 0.0)
                    self.todayGains = sum(item[5] for item in self.ticker_lst if item[5] > 0.0)
                    #setup plot widget
                    self.setup_plot(self.ticker_lst,plot_type=self.current_plot_type)
                    #edit status bar
            
                frm_TotalGains = "{0:,.2f}".format(self.totalGains)
                frm_TodayGains = "{0:,.2f}".format(self.todayGains)

                lbltotal = self.ui.statusBar.findChild(QLabel, "lblStatusBar")
                lbltotal.setText(f"Total Assets: {self.ui.tblAssets.rowCount()}")

                lblGainToday = self.ui.statusBar.findChild(QLabel, "lblStatusBar_pctToday")
                lblGainToday.setText(f"Todays Gains: ${frm_TodayGains}")
                lblGainTotal = self.ui.statusBar.findChild(QLabel, "lblStatusBar_pctT")
                lblGainTotal.setText(f"Total Gains: ${frm_TotalGains}")
            finally:
                #Restore the cursor
                
                QApplication.restoreOverrideCursor()
        else: #user pressed cancel at cridential dialog
            return

      
    def cmbDollarShare_clicked(self):
        lstShares = []
        priceTotal = 0.0

        dollar_share = self.ui.cmbDollarShare.currentText()
        if dollar_share == "Buy in USD":
           self.ui.lblDollarValueToSell.setText("Dollar value of selected Stock(s) to Buy:")
           if self.ui.edtDollarValueToSell.text() != "" and re.match(r'^[0-9]+(\.[0-9]{1,2})?$',self.ui.edtDollarValueToSell.text()):
                self.edtDollarValueToSell_changed()

        elif dollar_share == "Buy in Shares":
            self.ui.lblDollarValueToSell.setText("Amount of Shares to Buy of selected Stock(s):")
            if self.ui.edtDollarValueToSell.text() != "" and re.match(r'^[0-9]+(\.[0-9]{1,2})?$',self.ui.edtDollarValueToSell.text()):
                self.edtDollarValueToSell_changed()
           

           
        return
    def edtAllocAmount_changed(self):
        dollar_value = self.ui.edtAllocAmount.text()
        if dollar_value != "" and re.match(r'^[0-9]+(\.[0-9]{1,2})?$', dollar_value):
            #calculate what percent of your portfolio is the dollar_value
            if self.portfolio_tvalue > 0:
                percent = (float(dollar_value) / self.portfolio_tvalue) * 100
                self.ui.edt_pct_of_portfolio.setText(f"{percent:.2f}%")
            self.ui.btnExecute.setEnabled(True)
            self.ui.btnExecute.setStyleShetet("background-color: green; color: white;")
        else:
            self.ui.btnExecute.setEnabled(False)
            self.ui.btnExecute.setStyleSheet("background-color: grey; color: white;")

    def find_total_equity_for_buysell_amount(self, lst_stock_tickers,dollar_value_to_buy_sell):
        priceTotal = 0.0
        for i in lst_stock_tickers:
            last_price = r.get_quotes(i, "last_trade_price")[0]
            priceTotal += float(last_price) * float(dollar_value_to_buy_sell)

        return priceTotal
    
    def tblAsset_clicked(self):
        stock_names = []
        priceTotal = 0.0

        stock_names = self.get_tickers_from_selected_lstAssets()
        self.selected_stocks = self.find_and_remove(self.ticker_lst,stock_names,1)
       
         #Item[0] =  tickers
        #Item[1]= Total_return
        #Item[2] = stock_quantity_to_sell/buy
        #Item[3]= last price
        #item[4]= your quantities
        #item[5]=today's return
        #item[6]= average buy price
        #item[7]=%change in price
        #item[8]=change in price since previous close
        #items to be updated ["Ticker","Price","Change","Quantity","Today's Return","Total Return"]
        #updated_items = update_current_assets()
        #item[9] = stock name
        #item[10] = % of portfolio
        #item[11] = div yield
        
        
     

        self.ui.edtBuyWithAmount.setReadOnly(True)
        self.ui.edtAmountEst.setReadOnly(True)               
        self.ui.edtLstStocksSellected.setReadOnly(True)
        
        if len(stock_names) >0: 
            
            total_equity = 0.0
            total_equity = sum(float(self.portfolio[sym]['equity']) for sym in stock_names if sym in self.portfolio)
            self.ui.lbltblAsset_sum.setText(f"Equity: ${total_equity:,.2f}")
           

            match self.ui.cmbAction.currentText():
                case "stock_info":
                    # ensure not too much data to plot
                    if not len(stock_names) > 1:
                        self.setup_plot(self.ticker_lst,stock_names,plot_type=self.current_plot_type)
                    

                case "sell_selected":

                    strjoinlst = ",".join(stock_names)
                    self.ui.edtRaiseAmount.setText(strjoinlst)

                    dollar_value_buy_sell = self.ui.edtDollarValueToSell.text()
                    if dollar_value_buy_sell == "" :
                        self.ui.edtBuyWithAmount.setText("0.00")
                    else:
                        priceTotal = self.find_total_equity_for_buysell_amount(stock_names,float(dollar_value_buy_sell))
                        self.ui.edtBuyWithAmount.setText(f"{priceTotal:,.2f}")
                        
                    
                    #self.highlight_stocks_in_table(stock_names)
                    if not len(stock_names) > 1:
                        self.setup_plot(self.ticker_lst,plot_type=self.current_plot_type)
                case "sell_gains_except_x":

                        strjoinlst = ",".join(stock_names)
                        self.ui.edtLstStocksSellected.setText(strjoinlst)
                        
                        n_tickersPerf = self.find_and_remove(self.ticker_lst,stock_names,0)
                        total_return = sum(item[1] for item in n_tickersPerf if item[1] > 0.0)
                        
                        self.ui.edtAmountEst.setText(f"{total_return:,.2f}")

                case "sell_todays_return_except_x":
                    
                        strjoinlst = ",".join(stock_names)
                        self.ui.edtLstStocksSellected.setText(strjoinlst)
        
                        n_tickersPerf = self.find_and_remove(self.ticker_lst,stock_names,0)
                        todays_return = sum(item[5] for item in n_tickersPerf if item[5] > 0.0)
                        
                        self.ui.edtAmountEst.setText(f"{todays_return:,.2f}")
                case "buy_selected_with_x":
                    strjoinlst = ",".join(stock_names)
                    self.ui.edtRaiseAmount.setText(strjoinlst)
                    if not len(stock_names) > 1:
                        self.setup_plot(self.ticker_lst,plot_type=self.current_plot_type)
                case "reinvest_with_gains":
                    if os.path.isfile(self.ui.edtFileBrowse_buyLower.text()):
                        pass
                    else:
                        strjoinlst = ",".join(stock_names)
                        self.ui.edtStocksInFile_BuyLower.setText(strjoinlst)
                case "raise_x_sell_y_dollars":

                    pass

                case "raise_x_sell_y_dollars_except_z":
                    strjoinlst = ",".join(stock_names)
                    self.ui.edtRaiseAmount.setText(strjoinlst)

                case _:
                    self.ui.lblRaiseAmount.setVisible(False)
                    self.ui.lblDollarValueToSell.setVisible(False)
                    self.ui.edtRaiseAmount.setVisible(False)
                    self.ui.edtDollarValueToSell.setVisible(False)
                    self.ui.lblRaiseAmount.setText("")
                    self.ui.edtRaiseAmount.setText("")
                    self.ui.lblBuyWithAmount.setVisible(False)
                    self.ui.edtBuyWithAmount.setVisible(False)
        else:   #len(selected_tickers) == 0 #default
            self.ui.edtStocksInFile_BuyLower.setText("")
            self.ui.lbltblAsset_sum.setText(f"Equity: $0.00")
            self.selected_stocks = []            
            self.ui.edtBuyWithAmount.setText("0.0")
            self.ui.edtRaiseAmount.setText("")

        
        self.updateStatusBar(self.selected_stocks)
        return

                
        
    def recalculate_estimated_amount(self):
        priceTotal = 0.0
        Total_quantity = 0.0
        dollar_share = self.ui.cmbDollarShare.currentText()
        self.new_lstShares = []

       

        if re.match(r'^\d+$',self.ui.edtDollarValueToSell.text()):
            self.ui.btnExecute.setEnabled(True)
            lstShares = self.ui.edtRaiseAmount.text().split(',')
            ticker_copy_include_list = self.find_and_remove(self.ticker_lst,lstShares,1)
            #user entered new symbols that are not in the list
            if ticker_copy_include_list is None or len(ticker_copy_include_list) == 0:
                last_price = r.get_quotes(lstShares, "last_trade_price")
                for index, item in enumerate(lstShares):
                    est_price = last_price[index]
                    if dollar_share == "Buy in USD":
                        Total_quantity = float(self.ui.edtDollarValueToSell.text()) / float(est_price)
                        frm_total_quantity = "{0:.2f}".format(Total_quantity)
                        priceTotal += float(est_price) * Total_quantity
                        #Item 0 =  tickers
                        #Item 2 = stock_quantity_to_sell/buy
                        #Item 3 = last price
                        self.new_lstShares.append((item, frm_total_quantity, est_price))
                    elif dollar_share == "Buy in Shares":
                        priceTotal += float(est_price) * float(self.ui.edtDollarValueToSell.text())
                        frmPriceTotal = "{0:.2f}".format(priceTotal)
                        self.new_lstShares.append((item, float(self.ui.edtDollarValueToSell.text()), est_price))

                self.ui.edtBuyWithAmount.setText(f"{priceTotal:,.2f}")
                
                #create new list to hold the stocks and quantities to buy
                
                return

            if dollar_share == "Buy in USD":
                #get comma separated stocks and get a total estimate it would cost to buy the shares
            
                for item in ticker_copy_include_list:
                        #get latest price of the stock
                        est_price = item[3]
                        Total_quantity = float(self.ui.edtDollarValueToSell.text()) / float(est_price)
                        priceTotal += float(est_price) * Total_quantity
                
                self.ui.edtBuyWithAmount.setText(f"{priceTotal:.2f}")
               
            
            elif dollar_share == "Buy in Shares":
            
                #get comma separated stocks and get a total estimate it would cost to buy the shares
            
                for item in ticker_copy_include_list:
                        #get est latest price from new ticker_copy_include_list
                        est_price = item[3]
                        priceTotal += float(est_price) * float(self.ui.edtDollarValueToSell.text())

                
                self.ui.edtBuyWithAmount.setText(f"{priceTotal:.2f}")
       

           
            

        return

    def clear_all_clicked(self):
        self._selectAll_in_progress = False
        
        self.ui.edtReinvestAmount_buyLower.setEnabled(True)
        self.ui.edtStocksInFile_BuyLower.setEnabled(True)
        self.ui.tblAssets.viewport().setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        #Reinvest page--------------------------------
        if self.ui.cmbAction.currentText() == "reinvest_with_gains":
            self.ui.tblAssets.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
        self.ui.edtReinvestAmount_buyLower.setEnabled(True)
        self.ui.edtStocksInFile_BuyLower.setEnabled(True)
        self.ui.edtStocksInFile_BuyLower.setText("")
        self.ui.edtReInvestValue.setText("")
        self.ui.edtFileBrowse_buyLower.setText("")
        self.ui.edtReinvestAmount_buyLower.setText("")
        #---------------------------------
        
        #tooltip is open so close it
        if self.tooltip is not None and self.tooltip.isVisible():
            self.tooltip.close()
            self.tooltip = None
            self.ui.tblAssets.viewport().setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        if self.ui.cmbAction.currentText() == "stock_info": 
            self.ui.tblAssets.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        else:
            self.ui.tblAssets.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)

        self.ui.lbltblAsset_sum.setText(f"Equity: $0.00")
        self.ui.tblAssets.clearSelection()
        self.selected_stocks = [] 
        self.ui.edtRaiseAmount.setText("")
        self.ui.edtDollarValueToSell.setText("")
        self.ui.edtBuyWithAmount.setText("")
        self.ui.edtLstStocksSellected.setText("")
        self.ui.edtLstStocksSellected.setReadOnly(False)
        self.ui.edtLstStocksSellected.setStyleSheet("background-color: white;")
        self.ui.edtFileBrowse.setText("")
        self.ui.edtAmountEst.setText("")
        self.ui.lstTerm.clear()
        self.ui.lbltblAsset_sum.setText("Equity: $0.00")
        self.ui.btnExecute.setEnabled(False)
        self.ui.btnExecute.setStyleSheet("background-color: grey; color: white;")
        self.setup_plot(self.ticker_lst,plot_type=self.current_plot_type)
        self.selected_stocks = []
        self.updateStatusBar(self.selected_stocks)
        

    def closeMenu_clicked(self):
       
        cursor = QCursor()
        cursor.setShape(cursor.shape().WaitCursor)
       
        try:
            QApplication.setOverrideCursor(cursor)
            
            self._shutting_down = True
            # stop timers first
            if hasattr(self, "seq_timer"):
                self.seq_timer.stop()
            if self.monitor_thread is not None:
                self.monitor_thread.stop()
                self.monitor_thread.join(timeout=1.0)
            if self.update_thread is not None:
                self.update_thread.stop()
                self.update_thread.join(timeout=1.0)
            if self.command_thread is not None:
                self.command_thread.stop()
                self.command_thread.join(timeout=2.0)
          

           
            self.close()
        except Exception as e:
            print(e)
            
        finally:
            QApplication.restoreOverrideCursor()
            QApplication.quit()
        #close the robinhood session
        
        #close the app
        

    def ledit_Iteration_textChanged(self):
        text = self.ui.ledit_Iteration.text()
        todays_stockReturn = 0.0
        total_return = 0.0
        
        #Item[0] =  tickers
        #Item[1]= Total_return
        #Item[2] = stock_quantity_to_sell/buy
        #Item[3]= last price
        #item[4]= your quantities
        #item[5]=today's return
        #item[6]= 1 year history
        #item[7]= average buy price
        #item[8]=%change in price
        #item[9]=change in price since previous close
        #items to be updated ["Ticker","Price","Change","Quantity","Today's Return","Total Return"]
        #updated_items = update_current_assets()
        #item[10] = stock name
        #item[11] = % of portfolio
        #item[12] = div yield
        
        if re.match(r'^[0-9]+$',text) and text != "":
            iteration = int(text)
            self.totalGains,self.todayGains = self.cal_today_total_gains(self.ticker_lst)
            match self.ui.cmbAction.currentText():
                case "sell_gains":
                    new_total_return = self.totalGains * iteration
                    self.ui.edtBuyWithAmount.setText(f"${new_total_return:,.2f}")
                case "sell_todays_return":
                    new_todays_stockReturn = self.todayGains * iteration
                    self.ui.edtBuyWithAmount.setText(f"${new_todays_stockReturn:,.2f}")

            self.ui.btnExecute.setEnabled(True)
            self.ui.btnExecute.setStyleSheet("background-color: green; color: white;")

        else:
            self.ui.edtBuyWithAmount.setText("$0.00")
            self.ui.btnExecute.setEnabled(False)
            self.ui.btnExecute.setStyleSheet("background-color: grey; color: white;")
        return


    def edtBuyWith_changed(self):
       #if the edtBuyWith textbox is empty and the raise amount and dollar value to sell textboxes are not empty then enable the execute button
        # if self.ui.edtBuyWith.text() == "" and self.ui.edtRaiseAmount.text() != "" and re.match(r'^[0-9]+$',self.ui.edtDollarValueToSell.text()) and \
        #     self.ui.edtDollarValueToSell.text() != "":
        #     self.ui.btnExecute.setEnabled(True)
        #     self.ui.btnExecute.setStyleSheet("background-color: green; color: white;")  # Change background to green

        # elif re.match(r'^[1-9]+$',self.ui.edtBuyWith.text()) and self.ui.edtRaiseAmount.text() != "" and self.ui.edtDollarValueToSell.text() != "":
        #     self.ui.btnExecute.setEnabled(True)
        #     self.ui.btnExecute.setStyleSheet("background-color: green; color: white;")
        
            
        # if perform_action == "stock_info":
            
        #     elif perform_action == "sell_selected":
                
        #     elif perform_action == "sell_gains_except_x":
        #     elif perform_action == "sell_todays_return":
            
        #     elif perform_action == "raise_x_sell_y_dollars":
        #     elif perform_action == "raise_x_sell_y_dollars_except_z":
        #     elif perform_action == "reinvest_with_gains":
        #     elif perform_action == "buy_x_with_y_amount":
        
        #     elif perform_action == "buy_selected_with_x":
            
        #     else: #default
        
        return

    def edtBuyWithAmount_changed(self):
       

        if re.match(r'^[1-9]+$',self.ui.edtBuyWithAmount.text()) and self.ui.cmbAction.currentText() != "stock_info":
            self.ui.btnExecute.setEnabled(True)
            self.ui.btnExecute.setStyleSheet("background-color: green; color: white;")
      
      


          
        self.ui.btnExecute.setEnabled(True)
        self.ui.btnExecute.setStyleSheet("background-color: green; color: white;")
        #  if perform_action == "stock_info":
        
        # elif perform_action == "sell_selected":
            
        # elif perform_action == "sell_gains_except_x":
        # elif perform_action == "sell_todays_return":
        
        # elif perform_action == "raise_x_sell_y_dollars":
        # elif perform_action == "raise_x_sell_y_dollars_except_z":
        # elif perform_action == "reinvest_with_gains":
        # elif perform_action == "buy_x_with_y_amount":
      
        # elif perform_action == "buy_selected_with_x":
          
        # else: #default
        

    def edtDollarValueToSell_changed(self):
        stock_tickers = []
        priceTotal = 0.0
        # Function body required to avoid 'expected indented block' error
       

        if self.ui.cmbAction.currentText() == "buy_selected_with_x":
            if self.ui.edtDollarValueToSell.text() != "0" and re.match(r'^[0-9]+$',self.ui.edtDollarValueToSell.text()) and self.ui.edtRaiseAmount.text() != "":
                self.recalculate_estimated_amount()
                self.ui.btnExecute.setEnabled(True)
                self.ui.btnExecute.setStyleSheet("background-color: green; color: white;")
            else:
                self.ui.btnExecute.setEnabled(False)
                self.ui.btnExecute.setStyleSheet("background-color: grey; color: white;")
                self.ui.edtBuyWithAmount.setText("$0")
                
        elif self.ui.cmbAction.currentText() == "sell_selected":
            if self.ui.edtDollarValueToSell.text() != "0" and re.match(r'^[0-9]+$',self.ui.edtDollarValueToSell.text()) and self.ui.edtRaiseAmount.text() != "":
                self.recalculate_estimated_amount()  
                self.ui.btnExecute.setEnabled(True)
                self.ui.btnExecute.setStyleSheet("background-color: green; color: white;")
            else:
                self.ui.btnExecute.setEnabled(False)
                self.ui.btnExecute.setStyleSheet("background-color: grey; color: white;")

        
        # if perform_action == "stock_info":
        
        # elif perform_action == "sell_selected":
            
        # elif perform_action == "sell_gains_except_x":
        # elif perform_action == "sell_todays_return":
        
        # elif perform_action == "raise_x_sell_y_dollars":

        #     elif perform_action == "raise_x_sell_y_dollars_except_z":
        #     elif perform_action == "reinvest_with_gains":
        # elif perform_action == "buy_x_with_y_amount":
        
        # elif perform_action == "buy_selected_with_x":
        
        # else: #default
        
                

    def edtRaiseAmount_changed(self):
        
        if re.match(r'^[A-Z,]+$',self.ui.edtRaiseAmount.text()) and self.ui.cmbAction.currentText() != "stock_info":
            return

        if re.match(r'^[1-9]+$',self.ui.edtRaiseAmount.text()) and self.ui.cmbAction.currentText() != "stock_info":
            self.ui.btnExecute.setEnabled(True)
            self.ui.btnExecute.setStyleSheet("background-color: green; color: white;")  # Change background to green
        else:
            self.ui.btnExecute.setEnabled(False)
            self.ui.btnExecute.setStyleSheet("background-color: grey; color: white;")  # Change background to grey

        self.ui.btnExecute.setEnabled(True)
        self.ui.btnExecute.setStyleSheet("background-color: green; color: white;")  # Change background to green
        #  if perform_action == "stock_info":
        
        # elif perform_action == "sell_selected":

        # elif perform_action == "sell_gains_except_x":
        # elif perform_action == "sell_todays_return":
        
        # elif perform_action == "raise_x_sell_y_dollars":
        # elif perform_action == "raise_x_sell_y_dollars_except_z":
        # elif perform_action == "reinvest_with_gains":
        # elif perform_action == "buy_x_with_y_amount":
      
        # elif perform_action == "buy_selected_with_x":
        #   
        # else: #default

    def setup_plot(self,tickersPerf = [],sellected_tickets = [],plot_type = "Bar (Sector Colors)"):
        frm_h = self.plot_scroll.height()
        frm_w = self.plot_scroll.width()

        self.plot.figure.clf()  # Clear the existing figure
        error_msg = self.plot.add_plot_to_figure(tickersPerf,sellected_tickets,plot_type, self.dict_sectors,frm_h,frm_w)
        if error_msg != "":
            self.ui.lstTerm.addItem(f"Error: {error_msg}")
    
        self.plot.draw()
       
        return


    def StoreAccounts(self):
        msgBox = msgBoxGetAccounts()
        button = msgBox.exec() #show the popup box for the user to enter account number
        if button == 1: #add account number to the combobox and store in the .env file
            self.ui.cmbAccount.addItem(msgBox.ledit.text())
           
            if self.account_info != "":
                new_str_account = self.account_info + "," + msgBox.ledit.text()            
                set_key(self.env_path,'account_number',new_str_account)
            else:
                
                set_key(self.env_path,'account_number',msgBox.ledit.text()) 

        return
       
  


    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print("THREAD COMPLETE!")
   
              
    def Cancel_operation(self):
        # Clear any pending sequence on Cancel
        if self.command_thread and self.command_thread.is_alive():
            self.command_thread.stop()
        self.op_queue.clear()
        self.seq_timer.stop()
        self.ui.btnExecute.setStyleSheet("background-color: green; color: white;")
        self.ui.btnExecute.setText("Execute ...")
        self.ui.btnExecute.setEnabled(False)
        return
    
    def btnExecute_clicked(self):
        if self.ui.btnExecute.text() == "Cancel":
            self.Cancel_operation()
        elif self.ui.btnExecute.text() == "Execute ...":    
            
            num_iter,lst = self.check_and_read_conditions_met()

            if lst == ['err']:
                return
         
            match self.ui.cmbAction.currentText():
                case "sell_selected":
                    self.Execute_operation("sell_selected",num_iter,lst)
                     #check is all required values are entered

                case "sell_gains_except_x":
                    self.Execute_operation("sell_gains_except_x",num_iter,lst)

                case "sell_todays_return_except_x":
                    self.Execute_operation("sell_todays_return_except_x",num_iter,lst)

                case "buy_selected_with_x":
                    self.Execute_operation("buy_selected_with_x",num_iter,lst)

                case "reinvest_with_gains":
                    self.Execute_operation("reinvest_with_gains",num_iter,lst)

                case "allocate_reallocate_to_sectors":
                    self.symbols_from = [item.split(":")[0] for item in self.alloc_from]
                    self.symbols_to = [item.split(":")[0] for item in self.alloc_to]

                    self.Execute_operation("raise_x_sell_y_dollars_except_z",num_iter,self.symbols_from)

                    # Queue the second op to run after the first finishes (no extra confirm)
                    self.op_queue = [("buy_selected_with_x", self.symbols_to)]
                    self._seq_num_iter = num_iter
                    self.seq_timer.start()             
                    

                case "raise_x_sell_y_dollars_except_z":
                    self.Execute_operation("raise_x_sell_y_dollars_except_z",num_iter,lst)

                case _:
                    self.Execute_operation(None) #default

    def write_to_file(self, data):
        method_name = self.ui.cmbAction.currentText() 
        t_now = datetime.now()
        frm_date = t_now.strftime("%Y-%m-%d_%H_%M_%S")
        file_path = os.path.join(self.data_path, f"{method_name}_{self.current_account_num}_{frm_date}.csv")
        with open(file_path,"w") as file_write:
            stocks_format = "\n".join(data)
            file_write.write(f"{stocks_format}")

    def cmbAction_clicked(self):
        #Item[0] =  tickers
        #Item[1]= Total_return
        #Item[2] = stock_quantity_to_sell/buy
        #Item[3]= last price
        #item[4]= your quantities
        #item[5]=today's return
        #item[5]= 1 year history
        #item[6]= average buy price
        #item[7]=%change in price
        #item[8]=change in price since previous close
        #items to be updated ["Ticker","Price","Change","Quantity","Today's Return","Total Return"]
        #updated_items = update_current_assets()
        #item[9] = stock name

        allStockReturn = 0.0
        todays_stockReturn = 0.0

        perform_action = self.ui.cmbAction.currentText()
        #clear all fields and reset to default
        
        self.ui.edtRaiseAmount.setVisible(False)
        self.ui.lblRaiseAmount.setVisible(False)
        self.ui.edtRaiseAmount.setEnabled(True)
        self.ui.edtRaiseAmount.setReadOnly(False)
        self.ui.edtDollarValueToSell.setVisible(False)
        self.ui.lblDollarValueToSell.setVisible(False)
        self.ui.lblBuyWithAmount.setVisible(False)
        self.ui.edtBuyWithAmount.setVisible(False)
        self.ui.lblbuyWith.setVisible(False)
        self.ui.edtBuyWith.setVisible(False)
        self.ui.cmbDollarShare.setVisible(False)
        self.ui.tblAssets.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
       
        
        match perform_action:
            case "stock_info":
                self.ui.stackPage.setCurrentIndex(4)
                
                self.ui.edtRaiseAmount.setVisible(False)
                self.ui.lblRaiseAmount.setVisible(False)
                self.ui.edtDollarValueToSell.setVisible(False)
                self.ui.lblDollarValueToSell.setVisible(False)
                self.ui.lblBuyWithAmount.setVisible(False)
                self.ui.edtBuyWithAmount.setVisible(False)
                self.ui.lblbuyWith.setVisible(False)
                self.ui.edtBuyWith.setVisible(False)
                self.ui.cmbDollarShare.setVisible(False)
                
                
                self.setup_plot(self.ticker_lst,plot_type=self.current_plot_type)  
            case "sell_selected":
                self.ui.stackPage.setCurrentIndex(2)
                
                self.ui.lblRaiseAmount.setText("Sell Selected Asset:")
                self.ui.lblRaiseAmount.setToolTip("Sell (,) Comma separated list of tickers")
                self.ui.lblRaiseAmount.setVisible(True)
                self.ui.edtRaiseAmount.setVisible(True)
                self.ui.edtRaiseAmount.setReadOnly(True)

                self.ui.edtBuyWithAmount.setText("0.00")          
                self.ui.edtBuyWithAmount.setVisible(True)
                self.ui.edtBuyWithAmount.setEnabled(False)   
                self.ui.edtBuyWithAmount.setForegroundRole(QPalette.ColorRole.Shadow)
                self.ui.lblBuyWithAmount.setText("Amount (est.)(USD):")
                self.ui.lblBuyWithAmount.setVisible(True)

                self.ui.lblDollarValueToSell.setText("Dollar value to Sell of each Stock(s):")
                self.ui.lblDollarValueToSell.setVisible(True)
                self.ui.edtDollarValueToSell.setVisible(True)
            
                
                self.ui.lblbuyWith.setVisible(False)
                self.ui.edtBuyWith.setVisible(False)
                self.ui.edtBuyWith.setText("")   

                self.ui.tblAssets.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)             
               
            case "sell_gains_except_x":
                self.ui.stackPage.setCurrentIndex(1)
                total_return,_ = self.cal_today_total_gains(self.ticker_lst)

                self.ui.edtAmountEst.setText(f"${total_return:,.2f}")          
                self.ui.edtAmountEst.isEnabled = False
                self.ui.edtAmountEst.setForegroundRole(QPalette.ColorRole.Shadow)   

                self.ui.tblAssets.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
                self.ui.btnExecute.setStyleSheet("background-color: green; color: white;")  # Change background to green             
                self.ui.btnExecute.setEnabled(True)  # Disable the button initially
               
            case "sell_todays_return_except_x":
                self.ui.stackPage.setCurrentIndex(1)
                _,todays_stockReturn = self.cal_today_total_gains(self.ticker_lst)
                self.ui.edtAmountEst.setText(f"${todays_stockReturn:,.2f}")
                self.ui.edtAmountEst.isEnabled = False
                self.ui.edtAmountEst.setForegroundRole(QPalette.ColorRole.Shadow)
                
                self.ui.tblAssets.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
                self.ui.btnExecute.setStyleSheet("background-color: green; color: white;")
                self.ui.btnExecute.setEnabled(True)
                
            case "buy_selected_with_x":
                self.ui.stackPage.setCurrentIndex(2)
                self.ui.lblRaiseAmount.setText("Buy Selected Asset:")
                self.ui.lblRaiseAmount.setToolTip("Buy (,) Comma separated list of tickers")
                self.ui.lblRaiseAmount.setVisible(True)
                self.ui.edtRaiseAmount.setVisible(True)
                self.ui.lblbuyWith.setVisible(True)
                self.ui.edtBuyWith.setVisible(True)
                self.ui.lblDollarValueToSell.setText("Dollar value of selected Stock(s) to Buy:")
                self.ui.lblDollarValueToSell.setVisible(True)
                self.ui.edtDollarValueToSell.setVisible(True)
                self.ui.lblBuyWithAmount.setText("Amount (est.)(USD):")
                self.ui.lblBuyWithAmount.setVisible(True)
                self.ui.edtBuyWithAmount.setVisible(True)
                self.ui.edtBuyWithAmount.setEnabled(False)
                self.ui.cmbDollarShare.setVisible(True)
                self.ui.cmbDollarShare.setToolTip("Sell/Buy in US Dollars/Shares")
                self.ui.tblAssets.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
              
            case "reinvest_with_gains":
                self.ui.btnExecute.setEnabled(True)
                self.ui.cmbReInvest.addItems(["10%","20%","30%","40%","50%","60%","70%","80%","90%","100%"])
                self.ui.stackPage.setCurrentIndex(3)
                self.ui.tblAssets.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
                
                
            case "allocate_reallocate_to_sectors":
                self.ui.stackPage.setCurrentIndex(0)
            case "raise_x_sell_y_dollars_except_z":
                self.ui.stackPage.setCurrentIndex(2)
                self.ui.lblRaiseAmount.setText("Sell Asset Except:")
                self.ui.lblRaiseAmount.setToolTip("Sell Except (,) Comma separated list of tickers")
                self.ui.lblRaiseAmount.setVisible(True)
                self.ui.edtRaiseAmount.setVisible(True)
                self.ui.lblDollarValueToSell.setText("Dollar value of Stock to Sell:")
                self.ui.lblDollarValueToSell.setVisible(True)
                self.ui.edtDollarValueToSell.setVisible(True)
                self.ui.edtBuyWithAmount.setVisible(True)
                self.ui.edtBuyWithAmount.setEnabled(True)
                self.ui.lblBuyWithAmount.setText("Raise Amount (USD):")
                self.ui.lblBuyWithAmount.setVisible(True)
                self.ui.lblbuyWith.setVisible(False)
                self.ui.edtBuyWith.setVisible(False)
                self.ui.edtBuyWith.setText("")
                self.ui.edtRaiseAmount.setReadOnly(False)
                self.ui.tblAssets.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)   
        #self.clear_all_clicked()
        return
        
   


    def account_clicked(self):
        #check to see if the account number has changed
        #if it has update the lstAsset list and plot
        # if NOT return
        if self.current_account_num != self.ui.cmbAccount.currentText().split(' ')[0]:
            wait_cursor = QCursor()
            wait_cursor.setShape(wait_cursor.shape().WaitCursor)
           
            QApplication.setOverrideCursor(wait_cursor)
            try:
                self.current_account_num = self.ui.cmbAccount.currentText().split(' ')[0]
                accountNum = self.current_account_num
                if self.ui.tblAssets.rowCount() > 0:
                    self.ui.tblAssets.clear()
                #get tickers in portfolio
                try:
                    
                    self.ticker_lst = self.get_stocks_from_portfolio(accountNum)
                    self.print_cur_protfolio(self.ticker_lst)
                    self.totalGains,self.todayGains = self.cal_today_total_gains(self.ticker_lst)
                    self.setupStatusbar()
                    tickersPerf = self.ticker_lst
                    
                    if self.ui.lstTerm.count() > 0:
                        self.ui.lstTerm.clear()

                    self.setup_plot(tickersPerf,plot_type=self.current_plot_type)
                   # self.updateStatusBar(tickersPerf)
                except Exception as e:
                    if e.args[0] == "No stocks in account":
                        self.ui.lstTerm.addItem(f"Error: {e.args[0]}")
                        self.print_cur_protfolio(self.ticker_lst)
                        self.setup_plot(self.ticker_lst,plot_type=self.current_plot_type)
                        #self.updateStatusBar(self.ticker_lst)
                    
                    
               
               
            finally:
                QApplication.restoreOverrideCursor()
        
    
    #Add the sequence helpers 
    def _check_and_run_next(self):
        if (self.command_thread is None) or (not self.command_thread.is_alive()):
            if self.op_queue:
                self._run_next_op()
            else:
                self.seq_timer.stop()

    def _run_next_op(self):
        if not self.op_queue:
            self.seq_timer.stop()
            self.ui.btnExecute.setText("Execute ...")
            self.ui.btnExecute.setStyleSheet("background-color: green; color: white;")
            return
        method, lst = self.op_queue.pop(0)
        # Start next without confirmation
        self.Execute_operation(method, self._seq_num_iter, lst, ask_confirm=False)
       
    def Execute_operation(self,method_name = None,num_iter = 1,lst=None, ask_confirm=True):
        
          #Item[0] =  tickers
        #Item[1]= Total_return
        #Item[2] = stock_quantity_to_sell/buy
        #Item[3]= last price
        #item[4]= your quantities
        #item[5]=today's return
        #item[6]= 1 year history
        #item[7]= average buy price
        #item[8]=%change in price
        #item[9]=change in price since previous close
        #items to be updated ["Ticker","Price","Change","Quantity","Today's Return","Total Return"]
        #updated_items = update_current_assets()
        #item[10] = stock name
        #item[11] = % of portfolio
        #item[12] = div yield

        sell_list = []
        
        msg = ""
        raise_amount = ""
        reinvest_amount = ""
        dollar_value_to_sell = 0.0
        buying_with_amount = ""
        preview_sellbuy_list = []

        #populate variables based on method name
        if lst is None:
            lst = ["Don't Care"]
        
        if self.ui.cmbAction.currentText() == "allocate_reallocate_to_sectors":
            raise_amount = self.ui.edtAllocAmount.text()
            dollar_value_to_sell = 100.0
            if self.raised_amount != "":
                buying_with_amount = self.raised_amount
            else:
                buying_with_amount = raise_amount

        elif self.ui.cmbAction.currentText() == "raise_x_sell_y_dollars_except_z":
            raise_amount = self.ui.edtBuyWithAmount.text()
            dollar_value_to_sell = self.ui.edtDollarValueToSell.text()
            buying_with_amount = "Not Used"
        elif self.ui.cmbAction.currentText() == "reinvest_with_gains":
            buying_with_amount = float(self.ui.edtReInvestValue.text().replace("$","").replace(",",""))
            
            dollar_value_to_sell = self.ui.cmbReInvest.currentText().replace("%","")
            raise_amount = "Not Used"
        else:
            raise_amount = self.ui.edtRaiseAmount.text()
            if  raise_amount == "":
                raise_amount = "Not Used"
            dollar_value_to_sell = self.ui.edtDollarValueToSell.text()
            if dollar_value_to_sell == "":
                dollar_value_to_sell = "Not Used"
            buying_with_amount = self.ui.edtBuyWith.text()
            

        if ask_confirm:
            match method_name:
                case "sell_selected":
                    msg =   f"Are you sure you want to execute operation '{self.ui.cmbAction.currentText()}'\n" \
                            f"Selected: {lst}\n" \
                            f"Sell Amount: {self.ui.edtBuyWithAmount.text()}\n" \
                            f"\nPreview:"
                    
                case "sell_gains_except_x":
                    msg =   f"Are you sure you want to execute operation '{self.ui.cmbAction.currentText()}'\n" \
                            f"Except: {lst}\n" \
                            f"Sell Amount: {self.ui.edtAmountEst.text()}\n" \
                            f"\nPreview:"
                    
                case "sell_todays_return_except_x":
                    msg =   f"Are you sure you want to execute operation '{self.ui.cmbAction.currentText()}'\n" \
                            f"Except: {lst}\n" \
                            f"Sell Amount: {self.ui.edtAmountEst.text()}\n" \
                            f"\nPreview:"
                case "buy_selected_with_x":
                    msg =   f"Are you sure you want to execute operation '{self.ui.cmbAction.currentText()}'\n" \
                            f"Except: {lst}\n" \
                            f"Buy Amount: {self.ui.edtBuyWithAmount.text()}\n" \
                            f"\nPreview:\n"
                case "reinvest_with_gains":
                    buy_list,spent = self.reinvest_with_gains_prev(num_iter,lst,raise_amount,dollar_value_to_sell,buying_with_amount)
                    name_lst = self.ui.edtStocksInFile_BuyLower.text()
                    msg =   f"Are you sure you want to execute operation '{self.ui.cmbAction.currentText()}'\n" \
                            f"Selected: {name_lst}\n" \
                            f"Reinvest: {buying_with_amount} by buying {dollar_value_to_sell}% of a previous sale of the stock\n" \
                            f"Money spent: {spent}\n" \
                            f"\nPreview:\n"
                        
                    preview_sellbuy_list = [f"{item[0]}: buy {item[1]} shares" for item in buy_list]
                    lst = buy_list
                case "allocate_reallocate_to_sectors":
                    pass
                case "raise_x_sell_y_dollars_except_z":
                    # use allocate message
                    if self.ui.cmbAction.currentText() == "allocate_reallocate_to_sectors": 
                        sell_list,self.raised_amount = self.raise_x_sell_y_dollars_except_z_prev(num_iter,self.current_account_num,lst,raise_amount,dollar_value_to_sell,buying_with_amount)
                        buy_list,raised_amount = self.buy_selected_with_x_prev(num_iter,self.current_account_num,self.symbols_to,raise_amount,dollar_value_to_sell,buying_with_amount)
                        if sell_list or buy_list: 
                            format_sell_list = [f"{item[0]}: sell {item[1]} shares" for item in sell_list]
                            format_buy_list = [f"{item[0]}: buy {item[1]} shares" for item in buy_list]
                            preview_sellbuy_list = format_sell_list + format_buy_list
                            
                        if float(self.raised_amount) < float(raise_amount):
                            msg =  f"Are you sure you want to execute operation '{self.ui.cmbAction.currentText()}'\n" \
                                    f"Except: {lst}\n" \
                                    f"Allocate Amount: Can only allocate ${self.raised_amount} when selling ${dollar_value_to_sell} of each share, reduce share count to raise more\n" \
                                    f"\nPreview:\n" 
                                    
                        else:
                            msg =   f"Are you sure you want to execute operation '{self.ui.cmbAction.currentText()}'\n" \
                                f"Allocate from Sector '{self.ui.cmbFromSector.currentText()}' - {self.symbols_from} to Sector '{self.ui.cmbToSector.currentText()}' - {self.symbols_to}\n" \
                                f"Allocate Amount: {raise_amount}\n" \
                                f"\nPreview:\n"
                                
                    else:
                        #preview function
                        sell_list,self.raised_amount = self.raise_x_sell_y_dollars_except_z_prev(num_iter,self.current_account_num,lst,raise_amount,dollar_value_to_sell,buying_with_amount)
                        if sell_list: 
                            format_sell_list = [f"{item[0]}: sell {item[1]} shares" for item in sell_list if float(item[1]) != 0.0]
                            preview_sellbuy_list = format_sell_list
                            if float(self.raised_amount) < float(raise_amount):
                                msg =  f"Are you sure you want to execute operation '{self.ui.cmbAction.currentText()}'\n" \
                                        f"Except: {lst}\n" \
                                        f"Sell Amount: Can only raise ${self.raised_amount} when selling ${dollar_value_to_sell} of each share, reduce dollar amount to raise more money\n" \
                                        f"\nPreview:\n"
                            else:
                                msg =   f"Are you sure you want to execute operation '{self.ui.cmbAction.currentText()}'\n" \
                                        f"Except: {lst}\n" \
                                        f"Sell Amount: {raise_amount}\n" \
                                        f"\nPreview:\n"

                            lst = [item for item in sell_list if float(item[1]) != 0.0]
                case _: #default
                    pass
                
            confirm = confirmMsgBox(msg,preview_sellbuy_list, self)
            button = confirm.exec() #show the popup box for the user to enter account number

        if button != 1: #if user did NOT click yes then return else execute
            self.ui.btnExecute.setText("Execute ...")
            self.ui.btnExecute.setStyleSheet("background-color: green; color: white;")
            return            
        
        else: # no confirmation needed

            self.ui.btnExecute.setText("Cancel")
            self.ui.btnExecute.setStyleSheet("background-color: red; color: white;")
            
            if self.ui.cmbAction.currentText() == "allocate_reallocate_to_sectors":
                self.ui.lstTerm.addItem(f"Allocating/Reallocating sectors From: ' {self.ui.cmbFromSector.currentText()} ' To: ' {self.ui.cmbToSector.currentText()} ' Amount: ${self.ui.edtAllocAmount.text()} '")
            else:
                self.ui.lstTerm.clear()

            #call the method to execute
            if method_name is None:
                name_of_method = self.ui.cmbAction.currentText()
            else:
                name_of_method = method_name

            fn = getattr(self, name_of_method)
            self.command_thread = CommandThread(fn,num_iter,self.current_account_num,lst,raise_amount,dollar_value_to_sell,buying_with_amount) # Any other args, kwargs are passed to the run function
            # start thread
            self.command_thread.start()

            return 
            


    def SelectAll_clicked(self):
        #select all items in the list
        self.ui.tblAssets.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
        self.ui.tblAssets.selectAll()
        self.ui.tblAssets.setFocus()
        self.tblAsset_clicked()
        self._selectAll_in_progress = True
        return
    def print_cur_protfolio(self, curlist):
       
        #Item 0 =  tickers
        #Item 1 = Total_return
        #Item 2 = stock_quantity_to_sell/buy
        #Item 3 = last price
        #item[4]= your quantities
        #item[5]=today's return
        #item[6]= 1 year history <- removed
        #item[6]= average buy price
        #item[7]=%change in price
        #item[8]=change in price since previous close
        #item[9]=stock_name
        #item[10]=% of portfolio
        
        join_list = []
        
        lst_elements_to_update = []
        #set header
        
        
        
        self.ui.tblAssets.setColumnCount(8)
        self.ui.tblAssets.setRowCount(len(curlist))
        

        self.ui.tblAssets.setHorizontalHeaderLabels(["Ticker","Price","Change","Quantity","Today's Return","Total Return","Equity", "% of Portfolio"])

        cur_portfolio_file = os.path.join(self.data_path,"current_portfolio.csv")
        open_file = open(cur_portfolio_file,"w")

        for item in self.ticker_lst:
            last_price = r.get_quotes(item[0], "last_trade_price")[0]
            prev_close = r.get_quotes(item[0], "previous_close")[0]
            total_return = (float(last_price) - float(item[6])) * float(item[4])
            todays_return = (float(last_price) - float(prev_close)) * float(item[4]) 
            quantity = item[4]
            change = float(last_price) - float(prev_close)  
            equity = float(last_price) * float(quantity)
            lst_elements_to_update.append([f"{item[9]} ({item[0]})", float(last_price), change, item[4], todays_return, total_return, equity, item[10]])

       
        
        #update table
        for row in range(len(lst_elements_to_update)):
            join_list.append(f'{lst_elements_to_update[row][0]}:{str(lst_elements_to_update[row][3])}')
            
            for col in range(len(lst_elements_to_update[row])):
                table_item = QTableWidgetItem()

                if col == 2 and lst_elements_to_update[row][col] > 0.0:
                    # found change item add up/down arrow depending on the value
                    table_item.setText("{0:+.2f}".format(lst_elements_to_update[row][col]))
                    table_item.setIcon(QIcon(f"{self.icon_path}\\up.png"))
                    #table_item.setForeground(QColor("green"))
                elif col ==2 and lst_elements_to_update[row][col] < 0.0:
                    table_item.setText("{0:-.2f}".format(lst_elements_to_update[row][col]))
                    table_item.setIcon(QIcon(f"{self.icon_path}\\down.png"))
                    #table_item.setForeground(QColor("red"))
                elif col == 2 and lst_elements_to_update[row][col] == 0.0:
                    table_item.setText("{0:.2f}".format(lst_elements_to_update[row][col]))
                    table_item.setIcon(QIcon(f"{self.icon_path}\\equal.png"))
                    #table_item.setForeground(QColor("grey"))
                else:
                    if col == 0:
                        table_item.setText(lst_elements_to_update[row][col])
                    elif col == 7 or col == 8: #percentage column
                        table_item.setText("{0:.2f}".format(lst_elements_to_update[row][col]))
                    else:
                        table_item.setText("{0:,.2f}".format(lst_elements_to_update[row][col]))   
                  
                #set table properties
                table_item.setForeground(QColor("white"))
                table_item.setBackground(QColor("black"))
                table_item.setFlags(table_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table_item.setFont(QFont("Arial",12,QFont.Weight.Bold))
                self.ui.tblAssets.setItem(row,col,table_item)
            
        self.ui.tblAssets.resizeColumnsToContents()       
           
           
        plst = "\n".join(join_list)
        open_file.write(f'{plst}')
        open_file.close()
        return
    
    def get_tickers_from_selected_lstAssets(self):
        stock_tickers_names = []
        sel_items = [item.text() for item in self.ui.tblAssets.selectedItems()]
        selected_col_zero = [sel_items[i:i+8][0] for i in range(0,len(sel_items),8)]
        
        
        if len(selected_col_zero) > 0:
            #get stock tickers from selected items
            for index, ticker in enumerate(selected_col_zero):
                match = re.search(r"\((\w+\.?\w*)\)", ticker)
                if match:
                    stock_tickers_names.append(match.group(1))
            return stock_tickers_names

        
        return stock_tickers_names
    
    def get_stocks_from_portfolio(self, acc_num):
        
        positions = r.get_open_stock_positions(acc_num)
        if len(positions) == 0:
            raise Exception("No stocks in account")
        
            
      
       
        # Get Ticker symbols
        tickers = [r.get_symbol_by_url(item["instrument"]) for item in positions]
        lastPrice = r.get_quotes(tickers, "last_trade_price")
        previous_close = r.get_quotes(tickers, "previous_close") 

         # Get your average buy price
        avg_buy_price = [float(item["average_buy_price"]) for item in positions]

        #get stock names
        stock_name = [r.get_name_by_url(item["instrument"]) for item in positions]
        #get fundamentals
        #self.fundamentals = r.get_fundamentals(tickers, info='sector')
       
       
           
        

        #build dictionary for holdings
        holdings = {}
        for i, sym in enumerate(tickers):
            qty = float(positions[i]["quantity"])
            equity = float(lastPrice[i]) * qty
            holdings[sym] = {
                "price": float(lastPrice[i]),
                "quantity": qty,
                "equity": equity,
                "average_buy_price": float(avg_buy_price[i]),
                "percentage": 0.0,  # filled after total equity known
                "prev_close": float(previous_close[i]),
                "sector":  r.get_fundamentals(sym, info='sector')[0],
                "stock_name": stock_name[i]
                
            }

        self.portfolio = holdings
        self.portfolio_tvalue = sum((float(self.portfolio[item]['equity']) for item in self.portfolio))
        
        if len(tickers) != len (previous_close):
            tickers.pop()
            stock_name.pop()
            positions.pop()

        #calculate % of each stock in your portfolio
        lst_pct_of_portfolio = [(float(self.portfolio[item]["equity"]) / self.portfolio_tvalue * 100) for item in self.portfolio]
        
        pct_change = [(float(lastPrice[i]) - float(previous_close[i]))/float(previous_close[i])*100  for i in range(len(tickers))]
        change = [float(lastPrice[i]) - float(previous_close[i]) for i in range(len(tickers))]
        # Get your quantities
        quantities = [float(item["quantity"]) for item in positions]
       
        
        # Calculate total returns
        total_return = [(float(lastPrice[i]) - avg_buy_price[i])*quantities[i] for i in range(len(tickers))]
        #calc Todays return
        todays_return = [(float(lastPrice[i]) - float(previous_close[i]))*quantities[i] for i in range(len(tickers))]

        # Calculate stock quantities to sell to get total returns
        stock_quantity_to_sell = [total_return[i] / float(lastPrice[i]) for i in range(len(tickers))]   
        # build tuple to iterate through and sell stocks
       

        #Item 0 =  tickers
        #Item 1 = Total_return
        #Item 2 = stock_quantity_to_sell/buy
        #Item 3 = last price
        #item[4]= your quantities
        #item[5]=today's return
        #item[6]= 1 year history <-- removed
        #item[6]= average buy price
        #item[7]=%change in price
        #item[8]=change in price since previous close
        #item[9] = stock name
        #item[10] = % of portfolio
        #item[11] = dividend yield
        tickersPerf = list(zip(tickers,total_return,stock_quantity_to_sell,lastPrice,quantities,todays_return,
                               avg_buy_price,pct_change,change,stock_name,lst_pct_of_portfolio) )
        
        sorted_list = sorted(tickersPerf,key=lambda x: x[9])

        return sorted_list

    #calculate total gains and today's gains
    def cal_today_total_gains(self, list_p) -> tuple[float,float]:
        
        grand_total_gains = 0.0
        todays_gains = 0.0
            #Item 0 =  tickers
        #Item 1 = Total_return
        #Item 2 = stock_quantity_to_sell/buy
        #Item 3 = last price
        #item[4]= your quantities
        #item[5]=today's return

        for i in list_p:
                
            if (float(i[1]) > 0.0): 
                grand_total_gains += i[1]
            if (float(i[5] > 0.0)):
                todays_gains += i[5]
                
        return  grand_total_gains,todays_gains
        
    def find_and_remove(self, tickers, in_exList,include_flag = 1):
        
        if include_flag == 0:
        # Create a new list including the items not in in_exList
            updated_tickers = [ticker for ticker in tickers if ticker[0] not in in_exList]
        elif include_flag == 1:
        # Create a new list including only the items in in_exList
            updated_tickers = [ticker for ticker in tickers if ticker[0] in in_exList]

        return updated_tickers

    def check_and_read_conditions_met(self):
        cond_check = False
        check_one = False
        check_two = False

        lst = []


        if not re.match(r'^[1-9]+$',self.ui.ledit_Iteration.text()):
            msg = QMessageBox.warning(self,"Iteration","Must enter a number of iterations to sell",QMessageBox.StandardButton.Ok)
            if msg == QMessageBox.StandardButton.Ok:
                return False,lst
        else:
            txtIter = self.ui.ledit_Iteration.text()
            check_one = True

        match self.ui.cmbAction.currentText() :
            case "buy_selected" | "buy_selected_with_x" | "sell_selected":
                lst = self.ui.edtRaiseAmount.text().split(",")
                check_two = True
            case "allocate_reallocate_to_sectors":
                self.alloc_from = self.get_symbols_From_sectors()
                self.alloc_to = self.get_symbols_To_sectors()
                
                if len(self.alloc_from) == 0 or len(self.alloc_to) == 0:
                    msg = QMessageBox.warning(self,"Selection","There are no stocks in the selected sector.",QMessageBox.StandardButton.Ok)
                    if msg == QMessageBox.StandardButton.Ok:
                        lst = ['err']
                        return False,lst
                elif self.ui.cmbFromSector.currentText() == self.ui.cmbToSector.currentText():
                    msg = QMessageBox.warning(self,"Selection","To and From sectors are the same!.",QMessageBox.StandardButton.Ok)
                    if msg == QMessageBox.StandardButton.Ok:
                        lst = ['err']   
                        return False,lst
                else:
                    check_two = True
            case "sell_todays_return_except_x" | "sell_gains_except_x": 
                lst = self.ui.edtLstStocksSellected.text().split(",")
                check_two = True
            case "raise_x_sell_y_dollars_except_z":
                lst = self.ui.edtRaiseAmount.text().split(",")
            case "reinvest_with_gains":
                lst = [item for item in self.ui.edtStocksInFile_BuyLower.text().split(",")]
                
                check_two = True
    
        if check_one and check_two:
            return txtIter,lst
        else:
            return False,lst

#---------------------------------------------------------------------------------------------------------------------------------------------------    
# print the terminal lstTerm to a file in the data directory
    def print_terminal_to_file(self):
        file_path = os.path.join(self.data_path, "terminal_output.txt")
       

        with open(file_path, "a") as f:
            for i in range(self.ui.lstTerm.count()):
                item = self.ui.lstTerm.item(i)
                if os.environ['debug'] == '1':
                    f.write(f"debug - {item.text()}\n")
                else:
                    f.write(f"{item.text()}\n")

#----------------------------------------------------------------------------------------------------------------------------------
# reinvest_with_gains_prev 
# # -------------------------------------------------------------------------------------------------------------------------------------   
    def reinvest_with_gains_prev(self,num,lst,raise_amount,dollar_value_to_sell,buying_with_amount):
        total_gains = 0.0
        money_spent = 0.0
        spent = 0.0
        stock_symbols = []
        stocks = []
        buy_list = []
        #1 - open last stock_sell_gains.csv file
        #2 - iterate thru stocks and reinvest all stocks with current price < sold price with  gains from that stock.
        #3 - 
        #lst = 
            #Item 0 =  stock ticker
            #Item 1 = quantity sold of stock
            #Item 2 = price stock sold for
        
        method_name = self.ui.cmbAction.currentText()
        invest_amount = buying_with_amount / len(lst)
        

        for stock in lst:
            stock_market_prices = r.stocks.get_latest_price(stock)
            market_price_of_stock = float(stock_market_prices[0])

            buy_price = market_price_of_stock+0.1 #add 10 cents to current price to ensure it gets bought
            


            #calc what quantity of the stock can be bought with the invest amount
            
            per_quantity = invest_amount / buy_price
            frm_per_quantity = float("{0:.2f}".format(per_quantity) )
            buy_list.append( (stock,frm_per_quantity) )
            spent += frm_per_quantity*buy_price

        return buy_list,spent


#----------------------------------------------------------------------------------------------------------------------------------
# reinvest_with_gains SOMETHING WRONG COMMENTED CODE CAUSE PROGRAM NOT TO RUN "FIX ME"
# # -------------------------------------------------------------------------------------------------------------------------------------   
    def reinvest_with_gains(self,n,acc_num,lst,raise_amount,dollar_value_to_sell,buying_with_amount):
        total_gains = 0.0
        money_spent = 0.0
        spent = 0.0
        stock_symbols = []
        stocks = []
        buy_info = {}
        #1 - open last stock_sell_gains.csv file
        #2 - iterate thru stocks and buy all stocks with current price < sold price with  gains from that stock.
        #3 - 
        #lst = 
            #Item 0 =  stock ticker
            #Item 1 = quantity sold of stock
            #Item 2 = price stock sold for
        divider_pct = float(dollar_value_to_sell) / 100.0   
        method_name = self.ui.cmbAction.currentText()

      
        self.lstTerm_update_progress_fn(f"Reinvest: {buying_with_amount} by buying {dollar_value_to_sell}% of a previous sale of the stock")

        for index in range(int(n)):
            for stock in lst:
                stock_name,quantity = stock[0],stock[1]
                frm_per_quantity = f'{float(quantity):0.2f}'
                buy_price = r.stocks.get_latest_price(stock_name)[0]
                buy_price = float(buy_price) + 0.1  #add 10
                if self.command_thread.stop_event.is_set():
                    print("stop event")
                    self.lstTerm_update_progress_fn("Operation Cancelled!")
                    break
                if os.environ['debug'] == '0':
                    try:
                        buy_info = r.order(symbol=stock_name,quantity=frm_per_quantity,side='buy',timeInForce='gfd',limitPrice=buy_price,account_number=acc_num)
                        time.sleep(0.5)
                        buy_info = r.get_stock_order_info(buy_info['id'])
                        #if not state infor is filled then wait till it is filled
                        while 'state' not in buy_info and buy_info['state'] != 'filled' and buy_info['state'] != 'queued':
                            time.sleep(0.5)
                            buy_info = r.get_stock_order_info(buy_info['id'])

                        
                    except Exception as e:
                        self.lstTerm_update_progress_fn(f"Error: {e.args[0]}")
                        continue

                time.sleep(2)
                if 'price' in buy_info and buy_info['price'] is not None:        #Item 0 =  tickers     #Item 2 = stock_quantity_to_sell  #Item 3 = last price
                    fill_price = "{0:.2f}".format(float(buy_info['price']))
                else:
                    fill_price = "0.00"
                
                    #Item 0 =  tickers     #Item 2 = stock_quantity_to_sell  #Item 3 = last price
                stock_symbols.append(f"{stock_name}:{frm_per_quantity}:{fill_price}")
                self.lstTerm_update_progress_fn(f"{frm_per_quantity} shares of {stock_name} bought at {fill_price}" )
                spent += float(quantity)*float(fill_price)        

        if len(stock_symbols) > 0:
            self.write_to_file(stock_symbols)

        self.lstTerm_update_progress_fn(f"Operation Done! - You spent ${spent:.2f} of ${buying_with_amount:.2f} on buying shares of the stocks in the file.")
        
        
        return
    
#------------------------------------------------------------------------------------------------------------
# buy_selected_with_x
# "Buy {dollar_value_to_buy} dollars of each stock in your portfolio until you cannot buy anymore with x ${with_buying_power}
# -------------------------------------------------------------------------------------------------------------------------------------
    def buy_selected_with_x_prev(self,n,acc_num,lst,raise_amount,dollar_value_to_sell,buying_with):
        if buying_with != '':
            buying_power = float(buying_with)
        else:
            buying_power = 0.0
        if dollar_value_to_sell == "Not Used":
            dollar_value_to_sell = 0.0
        else:
            dollar_value_to_buy = float(dollar_value_to_sell)
        stock_symbols = []
        method_name = self.ui.cmbAction.currentText()
        
        buy_list = []
        found  = False
        tot = 0.0
        gtotal = 0.0
        quantity_to_buy = 0.0
        #format list to buy, get stocks from portfolio and remove stocks not in the list and sort the list
        tickersPerf = self.get_stocks_from_portfolio(acc_num)
        #if allocate/reallocate then get rid of all other tickers except the ones in the sector
        if self.ui.cmbAction.currentText() == "allocate_reallocate_to_sectors":       
            #get rid of all other tickers except the ones in the sector
            n_tickersPerf = self.find_and_remove(tickersPerf, lst,1)
        else:
            #exclude the tickets in excludeList
            n_tickersPerf = self.find_and_remove(tickersPerf, lst,0)

        sorted_lst = sorted(n_tickersPerf,key=lambda x: x[0])
        if n_tickersPerf is None or len(n_tickersPerf) == 0:
            self.lstTerm_update_progress_fn(f"Buy new list of stocks:")
            buy_list = self.new_lstShares
        else:
            
            if buying_power != 0.0: # user entered a buying power amount

                while not (buying_power <= 0):
                    for item in sorted_lst:
                            #Item 0 =  tickers
                            #Item 1 = Total_return
                            #Item 2 = stock_quantity_to_sell/buy
                            #Item 3 = last price
                            #item[4]= your quantities
                            #item[5]=today's return
                        # if there is no money left then break and continue buying the stocks that are in the list
                        if buying_power <= 0:
                            break    
                    
                        if self.ui.cmbDollarShare.currentText() == "Buy in Shares":
                            quantity_to_buy = dollar_value_to_buy
                        elif self.ui.cmbDollarShare.currentText() == "Buy in USD":
                            quantity_to_buy = dollar_value_to_buy / float(item[3])     
                    
                        tot = quantity_to_buy*float(item[3])
                        frm_tot = "{0:.2f}".format(tot)
                        strquantity_to_buy = "{0:.2f}".format(quantity_to_buy)
                    
                        for i,value  in enumerate(buy_list): #check if already in list and return index
                            if value[0] == item[0]:
                                exist_quantity = buy_list[i][1]
                                found = True
                                    # stock_quantity_to_sell and (your quantity > stock_quantity_to_sell)
                                if tot < buying_power:    
                                    buy_list[i][1] = "{0:.2f}".format(float(exist_quantity) + float(strquantity_to_buy))
                                    buying_power -= tot
                                    break
                            else:
                                found = False
                                        
                        if not found:
                            itm = [item[0],float(strquantity_to_buy),item[3]]
                            buy_list.append(itm)
                            buying_power -= tot 

        return buy_list, float(raise_amount) - buying_power

#------------------------------------------------------------------------------------------------------------
# buy_selected_with_x
# "Buy {dollar_value_to_buy} dollars of each stock in your portfolio until you cannot buy anymore with x ${with_buying_power}
# -------------------------------------------------------------------------------------------------------------------------------------
    def buy_selected_with_x(self,n,acc_num,lst,raise_amount,dollar_value_to_sell,buying_with):

        frm_total = "0.0"
        fill_price = "0.0"
        buy_info = {}
        if buying_with != '':
            buying_power = float(buying_with)
        else:
            buying_power = 0.0

        dollar_value_to_buy = float(dollar_value_to_sell)
        stock_symbols = []
      
        
        buy_list = []
        found  = False
        tot = 0.0
        gtotal = 0.0
        quantity_to_buy = 0.0
        #format list to buy, get stocks from portfolio and remove stocks not in the list and sort the list
        tickersPerf = self.get_stocks_from_portfolio(acc_num)
        n_tickersPerf = self.find_and_remove(tickersPerf, lst,1)
        
      
        sorted_lst = sorted(n_tickersPerf,key=lambda x: x[0])
        if n_tickersPerf is None or len(n_tickersPerf) == 0:
            self.lstTerm_update_progress_fn(f"Buy new list of stocks:")
            buy_list = self.new_lstShares
        else:
            
            if buying_power != 0.0: # user entered a buying power amount

                while not (buying_power <= 0):
                        if self.command_thread.stop_event.is_set():
                            print("stop event")
                            self.lstTerm_update_progress_fn("Operation Cancelled!")
                            break
                    

                        for item in sorted_lst:
                                #Item 0 =  tickers
                                #Item 1 = Total_return
                                #Item 2 = stock_quantity_to_sell/buy
                                #Item 3 = last price
                                #item[4]= your quantities
                                #item[5]=today's return
                            # if there is no money left then break and continue buying the stocks that are in the list
                            if buying_power <= 0:
                                break    
                        
                            if self.ui.cmbDollarShare.currentText() == "Buy in Shares":
                                quantity_to_buy = dollar_value_to_buy
                            elif self.ui.cmbDollarShare.currentText() == "Buy in USD":
                                quantity_to_buy = dollar_value_to_buy / float(item[3])     
                        
                            tot = quantity_to_buy*float(item[3])
                            frm_tot = "{0:.2f}".format(tot)
                            strquantity_to_buy = "{0:.2f}".format(quantity_to_buy)
                        
                            for i,value  in enumerate(buy_list): #check if already in list and return index
                                if value[0] == item[0]:
                                    exist_quantity = buy_list[i][1]
                                    found = True
                                     # stock_quantity_to_sell and (your quantity > stock_quantity_to_sell)
                                    if tot < buying_power:    
                                        buy_list[i][1] = exist_quantity + float(strquantity_to_buy) 
                                        buying_power -= tot
                                        break
                                else:
                                    found = False
                                            
                            if not found:
                                itm = [item[0],float(strquantity_to_buy),item[3]]
                                buy_list.append(itm)
                                buying_power -= tot 
            elif buying_power == 0.0: # user did not enter a buying power amount so buy all stocks in the list once
                for item in sorted_lst:
                    if self.command_thread.stop_event.is_set():
                        print("stop event")
                        self.lstTerm_update_progress_fn("Operation Cancelled!")
                        break
                    if self.ui.cmbDollarShare.currentText() == "Buy in Shares":
                        quantity_to_buy = dollar_value_to_buy
                    elif self.ui.cmbDollarShare.currentText() == "Buy in USD":
                        quantity_to_buy = dollar_value_to_buy / float(item[3])     
                    
                    tot = quantity_to_buy*float(item[3])
                    frm_tot = "{0:.2f}".format(tot)
                    strquantity_to_buy = "{0:.2f}".format(quantity_to_buy)
                    
                    itm = [item[0],float(strquantity_to_buy),item[3]]
                    buy_list.append(itm)

    

           

        self.lstTerm_update_progress_fn(f"Buying {lst} with buying {dollar_value_to_buy} of each stock." )
        #place buy orders
        for n in range(int(n)):
            self.lstTerm_update_progress_fn(f"Iteration {n+1}")
            for item in buy_list:    
               
                # Item[0] = stock_name
                # Item[1] = quantity to buy (shares)
                # Item[2] = last price
                frm_quantity = float(item[1])+0.02

                str_quantity = "{0:.2f}".format(frm_quantity)
                #if user click cancel then cancel operation
                if self.command_thread.stop_event.is_set():
                    print("stop event")
                    self.lstTerm_update_progress_fn("Operation Cancelled!")
                    break
                
                if os.environ['debug'] == '0':
                    try:
                        buy_info = r.order(symbol=item[0],quantity=item[1],side='buy',timeInForce='gfd',limitPrice=float(item[2])+0.02,account_number=acc_num)
                        
                        time.sleep(0.5)
                        buy_info = r.get_stock_order_info(buy_info['id'])
                        #if not state infor is filled then wait till it is filled
                        while 'state' not in buy_info and buy_info['state'] != 'filled' and buy_info['state'] != 'queued':
                            time.sleep(0.5)
                            buy_info = r.get_stock_order_info(buy_info['id'])

                      

                        if 'detail' in buy_info and buy_info['detail'] is not None:
                                    self.lstTerm_update_progress_fn(f"Error: {buy_info['detail']}")

                        
                    except Exception as e:
                            self.lstTerm_update_progress_fn(f"Error: {e.args[0]}")
                            continue
                
                time.sleep(2)
                if 'price' in buy_info and buy_info['price'] is not None:        #Item 0 =  tickers     #Item 2 = stock_quantity_to_sell  #Item 3 = last price
                    fill_price = "{0:.2f}".format(float(buy_info['price']))
                else:
                    fill_price = "0.00"
                    
                stock_symbols.append(f'{item[0]}:{item[1]}:{fill_price}')
                total = float(item[1])*float(fill_price)
                gtotal += total
                frm_total = "{0:,.2f}".format(total)

                self.lstTerm_update_progress_fn(f"{str_quantity} of {item[0]} shares bought at market price - ${fill_price} - Total: ${frm_total}")
       
        if len(stock_symbols) > 0:
            self.write_to_file(stock_symbols)
        
        stock_symbols = []
        fmt_gtotal = "{0:,.2f}".format(gtotal)
        self.lstTerm_update_progress_fn(f"Operation Done! - Total=${fmt_gtotal}")
        self.print_terminal_to_file()
        return
 
       

#----------------------------------------------------------------------------------------------------------------------------------
# get stock information (plotting historicals etc...)
# -------------------------------------------------------------------------------------------------------------------------------------   
    def stock_info(self,n,acc_num,lst,raise_amount,dollar_value_to_sell,buying_with):
        #Item[0] =  tickers
        #Item[1] = Total_return
        #Item[2] = stock_quantity_to_sell/buy
        #Item[3] = last price
        #item[4]= your quantities
        #item[5]=today's return
        #item[6]= 1 year history

        tickersPerf = self.get_stocks_from_portfolio(acc_num)
        n_tickersPerf = self.find_and_remove(tickersPerf, lst,0)
        sorderd_lst = sorted(n_tickersPerf,key=lambda x: x[0])
        self.lstTerm_update_progress_fn(f"Stock Information: {lst}")

        for item in sorderd_lst:
            self.lstTerm_update_progress_fn(f"Ticker: {item[0]} - Quantity: {item[4]} - Last Price: {item[3]} - Total Return: {item[1]} - Today's Return: {item[5]}")

        return    
#----------------------------------------------------------------------------------------------------------------------------------
# sell__selected
# -------------------------------------------------------------------------------------------------------------------------------------        
    def sell_selected(self,n,acc_num,lst,raise_amount,dollar_value_to_sell,buying_with):
   #Item 0 =  tickers
        #Item 1 = Total_return
        #Item 2 = stock_quantity_to_sell/buy
        #Item 3 = last price
        #item[4]= your quantities
        #item[5]=today's return
        #item[6]= 1 year history
        #item[7]= average buy price
        #item[8]=%change in price
        #item[9]=change in price since previous close

        stock_symbols = []
        tgains_actual = 0.0 
        priceTotal = 0.0
        sell_info = {}
        frm_tot = "0.0"
        fill_price = "0.0"
        method_name = self.ui.cmbAction.currentText()
        tickersPerf = self.get_stocks_from_portfolio(acc_num)
        frm_quantity_dollar_amount = "{0:.2f}".format(float(dollar_value_to_sell))  
        #new list with selected tickers only      
        n_tickersPerf = self.find_and_remove(tickersPerf, lst,1)

        for index, item in enumerate(n_tickersPerf):
                    est_price = item[3]
                    Total_quantity = float(dollar_value_to_sell) / float(est_price)
                    priceTotal += float(est_price) * Total_quantity

        self.lstTerm_update_progress_fn(f"Sell Selected: {lst} Total gains = ${priceTotal*int(n):,.2f}") 


        
        for index in range(int(n)):
            if self.command_thread.stop_event.is_set():
                print("stop event")
                self.lstTerm_update_progress_fn("Operation Cancelled!")
                break
            
            self.lstTerm_update_progress_fn(f"Iteration{index+1}")
            
            stock_symbols = []
            #sell stocks if quantity_to_sell > 0 
            for item in n_tickersPerf:
              
                time.sleep(5)
                if self.command_thread.stop_event.is_set():
                    print("stop event")
                    self.lstTerm_update_progress_fn("Operation Cancelled!")
                    break
                
                shares_to_sell = float(dollar_value_to_sell)/float(item[3])
                frm_shares_to_sell = "{0:.2f}".format(shares_to_sell)
                #if share quantity > shares to sell then sell shares_to_sell
                if float(item[4]) - shares_to_sell >= 0.1:
                    if os.environ['debug'] == '0':
                        try:
                            sell_info = r.order_sell_market(symbol=item[0],quantity=frm_shares_to_sell,timeInForce='gfd',account_number=acc_num)
                            time.sleep(0.5)
                            sell_info = r.get_stock_order_info(sell_info['id'])
                            #if not state infor is filled then wait till it is filled
                            while 'state' not in sell_info and sell_info['state'] != 'filled' and sell_info['state'] != 'queued':
                                time.sleep(0.5)
                                sell_info = r.get_stock_order_info(sell_info['id'])

                           
                            if 'detail' in sell_info and sell_info['detail'] is not None:
                                    self.lstTerm_update_progress_fn(f"Error: {sell_info['detail']}")
                            
                           
                        except Exception as e:
                            self.lstTerm_update_progress_fn(f"Error: {e.args[0]}")
                            return
                    
                    if 'average_price' in sell_info and sell_info['average_price'] is not None:        #Item 0 =  tickers     #Item 2 = stock_quantity_to_sell  #Item 3 = last price
                        fill_price = "{0:.2f}".format(float(sell_info['average_price']))
                    else:
                        if sell_info['state'] == 'queued':
                            fill_price = "queued"
                        else:
                            fill_price = "0.00"
                
                    if sell_info['state'] == 'filled':
                        stock_symbols.append(f'{item[0]}:{frm_shares_to_sell}:{fill_price}')
                    elif sell_info['state'] == 'queued':
                        stock_symbols.append(f"{item[0]}:{frm_shares_to_sell}:queued-{sell_info['id']}")
                    tot = float(dollar_value_to_sell)
                    tgains_actual += tot

                    self.lstTerm_update_progress_fn(f"${frm_quantity_dollar_amount} of {item[0]} shares sold at market price - ${fill_price} - Total: {shares_to_sell:,.2f} shares")
        
        if len(stock_symbols) > 0:
            self.write_to_file(stock_symbols)
            
        fmt_tgains_actual = "{0:,.2f}".format(tgains_actual*int(n))
        
        self.lstTerm_update_progress_fn(f"Operation Done! - Total=${fmt_tgains_actual}")
        self.print_terminal_to_file()
        
        return
    

                
#----------------------------------------------------------------------------------------------------------------------------------
# sell_gains_x exclude a list of stocks
# -------------------------------------------------------------------------------------------------------------------------------------        
    def sell_gains_except_x(self,n,acc_num,lst,raise_amount,dollar_value_to_sell,buying_with):
     #Item 0 =  tickers
        #Item 1 = Total_return
        #Item 2 = stock_quantity_to_sell/buy
        #Item 3 = last price
        #item[4]= your quantities
        #item[5]=today's return
        #item[6]= 1 year history
        #item[7]= average buy price
        #item[8]=%change in price
        #item[9]=change in price since previous close
        fill_price = "0.0"
        frm_tot = "0.0"
        tot_gains = 0.0
        tot_tgains = 0.0
        
        sell_info = {} 
        stock_symbols = []
        tgains_actual = 0.0
                
                #exclude the tickets in excludeList
        tickersPerf = self.get_stocks_from_portfolio(acc_num)
        
        
        n_tickersPerf = self.find_and_remove(tickersPerf, lst,0)
        
        tot_gains,_ = self.cal_today_total_gains(n_tickersPerf)

        fmt_tot_gains = "{0:,.2f}".format(tot_gains*int(n))
            
        if os.environ['debug'] == '0':
            self.lstTerm_update_progress_fn(f"Sell Gains: Total gains ~ ${fmt_tot_gains}, Except = {lst}")



              
        for index in range(int(n)):
            self.lstTerm_update_progress_fn(f"Iteration{index+1}")
              #if user click cancel then cancel operation
            if self.command_thread.stop_event.is_set():
                print("stop event")
                self.lstTerm_update_progress_fn("Operation Cancelled!")
                break
            stock_symbols = []

            #sell stocks if quantity_to_sell > 0 
            for item in n_tickersPerf: #
              
                time.sleep(5)
                 #if user click cancel then cancel operation
                if self.command_thread.stop_event.is_set():
                    print("stop event")
                    self.lstTerm_update_progress_fn("Operation Cancelled!")
                    break
                

                frm_quantity = "{0:,.2f}".format(float(item[2]))
                # stock_quantity_to_sell and your quantity > stock_quantity_to_sell or stock quantity <=1.0
                if (not (float(item[2]) <= 0) and (float(item[2]) >= 0.01) and (float(item[4]) > float(item[2])) ) and not (float(item[4]) <= 1.0):
                    if os.environ['debug'] == '0':
                        try:
                            sell_info = r.order_sell_market(symbol=item[0],quantity="{0:.2f}".format(float(item[2])),timeInForce='gfd',account_number=acc_num)
                            time.sleep(0.5)
                            sell_info = r.get_stock_order_info(sell_info['id'])
                            #if not state infor is filled then wait till it is filled
                            while 'state' not in sell_info and sell_info['state'] != 'filled' and sell_info['state'] != 'queued':
                                time.sleep(0.5)
                                sell_info = r.get_stock_order_info(sell_info['id'])

                          

                            if 'detail' in sell_info and sell_info['detail'] is not None:
                                    self.lstTerm_update_progress_fn(f"Error: {sell_info['detail']}")
                        except Exception as e:
                            self.lstTerm_update_progress_fn(f"Error: {e.args[0]}")
                            return
                    
                    
                    if 'average_price' in sell_info and sell_info['average_price'] is not None:        #Item 0 =  tickers     #Item 2 = stock_quantity_to_sell  #Item 3 = last price
                        fill_price = "{0:.2f}".format(float(sell_info['average_price']))
                    else:
                        fill_price = "0.00"    #Item 0 =  tickers     #Item 2 = stock_quantity_to_sell  #Item 3 = last price
                    
                    stock_symbols.append(f"{item[0]}:{item[2]}:{fill_price}")
                    tot = float(item[2])*float(fill_price)
                    tgains_actual += float(tot)
                    frm_tot = "{0:,.2f}".format(tot)

                    self.lstTerm_update_progress_fn(f"{frm_quantity} of {item[0]} shares sold at market price - ${fill_price} - Total: ${frm_tot}")
                                             
                   
        if len(stock_symbols) > 0:
            self.write_to_file(stock_symbols)


        tgains_actual= "{0:,.2f}".format(tgains_actual)
        self.lstTerm_update_progress_fn(f"Operation Done! - Total=${tgains_actual}")
        self.print_terminal_to_file()

        return
    

            
#----------------------------------------------------------------------------------------------------------------------------------
# sell__todays_return
# -------------------------------------------------------------------------------------------------------------------------------------        
    def sell_todays_return_except_x(self,n,acc_num,lst,raise_amount,dollar_value_to_sell,buying_with):
         #Item 0 =  tickers
        #Item 1 = Total_return
        #Item 2 = stock_quantity_to_sell/buy
        #Item 3 = last price
        #item[4]= your quantities
        #item[5]=today's return
        #item[6]= 1 year history
        #item[7]= average buy price
        #item[8]=%change in price
        #item[9]=change in price since previous close


        fill_price = "0.0"
        frm_tot = "0.0"
        stock_symbols = []
        tgains_actual = 0.0 
        sell_info = {}
        
        tickersPerf = self.get_stocks_from_portfolio(acc_num)
        n_tickersPerf = self.find_and_remove(tickersPerf, lst,0)
        
        grand_total_gains,tgains = self.cal_today_total_gains(n_tickersPerf)
        fmt_tgains = "{0:,.2f}".format(tgains*int(n))     

        self.lstTerm_update_progress_fn(f"Sell Todays Return: Total gains = ${fmt_tgains}, Except: {lst}")

        
        for index in range(int(n)):
               #if user click cancel then cancel operation
            if self.command_thread.stop_event.is_set():
                print("stop event")
                self.lstTerm_update_progress_fn("Operation Cancelled!")
                break
            self.lstTerm_update_progress_fn(f"Iteration{index+1}")
            

            stock_symbols = []
            #sell stocks if quantity_to_sell > 0 
            for item in n_tickersPerf: #
                
                time.sleep(5)
                  #if user click cancel then cancel operation
                if self.command_thread.stop_event.is_set():
                    print("stop event")
                    self.lstTerm_update_progress_fn("Operation Cancelled!")
                    break
                #cal how much to sell for today's gains
                amount_to_sell = float(item[5]) / float(item[3])
                frm_amount_to_sell = "{0:.2f}".format(amount_to_sell)

            # stock_quantity_to_sell and (your quantity > stock_quantity_to_sell) and todays_return >= 0 and stock quantity is not <= 1
                if (not (float(item[5]) <= 0.1) and (float(item[4]) > amount_to_sell) ) and not (float(item[4]) <= 1.0):
                    if os.environ['debug'] == '0':
                        try:
                            sell_info = r.order_sell_market(symbol=item[0],quantity="{0:.2f}".format(amount_to_sell),timeInForce='gfd',account_number=acc_num)
                            time.sleep(0.5)
                            sell_info = r.get_stock_order_info(sell_info['id'])
                            #if not state infor is filled then wait till it is filled
                            while 'state' not in sell_info and sell_info['state'] != 'filled' and sell_info['state'] != 'queued':
                                time.sleep(0.5)
                                sell_info = r.get_stock_order_info(sell_info['id'])

                            if 'detail' in sell_info and sell_info['detail'] is not None:
                                    self.lstTerm_update_progress_fn(f"Error: {sell_info['detail']}")
                            

                        except Exception as e:
                            self.lstTerm_update_progress_fn(f"Error: {e.args[0]}")
                            continue
                   
                    

                    if 'average_price' in sell_info and sell_info['average_price'] is not None:        #Item 0 =  tickers     #Item 2 = stock_quantity_to_sell  #Item 3 = last price
                        fill_price = "{0:.2f}".format(float(sell_info['average_price']))
                    else:
                        fill_price = "0.00"
                    #Item 0 =  tickers     #Item 2 = stock_quantity_to_sell  #Item 3 = last price
                    stock_symbols.append(f"{item[0]}:{frm_amount_to_sell}:{fill_price}")
                    tot = amount_to_sell*float(fill_price)
                    tgains_actual += tot
                    frm_tot = "{0:,.2f}".format(tot)

                    self.lstTerm_update_progress_fn(f"{frm_amount_to_sell} of {item[0]} shares sold at market price - ${fill_price} - Total: ${frm_tot}")                
        if len(stock_symbols) > 0:
            self.write_to_file(stock_symbols)

        fmt_tgains_actual = "{0:.2f}".format(tgains_actual)    
        self.lstTerm_update_progress_fn(f"Operation Done! - Total=${fmt_tgains_actual}")
        self.print_terminal_to_file()

        return
                                

#---------------------------------------------------------------------------------------------------------------------------
# raise x (dollars) by selling y dollars of each stock PREVIEW
#---------------------------------------------------------------------------------------------------------------------------------
    def raise_x_sell_y_dollars_except_z_prev(self,n,acc_num,lst,raise_amount,dollar_value_to_sell,buying_with):
      
        sell_list = []
        found  = False
        raised_amount_lst = []
        raise_amount_converged = False
        stock_symbols = []
        n_tickersPerf = []

        tickersPerf = self.get_stocks_from_portfolio(acc_num)
        if self.ui.cmbAction.currentText() == "allocate_reallocate_to_sectors":       
            #get rid of all other tickers except the ones in the sector
            n_tickersPerf = self.find_and_remove(tickersPerf, lst,1)
        else:
            #exclude the tickets in excludeList
            n_tickersPerf = self.find_and_remove(tickersPerf, lst,0)
        
        
        n_tickersPerf = sorted(n_tickersPerf,key=lambda x: x[0]) 
        accu_quantity_to_buy = 0.0
        raised_amount = 0.0
        quantity_to_sell = 0.0
        strquantity_to_sell = "0.0"
        total_new_quantity = 0.0
        n_raise_amount = float(raise_amount)
        n_dollar_value_to_sell = float(dollar_value_to_sell)
        frmt_dollar_value = "{0:,.2f}".format(n_dollar_value_to_sell)
        frmt_raise_amount = "{0:,.2f}".format(n_raise_amount)

        index = 0
        tgains_actual = 0.0
        
        while not (raised_amount >= n_raise_amount or raise_amount_converged==True):
               #if user click cancel then cancel operation
        
            for item in n_tickersPerf:
               
                #Item 0 =  tickers
                #Item 1 = Total_return
                #Item 2 = stock_quantity_to_sell/buy
                #Item 3 = last price
                #item[4]= your quantities
                #item[5]=today's return
                #item[6]= 1 year history
                #item[7]= average buy price
                #item[8]=%change in price
                #item[9]=change in price since previous close

                if raised_amount >= n_raise_amount or raise_amount_converged:
                    break    

                if not (n_dollar_value_to_sell / float(item[3]) >= item[4]+1): #check if you have enough shares to sell
                    quantity_to_sell = n_dollar_value_to_sell / float(item[3])     
                    strquantity_to_sell = "{0:.2f}".format(quantity_to_sell) 
                else:
                    quantity_to_sell = 0.0    
                    strquantity_to_sell = "0.0"
                    

                for i,value  in enumerate(sell_list): #check if already in list and return index
                    #if found in list and you have enough shares to sell 
                    if (value[0] == item[0]) and quantity_to_sell != 0.0:
                        exist_quantity = sell_list[i][1]
                        found = True
                        # stock_quantity_to_sell and (your quantity > stock_quantity_to_sell)
                        total_new_quantity = float(exist_quantity) + quantity_to_sell
                        if not (total_new_quantity >= item[4] + 0.1):
                            sell_list[i][1] = "{0:.2f}".format(total_new_quantity)
                            raised_amount += quantity_to_sell*float(item[3])
                            raised_amount_lst.append(raised_amount)
                            #look at 2 previous amounts if they are the same then break
                            if len(raised_amount_lst) > 2:
                                if raised_amount_lst[-1] == raised_amount_lst[-2] == raised_amount_lst[-3]:
                                    raise_amount_converged = True
                                    break
                        break
                    else:
                        found = False
                                
                if not found:
                   #don't add to list when you do not have enough shares to sell
                    if not ((n_dollar_value_to_sell / float(item[3])) >= item[4]+1):
                        itm = [item[0],strquantity_to_sell,item[3]]
                        sell_list.append(itm)
                        raised_amount += quantity_to_sell*float(item[3])   
                        raised_amount_lst.append(raised_amount)

      
        return sell_list,"{0:.2f}".format(raised_amount)

#---------------------------------------------------------------------------------------------------------------------------
#  sell_to_5_percent
# --------------------------------------------------------------------------------------------------------------------------                

    def sell_to_5_percent(self,n,acc_num,lst,raise_amount,dollar_value_to_sell,buying_with):
        
        self.reduce_position_to_5pct_of_portfolio()

             
    

#----------------------------------------------------------------------------------------------------------------------------------------------------
# raise x (dollars) by selling y dollars of each stock except [exclude list]
#---------------------------------------------------------------------------------------------------------------------------------
    def raise_x_sell_y_dollars_except_z(self,n,acc_num,lst,raise_amount,dollar_value_to_sell,buying_with):
      
          
        found  = False
        stock_symbols = []
        raised_amount_lst = []
        raise_amount_converged = False
        tot_gains = 0.0
        tgains = 0.0
        frm_tot = "0.0"
        fill_price = "0.0"
        n_tickersPerf = []

        method_name = self.ui.cmbAction.currentText()
        tickersPerf = self.get_stocks_from_portfolio(acc_num)   
        

        if method_name == "allocate_reallocate_to_sectors":       
            #get rid of all other tickers except the ones in the sector
            sell_list = self.find_and_remove(tickersPerf, lst,1)
        else:
            #exclude the tickets in excludeList
            sell_list = lst
          
       
   
       
        n_tickersPerf = sorted(n_tickersPerf,key=lambda x: x[0])
        tot_gains,tgains = self.cal_today_total_gains(n_tickersPerf)

        accu_quantity_to_buy = 0.0
        raised_amount = 0.0
        raised_amount_lst = []
        quantity_to_sell = 0.0
        total_new_quantity = 0.0
        strquantity_to_sell = "0.0"
        n_raise_amount = float(raise_amount)
        n_dollar_value_to_sell = float(dollar_value_to_sell)
        frmt_dollar_value = "{0:,.2f}".format(n_dollar_value_to_sell)
        frmt_raise_amount = "{0:,.2f}".format(n_raise_amount)

        index = 0
        tgains_actual = 0.0
        sell_info = {}
        

        if method_name == "allocate_reallocate_to_sectors":
            self.lstTerm_update_progress_fn(f"Raise Amount: ${n_raise_amount} by selling {lst}")
        else:
            self.lstTerm_update_progress_fn(f"Raise Amount: ${n_raise_amount} by selling except {lst}")
   
    #     #place sell orders
        for item in sell_list:        
            
            time.sleep(5)
                #if user click cancel then cancel operation
            if self.command_thread.stop_event.is_set():
                print("stop event")
                self.lstTerm_update_progress_fn("Operation Cancelled!")
                break
            # Item[0] = stock_name
            # Item[1] = quantity to sell
            # Item[2] = last price    
            frm_quantity_to_sell = float(item[1])
            frm_quantity_to_sell += 0.02
            str_quantity = str(frm_quantity_to_sell)
            if os.environ['debug'] == '0':
                    try:
                        sell_info = r.order_sell_market(symbol=item[0],quantity=item[1],timeInForce='gfd',account_number=acc_num)

                        time.sleep(0.5)
                        sell_info = r.get_stock_order_info(sell_info['id'])
                        #if not state infor is filled then wait till it is filled
                        while 'state' not in sell_info and sell_info['state'] != 'filled' and sell_info['state'] != 'queued':
                            time.sleep(0.5)
                            sell_info = r.get_stock_order_info(sell_info['id'])

                        if 'detail' in sell_info and sell_info['detail'] is not None:
                                    self.lstTerm_update_progress_fn(f"Error: {sell_info['detail']}")
                    except Exception as e:
                        self.lstTerm_update_progress_fn(f"Error: {e.args[0]}")
                        continue
            
            if 'average_price' in sell_info and sell_info['average_price'] is not None:        #Item 0 =  tickers     #Item 2 = stock_quantity_to_sell  #Item 3 = last price
                    fill_price = "{0:.2f}".format(float(sell_info['average_price']))
            else:
                    if sell_info['state'] == 'quequed':
                        fill_price = "queued"
                    else:
                        fill_price = "0.00"
                
            if sell_info['state'] == 'filled':
                stock_symbols.append(f'{item[0]}:{item[1]}:{fill_price}')
            elif sell_info['state'] == 'queued':
                stock_symbols.append(f"{item[0]}:{item[1]}:queued-{sell_info['id']}")

            tot = float(item[1])*float(fill_price)
            tgains_actual += tot
            frm_tot = "{0:,.2f}".format(tot)

            self.lstTerm_update_progress_fn(f"{str_quantity} shares of {item[0]} sold at market price ${fill_price} - Total: ${frm_tot} ")                    

        if len(stock_symbols) > 0:
            self.write_to_file(stock_symbols)
        
        stock_symbols = []  
        fmt_tgains_actual = "{0:,.2f}".format(tgains_actual)
        self.lstTerm_update_progress_fn(f"Operation Done! - Total=${fmt_tgains_actual}")
        self.print_terminal_to_file()

        return
    # end of class MainWIndow

class MpfCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=8, height=4):
        # Use inches + dpi (not pixels)
        dpi = 100

        self.fig = mpf.figure(figsize=(width, height), dpi=dpi, tight_layout=False)
        super().__init__(self.fig)

        # Let the scroll area control when to add scrollbars
        self.setMinimumSize(1, 1)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.legend_handles = []
       



    @staticmethod
    def compute_rsi(data, window=14):
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def compute_macd(data, fast=12, slow=26, signal=9):
        ema_fast = data['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = data['Close'].ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        return macd, signal_line, histogram


    @staticmethod
    def compute_stochastic(data, k_window=14, d_window=3):
        low_min = data['Low'].rolling(window=k_window).min()
        high_max = data['High'].rolling(window=k_window).max()
        k = 100 * ((data['Close'] - low_min) / (high_max - low_min))
        d = k.ewm(span=d_window, adjust=False).mean()
        return k, d




    def _ensure_scrollable(self, n_rows: int, n_cols: int, frm_h: int, frm_w: int):
        # Give each subplot a reasonable pixel footprint; QScrollArea will add scrollbars
        per_w, per_h = 220, 420  # px per subplot (tune as desired)
        dpi = self.fig.get_dpi()
        width_px = max(frm_w, n_cols * per_w)
        height_px = max(frm_h, n_rows * per_h)
        self.fig.set_size_inches(width_px / dpi, height_px / dpi)
        # Do not inflate minimum beyond required
        # When going back to a single plot, allow the canvas to shrink again
        if n_rows * n_cols <= 1:
            self.setMinimumSize(1, 1)
        else:
            self.setMinimumSize(int(width_px), int(height_px))
   

    def add_plot_to_figure(self,ticker_lst,sel_ticker_lst=[],action_selection="Bar (Sector Colors)", sectorsDict={}, frm_h=0, frm_w=0) -> str:
        #Item[0] =  tickers
        #Item[1]= Total_return
        #Item[2] = stock_quantity_to_sell/buy
        #Item[3]= last price
        #item[4]= your quantities
        #item[5]=today's return
        #item[6]= average buy price
        #item[7]=%change in price
        #item[8]=change in price since previous close
        #items to be updated ["Ticker","Price","Change","Quantity","Today's Return","Total Return"]
        #updated_items = update_current_assets()
        #item[9] = stock name
       

     
       
        err_msg = ""
        bars = []
        self.legend_handles = []  # reset
        n_col = 0
        n_row = 0
        index = 0
        

        
        match action_selection:
            case "Bar (Individual Stocks)":
                if len(sel_ticker_lst) >= 1:
                    #calculate row and columns max columns = 3
                    if len(sel_ticker_lst) > 3:
                        n_col = 3
                        n_row = len(sel_ticker_lst) // 3
                        if len(sel_ticker_lst) % 3 != 0:
                            n_row += 1
                            
                    elif len(sel_ticker_lst) == 1:
                        n_col = 1
                        n_row = 1

                    elif len(sel_ticker_lst) > 1:
                        n_col = len(ticker_lst)
                        n_row = 1


                    my_style = mpf.make_mpf_style(
                            base_mpf_style='charles',
                            rc={'font.size': 10},
                            marketcolors=mpf.make_marketcolors(
                                up='green', down='red',
                                edge='inherit', wick='black',
                                volume='in'
                            ),
                            facecolor='lightgray',
                            gridcolor='white'
                    )
                    # Resize canvas so scrollbars show when content is larger than viewport
                    self._ensure_scrollable(n_row, n_col, frm_h, frm_w)
                    outer_grid = self.fig.add_gridspec(n_row, n_col, hspace=0.08, wspace=0.2)

                    #sorted_name_list = sorted(ticker_lst,key=lambda x: x[9])
                    
                    #plot each selected stock in a subplot
                    for index, ticker in enumerate(sel_ticker_lst):
                        try:
                            df = yf.download(ticker, period='1y', interval='1d', progress=False)
                            df.columns = ['Close', 'High', 'Low', 'Open', 'Volume']

                            row, col = divmod(index, n_col)
                            subgrid = outer_grid[row, col].subgridspec(5, 1, height_ratios=[5, 1, 1, 1, 1], hspace=0.06)
                            ax_price = self.fig.add_subplot(subgrid[0])
                            ax_volume = self.fig.add_subplot(subgrid[1], sharex=ax_price)
                            ax_rsi = self.fig.add_subplot(subgrid[2], sharex=ax_price)
                            ax_macd = self.fig.add_subplot(subgrid[3], sharex=ax_price)
                            ax_stoch = self.fig.add_subplot(subgrid[4], sharex=ax_price)
                            ax_price.set_title(ticker, fontsize=9)
                            ax_price.tick_params(axis='y', labelsize=9, left=True)
                            ax_price.set_ylabel('Price',fontsize=9)
                            ax_price.grid(True, linestyle='solid',alpha=1)
                            ax_price.xaxis.set_visible(False)

                            ax_volume.tick_params(axis='y', labelsize=9, left=True)
                            ax_volume.xaxis.set_visible(False)
                            ax_volume.set_ylabel('Volume',fontsize=9)
                            ax_volume.grid(True, linestyle='solid', alpha=1)
                            ax_volume.xaxis.set_visible(False)

                            ax_rsi.tick_params(axis='y', labelsize=9, left=True)
                            ax_rsi.set_ylim(0, 100)
                            ax_rsi.set_ylabel('RSI',fontsize=9)
                            ax_rsi.grid(True, linestyle='solid', alpha=1)
                            ax_rsi.xaxis.set_visible(False)

                            ax_macd.tick_params(axis='y', labelsize=9, left=True)
                            ax_macd.xaxis.set_visible(False)
                            ax_macd.set_ylabel('MACD',fontsize=9)
                            ax_macd.grid(True, linestyle='solid', alpha=1)
                            ax_macd.xaxis.set_visible(False)
                            
                            ax_stoch.tick_params(axis='y', labelsize=9, left=True)
                            ax_stoch.tick_params(axis='x', labelsize=9)
                            ax_stoch.set_ylabel('Stochastic',fontsize=9)
                            ax_stoch.set_ylim(0, 100)
                            ax_stoch.grid(True, linestyle='solid', alpha=1)
                            
                            df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = self.compute_macd(df)
                            df['Stoch_K'], df['Stoch_D'] = self.compute_stochastic(df)
                            df['RSI'] = self.compute_rsi(df)
                            ma50 = df['Close'].rolling(50).mean()
                            ma200 = df['Close'].rolling(200).mean()

                            apds = [
                                mpf.make_addplot(ma50, ax=ax_price, color='orange', label='MA50'),
                                mpf.make_addplot(ma200, ax=ax_price, color='blue', label='MA200'),
                                mpf.make_addplot(df['RSI'], ax=ax_rsi, color='purple', ylim=(0,100)),
                                mpf.make_addplot(df['MACD'], ax=ax_macd, color='blue'),
                                mpf.make_addplot(df['MACD_Signal'], ax=ax_macd, color='orange'),
                                mpf.make_addplot(df['MACD_Hist'], ax=ax_macd, type='bar', color='gray'),
                                mpf.make_addplot(df['Stoch_K'], ax=ax_stoch, color='green'),
                                mpf.make_addplot(df['Stoch_D'], ax=ax_stoch, color='red'),
                                mpf.make_addplot(df['Volume'], ax=ax_volume, type='bar', color='grey'), #overlap volume on price
                            ]

                            mpf.plot(
                                df,
                                ax=ax_price,
                                style=my_style,
                                addplot=apds,
                                type='candle',
                                volume=False,
                                warn_too_much_data=10000
                            )
                        except Exception as e:
                            print(f"Error downloading data for {ticker[0]}: {e}")
                            return e
            
            case "Bar (Gain/Loss)":
              
                    # create bar chart with gain/loss colors
                    
                    n_row = 1
                    n_col = 1
                    index=1
                    val_up = 0
                    val_down = 0
                    self.legend_handles = []  # reset
                    tot_up_change = 0.0
                    tot_down_change = 0.0
                    self._ensure_scrollable(1, 1, frm_h, frm_w)
                    

                    sorted_list = sorted(ticker_lst,key=lambda x: float(x[4])*float(x[3]),reverse=True)

                    x_data = []
                    y_data = []
                    for item in sorted_list:
                        x_data.append(item[0])
                        y_data.append(float(item[4])*float(item[3]))


                    ax = self.fig.add_subplot(n_row,n_col,index)
                    ax.grid(True)
                    ax.set_xlabel('Stocks')
                    ax.set_ylabel('$value of stock')
                    ax.set_title('Stocks Ticker/Quantity')
                    ax.tick_params(axis='x', rotation=90, labelsize=9)
                   
                    
                  
                  
                   
                    bars = ax.bar(x_data, y_data, width=0.7)
                    for i, ticker in enumerate(sorted_list):
                        if ticker[8] < 0.0:
                            bars[i].set_facecolor('darkred')
                            val_down += 1
                            tot_down_change += ticker[5] #- total today down return
                        elif ticker[8] > 0.0:
                            bars[i].set_facecolor('darkgreen')
                            val_up += 1
                            tot_up_change += ticker[5] #- total today up return
                        else:
                            bars[i].set_facecolor('gray')

                        if ticker[0] in sel_ticker_lst:
                            bars[i].set_edgecolor('yellow')
                            bars[i].set_linestyle('solid')
                            bars[i].set_linewidth(2.5)  
                        

                    patch = [Patch(facecolor='darkgreen', edgecolor='black', label=f'Gain - {val_up} Up {tot_up_change:+.2f}'), \
                            Patch(facecolor='darkred', edgecolor='black', label=f'Loss - {val_down} Down {tot_down_change:-.2f}'), \
                            Patch(facecolor='gray', edgecolor='black', label='No Change')]
                    for p in patch:
                        self.legend_handles.append(p)
                    
                    self._add_legend(ax)
              
                       
                    
            case "Bar (Sector Colors)":
                
                    n_row = 1
                    n_col = 1
                    index = 1
                    count_total_pct = 0.0

                    self._ensure_scrollable(1,1,frm_h,frm_w)

                    sorted_list = sorted(ticker_lst,key=lambda x: float(x[4])*float(x[3]),reverse=True)

                    x_data = []
                    y_data = []
                    sorted_list_stock_name = [item[0] for item in sorted_list]
                    #build bars according to sectors    
                    for sector, stocks_in_sector in sectorsDict.items():   
                        lst_stock_in_sec = [stock.split(":")[0] for stock in stocks_in_sector]
                        for stock in lst_stock_in_sec:
                            index = sorted_list_stock_name.index(stock)
                            x_data.append(stock)
                            y_data.append(float(sorted_list[index][4])*float(sorted_list[index][3]))


                    index=1
                    ax = self.fig.add_subplot(n_row,n_col,index)
                    
                
                    bars = ax.bar(x_data, y_data, width=0.7)
                    
                    ax.grid(True)
                
                    
                    bar_index = 0
                    sec_index = 1
                    colors = mcolors.CSS4_COLORS
                    names = sorted(colors, key=lambda c: tuple(mcolors.rgb_to_hsv(mcolors.to_rgb(c))))
                    
                    
                    for sector, stocks_in_sector in sectorsDict.items():
                        
                        lst_stock_in_sec = [stock.split(":")[0] for stock in stocks_in_sector]
                        lst_pct_in_sec = [float(stock.split(":")[1]) for stock in stocks_in_sector]
                        count_total_pct = sum(lst_pct_in_sec)

                        color_idx = sec_index
                        color = names[color_idx % len(names)]
                        patch = Patch(facecolor=color, edgecolor='black', label=f'{sector} - ({count_total_pct:.2f}%)')
                        self.legend_handles.append(patch)       
                        sec_index += 20
                        for stock in lst_stock_in_sec:
                            bars[bar_index].set_facecolor(color)
                            if stock in sel_ticker_lst:
                                if bars[bar_index].get_facecolor() == mcolors.to_rgba('yellow') or bars[bar_index].get_edgecolor() == mcolors.to_rgba('orange'):
                                    bars[bar_index].set_edgecolor('blue')
                                    bars[bar_index].set_linestyle('solid')
                                    bars[bar_index].set_linewidth(2.5)
                                else:    
                                    bars[bar_index].set_edgecolor('yellow')
                                    bars[bar_index].set_linestyle('solid')
                                    bars[bar_index].set_linewidth(2.5)
                            bar_index += 1
                            

                    self._add_legend(ax)    
                    
                    ax.set_xlabel('Stocks')
                    ax.set_ylabel('$value of stock')
                    ax.set_title('Stocks Ticker/Quantity')
                    ax.tick_params(axis='x', rotation=90, labelsize=9)
              
            case _:
                pass
          
        return err_msg
 
    
    def _add_legend(self, ax):
       ax.legend(handles=self.legend_handles, loc='best', frameon=True, fontsize=9)

    
class TableToolTip(QWidget):
    def __init__(self, obj ,parent=MainWindow):
        super().__init__(parent, Qt.WindowType.ToolTip)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.obj = obj
        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.sectorlabel_pct = QLabel()
        self.table.setColumnCount(4)
        
        self.table.setObjectName("SectorTable")
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.table.setShowGrid(False)
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        #bundle, the PyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app 
        # path into variable _MEIPASS'.
            self.base_path = sys._MEIPASS
           
        else:
            self.base_path = os.path.abspath(".")

        #set the program paths
        icon_path = os.path.join(self.base_path,"icons")
        data_path = os.path.join(os.environ['LOCALAPPDATA'], "pyShares")

        icon_path = os.path.join(self.base_path,"icons")
        

        self.icon_up = QIcon(f"{icon_path}\\up.png")
        self.icon_down = QIcon(f"{icon_path}\\down.png")
        self.icon_equal = QIcon(f"{icon_path}\\equal.png")

        
        #load sector data
        lst_stocks_in_sector = self.parent().get_symbols_pct_in_sector(obj.objectName())
        self.createTable(lst_stocks_in_sector)

        layout.addWidget(self.sectorlabel_pct)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.adjustSize()

    def createTable(self,lst_stocks):
        
        tot_pct = 0.0
        
        self.table.setRowCount(len(lst_stocks))
        
        lst_vals = []
        
        #calc total percent of portfolio
        
           

        for item in lst_stocks:
                pct = item.split(":")[1]
                tot_pct += float(pct)
                #get the stock name
                stock_name = r.get_name_by_symbol(item.split(":")[0])
                #get the last price
                val = r.get_quotes(f'{item.split(":")[0]}',"last_trade_price")[0]
                #get the previous close
                prev_close = r.get_quotes(f'{item.split(":")[0]}',"previous_close")[0]
                #calculate the gains
                if val is not None and prev_close is not None:
                    Gains = float(val) - float(prev_close) 
                    lst_vals.append([f'{stock_name} ({item.split(":")[0]})', float(val),float(Gains), float(item.split(":")[1])])
                else:
                    lst_vals.append([f'{stock_name} ({item.split(":")[0]})', 0.0,0.0, 0.0])
                    #add the stock to the list
                    
                    
        for row in range(len(lst_vals)):
            for col in range(0,4):
                table_item = QTableWidgetItem()
                if col == 2 and lst_vals[row][col] > 0.0:
                    # found change item add up/down arrow depending on the value
                    table_item.setText("{0:+.2f}".format(lst_vals[row][col]))
                    table_item.setIcon(self.icon_up)
                elif col == 2 and lst_vals[row][col] < 0.0:
                    table_item.setText("{0:-.2f}".format(lst_vals[row][col]))
                    table_item.setIcon(self.icon_down)
                elif col == 2 and lst_vals[row][col] == 0.0:
                    table_item.setText("{0:.2f}".format(lst_vals[row][col]))
                    table_item.setIcon(self.icon_equal)
                else:
                    if col == 0:
                       
                        table_item.setText(lst_vals[row][col])
                    elif col == 3:
                        table_item.setText(f'{lst_vals[row][col]:.2f}%')
                    else:
                        table_item.setText("{0:,.2f}".format(lst_vals[row][col]))


                table_item.setFont(QFont("Arial",8,QFont.Weight.Bold))
                table_item.setBackground(QColor("White"))
                table_item.setForeground(QColor("Black"))
                self.table.setItem(row, col,table_item)

        #set label percent

        self.sectorlabel_pct.setText(f'{tot_pct:.2f}% of Portfolio')
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.width = self.table.horizontalHeader().length()
        self.table.height = self.table.verticalHeader().length()
        self.table.setMinimumHeight(self.table.height)
        self.table.setMaximumHeight(self.table.height)
        self.table.setMinimumWidth(self.table.width)
       
        return
    
    def createTable_reduce(self,lst_stocks):
        tot_pct = 0.0
        
        self.table.setRowCount(len(lst_stocks))
        
        lst_vals = []
        
        #calc total percent of portfolio
        
           

        for item in lst_stocks:
            #get the stock name
            stock_name = r.get_name_by_symbol(item.split(":")[0])
            lst_vals.append([f'{stock_name} ({item.split(":")[0]})', float(item.split(":")[1])])
                    
                    
                    
                    
        for row in range(len(lst_vals)):
            for col in range(0,2):
                table_item = QTableWidgetItem()

                if col == 1 and lst_vals[row][col] > 0.0:
                    table_item.setText("{0:+.2f}".format(lst_vals[row][col]))
                    table_item.setIcon(self.icon_up)
                elif col ==1 and lst_vals[row][col] < 0.0:
                    table_item.setText("{0:-.2f}".format(lst_vals[row][col]))
                    table_item.setIcon(self.icon_down)
                else:
                    table_item.setText(lst_vals[row][col])


                table_item.setFont(QFont("Arial",8,QFont.Weight.Bold))
                table_item.setBackground(QColor("White"))
                table_item.setForeground(QColor("Black"))
                self.table.setItem(row, col,table_item)

        
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.width = self.table.horizontalHeader().length()
        self.table.height = self.table.verticalHeader().length()
        self.table.setMinimumHeight(self.table.height)
        self.table.setMaximumHeight(self.table.height)
        self.table.setMinimumWidth(self.table.width)
       
        return


                