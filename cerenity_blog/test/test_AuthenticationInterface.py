#!/usr/bin/python
#
# Aim: Full coverage testing of the authentication interface
#
# (C) Cerenity Contributors, All Rights Reserved.
#
# You may use and redistribute this under the terms of the modified BSD license 
# http://cerenity.org/ModifiedBSDLicense
#

import unittest

import sys; sys.path.append("../")
from AuthenticationInterface import AuthenticationInterface

class BasicTests(unittest.TestCase):
    def test_SmokeTest_NoArguments(self):
        """__init__ - Creating an AuthenticationInterface with no arguments should raise TypeError"""
        try:
            x = AuthenticationInterface()
        except TypeError:
            return
        self.fail("Creating an AuthenticationInterface with no arguments should raise TypeError")

    def test_SmokeTest_MinimumArguments(self):
        """__init__ - Creating an AuthenticationInterface with arguments in required positions succeeds"""
        x = AuthenticationInterface(None, None, None, None, None, None, None)

    def test_login_screen_incorrectlyConfigured(self):
        """login_screen - raises TypeError if the template callback is initialised incorrectly"""
        x = AuthenticationInterface(None, None, None, None, None, None, None)
        self.assertRaises(TypeError, x.login_screen, "Authentication interface must be provided with a valid template callback")

    def test_login_screen_calls_TemplateCallbackProvided(self):
        """login_screen - Calls the template callback provided to the AuthenticationInterface"""
        log = []
        def callback(*args):
            log.append(args)
        x = AuthenticationInterface(None, callback, None, None, None, None, None)
        x.login_screen()
        self.assertEqual(len(log), 1, "Calling the callback extends the log by 1 element containing the arguments sent to the callback")

    def test_login_screen_calls_TemplateCallArgsBasicCheck(self):
        """login_screen - The first argument sent to the template callback should request the "login_screen.html" template, the second should be a dictionary of key/value arguments to fill the template with"""
        log = []
        def callback(*args):
            log.append(args)
        x = AuthenticationInterface(None, callback, None, None, None, None, None)
        x.login_screen()
        template_requested = log[0][0]
        template_arguments = log[0][1]
        self.assertEqual(template_requested, "login_screen.html", "Should request the login_screen template")
        self.assert_(isinstance(template_arguments,dict))

    def test_login_screen_TemplateArgsCheck(self):
        """login_screen - Template arguments should be blogname, blogbanner and host, which should match the values used to initialise the AuthenticationInterface given"""
        log = []
        def callback(*args):
            log.append(args)
        blogname = "Blog Name"
        blogbanner = "Testing Banner"
        host = "127.0.0.1"

        x = AuthenticationInterface(None, callback, None, None, host, blogbanner, blogname)
        x.login_screen()
        template_arguments = log[0][1]
        self.assert_("blogname" in template_arguments.keys())
        self.assert_("blogbanner" in template_arguments.keys())
        self.assert_("host" in template_arguments.keys())
        self.assertEqual(3, len(template_arguments.keys()))
        self.assertEqual(template_arguments["blogname"], blogname)
        self.assertEqual(template_arguments["blogbanner"], blogbanner)
        self.assertEqual(template_arguments["host"], host)

    def test_login_screen_TemplateArgsCheck_2(self):
        """login_screen - Template arguments should be blogname, blogbanner and host, which should match the values used to initialise the AuthenticationInterface given (test with different args!)"""
        log = []
        def callback(*args):
            log.append(args)
        blogname = "Blog Name 2"
        blogbanner = "Testing Banner 2"
        host = "127.0.0.2"

        x = AuthenticationInterface(None, callback, None, None, host, blogbanner, blogname)
        x.login_screen()
        template_arguments = log[0][1]
        self.assertEqual(template_arguments["blogname"], blogname)
        self.assertEqual(template_arguments["blogbanner"], blogbanner)
        self.assertEqual(template_arguments["host"], host)

    def test_login_auth_AfterNoUIArgumentInInit(self):
        """login_auth - Fails if the ui argument to the initialiser was invalid."""
        #
        # XXX This test rummages too deep. This implies the UI argument is incomplete
        #     has an incomplete UI
        #
        # Also, this *might* look like it's testing the mock, but what it's
        # doing is explicitly laying out behvaiour in case the provided data
        # is broken.
        #
        # Whilst this test suite is valid, it's inherently broken conceptually and
        # needs to evolve to a better state with greater decoupling.
        #
        # Fails if no authenticator attribute on the ui argument
        x = AuthenticationInterface(None, None, None, None, None, None, None)
        self.assertRaises(AttributeError, x.login_auth)

        class temp:
            authenticator = None

        # Fail if no check attribute on the authenticator on the ui argument
        x = AuthenticationInterface(temp, None, None, None, None, None, None)
        self.assertRaises(AttributeError, x.login_auth)

        # Fail if check attribute of auth on ui isn't callable
        class AuthenticatorMock:
            check = None

        class UIMock:
            authenticator = AuthenticatorMock()

        x = AuthenticationInterface(UIMock, None, None, None, None, None, None)
        self.assertRaises(TypeError, x.login_auth)

        # Throw a type error if the API for the authenticator is wrong.
        class AuthenticatorMock:
            def check():
                return

        class UIMock:
            authenticator = AuthenticatorMock()

        x = AuthenticationInterface(UIMock, None, None, None, None, None, None)
        self.assertRaises(TypeError, x.login_auth)

        # Throw an AttributeError if the Authenticator in use doesn't provide a notloggedin attribute
        class AuthenticatorMock:
            def check(self,one, other):
                return

        class UIMock:
            authenticator = AuthenticatorMock()

        x = AuthenticationInterface(UIMock, None, None, None, None, None, None)
        self.assertRaises(AttributeError, x.login_auth)

        # If the authenticator doesn't provide a forget attribute, should fail with AttributeError
        class AuthenticatorMock:
            notloggedin = None
            def check(self,one, other):
                return

        class UIMock:
            authenticator = AuthenticatorMock()

        x = AuthenticationInterface(UIMock, None, None, None, None, None, None)
        self.assertRaises(AttributeError, x.login_auth)

        # If the authenticator's forget isn't a callable, fail with TypeError
        class AuthenticatorMock:
            notloggedin = None
            def forget(): return
            def check(self,one, other):
                return

        class UIMock:
            authenticator = AuthenticatorMock()

        x = AuthenticationInterface(UIMock, None, None, None, None, None, None)
        self.assertRaises(TypeError, x.login_auth)

        # If the notloggedin attribute is True and we have no "remember" attribute, fail with an AttributeError
        class AuthenticatorMock:
            notloggedin = True
            def check(self,one, other):
                return

        class UIMock:
            authenticator = AuthenticatorMock()

        x = AuthenticationInterface(UIMock, None, None, None, None, None, None)
        self.assertRaises(AttributeError, x.login_auth)

        # If the notloggedin attribute is True and our "remember" attribute isn't callable, fail with type error
        class AuthenticatorMock:
            notloggedin = True
            remember = None
            def check(self,one, other):
                return

        class UIMock:
            authenticator = AuthenticatorMock()

        x = AuthenticationInterface(UIMock, None, None, None, None, None, None)
        self.assertRaises(TypeError, x.login_auth)

        # If the notloggedin attribute is True and our remember method has wrong signature, fail with TypeError
        class AuthenticatorMock:
            notloggedin = True
            def remember(): return
            def check(self,one, other):
                return

        class UIMock:
            authenticator = AuthenticatorMock()

        x = AuthenticationInterface(UIMock, None, None, None, None, None, None)
        self.assertRaises(TypeError, x.login_auth)

    def test_login_auth_SuccessfulLogin(self):
        """login_auth - if login is successfully authenticated, call login_successful"""

        class AuthenticatorMock:
            notloggedin = True
            def remember(self,value): return
            def check(self,one, other):
                return

        class UIMock:
            authenticator = AuthenticatorMock()

        x = AuthenticationInterface(UIMock, None, None, None, None, None, None)
        log = []
        def replacement(*args):
           log.append(args)
        x.login_successful = replacement
        x.login_auth()
        self.assertEqual(1, len(log))
      
    def test_login_auth_FailedLogin(self):
        """login_auth - if login is NOT successfully authenticated, call login_denied"""

        class AuthenticatorMock:
            notloggedin = None
            def forget(self): return
            def check(self,one, other):
                return

        class UIMock:
            authenticator = AuthenticatorMock()

        x = AuthenticationInterface(UIMock, None, None, None, None, None, None)
        log = []
        def replacement(*args):
           log.append(args)
        x.login_denied = replacement
        x.login_auth()
        self.assertEqual(1, len(log))

    def test_login_successful_calls_TemplateCallArgsBasicCheck(self):
        """login_successful - The first argument sent to the template callback should request the "login_auth.html" template, the second should be a dictionary of key/value arguments to fill the template with"""
        log = []
        def callback(*args):
            log.append(args)

        class AuthenticatorMock:
            def remember(self,value): return

        class UIMock:
            username = "fake username"
            authenticator = AuthenticatorMock()

        x = AuthenticationInterface(UIMock, callback, None, None, None, None, None)
        x.login_successful()
        template_requested = log[0][0]
        template_arguments = log[0][1]

        self.assertEqual(template_requested, "login_auth.html", "Should request the login_auth template")
        self.assert_(isinstance(template_arguments,dict))

    def test_login_successful_TemplateArgsCheck(self):
        """login_successful - Template arguments should be blogbanner, username, blogname, host, which should match the values used to initialise the AuthenticationInterface given"""
        log = []
        blogname = "Blog Name"
        blogbanner = "Testing Banner"
        host = "127.0.0.1"
        username = "fake username"
        def callback(*args):
            log.append(args)

        class AuthenticatorMock:
            def remember(self,value): return

        class UIMock:
            username = "fake username"
            authenticator = AuthenticatorMock()

        x = AuthenticationInterface(UIMock, callback, None, None, host, blogbanner, blogname)
        x.login_successful()
        template_requested = log[0][0]
        template_arguments = log[0][1]

        self.assert_("blogname" in template_arguments.keys())
        self.assert_("blogbanner" in template_arguments.keys())
        self.assert_("host" in template_arguments.keys())
        self.assert_("username" in template_arguments.keys())
        self.assertEqual(4, len(template_arguments.keys()))
        self.assertEqual(template_arguments["blogname"], blogname)
        self.assertEqual(template_arguments["blogbanner"], blogbanner)
        self.assertEqual(template_arguments["host"], host)
        self.assertEqual(template_arguments["username"], username)

    def test_login_successful_TemplateArgsCheck_2(self):
        """login_successful - Template arguments should be blogbanner, username, blogname, and host, which should match the values used to initialise the AuthenticationInterface given (test with different args!)"""
        log = []
        blogname = "Blog Name 2"
        blogbanner = "Testing Banner 2"
        host = "127.0.0.2"
        username = "fake username 2"
        def callback(*args):
            log.append(args)

        class AuthenticatorMock:
            def remember(self,value): return

        class UIMock:
            username = "fake username 2"
            authenticator = AuthenticatorMock()

        x = AuthenticationInterface(UIMock, callback, None, None, host, blogbanner, blogname)
        x.login_successful()
        template_requested = log[0][0]
        template_arguments = log[0][1]

        self.assert_("blogname" in template_arguments.keys())
        self.assert_("blogbanner" in template_arguments.keys())
        self.assert_("host" in template_arguments.keys())
        self.assert_("username" in template_arguments.keys())
        self.assertEqual(4, len(template_arguments.keys()))
        self.assertEqual(template_arguments["blogname"], blogname)
        self.assertEqual(template_arguments["blogbanner"], blogbanner)
        self.assertEqual(template_arguments["host"], host)
        self.assertEqual(template_arguments["username"], username)

    def test_logout(self):
        """logout - forces the authentictor to forget the current thing and redirect to the pre-supplied URL"""
        log = []
        def redirect_callback(*args):
            log.append(("REDIRECT", args))

        class AuthenticatorMock:
            def forget(*args):
                log.append(("FORGET", args))

        class UIMock:
            username = "fake username 2"
            authenticator = AuthenticatorMock()

        x = AuthenticationInterface(UIMock, None, redirect_callback, None, None, None, None)
        x.logout()
        self.assertEqual(log[0][0], "FORGET")
        self.assertEqual(log[1][0], "REDIRECT")

        log = []
        full_cgi_url = "foo"
        x = AuthenticationInterface(UIMock, None, redirect_callback, full_cgi_url, None, None, None)
        x.logout()
        self.assertEqual(log[0][0], "FORGET")
        self.assertEqual(log[1][0], "REDIRECT")
        self.assertEqual(log[1][1][0],  full_cgi_url)

        log = []
        full_cgi_url = "bar"
        x = AuthenticationInterface(UIMock, None, redirect_callback, full_cgi_url, None, None, None)
        x.logout()
        self.assertEqual(log[0][0], "FORGET")
        self.assertEqual(log[1][0], "REDIRECT")
        self.assertEqual(log[1][1][0],  full_cgi_url)

    def test_login_denied_calls_TemplateCallArgsBasicCheck(self):
        """login_denied - The first argument sent to the template callback should request the "login_auth.html" template, the second should be a dictionary of key/value arguments to fill the template with"""
        log = []
        def callback(*args):
            log.append(args)

        class AuthenticatorMock:
            def forget(self): return

        class UIMock:
            username = "fake username"
            authenticator = AuthenticatorMock()

        x = AuthenticationInterface(UIMock, callback, None, None, None, None, None)
        x.login_denied()
        template_requested = log[0][0]
        template_arguments = log[0][1]

        self.assertEqual(template_requested, "login_deny.html", "Should request the login_auth template")
        self.assert_(isinstance(template_arguments,dict))

    def test_login_denied_TemplateArgsCheck(self):
        """login_denied - Template arguments should be blogbanner, username, blogname, host, which should match the values used to initialise the AuthenticationInterface given"""
        log = []
        blogname = "Blog Name"
        blogbanner = "Testing Banner"
        host = "127.0.0.1"
        username = "fake username"
        def callback(*args):
            log.append(args)

        class AuthenticatorMock:
            def forget(self): return

        class UIMock:
            username = "fake username"
            authenticator = AuthenticatorMock()

        x = AuthenticationInterface(UIMock, callback, None, None, host, blogbanner, blogname)
        x.login_denied()
        template_requested = log[0][0]
        template_arguments = log[0][1]

        self.assert_("blogname" in template_arguments.keys())
        self.assert_("blogbanner" in template_arguments.keys())
        self.assert_("host" in template_arguments.keys())
        self.assert_("username" in template_arguments.keys())
        self.assertEqual(4, len(template_arguments.keys()))
        self.assertEqual(template_arguments["blogname"], blogname)
        self.assertEqual(template_arguments["blogbanner"], blogbanner)
        self.assertEqual(template_arguments["host"], host)
        self.assertEqual(template_arguments["username"], username)

    def test_login_denied_TemplateArgsCheck_2(self):
        """login_denied - Template arguments should be blogbanner, username, blogname, and host, which should match the values used to initialise the AuthenticationInterface given (test with different args!)"""
        log = []
        blogname = "Blog Name 2"
        blogbanner = "Testing Banner 2"
        host = "127.0.0.2"
        username = "fake username 2"
        def callback(*args):
            log.append(args)

        class AuthenticatorMock:
            def forget(self): return

        class UIMock:
            username = "fake username 2"
            authenticator = AuthenticatorMock()

        x = AuthenticationInterface(UIMock, callback, None, None, host, blogbanner, blogname)
        x.login_denied()
        template_requested = log[0][0]
        template_arguments = log[0][1]

        self.assert_("blogname" in template_arguments.keys())
        self.assert_("blogbanner" in template_arguments.keys())
        self.assert_("host" in template_arguments.keys())
        self.assert_("username" in template_arguments.keys())
        self.assertEqual(4, len(template_arguments.keys()))
        self.assertEqual(template_arguments["blogname"], blogname)
        self.assertEqual(template_arguments["blogbanner"], blogbanner)
        self.assertEqual(template_arguments["host"], host)
        self.assertEqual(template_arguments["username"], username)

class BugFixes(unittest.TestCase):
    pass

if __name__=="__main__":
    unittest.main()
