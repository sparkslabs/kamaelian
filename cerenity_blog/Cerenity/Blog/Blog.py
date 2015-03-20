#!/usr/bin/python 
#

import cgi_app
from cgi_app import CGI_Application
import time
import re

months=["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

regex_brbr = re.compile("(<br><br>)")

action_description = {
    "previewreply" : "preview a reply to a comment/post",
    "preview" : "preview new post",
    "savepost" : "Save new post",
    "savereply" : "Save reply to a comment/post",
    "denynode" : "Moderate a comment or post and deny it",
    "approvenode" : "Moderate a post/comment and approve it",
    "moderatecomment" : "Moderate a comment",
    "moderatecomments": "Moderate Comments",
    "moderatepost" : "Moderate a post",
    "moderateposts": "Moderate posts",
    "undefinedaction" : "Do something undefined",
    "addreply" : "Reply to a post",
    "newposting" : "Make a new posting",
    "todolist" : "View the todo list. (deprecated code anyway!)",
    "viewpost" : "View a post",
    "welcome" : "View the post list/homepage!",
    "login_screen" : "See the login screen",
    "login_auth": "Attempt to login",
    "login_successful": "Be logged in" ,
    "logout": "Logout",
    "login_denied": "Be denied logging in",
}
postmessage = {
     "postvisible" : "<P> Your new post has been saved, and will now be visible to the outside world! Your post will look like this: ",
     "postinvisible" : "<P> Your contribution has been saved. Anonymous contribution go through a moderation phase at this site, and your contribution should appear within 24 hours. Many Thanks! Your post will look like this: ",
     "posterror" : "<P> <b>Error saving post: please go back in your browser and try again, or the post below will be lost!</b>",

}

class Blog(CGI_Application, object):
    def __init__(self,
                 conf,
                 authen,
                 authorise,
                 mess,
                 posts,
                 interface,
                 auth_interface,
                 *args):
       global config, Authenticator, Authorisor, message, Posts, Interface, AuthenticationInterface

       config = conf
       Authenticator = authen
       Authorisor = authorise
       message = mess
       Posts = posts
       Interface = interface
       AuthenticationInterface = auth_interface
       CGI_Application.__init__(self,*args)

    #
    # Logically needs the formatting aspects farmed out...
    #
    def setup(self):
        self.start_mode = 'welcome'
        self.posts = Posts()
        self.authenticator = Authenticator(self,"guest")
        self.authorisation = Authorisor(self,config)
        self.username = self.authenticator.simple_auth()
        self.ui = Interface(self, AuthenticationInterface,config)

    def login_screen(self): return self.ui.auth.login_screen()
    def login_auth(self): return self.ui.auth.login_auth()
    def login_successful(self): return self.ui.auth.login_successful()
    def logout(self): return self.ui.auth.logout()
    def login_denied(self): return self.ui.auth.login_denied()

    #
    # ==== MOST COMMON FUNCTIONS ====
    #
    def welcome(self):

       welcome = []
       welcome.append("""\
<div class="boxnew">
<a href='blog.cgi?rm=newposting'
ONMOUSEOVER="popup('&lt;p&gt; &lt;a href=\\'blog.cgi?rm=newposting\\'&gt; make a post! &lt;/a&gt; &lt;P&gt; This blog has a mechanism allowing anonymous posts. If you want to start a discussion on anything %s related, please post! Posts are moderated for spam and abuse. If you\\'re tempted to use it for those purposes (spam or abuse), please be aware this won\\'t work, \\'sorry\\' to disappoint. &lt;p&gt; &lt;a href=\\'blog.cgi?rm=newposting\\'&gt; make a post! &lt;/a&gt;','white')"
ONMOUSEOUT="removeBox()">
Post Something!</a>
<p class="postedby"> Start a new discussion here! Yes, without registration!
</div>
""" % (config.v["blogsubject"],)
)
       posts = [ post for post in self.posts.allNodes() ]
       posts.reverse() # The intent here is to reverse order by time, which spectacularly fails here...
       if self.param("recentchanges") == "":
          posts = [ post for post in posts if self.posts.isBase(post) ]
       elif self.param("recentchanges") == "2":
          newposts = []
          for p in posts:
              b = self.posts.baseNode(p)
              if not (b in newposts):
                  newposts.append(b)
          posts = newposts
       for postid in posts:
             try:
                 basepost = self.posts.readNode(self.posts.baseNode(postid))
                 if basepost["Visible"] != "1": continue 
                 post = self.posts.readNode(postid)
                 if post["Subject"] == "": post["Subject"] = "(No Subject)"
                 formatted_post = self.ui._formatNodeForListview(post, viewnode=self.posts.baseNode(postid))
                 welcome.append(formatted_post)
             except "NotVisible":
                 pass # skip post
       welcometext = "\n".join(welcome)
       return {              "template": "welcome.html",
                             "welcometext": welcometext,
                             "feedurl" : config.v["feedurl"],
                             "personalmessage":self.ui._prefsbox(),
                            }

    def viewpost(self):
       nodeid = self.param("nodeid")
       post = self.ui._format_NodeTree(nodeid)
       return {              "template": "viewpost.html", 
                             "feedurl" : config.v["feedurl"],
                             "post":post,
                             "personalmessage":self.ui._prefsbox()
                            }

    def todolist(self):
       return {              "template" : "todolist.html",
                             "feedurl" : config.v["feedurl"],
                             "username":self.username
                            }

    #
    # ==== DATA ENTRY ====
    #
    def newposting(self):
       return {              "template" : "newposting.html", 
                             "feedurl" : config.v["feedurl"],
                            }

    def addreply(self):
       postid=self.param("nodeid")
       post = self.posts.readNode(postid)
       return {             "template" : "addreply.html",
                             "postid":postid,
                             "postsubject":post["Subject"],
                             "personalmessage":self.ui._prefsbox()
                            }

    def unauthorised_template(self, action):
          return self.template("unauthorisedaction.html",
                               {
                                "blogbanner": config.v["blogbanner"],
                                "blogname": config.v["blogname"],
                                "host": config.v["host"],
                                "feedurl" : config.v["feedurl"],
                                "action":action_description[action],
                                "username": self.username
                               }
                              )

    # ==== PREVIEW ====
    #
    def preview(self): return self.previewnode() # Exists to allow access controls to happen
    def previewreply(self): return self.previewnode() # Exists to allow access controls to happen
    
    def previewnode(self):
       posttitle = self.param("title")
       nodebody = self.param("nodebody")

       postid = self.param("postid")
       if postid != "":
           post = self.posts.readNode(postid)
           template = "previewreply.html"
       else:
           post = {"Subject":""}
           template = "preview.html"

       t=time.localtime()
       datetime = config.format["network"]["datetime"] % {
                     "day": t[2],
                     "month": months[t[1]],
                     "year": t[0],
                     "hours": t[3],
                     "minutes": t[4]
                  }
       return               {
                             "template" : "previewreply.html",
                             "posttitle": posttitle,
                             "feedurl" : config.v["feedurl"],
                             "nodebody":nodebody,
                             "username":self.username,
                             "datetime":datetime,
                             "postid":postid,
                             "postsubject":post["Subject"]
                            }

    def savenode(self, node_dict, replyto, visible):
       global postmessage
       global regex_brbr
       success = True
       junk = cgi_app.cgi.parse_qs("nodebody="+self.param("nodebody"))
       try:
          nodebody = junk["nodebody"][0]
       except KeyError:
          savemessage = "<P>Post body cannot be empty! Either provide one or give up - Sorry!"
          success = False
       else:
          node_dict["__BODY__"] = nodebody
          node_dict["__BODY__"] = regex_brbr.sub("<br>\n\n<br>", node_dict["__BODY__"], 1) # Insert blank line after first double link
          success = self.posts.newNode(node_dict, replyto)
       
       if success:
          if visible == "1":
             savemessage = postmessage["postvisible"]
          else:
             savemessage = postmessage["postinvisible"]
       else:
          savemessage = postmessage["posterror"] + savemessage

       return {
                 "template"    : "savepost.html",
                 "posttitle"   : node_dict["Subject"],
                 "nodebody"    : node_dict["__BODY__"],
                 "username"    : node_dict["From"],
                 "datetime"    : node_dict["Date"],
                 "feedurl"     : config.v["feedurl"],
                 "savemessage" : savemessage
              }
    
    def getNewNodeData(self,replyparam="replynode"):
        replyto = self.param(replyparam)
        if replyto == "": replyto = None

        if self.authorisation.action("savecommentvisible"):
            visible = "1"
        else:
            visible = "0"

        node_dict = {
           "From"      : self.username,
           "__BODY__"  : "",
           "Subject"   : self.param("title"),
           "Date"      : self.param("datetime"),
           "Visible"   : visible,
           "Ratings"   : "0",
           "Moderated" : "0",
        }
        return ( replyto, visible, node_dict )

    #
    # ==== CONTENT UPDATE ====
    #
    def savepost(self):
       if self.referer() == "http://yeoldeclue.com/cgi-bin/blog/blog.cgi":
           replyto, visible, node_dict = self.getNewNodeData()
           return self.savenode(node_dict, replyto, visible)
       return self.unauthorised_template("Error, retry")

    #
    # ==== CONTENT UPDATE ====
    #
    def savereply(self):

       replyto, visible, node_dict = self.getNewNodeData("postid")
       node_dict["PostID"] = replyto
       return self.savenode(node_dict, replyto, visible)

    #
    # ==== COMMENT MODERATION ====
    #    
    def unmoderatedNonVisibleNodes(self, filterfunc, template):
       nodes = self.posts.allNodes()
       nodes_to_moderate = [ x for x in nodes if filterfunc(x) ] # self.posts.isReply(x) ]
       nodes = []
       for nodeid in nodes_to_moderate:
           node = self.posts.readNode(nodeid)
           if node["Visible"]=="0" and node["Moderated"]== "0":
               if self.posts.isReply(nodeid):
                   postid = self.posts.baseNode(nodeid)
                   nodes.append(self.ui._formatCommentToModerate(node,postid))
               else:
                   nodes.append( self.ui._formatPostToModerate(node) )
       invisiblenomod = "<ul>\n"+"".join(nodes)+ "</ul>\n"
       return {
                 "template"       : template,
                 "username"       : self.username,
                 "feedurl"        : config.v["feedurl"],
                 "invisiblenomod" : invisiblenomod,
                 "comments"       : ""
              }

    def moderatecomments(self): return self.unmoderatedNonVisibleNodes(self.posts.isReply, "moderatecomments.html")
    def moderateposts(self): return self.unmoderatedNonVisibleNodes(self.posts.isBase, "moderateposts.html")

    def moderateNode(self, nodetype): ### "moderatecomment" , "moderatepost"
       nodeid = self.param("nodeid")
       NODE = self.posts.readNode(nodeid)
       nodeText = config.format["network"][nodetype] % NODE
       return {
               "template"      : nodetype + ".html",
               "username"      : self.username,
               "feedurl"       : config.v["feedurl"],
               "formattednode" : nodeText,
               "nodeid"        : nodeid,
              }
    
    def moderatecomment(self): return self.moderateNode("moderatecomment")
    def moderatepost(self):    return self.moderateNode("moderatepost")
        
    def updateModeration(self, **argd):
       nodeid = self.param("nodeid")
       next = self.param("next")
       if next == "": next = "moderatecomments"
       self.posts.updateNode(nodeid, **argd)
       return {
              "redirecturl" : "%s?rm=%s" % (config.v["fullurl"], next)
       }
    
#<<<<<<< Blog.py
#    def denynode(self): return self.posts.updateNode(Moderated="1", Visible="0")
#    def approvenode(self): return self.posts.updateNode(Moderated="1",Visible="1")
#=======
    def denynode(self): return self.updateModeration(Moderated="1", Visible="0")
    def approvenode(self): return self.updateModeration(Moderated="1",Visible="1")
#>>>>>>> 1.102

    def __getattribute__(self, attr):
        AAs = super(Blog, self).__getattribute__("authenticatedActions")
        if attr in AAs:
            UT = super(Blog, self).__getattribute__("unauthorised_template")
            if self.authorisation.action(attr):
                def customCallback(*args):
                    result = super(Blog, self).__getattribute__(attr)(*args)
                    try:
                        if result.get("redirecturl", None) is not None:
                            self.redirect(result["redirecturl"])
                            return
                        if result.get("template", None) is not None:
                            template = result.pop("template")
                            result["blogname"] = result.get("blogname", config.v["blogname"])
                            result["blogbanner"] = result.get("blogbanner", config.v["blogbanner"])
                            result["host"] = result.get("host", config.v["host"])
                            return self.template( template, result)
                    except AttributeError:
                       return result
                return customCallback
            else:
                def customisedError():
                    return UT(attr)
                return customisedError
        else:
            try:
                return super(Blog, self).__getattribute__(attr)
            except AttributeError:
                UT = super(Blog, self).__getattribute__("unauthorised_template")
                def customisedError():
                    return UT("undefinedaction")
                return customisedError

    #
    # This has changed to defaulting to allow actions unless authenticated.
    # This is bad practice actually. This list should show whitelisted actions
    #    Whitelisted abilities: __init__, setup, unauthorised_template, __getattribute__(
    # Grey listing would allow for "Permit X if Y is granted". This may be recursive.
    #
    authenticatedActions = {
        "previewreply" : previewreply,
        "preview" : preview,
        "savepost" : savepost,
        "savereply" : savereply,
        "denynode" : denynode,
        "approvenode" : approvenode, 
        "moderatecomment" : moderatecomment,
        "moderatecomments" : moderatecomments,
        "moderatepost" : moderatepost,
        "moderateposts": moderateposts,
        "addreply": addreply,
        "newposting": newposting,
        "todolist": todolist,
        "viewpost": viewpost,
        "welcome": welcome,
        "login_screen" : login_screen,
        "login_auth": login_auth,
        "login_successful": login_successful,
        "logout": logout,
        "login_denied": login_denied,
    }

if __name__ == "__main__":
     print "No code that can/should be run for __main__"
