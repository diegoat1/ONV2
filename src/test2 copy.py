import win32com.client
import os

x1 = win32com.client.Dispatch("Excel.Application")
x1.Visible = False
x1.Workbooks.Open(r'D:\Users\Diego Toffaletti\Desktop\ONV2\src\StrenghtCreator.xlsm')
x1.Run("Solver")
x1.DisplayAlerts = False
x1.Application.Quit()
#del x1