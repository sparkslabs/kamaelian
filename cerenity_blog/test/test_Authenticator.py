#!/usr/bin/python
#
# Aim: Full coverage testing of the _authentication_ subsystem
#
# (C) Cerenity Contributors, All Rights Reserved.
#
# You may use and redistribute this under the terms of the modified BSD license 
# http://cerenity.org/ModifiedBSDLicense
#

import unittest

import sys; sys.path.append("../")
from Authenticator import Authenticator

class Authenticator_Tests(unittest.TestCase):
   def test_SmokeTest_NoArguments(self):
      """__init__ - Creating an Authenticator with no arguments fails, since it needs a "source" argument, which can be told to remember authentication information"""
      self.assertRaises(TypeError, Authenticator)


class BugFixes(unittest.TestCase):
    pass
if __name__=="__main__":
    unittest.main()
