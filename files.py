
from . import _
from Tools.LoadPixmap import LoadPixmap

from Screens.LocationBox import LocationBox
from Tools.Directories import *
from Components.config import *
from Components.ActionMap import NumberActionMap
from Components.Label import Label
from Components.Sources.List import List
from Components.Pixmap import Pixmap
from Components.AVSwitch import AVSwitch
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from enigma import getDesktop
from enigma import ePicLoad
from Components.config import ConfigLocations

from os import path as os_path, listdir, remove
from Tools.Directories import copyfile
try:
	from enigma import eMediaDatabase
	DPKG = True
except:
	DPKG = False
plugin="PictureCenterFS"
plugin_path = "/usr/lib/enigma2/python/Plugins/Extensions/PictureCenterFS"
DWide = getDesktop(0).size().width()
size_w = getDesktop(0).size().width()
if size_w < 730:
	skin_zusatz="SD/"
elif size_w > 1850:
	skin_zusatz="fHD/"
else:
	skin_zusatz="HD/"



class PictureCenterFS7_Filemenu(Screen):
	skindatei = plugin_path+"/skin/"+skin_zusatz+ "pcFS_menulist.xml"
	tmpskin = open(skindatei)
	skin = tmpskin.read()
	tmpskin.close()

	def __init__(self, session, file1,file2="",akti=None):
		self.file1=file1
		self.file2=file2
		self.edit=0
		self.akti=akti
		Screen.__init__(self, session)
		self.skinName = "PictureCenterFS7_Filemenu"
		self.session = session
		self.settigspath = ""
		mlist = []
		template="default"
		pics = ["nix", "red","green","yellow","blue","rec","epg","bouquet","exit","info","down","up","left","right","9","7","4","2","5","ok","stop","back","for"]
		pics[0] = LoadPixmap(plugin_path+"/skin/pictures/nix.png")
		if skin_zusatz !="SD/":
			template="with_numpic"
			for i in range(1,len(pics)):
				if os_path.exists(resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/buttons/key_" + pics[i] + ".png")):
					pics[i] = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/buttons/key_" + pics[i] + ".png"))
				elif os_path.exists(resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/buttons/" + pics[i] + ".png")):
					pics[i] = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/buttons/" + pics[i] + ".png"))
				else:
					pics[i] = pics[0]

		mlist.append((_('Copy selected/displayed file'), 'copy',pics[0]))
		if len(self.file2)>0:
			mlist.append((_('save changes in the original image'), 'save_rotat',pics[0]))
			self.setTitle(plugin+": "+_("Options for edited image"))
		else:
			mlist.append((_('Move selected/displayed file'), 'move',pics[0]))
			mlist.append((_('Delete selected/displayed file'), 'delete',pics[0]))
		if akti:
			mlist.append((" ", "",pics[0]))
			mlist.append((" "+_("Back to Startscreen"), 'cancel',pics[8]))
			mlist.append((" "+_("Show/Hide Text"), 'red',pics[1]))
			mlist.append((" "+_("Pause / Resume Slideshow"), 'green',pics[2]))
			mlist.append((" "+_("toggle Slideshow random/sorted"), 'yellow',pics[3]))
			if akti==1:
				mlist.append((" "+_("Show Exif-Data"), 'info',pics[6]))
				mlist.append((" "+_("Zoom"), 'blue',pics[4]))
				mlist.append((" "+_("Start Zoom"), 'ok',pics[19]))
				mlist.append((" "+_("Zoom range Up"), 'up',pics[11]))
				mlist.append((" "+_("Zoom range Down"), 'down',pics[10]))
				mlist.append((" "+_("reduced zoom range"), 'Back',pics[21]))
				mlist.append((" "+_("increased zoom range"), 'For',pics[22]))
				mlist.append((" "+_("Rotate 90->"), '9',pics[14]))
				mlist.append((" "+_("Rotate <-90"), '7',pics[15]))
				mlist.append((" "+_("Flip image horizontally"), '4',pics[16]))
				mlist.append((" "+_("Flip image vertically"), '2',pics[17]))
				mlist.append((" "+_("Image manipulation undo"), '5',pics[18]))
			mlist.append((" "+_("Next Picture or zoom range right"), 'right',pics[13]))
			mlist.append((" "+_("Prev. Picture or zoom range left"), 'left',pics[12]))
			mlist.append((" "+_("Stop Slideshow"), 'stop',pics[20]))
			mlist.append((" "+_("Add to marked list"), 'record',pics[5]))
			mlist.append((" "+_("Slide-time faster"), 'nextBouquet',pics[7]))
			mlist.append((" "+_("Slide-time slower"), 'prevBouquet',pics[7]))
		
		self.m_liste=mlist
		self["m_liste"] = List(mlist)
		self["m_liste"].style = template
		if skin_zusatz !="SD/":
			self["thumb"]=Pixmap()
			self.picload = ePicLoad()
			if DPKG:
				self.picload_conn = self.picload.PictureData.connect(self.showPic)
			else:
				self.picload.PictureData.get().append(self.showPic)
		self.setTitle(plugin+": "+_("Options for selected/displayed file"))
		self["actions"] = NumberActionMap(["OkCancelActions", "ColorActions", "InputActions","DirectionActions"],
		{
			"ok": self.run,
			"cancel": self.exit,
		}, -1)
		if skin_zusatz !="SD/":
			self.onLayoutFinish.append(self.show_pic)

	def show_pic(self):
		if skin_zusatz !="SD/":
			sc = AVSwitch().getFramebufferScale()
			self.picload.setPara((self["thumb"].instance.size().width(), self["thumb"].instance.size().height(), sc[0], sc[1], False, 1, '#000000'))
			
			if self.akti==2:
				pic=plugin_path+"/skin/pictures/mov.jpg"
			elif self.file2 and len(self.file2):
				pic=self.file2
			else:
				pic=self.file1
			self.picload.startDecode(pic)

	def showPic(self, picInfo=""):
		if skin_zusatz !="SD/":
			ptr = self.picload.getData()
			if ptr != None:
				self["thumb"].instance.setPixmap(ptr)


	def keyNumberGlobal(self, number):
		self["m_liste"].setIndex(number-1)
		self.run()

	def run(self):
		ind=self["m_liste"].getIndex()
		returnValue = self.m_liste[ind][1]
		if returnValue == 'delete':
				self.del_file()
		elif returnValue == 'copy':
				self.copy()
		elif returnValue == 'move':
			self.move()
		elif returnValue == 'save_rotat':
			self.save_rotat()
		else:
		    self.close(returnValue)



#bearbeiten ############################################

	def save_rotat(self): 
		text1=_("selceted File is:")+"\n"+self.file1+"\n\n"
		self.session.openWithCallback(self.save_rotat2,MessageBox,_(text1+_("Do you really overwrite this file?")) ,MessageBox.TYPE_YESNO)

	def save_rotat2(self,args=None):
		if args:
			source=self.file2 
			target= self.file1
			try:
				ret = copyfile(source, target)
				self.session.openWithCallback(self.exit,MessageBox,(self.file1+"\n"+_("file successfully saved")) ,MessageBox.TYPE_INFO)
			except OSError as e:
				txt= 'error: \n%s' % e
				self.session.openWithCallback(self.exit,MessageBox,txt ,MessageBox.TYPE_INFO) 

	def copy(self):
		if len(self.file2)<=0: self.file2=self.file1
		self.endung = "." + os_path.basename(self.file1).split(".")[-1]
		text1=os_path.basename(self.file1).replace("."+os_path.basename(self.file1).split(".")[-1],"")
		self.session.openWithCallback(self.copy2,VirtualKeyBoard,title = _("Edit file-save-name:"), text=text1)

	def copy2(self,filename):
		if filename:
			self.oldpath=os_path.dirname(self.file1)+"/"
			self.filename=filename+self.endung
		else:
			self.filename= os_path.basename(self.file1)
		self.session.openWithCallback(self.callCopy,dirSelect,_("Please select target path..."),os_path.split(os_path.dirname(self.file1))[0]+"/",os_path.getsize(self.file1))

	def callCopy(self, path):
		if path is not None:
			self.copy_source=self.file2
			self.copy_target= path + self.filename
			if pathExists(path +  self.filename):
				self.session.openWithCallback(self.callCopy2,MessageBox,_("file exist on this path, overwrite?") ,MessageBox.TYPE_YESNO)
			else:
				self.callCopy2(1)

	def callCopy2(self, answer):
		if answer:
			try:
				ret = copyfile(self.copy_source, self.copy_target)
				self.session.openWithCallback(self.exit,MessageBox,(self.file1+"\n"+_("file successfully copied at")+"\n"+self.filename) ,MessageBox.TYPE_INFO)
			except OSError as e:
				txt= 'error: \n%s' % e
			self.session.openWithCallback(self.exit,MessageBox,txt ,MessageBox.TYPE_INFO) 

	def move(self):
		self.session.openWithCallback(self.callmove,dirSelect,_("Please select target path..."),"","/tmp/")

	def del_file(self): 
		text1=_("selceted File is:")+"\n"+self.file1+"\n\n"
		self.session.openWithCallback(self.del_file_ok,MessageBox,_(text1+_("Do you really want to delete this file?")) ,MessageBox.TYPE_YESNO)

	def del_file_ok(self,answer):
		if answer:
			try:
				remove(self.file1)
				self.edit=1
				self.session.openWithCallback(self.exit,MessageBox,(self.file1+"\n"+_("file is deleted")) ,MessageBox.TYPE_INFO)
			except OSError as e:
				txt= 'error: \n%s' % e
				self.session.openWithCallback(self.exit,MessageBox,txt ,MessageBox.TYPE_INFO)

	def callmove(self, path):
		if path is not None:
			source=self.file1
			target= path +  os_path.basename(self.file1)    
			try:
				ret = copyfile(source, target)
				self.del_file_ok("ok")
				self.edit=1
				self.session.openWithCallback(self.exit,MessageBox,(self.file1+"\n"+_("file successfully moved")) ,MessageBox.TYPE_INFO)
			except OSError as e:
				txt= 'error: \n%s' % e
				self.session.openWithCallback(self.exit,MessageBox,txt ,MessageBox.TYPE_INFO)

	def exit(self,args=None):
		if args:
			self.close(1)
		else:
			self.close()

class save_mark:
	def __init__(self,session,name):
		ret = copyfile("/tmp/pcfs_mark", "/etc/ConfFS/"+name)

class backup:

	def __init__(self,session):
		self.session = session
		self.settigspath = None
		self.num=None
		self.file1=None

	def start(self,num=None):
		if num:   
			self.num=num
		if self.num==5:
			self.restore()
		elif self.num==3:
			self.backup()

	def backup(self):
		self.session.openWithCallback(self.callBackup,dirSelect,_("select target directory for backup"), "")

	def callBackup(self, path):
		if self.num and path is not None:
			if pathExists(path):
				if self.num==3:
					self.settigspath = path + "ConfFS_backup.tar.gz"
				if fileExists(self.settigspath):
					self.session.openWithCallback(self.callOverwriteBackup, MessageBox,_("Overwrite existing Backup?"),type = MessageBox.TYPE_YESNO,)
				else:
					self.callOverwriteBackup(True)
			else:
				self.err(_("Backup failed"))
				self.session.open(MessageBox,_("Directory %s nonexistent.") % (path),type = MessageBox.TYPE_ERROR,timeout = 5)
		else:
			self.err(_("Backup failed"))

	def callOverwriteBackup(self, res):
		if res:
			self.cBackup()

	def cBackup(self,num=None):
		if num:self.num=num
		if self.num and self.settigspath:
			mpath="/etc/ConfFS/"
			if pathExists(mpath) is True:
				files = []
				for file in listdir(mpath):
					files.append("/etc/ConfFS/"+file)
				tarFiles = ""
				for arg in files:
					tarFiles += "%s " % arg
			try:
				com = "tar czvf %s %s" % (self.settigspath,tarFiles)
				self.session.open(Console,_("Backup Settings..."),[com])
			except:
				self.err(_("backup failed"))

	def restore(self):
		if self.num==5:
			self.tarfile="ConfFS_backup.tar.gz"
			self.session.openWithCallback(self.callRestore,dirSelect,_("select directory with the backup"),"")

	def callRestore(self, path1):
		if self.tarfile and path1:
			self.settigspath = path1 + self.tarfile
			if fileExists(self.settigspath):
				self.session.openWithCallback(self.callOverwriteSettings, MessageBox,_("Overwrite existing Files?"),type = MessageBox.TYPE_YESNO,)
			else:
				self.session.open(MessageBox,_("File %s nonexistent.") % (path1),type = MessageBox.TYPE_ERROR,timeout = 5)
		else:
			self.err("restore failed")

	def callOverwriteSettings(self,res=None):
		if res:
			try:
				com = "cd /; tar xzvf %s" % (self.settigspath)
				self.session.open(Console,_("Restore Settings..."),[com])
			except:
				self.err(_("restore failed"))

	def err(self, res):
		pass

class dirSelect(LocationBox):
	def __init__(self, session, text, dir="/", minFree = None):
		if not dir or (dir and (dir=="" or not os_path.exists(dir))):dir="/"
		inhibitDirs = ["/bin", "/boot", "/dev", "/lib", "/proc", "/sbin", "/sys", "/usr", "/var"]
		LocationBox.__init__(self, session, text = text, currDir = dir, inhibitDirs = inhibitDirs, minFree = minFree)
		self.skinName = "LocationBox"
