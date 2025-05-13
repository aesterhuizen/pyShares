import os
import sys,traceback # type: ignore
import time
import pyotp
import robin_stocks.robinhood as r

import numpy as np 
import matplotlib
import pandas as pd
import mplfinance as mpf

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

matplotlib.use('QtAgg')

import re
from PyQt6.QtGui import QPalette


from threading import Thread,Lock


from dotenv import load_dotenv, set_key


from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox,QLabel, QTableWidget, QTableWidgetItem
                            
from PyQt6.QtGui import QAction, QIcon, QCursor, QColor,QFont,QStandardItemModel,QStandardItem
from PyQt6.QtCore import QSize,Qt

from layout import Ui_MainWindow

from PopupWindows import msgBoxGetCredentialFile, msgBoxGetAccounts
from WorkerThread import CommandThread, UpdateThread

class MainWindow(QMainWindow):

    
    def __init__(self):
        super().__init__()

        #class variabled
        # self.quantity = []

        
        self.ver_string = "v1.0.12"
        self.icon_path = ''
        self.base_path = ''
        self.env_file = ''
        self.data_path = ''
        
        
        self.update_thread = None
        self.command_thread = None
        
        self.totalGains = 0.0
        self.todayGains = 0.0

        # self.stock_quantity_to_sell = 0
        self.current_account_num = ""
        self.account_info = ''
        #main list of tickers and performance metrics
        self.ticker_lst = []
        self.lstupdated_tblAssets = []
        
        
        # setup UI
        self.ui = Ui_MainWindow()       
        
        self.ui.setupUi(self)
        self.plot = MpfCanvas(self, width=12, height=12)
        self.ui.grdGraph.addWidget(self.plot)
        self.setGeometry(300, 300, 2500, 1000)
                
        self.ui.splt_horizontal.setSizes([10, 550])
        self.ui.vertical_splitter.setSizes([450, 50])
        #add combo box items to the action combobox
        self.ui.cmbAction.addItem("stock_info")
        self.ui.cmbAction.addItem("sell_selected")
        self.ui.cmbAction.addItem("sell_gains")
        self.ui.cmbAction.addItem("sell_todays_return")
        self.ui.cmbAction.addItem("sell_selected")
        self.ui.cmbAction.addItem("sell_gains_except_x")
        self.ui.cmbAction.addItem("sell_todays_return_except_x")
        self.ui.cmbAction.addItem("buy")
        self.ui.cmbAction.addItem("buy_selected")
        self.ui.cmbAction.addItem("buy_selected_with_x")
        self.ui.cmbAction.addItem("buy_lower_with_gains")
        self.ui.cmbAction.addItem("raise_x_sell_y_dollars")
        self.ui.cmbAction.addItem("raise_x_sell_y_dollars_except_z")
        
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
                    if e.args[0] == "Invalid account number":
                        self.ui.lstTerm.addItem(f"Error!: {e.args[0]}")
                        
                        
            
                self.print_cur_protfolio(self.ticker_lst)
                #get total gains for the day
                self.totalGains,self.todayGains = self.cal_today_total_gains(self.ticker_lst)
                #setup plot widget
                self.setup_plot(self.ticker_lst)
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
                    self.ticker_lst = self.get_stocks_from_portfolio(self.current_account_num)
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
                        self.ticker_lst = self.get_stocks_from_portfolio(self.current_account_num)
                        
                    except Exception as e:
                        if e.args[0] == "Invalid account number":
                            self.ui.lstTerm.addItem(f"Error: {e.args[0]}")
                            return
                    
                    self.print_cur_protfolio(self.ticker_lst)
                    #get total gains for the day
                    self.totalGains,self.todayGains = self.cal_today_total_gains(self.ticker_lst)
                    #setup plot widget
                    self.setup_plot(self.ticker_lst)
            else: #user pressed cancel at credential dialog
                self.setWindowTitle(f"PyShares - {self.ver_string}")

        #Setup signals / Slots
    
        
        #menu Qaction_exit
        self.ui.action_Exit.triggered.connect(self.closeMenu_clicked)
        self.ui.actionCredentials_File.triggered.connect(self.Show_msgCredentials)
        
        #Toolbar
        self.ui.toolBar.setIconSize(QSize(32,32))
        button_action = QAction(QIcon(self.icon_path +'/application--arrow.png'), "Exit", self)
        button_action.triggered.connect(self.closeMenu_clicked)
        button_action = self.ui.toolBar.addAction(button_action)

        #add credentials button
        button_cred_action = QAction(QIcon(self.icon_path +'/animal-monkey.png'), "Credentials", self)
        button_cred_action.triggered.connect(self.Show_msgCredentials)
        button_cred_action = self.ui.toolBar.addAction(button_cred_action)

       
        #connect function to combo dollar/value selector
        self.ui.cmbDollarShare.activated.connect(self.cmbDollarShare_clicked)
        #connect sigals and slots Account combo box
        self.ui.cmbAccount.activated.connect(self.account_clicked)
        #connect sigals and slots Actions combo box
        self.ui.cmbAction.activated.connect(self.cmbAction_clicked)
        #connect signal/slot for label Iteration button
        #connect selectAll button
        self.ui.btnSelectAll.clicked.connect(self.SelectAll_clicked)
        self.ui.ledit_Iteration.textChanged.connect(self.ledit_Iteration_textChanged)
        
        #connect signal/slot for Execute button
        self.ui.btnExecute.clicked.connect(self.btnExecute_clicked)
        self.ui.btnExecute.setStyleSheet("background-color: green; color: white;")  # Change background to green             
        self.ui.btnExecute.setText("Execute ...")
        #connect GetAccount button
        self.ui.btnStoreAccounts.clicked.connect(self.StoreAccounts)
        #connect signal/slot for edtRaiseAmount
        self.ui.edtRaiseAmount.textChanged.connect(self.edtRaiseAmount_changed)
        #connect signal/slot for edtDollarValueToSell
        self.ui.edtDollarValueToSell.textChanged.connect(self.edtDollarValueToSell_changed)
        self.ui.edtBuyWithAmount.textChanged.connect(self.edtBuyWithAmount_changed)   
        #connect clear selection button
        self.ui.btnClearSelec.clicked.connect(self.clear_selection_clicked)  
        #connect the Asset table box
        self.ui.tblAssets.itemClicked.connect(self.tblAsset_clicked)
        #setup status bar
        lblStatusBar = QLabel(f"Total Assets: {self.ui.tblAssets.rowCount()}")
        lblStatusBar.setMinimumWidth(50)
        lblStatusBar.setObjectName("lblStatusBar")
        self.ui.statusBar.addWidget(lblStatusBar,1)

        frm_TotalGains = "{0:,.2f}".format(self.totalGains)
        lblStatusBar_pctT = QLabel(f"Total Gains: ${frm_TotalGains}")
        lblStatusBar_pctT.setObjectName("lblStatusBar_pctT")
        lblStatusBar_pctT.setMinimumWidth(150)
        self.ui.statusBar.addWidget(lblStatusBar_pctT,1)

        frm_TodayGains = "{0:,.2f}".format(self.todayGains)
        lblStatusBar_pctToday = QLabel(f"Todays Gains: ${frm_TodayGains}")
        lblStatusBar_pctToday.setObjectName("lblStatusBar_pctToday")

        lblStatusBar_pctToday.setMinimumWidth(150)
        self.ui.statusBar.addWidget(lblStatusBar_pctToday,1)

        #setup the status table widget
        tbl_Index = QTableWidget()
        tbl_Index.width = 540
        tbl_Index.setObjectName("tbl_Index")
        tbl_Index.setMaximumHeight(25)
        tbl_Index.setMinimumWidth(540)
       
        tbl_Index.setRowCount(1)
        tbl_Index.horizontalHeader().setVisible(False)
        tbl_Index.verticalHeader().setVisible(False)
        tbl_Index.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        tbl_Index.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        
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
        lst_SPY.append(["S&P", float(SPY_value),float(SPY_Gains)])
        lst_SPY.append(["DOW", float(Dow_value),float(Dow_Gains)])


        tbl_Index.setColumnCount(3*len(lst_SPY))
        SPY_icon_up = QIcon(f"{self.icon_path}\\up.png")
        SPY_icon_down = QIcon(f"{self.icon_path}\\down.png")
        SPY_icon_equal = QIcon(f"{self.icon_path}\\equal.png")
        
        
        for row in range(len(lst_SPY)):
            for col in range(0,3):
                table_item = QTableWidgetItem()
                if col == 2 and lst_SPY[row][col] > 0.0:
                    # found change item add up/down arrow depending on the value
                    table_item.setText("{0:.2f}".format(lst_SPY[row][col]))
                    table_item.setIcon(SPY_icon_up)
                elif col == 2 and lst_SPY[row][col] < 0.0:
                    table_item.setText("{0:.2f}".format(lst_SPY[row][col]))
                    table_item.setIcon(SPY_icon_down)
                elif col == 2 and lst_SPY[row][col] == 0.0:
                    table_item.setText("{0:.2f}".format(lst_SPY[row][col]))
                    table_item.setIcon(SPY_icon_equal)
                else:
                    if col == 0:
                        table_item.setText(lst_SPY[row][col])
                    else:
                        table_item.setText("{0:.2f}".format(lst_SPY[row][col]))

                
                table_item.setFont(QFont("Arial",8))
                table_item.setBackground(QColor("Black"))
                table_item.setForeground(QColor("White"))
                if row > 0:
                    count += 1
                    tbl_Index.setColumnWidth(2+count, 55)
                    tbl_Index.setItem(0,2+count, table_item)
                elif row == 0:
                    tbl_Index.setItem(0,col, table_item)
                    tbl_Index.setColumnWidth(col, 55)

                    # else:
               
                    
              
        self.ui.statusBar.addWidget(tbl_Index,1)
            
       
        
        #set ticker_lst = prev_lst
        self.prev_ticker_lst = self.ticker_lst
        
      
        # #create an update worker thread to update the asset list every 10 seconds 
        self.update_thread = UpdateThread(self.updateLstAssets)
        self.update_thread.start()
  
        # show the Mainwindow
        self.show()
            
    
          
    def closeEvent(self, event):
        # Perform any cleanup or save operations here
        try:
            if self.update_thread is not None:
                self.update_thread.stop()
                self.update_thread.join(timeout=2)
            if self.command_thread is not None:
                self.command_thread.stop()
                self.command_thread.join(timeout=2)
            r.logout()
        except Exception as e:
            print(e)
        finally:
            event.accept()  # Accept the event to close the window

  



    def lstTerm_update_progress_fn(self, n):
        self.ui.lstTerm.addItem(n)
        return

    def updateStatusBar(self,temp_lst):
       
        self.totalGains,self.todayGains = self.cal_today_total_gains(temp_lst)
        frm_TotalGains = "{0:,.2f}".format(self.totalGains)
        frm_TodayGains = "{0:,.2f}".format(self.todayGains)

        lbltotal = self.ui.statusBar.findChild(QLabel, "lblStatusBar")
        lbltotal.setText(f"Total Assets: {self.ui.tblAssets.rowCount()}")

        lblGainToday = self.ui.statusBar.findChild(QLabel, "lblStatusBar_pctToday")
        lblGainToday.setText(f"Todays Gains: ${frm_TodayGains}")
        lblGainTotal = self.ui.statusBar.findChild(QLabel, "lblStatusBar_pctT")
        lblGainTotal.setText(f"Total Gains: ${frm_TotalGains}")
       
        # #setup the status table widget
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
        lst_SPY.append(["S&P", float(SPY_value),float(SPY_Gains)])
        lst_SPY.append(["Dow", float(Dow_value),float(Dow_Gains)])


        
        SPY_icon_up = QIcon(f"{self.icon_path}\\up.png")
        SPY_icon_down = QIcon(f"{self.icon_path}\\down.png")
        SPY_icon_equal = QIcon(f"{self.icon_path}\\equal.png")
        
        
        for row in range(len(lst_SPY)):
            for col in range(0,3):
                table_item = QTableWidgetItem()
                if col == 2 and lst_SPY[row][col] > 0.0:
                    # found change item add up/down arrow depending on the value
                    table_item.setText("{0:.2f}".format(lst_SPY[row][col]))
                    table_item.setIcon(SPY_icon_up)
                elif col == 2 and lst_SPY[row][col] < 0.0:
                    table_item.setText("{0:.2f}".format(lst_SPY[row][col]))
                    table_item.setIcon(SPY_icon_down)
                elif col == 2 and lst_SPY[row][col] == 0.0:
                    table_item.setText("{0:.2f}".format(lst_SPY[row][col]))
                    table_item.setIcon(SPY_icon_equal)
                else:
                    if col == 0:
                        table_item.setText(lst_SPY[row][col])
                    else:
                        table_item.setText("{0:.2f}".format(lst_SPY[row][col]))

                
                table_item.setFont(QFont("Arial",8))
                table_item.setBackground(QColor("Black"))
                table_item.setForeground(QColor("White"))
                if row > 0:
                    count += 1
                    tbl_Index.setColumnWidth(2+count, 55)
                    tbl_Index.setItem(0,2+count, table_item)
                elif row == 0:
                    tbl_Index.setItem(0,col, table_item)
                    tbl_Index.setColumnWidth(col, 55)


        return
    
    def updateLstAssets(self):        
        
        #setup timer for status bar and lstAssets
        
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
        lst_assets = []
        lst_elements_to_update = []
        get_selected_tickers = []
        #update the list every 10 seconds
        
        time.sleep(10)
        # if there is stocks in list update it every 10 seconds if there is something to update
        if len(self.ticker_lst) != 0: 
            lst_assets = self.ticker_lst
        
         
                #monitor the lstAsset selection
            #get_selected_tickers = self.get_tickers_from_selected_lstAssets()
        
        
            
            

            for item in lst_assets:
                last_price = r.get_quotes(item[0], "last_trade_price")[0]
                prev_close = r.get_quotes(item[0], "previous_close")[0]
                total_return = (float(last_price) - float(item[7])) * float(item[4])
                todays_return = (float(last_price) - float(prev_close)) * float(item[4]) 
                quantity = item[4]
                change = float(last_price) - float(prev_close)    
                lst_elements_to_update.append([f"{item[10]} ({item[0]})",float(last_price),change,item[4],todays_return,total_return])

            #update table
            for row in range(len(lst_elements_to_update)):
                for col in range(0,len(lst_elements_to_update[row])):
                    table_item = QTableWidgetItem()
                        
                    if col == 2 and lst_elements_to_update[row][col] > 0.0:
                        # found change item add up/down arrow depending on the value
                        table_item.setText("{0:.2f}".format(lst_elements_to_update[row][col]))
                        table_item.setIcon(QIcon(f"{self.icon_path}\\up.png"))
                        
                    elif col ==2 and lst_elements_to_update[row][col] < 0.0:
                        table_item.setText("{0:.2f}".format(lst_elements_to_update[row][col]))
                        table_item.setIcon(QIcon(f"{self.icon_path}\\down.png"))
                        
                    elif col == 2 and lst_elements_to_update[row][col] == 0.0:
                        table_item.setText("{0:.2f}".format(lst_elements_to_update[row][col]))
                        table_item.setIcon(QIcon(f"{self.icon_path}\\equal.png"))
                        
                    else:
                        if col == 0:
                            table_item.setText(lst_elements_to_update[row][col])
                        else:
                            table_item.setText("{0:.2f}".format(lst_elements_to_update[row][col]))   
                            
                        # if lst_elements_to_update[row][2] > 0.0:
                        #     table_item.setForeground(QColor("green"))
                            
                        # elif lst_elements_to_update[row][2] < 0.0:
                        #     table_item.setForeground(QColor("red"))
                    
                    table_item.setForeground(QColor("white"))
                    table_item.setBackground(QColor("black"))
                    table_item.setFlags(table_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    table_item.setFont(QFont("Arial",12,QFont.Weight.Bold))
                    self.ui.tblAssets.setItem(row,col,table_item)
                

                
        
            
            self.lstupdated_tblAssets = lst_elements_to_update
            
            self.plot.add_plot_to_figure(self.ticker_lst,get_selected_tickers,self.ui.cmbAction.currentText())           
            self.plot.draw()
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
                    #get total gains for the day
                    self.totalGains,self.todayGains = self.cal_today_total_gains(self.ticker_lst)
                    #setup plot widget
                    self.setup_plot(self.ticker_lst)
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
           self.ui.lblRaiseAmount.setText("Buy Selected Asset:")
           self.ui.lblRaiseAmount.setToolTip("Buy (,) Comma separated list of tickers")
           self.ui.lblRaiseAmount.setVisible(True)
           self.ui.edtRaiseAmount.setVisible(True)
           self.ui.lblDollarValueToSell.setText("Dollar value of Stock to Buy:")
           self.ui.lblDollarValueToSell.setVisible(True)
           self.ui.edtDollarValueToSell.setVisible(True)
           self.ui.edtBuyWithAmount.setVisible(True)
           self.ui.lblBuyWithAmount.setText("Buy with Amount (USD):")
           self.ui.lblBuyWithAmount.setVisible(True)

           self.ui.edtBuyWithAmount.setEnabled(True)   
           self.ui.edtBuyWithAmount.setText("")
           self.ui.edtBuyWithAmount.setForegroundRole(QPalette.ColorRole.WindowText)

        elif dollar_share == "Buy in Shares":
            self.ui.lblRaiseAmount.setText("Buy Selected Asset:")
            self.ui.lblRaiseAmount.setToolTip("Buy (,) Comma separated list of tickers")
            self.ui.lblRaiseAmount.setVisible(True)
            self.ui.edtRaiseAmount.setVisible(True)
            self.ui.lblDollarValueToSell.setText("Amount of Shares to Buy:")
            self.ui.lblDollarValueToSell.setVisible(True)
            self.ui.edtDollarValueToSell.setVisible(True)
            self.ui.lblBuyWithAmount.setText("Buy with Amount (est.)(USD):")
            self.ui.lblBuyWithAmount.setVisible(True)

           
        return
    
    def tblAsset_clicked(self):
        stock_tickers = []
        sel_items = [item.text() for item in self.ui.tblAssets.selectedItems()]
        
        selected_tickers = [sel_items[i:i+6][0] for i in range(0,len(sel_items),6)]
        if len(selected_tickers) > 0:
            for index, ticker in enumerate(selected_tickers):
                match = re.search(r"\((\w+)\)", ticker)
                stock_tickers.append(match.group(1))
               


        if len(selected_tickers) > 0:
            if self.ui.cmbAction.currentText() == "stock_info":
                self.plot.add_plot_to_figure(self.ticker_lst, stock_tickers,self.ui.cmbAction.currentText())
                self.plot.draw()
               

                
            #check to see if the action is sell selected
            elif self.ui.cmbAction.currentText() == "sell_selected":
            
                strjoinlst = ",".join(selected_tickers)
                self.ui.lblRaiseAmount.setVisible(True)
                self.ui.lblDollarValueToSell.setVisible(True)
                self.ui.edtRaiseAmount.setVisible(True)
                self.ui.edtDollarValueToSell.setVisible(True)
                self.ui.lblRaiseAmount.setText("Sell Selected Asset:")
                self.ui.edtRaiseAmount.setText(strjoinlst)
                
                

            elif self.ui.cmbAction.currentText() == "buy_selected" :

                strjoinlst = ",".join(selected_tickers)
                self.ui.lblRaiseAmount.setText("Buy Selected Asset:")
                self.ui.lblRaiseAmount.setToolTip("Buy (,) Comma separated list of tickers")
                self.ui.lblRaiseAmount.setVisible(True)
                self.ui.edtRaiseAmount.setVisible(True)
                self.ui.lblDollarValueToSell.setText("Amount of Shares to Buy:")
                self.ui.lblDollarValueToSell.setVisible(True)
                self.ui.edtDollarValueToSell.setVisible(True)
                self.ui.lblBuyWithAmount.setText("Buy with Amount (est.)(USD):")
                self.ui.lblBuyWithAmount.setVisible(True)

                self.ui.cmbDollarShare.setVisible(True)
                self.ui.cmbDollarShare.setCurrentIndex(0)
                self.ui.cmbDollarShare.setToolTip("Sell/Buy in US Dollars/Shares")
                
                
                self.ui.edtRaiseAmount.setText(strjoinlst)
                
            elif self.ui.cmbAction.currentText() == "buy_selected_with_x":
                strjoinlst = ",".join(selected_tickers)
                self.ui.lblRaiseAmount.setText("Buy Selected Asset:")
                self.ui.lblRaiseAmount.setVisible(True)
                self.ui.lblDollarValueToSell.setText("Buy Dollar value of each Stock(s):")
                self.ui.lblDollarValueToSell.setVisible(True)
                self.ui.edtRaiseAmount.setVisible(True)
                self.ui.edtDollarValueToSell.setVisible(True)
                self.ui.lblBuyWithAmount.setText("Buy with Amount:")
                self.ui.lblBuyWithAmount.setVisible(True)
                self.ui.edtBuyWithAmount.setVisible(True)

                
                self.ui.edtRaiseAmount.setText(strjoinlst)
                

            elif self.ui.cmbAction.currentText() == "raise_x_sell_y_dollars_except_z" or self.ui.cmbAction.currentText() == "raise_x_sell_y_dollars":

                self.ui.lblDollarValueToSell.setText("Dollar value to Sell of each Stock(s):")
                self.ui.lblRaiseAmount.setVisible(True)
                self.ui.lblDollarValueToSell.setVisible(True)
                self.ui.edtRaiseAmount.setVisible(True)
                self.ui.edtDollarValueToSell.setVisible(True)
                self.ui.lblRaiseAmount.setText("Raise Amount (USD):")
                self.ui.edtRaiseAmount.setText("")
                if self.ui.ledit_Iteration.text() != "":
                    self.ui.btnExecute.setEnabled(True)

            elif self.ui.cmbAction.currentText() == "sell_todays_return_except_x":
                strjoinlst = ",".join(selected_tickers)
                self.ui.lblRaiseAmount.setVisible(True)
                self.ui.lblDollarValueToSell.setVisible(True)
                self.ui.edtRaiseAmount.setVisible(True)
                self.ui.edtDollarValueToSell.setVisible(True)
                self.ui.lblRaiseAmount.setText("Sell Assets Except:")
                self.ui.edtRaiseAmount.setText(strjoinlst)
                self.ui.edtBuyWithAmount.setText("")
                self.ui.edtBuyWithAmount.setVisible(False)
               
                    
            elif self.ui.cmbAction.currentText() == "sell_gains_except_x":
                strjoinlst = ",".join(selected_tickers)
                self.ui.lblRaiseAmount.setVisible(True)
                self.ui.lblDollarValueToSell.setVisible(True)
                self.ui.edtRaiseAmount.setVisible(True)
                self.ui.edtDollarValueToSell.setVisible(True)
                self.ui.lblRaiseAmount.setText("Sell Assets Except:")
                self.ui.edtRaiseAmount.setText(strjoinlst)
             
            else:
                self.ui.lblRaiseAmount.setVisible(False)
                self.ui.lblDollarValueToSell.setVisible(False)
                self.ui.edtRaiseAmount.setVisible(False)
                self.ui.edtDollarValueToSell.setVisible(False)
                self.ui.lblRaiseAmount.setText("")
                self.ui.edtRaiseAmount.setText("")
                self.ui.lblBuyWithAmount.setVisible(False)
                self.ui.edtBuyWithAmount.setVisible(False)
               
                
                
            
        else:   #len(selected_tickers) == 0 #default
                self.ui.lblRaiseAmount.setVisible(False)
                self.ui.lblDollarValueToSell.setVisible(False)
                self.ui.edtRaiseAmount.setVisible(False)
                self.ui.edtDollarValueToSell.setVisible(False)
                self.ui.lblRaiseAmount.setText("")
                self.ui.edtRaiseAmount.setText("")
                self.ui.lblBuyWithAmount.setVisible(False)
                self.ui.edtBuyWithAmount.setVisible(False)
                self.ui.ledit_Iteration.setText("1")
                self.ui.cmbDollarShare.setVisible(False)
               
                self.setup_plot(self.ticker_lst)
               
            # self.ui.edtRaiseAmount.setVisible(False)
            # self.ui.edtRaiseAmount.setText("")
            # self.ui.lblRaiseAmount.setVisible(False)
            # self.ui.edtDollarValueToSell.setVisible(False)
            # self.ui.edtDollarValueToSell.setText("")
            # self.ui.edtBuyWithAmount.setText("")
            # 
            # self.ui.lblDollarValueToSell.setVisible(False)
            # self.ui.tblAssets.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
            # self.clear_selection_clicked()
            # self.setup_plot(self.ticker_lst)

        return

                
        
        

    def clear_selection_clicked(self):
        self.ui.tblAssets.clearSelection()
        self.setup_plot(self.ticker_lst)
       


    def closeMenu_clicked(self):
       
        cursor = QCursor()
        cursor.setShape(cursor.shape().WaitCursor)
       
        try:
            QApplication.setOverrideCursor(cursor)
            
            if self.update_thread is not None:
                self.update_thread.stop()
                self.update_thread.join(timeout=2)
            if self.command_thread is not None:
                self.command_thread.stop()
                self.command_thread.join(timeout=2)
          

            r.logout()
            self.close()
        except Exception as e:
            print(e)
            
        finally:
            QApplication.restoreOverrideCursor()
            sys.exit()
        #close the robinhood session
        
        #close the app
        

    def ledit_Iteration_textChanged(self):
        if re.match(r'^\d+$',self.ui.ledit_Iteration.text()) and self.ui.cmbAction.currentText() != "stock_info":
            self.ui.btnExecute.setEnabled(True)
        else:
            self.ui.btnExecute.setEnabled(False)

    def edtBuyWithAmount_changed(self):
        if re.match(r'^[1-9]+$',self.ui.edtBuyWithAmount.text()) and self.ui.cmbAction.currentText() != "stock_info":
            self.ui.btnExecute.setEnabled(True)
        else:
            self.ui.btnExecute.setEnabled(False)

    def edtDollarValueToSell_changed(self):

        priceTotal = 0.0
        dollar_share = self.ui.cmbDollarShare.currentText()

        if re.match(r'^\d+$',self.ui.edtDollarValueToSell.text()) and self.ui.cmbAction.currentText() != "stock_info":
            self.ui.btnExecute.setEnabled(True)
           
            if dollar_share == "Buy in USD":
                self.ui.lblRaiseAmount.setText("Buy Selected Asset:")
                self.ui.lblRaiseAmount.setToolTip("Buy (,) Comma separated list of tickers")
                self.ui.lblRaiseAmount.setVisible(True)
                self.ui.edtRaiseAmount.setVisible(True)
                self.ui.lblDollarValueToSell.setText("Dollar value of Stock to Buy:")
                self.ui.lblDollarValueToSell.setVisible(True)
                self.ui.edtDollarValueToSell.setVisible(True)
                self.ui.edtBuyWithAmount.setVisible(True)
                self.ui.lblBuyWithAmount.setText("Buy with Amount (USD):")
                self.ui.lblBuyWithAmount.setVisible(True)
            elif dollar_share == "Buy in Shares":
              
                #get comma separated stocks and get a total estimate it would cost to buy the shares
                lstShares = self.ui.edtRaiseAmount.text().split(',')
                for item in lstShares:
                    if item.strip() == "":
                        self.ui.btnExecute.setEnabled(False)
                        break
                    else:
                        #get latest price of the stock
                        last_price = r.get_quotes(item.strip(),"last_trade_price")[0]
                        priceTotal += float(last_price) * float(self.ui.edtDollarValueToSell.text())

                self.ui.lblBuyWithAmount.setText("Buy with Amount (est.)(USD):")
                self.ui.edtBuyWithAmount.setText(f"{priceTotal:.2f}")
                self.ui.edtBuyWithAmount.setEnabled(False)   
                self.ui.edtBuyWithAmount.setForegroundRole(QPalette.ColorRole.Shadow)
        else:
                self.ui.btnExecute.setEnabled(False)
                if dollar_share == "Buy in Shares":
                    self.ui.edtBuyWithAmount.setEnabled(False)   
                    self.ui.edtBuyWithAmount.setText("")
                    self.ui.edtBuyWithAmount.setForegroundRole(QPalette.ColorRole.Shadow)
                

    def edtRaiseAmount_changed(self):
        
        if re.match(r'^[A-Z,]+$',self.ui.edtRaiseAmount.text()) and self.ui.cmbAction.currentText() != "stock_info":
            return

        if re.match(r'^[1-9]+$',self.ui.edtRaiseAmount.text()) and self.ui.cmbAction.currentText() != "stock_info":
            self.ui.btnExecute.setEnabled(True)
        else:
            self.ui.btnExecute.setEnabled(False)
        

    def setup_plot(self,tickersPerf = []):
        action_selection = self.ui.cmbAction.currentText()
        self.plot.add_plot_to_figure(tickersPerf,self.get_tickers_from_selected_lstAssets(),action_selection)
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
        if self.command_thread.is_alive():
            self.command_thread.stop()

        
        self.ui.btnExecute.setStyleSheet("background-color: green; color: white;")  # Change background to green             
        self.ui.btnExecute.setText("Execute ...")
        self.ui.btnExecute.setEnabled(False)
        return
    
    def btnExecute_clicked(self):
        if self.ui.btnExecute.text() == "Cancel":
            self.Cancel_operation()
        elif self.ui.btnExecute.text() == "Execute ...":    
            self.Execute_operation()
            
    

    def cmbAction_clicked(self):
        perform_action = self.ui.cmbAction.currentText()
        
        if perform_action == "stock_info":
            self.ui.tblAssets.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
            self.ui.btnExecute.setEnabled(False)    

        elif perform_action == "raise_x_sell_y_dollars" or perform_action == "raise_x_sell_y_dollars_except_z":
            self.ui.edtRaiseAmount.setVisible(True)
            self.ui.lblRaiseAmount.setVisible(True)
            self.ui.lblRaiseAmount.setText("Raise Amount (USD):")
            self.ui.edtRaiseAmount.setText("")

            self.ui.edtDollarValueToSell.setVisible(True)
            self.ui.lblDollarValueToSell.setVisible(True)
            self.ui.tblAssets.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
            
        elif perform_action == "buy_lower_with_gains":
            #FIX ME
            self.ui.edtRaiseAmount.setVisible(True)
            self.ui.lblRaiseAmount.setVisible(True)
            self.ui.lblRaiseAmount.setText("Raise Amount (USD):")
            self.ui.edtRaiseAmount.setText("")

            self.ui.edtDollarValueToSell.setVisible(False)
            self.ui.lblDollarValueToSell.setVisible(False)
            self.ui.tblAssets.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
        elif perform_action == "buy_x_with_y_amount":

            self.ui.edtRaiseAmount.setVisible(True)
            self.ui.lblRaiseAmount.setVisible(True)
            self.ui.lblRaiseAmount.setText("Buy with Amount (USD):")
            self.ui.edtRaiseAmount.setText("")

            self.ui.edtDollarValueToSell.setVisible(True)
            self.ui.lblDollarValueToSell.setVisible(True) 
            
            self.ui.tblAssets.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
        elif perform_action == "buy":
                
            self.ui.lblRaiseAmount.setText("Buy Selected Asset:")
            self.ui.lblRaiseAmount.setToolTip("Buy (,) Comma separated list of tickers")
            self.ui.lblRaiseAmount.setVisible(True)
            self.ui.edtRaiseAmount.setVisible(True)
            self.ui.lblDollarValueToSell.setText("Dollar value of Stock to Buy:")
            self.ui.lblDollarValueToSell.setVisible(True)
            self.ui.edtDollarValueToSell.setVisible(True)
            self.ui.edtBuyWithAmount.setVisible(True)
            self.ui.lblBuyWithAmount.setText("Buy with Amount (USD):")
            self.ui.lblBuyWithAmount.setVisible(True)

            self.ui.cmbDollarShare.setVisible(True)
            self.ui.cmbDollarShare.setCurrentIndex(0)
            self.ui.cmbDollarShare.setToolTip("Sell/Buy in US Dollars/Shares")
        elif perform_action == "buy_selected":
            self.ui.lblRaiseAmount.setText("Buy Selected Asset:")
            self.ui.lblRaiseAmount.setToolTip("Buy (,) Comma separated list of tickers")
            self.ui.lblRaiseAmount.setVisible(True)
            self.ui.edtRaiseAmount.setVisible(True)
            self.ui.lblDollarValueToSell.setText("Amount of Shares to Buy:")
            self.ui.lblDollarValueToSell.setVisible(True)
            self.ui.edtDollarValueToSell.setVisible(True)
            self.ui.lblBuyWithAmount.setText("Buy with Amount (est.)(USD):")
            self.ui.lblBuyWithAmount.setVisible(True)
            self.ui.edtBuyWithAmount.setVisible(True)
            self.ui.cmbDollarShare.setVisible(True)
            self.ui.cmbDollarShare.setCurrentIndex(0)
            self.ui.cmbDollarShare.setToolTip("Sell/Buy in US Dollars/Shares")
            self.ui.tblAssets.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
        else: #default
            self.ui.edtRaiseAmount.setVisible(False)
            self.ui.edtRaiseAmount.setText("")
            self.ui.lblRaiseAmount.setVisible(False)
            self.ui.edtDollarValueToSell.setVisible(False)
            self.ui.edtDollarValueToSell.setText("")
            self.ui.edtBuyWithAmount.setText("")
            self.ui.ledit_Iteration.setText("")
            self.ui.lblDollarValueToSell.setVisible(False)
            self.ui.cmbDollarShare.setVisible(False)
            self.ui.tblAssets.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
            self.clear_selection_clicked()
            self.setup_plot(self.ticker_lst)
            

            
        
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
                    tickersPerf = self.ticker_lst
                    self.print_cur_protfolio(tickersPerf)
                    self.setup_plot(tickersPerf)
                    self.updateStatusBar(tickersPerf)
                except Exception as e:
                    if e.args[0] == "No stocks in account":
                        self.ui.lstTerm.addItem(f"Error: {e.args[0]}")
                        self.ticker_lst = []
                        self.print_cur_protfolio(self.ticker_lst)
                        self.setup_plot(self.ticker_lst)
                        self.updateStatusBar(self.ticker_lst)
                    
                    
               
               
            finally:
                QApplication.restoreOverrideCursor()
        
    
        
    
       
    def Execute_operation(self):

        lst = []
        num_iter = ''
        #check is all required values are entered
        num_iter,lst = self.check_and_read_conditions_met()
        if int(num_iter) == False and len(lst) == 0:
            return
        #all the conditions are met
        elif num_iter >= '1' and (len(lst) > 0 or lst[0] == 'dont care'):
            if lst[0] != 'dont care':
                # get the text of the selected items
                lst = self.get_tickers_from_selected_lstAssets()
            
      

        confirm = QMessageBox.question(self,"Confirm",f"Are you sure you want to execute operation '{self.ui.cmbAction.currentText()}'?",QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            
            #Change btnExecute to red cancel
            self.ui.btnExecute.setText("Cancel")
            self.ui.btnExecute.setStyleSheet("background-color: red; color: white;")  # Change background to red
           
            #call the method to execute
            name_of_method = self.ui.cmbAction.currentText()

           
          
            fn = getattr(self, name_of_method)
            
          
            raise_amount = self.ui.edtRaiseAmount.text()
            dollar_value_to_sell = self.ui.edtDollarValueToSell.text()
            buying_with_amount = self.ui.edtBuyWithAmount.text()

            self.command_thread = CommandThread(fn,num_iter,self.current_account_num,lst,raise_amount,dollar_value_to_sell,buying_with_amount) # Any other args, kwargs are passed to the run function
           

            # start thread
            self.command_thread.start()

            # if self.ui.btnExecute.text() == "Execute":
            #     self.ui.btnExecute.setText("Cancel Operation")
                
            # else:
            #     self.ui.btnExecute.setText("Cancel")
        else:
            #user pressed no
            self.ui.btnExecute.setText("Execute ...")
            self.ui.btnExecute.setStyleSheet("background-color: green; color: white;")
                
            
        return 
            


    def SelectAll_clicked(self):
        #select all items in the list
        self.ui.tblAssets.selectAll()
        self.ui.tblAssets.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
        self.ui.tblAssets.setFocus()
        return
    def print_cur_protfolio(self, curlist):
       
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
        #item[10]=stock_name
        join_list = []
        lst_elements_to_update = []
        #set header
        
        
        
        self.ui.tblAssets.setColumnCount(6)
        self.ui.tblAssets.setRowCount(len(curlist))
        
        
        self.ui.tblAssets.setColumnWidth(0,300)
        self.ui.tblAssets.setColumnWidth(1,65)
        self.ui.tblAssets.setColumnWidth(2,75)
        self.ui.tblAssets.setColumnWidth(3,75)
        self.ui.tblAssets.setColumnWidth(4,85)
        self.ui.tblAssets.setColumnWidth(5,85)
        
        
        self.ui.tblAssets.setHorizontalHeaderLabels(["Ticker","Price","Change","Quantity","Today's Return","Total Return"])
       
        cur_portfolio_file = os.path.join(self.data_path,"current_portfolio.csv")
        open_file = open(cur_portfolio_file,"w")
        
        for item in curlist:
            last_price = r.get_quotes(item[0], "last_trade_price")[0]
            prev_close = r.get_quotes(item[0], "previous_close")[0]
            total_return = (float(last_price) - float(item[7])) * float(item[4])
            todays_return = (float(last_price) - float(prev_close)) * float(item[4]) 
            quantity = item[4]
            change = float(last_price) - float(prev_close)  
              
            lst_elements_to_update.append([f"{item[10]} ({item[0]})",float(last_price),change,item[4],todays_return,total_return])

        #update table
        for row in range(len(lst_elements_to_update)):
            join_list.append(lst_elements_to_update[row][0])
            join_list.append(str(lst_elements_to_update[row][3]))
            for col in range(len(lst_elements_to_update[row])):
                table_item = QTableWidgetItem()
                    
                if col == 2 and lst_elements_to_update[row][col] > 0.0:
                    # found change item add up/down arrow depending on the value
                    table_item.setText("{0:.2f}".format(lst_elements_to_update[row][col]))
                    table_item.setIcon(QIcon(f"{self.icon_path}\\up.png"))
                    #table_item.setForeground(QColor("green"))
                elif col ==2 and lst_elements_to_update[row][col] < 0.0:
                    table_item.setText("{0:.2f}".format(lst_elements_to_update[row][col]))
                    table_item.setIcon(QIcon(f"{self.icon_path}\\down.png"))
                    #table_item.setForeground(QColor("red"))
                elif col == 2 and lst_elements_to_update[row][col] == 0.0:
                    table_item.setText("{0:.2f}".format(lst_elements_to_update[row][col]))
                    table_item.setIcon(QIcon(f"{self.icon_path}\\equal.png"))
                    #table_item.setForeground(QColor("grey"))
                else:
                    if col == 0:
                        table_item.setText(lst_elements_to_update[row][col])
                    else:
                        table_item.setText("{0:.2f}".format(lst_elements_to_update[row][col]))   
                    # if lst_elements_to_update[row][2] > 0.0: #change item[2]
                    #     table_item.setForeground(QColor("green"))
                    # elif lst_elements_to_update[row][2] < 0.0:
                    #     table_item.setForeground(QColor("red"))
           
                table_item.setForeground(QColor("white"))
                table_item.setBackground(QColor("black"))
                table_item.setFlags(table_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table_item.setFont(QFont("Arial",12,QFont.Weight.Bold))
                self.ui.tblAssets.setItem(row,col,table_item)
            
                
           
           
        plst = ",".join(join_list)
        open_file.write(plst)
        open_file.close()
        return
    
    def get_tickers_from_selected_lstAssets(self):
        stock_tickers = []
        sel_items = [item.text() for item in self.ui.tblAssets.selectedItems()]
        
        selected_tickers = [sel_items[i:i+6][0] for i in range(0,len(sel_items),6)]
        if len(selected_tickers) > 0 :
              for index, ticker in enumerate(selected_tickers):
                match = re.search(r"\((\w+)\)", ticker)
                stock_tickers.append(match.group(1))
                return stock_tickers
        return selected_tickers
    
    def get_stocks_from_portfolio(self, acc_num):


       

        positions = r.get_open_stock_positions(acc_num)
        if len(positions) == 0:
            raise Exception("No stocks in account")
        else:
            self.ui.lstTerm.clear()
            

        # Get Ticker symbols
        tickers = [r.get_symbol_by_url(item["instrument"]) for item in positions]
        #get stock names
        stock_name = [r.get_name_by_url(item["instrument"]) for item in positions]
        
        
        lastPrice = r.get_quotes(tickers, "last_trade_price")
        

        previous_close = r.get_quotes(tickers, "previous_close")
    
        pct_change = [(float(lastPrice[i]) - float(previous_close[i]))/float(previous_close[i])*100  for i in range(len(tickers))]
        change = [float(lastPrice[i]) - float(previous_close[i]) for i in range(len(tickers))]
        

        #change = lastPrice - previous_close

        # Get your quantities
        quantities = [float(item["quantity"]) for item in positions]
    

        # Get your average buy price
        avg_buy_price = [float(item["average_buy_price"]) for item in positions]
        # Calculate total returns
        total_return = [(float(lastPrice[i]) - avg_buy_price[i])*quantities[i] for i in range(len(tickers))]
        #calc Todays return
        todays_return = [(float(lastPrice[i]) - float(previous_close[i]))*quantities[i] for i in range(len(tickers))]

        # Calculate stock quantities to sell to get total returns
        stock_quantity_to_sell = [total_return[i] / float(lastPrice[i]) for i in range(len(tickers))]   
        # build tuple to iterate through and sell stocks
        history_week = r.get_stock_historicals(tickers, interval='hour', span='week', bounds='regular', info=None)

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
        #item[10] = stock name
        tickersPerf = list(zip(tickers,total_return,stock_quantity_to_sell,lastPrice,quantities,todays_return,history_week,avg_buy_price,pct_change,change,stock_name))
        return tickersPerf

    def cal_today_total_gains(self, list_p):
        
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
        
    def find_and_remove(self, tickers, in_exList,include_flag = None):
        
        if include_flag is None:
        # Create a new list excluding the items in in_exList
            updated_tickers = [ticker for ticker in tickers if ticker[0] not in in_exList]
        else:
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
        
        if self.ui.cmbAction.currentText() == "sell_gains_x" or \
            self.ui.cmbAction.currentText() == "buy_selected" or \
            self.ui.cmbAction.currentText() == "sell_selected" or \
            self.ui.cmbAction.currentText() == "sell_todays_return_x" or \
            self.ui.cmbAction.currentText() == "raise_x_sell_y_dollars_except_z" or \
            self.ui.cmbAction.currentText() == "sell_gains_except_x" or \
            self.ui.cmbAction.currentText() == "sell_todays_return_except_x" or \
            self.ui.cmbAction.currentText() == "sell_gains_x_except_z" or \
            self.ui.cmbAction.currentText() == "buy_selected_with_x":



            if len(self.ui.tblAssets.selectedItems()) == 0:
                msg = QMessageBox.warning(self,"Selection","Must select at least 1 item from the Asset list.",QMessageBox.StandardButton.Ok)
                if msg == QMessageBox.StandardButton.Ok:
                    return False,lst
            else:
                lst = self.ui.tblAssets.selectedItems()
                check_two = True
        else:
            lst = ['dont care']
            check_two = True
            
                

                
            

        if check_one and check_two:
            return txtIter,lst
        else:
            return False,lst

#----------------------------------------------------------------------------------------------------------------------------------
# buy_lower_with_gains FIX ME
# # -------------------------------------------------------------------------------------------------------------------------------------   
    def buy_lower_with_gains(self,n,acc_num,lst,raise_amount,dollar_value_to_sell):
        total_gains = 0.0
        money_spent = 0.0
        spent = 0.0
        stock_symbols = []
        #1 - open last stock_sell_gains.csv file
        #2 - iterate thru stocks and buy all stocks with current price < sold price with 50% gains from that stock.
        #3 - 

            #Item 0 =  tickers
            #Item 1 = Total_return
            #Item 2 = stock_quantity_to_sell/buy
            #Item 3 = last price
            #item[4]= your quantities
                #item[5]=today's return

        file_sell_agains_exists = os.path.exists("stocks_sell.csv")
        if file_sell_agains_exists:
            read_file = open("stocks_sell.csv","r")
            
            for line in read_file:
                stocks = line.split(',')
                
                #calc total gains from previous sale
                for i in stocks:
                    total = i.split(":")
                    #FIX ME contains = inPortfolio(total[0],tickersPerf)
                # if contains:
                    #    total_gains += float(total[1]) * float(total[2] )

                print(f"you have ${total_gains} to spend to buy shares")
                

                for stock in stocks:
                    stock_name,quantity,price_sold, = stock.split(":")
                    #--------see if stock is in current portfolio
                    #FIX ME contains = inPortfolio(stock_name,tickersPerf)
                    # if not contains :
                    #     next

                    #50% of gains = gains*.5
                    hlf_gain= float(quantity)*float(price_sold)*0.5

                    stock_market_prices = r.stocks.get_latest_price(stock_name)
                    market_price_of_stock = float(stock_market_prices[0])

                    buy_price = float("{0:,.2f}".format(market_price_of_stock))



                    #calc what quantity of the stock can be bought with the hlfgain
                    per_quantity = hlf_gain / buy_price
                    frm_per_quantity = float("{0:,.2f}".format(per_quantity) )

                    #---------------- market_price < price sold -------------------------------------------------
                    if market_price_of_stock < float(price_sold):
                        if (market_price_of_stock*per_quantity) <= total_gains:

                            if self.command_thread.stop_event.is_set():
                                print("stop event")
                                self.lstTerm_update_progress_fn("Operation Cancelled!")
                                break
                            if os.environ['debug'] == '0':
                                try:
                                    buy_info = r.order(symbol=stock_name,quantity=frm_per_quantity,side='buy',timeInForce='gfd',limitPrice=buy_price,account_number=acc_num)
                                except Exception as e:
                                    self.lstTerm_update_progress_fn(f"Error: {e.args[0]}")
                                    return  
                            time.sleep(5)
                            #Item 0 =  tickers     #Item 2 = stock_quantity_to_sell  #Item 3 = last price
                            stock_symbols.append(f"{stock_name}:{frm_per_quantity}:{buy_price}")
                            print(f"{frm_per_quantity} shares of {stock_name} bought at {buy_price}" )
                            spent -= frm_per_quantity*buy_price

                            #buying_power = calc_buying_power()
                            
            
            file_buy_write = open("stocks_buy.csv","w")
            stocks_format = ",".join(stock_symbols)
            file_buy_write.write(stocks_format)
            file_buy_write.close()
            money_spent = total_gains-spent
            print(f"You spent ${money_spent}!")
            stock_symbols = []
        
        return
#----------------------------------------------------------------------------------------------------------------------------------
# buy_selected
# # -------------------------------------------------------------------------------------------------------------------------------------   
    def buy(self,n,acc_num,lst,raise_amount,dollar_value_to_sell,buying_with):
        
               
        #Item[0] =  tickers
        #Item[1] = Total_return
        #Item[2] = stock_quantity_to_sell/buy
        #Item[3] = last price
        #item[4]= your quantities
        #item[5]=today's return
        #item[6]= 1 year history
        
        stocks_to_buy = []
        BuyinShares = 0
        buy_list = []
        dollar_value_to_buy = float(dollar_value_to_sell)
        buying_with_amount = float(buying_with)
        quantity_to_buy = 0.0
        stock_symbols = []
        money_left = buying_with_amount
        found = False
        tgains_actual = 0.0
        #tickersPerf = self.get_stocks_from_portfolio(acc_num)
        stocks_to_buy = raise_amount.split(',')

        
        while not (money_left <= 0.0) and BuyinShares != 1:
            if self.command_thread.stop_event.is_set():
                print("stop event")
                self.lstTerm_update_progress_fn("Operation Cancelled!")
                break
            for item in stocks_to_buy:
                # if there is no money left then break and continue buying the stocks that are in the list
                if money_left <= 0.0: 
                    break    
                
                last_price = r.get_quotes(item, "last_trade_price")[0]
                #buy in shares
                if (self.ui.cmbDollarShare.currentText() == "Buy in Shares"):
                    quantity_to_buy = dollar_value_to_buy
                    BuyinShares = 1

                    if not found:
                       itm = [item,quantity_to_buy,float(last_price)]
                       buy_list.append(itm)
                       money_left -= quantity_to_buy*float(last_price) 


                # Buy in dollars    
                else: 
                    quantity_to_buy = dollar_value_to_buy / float(last_price)     
                    BuyinShares = 0

                    for i,value in enumerate(buy_list): #check if already in list and return index
                        #if found in list add the quantity to buy
                        if value[0] == item:
                            exist_quantity = buy_list[i][1]
                            buy_list[i][1] = exist_quantity + quantity_to_buy
                            if BuyinShares:
                                money_left -= float(last_price)
                            else:
                                money_left -= quantity_to_buy*float(last_price)

                            found = True
                            break
                                    
                    if not found:
                        itm = [item,quantity_to_buy,float(last_price)]
                        buy_list.append(itm)
                        money_left -= quantity_to_buy*float(last_price)   
                
            
            
            
        

        for item in buy_list:    
            time.sleep(5)
            if self.command_thread.stop_event.is_set():
                print("stop event")
                self.lstTerm_update_progress_fn("Operation Cancelled!")
                break
            # Item[0] = stock_name
            # Item[1] = quantity to buy
            # Item[2] = last price        
            frm_quantity = "{0:.2f}".format(item[1])
            
            last_price = r.get_quotes(item, "last_trade_price")[0]
            buy_price = float(last_price) + 1.00
            frm_buy_price = "{0:.2f}".format(buy_price)

            if os.environ['debug'] == '0':
                try:
                   buy_info = r.order_buy_limit(symbol=item[0],quantity=frm_quantity,limitPrice=frm_buy_price,timeInForce='gfd',account_number=acc_num)
                except Exception as e:
                    self.lstTerm_update_progress_fn(f"Error: {e.args[0]}")
                    return
            
            
            #stock_order = r.get_stock_order_info(orderID=buy_info['id'])
            stock_symbols.append("{0}:{1}:{2}".format(item[0],frm_quantity,item[2]) ) 
            tot = float(item[1])*float(item[2])
            tgains_actual += float(tot)

            last_price = "{0:,.2f}".format(float(item[2]))
            frm_tot = "{0:,.2f}".format(tot)
            self.lstTerm_update_progress_fn(f"{frm_quantity} shares of {item[0]} bought at market price ${last_price} - Total: ${frm_tot}")
           
                    
            
    
        file_path = os.path.join(self.data_path,"stocks_buy.csv")
        file_buy_write = open(file_path,"w")
        stocks_format = ",".join(stock_symbols)
        file_buy_write.write(stocks_format)
        file_buy_write.close()
        stock_symbols = []   
        fmt_tgains_actual = "{0:,.2f}".format(tgains_actual*int(n))
        self.lstTerm_update_progress_fn(f"Operation Done! - Total=${fmt_tgains_actual}")
        #update ticker list for updated portfolio
        self.ticker_lst = self.get_stocks_from_portfolio(acc_num)
    
        return
#----------------------------------------------------------------------------------------------------------------------------------
# buy_selected
# # -------------------------------------------------------------------------------------------------------------------------------------   
    def buy_selected(self,n,acc_num,lst,raise_amount,dollar_value_to_sell,buying_with):
        
               
        #Item[0] =  tickers
        #Item[1] = Total_return
        #Item[2] = stock_quantity_to_sell/buy
        #Item[3] = last price
        #item[4]= your quantities
        #item[5]=today's return
        #item[6]= 1 year history
        
        stocks_to_buy = []
        
        dollar_value_to_buy = float(dollar_value_to_sell)
        stock_symbols = []
        tot = 0.0
        gtotal = 0.0
        tgains_actual = 0.0
        tickersPerf = self.get_stocks_from_portfolio(acc_num)
        
        
        n_tickersPerf = self.find_and_remove(tickersPerf, lst,1)
        sorted_lst = sorted(n_tickersPerf,key=lambda x: x[0])
        if os.environ['debug'] == '0':
            self.lstTerm_update_progress_fn(f"Buy Selected: Total = ${dollar_value_to_buy * len(lst)}") 
        else:
            print(f"Buy Selected: Total = ${dollar_value_to_buy * len(lst)}")

        file_buy_write = open("stocks_buy.csv","w")
        for index in range(int(n)):
            self.lstTerm_update_progress_fn(f"Iteration{index+1}")
            
            #if user click cancel then cancel operation
            if self.command_thread.stop_event.is_set():
                print("stop event")
                self.lstTerm_update_progress_fn("Operation Cancelled!")
                break
            
            stock_symbols = []
           

            #sell stocks if quantity_to_sell > 0 
            for item in sorted_lst:
                   #if user click cancel then cancel operation
                if self.command_thread.stop_event.is_set():
                    print("stop event")
                    self.lstTerm_update_progress_fn("Operation Cancelled!")
                    break

                if (self.ui.cmbDollarShare.currentText() == "Buy in Shares"):
                    quantity_to_buy = dollar_value_to_buy
                else:
                    quantity_to_buy = dollar_value_to_buy / float(item[3])     
                
                tot = quantity_to_buy*float(item[3])
                frm_quantity = "{0:.2f}".format(float(quantity_to_buy))

                if os.environ['debug'] == '0':
                    try:
                        buy_info = r.order(symbol=item[0],quantity=frm_quantity,side='buy',timeInForce='gfd',limitPrice=float(item[3])+0.02,account_number=acc_num)
                    except Exception as e:
                        self.lstTerm_update_progress_fn(f"Error: {e.args[0]}")
                        return
                time.sleep(5)

                    
                #Item 0 =  tickers     #Item 2 = stock_quantity_to_buy  #Item 3 = last price
                stock_symbols.append(f"{item[0]}:{frm_quantity}:{item[3]}")
                gtotal += tot 
                lprize = float(item[3])+0.50
                last_price = "{0:,.2f}".format(lprize)
                frm_tot = "{0:,.2f}".format(tot)
                self.lstTerm_update_progress_fn(f"{frm_quantity} of {item[0]} shares bought at market price - ${last_price} - Total: ${frm_tot}")
              
        
        stocks_format = ",".join(stock_symbols)
        file_buy_write.write(stocks_format)
            
            

        file_buy_write.close()
        
        self.lstTerm_update_progress_fn(f"Operation Done! - Total=${gtotal}")
        

        return

#------------------------------------------------------------------------------------------------------------
# buy_selected_with_x
# "Buy {dollar_value_to_buy} dollars of each stock in your portfolio until you cannot buy anymore with x ${with_buying_power}
# -------------------------------------------------------------------------------------------------------------------------------------
    def buy_selected_with_x(self,n,acc_num,lst,raise_amount,dollar_value_to_sell,buying_with):
        buying_power = float(buying_with)
        dollar_value_to_buy = float(dollar_value_to_sell)
        stock_symbols = []

        #confirm = input(f"\nBuy {dollar_value_to_buy} dollars of each stock in your portfolio until you cannot buy anymore with ${with_buying_power}
        buy_list = []
        found  = False
        
        tickersPerf = self.get_stocks_from_portfolio(acc_num)
        
        while not (buying_power <= 0):

            for item in tickersPerf:
                    #Item 0 =  tickers
                    #Item 1 = Total_return
                    #Item 2 = stock_quantity_to_sell/buy
                    #Item 3 = last price
                    #item[4]= your quantities
                    #item[5]=today's return

                if buying_power <= 0:
                    break    

                quantity_to_buy = dollar_value_to_buy / float(item[3])     
                strquantity_to_buy = "{0:,.2f}".format(quantity_to_buy)
                    

            
                for i,value  in enumerate(buy_list): #check if already in list and return index
                    if value[0] == item[0]:
                        exist_quantity = buy_list[i][1]
                        buy_list[i][1] = exist_quantity + float(strquantity_to_buy) 
                        buying_power -= quantity_to_buy*float(item[3])
                        found = True
                        break
                                
                if not found:
                    itm = [item[0],float(strquantity_to_buy),item[3]]
                    buy_list.append(itm)
                    buying_power -= quantity_to_buy*float(item[3])   
            
                        

        

        for item in buy_list:        
            frm_quantity = float(item[2])
            frm_quantity += 0.02
            str_quantity = str(frm_quantity)
            #if user click cancel then cancel operation
            if self.command_thread.stop_event.is_set():
                print("stop event")
                self.lstTerm_update_progress_fn("Operation Cancelled!")
                break

            if os.environ['debug'] == '0':
                try:
                    buy_info = r.order(symbol=item[0],quantity=item[1],side='buy',timeInForce='gfd',limitPrice=item[3]+0.2,account_number=acc_num)
                    if 'detail' in buy_info and buy_info['detail'] is not None:
                                self.lstTerm_update_progress_fn(f"Error: {buy_info['detail']}")
                except Exception as e:
                        self.lstTerm_update_progress_fn(f"Error: {e.args[0]}")
                        return
            time.sleep(5)
            #stock_order = r.get_stock_order_info(orderID=buy_info['id'])
            stock_symbols.append("{0}:{1}:{2}".format(item[0],item[1],str_quantity) ) 
            
    
            txt = "{} dollars of {} bought at market price ${}- {} shares"
           
            self.lstTerm_update_progress_fn(txt.format(dollar_value_to_buy, item[0],item[2],item[1]) )    
          

            # Item[0] = stock_name
            # Item[1] = quantity to buy
            # Item[2] = price bought    
            
    

        file_buy_write = open("stocks_buy.csv","w")
        stocks_format = ",".join(stock_symbols)
        file_buy_write.write(stocks_format)
        file_buy_write.close()
        stock_symbols = []
 
        self.lstTerm_update_progress_fn(f"Operation Done! - Total=${buying_power}")
        

        return
 
#----------------------------------------------------------------------------------------------------------------------------------
# buy_x_with_y_amount_except_z
# # -------------------------------------------------------------------------------------------------------------------------------------   
    def buy_x_with_y_amount_except_z(self,n,acc_num,lst,raise_amount,dollar_value_to_sell,buying_with):    
        print("buy_x_with_y_amount_except_z")

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
        n_tickersPerf = self.find_and_remove(tickersPerf, lst)
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
       

        tickersPerf = self.get_stocks_from_portfolio(acc_num)
        frm_quantity = "{0:,.2f}".format(float(dollar_value_to_sell))        
        n_tickersPerf = self.find_and_remove(tickersPerf, lst,1)
        sorderd_lst = sorted(n_tickersPerf,key=lambda x: x[0])
        
        self.lstTerm_update_progress_fn(f"Sell Selected: Total gains = ${dollar_value_to_sell*int(n)}") 
        

        file_path = os.path.join(self.data_path,"stocks_sell.csv")
        file_sell_write = open(file_path,"w")
        for index in range(int(n)):
            if self.command_thread.stop_event.is_set():
                print("stop event")
                self.lstTerm_update_progress_fn("Operation Cancelled!")
                break
            
            self.lstTerm_update_progress_fn(f"Iteration{index+1}")
            
            stock_symbols = []
            #sell stocks if quantity_to_sell > 0 
            for item in sorderd_lst:
              
                time.sleep(5)
                if self.command_thread.stop_event.is_set():
                    print("stop event")
                    self.lstTerm_update_progress_fn("Operation Cancelled!")
                    break
                
                shares_to_sell = float(dollar_value_to_sell)/float(item[3])
                # stock_quantity_to_sell and (your quantity > stock_quantity_to_sell)
                if float(item[4]*float(item[3])) > float(dollar_value_to_sell) :
                    if os.environ['debug'] == '0':
                        try:
                            sell_info = r.order_sell_market(symbol=item[0],quantity="{0:.2f}".format(shares_to_sell),timeInForce='gfd',account_number=acc_num)
                            if 'detail' in sell_info and sell_info['detail'] is not None:
                                self.lstTerm_update_progress_fn(f"Error: {sell_info['detail']}")
                        except Exception as e:
                            self.lstTerm_update_progress_fn(f"Error: {e.args[0]}")
                            return
                    

                    

                    
                    #Item 0 =  tickers     #Item 2 = stock_quantity_to_sell  #Item 3 = last price
                    stock_symbols.append(f"{item[0]}:{frm_quantity}:{item[3]}")
                    tot = float(dollar_value_to_sell)
                    tgains_actual += float(tot)

                    last_price = "{0:,.2f}".format(float(item[3]))
                    frm_tot = "{0:,.2f}".format(tot)
                    self.lstTerm_update_progress_fn(f"${frm_quantity} of {item[0]} shares sold at market price - ${last_price} - Total: ${frm_tot}")
                    
               
             
       
        stocks_format = ",".join(stock_symbols)
        file_sell_write.write(stocks_format)
            
            
        fmt_tgains_actual = "{0:,.2f}".format(tgains_actual*int(n))
        file_sell_write.close()
        self.lstTerm_update_progress_fn(f"Operation Done! - Total=${fmt_tgains_actual}")
      
        
        return
#----------------------------------------------------------------------------------------------------------------------
#  sell_gains
# -------------------------------------------------------------------------------------------------------------------------      
    def sell_gains(self,n,acc_num,lst,raise_amount,dollar_value_to_sell,buying_with):
        
        stock_symbols = []
        tgains_actual = 0.0
        

        #calc total gains
        tickersPerf = self.get_stocks_from_portfolio(acc_num)

        grand_total_gains,today_gains = self.cal_today_total_gains(tickersPerf)
      
        inse = "{0:,.2f}".format(float(grand_total_gains*int(n)))
           
          
        sorderd_lst = sorted(tickersPerf,key=lambda x: x[0])
          
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
        self.lstTerm_update_progress_fn(f"Total gains = ${inse}")
        

        file_path = os.path.join(self.data_path,"stocks_sell.csv")
        file_sell_write = open(file_path,"w")
        for index in range(int(n)):
            if self.command_thread.stop_event.is_set():
                print("stop event")
                self.lstTerm_update_progress_fn("Operation Cancelled!")
                break
            stock_symbols = []    
            self.lstTerm_update_progress_fn(f"Iteration: {index+1}")
            #sell stocks if quantity_to_sell > 0 
            for item in sorderd_lst: #
                frm_quantity = "{0:,.2f}".format(float(item[2]))
              
                
                time.sleep(5)
                    #if user click cancel then cancel operation
                if self.command_thread.stop_event.is_set():
                    print("stop event")
                    self.lstTerm_update_progress_fn("Operation Cancelled!")
                    break
            # stock_quantity_to_sell and (your quantity > stock_quantity_to_sell)
                if not (float(item[2]) <= 0) and (float(item[2]) >= 0.01) and (float(item[4]) > float(item[2])) :
                    if os.environ['debug'] == '0':
                        try:
                            sell_info = r.order_sell_market(symbol=item[0],quantity="{0:.2f}".format(float(item[2])),timeInForce='gfd',account_number=acc_num)
                            if 'detail' in sell_info and sell_info['detail'] is not None:
                                self.lstTerm_update_progress_fn(f"Error: {sell_info['detail']}")
                        except Exception as e:
                            self.lstTerm_update_progress_fn(f"Error: {e.args[0]}")
                            return
                    
                    
                    #Item 0 =  tickers     #Item 2 = stock_quantity_to_sell  #Item 3 = last price
                    stock_symbols.append(f"{item[0]}:{item[2]}:{item[3]}")
                    tot = float(item[2])*float(item[3])
                    tgains_actual += float(tot)

                    last_price = "{0:,.2f}".format(float(item[3]))
                    frm_tot = "{0:,.2f}".format(tot)
                    self.lstTerm_update_progress_fn(f"{frm_quantity} of {item[0]} shares sold at market price - ${last_price} - Total: ${frm_tot}")
                    
        
            
            stocks_format = ",".join(stock_symbols)
            file_sell_write.write(stocks_format)
            
            
        fmt_tgains_actual = "{0:,.2f}".format(tgains_actual)
        file_sell_write.close()
        self.lstTerm_update_progress_fn(f"Operation Done! - Total=${fmt_tgains_actual}")
        
        
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
    
        tot_gains = 0.0
        tot_tgains = 0.0
            
         
        stock_symbols = []
        tgains_actual = 0.0
                
                #exclude the tickets in excludeList
        tickersPerf = self.get_stocks_from_portfolio(acc_num)
        
        
        n_tickersPerf = self.find_and_remove(tickersPerf, lst)
        sorderd_lst = sorted(n_tickersPerf,key=lambda x: x[0])
        for item in sorderd_lst:
            if item[1] >= 0.0:    
                tot_gains += item[1]
            if item[5] >= 0.0:    
                tot_tgains += item[5]

        
        n_lst = self.get_tickers_from_selected_lstAssets()
        fmt_tot_gains = "{0:,.2f}".format(tot_gains*int(n)) 
          
            
        if os.environ['debug'] == '0':
            self.lstTerm_update_progress_fn(f"Sell Gains: Total gains ~ ${fmt_tot_gains} exclude = {n_lst}")
        
        file_path = os.path.join(self.data_path,"stocks_sell.csv")
        file_sell_write = open(file_path,"w")  
        
        for index in range(int(n)):
            self.lstTerm_update_progress_fn(f"Iteration{index+1}")
              #if user click cancel then cancel operation
            if self.command_thread.stop_event.is_set():
                print("stop event")
                self.lstTerm_update_progress_fn("Operation Cancelled!")
                break
            stock_symbols = []

            
                #sell stocks if quantity_to_sell > 0 
            for item in sorderd_lst: #
              
                time.sleep(5)
                 #if user click cancel then cancel operation
                if self.command_thread.stop_event.is_set():
                    print("stop event")
                    self.lstTerm_update_progress_fn("Operation Cancelled!")
                    break
                

                frm_quantity = "{0:,.2f}".format(float(item[2]))
                # stock_quantity_to_sell and (your quantity > stock_quantity_to_sell)
                if not (float(item[2]) <= 0) and (float(item[2]) >= 0.01) and (float(item[4]) > float(item[2])) :
                    if os.environ['debug'] == '0':
                        try:
                            sell_info = r.order_sell_market(symbol=item[0],quantity="{0:.2f}".format(float(item[2])),timeInForce='gfd',account_number=acc_num)
                            if 'detail' in sell_info and sell_info['detail'] is not None:
                                self.lstTerm_update_progress_fn(f"Error: {sell_info['detail']}")
                        except Exception as e:
                            self.lstTerm_update_progress_fn(f"Error: {e.args[0]}")
                            return
                    
                                             
                        #Item 0 =  tickers     #Item 2 = stock_quantity_to_sell  #Item 3 = last price
                    stock_symbols.append(f"{item[0]}:{item[2]}:{item[3]}")
                    tot = float(item[2])*float(item[3])
                    tgains_actual += float(tot)

                    last_price = "{0:,.2f}".format(float(item[3]))
                    frm_tot = "{0:,.2f}".format(tot)
                    self.lstTerm_update_progress_fn(f"{frm_quantity} of {item[0]} shares sold at market price - ${last_price} - Total: ${frm_tot}")

        
        stocks_format = ",".join(stock_symbols)
        file_sell_write.write(stocks_format)
                
            
                  
        file_sell_write.close()
        tgains_actual= "{0:,.2f}".format(tgains_actual)
        self.lstTerm_update_progress_fn(f"Operation Done! - Total=${tgains_actual}")
        

        return
    

            
#----------------------------------------------------------------------------------------------------------------------------------
# sell__todays_return
# -------------------------------------------------------------------------------------------------------------------------------------        
    def sell_todays_return(self,n,acc_num,lst,raise_amount,dollar_value_to_sell,buying_with):
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

        
        tickersPerf = self.get_stocks_from_portfolio(acc_num)
        
        sorderd_lst = sorted(tickersPerf,key=lambda x: x[0])
        grand_total_gains,tgains = self.cal_today_total_gains(sorderd_lst)
        fmt_tgains = "{0:,.2f}".format(tgains*int(n))     
       
        self.lstTerm_update_progress_fn(f"Sell Todays Return: Total gains = ${fmt_tgains}") 
        

        file_path = os.path.join(self.data_path,"stocks_sell.csv")
        file_sell_write = open(file_path,"w")
        for index in range(int(n)):
               #if user click cancel then cancel operation
            if self.command_thread.stop_event.is_set():
                print("stop event")
                self.lstTerm_update_progress_fn("Operation Cancelled!")
                break
            self.lstTerm_update_progress_fn(f"Iteration{index+1}")
            

            stock_symbols = []
            #sell stocks if quantity_to_sell > 0 
            for item in sorderd_lst: #
               
                time.sleep(5)
                  #if user click cancel then cancel operation
                if self.command_thread.stop_event.is_set():
                    print("stop event")
                    self.lstTerm_update_progress_fn("Operation Cancelled!")
                    break
                #cal how much to sell for today's gains
                amount_to_sell = float(item[5]) / float(item[3])
                frm_amount_to_sell = "{0:.2f}".format(amount_to_sell)

            # stock_quantity_to_sell and (your quantity > stock_quantity_to_sell) and todays_return >= 0
                if not (float(item[5]) <= 0.1) and (float(item[4]) > amount_to_sell) :
                    if os.environ['debug'] == '0':
                        try:
                            sell_info = r.order_sell_market(symbol=item[0],quantity=frm_amount_to_sell,timeInForce='gfd',account_number=acc_num)
                            if 'detail' in sell_info and sell_info['detail'] is not None:
                                self.lstTerm_update_progress_fn(f"Error: {sell_info['detail']}")
                                
                            
                        except Exception as e:
                            self.lstTerm_update_progress_fn(f"Error: {e.args[0]}")
                            self.lstTerm_update_progress_fn(f"Error: Continueing...")
                            continue
                    
                    
               
                    #Item 0 =  tickers     #Item 2 = stock_quantity_to_sell  #Item 3 = last price
                    stock_symbols.append(f"{item[0]}:{frm_amount_to_sell}:{item[3]}")
                    tot = amount_to_sell*float(item[3])
                    tgains_actual += tot

                    last_price = "{0:.2f}".format(float(item[3]))
                    frm_tot = "{0:,.2f}".format(tot)
                    self.lstTerm_update_progress_fn(f"{frm_amount_to_sell} of {item[0]} shares sold at market price - ${last_price} - Total: ${frm_tot}")

        
        stocks_format = ",".join(stock_symbols)
        file_sell_write.write(stocks_format)
        fmt_tgains_actual = "{0:.2f}".format(tgains_actual)
        file_sell_write.close() 
           
        self.lstTerm_update_progress_fn(f"Operation Done! - Total=${fmt_tgains_actual}")
        

        return
    

                                
#---------------------------------------------------------------------------------------------------------------------------
# Sell_todays_return_x (exclude list)
#---------------------------------------------------------------------------------------------------------------------------------
    def  sell_todays_return_except_x(self,n,acc_num,lst,raise_amount,dollar_value_to_sell,buying_with):
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

        excludeList = []
        stock_symbols = []
        tot_gains = 0.0
        tgains = 0.0
        tgains_actual = 0.0
              
      
        tickersPerf = self.get_stocks_from_portfolio(acc_num)
            
            #exclude the tickets in excludeList
        
            
        n_tickersPerf = self.find_and_remove(tickersPerf, lst)
          
        sorderd_lst = sorted(n_tickersPerf,key=lambda x: x[0])
        tot_gains,tgains = self.cal_today_total_gains(sorderd_lst)
        
      
        
        
                              
                                    
        fmt_tgains = "{0:,.2f}".format(tgains*int(n)) 
        
        
        self.lstTerm_update_progress_fn(f"Sell Today's Return: ~ ${fmt_tgains}, exclude = {lst}")
        

        file_path = os.path.join(self.data_path,"stocks_sell.csv")
        file_sell_write = open(file_path,"w")
        for index in range(int(n)):
              #if user click cancel then cancel operation
            if self.command_thread.stop_event.is_set():
                print("stop event")
                self.lstTerm_update_progress_fn("Operation Cancelled!")
                break
            self.lstTerm_update_progress_fn(f"Iteration{index+1}")
            

            #sell stocks if quantity_to_sell > 0 
            for item in sorderd_lst: #
                time.sleep(5)
                    #if user click cancel then cancel operation
                if self.command_thread.stop_event.is_set():
                    print("stop event")
                    self.lstTerm_update_progress_fn("Operation Cancelled!")
                    break
               

                              #cal how much to sell for today's gains
                amount_to_sell = float(item[5]) / float(item[3])
                frm_amount_to_sell = "{0:.2f}".format(amount_to_sell)

            # stock_quantity_to_sell and (your quantity > stock_quantity_to_sell) and todays_return >= 0
                if not (float(item[5]) <= 0.1) and (float(item[4]) > amount_to_sell) :
                    if os.environ['debug'] == '0':
                        try:
                            sell_info = r.order_sell_market(symbol=item[0],quantity=frm_amount_to_sell,timeInForce='gfd',account_number=acc_num)
                            if 'detail' in sell_info and sell_info['detail'] is not None:
                                self.lstTerm_update_progress_fn(f"Error: {sell_info['detail']}")
                        except Exception as e:
                            self.lstTerm_update_progress_fn(f"Error: {e.args[0]}")
                            return
                   
                    
                

                        
                    #Item 0 =  tickers     #Item 2 = stock_quantity_to_sell  #Item 3 = last price
                    stock_symbols.append(f"{item[0]}:{frm_amount_to_sell}:{item[3]}")
                    tot = amount_to_sell*float(item[3])
                    tgains_actual += tot

                    last_price = "{0:,.2f}".format(float(item[3]))
                    frm_tot = "{0:,.2f}".format(tot)
                    self.lstTerm_update_progress_fn(f"{frm_amount_to_sell} of {item[0]} shares sold at market price - ${last_price} - Total: ${frm_tot}")
                    



            
            stocks_format = ",".join(stock_symbols)
            file_sell_write.write(stocks_format)
        
        file_sell_write.close()
        stock_symbols = []   
        fmt_tgains_actual = "{0:,.2f}".format(tgains_actual) 
        
        self.lstTerm_update_progress_fn(f"Operation Done! - Total=${fmt_tgains_actual}")
        
        

        return
                
#---------------------------------------------------------------------------------------------------------------------------
# raise x (dollars) by selling y dollars of each stock
#---------------------------------------------------------------------------------------------------------------------------------
    def raise_x_sell_y_dollars(self,n,acc_num,lst,raise_amount,dollar_value_to_sell,buying_with):
      
        sell_list = []
        found  = False
        stock_symbols = []

        tickersPerf = self.get_stocks_from_portfolio(acc_num)
               
        sorderd_lst = sorted(tickersPerf,key=lambda x: x[0])
        
        
        
        accu_quantity_to_buy = 0.0
        raised_amount = 0.0
        
        n_raise_amount = float(raise_amount)
        n_dollar_value_to_sell = float(dollar_value_to_sell)
        frmt_dollar_value = "{0:,.2f}".format(n_dollar_value_to_sell)
        frmt_raise_amount = "{0:,.2f}".format(n_raise_amount)

        index = 0
        tgains_actual = 0.0
        self.lstTerm_update_progress_fn(f"Raise ${frmt_raise_amount} by selling ${frmt_dollar_value} dollars of each stock: Total gains = ${n_raise_amount}")
        while not (raised_amount >= n_raise_amount):
               #if user click cancel then cancel operation
            if self.command_thread.stop_event.is_set():
                print("stop event")
                self.lstTerm_update_progress_fn("Operation Cancelled!")
                break
            for item in sorderd_lst:
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

                if raised_amount >= n_raise_amount:
                    break    

                quantity_to_sell = n_dollar_value_to_sell / float(item[3])     
                strquantity_to_sell = "{0:,.2f}".format(quantity_to_sell)
                    

                
                for i,value  in enumerate(sell_list): #check if already in list and return index
                    #if found in list and you have enough shares to sell 
                    if (value[0] == item[0]) and (item[4] >= quantity_to_sell) :
                        exist_quantity = sell_list[i][1]
                        # stock_quantity_to_sell and (your quantity > stock_quantity_to_sell)
                            
                        sell_list[i][1] = "{0:.2f}".format(float(exist_quantity) + float(strquantity_to_sell))
                        raised_amount += quantity_to_sell*float(item[3])
                        found = True
                        break
                                
                if not found:
                    itm = [item[0],strquantity_to_sell,item[3]]
                    sell_list.append(itm)
                    raised_amount += quantity_to_sell*float(item[3])   
                
            
            
            
        

        for item in sell_list:    
               #if user click cancel then cancel operation
           
            time.sleep(5)
            if self.command_thread.stop_event.is_set():
                print("stop event")
                self.lstTerm_update_progress_fn("Operation Cancelled!")
                break
            # Item[0] = stock_name
            # Item[1] = quantity to sell
            # Item[2] = last price        
            frm_quantity = float(item[1])
            frm_quantity += 0.02
            str_quantity = str(frm_quantity)
            
            if os.environ['debug'] == '0':
                try:
                    sell_info = r.order_sell_market(symbol=item[0],quantity=item[1],timeInForce='gfd',account_number=acc_num)
                    if 'detail' in sell_info and sell_info['detail'] is not None:
                                self.lstTerm_update_progress_fn(f"Error: {sell_info['detail']}")
                except Exception as e:
                    self.lstTerm_update_progress_fn(f"Error: {e.args[0]}")
                    return
            
            
            #stock_order = r.get_stock_order_info(orderID=buy_info['id'])
            stock_symbols.append("{0}:{1}:{2}".format(item[0],item[1],str_quantity) ) 
            tot = float(item[1])*float(item[2])
            tgains_actual += float(tot)

            last_price = "{0:,.2f}".format(float(item[2]))
            frm_tot = "{0:,.2f}".format(tot)
            self.lstTerm_update_progress_fn(f"{str_quantity} shares of {item[0]} sold at market price ${last_price} - Total: ${frm_tot}")
           
                    
            
    
        file_path = os.path.join(self.data_path,"stocks_sell.csv")
        file_sell_write = open(file_path,"w")
        stocks_format = ",".join(stock_symbols)
        file_sell_write.write(stocks_format)
        file_sell_write.close()
        stock_symbols = []   
        fmt_tgains_actual = "{0:,.2f}".format(tgains_actual*int(n))
        self.lstTerm_update_progress_fn(f"Operation Done! - Total=${fmt_tgains_actual}")
        
    
        return
#---------------------------------------------------------------------------------------------------------------------------
# raise x (dollars) by selling y dollars of each stock except [exclude list]
#---------------------------------------------------------------------------------------------------------------------------------
    def raise_x_sell_y_dollars_except_z(self,n,acc_num,lst,raise_amount,dollar_value_to_sell,buying_with):
      
        sell_list = []
        found  = False
        stock_symbols = []

        tot_gains = 0.0
        tgains = 0.0

        tickersPerf = self.get_stocks_from_portfolio(acc_num)
     

        #exclude the tickets in excludeList
        
            
        n_tickersPerf = self.find_and_remove(tickersPerf, lst)
          
        sorderd_lst = sorted(n_tickersPerf,key=lambda x: x[0])
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
        n_lst = self.get_tickers_from_selected_lstAssets()

        for item in sorderd_lst:
            if item[1] >= 0.0:    
                tot_gains += item[1]
            if item[5] >= 0.0:    
                tgains += item[5]

        accu_quantity_to_buy = 0.0
        raised_amount = 0.0
        n_raise_amount = float(raise_amount)
        n_dollar_value_to_sell = float(dollar_value_to_sell)
        frmt_dollar_value = "{0:,.2f}".format(float(dollar_value_to_sell))
        frmt_raise_amount = "{0:,.2f}".format(float(raised_amount))

        index = 0
        tgains_actual = 0.0
        self.lstTerm_update_progress_fn(f"Raise {frmt_raise_amount} by selling ${frmt_dollar_value} of each stock exclude = {n_lst}: Total gains = ${tot_gains * int(n)} ")
        

        while not (raised_amount >= n_raise_amount):
              #if user click cancel then cancel operation
            if self.command_thread.stop_event.is_set():
                print("stop event")
                self.lstTerm_update_progress_fn("Operation Cancelled!")
                break
            #loop through the list of tickers and build a new list(sell_list) of quantities to sell
            for item in sorderd_lst:
                if self.command_thread.stop_event.is_set():
                    print("stop event")
                    self.lstTerm_update_progress_fn("Operation Cancelled!")
                    break
                #Item[0] =  tickers
                #Item[1] = Total_return
                #Item[2] = stock_quantity_to_sell/buy
                #Item[3] = last price
                #item[4]= your quantities
                #item[5]=today's return

                if raised_amount >= n_raise_amount:
                    break    

                quantity_to_sell = n_dollar_value_to_sell / float(item[3])     
                strquantity_to_sell = "{0:,.2f}".format(quantity_to_sell)
                
                                       
                for i,value  in enumerate(sell_list): #check if already in list and return index
                    #if found in list and you have enough shares to sell
                    if (value[0] == item[0]) and (item[4] >= quantity_to_sell) :
                        exist_quantity = sell_list[i][1]
                        sell_list[i][1] = "{0:.2f}".format(float(exist_quantity) + float(strquantity_to_sell))
                        raised_amount += quantity_to_sell*float(item[3])
                        found = True
                        break
                                
                if not found:
                    #sell list item[0] = stock_name
                    #sell list item[1] = quantity to sell
                    #sell list item[2] = last price
                    itm = [item[0],strquantity_to_sell,item[3]]
                    sell_list.append(itm)
                    raised_amount += quantity_to_sell*float(item[3])   
                
            
            
            
        

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
            frm_quantity = float(item[2])
            frm_quantity += 0.02
            str_quantity = str(frm_quantity)
            
            if os.environ['debug'] == '0':
                try:
                    sell_info = r.order_sell_market(symbol=item[0],quantity=item[1],timeInForce='gfd',account_number=acc_num)
                    if 'detail' in sell_info and sell_info['detail'] is not None:
                                self.lstTerm_update_progress_fn(f"Error: {sell_info['detail']}")
                except Exception as e:
                    self.lstTerm_update_progress_fn(f"Error: {e.args[0]}")
                    return
           
            
            stock_symbols.append("{0}:{1}:{2}".format(item[0],item[1],str_quantity) ) 
            tot = float(item[1])*float(item[2])
            tgains_actual += tot

            last_price = "{0:,.2f}".format(float(item[2]))
            frm_tot = "{0:,.2f}".format(tot)
            self.lstTerm_update_progress_fn(f"{frmt_dollar_value} dollars of {item[0]} sold at market price ${last_price} - Total: ${frm_tot} ")  
        
            
          
                    
            
    
        file_path = os.path.join(self.data_path,"stocks_sell.csv")
        file_sell_write = open(file_path,"w")
        stocks_format = ",".join(stock_symbols)
        file_sell_write.write(stocks_format)
        file_sell_write.close()
        stock_symbols = []  
        fmt_tgains_actual = "{0:,.2f}".format(tgains_actual*int(n))
        self.lstTerm_update_progress_fn(f"Operation Done! - Total=${fmt_tgains_actual}")
        

        return
    # end of class MainWIndow


class MpfCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=7, height=4):
          
        self.fig = mpf.figure(figsize=(width, height),style='charles',tight_layout=True)
        ax = self.fig.add_subplot(111)
        super().__init__(self.fig)

      
    
    def add_plot_to_figure(self,ticker_lst,selected_tickers=[],action_selection="stock_info"):

       

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
        x_data = []; y_data = []
        
    
        n_col = 1
        n_row = 1

        if  len(selected_tickers) == 0:
            self.fig.clear()
            n_row = 1
            n_col = 1
            index=1
            
            
            
            #fig = mpf.figure(figsize=(5,4), dpi=100,layout='constrained')
            #self.axes = fig.add_subplot(111)
                
            sorted_list = sorted(ticker_lst,key=lambda x: float(x[4])*float(x[3]),reverse=True)

            for item in sorted_list:
                x_data.append(item[0])
                y_data.append(float(item[4])*float(item[3]))

            ax = self.fig.add_subplot(n_row,n_col,index)

            ax.grid(True)
            ax.bar(x_data, y_data)
            ax.set_xlabel('Stocks')
            ax.set_ylabel('$value of stock')
            ax.set_title('Stocks Ticker/Quantity')
            ax.tick_params(axis='x', rotation=55)
            

            return
        elif action_selection == "stock_info" and len(selected_tickers) > 0:
            
            self.fig.clear()

            max_col = 4
            n_row = 1
            n_col=1
            index = 1
     
            

            hist_dict = r.get_stock_historicals(selected_tickers, interval='hour', span='week', bounds='regular', info=None)
            df = pd.DataFrame(hist_dict)
            #format datatable
            fmt_timestamp  = [pd.to_datetime(item) for item in df["begins_at"]]
            date_timeIndex = pd.DatetimeIndex(fmt_timestamp)
            
            df["begins_at"] = date_timeIndex # set the Date column as the index
            float_op = [float(item) for item in df['open_price']]
            float_cl = [float(item) for item in df['close_price']]
            float_hi = [float(item) for item in df['high_price']]
            float_lo = [float(item) for item in df['low_price']]


            df['open_price'] = float_op
            df['close_price'] = float_cl
            df['high_price'] = float_hi
            df['low_price'] = float_lo
            df.rename(columns={'open_price':'Open','close_price':'Close','high_price':'High','low_price':'Low','volume':'Volume'},inplace=True)
            df.set_index('begins_at',inplace=True) # Set the Date column as the index
            
          
           
            #split tickets in seperate plots
            for item in selected_tickers:
                df_plot = df[df['symbol'] == item]
                
                
                df_plot_slice = df_plot[['Open','Close','High','Low','Volume']] # Select required columns    
                ax_plot = self.fig.add_subplot(n_row,n_col,index)
                mpf.plot(df_plot_slice,ax=ax_plot,type='candle',xrotation=15)
                ax_plot.set_title(f"{item} - 1 week")
                ax_plot.axes.set_xlabel('Date')
                ax_plot.set_ylabel('Price')             
        
            return
        elif action_selection != "stock_info" and len(selected_tickers) > 0:
            self.fig.clear()
            n_row = 1
            n_col = 1
            index=1
            
            
            
            #fig = mpf.figure(figsize=(5,4), dpi=100,layout='constrained')
            #self.axes = fig.add_subplot(111)
                
            sorted_list = sorted(ticker_lst,key=lambda x: float(x[4])*float(x[3]),reverse=True)

            for item in sorted_list:
                x_data.append(item[0])
                y_data.append(float(item[4])*float(item[3]))

            ax = self.fig.add_subplot(n_row,n_col,index)

            ax.grid(True)
            ax.bar(x_data, y_data)
            ax.set_xlabel('Stocks')
            ax.set_ylabel('$value of stock')
            ax.set_title('Stocks Ticker/Quantity')
            ax.tick_params(axis='x', rotation=55)
            return