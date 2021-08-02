#!/usr/bin/env python3

# FIX LOG
# 
# - Fix font size for screen size
# - Add Documentation & README (WORKING)
# - Build Process
# - Add GUI?
# - hosting utility 
#
# - Optimisation (Double Request?)
# - Optimisation (PIL Library)
# - Make Cross Compatible

import requests
import random
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from pathlib import Path
import time
import dotenv
import os

PER_PAGE = 30
RESOLUTION = (1920,1200)

cwd = str(Path(__file__).parent.resolve()) + "/"
logf = open(cwd + "app.log", "a")
logf.write("\n"+ 100*"-"+"\n")

root_unsplash_url = "https://api.unsplash.com/"
topic = "current-events"

dotenv.load_dotenv()

access_key = os.getenv("UNSPLASH_API_KEY")
mapbox_client_id = os.getenv("MAPBOX_API_KEY")

params = {"client_id":access_key,"orientation":"landscape","order_by":"popular","per_page":PER_PAGE}


class UnsplashImg:
    def __init__(self, url : str, params : dict):

        # Needed for request
        self.url = url
        self.params = params
        
        # Run the main function
        self.main()

    def __repr__(self):
        return f"Image Object: \nURL: \n{self.url} \nLocation: \n{self.location}"

    def main(self):
        self.findImgId()
        self.getImgData()
        self.formatLocation()
        self.formatExif()

    def findImgId(self) -> str:
        res1 = requests.get(root_unsplash_url + "topics/" + topic + "/photos", params=params)
        
        rand = random.randint(0,PER_PAGE-1)
        self.photo_id = res1.json()[rand]["id"]

    # Add url to info
    def getImgData(self) -> dict:
        res2 = requests.get(root_unsplash_url + "photos/" + self.photo_id, params={"client_id":access_key})
        self.data = res2.json()
        self.url = self.data["urls"]["full"]
        self.title = self.data["description"]
        self.author = self.data["user"]["name"]

    # Change this function to handle coordinates and that 
    def formatLocation(self):
        self.location = ""
        self.coords = ()

        title = self.data['location']['title']
        city = self.data['location']['city']
        lat = self.data['location']['position']['latitude']
        lon = self.data['location']['position']['longitude']

        if lat == None:
            self.main()
        
        if title != None:
            self.location += f"{title}\n"
        if city != None and title.split()[0] != city:
            self.location += f"{city}\n"
        if lat != None:
            self.location += f"{lat}, {lon}\n"
            self.coords = (lon,lat)
    
    def formatExif(self):
        self.exif = ""

        make = self.data['exif']['make']
        model = self.data['exif']['model']
        exposure = self.data['exif']['exposure_time']
        aperture = self.data['exif']['aperture']
        focal_length = self.data['exif']['focal_length']
        iso = self.data['exif']['iso']

        if model != None:
            self.exif += f"{model}\n"
        if make != None and model.split()[0] != make:
            self.exif = f"{make}\n{self.exif}"
        if exposure != None:
            self.exif += f"{exposure}\n"
        if aperture != None:
            self.exif += f"f/{aperture}\n"
        if focal_length != None:
            self.exif += f"{focal_length}mm\n"
        if iso != None:
            self.exif += f"{iso} ISO\n"

class Wallpaper:
    def __init__(self, url : str, location : str, exif : str , coords : tuple):
        self.url = url
        self.location = location
        self.exif = exif
        self.coords = coords

        self.formatImage()
        self.setImage()

    def formatImage(self):
        # Take Image
        # Crop it to Resolution
        # Add Location
        # Store as PIL.Image Obj

        mapbox_url = f"https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v11/static/{self.coords[0]},{self.coords[1]},13.0,0/500x550@2x?access_token={mapbox_client_id}" 

        im = Image.open(requests.get(self.url, stream=True).raw).convert("RGBA")

        width, height = im.size
        height1 = width*10/16
        vert_offset = (height - (height1))/2
        
        font_size = 30 #int(RESOLUTION[0]*RESOLUTION[1]/76800)

        im1 = im.crop((0,vert_offset,width,height1+vert_offset))
        im1 = im.resize(RESOLUTION,Image.ANTIALIAS)

        # Request a minimap
        minimap = Image.open(requests.get(mapbox_url, stream=True).raw).convert("RGBA")
        minimap = minimap.resize((400,480),Image.ANTIALIAS)
        minimap = minimap.crop((0,0,400,400))
        im1.paste(minimap,(RESOLUTION[0]-minimap.width-30,RESOLUTION[1]-minimap.height-30))

        draw = ImageDraw.Draw(im1)
        font_loc = ImageFont.truetype(cwd + "arial.ttf", font_size)
        font_exif = ImageFont.truetype(cwd + "arial.ttf", int(3*font_size/4))

        w_exif, h_exif = draw.textsize(self.exif, font=font_exif)

        draw.text((RESOLUTION[0]/25,26*RESOLUTION[1]/30),self.location,(255,255,255),font=font_loc)
        draw.text((RESOLUTION[0]-(1.3*w_exif),RESOLUTION[1]/20),self.exif,(255,255,255),font=font_exif)
        im1.save(cwd + 'wallpaper.png',quality=100)

    def setImage(self):
        # For extending functionality
        pass

img = UnsplashImg(root_unsplash_url,params)
Wallpaper(img.url,img.location,img.exif,img.coords)

logf.write(time.ctime()+"\n")
logf.write(img.url+"\n")
logf.write(img.location+"\n")
logf.write(img.photo_id+"\n")
logf.write(img.exif+"\n")

logf.write("Done Saving")

logf.close()
