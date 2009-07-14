class config:
   authorisedactions = {}
   format = {"disk":{},"network":{}}
   v = {}

import ConfigParser

x = ConfigParser.ConfigParser()
y = ConfigParser.ConfigParser()
x.read("blog.conf.defaults")
y.read("blog.conf")

for option in x.options("main"):
   try:
      config.v[option] = x.get("main",option,True)
      config.v[option] = y.get("main",option,True)
   except ConfigParser.NoOptionError, e:
      pass
   except ConfigParser.NoSectionError, e:
      pass
   config.v[option] = config.v[option].replace("%(__EMPTYCHAR__)","")

for format in x.options("network_formats"):
   try:
      config.format["network"][format] = x.get("network_formats",format,True)
      config.format["network"][format] = y.get("network_formats",format,True)
   except ConfigParser.NoOptionError, e:
      pass
   except ConfigParser.NoSectionError, e:
      pass
   config.format["network"][format] = config.format["network"][format].replace("%(__EMPTYCHAR__)","")

for access_control in x.options("authorisation"):
   who = ""
   try:
      who = x.get("authorisation",access_control,True)
      who = y.get("authorisation",access_control,True)
   except ConfigParser.NoOptionError, e:
      pass
   except ConfigParser.NoSectionError, e:
      pass
   config.authorisedactions[access_control] = who.split()

