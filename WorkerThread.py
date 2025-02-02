from PyQt6.QtCore import QObject
import sys, traceback
from threading import Thread,Event

class WorkerThread(Thread):
    def __init__(self,fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.stop_event = Event()

    
    def run(self):
        
        # Retrieve args/kwargs here; and fire processing using them
        try:
            while not self.stop_event.is_set():
                result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            #self.signals.error.emit((exctype, value, traceback.format_exc()))
            print(f"Error: {e}")
        #else:
            #self.signals.result.emit(result)  # Return the result of the processing
        finally:
            #self.signals.finished.emit()  # Done
             print("Thread finished")
        #comment in app.py
    def stop(self):
        self.stop_event.set()
        
 
        