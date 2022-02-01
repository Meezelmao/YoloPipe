# YoloPipe
 Detect defects on pipe surface. This is a research work within the university.
This script is designed to detect defects on the surface of a stainless tube and is used in production for online troubleshooting. 
For simultaneous viewing of the entire surface of the tube (360 degrees), 
3 Baumer machine vision cameras are used. 
<p align="center">
<img src="https://user-images.githubusercontent.com/90841085/151109489-99f96cbd-95f8-4c3b-a056-d5195a3965d2.jpg" width="400" height="300"/>
<p>
 <p align="center">
 Fig. 1. Cams using for detection.
 <p>
Images from all cameras enter the buffer, where they are processed one by one using an algorithm based on the Yolo 5 version.
This algorithm was trained on a sample of 200 images of various defects (dents, scratches, dirt, tint and other mechanical damage).
for user interaction, there is a human-machine interface that displays the image from the cameras with the ability to enable / disable YOLO processing.
Image processing is possible at a rate of about 15 frames/sec for each of the three cameras. 
All calculations are made on the Nvidia RTX 2060 super graphics card. Result of detection on Fig. 2.
<p align="center">
<img src="https://user-images.githubusercontent.com/90841085/151109563-70053de3-0e85-477d-ad9a-5235d075d4e9.png" width="400" height="300"/>
 <p>
<p align="center">
Fig. 2. Detection results
<p>
Due to the fact that the speed of the conveyor that passes the tube through the viewing device is about 5mm/sec, 
and the viewing area of the camera is about 3x5mm, the speed of 15 frames/sec is enough to detect defects in the images from all three cameras.
To achieve this speed, the YOLO5s structure was taken as the basis.
