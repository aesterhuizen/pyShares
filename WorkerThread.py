import sys, traceback
from threading import Thread,Event

#A thread that Updates/Monitors the status of a command
# This is a simple thread that can be used to run a function in the background
class UpdateThread(Thread):
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
        finally:
            {}

      
    def stop(self):
        self.stop_event.set()


#A Thread that is used to run a command in the background

class CommandThread(Thread):
    def __init__(self,fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.stop_event = Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        
        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            #self.signals.error.emit((exctype, value, traceback.format_exc()))
            print(f"Error: {e}")
        finally:
            {}
        

      
    
     
        
 
        