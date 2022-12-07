from flask import redirect, render_template, session
from functools import wraps
import cv2
import numpy as np
import os
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField
from flask_uploads import UploadSet, IMAGES

# Define valid video formats
VIDEOS = tuple("mp4 webm ogg avi mov mkv".split())

# same as finance
def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


# same as finance
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


# For future tensorflow model integration. Work in progress

# def prepare_image_for_detection(filepath):
#     img = tf.keras.preprocessing.image.load_img(filepath, target_size=(224, 224))
#     img_array = tf.keras.preprocessing.image.img_to_array(img)
#     expand_dims = np.expand_dims(img_array, axis=0)
#     return tf.keras.applications.mobilenet.preprocess_input(expand_dims)


def draw_boxes(
    image: np.ndarray,
    class_ids: np.ndarray,
    scores: np.ndarray,
    boxes: np.ndarray,
    class_dict: dict,
    detection_time_ms: float | None = None,
):
    """Draws boxes around detected objects"""
    # Define parameters for drawing.
    color = (150, 13, 165)
    font_size = 0.5
    stroke_thickness = 1

    # Go through each detection
    for (class_id, score, box) in zip(class_ids, scores, boxes):
        # create label
        label = "%s : %.2f" % (class_dict[class_id], score)

        # Put detection info on image itself
        cv2.rectangle(image, box, color, 2)
        cv2.putText(
            image,
            label,
            (box[0], box[1] - 10),
            cv2.FONT_HERSHEY_COMPLEX_SMALL,
            font_size,
            color,
            stroke_thickness,
        )

    # Work in progress, image detection time will also be printed via a setting in a settings tab
    if detection_time_ms:
        cv2.putText(
            image,
            str(detection_time_ms) + "ms",
            (10, 10),
            cv2.FONT_HERSHEY_COMPLEX_SMALL,
            font_size,
            color,
            stroke_thickness,
        )


# Create an upload form to accept images only
class ImageUploadForm(FlaskForm):
    photo = FileField(
        # Create validators 
        validators=[
            FileRequired("Please upload a file"),
            FileAllowed(UploadSet("photos", IMAGES), "Only image formats are allowed"),
        ]
    )
    submit = SubmitField("Upload")

# Create an upload form to accept videos only
class VideoUploadForm(FlaskForm):

    video = FileField(
        # Create validators 
        validators=[
            FileRequired("Please upload a file"),
            FileAllowed(
                UploadSet("videos", VIDEOS),
                f"Only {str(VIDEOS)} formats are allowed",
            ),
        ]
    )
    submit = SubmitField("Upload")

# Create a folder if it does not exist
def create_user_folder(user_id: int | str, root_dir: str):
    """Creates a user folder if one does not exist"""
    path = os.path.join(root_dir, str(user_id))
    if not os.path.isdir(path):
        os.mkdir(path)
