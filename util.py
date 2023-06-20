import pandas as pd
import os


class Util:
    def getTime(timetext):
        if "สัปดาห์" in timetext or "วัน" in timetext:
            return 0.1
        if "เดือน" in timetext:
            txt = timetext.split(' ')
            if len(txt) > 1:
                month = int(txt[0])
                if month > 9:
                    return 1.0
                else:
                    return month / 10
            else:
                return 0.1
        if "ปี" in timetext:
            txt = timetext.split(' ')
            if len(txt) > 1:
                year = int(txt[0])
                return year
            else:
                return 1
        return 0.1

    def getfile(filepath, isLoad=True):
        df = pd.DataFrame()
        if not isLoad:
            return df
        try:
            if os.path.exists(filepath):
                df = pd.read_csv(filepath, sep='|')
        except:
            return df
        return df

    @staticmethod
    def convertStar(labeltext):
        if "ดาว" in labeltext:
            return float(labeltext.split()[0])
        else:
            return float(labeltext)
            
    @staticmethod
    def getProvince(address):
        if "-" in address:
            address = address.replace("-", " ")

        province = [
            'กระบี่', 'กรุงเทพมหานคร', 'กาญจนบุรี', 'กาฬสินธุ์', 'กำแพงเพชร',
            'ขอนแก่น',
            'จันทบุรี',
            'ฉะเชิงเทรา',
            'ชลบุรี', 'ชัยนาท', 'ชัยภูมิ', 'ชุมพร', 'เชียงราย', 'เชียงใหม่',
            'ตรัง', 'ตราด', 'ตาก',
            'นครนายก', 'นครปฐม', 'นครพนม', 'นครราชสีมา', 'นครศรีธรรมราช', 'นครสวรรค์', 'นนทบุรี', 'นราธิวาส', 'น่าน',
            'บึงกาฬ', 'บุรีรัมย์',
            'ปทุมธานี', 'ประจวบคีรีขันธ์', 'ปราจีนบุรี', 'ปัตตานี',
            'พระนครศรีอยุธยา', 'พะเยา', 'พังงา', 'พัทลุง', 'พิจิตร', 'พิษณุโลก', 'เพชรบุรี', 'เพชรบูรณ์', 'แพร่',
            'ภูเก็ต',
            'มหาสารคาม', 'มุกดาหาร', 'แม่ฮ่องสอน',
            'ยโสธร', 'ยะลา',
            'ร้อยเอ็ด', 'ระนอง', 'ระยอง', 'ราชบุรี',
            'ลพบุรี', 'ลำปาง', 'ลำพูน', 'เลย',
            'ศรีสะเกษ',
            'สกลนคร', 'สงขลา', 'สตูล', 'สมุทรปราการ', 'สมุทรสงคราม', 'สมุทรสาคร', 'สระแก้ว', 'สระบุรี', 'สิงห์บุรี', 'สุโขทัย', 'สุพรรณบุรี', 'สุราษฎร์ธานี', 'สุรินทร์',
            'หนองคาย', 'หนองบัวลำภู',
            'อ่างทอง', 'อำนาจเจริญ', 'อุดรธานี', 'อุตรดิตถ์', 'อุทัยธานี', 'อุบลราชธานี']
        
        address = address.split(' ')
        for city in address:
            if city in province:
                return city
