#encoding:utf-8
import os,sys,ConfigParser,mod_config
##cut eyes
scriptPath=sys.path[0]
os.system('python '+scriptPath+'/facePartDetect_1.py')
##iris segmentation
os.system('python '+scriptPath+'/iris_detect_edgeFit_landmarks_2.py')
##quantification and classification
resPath=mod_config.getConfig("path", "resPath")
colorReadFile=mod_config.getConfig("path", "humanRead_refFile") 
##iris color statistics
os.system(' '.join(('Rscript',scriptPath+'/iris_HSVandStat_3.R',resPath)))
##iris color classification by SVM
os.system(' '.join(('Rscript',scriptPath+'/iris_predict_4.R',scriptPath,resPath,colorReadFile)))
##
