from . import _

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.InputBox import InputBox
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry,ConfigText,config,NoSave
from Components.ActionMap import NumberActionMap
from Components.Label import Label
from Screens.VirtualKeyBoard import VirtualKeyBoard
from enigma import eConsoleAppContainer, quitMainloop, eTimer,getDesktop
from Plugins.Plugin import PluginDescriptor
from Tools.Directories import copyfile,resolveFilename, SCOPE_PLUGINS, fileExists

import os,urllib

pyvers1=str(os.sys.version_info[0])
pyvers2=str(os.sys.version_info[1])
if pyvers1=="3":
	from configparser import ConfigParser
	from urllib.parse import urlencode
	from urllib.request import Request, urlopen
else:
	from ConfigParser import ConfigParser
	from urllib2 import urlopen,Request
	from urllib import urlencode
	import requests

configparser = ConfigParser()

if os.path.exists("/home/root/logs/"):
	debfile="/home/root/logs/camo3FSdebug.txt"
elif os.path.exists("/media/hdd/"):
	debfile="/media/hdd/camo3FSdebug.txt"
else:
	debfile="/tmp/camo3FSdebug.txt"
if not os.path.exists(debfile):
	deb=open(debfile,"w")
	deb.close()
if not os.path.exists('/etc/ConfFS/'):
	os.mkdir('/etc/ConfFS')
dat = '/etc/ConfFS/camo3FS.dat'
if not os.path.exists(dat):
	if os.path.exists('/etc/ConfFS/camoFS.dat'):
		ret = copyfile('/etc/ConfFS/camoFS.dat','/etc/ConfFS/camo3FS.dat')
	else:
		deb=open(dat,"w")
		deb.close()
DWide = getDesktop(0).size().width()

