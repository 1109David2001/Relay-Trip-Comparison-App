I have created an app to help relay protection engineers to quickly determine the state of change of differential current - OMICRON Electronics Technical Assistant.
Relay-Trip-Comparison APP Version 1（Version 1 is only for Line fault，Version 2 may include transfermoer and CT saturated）

This is a guide on how to use this app correctly and possible issues that may arise


1.The user needs to prepare a RIO document and COMTRADE file from the Relay：DAT and COMTRADE file
<img width="675" alt="image" src="https://github.com/1109David2001/Relay-Trip-Comparison-App/assets/155039981/8cdef3d3-7c22-472c-84d2-17eab438d0d7">

2.Users need to upload COMTRADE file before select current. COMTRADE file and DAT file should be uploaded separately. Due to differential protection, it is necessary to compare the current values of two Current Transformer/Relay. The user needs to upload two COMTRADE files separately (two COMTRADE files can be uploaded with the same or different values). Note that you have to upload the .COM file first, and then the .DAT file. After uploading, you can see the first five values in the COMTRADE data.
![image](https://github.com/1109David2001/Relay-Trip-Comparison-App/assets/155039981/8def43df-096e-4ca5-b740-55acfe1762f0)
![image](https://github.com/1109David2001/Relay-Trip-Comparison-App/assets/155039981/09bfb169-264b-45ac-8758-6465b06731dd)
<img width="673" alt="image" src="https://github.com/1109David2001/Relay-Trip-Comparison-App/assets/155039981/480de834-fc2d-4df6-a35d-0b626a5a0e8a">

3.The user needs to upload the RIO file which contains Relay's ideal Trigger curve. APP can automatically read the settings in RIO.
![image](https://github.com/1109David2001/Relay-Trip-Comparison-App/assets/155039981/aa4b4660-7de7-4959-9aeb-9ad9ff4926ea)

4.Show RIO file content can get all the data of RIO, if there is no data, it will show '---'.
![image](https://github.com/1109David2001/Relay-Trip-Comparison-App/assets/155039981/20e4a4cd-d7a2-43b3-a0ca-34c43f5dc17c)

5.After uploading the COMTRADE file, you need to choose to calculate the differential current; if you do not calculate the differential current, you will not be able to plot the real time change and real trip curve.
<img width="671" alt="image" src="https://github.com/1109David2001/Relay-Trip-Comparison-App/assets/155039981/aa097811-34e7-43a6-a089-a799c5e8bb81">
Section 1：data from CT A or Relay A.  Section 2：data from CT B or Relay B. 
The user must select three data with the same data length. (If it is from the same type of CT/Relay, there is no need to worry about the data length.) Otherwise the data structure may not be calculated
<img width="671" alt="image" src="https://github.com/1109David2001/Relay-Trip-Comparison-App/assets/155039981/8151371a-a965-4a18-b7e4-98e4495adc3b">

6.Idiff and Ibias have been calculated, RIO file has been uploaded, user can click 'show real time change' button, user can drag the timeline to find out the change of Differential current and Bias current in different time states. Users can drag the timeline to find out the changes of Differential current and Bias current in different time states. Trigger time' label in my app means the time when the Differential current is out of the normal state ('Trigger time' label in this case does not mean that the relay has been tripped, but the Current has entered the abnormal state, which may have generated a change in the current). has entered an abnormal state and may have generated a fault.)
![image](https://github.com/1109David2001/Relay-Trip-Comparison-App/assets/155039981/3787fab6-be5e-4100-b166-6b542620a9c6)

If you need a packaged programme, you can contact me at my email address. If there are ANY bugs or feedbacks you can contact me.
If you have any question，feel free to contact me david.zhang2@omicronenergy.com/yuzhe.zhang@connect.polyu.hk


