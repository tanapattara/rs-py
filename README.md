# Recommendation System
## การดึงข้อมูลรีวิวจาก Google Maps
สำหรับการดึงข้อมูลรีวิวสถานที่ที่มีใน Google Maps โดยใช้ chromedriver โดยเครืองต้องมีการติดตั้ง [Chrome Browser](https://www.google.com/intl/th_th/chrome/)
### ติดตั้งแพ็กเก็จสำหรับ Python
ที่ Terminal เรียกใช้คำสั่ง pip install ตามด้วย package เพื่อทำการติดตั้ง
 ```
 pip install selenium pandas lxml openpyxl bs4
 ```
### การทำงาน

1. ใส่ url ของสถานที่ที่ได้จาก Google map `data/placelist.csv` โดยสถานที่แต่ละที่ ต่อหนึ่งบรรทัด
2. สั่งทำงานไฟล์ `getgooglereview.py`
   ```
   python getgooglereview.py
   ```
3. ข้อมูลที่รวบรวมได้จะถูกเก็บไว้ในโฟลเดอร์ `results` แยกเป็น 2 ส่วน 
   1. ข้อมูลสถานที่จะถูกเก็บไว้ที่ `results/place.csv`
   2. ข้อมูลรีวิวจะถูกเก็บไว้ที่ `results/placeid.csv`


## Dataframe diagram
โครงสร้างข้อมูล Dataframe โดยนำมาจากข้อมูลที่ได้จาก Google map ในการคำนวน

### user
|userid|name|
|------|----|
|1|Google username|
### venue
|venueid|name|score|category|latitude|longitude|
|-------|----|-----|--------|--------|---------|
|1|Google place's name|5.0|Google place's category|0.00|0.00|
### review
|reviewid|userid|score|time|comment|
|--------|------|-----|----|-------|
|1|1|5|0.1|comment text|

*หน่วยของ time เป็นปี หากน้อยกว่า 1 ปี จะใช้จุดทศนิยม เช่น 1 เดือนใช้ 0.1 เป็นต้น แต่หากมีระยะเวลานานกว่า 10 เดือนขึ้นไปนับเป็น 1 ปี*