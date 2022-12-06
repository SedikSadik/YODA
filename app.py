# Flask imports
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    send_from_directory,
    url_for,
)
from flask_session import Session
from flask_uploads import UploadSet, configure_uploads, IMAGES

from helpers import (
    apology,
    login_required,
    draw_boxes,
    VideoUploadForm,
    ImageUploadForm,
    VIDEOS,
    create_user_folder,
)

# TODO
import logging
import datetime

# Other
from werkzeug.security import check_password_hash, generate_password_hash
import cv2
import os
from cs50 import SQL

# Configure application
app = Flask(__name__)


# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "very_important_secret_key"
app.config["UPLOADED_PHOTOS_DEST"] = "uploads/images"
app.config["UPLOADED_VIDEOS_DEST"] = "uploads/videos"
app.config["DETECTED_PHOTOS_DEST"] = "detected/images"
app.config["DETECTED_VIDEOS_DEST"] = "detected/videos"

# create directories if they dont exits
if not os.path.isdir("uploads"):
    os.mkdir("uploads")
if not os.path.isdir("detected"):
    os.mkdir("detected")

if not os.path.isdir("uploads/images"):
    os.mkdir("uploads/images")
if not os.path.isdir("uploads/videos"):
    os.mkdir("uploads/videos")
if not os.path.isdir("detected/images"):
    os.mkdir("detected/images")
if not os.path.isdir("detected/videos"):
    os.mkdir("detected/videos")


# Define upload sets for images and photos
photos = UploadSet("photos", IMAGES)
videos = UploadSet("videos", VIDEOS)
configure_uploads(app, photos)
configure_uploads(app, videos)

# Create YOLOv4 object detection model
net = cv2.dnn.readNet("models/yolov4-tiny.weights", "models/yolov4-tiny.cfg")

model = cv2.dnn_DetectionModel(net)
model.setInputParams(size=(416, 416), scale=1 / 255, swapRB=True)
# Use the MSCOCO dataset names
with open("models/coco.names", "r") as f:
    class_names = [cname.strip() for cname in f.readlines()]

class_dict = {i: class_name for i, class_name in enumerate(class_names)}

# Thresholds for confidence and non max supression
confidence_threshold = 0.4
nms_threshold = 0.5

# create session
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///yoda.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Define 4 functions for the four file destinations
@app.route("/<process_type>/<media_type>/<user_id>/<filename>")
def get_file(process_type, media_type, user_id, filename):
    directory = os.path.join(process_type, media_type, user_id)
    # logging.critical(process_type)
    # logging.critical(media_type)
    # logging.critical(user_id)
    logging.critical(filename)
    # logging.critical(directory)
    return send_from_directory(directory, filename)


# @app.route("/detected/images/<user_id>/<filename>")
# def get_detected_image(user_id, filename):
#     return send_from_directory(app.config["DETECTED_PHOTOS_DEST"], filename)


# @app.route("/uploads/videos/<filename>")
# def get_uploaded_video(filename):
#     return send_from_directory(app.config["UPLOADED_VIDEOS_DEST"], filename)


# @app.route("/detected/videos/<filename>")
# def get_detected_video(filename):
#     return send_from_directory(app.config["DETECTED_VIDEOS_DEST"], filename)


@app.route("/", methods=["GET"])
@login_required
def index():
    """Return the image_detection.html page"""
    return render_template("index.html")


