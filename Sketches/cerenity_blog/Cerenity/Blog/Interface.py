#!/usr/bin/python
#
#

import re

class Interface:
    #
    # application:
    #     self.posts = application.posts
    #     self.username = application.username
    #     self.authenticator = application.authenticator
    #     self.authorisation = application.authorisation
    #     AuthenticationInterface(self, application, config)
    #
    # AuthenticationInterface:
    #    self.auth = AuthenticationInterface(self, application, config)
    # config:
    #
    def __init__(self, application,AuthenticationInterface,config):
       self.posts = application.posts
       self.username = application.username
       self.authenticator = application.authenticator
       self.authorisation = application.authorisation
       self.config = config
       self.auth = AuthenticationInterface(self, config.v)

    def _formatNodeForListview(self,post,viewnode=None):
       if viewnode is None:
           viewnode = post["__NODEID__"]
       
       colours = ("blue", "red","green", "yellow", "purple", "cyan")
       if post.get("Visible", None) != "1":
           raise "NotVisible"
       post["__COMMENTS__"] = str(self.posts.numReplies(post["__NODEID__"]))
       post["__COLOUR__"] = colours[(len(post["__BODY__"]) % len(colours))]
       post["__ESCAPEDSUMMARY__"] = post["__SUMMARY__"].replace("'","\\'")
       post["__ESCAPEDSUMMARY__"] = post["__ESCAPEDSUMMARY__"].replace('"',"\\'")
       post["__ESCAPEDSUMMARY__"] = post["__ESCAPEDSUMMARY__"].replace('<',"&lt;")
       post["__ESCAPEDSUMMARY__"] = post["__ESCAPEDSUMMARY__"].replace('>',"&gt;")
       post["extra"] = ""
       if self.authorisation.action("denynode"):
           post["extra"] = (   # This adds a "hide" button into the popup :-)
                            "&lt;p align=\\'right\\'&gt;"
                            "&lt;i&gt;"
                            "&lt;a href=\\'blog.cgi?rm=denynode&nodeid=%s\\'&gt;"
                            "[hide]"
                            "&lt;/a&gt;"
                            "&lt;/i&gt;" 
                            )\
                            % post["__NODEID__"]

       post["__NODEID__"] = viewnode
       postText = self.config.format["network"]["post"] % post
       return postText

    def _formatNodeForPageView(self, comment, commentid):
        if comment.get("Visible", None) != "1":
           raise "NotVisible"
        indentCount = self.posts.replyDepth(comment)
        if comment["Moderated"]:
           comment["moderate"] = self.config.format["network"]["moderatedby"] % comment

        comment["Indent"] = '<div class="reply">'*indentCount
        comment["Outdent"] = "</div>"*indentCount
        comment["extra"] = ""
        if self.authorisation.action("denynode"):
            comment["extra"] = \
                 '<a href="blog.cgi?rm=denynode&nodeid=%s">%s</a>' % (
                       str(commentid), 
                       "(hide)"
                 )

        commentText = self.config.format["network"]["comment"] % comment
        return commentText

    def _format_NodeTree(self,rootnodeid):

       # Get replies IDs. These are in thread order.
       replies = list(self.posts.allNodes(rootnodeid))
       replies_ = [ self.posts.replyNodeIDAsSortableID(len(rootnodeid), x) for x in replies]
       replies_.sort()
       replies = [ self.posts.SortableIDAsNodeID(rootnodeid, x) for x in replies_ ]

       # Read the replies, and format the individual nodes
       comments = []
       for commentid in replies:
           comment = self.posts.readNode(commentid)
           try:
               commentText = self._formatNodeForPageView(comment,commentid)
               comments.append(commentText)
           except "NotVisible":
               pass
       commentText = "\n".join(comments)
       
       # Combine the replies with the rootnode to create the NodeTreeView
       post = self.posts.readNode(rootnodeid)
       if self.posts.isReply(rootnodeid):
           basenode = self.posts.baseNode(rootnodeid)
           post["__BODY__"] = ('<P>This is a reply, <a href="blog.cgi?rm=viewpost&nodeid=%s"> basepost </a><P>' % basenode) +post["__BODY__"]
       post["__COMMENTTEXT__"] = commentText
       return self.config.format["network"]["fullpost"] % post

    def _formatCommentToModerate(self, comment,nodeid):
       post = self.posts.readNode(nodeid)
       # Need to pull in post's subject for various reasons
       comment["PostSubject"] = post["Subject"]
       if comment["Subject"] == "":
           comment["Subject"] = "( No Subject )" # Can't select to moderate otherwise :-/
       return self.config.format["network"]["shortmoderatecomment"] % comment

    def _formatPostToModerate(self, post):
       if post["Subject"] == "":
           if post["__NODEID__"][-5:] == ".html":
               post["Subject"] = post["__NODEID__"][:-5]
           else:
               post["Subject"] = "( No Subject )" # Can't select to moderate otherwise :-/
       return self.config.format["network"]["shortmoderatepost"] % post

    def _prefsbox(self):
       sidebar = [self.username]
       if self.username == self.authenticator.notloggedin:
          sidebar.append('<a href="blog.cgi?rm=login_screen">Login</a>')
       else:
          sidebar.append('<a href="blog.cgi?rm=logout">Logout</a>')

       descriptions = {
          "newposting": "New Post",
          "moderatecomments": "Moderate",
          "moderateposts" : "Moderate Posts",
          "todolist": "Scrapbook",
          "todolist": "Scrapbook",
       }
       for action in descriptions.keys():
          if self.authorisation.action(action):
             sidebar.append('<a href="blog.cgi?rm=%s">%s</a>' % (action, descriptions[action]))

       sidebar.append('<a href="blog.cgi?recentchanges=1">All Changes</a>')
       sidebar.append('<a href="blog.cgi">Home</a>')
       return '<div class="navblock">' + (",\n".join(sidebar)) + "</div>"


# or as a regular CGI app...
if __name__ == "__main__":
    e = Blog()
    e.run()
