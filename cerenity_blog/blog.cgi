#!/usr/bin/python
#
# Problems:
#   * Too much code duplication. (Not too suprising - no refactoring has occurred yet)
#   * Too much of responses/templates hardcoded
#   * Uses too much HTML to define things. (CDML rendered would be nicer)
#   * Formatting tangled. (I can see at least 2 formatting classes that make
#     sense to refactor out)
#   * No self-registration, user handling etc.
#   * No integration with cerenity's stores/etc
#     However this is a very different use case for cerenity. The
#     interesting thing is how much should map over cleanly.
#   * Inconsistent API, etc
#   * Triple A stuff only really has two of the A's visible, and one is
#     enforced in the wrong place (throughout the code... :-( ). This is
#     partly due to the hacked design, and partly due to cgi_app not being
#     quite as good as it could be.
#   * Templates are hideous and completely minimalistic.
#   * etc ...
#
# Upside:
#   * Does precisely what I want:
#
#     Provides a mechanism for me publishing thoughts on the web, and
#     getting feedback, on the web, with trusted users getting automatic
#     rights to append their thoughts/comments to the post, and everyone
#     else getting the right to post their comments which go through a
#     moderation phase and a moderation interface. Moderation interface is
#     very simple "list of things not moderated not visible", and a simple
#     set of "yay"/"nay" options.
#

# Needed to make this code work happily with Python 2.2
from __future__ import generators
import cgitb; cgitb.enable()

config = (__import__("config")).config
Authenticator = (__import__("Authenticator")).Authenticator
Authorisor = (__import__("Authorisor")).Authorisor
#message = (__import__("message")).message
message = None
Posts = (__import__("Posts")).Posts
Interface = (__import__("Interface")).Interface
AuthenticationInterface = (__import__("AuthenticationInterface")).AuthenticationInterface
Blog = (__import__("Blog")).Blog

months=["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# or as a regular CGI app...
if __name__ == "__main__":
    e = Blog(config, Authenticator, Authorisor, message, Posts, Interface, AuthenticationInterface)
    e.run()
