import praw as pr
import urllib.request
import re
from PIL import Image
from imgurpython import ImgurClient as ip

from credentials import *


def combine_and_upload(comment, path1, path2):
	#Combine Images
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

	comment.reply(image["link"])

def download_from_submission(submission):

	file_name, headers = urllib.request.urlretrieve(submission.url, "submission" + ".png")

	return file_name

def download_from_comment(comment):

	while not comment.is_root:
		comment = comment.parent()

	url = re.search("(?P<url>https?://[^\s]+)", comment.body).group("url")

	file_name, headers = urllib.request.urlretrieve(url, "comment" + ".png")

	return file_name


reddit = pr.Reddit(client_id = reddit_client_id,
 client_secret = reddit_client_secret,
  user_agent = "Python:IDontSeeItBot:1.0.0 (by /u/panner2)",
  username = username,
  password = password)

subreddit = reddit.subreddit("bottest")

#Search for "!IDontSeeIt"
for submission in subreddit.hot(limit=25):
	for comment in submission.comments.list():
		if("!idontseeit" in comment.body.lower()):
			combine_and_upload(comment, download_from_submission(submission), download_from_comment(comment))
