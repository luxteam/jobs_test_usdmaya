import platform

if platform.system() == "Windows":
    import win32gui
    import win32con


def close_maya_window():
    if platform.system() == "Windows":
        window = win32gui.FindWindow(None, "maya")

        while window != 0:
            win32gui.PostMessage(window, win32con.WM_CLOSE, 0, 0)
            
            window = win32gui.FindWindow(None, "maya")
