import micropython
import os, uos, machine, io, ujson, json, time, utime, network, gc, esp, sys, re, binascii
from micropython import const
from machine import Pin, PWM, reset, Timer

FINGERPRINT_OK                  = const(0x00)           #!< Lệnh thực thi hoàn tất
FINGERPRINT_PACKETRECIEVEERR    = const(0x01)           #!< Lỗi gói tin nhận
FINGERPRINT_NOFINGER            = const(0x02)           #!< Không phát hiện ngón tay trên cảm biến
FINGERPRINT_IMAGEFAIL           = const(0x03)           #!< Lấy ảnh vân tay thất bại
FINGERPRINT_IMAGEMESS           = const(0x06)           #!< Ảnh vân tay quá mờ/rối
FINGERPRINT_FEATUREFAIL         = const(0x07)           #!< Quá ít điểm đặc trưng
FINGERPRINT_NOMATCH             = const(0x08)           #!< Vân tay không trùng khớp
FINGERPRINT_NOTFOUND            = const(0x09)           #!< Không tìm thấy trong bộ nhớ
FINGERPRINT_ENROLLMISMATCH      = const(0x0A)           #!< Hai lần chạm không khớp cùng một ngón
FINGERPRINT_BADLOCATION         = const(0x0B)           #!< Vị trí ID vượt quá giới hạn
FINGERPRINT_DBRANGEFAIL         = const(0x0C)           #!< Lỗi đọc bộ nhớ Flash
FINGERPRINT_UPLOADFEATUREFAIL   = const(0x0D)           
FINGERPRINT_PACKETRESPONSEFAIL  = const(0x0E)           
FINGERPRINT_UPLOADFAIL          = const(0x0F)           
FINGERPRINT_DELETEFAIL          = const(0x10)           #!< Xóa mẫu thất bại
FINGERPRINT_DBCLEARFAIL         = const(0x11)           #!< Xóa toàn bộ thất bại

from AS608 import fig

p = -1
SaveResult = -1

def getFingerprintEnroll(id, timeout_sec=5):
    """
    Quy trinh dang ky van tay voi thong bao chi tiet tren Terminal
    """
    global SaveResult
    SaveResult = 0
    
    print("\n" + "=" * 45)
    print(">> [AS608] KHOI DONG DANG KY VAN TAY CHO ID:", id)
    print("=" * 45)

    # 1. Neu ngon tay dang cham san, yeu cau nhac ra truoc
    dem_nhac_tay = 0
    p = fig.getImage()
    if p != FINGERPRINT_NOFINGER:
        print(">> [NHAC NHO]: Phat hien ngon tay dang cham san, vui long nhac ra...")
        while p != FINGERPRINT_NOFINGER:
            time.sleep(0.1)
            dem_nhac_tay += 1
            if dem_nhac_tay > 25: # 2.5 giay
                break
            p = fig.getImage()

    # 2. Cho cham tay LAN 1 (Toi da timeout_sec giay)
    print("-> [BUOC 1/2]: Xin moi dat ngon tay len cam bien (Cho toi da {}s)...".format(timeout_sec))
    gioi_han = timeout_sec * 10
    dem = 0
    p = fig.getImage()
    while p != FINGERPRINT_OK:
        time.sleep(0.1)
        dem += 1
        if dem >= gioi_han:
            print(">> [HET GIO]: Qua {} giay khong cham tay. Da HUY dang ky!".format(timeout_sec))
            SaveResult = 0
            return 0
        p = fig.getImage()
    
    print("   [+] Da chup duoc anh 1! Dang trich xuat dac trung...")
    time.sleep(0.2)
    p = fig.image2Tz(1)
    if p != FINGERPRINT_OK:
        print(">> [LOI]: Anh ngon tay lan 1 khong ro hoac qua mo! Ma loi:", hex(p))
        SaveResult = 0
        return 0
    
    # 3. Yeu cau nhac ngon tay ra
    print("-> [HANH DONG]: Vui long NHAC NGON TAY RA khoi cam bien...")
    dem = 0
    p = fig.getImage()
    while p != FINGERPRINT_NOFINGER:
        time.sleep(0.1)
        dem += 1
        if dem >= 30: # 3 giay
            break
        p = fig.getImage()

    # 4. Cho cham lai ngon tay do LAN 2
    print("-> [BUOC 2/2]: Dat lai DUNG NGON TAY DO mot lan nua de doi chieu...")
    dem = 0
    p = fig.getImage()
    while p != FINGERPRINT_OK:
        time.sleep(0.1)
        dem += 1
        if dem >= gioi_han:
            print(">> [HET GIO]: Qua {} giay khong xac nhan lai. Da HUY dang ky!".format(timeout_sec))
            SaveResult = 0
            return 0
        p = fig.getImage()

    print("   [+] Da chup duoc anh 2! Dang kiem tra do trung khop...")
    time.sleep(0.2)
    p = fig.image2Tz(2)
    if p != FINGERPRINT_OK:
        print(">> [LOI]: Anh ngon tay lan 2 khong dat tieu chuan! Ma loi:", hex(p))
        SaveResult = 0
        return 0
    
    # 5. Ghep model tu 2 lan cham
    time.sleep(0.3)
    p = fig.createModel()
    if p != FINGERPRINT_OK:
        print(">> [THAT BAI]: 2 lan cham KHONG TRUNG KHOP cung 1 ngon tay! Ma loi:", hex(p))
        SaveResult = 0
        return 0

    # 6. Luu vao o nho Flash
    time.sleep(0.3)
    p = fig.storeModel(id)
    if p != FINGERPRINT_OK:
        print(">> [LOI PHAN CUNG]: Khong the ghi vao Flash o nho ID {}! Ma loi: {}".format(id, hex(p)))
        SaveResult = 0      
        return 0

    print(">> [THANH CONG HOAN TOAN]: Da luu van tay vao ID {}!".format(id))
    print("=" * 45 + "\n")
    SaveResult = 1
    return 1

def searchFinger():
    p = fig.getImage()
    if p != FINGERPRINT_OK:
        return -1 # Khong co ai cham tay
    
    # Co nguoi cham tay -> thong bao ngay
    print(">> [AS608]: Phat hien ngon tay cham vao! Dang kiem tra...")
    
    p = fig.image2Tz(1)
    if p != FINGERPRINT_OK:
        print("   [-] Anh van tay mo, vui long an chat hon!")
        return -1 

    p = fig.search() 
    if p == FINGERPRINT_OK:
        fid = fig.return_FingerID()
        print(">> [XAC THUC DUNG]: Van tay TRUNG KHOP voi ID: {}!".format(fid))
        return fid
    else:
        print(">> [TU CHOI]: Van tay LA, chua duoc dang ky trong bo nho!")
        return 0
    
def checkFinger():
    global SaveResult
    result = searchFinger()
    time.sleep(0.2)
    if result != -1:
        if result == 0:
            SaveResult = 0
            return 0
        else:
            SaveResult = 1
            return result
    else:
        return -1

def checkID(id):
    kq = checkFinger()
    return kq == id

def getLastSaveResult():
    return 1 if SaveResult == 1 else 0