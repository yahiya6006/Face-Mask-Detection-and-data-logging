import cv2
import numpy as np
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model

video = cv2.VideoCapture(0)

prototxtPath = "deploy.prototxt"
weightsPath = "res10_300x300_ssd_iter_140000_fp16.caffemodel"
net = cv2.dnn.readNetFromCaffe(prototxtPath, weightsPath)

print("[INFO] loading face mask detector model...")
model = load_model("mask_detect.model")

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
            rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
            resize = cv2.resize(rgb, (224, 224))

            img_array = img_to_array(resize)
            process = preprocess_input(img_array)
            face = np.expand_dims(process, axis=0)

            (mask, withoutMask) = model.predict(face)[0]
            label = "Mask Detected" if mask > withoutMask else "No Mask Detected"
            color = (0,255,0) if label == "Mask Detected" else (0,0,255)
            cv2.putText(frame, label, (x,y-10), cv2.FONT_HERSHEY_SIMPLEX,0.6,
                        color,2)
            cv2.rectangle(frame,(x,y),(W,H),color,2)
            #cv2.imshow("crop",process)
    cv2.imshow("Output",frame)
    
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
