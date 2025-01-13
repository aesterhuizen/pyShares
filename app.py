import os
import sys,traceback # type: ignore
import time
import pyotp
import robin_stocks.robinhood as r
import matplotlib


from dotenv import load_dotenv, set_key

matplotlib.use('QtAgg')

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QDialog, QDialogButtonBox, \
                            QFileDialog, QPushButton ,QLabel, QVBoxLayout, QHBoxLayout, QLineEdit
                            
from PyQt6.QtGui import QAction, QIcon, QCursor
from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSlot, pyqtSignal, QSize

from layout import Ui_MainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(object)

class Worker_Thread(QRunnable):
    def __init__(self,fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress
    
    @pyqtSlot()
    def run(self):
        
        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done
        #comment in app.py

class msgBoxGetCredentialFile(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Set Data File")

        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        
        # Access individual buttons
        self.okButton = self.buttonBox.button(QDialogButtonBox.StandardButton.Ok)
        self.cancelButton = self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel)
        self.okButton.setEnabled(False)

        # Connect signals
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        #self.buttonBox.setEnabled(False)

        vlayout = QVBoxLayout()
       
        message = QLabel("Path to Credential File: ")
        self.edtCred_path = QLineEdit('<credential file>')
        btnBrowse = QPushButton("Browse")
        self.edtCred_path.textChanged.connect(self.textChanged)
        
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.edtCred_path)
        hlayout.addWidget(btnBrowse)

        btnBrowse.clicked.connect(self.browse_clicked)

        
        vlayout.addWidget(message)
        vlayout.addLayout(hlayout)
        vlayout.addWidget(self.buttonBox)

        self.setLayout(vlayout)
    
    def textChanged(self):
        if self.edtCred_path.text() == "<credential file>":
            self.okButton.setEnabled(False)
        else:
            self.okButton.setEnabled(True)

    def browse_clicked(self):
        options = QFileDialog.Option.DontUseNativeDialog
       
        file_name, _ = QFileDialog.getOpenFileName(None, "Open File", f"{os.path.curdir}", "All Files (*);;Python Files (*.py)", options=options)
        if file_name:
            self.edtCred_path.setText(file_name)

        
        return
    

class msgBoxGetAccounts(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add Account")

        QBtn = QDialogButtonBox.StandardButton.Ok 

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.setEnabled(False)
        self.buttonBox.accepted.connect(self.accept)
        #self.buttonBox.rejected.connect(self.reject)
        #self.buttonBox.setEnabled(False)

        vlayout = QVBoxLayout()
       
        message = QLabel("Account number: ")
        self.ledit = QLineEdit('0')
        self.ledit.textChanged.connect(self.textChanged)
        

        
        vlayout.addWidget(message)
        vlayout.addWidget(self.ledit)
        #vlayout.addWidget(hlayout)
        vlayout.addWidget(self.buttonBox)
        self.setLayout(vlayout)

    def textChanged(self):
        if self.ledit.text() == "":
            self.buttonBox.setEnabled(False)
        else:
            self.buttonBox.setEnabled(True)

        return
   

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)


