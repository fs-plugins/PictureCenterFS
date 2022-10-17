# -*- coding: utf-8 -*-
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import gettext


def localeInit():
	gettext.bindtextdomain("PictureCenterFS", resolveFilename(SCOPE_PLUGINS, "Extensions/PictureCenterFS/locale"))


def _(txt):
	t = gettext.dgettext("PictureCenterFS", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t


localeInit()
language.addCallback(localeInit)
