import os
import sys
import socket
# for the GUI
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

# this doesn't work on non-windows systems
if sys.platform.startswith("win") != True:
	messagebox.showerror(message="This tool only works on Windows, as the hijacks it cleans are Windows-specific")
	sys.exit(1)
try:
	import ctypes
	def is_admin():
		try:
			return ctypes.windll.shell32.IsUserAnAdmin()
		except:
			return False
	if is_admin():
		pass
	else:
		# Re-run the program with admin rights
		ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
		sys.exit()
except Exception as err:
	messagebox.showerror(message=err)

g = {}
stypes = ["Scan for modified HOSTs file","Scan for disabled UAC","Scan for broken exe association"]

def scanHOSTs():
	try:
		hosts = open("C:\\Windows\\System32\\drivers\\etc\\hosts").read()
		lines = hosts.split("\n")
		totaldomains = 0
		for line in lines:
			if line.startswith("#") or line == "":
				continue
			try:
				domain = line.split(" ")[1]
				if domain != "" and domain != "localhost" and domain != socket.gethostname():
					totaldomains += 1
			except:
				# if it is not valid, just ignore it
				continue
		return totaldomains
	except:
		return 0

def isUACdisabled():
	try:
		import winreg
		keyname = "SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
		vn = "EnableLUA"
		k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,keyname)
		c = 6
		key_name, key_value, key_type = winreg.EnumValue(k,c)
		#print("Value: {}. Name: {}".format(key_value,key_name),keyname,"{}".format(c))
		if key_value == 0:
			return True
		else:
			return False
	except Exception as err:
		messagebox.showerror(message=err)
		# if something goes wrong, we want to return false
		return False

class scanner():
	def __init__(self):
		self.g = {}
		self.anyd = False
		self.res_names = {"HOSTs":"Modified hosts file","UAC":"Disabled UAC"}
		self.show_options()
	def scan(self):
		self.results = {}
		self.anyd = False
		#print(self.g["Scan for modified HOSTs file"].get(),self.g["Scan for disabled UAC"].get())
		if self.g["Scan for modified HOSTs file"].get() == "1":
			#print("Scanning HOSTs")
			self.results["HOSTs"] = scanHOSTs()
			if self.results["HOSTs"] != 0:
				self.anyd = True
		if self.g["Scan for disabled UAC"].get() == "1":
			#print("Scanning for disabled UAC")
			self.results["UAC"] = isUACdisabled()
			if self.results["UAC"] == True:
				self.anyd = True
		#print(self.results)	
		self.show_results()
	def show_options(self):
		self.anyd = False
		self.root = Tk()
		self.root.geometry("300x150")
		for i in stypes:
			self.g[i] = StringVar()
			check = ttk.Checkbutton(self.root, text=i, variable=self.g[i]).pack()
		button = ttk.Button(self.root, text='Scan', command=self.scan).pack()
		self.root.title("Scan options")
		self.root.mainloop()
	def show_results(self):
		#print(self.anyd)
		result = self.results
		self.root.destroy()
		self.root = Tk()
		self.root.geometry("300x150")
		self.threats = {}
		label = ttk.Label(self.root,text="Threats detected: ").pack()
		for i in self.results:
			if self.results[i] == False or self.results[i] == 0:
				continue
			self.threats[i] = StringVar()
			check = ttk.Checkbutton(self.root, text=self.res_names[i], variable=self.threats[i]).pack()
		if self.anyd == True:
			button = ttk.Button(self.root, text='Fix', command=self.fix).pack()
		else:
			label2 = ttk.Label(self.root,text="No threats detected").pack()
		button2 = ttk.Button(self.root, text='Rescan', command=self.scan).pack()
		self.root.title("Scan results")
		self.root.mainloop()
	def fix(self):
		self.root.destroy()
		#print(self.threats)
		try:
			try:
				if self.threats["UAC"].get() == "1":
					# there's got to be a better way
					import subprocess
					subprocess.run("C:\\Windows\\System32\\reg.exe ADD HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v EnableLUA /t REG_DWORD /d 1 /f",shell=True)
					if messagebox.askokcancel(message="Reboot to enable UAC? ") == True:
						subprocess.run("shutdown /r /c \"The System Hijack removal tool needs to reboot your computer\"",shell=True)
						sys.exit()
			except:
				pass
			try:
				if self.threats["HOSTs"].get() == "1":
					hosts = open("C:\\Windows\\System32\\drivers\\etc\\hosts").read()
					lines = hosts.split("\n")
					end = open("C:\\Windows\\System32\\drivers\\etc\\hosts","w")
					for line in lines:
						if line.startswith("#") or line == "":
							end.write(line + "\n")
							continue
						try:
							domain = line.split(" ")[1]
							if domain == "localhost" or domain == socket.gethostname():
								end.write(line + "\n")
						except:
							pass
					end.close()
			except:
				pass
		except Exception as err:
			messagebox.showerror(err)
		self.show_options()

main = scanner()