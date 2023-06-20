# Recommendation System

โปรเจคแนะนำอะไรสักอย่าง ด้วยเทคนิค Recommendation System ตอนนี้ก็พยายามดึงข้อมูลสถานที่มาจาก Google Map ด้วยเทคนิค Web Scraping และจะเก็บลงฐานข้อมูลเพื่อนำมาประมวลผลต่อไป

# Setup

## ติดตั้งแพ็กเก็จสำหรับ Python

ที่ Terminal เรียกใช้คำสั่ง pip install ตามด้วย package เพื่อทำการติดตั้ง

```
pip install -r requirements.txt
```

หากต้องการบันทึกข้อมูล package ที่ใช้ให้ใช้คำสั่ง

```
pip freeze >> requirements.txt
```

## ติดตั้ง Chrome Driver

สำหรับการดึงข้อมูลรีวิวสถานที่ที่มีใน Google Maps โดยใช้ chromedriver โดยเครืองต้องมีการติดตั้ง [Chrome Browser](https://www.google.com/intl/th_th/chrome/)

## ติดตั้งฐานข้อมูลโดยใช้ Docker

ทำการดาวโหลดและติดตั้ง Docker จาก[เว็บไซด์](https://www.docker.com/) หลังจากนั้นเข้าไปที่โฟลเดอร์ `rs-db` และเรียกใช้คำสั่งสำหรับสร้าง Docker

```
docker-compose up
```

โปรแกรมจะทำการสร้าง Docker container และ Docker image ขึ้นมาสำหรับฐานข้อมูล MySQL

สามารถใช้โปรแกรมเพื่อเชื่อต่อเข้าไปดูข้อมูลในฐานข้อมูลได้เช่นโปรแกรม [MySQL Workbench](https://www.mysql.com/products/workbench/)

> #### Note
>
> การตั้งค่าฐานข้อมูลจาก Docker ดูได้ที่ไฟล์ `rs-db/docker-compose.yaml`

# การดึงข้อมูลสถานที่จากเว็บไซด์

การดึงข้อมูลมีทั้งหมด 3 ขั้นตอน

1. การดึงข้อมูลจากเว็บไซด์ Google map
2. การดึงข้อมูลจาก Google Local guide
3. การอัพเดตข้อมูลสถานที่จาก Google map

## 1. การดึงข้อมูลจากเว็บไซด์ Google map

เป็นการดึงข้อมูลโดยการกำหนด url จาก google map โดยทำการอ่าน url เป้าหมายจากไฟล์ที่เรากำหนด โดยแบ่งเป็นขั้นตอนดังนี้

1. ใส่ url ของสถานที่ ที่เราต้องการดึงข้อมูล โดยนำ url ได้จาก Google map ในหน้าที่แสดงข้อมูลสถานที่มาใส่ในไฟล์ที่ชื่อ `data/placelist.csv` โดยบันทึก url ต่อหนึ่งบรรทัด
   > #### Note
   >
   > ตัวอย่าง url ดูได้ที่ไฟล์
2. สั่งทำงานไฟล์ `googleplace.py`

   ```
   python googleplace.py
   ```

   คำสั่งเพิ่มเติมสำหรับเรียกใช้งานโดยการเพิ่มอากิวเม้นต์ต่อท้ายชื่อไฟล์

   | argument         | details                                                          |
   | ---------------- | ---------------------------------------------------------------- |
   | `--empty-db`     | สำหรับสั่งให้ลบตารางทั้งหมดออกจากฐานข้อมูล แล้วทำการสร้างใหม่    |
   | `--force-update` | สำหรับสั่งให้ดึงข้อมูลจากเว็บแม้ว่าจะมีข้อมูลอยู่แล้วในฐานข้อมูล |

   ตัวอย่างการทำงาน

   ```
   python googleplace.py --empty-db --force-update
   ```

## 2. การดึงข้อมูลจาก Google Local guide

จากการทำงานในข้อที่ 1. เราจะได้ข้อมูลสถานที่ท่องเที่ยวเป้าหมาย พร้อมกับคนที่เข้ามารีวิว และ link ของผู้ใช้งาน ขั้นตอนนี้จะเป็นการเข้าไปดูข้อมูลผู้ใช้งานที่ละคน เพื่อดึงข้อมูลรีวิวของผู้ใช้งานมา พร้อมกับสถานที่ที่เคยรีวิวที่อื่นด้วย

คำสั่งที่ใช้ทำงานไฟล์ `googleplace_contrib.py`

```batch
python googleplace_contrib.py
```

ผลลัพท์ที่ได้ จะทำให้เราได้สถานที่เพิ่มขึ้น โดยอ้างอิงจากผู้ใช้งานในฐานข้อมูล

## 3. การอัพเดตข้อมูลสถานที่จาก Google map

จากการทำงานข้อที่ 2. เราจะได้ข้อมูลสถานที่ ขั้นตอนนี้เราจะเข้าไปเอาข้อมูลของสถานที่มาเพิ่มเติม โดยอ้างอิงจาก **ชื่อสถานที่** ที่เราได้จากข้อที่ 2.

คำสั่งที่ใช้ทำงานไฟล์ `googleplace_venue.py`

```batch
python googleplace_venue.py
```

# Entity Relationship Diagrams

โครงสร้างข้อมูล Dataframe โดยนำมาจากข้อมูลที่ได้จาก Google map ในการคำนวน

```mermaid
erDiagram
   USER ||--|{ REVIEW : review
   USER {
        int id
        string name
        string link
    }
    REVIEW }|--|| venue : review
    REVIEW {
        int id
        int user_id
        int venue_id
        int score
        double time
        string comment
        string link
        string review
    }
    venue ||--|| venue_CATEGORY : category
     venue {
        int id
        string name
        int score
        double latitude
        double longitude
        string link
    }
    venue_CATEGORY ||--|| CATEGORY : category
    venue_CATEGORY{
      int id
      int venue_id
      int category_id
    }
    CATEGORY{
      int id
      string name
    }

```

_หน่วยของ time เป็นปี หากน้อยกว่า 1 ปี จะใช้จุดทศนิยม เช่น 1 เดือนใช้ 0.1 เป็นต้น แต่หากมีระยะเวลานานกว่า 10 เดือนขึ้นไปนับเป็น 1 ปี_

## ChromeDriver ERROR

กรณีเกิดปัญหาข้อผิดพลาดในการเริ่มการทำงาน แสดงข้อผิดพลาดกรณี chromedriver.exe ไม่ตรงกับเวอร์ชั่นของ Chrome ในเครื่องคอมพิวเตอร์ ให้ทำการดาวโหลด chromedriver.exe ตัวใหม่ได้ที่ [ChromeDriver](https://chromedriver.chromium.org/downloads) ทำการเลือกเวอร์ชั่นและระบบปฏิบัติการ

```
Exception has occurred: SessionNotCreatedException
Message: session not created: This version of ChromeDriver only supports Chrome version 104
Current browser version is 114.0.5735.134
```
