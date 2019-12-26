# HAPP_EC

# HAPP_EC, Human Appearance Phenotyping from Photos: Eye Color.

Created by Xianming Tao, 2019.08

# Introduction
HAPP_EC is a program to automatically quantify and classify eye color from human portrait photos. It is based on the face detection, landmark location, iris segmentation and support vector machine (SVM) classification.
HAPP_EC is freely available for free non-commercial use, and may be redistributed under these conditions. For commercial queries, contact Xianming Tao, taoxianming@big.ac.cn or xianming_tao@163.com.

# Installation
In our experiment, all the codes are tested Python 2.7 and R 3.3.
Modules needed in Python: Dlib (version 19.7.99 here), numpy (version 1.13.3), skimage(0.13.1), Pillow (version 4.3.0), opencv-python (version 3.1.0).
Packages needed in R: imager, e1071.

# Usage
Change setup in the HAPP_EC/config.ini file.
1. picPath is the full directory path of facial photos (jpg or png format).
2. If you have manual classified eye colors and want use them as a part of reference, then write the results in the format of humanRead_reference/eyecolor_read_examples.txt and give its path to humanRead_refFile. if not, humanRead_refFile=‘’
3. resPath is the place where you want to save the result.
4. Run command ‘python run.py’ in the folder HAPP_EC or 'python path_to/HAPP_EC/run.py' to run the whole pipeline.

# Get results
The results are saved in resPath set at the HAPP_EC/config.ini (eyecolor_result as an example).
Folder eyecolor_result/eye/pic includes eyes cut from images.
Folder eyecolor_result/eye/loc shows iris segmentation details and images of *.use.PNG are used to quantify eye color. 
Folder eyecolor_result/eye/colorStat includes eye color quantification file colorStat.csv—medians and means of HSV and RGB, and classification file eyecolor_prediction*.csv-automated classification by medians of HSV. eyecolor_prediction_basemodel.csv is classified by default SVM models. eyecolor_prediction_addnewReference.csv is classified after adding new manual classifications.

