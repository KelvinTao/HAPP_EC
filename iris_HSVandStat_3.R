##
print('step 3: iris color ststistics.')
library(imager)
args=commandArgs(T)
resPath=args[1]
path=paste0(resPath,'/eye')
#hsvPath=paste0(path,'/hsv')
colorStatPath=paste0(path,'/colorStat')
dir.create(colorStatPath);
files=Sys.glob(paste0(path,'/loc/*.use.PNG'))
###
hsvStat=NULL##HSV statistics
rgbStat=NULL##RGB statistics
okFile=NULL
#noFile=NULL
getMedian<-function(imgHsv){
    stat=as.vector(apply(imgHsv,2,median))
    names(stat)=c('H_median','S_median','V_median')
    return(stat)
}
getMean<-function(imgHsv){
    stat=as.vector(apply(imgHsv,2,mean))
    names(stat)=c('H_mean','S_mean','V_mean')
    return(stat)
}

for(fi in 1:length(files)){
    img=load.image(files[fi])#0-1 for r g b
    ##gray for search
    imgGray=grayscale(img);errorRate=0.99;#plot(imgGray)
    index=imgGray<=1*errorRate # filter points of no white
    ##RGB and HSV statistics
    imgRgb=img[index];
    imgHsv=RGBtoHSV(img)[index]
    number=length(imgHsv)/3
    if (number>0){
        print(fi)
        #####statistics
        imgRgb=cbind(imgRgb[1:number],imgRgb[(number+1):(number*2)],imgRgb[(number*2+1):(number*3)])
        Median=getMedian(imgRgb);names(Median)=c('R_median','G_median','B_median')
        Mean=getMean(imgRgb);names(Mean)=c('R_mean','G_mean','B_mean')
        rgbStat=rbind(rgbStat,c(Median,Mean))
        ##
        imgHsv=cbind(imgHsv[1:number],imgHsv[(number+1):(number*2)],imgHsv[(number*2+1):(number*3)])
        hsvStat=rbind(hsvStat,c(getMedian(imgHsv),getMean(imgHsv)))
        okFile=c(okFile,fi)
    }else{
        #noFile=c(noFile,fi)#print(number)
        print(files[fi])
    }
}
statAll=cbind(hsvStat,rgbStat)
rownames(statAll)=gsub(paste0(path,'/loc/'),'',files)[okFile]
rownames(statAll)=gsub('.use.PNG','Side',rownames(statAll))
statAll=round(statAll,4)
write.csv(statAll,paste0(colorStatPath,'/colorStat.csv'),quote=F)


