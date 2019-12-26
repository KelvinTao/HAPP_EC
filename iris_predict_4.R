##
print('step 4: classification by SVM model.')
##
args=commandArgs(T)
scriptPath=args[1]
resPath=args[2]
colorReadFile=args[3]
##quantified iris color statistics
colorStatPath=paste0(resPath,'/eye/colorStat')
colorStat=read.csv(paste0(colorStatPath,'/colorStat.csv'),stringsAsFactors=F)

###predict by base models
if(nchar(colorReadFile)<4){
  print('Predict by base SVM models')
  library(e1071)
  load(paste0(scriptPath,'/svm_basemodel.RData'))#load svm base model
  statPred=data.frame(side=colorStat[,1],colorStat[,2:4],class=predict(model,colorStat[,c('H_median','S_median','V_median')]))
  write.csv(statPred,file=paste0(resPath,'/eye/colorStat/eyecolor_prediction_basemodel.csv'),row.names=F,quote=F)
}else{
##Prediction after adding additional human read classes
  print('Predict after adding manual classifications.')
  library(e1071)
  ##manual classification
  colorRead=read.table(colorReadFile,head=T,stringsAsFactors=F)
  colorRead=colorRead[,c('photo','LeftInPhoto','RightInPhoto')]
  reads=as.vector(as.matrix(colorRead[,2:3]))
  imgNames=c(paste0(colorRead$photo,'.eye_leftSide'),paste0(colorRead$photo,'.eye_rightSide'))
  crUse=na.omit(data.frame(photo=imgNames,class=reads))
  statRead=merge(colorStat[,c('X','H_median','S_median','V_median')],crUse,by.x=1,by.y=1)
  statRead=statRead[,c(5,2:4)];names(statRead)[1]='y'
  ##data of base models
  data=read.table(paste0(scriptPath,'/eyecolor_model_base.txt'),head=T,stringsAsFactors=F)
  ###building models
  model=svm(y~.,data=rbind(data,statRead),type='C-classification')
  statPred=data.frame(side=colorStat[,1],colorStat[,2:4],class=predict(model,colorStat[,c('H_median','S_median','V_median')]))
  write.csv(statPred,file=paste0(resPath,'/eye/colorStat/eyecolor_prediction_addnewReference.csv'),row.names=F,quote=F)
}

print('Finish!')
##




