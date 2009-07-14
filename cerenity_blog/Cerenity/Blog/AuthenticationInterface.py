#!/usr/bin/python
#

class AuthenticationInterface(object):
   #
   # ui:
   #    self.ui.username = self.ui.authenticator.check("name","pwd")
   #    self.ui.username is not self.ui.authenticator.notloggedin
   #    self.ui.authenticator.remember(self.ui.username)
   #    self.ui.authenticator.forget()
   #    {"username":self.ui.username})
   #
   def __init__(self, ui, config):
      self.ui = ui
      self.config = config
   #
   # ==== LOGIN/AUTHENTICATION HANDLING ====
   #
   def login_screen(self):
      return {
              "template" : "login_screen.html",
              "blogname": self.config["blogname"],
              "blogbanner": self.config["blogbanner"],
              "host": self.config["host"],
             }

   def login_auth(self):
      self.ui.username = self.ui.authenticator.check("name","pwd")
      if self.ui.username is not self.ui.authenticator.notloggedin:
         return self.login_successful()
      else:
         return self.login_denied()

   def login_successful(self):
      self.ui.authenticator.remember(self.ui.username)
      return {
              "template" : "login_auth.html",
              "blogbanner": self.config["blogbanner"],
              "username":self.ui.username,
              "blogname": self.config["blogname"],
              "host": self.config["host"],
             }

   def logout(self):
      self.ui.authenticator.forget()
      return {
              "redirecturl" : self.config["fullurl"],
      }

   def login_denied(self):
      self.ui.authenticator.forget()
      return {
              "template" : "login_deny.html",
              "username":self.ui.username,
              "blogbanner": self.config["blogbanner"],
              "blogname": self.config["blogname"],
              "host": self.config["host"]
             }

if __name__ == "__main__":
   print "No useful __main__ code for this yet"
	