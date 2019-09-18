""" 
# BIMP - Batch Image Manipulating with Python
 Author; Mark Pedersen @makerspender
 Recreated by : Gagan Gulyani
 License: CC BY 2.0 https://creativecommons.org/licenses/by/2.0/
"""
# load required libraries

import PIL
import textwrap
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
from io import BytesIO
import os
import os.path
import random

savePath = "static/Images/GeneratedQuotes"

def GenImage(quote, author, quoteID, update_ = False):
    path = 'models'
    pictures = os.listdir(path + '/' + 'Images')
    randomPicture = pictures[random.randint(0, len(pictures)-1)]
    print("Random picture: "  + randomPicture)
    cImagePath = f"{savePath}/{quoteID}.jpg"
    if os.path.exists(cImagePath) and not update_:
        return open(cImagePath, 'rb')
# for idx, val in enumerate(lines):
    val = quote
    currentauthor = author

# create main quote value
    if len(val) < 180:
        para = textwrap.wrap(val, width=40)
    else:
        para = textwrap.wrap(val, width=50)
# set image dimensions
    MAX_W, MAX_H = 1920, 1280
# set image location
    imageFile = f"{path}/Images/{randomPicture}"
# assign im to pillow and open the image
    im = Image.open(imageFile).convert('RGB')
# resize the image to our chosen proportions and use antialiasing
    im = im.resize((1920, 1280), Image.ANTIALIAS)
# create new layer for adding opacity
    poly = Image.new('RGBA', (1920, 1280))
    polydraw = ImageDraw.Draw(poly)
# fill the image with black and 165/255 opacity
    polydraw.rectangle([(0, 0), (1920, 1280)],
                       fill=(0, 0, 0, 165), outline=None)
# paste in the layer on top of the image im
    im.paste(poly, mask=poly)
# command to start merging layers
    draw = ImageDraw.Draw(im)
# setting up fonts
    if len(val) < 180:
        # print(f"{path}/Fonts/ArchivoBlack-Regular.ttf")
        # print(os.path.exists(f"{path}/Fonts/ArchivoBlack-Regular.ttf"))
        font = ImageFont.truetype(f"{path}/Fonts/ArchivoBlack-Regular.ttf", 80)
        authorfont = ImageFont.truetype(f"{path}/Fonts/Roboto-BlackItalic.ttf", 60)
        current_h, pad = 300, 50  # For Quote
        current_h2, pad2 = 900, 80  # For Author
    else:
        font = ImageFont.truetype(f"{path}/Fonts/ArchivoBlack-Regular.ttf", 50)
        authorfont = ImageFont.truetype(f"{path}/Fonts/Roboto-BlackItalic.ttf", 40)
        current_h, pad = 200, 40  # Reduced Padding for long quote
        current_h2, pad2 = 600, 80

    linkfont = ImageFont.truetype(f"{path}/Fonts/Roboto-Black.ttf", 24)
# setting up padding and positioning for quote text
# for loop breaking up each quote into lines not exceeding
# the width of the image dimensions
    for line in para:
        w, h = draw.textsize(line, font=font)
        draw.text(((MAX_W - w) / 2, current_h), line, font=font)
        current_h += h + pad
# setting up padding and positioning for author text

    w, h = draw.textsize(currentauthor, font=authorfont)
    draw.text(((MAX_W - w) / 2, (current_h + 100)),
              currentauthor, font=authorfont)
    current_h2 += h + pad2
# setting up padding and positining for optional text
    current_h3, pad3 = 1200, 30

    sitelink = "iThinketh.ml"
    w, h = draw.textsize(sitelink, font=linkfont)
    draw.text(((MAX_W - w) / 2, current_h3), sitelink, font=linkfont)
    current_h3 += h + pad3
    im.save(cImagePath, format="JPEG")
    return open(cImagePath, 'rb')
