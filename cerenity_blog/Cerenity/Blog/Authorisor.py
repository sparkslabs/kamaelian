class Authorisor(object):
   #
   # what:
   #   self.what.username
   # config:
   #   self.config.authorisedactions[action]
   #
   def __init__(self, what,config):
      self.what = what
      self.config = config
   def action(self,action):
      # return True # (Useful during debugging locally :)
      try:
         return self.what.username in self.config.authorisedactions[action]
      except KeyError:
         return False
