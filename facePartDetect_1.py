######necessary module
import sys,os,dlib,glob,cv2
import numpy as np
from skimage import io,transform#,draw
#from PIL import Image,ImageDraw#for add numer on image
import time#for calculate time
import mod_config

def shrinkImg(img0,shrink):
    img=np.uint8(np.around(transform.resize(img0,(round(img0.shape[0]*shrink),
        round(img0.shape[1]*shrink)),mode='constant')*255))
    return(img)

def getRectLandmark(img,detector,predictor):
    #upsample the image 1 time
    dets = detector(img,1)
    for d in dets:
        #get rectangle line
        rect=[d.top(),d.bottom(),d.left(),d.right()]
        # get the landmarks/parts for the face in box d
        shape = predictor(img, d)  #np.mat(shape.parts())
        landmarks=np.mat([[points.x,points.y] for points in shape.parts()])
    return([rect,landmarks])
'''
def getMarksImg(img,rect,landmarks):
    ##draw face rectangle on the image
    rr,cc = draw.polygon_perimeter([rect[0],rect[0],rect[1],rect[1]],[rect[3],rect[2],rect[2],rect[3]])
    img[rr-1,cc-1] = (255, 0, 0)
    ##draw landmarks circle on the image
    for rc in landmarks:
       lr,lc = draw.circle_perimeter(rc[0,1],rc[0,0],2)##y,x,radius
       img[lr,lc] = (0, 255, 0)
    return(img)
def drawRect(img,rect):
    ##draw face rectangle on the image
    rr,cc = draw.polygon_perimeter([rect[0],rect[0],rect[1],rect[1]],[rect[3],rect[2],rect[2],rect[3]])
    img[rr-1,cc-1] = (255, 0, 0)
    return(img)

def drawLandmarks(img,landmarks):
    ##draw landmarks circle on the image
    for rc in landmarks:
       lr,lc = draw.circle_perimeter(rc[0,1],rc[0,0],2)##y,x,radius
       img[lr,lc] = (0, 255, 0)
    return(img)

def addNumOnImg(markFile,landmarks):
    ##add landmarks NO at the corresponding point
    imgNO = Image.open(markFile)
    imgdraw = ImageDraw.Draw(imgNO)
    for NO,rc in enumerate(landmarks):
        NO=NO+1 #from 1
        imgdraw.text((rc[0,0],rc[0,1]),str(NO),fill=(255,0,0))
    return(imgNO)
'''

def cut(img0,landmarks,shrink,partIndex,part):
    ##original position
    oriMarks=np.around(landmarks/shrink).astype(int)
    ##get corresponding landmarks
    index=partIndex[part].split('-')
    marks=oriMarks[int(index[0]):int(index[1]),]
    top=np.amin(marks[:,1]);down=np.amax(marks[:,1])
    left=np.amin(marks[:,0]);right=np.amax(marks[:,0])
    ###jump
    jumpRatio=0.15  ###need another jump methods
    if part.split('_')[0]=='eye':
        jumpRatio=0.3
    jumpVertical=int((down-top)*jumpRatio);
    jumpHorizonal=int((right-left)*jumpRatio);
    ##original cut part
    oriCut=img0[top-jumpVertical:down+jumpVertical,
        left-jumpHorizonal:right+jumpHorizonal,]
    return([oriCut,[int(top*shrink),int(down*shrink),int(left*shrink),int(right*shrink)]])


def mkdir(mkpath):
    if not os.path.exists(mkpath):
        os.makedirs(mkpath)

def main():
    ###
    print('step 1: cut eyes from portrait photos.')
    landmarksRef=sys.path[0]+'/shape_predictor_68_face_landmarks.dat'
    path=mod_config.getConfig("path", "resPath")
    oriImgpath=mod_config.getConfig("path", "picPath") ##input images directory
    ###
    mkdir(path+'/landmarks')
    #mkdir(path+'/mark')
    mkdir(path+'/eye/pic');
    ##instantiation
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(landmarksRef)
    ###part and index
    ##for eye: 36-41,left part; 42-47, right part; from index 0
    partIndex={'eye_left':'36-42','eye_right':'42-48'}
    #####start
    imgFiles=os.listdir(oriImgpath)
    imgs=[]
    for img in imgFiles:
        img2=img.lower()
        if img2.endswith('png') or img2.endswith('jpg') or img2.endswith('jpeg') :
            imgs.append(img)
    shrink=0.3#1for unclear pictures,0.3 for clear pictures
    for n,fName in enumerate(imgs):
        try:
            print("Processing: {}".format(fName))
            time_start=time.time()
            #####start
            #img0 = io.imread(oriImgpath+'/'+fName)
            img0 = cv2.imread(oriImgpath+'/'+fName)
            img=shrinkImg(img0,shrink)
            ##give warnings for too dark images
            img_gray = cv2.cvtColor(img0,cv2.COLOR_BGR2GRAY) 
            if img_gray.mean()<50 or img_gray.mean()>200 :
                print('Warning: '+fName+' is too dark or too bright!')
            rect,landmarks=getRectLandmark(img,detector,predictor)
            ###landmarks save
            oriMarks=np.around(landmarks/shrink).astype(int)# in case of outside
            oriMarksFile=(path+'/landmarks/{}.landmarks.txt').format(fName)
            np.savetxt(oriMarksFile,oriMarks,delimiter='\t',fmt='%d')
            ## cut regions
            for part in partIndex:
                partImg=cut(img0,landmarks,shrink,partIndex,part)
                #mkdir(path+'/'+part.split('_')[0])
                cutFile=(path+'/{}/pic/{}.{}.PNG').format(part.split('_')[0],fName,part)
                #io.imsave(cutFile,partImg[0])
                cv2.imwrite(cutFile,partImg[0])
                #img=drawRect(img,partImg[1])
            ###draw marks on face
            '''
            img=drawRect(img,rect)
            img=drawLandmarks(img,landmarks)
            markFile=(path+'/mark/{}.shrink{}.JPG').format(fName,shrink)
            io.imsave(markFile,img)
            ############ add landmark number
            ifAddNO=False
            if ifAddNO:
                imgNO=addNumOnImg(markFile,landmarks)
                imgNO.save(markFile+'.NO.JPG')
            '''
            #############
            print(str(time.time()-time_start)+' seconds.')
        except Exception as e:
            print(e)
            print("error")
            continue

if __name__ == '__main__':
    main()
    ##iamge display
    #io.imshow(img);io.show();
