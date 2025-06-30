# utils.py

# # app_context.py
main_window = None

def global_function():
    print("This function is available everywhere!")

def do_magic():
    main_window.updateStatusBar("Boom!")

def setStatusBar(msg):
    main_window.updateStatusBar(msg)