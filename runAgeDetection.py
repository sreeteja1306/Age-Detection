import numpy as np
import cv2
#from google.colab.patches import cv2_imshow    # cv.imshow() is known to crash Google Colab notebooks. This is the alternative suggested by Colab.
import os
from tensorflow import keras
os.environ["CUDA_VISIBLE_DEVICES"]="-1"
model = keras.models.load_model('age_detect_cnn_model.h5')

print("Start")


age_ranges = ['1-2', '3-9', '10-20', '21-27', '28-45', '46-65', '66-116']
ads={'1-2':'https://www.amazon.in/dp/B01NCX2VKN/',
     '3-9':'https://www.amazon.in/Max-Baby-Boys-Regular-T-Shirt-S21BBT08RED_RED/dp/B08S1CSQ82/',
     '10-20':"https://www.amazon.in/Clothe-Funn-T-Shirt-Embroidery-Combo/dp/B094NVR5CM",
     '21-27':"https://www.amazon.in/dp/B089MS8NW8",
     '28-45':"https://www.amazon.in/HP-Pentium-14-inch-Windows-14s-dq3018TU/dp/B0928S5XS2/",
     '46-65':"https://www.amazon.in/Amazon-Brand-Symbol-Regular-SS20-SYM-FS-01_EPP-1A_White/dp/B081QJRMW9/",
     '66-116':"https://www.amazon.in/PHYSIQO-%C2%AE-Walking-Stick-People-Wooden/dp/B07NJYQWR8/"
     }


face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")


def shrink_face_roi(x, y, w, h, scale=0.9):
    wh_multiplier = (1-scale)/2
    x_new = int(x + (w * wh_multiplier))
    y_new = int(y + (h * wh_multiplier))
    w_new = int(w * scale)
    h_new = int(h * scale)
    return (x_new, y_new, w_new, h_new)


# Defining a function to create the predicted age overlay on the image by centering the text.

def create_age_text(img, text, pct_text, x, y, w, h):

    # Defining font, scales and thickness.
    fontFace = cv2.FONT_HERSHEY_SIMPLEX
    text_scale = 1.2
    yrsold_scale = 0.7
    pct_text_scale = 0.65

    # Getting width, height and baseline of age text and "years old".
    (text_width, text_height), text_bsln = cv2.getTextSize(text, fontFace=fontFace, fontScale=text_scale, thickness=2)
    (yrsold_width, yrsold_height), yrsold_bsln = cv2.getTextSize("years old", fontFace=fontFace, fontScale=yrsold_scale, thickness=1)
    (pct_text_width, pct_text_height), pct_text_bsln = cv2.getTextSize(pct_text, fontFace=fontFace, fontScale=pct_text_scale, thickness=1)

    # Calculating center point coordinates of text background rectangle.
    x_center = x + (w/2)
    y_text_center = y + h + 20
    y_yrsold_center = y + h + 48
    y_pct_text_center = y + h + 75

    # Calculating bottom left corner coordinates of text based on text size and center point of background rectangle calculated above.
    x_text_org = int(round(x_center - (text_width / 2)))
    y_text_org = int(round(y_text_center + (text_height / 2)))
    x_yrsold_org = int(round(x_center - (yrsold_width / 2)))
    y_yrsold_org = int(round(y_yrsold_center + (yrsold_height / 2)))
    x_pct_text_org = int(round(x_center - (pct_text_width / 2)))
    y_pct_text_org = int(round(y_pct_text_center + (pct_text_height / 2)))

    face_age_background = cv2.rectangle(img, (x-1, y+h), (x+w+1, y+h+94), (0, 100, 0), cv2.FILLED)
    face_age_text = cv2.putText(img, text, org=(x_text_org, y_text_org), fontFace=fontFace, fontScale=text_scale, thickness=2, color=(255, 255, 255), lineType=cv2.LINE_AA)
    yrsold_text = cv2.putText(img, "years old", org=(x_yrsold_org, y_yrsold_org), fontFace=fontFace, fontScale=yrsold_scale, thickness=1, color=(255, 255, 255), lineType=cv2.LINE_AA)
    pct_age_text = cv2.putText(img, pct_text, org=(x_pct_text_org, y_pct_text_org), fontFace=fontFace, fontScale=pct_text_scale, thickness=1, color=(255, 255, 255), lineType=cv2.LINE_AA)

    return (face_age_background, face_age_text, yrsold_text)


# Defining a function to find faces in an image and then classify each found face into age-ranges defined above.

def classify_age(img):

    img_copy = np.copy(img)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(img_copy, scaleFactor=1.2, minNeighbors=6, minSize=(100, 100))
   
    cat_age=[]
   
    for i, (x, y, w, h) in enumerate(faces):

       
        face_rect = cv2.rectangle(img_copy, (x, y), (x+w, y+h), (0, 100, 0), thickness=2)
        
        
        x2, y2, w2, h2 = shrink_face_roi(x, y, w, h)
        face_roi = img_gray[y2:y2+h2, x2:x2+w2]
        face_roi = cv2.resize(face_roi, (200, 200))
        face_roi = face_roi.reshape(-1, 200, 200, 1)
        face_age=age_ranges[np.argmax(model.predict(face_roi))]
        if face_age not in cat_age:
            cat_age.append(face_age)
        
        
        face_age_pct = f"({round(np.max(model.predict(face_roi))*100, 2)}%)"
        
        
        face_age_background, face_age_text, yrsold_text = create_age_text(img_copy, face_age, face_age_pct, x, y, w, h)
       
    return img_copy,cat_age



img = cv2.imread("w.jpeg")
age_img= classify_age(img)
print(age_img[1])
for cat in age_img[1]:
    print(ads[cat])

cv2.imshow("Output",age_img[0])

cv2.waitKey(0) 
  

cv2.destroyAllWindows() 

my_video = "o.mp4"


cap = cv2.VideoCapture(my_video)

# Getting the video frame width and height.
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

count=0
# Defining the codec and creating a VideoWriter object to save the output video at the same location.
while(cap.isOpened()):
    
    # Grabbing each individual frame, frame-by-frame.
    ret, frame = cap.read()
    
    if ret==True:
        frame=cv2.resize(frame, (500, 500))
        # Running age detection on the grabbed frame.
        age_img= classify_age(frame)
        
        if(count==0):
            try:
              for cat in age_img[1]:
                  print(ads[cat])
            except KeyError:
              pass
            count=1
        cv2.imshow("Video_out",age_img[0])
        if cv2.waitKey(25) & 0xFF == ord('q'):
            ret=False
            cv2.destroyAllWindows()
            break


    else:
        ret=False
        break

# Releasing the VideoCapture and VideoWriter objects.
cap.release()

cap1 = cv2.VideoCapture(0)

# Getting the video frame width and height.
frame_width = int(cap1.get(3))
frame_height = int(cap1.get(4))

count=0
while(cap1.isOpened()):
    
    # Grabbing each individual frame, frame-by-frame.
    ret, frame = cap1.read()
    frame=cv2.resize(frame, (500, 500))
    
    if ret==True:
        # Running age detection on the grabbed frame.
        age_img = classify_age(frame)
        if(count==0):
            try:
              for cat in age_img[1]:
                  print(ads[cat])
            except KeyError:
              pass
            count=1
        
        cv2.imshow("Video_out",age_img[0])
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

        
        
        # Saving frame to output video using the VideoWriter object defined above.
        #out.write(age_img[0])

    else:
        break

# Releasing the VideoCapture and VideoWriter objects.
cap1.release()


