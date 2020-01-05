# IOT_project: 指引系統
透過鏡頭及物件偵測模型判斷人們的主要行徑方向或排隊多寡，並透過告示牌指引人們至人數較少的方向，分散人流。使用者可透過網頁手動或自動控制告示牌。

所需材料：  
樹莓派* 1  
鏡頭* 1   
伺服馬達(可控角度)* 1  
Intel neural compute stick 2* 1  
杜邦線(公對母)* 1  
紙箱  
膠帶  

# 步驟一：安裝openVino
__注意不要使用python3.6__  
參考教學：https://docs.openvinotoolkit.org/latest/_docs_install_guides_installing_openvino_raspbian.html#install-package  
Go to the directory in which you downloaded the OpenVINO toolkit.  
```
cd ~/Downloads/
```
Create an installation folder
```
sudo mkdir -p /opt/intel/openvino
```
Unpack the archive:
```
sudo tar -xf  l_openvino_toolkit_runtime_raspbian_p_<version>.tgz --strip 1 -C /opt/intel/openvino
```
Set the Environment Variables
```
echo "source /opt/intel/openvino/bin/setupvars.sh" >> ~/.bashrc
```
## 測試模型
使用模型：person-detection-retail-0013  
參考網址：https://docs.openvinotoolkit.org/2018_R5/_docs_Retail_object_detection_pedestrian_rmnet_ssd_0013_caffe_desc_person_detection_retail_0013.html  
參考程式碼：personDetection.py
