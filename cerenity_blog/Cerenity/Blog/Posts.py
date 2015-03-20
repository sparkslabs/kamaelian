#!/usr/bin/python
#
# Changed over fully to using MimeDict. This allows Posts and Comments to
# share much of the same code with a few extra minor constraints/changes for
# Comments.
#

# Needed to make this code work happily with Python 2.2
from __future__ import generators
import time
import os
import MimeDict

class Posts(object):
   def __init__(self, directory="posts"):
      self.postdirectory = directory

   def formatForDisk(self, **argd): return str(MimeDict.MimeDict(**argd))

   def openFileToWrite(self, directory, name):
      "Always opens the file, unless permissions prevent it. Handles non-existance of the directory"
      filename = os.path.join(directory, name)
      try:
         f = open(filename, "w")
      except IOError:
         try:
            # This should fail with OSError. If it doesn't, it means we can
            # read the directory, but not write to it, meaning either
            # permissions are wrong, the disk is full, or similar error
            _ = os.listdir(self.postdirectory)
            raise "Directory: %s has the wrong permissions, please correct" % directory
         except OSError:
            os.mkdir(directory)
            f = open(filename, "w")
      return f,filename

   def saveNode(self, node, nodeid):
      f,filename = self.openFileToWrite(self.postdirectory, nodeid )
      f.write(self.formatForDisk(**node))
      f.close()
      return True

   def getReplyNodeID(self, replyToNodeID):
      replyCommentBase = os.path.join(self.postdirectory, str(replyToNodeID))
      base = 1
      commentfilename = replyCommentBase + "." + str(base)
      while os.path.exists(commentfilename):
          base = base + 1
          commentfilename = replyCommentBase + "." + str(base)
      commentid = replyToNodeID+"."+str(base)
      return commentid

   def newNode(self, node, BaseID=None):
      """Node ids here are like 123456, 123456.1 123456.4.2.1.3"""

      if ( node.get("InReplyToCommentID", None) is None) and (BaseID is None):
          nodeid = str(int(time.time()))
      else:
          inReplyTo = node.get("InReplyToCommentID", None)
          node["InReplyToCommentID"] = node.get("InReplyToCommentID", inReplyTo)
          inReplyToARG = node.get("InReplyToCommentID", BaseID)

          nodeid = node["PostID"]
          if inReplyToARG is not None:
              nodeid +=  "." + inReplyToARG

          nodeid = self.getReplyNodeID(nodeid)

      return self.saveNode(node, nodeid)

   def makeSummary(self, post):
      bodyLines = post["__BODY__"].split("\n")
      summarylines = []
      i = 0
      try:
         while bodyLines[i].lstrip().rstrip() != '':
            summarylines.append(bodyLines[i])
            i = i + 1
      except IndexError:
         pass      
      summary = "".join(summarylines)
      summary = summary.replace("\r","")
      return summary

   def enforcePostConstraints(self, post, postid):
      # Ensure certain fields exist with certain values
      # Always update the summary since the post MAY have changed since it
      # was last updated.
      #
      # First the values which are calculated - can't really come from a config file
      post["__SUMMARY__"] = self.makeSummary(post)
      post["__POSTID__"] = post.get("__POSTID__",postid)
      post["Date"] = post.get("Date", time.asctime(time.localtime()))
      #
      # Now the rest which could be statically defined
      post["Subject"] = post.get("Subject", "")
      post["From"] = post.get("From", "Guest")
      post["Ratings"] = post.get("Ratings", "")
      post["Moderator"] = post.get("Moderator", "anon")
      post["Moderated"] = post.get("Moderated", "0")
      post["Visible"] = post.get("Visible", "0")
      post["moderate"] = post.get("moderate", "")
      return post

   def enforceCommentConstraints(self, comment, postid,commentid):
      # Ensure certain fields exist with certain values
      # Always update the summary since the post MAY have changed since it
      # was last updated.
      #
      comment["__COMMENTID__"] = comment.get("__COMMENTID__", commentid)
      return comment

   def MimeDictFromFile(self,filename):
      f = open(filename)
      post = f.read()
      f.close()
      result = MimeDict.MimeDict.fromString(post)
      return result

   def readNode(self, nodeid):
      filename = os.path.join(self.postdirectory, nodeid)
      result = self.MimeDictFromFile(filename)
      result = self.enforcePostConstraints(result,nodeid)
      result["__NODEID__"] = nodeid
      return result

   def numReplies(self,nodeid): return len(list(self.allNodes(nodeid)))

   def replies(self,postid):
       l = len(postid)
       comments = [ C[l+1:] for C in self.allNodes(postid) ]
       return comments

   def allNodes(self, postid=""):
      nodes = os.listdir(self.postdirectory)
      nodes = [ x for x in nodes if (x[-2:] != ".d") ]
      nodes = [ x for x in nodes if (x != "CVS") ]
      nodes.sort()
      for c in nodes:
          if c.startswith(postid) and c != postid:
              yield c
   
   def baseNode(self, nodeid): 
       if self.isReply(nodeid):
           return nodeid[:nodeid.find(".")]
       return nodeid
   def isBase(self, nodeid): return not self.isReply(nodeid)
   def isReply(self, nodeid):
       if not ("." in nodeid): return False
       parts = nodeid.split(".")
       result = True
       del parts[0]
       for part in parts:
           try:
              _ = int(parts[0])
           except ValueError:
              result = False
       return result
   def replyDepth(self, comment): return comment["__NODEID__"].count(".")
   
   def replyNodeIDAsSortableID(self, striplen, nodeid):
       nodeid = nodeid[striplen+1:]
       return [ int(y) for y in nodeid.split(".")] 
   def SortableIDAsNodeID(self, rootnodeid, Snodeid): return rootnodeid + "." +(".".join([ str(x_) for x_ in Snodeid]) )

   def updateNode(self, nodeid, **argd):
       node = self.readNode(nodeid)
       for key in argd:
           node[key] = argd[key]
       self.saveNode(node, nodeid)

# or as a regular CGI app...
if __name__ == "__main__":
    e = Blog()
    e.run()
