Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = "C:\Users\mikem\Desktop\JARVIS"
sh.Run "pythonw ""C:\Users\mikem\Desktop\JARVIS\server.py""", 0, False
