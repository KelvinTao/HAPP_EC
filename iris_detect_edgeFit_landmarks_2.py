import sys,os,cv2
import numpy as np
import mod_config

def mkdir(mkPath):
	if not os.path.exists(mkPath):
		os.makedirs(mkPath)

def getPos(lms,side,sideLms):
	leftPoint=lms[sideLms[side][0]].split('\t')
	lpPos=[int(leftPoint[0]),int(leftPoint[1])]
	rightPoint=lms[sideLms[side][1]].split('\t')
	rpPos=[int(rightPoint[0]),int(rightPoint[1])]
	return([lpPos,rpPos])

def getCondition(light,iris,minus):
	if (light>90 and iris <30) or (light>150 and iris <35) or (light>200 and iris <45):
		condition='strong-dark';# 57,15#
		irisThresh=57;pupilThresh=15;pad=8;
	elif (light<90 and iris<20):#<=20
		condition='weak-dark';# 57,15
		irisThresh=57;pupilThresh=10;pad=8;
	else:
		condition='shallow';# 57,15
		pupilThresh=15;irisThresh=93;pad=0;#90
	return([irisThresh,pad,pupilThresh,condition])

def getColor(picName,picPath,locPath,lmPath):
	##get landmarks for detail location
	lmFile=lmPath+picName[0:picName.find('eye')]+'landmarks.txt'
	side=picName[(picName.find('_')+1):picName.find('.PNG')]
	locFile=locPath+picName.replace('PNG','loc.PNG')
	locGFile=locPath+picName.replace('PNG','loc.gray.PNG')
	useFile=locPath+picName.replace('PNG','use.PNG')	
	lms=open(lmFile).read().split('\n')
	sideLms = {'left':np.array([37,40])-1,'right':np.array([43,46])-1};
	lpPos,rpPos=getPos(lms,side,sideLms)
	##read picture
	picFile=picPath+picName
	img0 = cv2.imread(picFile)
	#cv2.imshow('eye', img0)
	##cut
	jumpRatio=0.4  #0.3 in face detection process
	length=rpPos[0]-lpPos[0];wgap=int(length*jumpRatio)
	[h,w,color]=img0.shape;
	upRatio=0.15;downRatio=0.1;up0=int(h*upRatio);
	img=img0[up0:int(h-h*downRatio),wgap:w-wgap]
	imgI=np.copy(img);
	#cv2.imshow('eye_use', imgI)
	##bring gray to 0-255
	img_gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	img_gray0=img_gray.copy()
	##get landmarks for detail location and conditions of eye
	##get irisThresh,pad,pupilThresh
	lms2=np.loadtxt(lmFile);
	sideLms0 = {'left':np.array(range(37,43))-1,'right':np.array(range(43,49))-1};
	sideLmsIn0 = {'left':np.array([38,39,41,42])-1,'right':np.array([44,45,47,48])-1};
	marks=lms2[sideLms0[side],];
	jumpRatio0=0.3;
	left=min(marks[:,0]);right=max(marks[:,0]);top=min(marks[:,1]);down=max(marks[:,1]);
	jumpHorizonal=int((right-left)*jumpRatio0);jumpVertical=int((down-top)*(jumpRatio0));
	marksIn=lms2[sideLmsIn0[side],];
	marksIn[:,0]=marksIn[:,0]-left+jumpHorizonal-wgap;
	marksIn[:,1]=marksIn[:,1]-top+jumpVertical-up0;
	tdJumpRatioT=0.1;tdJumpRatioD=0.05;tdJumpRatioL=0.05;tdJumpRatioR=0.05;
	leftIn=(min(marksIn[:,0])-(right-left)*tdJumpRatioL).astype(int);
	rightIn=(max(marksIn[:,0])+(right-left)*tdJumpRatioR).astype(int);#+
	topIn=(min(marksIn[:,1])+(down-top)*tdJumpRatioT).astype(int);
	downIn=(max(marksIn[:,1])-(down-top)*tdJumpRatioD).astype(int);
	leftIn4=(min(marksIn[:,0])+(right-left)*tdJumpRatioL).astype(int);
	rightIn4=(max(marksIn[:,0])-(right-left)*tdJumpRatioR).astype(int);#+
	gray4Thresh=img_gray0[topIn:downIn,leftIn4:rightIn4]
	light=np.percentile(img_gray0[topIn:downIn,leftIn:rightIn],95)
	iris=np.median(gray4Thresh)
	minus=np.mean(img_gray0)-iris
	irisThresh,pad,pupilThresh,condition=getCondition(light,iris,minus)
	pupil=np.percentile(img_gray,pupilThresh)
	if condition=='shallow':
		###
		topIn=(min(marksIn[:,1])+(down-top)*0.2).astype(int);#0.2
		downIn=(max(marksIn[:,1])-(down-top)*0.1).astype(int);#0.1
		rightIn4=(max(marksIn[:,0])-(right-left)*0.1).astype(int);#0.1
		img_grayUse=np.copy(img_gray);img_grayUse=img_grayUse[topIn:downIn,leftIn4:rightIn4];
		irisUse=np.percentile(img_grayUse,irisThresh)
		imgUse=np.copy(imgI);imgUse=imgUse[topIn:downIn,leftIn4:rightIn4];
		[h,w]=img_grayUse.shape;
		for xi in range(0,h):
			for yi in range(0,w):
				x=xi+topIn;y=yi+leftIn4;
				if img_grayUse[xi,yi]<irisUse and img_grayUse[xi,yi]>pupil:#white
					img_gray[x,y]=255
					img[x,y,1]=255
				else:
					imgUse[xi,yi,:]=255
		cv2.imwrite(locFile,np.hstack([imgI,img]))
		cv2.imwrite(locGFile,img_gray)
		cv2.imwrite(useFile,imgUse)	

    #########
	##removing pupil
	else:
		ret, closed2 = cv2.threshold(img_gray,pupil,255,cv2.THRESH_BINARY_INV)
		kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))#88
		closed2 = cv2.morphologyEx(closed2, cv2.MORPH_CLOSE, kernel)
		#cv2.imshow('removed pupil',closed2)
		mid=np.percentile(img_gray,irisThresh)#mid=np.mean(img_gray)##57
		ret, closed = cv2.threshold(img_gray,mid,255,cv2.THRESH_BINARY_INV)
		binary0=closed
		##fill middle
		kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (pad, pad))#88
		closed = cv2.morphologyEx(closed, cv2.MORPH_CLOSE, kernel)
		# perform a series of erosions and dilations
		closed = cv2.erode(closed, None, iterations=1)
		closed = cv2.dilate(closed, None, iterations=1)
		#cv2.imshow("filled binary", closed)
		##search edges##
		canny = cv2.Canny(closed, 254, 254)
		canny = np.uint8(np.absolute(canny))
		#cv2.imshow("edge", canny)
		[h,w,color]=img.shape;
		##split to 3 parts
		sideLmsIn={'left':np.array([38,41])-1,'right':np.array([44,47])-1};
		lpPos2,rpPos2=getPos(lms,side,sideLms)
		yCenter=int((rpPos2[0]+lpPos2[0])/2-lpPos[0]+0.3*length-jumpRatio*length)
		hdratio = 0.2;huratio=0.2;# if w/h>1.75 else 0.25
		xBottom=int(round(h*(1-hdratio)))
		xUp=int(round(h*huratio))
		##get iris edge: find first meet x left and right
		edgeL=[];edgeR=[]
		for x in range(xBottom,xUp,-1):
			for y in range(yCenter,1,-1):
				if canny[x,y]==0 and canny[x,y-1]==255:
					edgeL.append([x,y])
					img_gray[x,y]=125
					break
			for y in range(yCenter,int(w)-1):
				if canny[x,y-1]==0 and canny[x,y]==255:
					edgeR.append([x,y])
					img_gray[x,y]=125
					break
		##get new yCenter by edgeL and edgeR
		##same x, get pair y
		eLdic={edgeL[i][0]:edgeL[i][1] for i in range(0,len(edgeL))}
		eRdic={edgeR[i][0]:edgeR[i][1] for i in range(0,len(edgeR))}
		edgePair=[[eLdic[key],eRdic[key]] for key in list(set(eLdic.keys()).intersection(set(eRdic.keys())))]
		yCenter=np.array(edgePair).mean()
		##circle fit along ycenter by edges
		edges=edgeL;edges.extend(edgeR);edges=np.array(edges)
		topRatio=0.2;downRatio=0.66;##3366
		xUp=int(h*topRatio);xDown=int(h*downRatio);
		dists=[]
		for x in range(xUp,xDown+1):
			dist=0
			for i in range(0,edges.shape[0]):
				dist=dist+(edges[i,0]-float(x))**2+(edges[i,0]-yCenter)**2
			dists.append([x,dist])
		dists=np.array(dists)
		xCenter=dists[dists[:,1].argmin(),0]
		img_gray[int(xCenter),:]=255;
		img_gray[:,int(yCenter)]=255;
		##plot and get img color:H[0,179],S[0,255],V[0,255]
		imgUse=np.copy(img);
		r=max((rightIn-leftIn)/2,(downIn-topIn)/2)
		#print(pupil)
		#########
		#HSV=[];img_hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
		for xi in range(0,h):
			for yi in range(0,w):
				dist=((xi-xCenter)**2+(yi-yCenter)**2)**0.5
				#print(dist)#
				if dist<=r  and binary0[xi,yi]==255 and closed2[xi,yi]<255:
					img_gray[xi,yi]=255
					if  xi>topIn and xi<downIn and yi>leftIn and yi<rightIn:
						img[xi,yi,1]=255
					else:
						imgUse[xi,yi,:]=255
				else:
					imgUse[xi,yi,:]=255
		img_gray[topIn,:]=255;img_gray[downIn,:]=255;img_gray[:,leftIn]=255;img_gray[:,rightIn]=255;
		###save images
		cv2.imwrite(locFile,np.hstack([imgI,img,imgUse]))
		cv2.imwrite(locGFile,np.hstack([img_gray0,binary0,closed2,closed,canny,img_gray]))
		cv2.imwrite(useFile,imgUse)

'''
initial eye: img0
eye after cut: imgI
initial gray: img_gray0
initial target region: binary0
removed pupil region: closed2
filled target region: closed
ege of filled target region: canny
ciecle fit result of initial gray: img_gray
used green part on eye after cut: img
imaged used for extract color: imgUse
'''

print('step 2: iris segmentation.')
path=mod_config.getConfig("path", "resPath")
picPath=path+'/eye/pic/';
locPath=path+'/eye/loc/';mkdir(locPath)
##get landmarks for detail location
lmPath=path+'/landmarks/'
picNames=os.listdir(picPath)
for i,picName in enumerate(picNames):
	try:
		#print(i)
		if picName.endswith('PNG'):
			print(picName)
			getColor(picName,picPath,locPath,lmPath)
			#if i>300:
				#break
	except Exception as e:
		print(e)
		print("error")
		continue


