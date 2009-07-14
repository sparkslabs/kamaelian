#!/usr/bin/python

import htmltmpl
import os

files = [ os.path.join("templates",x) for x in os.listdir("templates") if
x[-5:] == ".html"]
tm = htmltmpl.TemplateManager()
for file in files:
   tm.prepare(file)