@app.route("/image_detection", methods=["GET", "POST"])
def image_detection():
    # Create a form for image uploads
    user_id = session["user_id"]
    form = ImageUploadForm()
    if request.method == "GET":
        return render_template("image_detection.html", form=form)
    else:
        # photos_info list holds info about the uploaded and the detected image
        photos_info = []
        if form.validate_on_submit():  # Check if form submission is valid

            # Save the uploaded photo from form
            filename_with_folder = photos.save(
                form.photo.data,
                str(user_id),
            )
            just_filename = filename_with_folder.split("/")[-1]
            # logging.critical(filename.split("/")[-1])
            # logging.critical(filename)
            full_file_path = os.path.join(
                app.config["UPLOADED_PHOTOS_DEST"], filename_with_folder
            )
            # logging.critical(file_path)

            # read the stored image in matrix form
            image = cv2.imread(filename=full_file_path)

            # Run object detection model on the image
            class_ids, scores, boxes = model.detect(
                image, confidence_threshold, nms_threshold
            )
            # Draw the detected objects on the image
            draw_boxes(image, class_ids, scores, boxes, class_dict)
            # Save the new image in the detected folder
            full_output_path = os.path.join(
                app.config["DETECTED_PHOTOS_DEST"], filename_with_folder
            )
            cv2.imwrite(
                full_output_path,
                image,
            )

            db.execute(
                "INSERT INTO saved (owner_id, filename, path, media_type, process_type, upload_time) VALUES (?,?,?,?,?,?)",
                user_id,
                just_filename,
                full_file_path,
                "Image",
                "Uploaded File",
                datetime.datetime.now(),
            )

            db.execute(
                "INSERT INTO saved (owner_id, filename, path, media_type, process_type, upload_time) VALUES (?,?,?,?,?,?)",
                user_id,
                just_filename,
                full_output_path,
                "Image",
                "Processed File",
                datetime.datetime.now(),
            )
            # get the urls for both images
            uploaded_url = url_for(
                "get_file",
                process_type="uploads",
                media_type="images",
                user_id=user_id,
                filename=just_filename,
            )
            # logging.critical(f"{uploaded_url} is the uploaded url")
            detected_url = url_for(
                "get_file",
                process_type="detected",
                media_type="images",
                user_id=user_id,
                filename=just_filename,
            )
            # logging.critical(f"{detected_url} is the detected url")
            photos_info.append(
                {
                    "url": uploaded_url,
                    "title": just_filename,
                    "description": "Uploaded Photo",
                }
            )
            photos_info.append(
                {
                    "url": detected_url,
                    "title": just_filename,
                    "description": "Processed Photo",
                }
            )

        # Pass in the photo infos to the template
        return render_template(
            "image_detection.html", form=form, photos_info=photos_info
        )


@app.route("/video_detection", methods=["GET", "POST"])
def video_detection():
    # Similar to image detection, this time create a form for video files
    form = VideoUploadForm()
    if request.method == "GET":
        return render_template("video_detection.html", form=form)
    else:
        videos_info = []
        user_id = session["user_id"]
        if form.validate_on_submit():
            # Save the passed in video
            filename_with_folder = videos.save(form.video.data, str(user_id))

            just_filename = filename_with_folder.split("/")[-1]
            just_output_filename = ".".join(just_filename.split(".")[:-1]) + ".mov"

            # logging.critical(filename.split("/")[-1])
            # logging.critical(filename)
            full_file_path = os.path.join(
                app.config["UPLOADED_VIDEOS_DEST"], filename_with_folder
            )
            # Create a capture object for the video
            cap = cv2.VideoCapture(full_file_path)
            if not cap.isOpened():
                flash("We weren't able to open the video you uploaded")
                return render_template("video_detection.html", form=form)

            # Get relevant info to write a detected version of the video.
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(3))
            height = int(cap.get(4))

            # Define the output destination
            full_output_path = (
                os.path.join(app.config["DETECTED_VIDEOS_DEST"], filename_with_folder)[
                    :-3
                ]
                + "mov"
            )
            # Create writer object that writes individual frames to a file.
            writer = cv2.VideoWriter(
                full_output_path,
                cv2.VideoWriter_fourcc(*"mp4v"),
                float(fps),
                (width, height),
            )

            # Begin reading every frame of passed in video
            while True:
                ret, frame = cap.read()

                # if no more frames are left, the close both the capture and writer objects
                if not ret:
                    writer.release()
                    cap.release()
                    break

                # Run detections on each frame and draw boxes
                class_ids, scores, boxes = model.detect(
                    frame, confidence_threshold, nms_threshold
                )
                draw_boxes(frame, class_ids, scores, boxes, class_dict)
                # Write the drawn image into new file.
                writer.write(frame)

            # Being able to download the uploaded video doens't seem to be necessary. But, this will be used in the future with a video player to show the video in the browser itself.
            # uploaded_url = url_for("get_file", filename=filename)
            # videos_info.append(
            #     {
            #         "url": uploaded_url,
            #         "title": filename,
            #         "description": "Uploaded Video",
            #         "type":filename[-3:]
            #     }
            # )
            db.execute(
                "INSERT INTO saved (owner_id, filename, path, media_type, process_type, upload_time) VALUES (?,?,?,?,?,?)",
                user_id,
                just_filename,
                full_file_path,
                "Video",
                "Uploaded File",
                datetime.datetime.now(),
            )
            db.execute(
                "INSERT INTO saved (owner_id, filename, path, media_type, process_type, upload_time) VALUES (?,?,?,?,?,?)",
                user_id,
                just_filename,
                full_output_path,
                "Video",
                "Processed File",
                datetime.datetime.now(),
            )

            detected_url = url_for(
                "get_file",
                process_type="detected",
                media_type="videos",
                user_id=user_id,
                filename=just_output_filename,
            )
            videos_info.append(
                {
                    "url": detected_url,
                    "title": filename_with_folder,
                    "description": "Detected Video",
                    "ext": "mov",
                }
            )

        return render_template(
            "video_detection.html", form=form, videos_info=videos_info
        )


