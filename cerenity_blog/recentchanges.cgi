#!/usr/bin/python


from __future__ import generators
import cgitb; cgitb.enable()
import cgi
import time
import os
from stat import ST_MTIME


config = (__import__("config")).config
Posts = (__import__("Posts")).Posts

posts = Posts()

opj = os.path.join

stats = []
for comment in Posts().allComments():
    parts = comment.split(".")
    
    postid, commentid = parts[0], ".".join(parts[1:])
    fp = opj("posts", postid +"."+ commentid)
    stats.append( (os.stat(fp)[ST_MTIME], fp, postid, commentid) )

for post in Posts().posts:
    X = (int(post), opj("posts", post), post, "")
    stats.append(X)

stats.sort()
stats.reverse()

print """\
Content-Type: application/xml

<?xml version="1.0"?>
<rss version="2.0">
   <channel>
      <title>%s</title>
      <link>%s</link>
      <description>%s</description>
      <language>en-uk</language>
      <pubDate> %s </pubDate>
      <lastBuildDate> %s </lastBuildDate>
      <docs>http://blogs.law.harvard.edu/tech/rss</docs>
      <generator>Kamaelia 0.1</generator>
      <managingEditor>%s</managingEditor>
      <webMaster>%s</webMaster>
""" % (config.v["blogname"],
       config.v["fullurl"],
       config.v["description"],
       time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()),
       time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()), 
       config.v["contact"],
       config.v["contact"], )



for stat in stats:
   postid = stat[2]
   commentid = stat[3]
   post = posts.readNode(postid)
   if post.get("Visible", "0") == "1":
      if commentid == "":
          subject = cgi.escape(post.get("Subject","No subject"))
          description = cgi.escape(post.get("__SUMMARY__","No summary"))
          author = cgi.escape(post.get("From","Guest"))
          pid = postid +".0"
          t = time.gmtime(float(postid))
          date = time.strftime("%a, %d %b %Y %H:%M:%S +0000", t)
          posturl = config.v["fullurl"]+"?rm=viewpost&amp;postid="+postid
          link = cgi.escape( posturl )

          print """\
          <item>
             <title>%(subject)s</title>
             <link>%(link)s</link>
             <author>%(author)s</author>
             <description>%(description)s</description>
             <pubDate>%(date)s</pubDate>
             <guid>%(link)s</guid>
          </item>
"""       % {
             "subject" : subject,
             "description" : description,
             "date" : date,
             "author" : author,
             "link" : link,
            }
      else:
          comment = posts.readComment(postid, commentid)
          if comment.get("Visible", "0") == "1":
             subject = cgi.escape(comment.get("Subject","No subject"))
             postsubject = cgi.escape(post.get("Subject","No subject"))
             description = cgi.escape(comment.get("__SUMMARY__","No summary"))
             author = cgi.escape(comment.get("From","Guest"))
             t = time.gmtime(float(stat[0]))
             date = time.strftime("%a, %d %b %Y %H:%M:%S +0000", t)
             posturl = config.v["fullurl"]+"?rm=viewpost&amp;postid="+postid
             link = cgi.escape( posturl )
             print """\
             <item>
                <title>Reply: %(subject)s (Post: %(postsubject)s) </title>
                <link>%(link)s</link>
                <author>%(author)s</author>
                <description>%(description)s</description>
                <pubDate>%(date)s</pubDate>
                <guid>%(link)s#%(commentid)s</guid>
             </item>
"""          % {
                "subject" : subject,
                "postsubject" : postsubject,
                "description" : description,
                "date" : date,
                "author" : author,
                "link" : link,
                "commentid" : commentid
               }


print """\
   </channel>
</rss>
"""
