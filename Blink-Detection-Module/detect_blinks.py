# import the necessary packages
from scipy.spatial import distance as dist
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils import face_utils
import argparse
import imutils
import time
import dlib
import cv2
from selenium import webdriver
import webbrowser
import time

def nextButton(id):
    tempArr=id.split('_')
    tempNum=int(tempArr[1])
    tempNum+=1
    if tempNum>5:
        tempNum%=5
    id=tempArr[0]+'_'+str(tempNum)
    return id

driver = webdriver.Chrome("C:/webdrivers/chromedriver")
driver.get("http://127.0.0.1:3000/index.html")
time.sleep(2)
id='button_1'
driver.execute_script(f'document.getElementById("{id}").style.border="thick solid black"')

def eye_aspect_ratio(eye):
	# compute the euclidean distances between the two sets of
	# vertical eye landmarks (x, y)-coordinates
	A = dist.euclidean(eye[1], eye[5])
	B = dist.euclidean(eye[2], eye[4])

	# compute the euclidean distance between the horizontal
	# eye landmark (x, y)-coordinates
	C = dist.euclidean(eye[0], eye[3])

	# compute the eye aspect ratio
	ear = (A + B) / (2.0 * C)

	# return the eye aspect ratio
	return ear
 
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--shape-predictor",default="Blink-Detection-Module\shape_predictor_68_face_landmarks.dat",
	help="path to facial landmark predictor")
ap.add_argument("-v", "--video", type=str, default="camera",
	help="path to input video file")
ap.add_argument("-t", "--threshold", type = float, default=0.27,
	help="threshold to determine closed eyes")
ap.add_argument("-f", "--frames", type = int, default=2,
	help="the number of consecutive frames the eye must be below the threshold")

def main() :
    global id
    args = vars(ap.parse_args())
    EYE_AR_THRESH = args['threshold']
    EYE_AR_CONSEC_FRAMES = args['frames']

    # initialize the frame counters and the total number of blinks
    COUNTER = 0
    TOTAL = 0

    # initialize dlib's face detector (HOG-based) and then create
    # the facial landmark predictor
    print("[INFO] loading facial landmark predictor...")
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(args["shape_predictor"])
 
    # grab the indexes of the facial landmarks for the left and
    # right eye, respectively
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
    
    # start the video stream thread
    print("[INFO] starting video stream thread...")
    print("[INFO] print q to quit...")
    if args['video'] == "camera":
        vs = VideoStream(src=0).start()
        fileStream = False
    else:
        vs = FileVideoStream(args["video"]).start()
        fileStream = True
   
    time.sleep(1.0)
    
    # loop over frames from the video stream
    while True:
    	# if this is a file video stream, then we need to check if
    	# there any more frames left in the buffer to process
    	if fileStream and not vs.more():
    		break
    
    	# grab the frame from the threaded video file stream, resize
    	# it, and convert it to grayscale
    	# channels)
    	frame = vs.read()
    	frame = imutils.resize(frame, width=450)
    	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    	# detect faces in the grayscale frame
    	rects = detector(gray, 0)
    	start = time.time()
    	# loop over the face detections
    	for rect in rects:
    		# determine the facial landmarks for the face region, then
    		# convert the facial landmark (x, y)-coordinates to a NumPy
    		# array
    		shape = predictor(gray, rect)
    		shape = face_utils.shape_to_np(shape)

    		#start = time.time()
    		# extract the left and right eye coordinates, then use the
    		# coordinates to compute the eye aspect ratio for both eyes
    		leftEye = shape[lStart:lEnd]
    		rightEye = shape[rStart:rEnd]
    		leftEAR = eye_aspect_ratio(leftEye)
    		rightEAR = eye_aspect_ratio(rightEye)
    
    		# average the eye aspect ratio together for both eyes
    		ear = (leftEAR + rightEAR) / 2.0
    
    		# compute the convex hull for the left and right eye, then
    		# visualize each of the eyes
    		leftEyeHull = cv2.convexHull(leftEye)
    		rightEyeHull = cv2.convexHull(rightEye)
    		cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
    		cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
    		

			#Calculate for single_blink or double_blink
		
				

    		# check to see if the eye aspect ratio is below the blink
    		# threshold, and if so, increment the blink frame counter
    		if ear < EYE_AR_THRESH:
    			COUNTER += 1;#driver.execute_script(f'document.getElementById("{id}").style.border="thick solid red"');id=nextButton(id);driver.execute_script(f'document.getElementById("{id}").style.border="thick solid black"')
    			
    
    		# otherwise, the eye aspect ratio is not below the blink
    		# threshold
    		else:
    			# if the eyes were closed for a sufficient number of
    			# then increment the total number of blinks
    			if COUNTER >= EYE_AR_CONSEC_FRAMES+5:
    				TOTAL += 1;button = driver.find_element_by_id(id)
    				button.click()
    			elif COUNTER >= EYE_AR_CONSEC_FRAMES+2:
    				driver.execute_script(f'document.getElementById("{id}").style.border="thick solid black"');id=nextButton(id);driver.execute_script(f'document.getElementById("{id}").style.border="thick solid white"')


    
    			# reset the eye frame counter
				
    							
    			COUNTER = 0
    
    		# draw the total number of blinks on the frame along with
    		# the computed eye aspect ratio for the frame
    		cv2.putText(frame, "Blinks: {}".format(TOTAL), (10, 30),
    			cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    		cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
    			cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

			
     
    	# show the frame
    	cv2.imshow("Frame", frame)
    	key = cv2.waitKey(1) & 0xFF
     
    	# if the `q` key was pressed, break from the loop
    	if key == ord("q"):
    		break
    
    # do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()
if __name__ == '__main__' :
    main()
