import cv2
import numpy as np
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import pickle
import msxlt

def preProcess(crop):
    try:
        rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
    except:
        preProcess(crop)
    resize = cv2.resize(rgb, (224, 224))

    img_array = img_to_array(resize)
    process = preprocess_input(img_array)
    face = np.expand_dims(process, axis=0)
    return face

#------- This Function was created to identify my face --------------------------
# Use your model for the face recognition
def faceRecog(face):
    gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    ID, conf = recognise.predict(gray)##
    if conf >= 20 and conf <= 115:##
        print(ID)##
        print(labels[ID])##
        return str(labels[ID])

video = cv2.VideoCapture(0)

print("[INFO] Loading required packages..")
prototxtPath = "deploy.prototxt"
weightsPath = "res10_300x300_ssd_iter_140000_fp16.caffemodel"
net = cv2.dnn.readNetFromCaffe(prototxtPath, weightsPath)

print("[INFO] loading face mask detector model...")
model = load_model("mask_detect.model")

print("[INFO] loading face recognise model...")

#----------------- This code was used to load my face deetection trained model---------------
recognise = cv2.face.LBPHFaceRecognizer_create()#
recognise.read("trainner.yml")##
labels = {}##
with open("labels.pickle", 'rb') as f:##
    og_label = pickle.load(f)##
    labels = {v:k for k,v in og_label.items()}##
    print(labels)
#----------------------- You can neglet the code above ----------------------------
# Load your model and try it instead.


#----------- Loading the msxlt script and creating the document-------------------
xl = msxlt.XLC()
xl.create("Date,Time,Person Identified,Status","FMDlogging","Face Mask Detection data")


prev_label = None
prev_recog = None
flag = 0
    
while True:
    _, frame = video.read()
    h,w = frame.shape[:2]
    
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300),(104.0, 117.0, 123.0),False,False)
    print("[INFO] computing face detections...")
    net.setInput(blob)
    detections = net.forward()
    
    
    for i in range(0 , detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (x,y,W,H) = box.astype("int")
            #print("sx: ",x,"ex",w,"sy",y,"ey",h)

            crop = frame[y:H, x:W]
            face = preProcess(crop)
        
            (mask, withoutMask) = model.predict(face)[0]
            label = "Mask Detected" if mask > withoutMask else "No Mask Detected"
            color = (0,255,0) if label == "Mask Detected" else (0,0,255)

            if label == "No Mask Detected":
                if label == prev_label:
                    #recognise face
                    recog = faceRecog(crop)
                    print(type(recog))
                    cv2.putText(frame, label, (x,y-30), cv2.FONT_HERSHEY_SIMPLEX,0.6,
                            color,2)
                    try:
                        cv2.putText(frame, "Person Identified: "+recog, (x,y-10), cv2.FONT_HERSHEY_SIMPLEX,0.6,
                                color,2)
                        if flag == 0:
                            time, date = xl.time_date()
                            data = date+','+time+','+recog+','+label
                            xl.updateData(data,"FMDlogging")
                            flag = 1
                            print("data saved @ date {} time {}".format(date,time))
                    except TypeError:
                        pass
                    if recog != prev_recog:
                        flag = 0
                    prev_recog = recog
            elif label == "Mask Detected":
                cv2.putText(frame, label, (x,y-10), cv2.FONT_HERSHEY_SIMPLEX,0.6,
                            color,2)
                if prev_label == label:
                    flag = 0
            prev_label = label
            print("Flag =",flag)
            print("Previous Label =",prev_label)
            cv2.rectangle(frame,(x,y),(W,H),color,2)
            #cv2.imshow("crop",process)
    cv2.imshow("Output",frame)
    
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