class camoinstall(Screen, ConfigListScreen):
	if DWide > 1300:
		skin =  """
		<screen position="center,center" size="900,520" title="camo3FS-Install">
			<widget name="config" position="10,10" size="880,120" scrollbarMode="showOnDemand" />
			<widget name="pyv" position="10,140" size="880,120" valign="center" halign="center" zPosition="2" foregroundColor="white" font="Regular;32" />
			<widget name="buttonred" position="10,460" size="200,60" backgroundColor="red" valign="center" halign="center" zPosition="2" foregroundColor="white" font="Regular;22" />
			<widget name="buttongreen" position="500,460" size="200,60" backgroundColor="green" valign="center" halign="center" zPosition="2" foregroundColor="white" font="Regular;22" />
			<widget name="running" position="10,250" size="880,200" valign="center" halign="center" zPosition="3" foregroundColor="white" font="Regular;32" />
		</screen>"""
	else:
		skin =  """
		<screen position="center,center" size="560,400" title="camo3FS-Install">
			<widget name="config" position="5,5" size="555,80" scrollbarMode="showOnDemand" />
			<widget name="pyv" position="5,90" size="555,80" valign="center" halign="center" zPosition="2" foregroundColor="white" font="Regular;24" />
			<widget name="buttonred" position="10,360" size="130,40" backgroundColor="red" valign="center" halign="center" zPosition="2" foregroundColor="white" font="Regular;18" />
			<widget name="buttongreen" position="218,360" size="200,40" backgroundColor="green" valign="center" halign="center" zPosition="2" foregroundColor="white" font="Regular;18" />
			<widget name="running" position="80,180" size="400,120" valign="center" halign="center" zPosition="3" foregroundColor="white" font="Regular;22" />
		</screen>"""

	def __init__(self, session):
		self.mid=""
		self.listb = []

		Screen.__init__(self, session)
		self.session = session
		self["buttonred"] = Label(_("Exit"))
		self["pyv"] = Label()
		self["running"] = Label(_("Installation tool for camo3FS")+"\n"+_("automatic detection of the required version")+"\n")
		self["buttongreen"] = Label(_("Start Install"))
		self["actions"] = NumberActionMap(["OkCancelActions", "ColorActions", "InputActions","DirectionActions"],
		{
			"ok": self.press_ok,
			"cancel": self.close,
			"red": self.close,
			"green": self.inst1,
		}, -1)

		try:
			configparser.read(dat)
			if configparser.has_section("settings") and configparser.has_option("settings","kid2"):
				self.mid= configparser.get("settings","kid2")
				if not self.mid.endswith("cmfs3"):
					self.mid=""
		except:
			pass
		ConfigListScreen.__init__(self, self.listb)
		self.s_id=NoSave(ConfigText(default = self.mid, fixed_size = False))
		self.s_mail=NoSave(ConfigText(default = "test@ftsets.de", fixed_size = False))
		self.listb.extend((
			getConfigListEntry(_("User-ID"), self.s_id),
			getConfigListEntry(_("EMail"), self.s_mail)
		))
		dummi=eTimer()
		self.ext="deb"
		self.fert=False
		if hasattr(dummi, 'callback'):
			self.ext="ipk"
		self["pyv"].setText("Python-Version: "+str(pyvers1)+"."+str(pyvers2)+"\n"+_("required")+": "+self.ext)
		self["config"].setList(self.listb)

	def press_ok(self):
		self.cur = self['config'].getCurrent()
		self.cur = self.cur and self.cur[1]
		if self.cur == self.s_id:
			self.session.openWithCallback(self.texteingabeFinished, VirtualKeyBoard, title=_('set User-ID'), text=self.s_id.value)
		elif self.cur == self.s_mail:
			self.session.openWithCallback(self.texteingabeFinished, VirtualKeyBoard, title=_('set Your E-Mail'), text=self.s_mail.value)

	def texteingabeFinished(self, ret):
		if ret is not None:
			self['config'].getCurrent()[1].value = ret

	def inst1(self):
		if self.fert==True:
			self.UpgradeReboot(True)
		else:
			self["running"].setText(_("start download and install\nplease be patient"))
			if self.s_id.value.strip() == "" or self.s_mail.value.strip() == "":
				self["pyv"].setText(_("User-ID and Email is necessary!"))
			else:
				self.inst2()

	def inst2(self):
		self["pyv"].setText(_("check for Version"))
		if self.mid != self.s_id.value:
			if configparser.has_section("settings") is False:
				configparser.add_section("settings")
			configparser.set("settings", "kid2", self.mid)
			fp = open(dat,"w")
			configparser.write(fp)
			fp.close()

		self.dlfile="x"
		lese=None
		read_dats=None
		deb=open(debfile, 'a')
		deb.write("iTool install camo3FS start, py "+ str(pyvers1)+"."+str(pyvers2)+"\n")
		param = {'kid':self.s_id.value.strip(),'anfrage':'install','pyvers1':pyvers1,'pyvers2':pyvers2,'mail':self.s_mail.value.strip(),'deb':self.ext}
		dta=urlencode(param).encode("utf-8")
		deb.write(str(param)+"\n")
		try:
			web1='https://www.fs-plugins.de/camo/dli'
			if str(pyvers1)=="2":
				request = Request(web1, dta)
				read_dats = urlopen(request, timeout=5).read()
			else:
				dta=urlencode(param).encode("utf-8")
				req =  Request(web1, data=dta)
				read_dats = urlopen(req).read().decode(errors='replace')
			if read_dats:
				lese=read_dats
			else:
				deb.write("iTool connect error 1\n")
				self["running"].setText(_("connection error")+" 1")
			if lese:
				self["pyv"].setText("")
				if lese.startswith("##"):
					deb.write(lese.replace("##","iTool ")+"\n")
					self["running"].setText(_("download failed"))
					self.session.open(MessageBox, lese.replace("##",""), type=MessageBox.TYPE_INFO)
				else:
					if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/camoFS"):
						self.session.open(MessageBox, _("please uninstall camoFS first!"), type=MessageBox.TYPE_INFO)
					else:
						self.dlfile="/tmp/enigma2-plugin-extensions-camo3fs."+self.ext
						deb.write("iTool load new file\n")
						if pyvers1=="2":
							response1 = requests.get(lese,timeout=5)
							if response1 and str(response1.status_code) =="200" :
								res = response1.content
								fh=open(self.dlfile,"wb")
								fh.write(str(res))
								fh.close()
								self.startPluginUpdate("w")
						else:
							req = Request(lese)
							dl=open(self.dlfile,"wb")
							dl.write(urlopen(req).read())
							dl.close()
							self.startPluginUpdate("w")

		except Exception as e:
			deb.write("iTool connection error: "+str(e)+"\n")
			self["running"].setText(_("download failed"))
			self.session.open(MessageBox, _("connection error")+" 2", type=MessageBox.TYPE_INFO)

		deb.close()

	def startPluginUpdate(self,t=""):
		self["buttongreen"].hide()
		self["running"].setText(_("start install"))
		if self.dlfile !="x" and fileExists(self.dlfile):
			try:
				self.updater = eConsoleAppContainer()
				if self.ext=="deb":
					self.updater.appClosed_conn = self.updater.appClosed.connect(self.finishedPluginUpdate)
					self.updater.execute("apt-get update ; dpkg --install --force-depends --force-overwrite %s ; apt-get -f install" % str(self.dlfile))
				else:
					self.updater.appClosed.append(self.finishedPluginUpdate)
					self.updater.execute("opkg install --force-overwrite --force-depends %s" % str(self.dlfile))

			except:
				self.download_error("programm error\n"+_("new file is downloaded in /tmp, please install self"))
		else:
			self.download_error("Temporarily no connection to the database is possible")


	def finishedPluginUpdate(self,retval):
		if int(retval) == 2:
			self.download_error(_("Please check free space on your root filesystem..\nCheck the update log carefully!\nThe GUI will restart now!"))
		else:
			deb=open(debfile, 'a')
			deb.write("iTool Install/Update: ")
			deb.write(str(retval)+"\n")
			deb.close()
			self.runUpgradeFinished()


	def download_error(self,txt=""):
		try:self.updater.kill()
		except: pass
		deb=open(debfile, 'a')
		deb.write("iTool install failed, download error\n")
		if txt != "":
			deb.write(str(txt)+"\n")
		deb.close()
		self.session.open(MessageBox, "camo3FS -"+_("Install failed!")+"\n"+txt, type=MessageBox.TYPE_INFO)

	def runUpgradeFinished(self):
		try:self.updater.kill()
		except:pass
		self.fert=True
		self["buttongreen"].show()
		if fileExists(self.dlfile):
			os.remove(self.dlfile)
		self["running"].setText(_("Installation finished.")+"\n"+_("Please restart GUI!"))
		self["buttongreen"].setText(_("GUI restart"))
		self.session.openWithCallback(self.UpgradeReboot, MessageBox, _("Installation finished.") +" "+_("Restart must be performed"), type=MessageBox.TYPE_YESNO)

	def UpgradeReboot(self, result):
		if result== True:
			quitMainloop(3)


def main(session, **kwargs):
	session.open(camoinstall)

def Plugins(**kwargs):
	return PluginDescriptor(name='camo3FS_install', description="install camo3FS", icon="camo3FS.png", where = PluginDescriptor.WHERE_PLUGINMENU, fnc=main)
