# YODA
## _You Only Detect All - An object detection website_
#### - Name inspired by YOLO, the object detection model used in the project. 
## Table of contents

- Introduction
- Requirements
- Installation
- Troubleshooting
- Credits
- About me.

## Introduction
This is an object detection project. Users may upload photos, videos to the website and have them processed by an object detection model. 
[Here](https://youtu.be/V95hg3Cvt3I) is a video of me showcasing my project. 
### Image and video detection
Here users can upload an image or video file. The file is processed and a processed copy is created. Both can be downloaded from the website. 
### Live Webcam 
A live webcam obtion is also available. A live feed is created when entering the tab. Then object detection is run on each frame and then displayed. Users can download the current frame using a button. 
### Saved images
All images and videos uploaded by the user (and their processed versions) can be downloaded or deleted from the database. 
### Changing passwords
Users can change their password by entering their old password and their desired new password. 


## Requirements
This project is a website served using python and flask and thus requires both. 

Install python to your computer and add python to your path. **This project was developed using Python version 3.10** It is recommended that you use this version of python. Python versions before **Python3.5** will not work. 


**I coded this project in Ubuntu 22.04 LTS** because that was the only operating system I had. This project should work with other debian based linux systems. I have not been able to test it with MAC and WINDOWS systems. 

The following python libraries are required to use YODA:
> * flask
> * flask-reuploaded
> * flask-wtf
> * cs50
> * opencv-python
> * numpy
> * flask-sessions

If you would like to look inside the `yoda.db`, the you will need a program such as `sqlite3`. 


## Installation
These instructions are for debian based systems. Since MacOS is a unix based operating system, the installation instructions are pretty similar. 
Download the git repository from github by running 
> `git clone https://github.com/SedikSadik/YODA` 

or downloading it as a zip. To use `git`, install it as such:
> `sudo apt install git`. 

You will need root privileges for this. 

Make sure you have installed python and run the following command in the root directory of this project. 
> `pip3 install -r requirements.txt`

You now have everything required to run YODA. 
You can run yoda using the following command while in the root directory of the project. 
> `flask run -h localhost -p 3000`

You can access the website by clicking the link generated in the command line interface or go to `http://localhost:3000`
If port 3000 is not available, you can change the number 3000 in both places with another integer above 3000
You should be able to see a register and login page. Register with a username and password and you're set! May YODA guide you.  

## Troubleshooting
If somehow the yoda database is deleted, you can create another one by first running `sqlite3 yoda.db` and then run each command from the  `make_database.sql` file within sqlite3. Delete both the uploads and detected folders and then restart the flask app.

Because of the size of the model I am using, my model is best suited for fast but not necessarily accurate detections. If the uploaded and processed photos look the same, it may be because the model did not find any object (even though there may be object in the uploaded image)
## Credits
When doing this project, I got help from the following sources:
* [w3schools](https://www.w3schools.com/)
* [bootstap](https://getbootstrap.com/)
* [drupal.com](https://www.drupal.org/docs/develop/managing-a-drupalorg-theme-module-or-distribution-project/documenting-your-project/readmemd-template)
* [Youtube: Luke Peters](https://www.youtube.com/@LukePeters)
* [Youtube: Red Eyed Code](https://www.youtube.com/@RedEyedCoderClub)
* [Youtube: Krish Naik](https://www.youtube.com/@krishnaik06)
* [Youtube: Web Dev Simplified](https://www.youtube.com/@WebDevSimplified)

## About Me
I am Sedik Sadik, a first year international student in Harvard College studying Computer Science (A.B/S.M). This is my submission for the CS50 final project. 