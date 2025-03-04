from PyQt6.QtWidgets import QDialog, QDialogButtonBox, \
                            QFileDialog, QPushButton ,QLabel, QVBoxLayout, QHBoxLayout, QLineEdit

import os.path

class msgBoxGetCredentialFile(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Get Data File")

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
       
        file_name, _ = QFileDialog.getOpenFileName(None, "Open File", f"{os.path.curdir}", "Environment Files (*.env)", options=options)
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