class MainWindow(QMainWindow):

    
    def __init__(self):
        super().__init__()

        #class variabled
        # self.quantity = []

        
       
        # self.stock_quantity_to_sell = 0
        # self.quantity_to_sell = 0
        # self.quantity_to_sell = 0
        # self.quantity_to_buy = 0
        # self.dollar_value_to_buy  = 0
        # self.with_buying_power = 0
        # self.quantity_left = 0
        # self.mystocks_dict = {}
        # self.account_dict = {}
        # self.raise_amount = 0
        self.totalGains = 0.0
        self.todayGains = 0.0

        # self.stock_quantity_to_sell = 0
        self.current_account_num = ""
        self.account_info = ''
        self.curAccountTickers_and_Quanties = []
        self.plot = MplCanvas(self, width=5, height=4, dpi=100)
        
        # setup UI
        self.ui = Ui_MainWindow()       
        
        self.ui.setupUi(self)
        self.setWindowTitle("PyShares - v1.0.0")
        self.setGeometry(300, 300, 2500, 1000)
        
        self.ui.splt_horizontal.setSizes([500, 1600])
        self.ui.splt_Vertical.setSizes([450, 50])
        
        self.ui.edtRaiseAmount.setVisible(False)
        self.ui.lblRaiseAmount.setVisible(False)
        self.ui.edtDollarValueToSell.setVisible(False)
        self.ui.lblDollarValueToSell.setVisible(False)

        self.ui.grdGraph.addWidget(self.plot)
        #Create a thread manager    
        self.threadpool = QThreadPool()
        #load credentials file
        if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the PyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app 
        # path into variable _MEIPASS'.
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        get_cred_file = msgBoxGetCredentialFile()
        button = get_cred_file.exec() #show the popup box for the user to enter account number
        if button == 1:
            self.env_path = get_cred_file.edtCred_path.text()
            #load credentials file                                     
            load_dotenv(self.env_path)
    
            #login to Robinhood
            otp = pyotp.TOTP(os.environ['robin_mfa']).now()
            r.login(os.environ['robin_username'],os.environ['robin_password'], mfa_code=otp)
            
            #Get account numers and populate comboboxes
            self.account_info = os.environ['account_number']
            #There is an account number
            if self.account_info != '':
                if self.account_info.find(',') != -1:
                    slice_account = self.account_info.split(',')
                    for item in slice_account:
                        self.ui.cmbAccount.addItem(item)
                else:
                    self.ui.cmbAccount.addItem(self.account_info)
                
                self.current_account_num = self.ui.cmbAccount.currentText().split(' ')[0]       
                self.curAccountTickers_and_Quanties = self.get_stocks_from_portfolio(self.current_account_num)
                self.print_cur_protfolio(self.curAccountTickers_and_Quanties)
                #get total gains for the day
                self.totalGains,self.todayGains = self.cal_total_gains(self.curAccountTickers_and_Quanties)
                #setup plot widget
                self.setup_plot(self.curAccountTickers_and_Quanties)
        
        
      


        #Setup signals / Slots
    
        
        icon_path = os.path.join(base_path,"icons")
        #menu Qaction_exit
        self.ui.action_Exit.triggered.connect(self.closeMenu_clicked)
        self.ui.actionCredentials_File.triggered.connect(self.Show_msgCredentials)
        
        #Toolbar
        self.ui.toolBar.setIconSize(QSize(32,32))
        button_action = QAction(QIcon(icon_path +'/application--arrow.png'), "Exit", self)
        button_action.triggered.connect(self.closeMenu_clicked)
        button_action = self.ui.toolBar.addAction(button_action)

        #add credentials button
        button_cred_action = QAction(QIcon(icon_path +'/animal-monkey.png'), "Credentials", self)
        button_cred_action.triggered.connect(self.Show_msgCredentials)
        button_cred_action = self.ui.toolBar.addAction(button_cred_action)


        #connect sigals and slots Account combo box
        self.ui.cmbAccount.activated.connect(self.account_clicked)
        #connect sigals and slots Actions combo box
        self.ui.cmbAction.activated.connect(self.cmbAction_clicked)
        #connect signal/slot for Execute button
        self.ui.btnExecute.clicked.connect(self.btnExecute_clicked)
        #connect GetAccount button
        self.ui.btnStoreAccounts.clicked.connect(self.StoreAccounts)
        #connect signal/slot for edtRaiseAmount
        self.ui.edtRaiseAmount.textChanged.connect(self.edtRaiseAmount_changed)
        #connect signal/slot for edtDollarValueToSell
        self.ui.edtDollarValueToSell.textChanged.connect(self.edtDollarValueToSell_changed)
        #connect clear selection button
        self.ui.btnClearSelec.clicked.connect(self.clear_selection_clicked)  
        #connect the list asset box
        self.ui.lstAssets.itemSelectionChanged.connect(self.lstAsset_clicked)
        #setup status bar
        lblStatusBar = QLabel(f"Total Assets: {self.ui.lstAssets.count()}")
        lblStatusBar.setMinimumWidth(50)
        lblStatusBar.setObjectName("lblStatusBar")
        self.ui.statusBar.addWidget(lblStatusBar,1)

        frm_TotalGains = "{0:.2f}".format(self.totalGains)
        lblStatusBar_pctT = QLabel(f"Total Gains: ${frm_TotalGains}")
        lblStatusBar_pctT.setObjectName("lblStatusBar_pctT")
        lblStatusBar_pctT.setMinimumWidth(120)
        self.ui.statusBar.addWidget(lblStatusBar_pctT,1)

        frm_TodayGains = "{0:.2f}".format(self.todayGains)
        lblStatusBar_pctToday = QLabel(f"Todays Gains: ${frm_TodayGains}")
        lblStatusBar_pctToday.setObjectName("lblStatusBar_pctToday")

        lblStatusBar_pctToday.setMinimumWidth(120)
        self.ui.statusBar.addWidget(lblStatusBar_pctToday,1)
        # show the Mainwindow
        self.show()
            
            
      
     



    def Show_msgCredentials(self):
        get_cred_file = msgBoxGetCredentialFile()
        button = get_cred_file.exec() #show the popup box for the user to enter account number
        if button == 1:
            wait_cursor = QCursor()
            wait_cursor.setShape(wait_cursor.shape().WaitCursor)

            QApplication.setOverrideCursor(wait_cursor)
            try:
                self.env_path = get_cred_file.edtCred_path.text()
                #load credentials file                                     
                load_dotenv(self.env_path)

                #login to Robinhood
                otp = pyotp.TOTP(os.environ['robin_mfa']).now()
                r.login(os.environ['robin_username'],os.environ['robin_password'], mfa_code=otp)
                
                #Get account numers and populate comboboxes
                self.account_info = os.environ['account_number']
                #There is an account number
                if self.account_info != '':
                    if self.account_info.find(',') != -1:
                        slice_account = self.account_info.split(',')
                        for item in slice_account:
                            self.ui.cmbAccount.addItem(item)
                    else:
                        self.ui.cmbAccount.addItem(self.account_info)
                    
                    self.current_account_num = self.ui.cmbAccount.currentText().split(' ')[0]       
                    self.curAccountTickers_and_Quanties = self.get_stocks_from_portfolio(self.current_account_num)
                    self.print_cur_protfolio(self.curAccountTickers_and_Quanties)
                    #get total gains for the day
                    self.totalGains,self.todayGains = self.cal_total_gains(self.curAccountTickers_and_Quanties)
                    #setup plot widget
                    self.setup_plot(self.curAccountTickers_and_Quanties)
                    #edit status bar
            
                frm_TotalGains = "{0:.2f}".format(self.totalGains)
                frm_TodayGains = "{0:.2f}".format(self.todayGains)

                lbltotal = self.ui.statusBar.findChild(QLabel, "lblStatusBar")
                lbltotal.setText(f"Total Assets: {self.ui.lstAssets.count()}")

                lblGainToday = self.ui.statusBar.findChild(QLabel, "lblStatusBar_pctToday")
                lblGainToday.setText(f"Todays Gains: ${frm_TodayGains}")
                lblGainTotal = self.ui.statusBar.findChild(QLabel, "lblStatusBar_pctT")
                lblGainTotal.setText(f"Total Gains: ${frm_TotalGains}")
            finally:
                #Restore the cursor
                
                QApplication.restoreOverrideCursor()
        else:
            return


    def lstAsset_clicked(self):
        
        sel_items = [item.text().split(' ')[0] for item in self.ui.lstAssets.selectedItems()]
        
        if len(sel_items) > 0:
            #check to see if the action is sell selected
            if self.ui.cmbAction.currentText() == "sell_selected":
            
                strjoinlst = ",".join(sel_items)
                self.ui.lblRaiseAmount.setVisible(True)
                self.ui.lblDollarValueToSell.setVisible(True)
                self.ui.edtRaiseAmount.setVisible(True)
                self.ui.edtDollarValueToSell.setVisible(True)

                self.ui.lblRaiseAmount.setText("Sell Selected Asset:")
                self.ui.edtRaiseAmount.setText(strjoinlst)

            elif self.ui.cmbAction.currentText() == "raise_x_sell_y_dollars_except_z" or self.ui.cmbAction.currentText() == "raise_x_sell_y_dollars":

                self.ui.lblRaiseAmount.setVisible(True)
                self.ui.lblDollarValueToSell.setVisible(True)
                self.ui.edtRaiseAmount.setVisible(True)
                self.ui.edtDollarValueToSell.setVisible(True)
                self.ui.lblRaiseAmount.setText("Raise Amount (USD):")
                self.ui.edtRaiseAmount.setText("")
            else:
                self.ui.lblRaiseAmount.setVisible(False)
                self.ui.lblDollarValueToSell.setVisible(False)
                self.ui.edtRaiseAmount.setVisible(False)
                self.ui.edtDollarValueToSell.setVisible(False)
                self.ui.lblRaiseAmount.setText("")
                self.ui.edtRaiseAmount.setText("")
            
        else:
                self.ui.lblRaiseAmount.setVisible(False)
                self.ui.lblDollarValueToSell.setVisible(False)
                self.ui.edtRaiseAmount.setVisible(False)
                self.ui.edtDollarValueToSell.setVisible(False)
                self.ui.lblRaiseAmount.setText("")
                self.ui.edtRaiseAmount.setText("")


        return

                
        
        

    def clear_selection_clicked(self):
        self.ui.lstAssets.clearSelection()


    def closeMenu_clicked(self):
       
        #close the robinhood session
        r.logout()
        #close the app
        sys.exit()

    def edtDollarValueToSell_changed(self):
        if (self.ui.edtDollarValueToSell.text() == "" or self.ui.edtDollarValueToSell.text() == "0") and \
            (self.ui.edtRaiseAmount.text() == "" or self.ui.edtRaiseAmount.text() == "0"):
            
            self.ui.btnExecute.setEnabled(False)
        else:
            self.ui.btnExecute.setEnabled(True)

    def edtRaiseAmount_changed(self):
        if (self.ui.edtRaiseAmount.text() == "" or self.ui.edtRaiseAmount.text() == "0") and \
            (self.ui.edtDollarValueToSell.text() == "" or self.ui.edtDollarValueToSell.text() == "0"):

            self.ui.btnExecute.setEnabled(False)
        else:
            self.ui.btnExecute.setEnabled(True)
        

    def setup_plot(self,tickersPerf):
        
        #Item 0 =  tickers
        #Item 1 = Total_return
        #Item 2 = stock_quantity_to_sell/buy
        #Item 3 = last price
        #item[4]= your quantities
        #item[5]=today's return
        x_data = []; y_data = []; bar_labels = []
        sorted_list = sorted(tickersPerf,key=lambda x: float(x[4])*float(x[3]),reverse=True)

        for item in sorted_list:
            x_data.append(item[0])
            y_data.append(float(item[4])*float(item[3])) 
            
        self.plot.axes.clear()
        self.plot.axes.grid(True)
        self.plot.axes.bar(x_data, y_data)
        self.plot.axes.set_xlabel('Stocks')
        self.plot.axes.set_ylabel('$value of stock')
        self.plot.axes.set_title('Stocks Ticker/Quantity')
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
    #Progress function from the worker threads
    def progress_fn(self, n):
        self.ui.lstTerm.addItem(n)
        
  


    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print("THREAD COMPLETE!")
   
              

    def btnExecute_clicked(self):
        self.Execute_operation()
    

    def cmbAction_clicked(self):
        perform_action = self.ui.cmbAction.currentText()
        # self.ui.btnExecute.setEnabled(False)
        if perform_action == "raise_x_sell_y_dollars" or perform_action == "raise_x_sell_y_dollars_except_z":
            self.ui.edtRaiseAmount.setVisible(True)
            self.ui.lblRaiseAmount.setVisible(True)
            self.ui.lblRaiseAmount.setText("Raise Amount (USD):")
            self.ui.edtRaiseAmount.setText("")

            self.ui.edtDollarValueToSell.setVisible(True)
            self.ui.lblDollarValueToSell.setVisible(True)
            
        else:
            self.ui.edtRaiseAmount.setVisible(False)
            self.ui.lblRaiseAmount.setVisible(False)
            self.ui.edtDollarValueToSell.setVisible(False)
            self.ui.lblDollarValueToSell.setVisible(False)
            
        self.clear_selection_clicked()
        
   


    def account_clicked(self):
        #check to see if the account number has changed
        #if it has update the lstAsset list and plot
        # if NOT return
        if self.current_account_num != self.ui.cmbAccount.currentText().split(' ')[0]:

            self.current_account_num = self.ui.cmbAccount.currentText().split(' ')[0]
            accountNum = self.current_account_num
            if self.ui.lstAssets.count() > 0:
                self.ui.lstAssets.clear()
            #get tickers in portfolio
            
            self.curAccountTickers_and_Quanties = self.get_stocks_from_portfolio(accountNum)
            tickersPerf = self.curAccountTickers_and_Quanties
            # add current trickets to Qtlist
            self.print_cur_protfolio(tickersPerf)
            self.setup_plot(tickersPerf)
        
    
        
    
       
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
                lst = [(item.text().split('\t')[0]).strip() for item in lst]
            
      

        confirm = QMessageBox.question(self,"Confirm","Are you sure you want to execute this operation?",QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:

         #call the method to execute
            name_of_method = self.ui.cmbAction.currentText()
            method = getattr(self, name_of_method,lambda: 'No operation of that name')
          
            raise_amount = self.ui.edtRaiseAmount.text()
            dollar_value_to_sell = self.ui.edtDollarValueToSell.text()
            

            worker = Worker_Thread(method,num_iter,self.current_account_num,lst,raise_amount,dollar_value_to_sell) # Any other args, kwargs are passed to the run function
            
            worker.signals.result.connect(self.print_output)
            worker.signals.finished.connect(self.thread_complete)
            worker.signals.progress.connect(self.progress_fn)

            # Execute
            #self.threadpool.start(worker)
            return method(num_iter,self.current_account_num,lst,raise_amount,dollar_value_to_sell, self.progress_fn)
            



    def print_cur_protfolio(self, curlist):
       

        # print ("Current Protfolio: ")
        # print ("Ticker\tQuantity")
        tmp_list = []

        txt = "{:<5}\t{:>5}"
      

        for item in curlist:
            tmp_list.append(txt.format(item[0],item[4]) )
            
        tmp_list.sort()
        tmp_list.insert(0,txt.format("Ticker","Quantity"))
        #add items to the QTList list
        self.ui.lstAssets.addItems(tmp_list)
        
        open_file = open("current_portfolio.csv","w")
        join_list = ",".join(tmp_list)
        open_file.write(join_list)
        open_file.close()
        return

    def get_stocks_from_portfolio(self, acc_num):
            
        positions = r.get_open_stock_positions(acc_num)
        # Get Ticker symbols
        tickers = [r.get_symbol_by_url(item["instrument"]) for item in positions]

        lastPrice = r.get_quotes(tickers, "last_trade_price")
        

        previous_close = r.get_quotes(tickers, "previous_close")
    

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

        tickersPerf = list(zip(tickers,total_return,stock_quantity_to_sell,lastPrice,quantities,todays_return,history_week))
        return tickersPerf

    def cal_total_gains(self, list_p):
        
        grand_total_gains = 0.0
        todays_gains = 0.0
            #Item 0 =  tickers
        #Item 1 = Total_return
        #Item 2 = stock_quantity_to_sell/buy
        #Item 3 = last price
        #item[4]= your quantities
        #item[5]=today's return

        for i in list_p:
                
            if (float(i[2]) > 0): 
                grand_total_gains += i[1]
            if (float(i[5] > 0)):
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


        if self.ui.ledit_Iteration.text() == "" or self.ui.ledit_Iteration.text() == "0":
            msg = QMessageBox.warning(self,"Iteration","Must enter a number of iterations to sell",QMessageBox.StandardButton.Ok)
            if msg == QMessageBox.StandardButton.Ok:
                return False,lst
        else:
            txtIter = self.ui.ledit_Iteration.text()
            check_one = True
        
        if self.ui.cmbAction.currentText() == "sell_gains_x" or \
            self.ui.cmbAction.currentText() == "sell_selected" or \
            self.ui.cmbAction.currentText() == "sell_todays_return_x" or \
            self.ui.cmbAction.currentText() == "raise_x_sell_y_dollars_except_z" or \
            self.ui.cmbAction.currentText() == "sell_gains_except_x" or \
            self.ui.cmbAction.currentText() == "sell_todays_return_except_x" or \
            self.ui.cmbAction.currentText() == "sell_gains_x_except_z":



            if len(self.ui.lstAssets.selectedItems()) == 0:
                msg = QMessageBox.warning(self,"Selection","Must select at least 1 item from the Asset list.",QMessageBox.StandardButton.Ok)
                if msg == QMessageBox.StandardButton.Ok:
                    return False,lst
            else:
                lst = self.ui.lstAssets.selectedItems()
                check_two = True
        else:
            lst = ['dont care']
            check_two = True

        if check_one and check_two:
            return txtIter,lst
        else:
            return False,lst

#----------------------------------------------------------------------------------------------------------------------------------
# sell__selected
# -------------------------------------------------------------------------------------------------------------------------------------        
    def sell_selected(self, n,acc_num,lst,raise_amount,dollar_value_to_sell,progress_callback):
    #Item 0 =  tickers
        #Item 1 = Total_return
        #Item 2 = stock_quantity_to_sell/buy
        #Item 3 = last price
        #item[4]= your quantities
        #item[5]=today's return

        stock_symbols = []
        tgains_actual = 0.0 
        
        tickersPerf = self.get_stocks_from_portfolio(acc_num)
        
        
        n_tickersPerf = self.find_and_remove(tickersPerf, lst,1)
        sorderd_lst = sorted(n_tickersPerf,key=lambda x: x[0])
        progress_callback.emit(f"Sell Selected: Total gains = ${dollar_value_to_sell}") 

        file_sell_write = open("stocks_sell.csv","w")
        for index in range(int(n)):
            progress_callback.emit(f"Iteration{index+1}")
            stock_symbols = []
            #sell stocks if quantity_to_sell > 0 
            for item in sorderd_lst:
#
                frm_quantity = "{0:.2f}".format(float(dollar_value_to_sell))
                # stock_quantity_to_sell and (your quantity > stock_quantity_to_sell)
                if float(item[4]) > frm_quantity :
                    sell_info = r.order_sell_market(symbol=item[0],quantity=frm_quantity,timeInForce='gfd')
                    time.sleep(5)

                    # while sell_info['id'] is not None:
                    #     time.sleep(5)
                    #     stock_order = r.get_stock_order_info(orderID=sell_info['id'])

                    
                    #Item 0 =  tickers     #Item 2 = stock_quantity_to_sell  #Item 3 = last price
                    stock_symbols.append(f"{item[0]}:{frm_quantity}:{item[3]}")
                    tot = "{0:.2f}".format(frm_quantity*float(item[3]))
                    tgains_actual += float(tot)

                    last_price = "{0:.2f}".format(float(item[3]))
                    progress_callback.emit(f"{frm_quantity} of {item[0]} shares sold at market price - ${last_price} - Total: ${tot}")
               
             
        
        stocks_format = ",".join(stock_symbols)
        file_sell_write.write(stocks_format)
            
            

        file_sell_write.close()
        progress_callback.emit(f"Operation Done! - Total=${tgains_actual}")
        
        return
#----------------------------------------------------------------------------------------------------------------------
#  sell_gains
# -------------------------------------------------------------------------------------------------------------------------      
    def sell_gains(self, n,acc_num,lst,raise_amount,dollar_value_to_sell,progress_callback):
        
        stock_symbols = []
        tgains_actual = 0.0
        

        #calc total gains
        tickersPerf = self.get_stocks_from_portfolio(acc_num)

        grand_total_gains,today_gains = self.cal_total_gains(tickersPerf)
      
        inse = "{0:.2f}".format(float(grand_total_gains))
           
          
        sorderd_lst = sorted(tickersPerf,key=lambda x: x[0])
          
            
                #Item 0 =  tickers
                #Item 1 = Total_return
                #Item 2 = stock_quantity_to_sell/buy
                #Item 3 = last price
                #item[4]= your quantities
                #item[5]=today's return
        progress_callback.emit(f"Total gains = ${inse}")
        file_sell_write = open("stocks_sell.csv","w")
        for index in range(int(n)):
            stock_symbols = []    
            
            progress_callback.emit(f"Iteration: {index+1}")
            
            
          
            #sell stocks if quantity_to_sell > 0 
            for item in sorderd_lst: #
                frm_quantity = "{0:.2f}".format(float(item[2]))

            # stock_quantity_to_sell and (your quantity > stock_quantity_to_sell)
                if not (float(item[2]) <= 0) and (float(item[2]) >= 0.01) and (float(item[4]) > float(item[2])) :
                    sell_info = r.order_sell_market(symbol=item[0],quantity="{0:.2f}".format(float(item[2])),timeInForce='gfd')
                    time.sleep(5)
                    
                    #Item 0 =  tickers     #Item 2 = stock_quantity_to_sell  #Item 3 = last price
                    stock_symbols.append(f"{item[0]}:{item[2]}:{item[3]}")
                    tot = "{0:.2f}".format(float(item[2])*float(item[3]))
                    tgains_actual += float(tot)

                    last_price = "{0:.2f}".format(float(item[3]))
                    progress_callback.emit(f"{frm_quantity} of {item[0]} shares sold at market price - ${last_price} - Total: ${tot}")
                    
        
            
            stocks_format = ",".join(stock_symbols)
            file_sell_write.write(stocks_format)
            
            

        file_sell_write.close()
        progress_callback.emit(f"Operation Done! - Total=${tgains_actual}")
        
        return
                
                
#----------------------------------------------------------------------------------------------------------------------------------
# sell_gains_x exclude a list of stocks
# -------------------------------------------------------------------------------------------------------------------------------------        
    def sell_gains_except_x(self,n,acc_num,excludeList,raise_amount,dollar_value_to_sell,progress_callback):
        #Item 0 =  tickers
        #Item 1 = Total_return
        #Item 2 = stock_quantity_to_sell/buy
        #Item 3 = last price
        #item[4]= your quantities
        #item[5]=today's return}
    
        minus_gains = 0.0
        minus_tgains = 0.0
            
         
        stock_symbols = []
        tgains_actual = 0.0
                
                #exclude the tickets in excludeList
        tickersPerf = self.get_stocks_from_portfolio(acc_num)
        
        grand_total_gains,tgains = self.cal_total_gains(tickersPerf)
            
        g2 = grand_total_gains * int(n) 
        n_tickersPerf = self.find_and_remove(tickersPerf, excludeList)
        sorderd_lst = sorted(n_tickersPerf,key=lambda x: x[0])
        for item in n_tickersPerf:
            if item[1] >= 0.0:    
                minus_gains += item[1]
            if item[5] >= 0.0:    
                minus_tgains += item[5]

        tgains = g2 - (minus_gains * int(n) )
                
            
          
            
          
        progress_callback.emit(f"Sell Gains: Total gains ~ ${tgains} exclude = {excludeList}")
        
        file_sell_write = open(f"stocks_sell.csv","w")  
        for index in range(int(n)):
            progress_callback.emit(f"Iteration{index+1}")
            stock_symbols = []

            
                #sell stocks if quantity_to_sell > 0 
            for item in sorderd_lst: #
                frm_quantity = "{0:.2f}".format(float(item[2]))
                # stock_quantity_to_sell and (your quantity > stock_quantity_to_sell)
                if not (float(item[2]) <= 0) and (float(item[2]) >= 0.01) and (float(item[4]) > float(item[2])) :
                    sell_info = r.order_sell_market(symbol=item[0],quantity="{0:.2f}".format(float(item[2])),timeInForce='gfd')
                    time.sleep(5)
                                             
                        #Item 0 =  tickers     #Item 2 = stock_quantity_to_sell  #Item 3 = last price
                    stock_symbols.append(f"{item[0]}:{item[2]}:{item[3]}")
                    tot = "{0:.2f}".format(float(item[2])*float(item[3]))
                    tgains_actual += float(tot)

                    last_price = "{0:.2f}".format(float(item[3]))
                    progress_callback.emit(f"{frm_quantity} of {item[0]} shares sold at market price - ${last_price} - Total: ${tot}")

                
            stocks_format = ",".join(stock_symbols)
            file_sell_write.write(stocks_format)
                
            
                  
        file_sell_write.close()
        tgains_actual= "{0:.2f}".format(tgains_actual)
        progress_callback.emit(f"Operation Done! - Total=${tgains_actual}")

    

            
#----------------------------------------------------------------------------------------------------------------------------------
# sell__todays_return
# -------------------------------------------------------------------------------------------------------------------------------------        
    def sell_todays_return(self, n,acc_num,lst,raise_amount,dollar_value_to_sell,progress_callback):
          #Item 0 =  tickers
                    #Item 1 = Total_return
                    #Item 2 = stock_quantity_to_sell/buy
                    #Item 3 = last price
                    #item[4]= your quantities
                    #item[5]=today's return


    
        stock_symbols = []
        tgains_actual = 0.0 

        
        tickersPerf = self.get_stocks_from_portfolio(acc_num)
        
        sorderd_lst = sorted(tickersPerf,key=lambda x: x[0])
        grand_total_gains,tgains = self.cal_total_gains(tickersPerf)
            
        g2 = grand_total_gains * int(n) 
         
        progress_callback.emit(f"Sell Todays Return: Total gains = ${tgains}") 

        file_sell_write = open("stocks_sell.csv","w")
        for index in range(int(n)):
            progress_callback.emit(f"Iteration{index+1}")
            stock_symbols = []
            #sell stocks if quantity_to_sell > 0 
            for item in sorderd_lst: #
                #cal how much to sell for today's gains
                amount_to_sell = float(item[5]) / float(item[3])
                frm_amount_to_sell = "{0:.2f}".format(amount_to_sell)

            # stock_quantity_to_sell and (your quantity > stock_quantity_to_sell) and todays_return >= 0
                if not (float(item[5]) <= 0.1) and (float(item[4]) > amount_to_sell) :
                    sell_info = r.order_sell_market(symbol=item[0],quantity=frm_amount_to_sell,timeInForce='gfd')
                    time.sleep(5)
                    
               
                    #Item 0 =  tickers     #Item 2 = stock_quantity_to_sell  #Item 3 = last price
                    stock_symbols.append(f"{item[0]}:{frm_amount_to_sell}:{item[3]}")
                    tot = "{0:.2f}".format(float(item[2])*float(item[3]))
                    tgains_actual += float(tot)

                    last_price = "{0:.2f}".format(float(item[3]))
                    progress_callback.emit(f"{frm_amount_to_sell} of {item[0]} shares sold at market price - ${last_price} - Total: ${tot}")

            
        stocks_format = ",".join(stock_symbols)
        file_sell_write.write(stocks_format)
        
        file_sell_write.close() 
           
        
        progress_callback.emit(f"Operation Done! - Total=${tgains_actual}")
                                
#---------------------------------------------------------------------------------------------------------------------------
# Sell_todays_return_x (exclude list)
#---------------------------------------------------------------------------------------------------------------------------------
    def sell_todays_return_except_x(self,n,acc_num,lst,raise_amount,dollar_value_to_sell,progress_callback):
                      #Item 0 =  tickers
                    #Item 1 = Total_return
                    #Item 2 = stock_quantity_to_sell/buy
                    #Item 3 = last price
                    #item[4]= your quantities
                    #item[5]=today's return

        excludeList = []
        stock_symbols = []
        minus_gains = 0.0
        minus_tgains = 0.0
        tgains_actual = 0.0
              
      
        tickersPerf = self.get_stocks_from_portfolio(acc_num)
        grand_total_gains,tgains = self.cal_total_gains(tickersPerf)
        
        g2 = grand_total_gains * int(n)
            
            #exclude the tickets in excludeList
        
            
        n_tickersPerf = self.find_and_remove(tickersPerf, excludeList)
          
        sorderd_lst = sorted(n_tickersPerf,key=lambda x: x[0])
        for item in n_tickersPerf:
            if item[1] >= 0.0:    
                minus_gains += item[1]
            if item[5] >= 0.0:    
                minus_tgains += item[5]
        
        tgains = g2 - (self.minus_tgains * int(n)) 
            
        
        
                                    
                                    
        
        
        file_sell_write = open(f"stocks_sell.csv","w")
        progress_callback.emit(f"Sell Today's Return: ~ ${tgains}, exclude = {excludeList}")
        for index in range(int(n)):
            print(f"Iteration{index+1}")
            stock_symbols = []

            #sell stocks if quantity_to_sell > 0 
            for item in sorderd_lst: #
                #cal how much to sell for today's gains
                amount_to_sell = float(item[5]) / float(item[3])
                frm_amount_to_sell = "{0:.2f}".format(amount_to_sell)

            # stock_quantity_to_sell and (your quantity > stock_quantity_to_sell) and todays_return >= 0
                if not (float(item[5]) <= 0.1) and (float(item[4]) > amount_to_sell) :
                    sell_info = r.order_sell_market(symbol=item[0],quantity=frm_amount_to_sell,timeInForce='gfd')
                    time.sleep(5)
                    
                

                        
                    #Item 0 =  tickers     #Item 2 = stock_quantity_to_sell  #Item 3 = last price
                    stock_symbols.append(f"{item[0]}:{frm_amount_to_sell}:{item[3]}")
                    tot = "{0:.2f}".format(float(item[2])*float(item[3]))
                    tgains_actual += float(tot)

                    last_price = "{0:.2f}".format(float(item[3]))
                    progress_callback.emit(f"{frm_amount_to_sell} of {item[0]} shares sold at market price - ${last_price} - Total: ${tot}")


            
            stocks_format = ",".join(self.stock_symbols)
            file_sell_write.write(stocks_format)
        
        file_sell_write.close()
        stock_symbols = []    
        
        progress_callback.emit(f"Operation Done! - Total=${tgains_actual}")
                
#---------------------------------------------------------------------------------------------------------------------------
# raise x (dollars) by selling y dollars of each stock
#---------------------------------------------------------------------------------------------------------------------------------
    def raise_x_sell_y_dollars(self, n,acc_num,lst,raise_amount,dollar_value_to_sell,progress_callback):
      
        sell_list = []
        found  = False
        stock_symbols = []

        tickersPerf = self.get_stocks_from_portfolio(acc_num)
        grand_total_gains,tgains = self.cal_total_gains(tickersPerf)
        
        g2 = grand_total_gains * int(n)
        f_g2 = "{0:.2f}".format(g2)    

            #exclude the tickets in excludeList
        
            
        #n_tickersPerf = self.find_and_remove(tickersPerf, excludeList)
          
        sorderd_lst = sorted(tickersPerf,key=lambda x: x[0])
        
        
        
        accu_quantity_to_buy = 0.0
        raised_amount = 0.0
        n_raise_amount = float(raise_amount)
        n_dollar_value_to_sell = float(dollar_value_to_sell)

        index = 0
        tgains_actual = 0.0
        progress_callback.emit(f"Raise ${n_raise_amount} by selling ${n_dollar_value_to_sell} dollars of each stock: Total gains = ${n_raise_amount}")
        while not (raised_amount >= n_raise_amount):

            for item in sorderd_lst:
                #Item 0 =  tickers
                #Item 1 = Total_return
                #Item 2 = stock_quantity_to_sell/buy
                #Item 3 = last price
                #item[4]= your quantities
                #item[5]=today's return

                if raised_amount >= n_raise_amount:
                    break    

                quantity_to_sell = n_dollar_value_to_sell / float(item[3])     
                strquantity_to_sell = "{0:.2f}".format(quantity_to_sell)
                    

                
                for i,value  in enumerate(sell_list): #check if already in list and return index
                    #if found in list and you have enough shares to sell #+1 share = leftover
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
             # Item[0] = stock_name
            # Item[1] = quantity to sell
            # Item[2] = last price        
            frm_quantity = float(item[1])
            frm_quantity += 0.02
            str_quantity = str(frm_quantity)

            sell_info = r.order_sell_market(symbol=item[0],quantity=item[1],timeInForce='gfd')
            time.sleep(5)
            #stock_order = r.get_stock_order_info(orderID=buy_info['id'])
            stock_symbols.append("{0}:{1}:{2}".format(item[0],item[1],str_quantity) ) 
            tot = "{0:.2f}".format(float(item[1])*float(item[2]))
            tgains_actual += float(tot)

            last_price = "{0:.2f}".format(float(item[2]))
    
            
            progress_callback.emit(f"{n_dollar_value_to_sell} dollars of {item[0]} sold at market price ${last_price} - Total: ${tot}")
            
           
                    
            
    
    
        file_sell_write = open("stocks_sell.csv","w")
        stocks_format = ",".join(stock_symbols)
        file_sell_write.write(stocks_format)
        file_sell_write.close()
        stock_symbols = []   

        progress_callback.emit(f"Operation Done! - Total=${tgains_actual}")
    
#---------------------------------------------------------------------------------------------------------------------------
# raise x (dollars) by selling y dollars of each stock except [exclude list]
#---------------------------------------------------------------------------------------------------------------------------------
    def raise_x_sell_y_dollars_except_z(self,n,acc_num,excludeList,raise_amount,dollar_value_to_sell,progress_callback):
      
        sell_list = []
        found  = False
        stock_symbols = []

        tickersPerf = self.get_stocks_from_portfolio(acc_num)
        grand_total_gains,tgains = self.cal_total_gains(tickersPerf)
        
        g2 = grand_total_gains * int(n)
        f_g2 = "{0:.2f}".format(g2)
            #exclude the tickets in excludeList
        
            
        n_tickersPerf = self.find_and_remove(tickersPerf, excludeList)
          
        sorderd_lst = sorted(n_tickersPerf,key=lambda x: x[0])
        
        accu_quantity_to_buy = 0.0
        raised_amount = 0.0
        n_raise_amount = float(raise_amount)
        n_dollar_value_to_sell = float(dollar_value_to_sell)

        index = 0
        tgains_actual = 0.0
        progress_callback.emit(f"Raise {n_raise_amount} by selling ${n_dollar_value_to_sell} of each stock exclude = {excludeList}: Total gains = ${f_g2} ")
        while not (raised_amount >= n_raise_amount):
            #loop through the list of tickers and build a new list(sell_list) of quantities to sell
            for item in sorderd_lst:
                #Item[0] =  tickers
                #Item[1] = Total_return
                #Item[2] = stock_quantity_to_sell/buy
                #Item[3] = last price
                #item[4]= your quantities
                #item[5]=today's return

                if raised_amount >= n_raise_amount:
                    break    

                quantity_to_sell = n_dollar_value_to_sell / float(item[3])     
                strquantity_to_sell = "{0:.2f}".format(quantity_to_sell)
                
                                       
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
              # Item[0] = stock_name
            # Item[1] = quantity to sell
            # Item[2] = last price    
            frm_quantity = float(item[2])
            frm_quantity += 0.02
            str_quantity = str(frm_quantity)

            sell_info = r.order_sell_market(symbol=item[0],quantity=item[1],timeInForce='gfd')
            time.sleep(5)
            
            stock_symbols.append("{0}:{1}:{2}".format(item[0],item[1],str_quantity) ) 
            tot = "{0:.2f}".format(float(item[1])*float(item[2]))
            tgains_actual += float(tot)

            last_price = "{0:.2f}".format(float(item[2]))
    
            
            progress_callback.emit(f"{n_dollar_value_to_sell} dollars of {item[0]} sold at market price ${last_price} - Total: ${tot} ", )  
            
          
                    
            
    
    
        file_sell_write = open("stocks_sell.csv","w")
        stocks_format = ",".join(stock_symbols)
        file_sell_write.write(stocks_format)
        file_sell_write.close()
        stock_symbols = []  

        progress_callback.emit(f"Operation Done! - Total=${tgains_actual}")

    # end of class MainWIndow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    
    sys.exit(app.exec())
