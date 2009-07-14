#!/usr/bin/python


from __future__ import generators
import cgitb; cgitb.enable()
import cgi
import time
import os

config = (__import__("config")).config
Posts = (__import__("Posts")).Posts

posts = Posts()

rss_template = """\
<?xml version="1.0"?>
<rss version="2.0">
   <channel>
      <title>%(blogname)s</title>
      <link>%(fullurl)s</link>
      <description>%(description)s</description>
      <language>en-uk</language>
      <pubDate> %(pubDate)s </pubDate>
      <lastBuildDate> %(lastBuildDate)s </lastBuildDate>
      <docs>http://blogs.law.harvard.edu/tech/rss</docs>
      <generator>Kamaelia 0.1</generator>
      <managingEditor>%(contact)s</managingEditor>
      <webMaster>%(contact)s</webMaster>
%(posts)s
   </channel>
</rss>
""" 

item_template = """\
      <item>
         <title>%(subject)s</title>
         <link>%(link)s</link>
         <author>%(author)s</author>
         <description>%(description)s</description>
         <pubDate>%(date)s</pubDate>
         <guid>%(link)s</guid>
      </item>"""




def get_posts_to_report_on():
    nodes = [ post for post in posts.allNodes() if posts.isBase(post) ]
    nodes = [ (    os.stat(os.path.join("posts", nodeid))  , nodeid ) for nodeid in nodes ]

    nodes.sort()
    nodes.reverse()
    nodes = [ nodeid for ts,nodeid in nodes ]


    posts_to_serve = []

    for postid in nodes:
       if len(posts_to_serve)>9:
          break
       if postid == "1222863253":
          continue
       post = posts.readNode(postid)

       if post.get("Visible", "0") == "1":
          filestat = os.stat(os.path.join("posts", postid))
          t = time.gmtime(filestat.st_mtime)  # |    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime)
          posts_to_serve.append((postid,post,t, filestat.st_mtime))

    return posts_to_serve

def format_posts(posts_to_serve):
    formatted_posts = []
    for (postid,post,t, fs_mt) in posts_to_serve:

          subject     = cgi.escape(post.get("Subject","No subject"))
          description = "<![CDATA[" + post.get("__BODY__","No summary") + "]]>"
          author      = cgi.escape(post.get("From","Guest"))

          date = time.strftime("%a, %d %b %Y %H:%M:%S +0000", t)
          posturl = config.v["fullurl"]+"?rm=viewpost&amp;nodeid="+postid
          link = posturl

          item = {}
          item["subject"] = subject
          item["description"] = description
          item["date"] = date
          item["author"] = author
          item["link"] = link

          formatted_posts.append(item_template % item)
    return formatted_posts

posts_to_serve = get_posts_to_report_on()

m = 0
for (x,y,z,a) in posts_to_serve:
   if a>m:
      m = a

BlogLastModified = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(m))

formatted_posts = format_posts(posts_to_serve)

feed_contents = {}

feed_contents.update(config.v)

feed_contents["pubDate"] = BlogLastModified
feed_contents["lastBuildDate"] = BlogLastModified
feed_contents["posts"] = "\n".join(formatted_posts)

print "Content-Type: application/xml"
print
print rss_template % feed_contents



