import praw as pr
import urllib.request
import re
import csv
from PIL import Image
from imgurpython import ImgurClient as ip

from credentials import *


#Combine and Upload Images
#Parameters: Reddit comment object, path to first image, path to second image
def combine_and_upload(comment, path1, path2):
	#Combine images
	image1 = Image.open(path1)
	image2 = Image.open(path2)

	(width1, height1) = image1.size
	(width2, height2) = image2.size

	result_width = width1 + width2
	result_height = max(height1, height2)

	result = Image.new('RGB', (result_width, result_height))
	result.paste(im=image1, box=(0, 0))
	result.paste(im=image2, box=(width1, 0))

	result.save("final.png", "PNG")

	#Upload final image
	client = ip(imgur_client_id, imgur_client_secret)
	config = {"album":None,"name":"Combined Image","title":"Combined Image","description":"Combined Image"}

	image = client.upload_from_path("final.png",config=config,anon=False)
	print(image["link"])

	#Submit a reply linking to the final image
	comment.reply(image["link"])

#Download Image From Submission
def download_from_submission(submission):
	#Download original post image
	file_name, headers = urllib.request.urlretrieve(submission.url, "submission" + ".png")

	#Return path to image
	return file_name

#Download Image From Comment
def download_from_comment(comment):
	#Find parent comment
	while not comment.is_root:
		comment = comment.parent()

	if re.search("(?P<url>https?://[^\s]+)", comment.body) is None:
		return "No Image"

	#Parse comment for link to photoshopped image
	url = re.search("(?P<url>https?://[^\s]+)", comment.body).group("url")

	#Download photoshopped image
	file_name, headers = urllib.request.urlretrieve(url, "comment" + ".png")

	#Return path to image
	return file_name

################################################################

#Open .csv file containing previously replied to comments
with open("completedcomments.csv", 'r') as file:
	reader = csv.reader(file, delimiter=',')
	comments_list = list(reader)
	print(comments_list)

#Access reddit API
reddit = pr.Reddit(client_id = reddit_client_id,
 client_secret = reddit_client_secret,
  user_agent = "Python:IDontSeeItBot:1.0.0 (by /u/panner2)",
  username = username,
  password = password)

#Access subreddit
subreddit = reddit.subreddit("bottest")

#Search for "!IDontSeeIt" in the top 25 "hot" posts
for submission in subreddit.hot(limit=25):
	for comment in submission.comments.list():
		if("!idontseeit" in comment.body.lower() and comment.permalink not in comments_list and download_from_comment(comment) != "No Image"):
			combine_and_upload(comment, download_from_submission(submission), download_from_comment(comment))
			comments_list.append(comment.permalink(fast=False))

#Save .csv file containing updated list of previously replied to comments
with open("completedcomments.csv", 'w') as outfile:

	writer = csv.writer(outfile, delimiter=',')
	writer.writerow(comments_list)
	print(comments_list)