# Render the live-webcam html file.
# The object detection for the live detection is performed with P5js in Javascipt
@app.route("/live_webcam", methods=["GET"])
def live_webcam():
    """Render the live-webcam html file"""

    return render_template("live_webcam.html")


@app.route("/saved_files", methods=["GET", "POST"])
def saved_files():
    """Render the saved_files html file"""
    user_id = session["user_id"]
    if request.method == "GET":
        files_dict_list = db.execute(
            "SELECT id, filename, media_type, path, process_type,upload_time FROM saved WHERE owner_id = ?",
            user_id,
        )
        return render_template("saved_files.html", files_dict_list=files_dict_list)
    else:
        id = request.form.get("id")
        path = db.execute("SELECT path FROM saved WHERE id = ? ", id)[0]["path"]
        logging.critical(path)
        os.remove(path=path)
        db.execute("DELETE FROM saved WHERE id = ? ", id)
        return redirect("/saved_files")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # GET method guard clause
    if request.method == "GET":
        return render_template("register.html")

    else:
        # Get info passed in through form
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # If any are empty, then error
        if not username or not password or not confirmation:
            return apology("All fields must not be blank")

        # Password and confirmation must match
        if not password == confirmation:
            return apology("The Passwords don't match")

        # Check if username exists
        name = db.execute("SELECT username FROM users WHERE username = ?", username)
        if len(name) > 0:
            return apology("This username is already taken")

        # Register user
        if not db.execute(
            "INSERT INTO users (username, hash) VALUES(?,?)",
            username,
            generate_password_hash(password),
        ):
            return apology("There was an error when registering your account.")
        user_id = db.execute("SELECT id FROM users WHERE username = ?", username)[0][
            "id"
        ]
        create_user_folder(user_id, "detected/images")
        create_user_folder(user_id, "detected/videos")
        create_user_folder(user_id, "uploads/images")
        create_user_folder(user_id, "uploads/videos")
        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # Guard clause of GET method
    if request.method == "GET":
        return render_template("login.html")

    else:
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        rows = db.execute(
            "SELECT id, hash FROM users WHERE username = ?",
            request.form.get("username"),
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/change_pass", methods=["GET", "POST"])
@login_required
def change_pass():
    """Let Users Change passwords"""
    if request.method == "GET":
        return render_template("password.html")

    else:
        # Get form data
        old_pass = request.form.get("old_pass")
        new_pass = request.form.get("new_pass")

        # Check if form filled
        if not old_pass or not new_pass:
            return apology(
                "You must enter your old and new password to change your password"
            )

        db_pass = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])[
            0
        ]["hash"]
        # Check pass
        if not check_password_hash(db_pass, old_pass):
            return apology("Your old password doesn't match what you entered")

        # Update Password
        db.execute(
            "UPDATE users SET hash = ? WHERE id = ?",
            generate_password_hash(new_pass),
            session["user_id"],
        )

        flash("Password Changed Successfully")
        return redirect("/")
