// I use the prettier extension to format javascript.
// declare global variable
let video = null; // video element
let detector = null; // detector object
let detections = []; // store detection result
let videoVisibility = true;
let detecting = false;

// global HTML element
const toggleDetectingOnOff = document.getElementById("toggleDetectingOnOff");

// set cursor to wait until video elment is loaded
document.body.style.cursor = "wait";

// The preload() function is called before the setup() function
function preload() {
	// create detector object from "cocossd" model
	detector = ml5.objectDetector("cocossd");
	console.log("detector object is loaded");
}

// The setup() function is called once when the program starts.
function setup() {
	// create canvas with 640 width and 480 height
	canvas = createCanvas(640, 480);
	// Creates a new HTML5 <video> element that contains the audio/video feed from a webcam.
	// The element is separate from the canvas and is displayed by default.
	video = createCapture(VIDEO);
	video.size(640, 480);

	// Don't show the raw video, we're just showing the processed version
	video.hide();
	console.log("video element is created");
	video.elt.addEventListener("loadeddata", function () {
		// set cursor back to default
		if (video.elt.readyState >= 2) {
			document.body.style.cursor = "default";
			console.log("Video Ready to Begin");
		}
	});
}

function saveImage() {
	save("image.png");
}

function draw() {
	if (!video || !detecting) return;
	// draw video frame to canvas and place it at the top-left corner
	image(video, 0, 0);
	// draw all detections to the canvas
	for (let i = 0; i < detections.length; i++) {
		drawResult(detections[i]);
	}
}

function drawResult(object) {
	drawBoundingBox(object);
	drawLabel(object);
}

// draw bounding box around the detected object
function drawBoundingBox(object) {
	// Sets the color used to draw lines.
	stroke("green");
	// width of the stroke
	strokeWeight(2);
	// Disables filling geometry
	noFill();
	// draw an rectangle
	// x and y are the coordinates of upper-left corner, followed by width and height
	rect(object.x, object.y, object.width, object.height);
}

// draw label of the detected object (inside the box)
function drawLabel(object) {
	// Disables drawing the stroke
	noStroke();
	// sets the color used to fill shapes
	fill("white");
	// set font size
	textSize(24);
	// draw string to canvas
	text(object.label, object.x + 10, object.y + 24);
}

// callback function. it is called when object is detected
function onDetected(error, results) {
	if (error) {
		console.error(error);
	}
	detections = results;
	// keep detecting object
	if (detecting) {
		detect();
	}
}

function detect() {
	// instruct "detector" object to start detect object from video element
	// and "onDetected" function is called when object is detected
	detector.detect(video, onDetected);
}

function toggleDetecting() {
	if (!video || !detector) return;
	if (!detecting) {
		detect();
		toggleDetectingOnOff.innerText = "Pause Detecting";
		toggleDetectingOnOff.setAttribute("class", "btn btn-success");
	} else {
		toggleDetectingOnOff.innerText = "Start Detecting";
		toggleDetectingOnOff.setAttribute("class", "btn btn-primary");
	}
	detecting = !detecting;
}
