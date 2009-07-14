class Authenticator(object):
   #
   # source:
   #   source.param(userfield)
   #   self.source.param(passfield)
   #   source.set_cookie("name",username)
   #   X = self.source.cookie("name")
   #
   def __init__(self, source, notloggedin="guest"):
      self.source = source
      self.notloggedin = notloggedin

   def check(self, userfield,passfield):
       import crypt
       passfile = open(".passwd")
       username = self.source.param(userfield)
       password = self.source.param(passfield)
       for line in passfile:
           user,crypted = line[:line.find(":")].rstrip(),line[line.find(":")+1:].lstrip().rstrip()
           if user == username:
              break
       else:
           return self.notloggedin
       passfile.close()

       cryptpass = crypt.crypt(password, crypted[:2])
       if str(cryptpass) == str(crypted):
          return username

       return self.notloggedin

   def remember(self,username):
      self.source.set_cookie("name",username,expires=3600*24*365*30)

   def forget(self):
      self.source.set_cookie("name",self.notloggedin,expires=3600*24*365*30)

   def simple_auth(self):
       X = self.source.cookie("name")
       if X:
           return X
       else:
           return self.notloggedin
