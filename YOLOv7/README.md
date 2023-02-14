# **YOLOv7**

<p align="center">
  <img src="https://user-images.githubusercontent.com/107953645/218757394-a40561d7-e3c8-4bd7-bedc-dec03198c467.jpg" />
</p>

This project is for detecting persian license plates and read them.

This project is based on YOLOv7 and uses two different models one for detecting the license plates and one to perform OCR on the plates.

The biggest challenge during this project was dealing with googel colaboratory since it is not designed for unsupervised 24/7 operation which made me spend a long time on training the models.

With special thanks to miss Maryam Sadeghi for their wonderful tutorials.

> ## **Table of content:**
> *   deployment.ipynb : Notebook for implementing the trained models.
> *   training.ipynb : Notebook for training models for object detection.
> *   character.pt : YOLOv7 model for OCR.
> *   plate.pt : YOLOv7 model for plate detection.
> *   requirements.txt : List of YOLOv7 required libraries.
> *   test_imgs : A folder containing some test images.
> *   models : A folder containing source codes from original YOLOv7 project.  
> *   utils : A folder containing source codes from original YOLOv7 project.

# **TO USE THIS PROJECT JUST OPEN deployment.ipynb AND RUN THE CODE**
