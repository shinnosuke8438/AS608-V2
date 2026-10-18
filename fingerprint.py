import time
from micropython import const
from AS608 import fig

# Dinh nghia cac ma xac nhan chuan
FINGERPRINT_OK                  = const(0x00)
FINGERPRINT_PACKETRECIEVEERR    = const(0x01)
FINGERPRINT_NOFINGER            = const(0x02)
FINGERPRINT_IMAGEFAIL           = const(0x03)
FINGERPRINT_IMAGEMESS           = const(0x06)
FINGERPRINT_FEATUREFAIL         = const(0x07)
FINGERPRINT_NOMATCH             = const(0x08)
FINGERPRINT_NOTFOUND            = const(0x09)
FINGERPRINT_ENROLLMISMATCH      = const(0x0A)
FINGERPRINT_BADLOCATION         = const(0x0B)
FINGERPRINT_DBRANGEFAIL         = const(0x0C)
FINGERPRINT_DELETEFAIL          = const(0x10)
FINGERPRINT_DBCLEARFAIL         = const(0x11)

p = -1
SaveResult = -1


def getFingerprintEnroll(id, timeout_sec=5):
    """Quy trinh dang ky van tay toi uu toc do va thong bao chi tiet"""
    global SaveResult
    SaveResult = 0
    timeout_ms = timeout_sec * 1000

    print("\n" + "=" * 45)
    print(">> [AS608] DANG KY VAN TAY CHO ID:", id)
    print("=" * 45)

    # Kiem tra giao tiep UART voi cam bien truoc
    p = fig.getImage()
    if p == 0xFF:
        print(">> [LOI KET NOI]: Khong nhan duoc phan hoi tu AS608 (Ma 0xFF)!")
        print("   Vui long kiem tra day TX/RX (P14/P15) va nguon 3.3V.")
        return 0

    # 1. Neu ngon tay dang cham san (p == FINGERPRINT_OK), yeu cau nhac ra truoc
    if p != FINGERPRINT_NOFINGER:
        print(">> [NHAC NHO]: Vui long nhac ngon tay ra truoc...")
        t0 = time.ticks_ms()
        while p != FINGERPRINT_NOFINGER:
            if time.ticks_diff(time.ticks_ms(), t0) > 2500:
                break
            time.sleep_ms(30)
            p = fig.getImage()

    # 2. Cho cham tay LAN 1
    print("-> [BUOC 1/2]: Dat ngon tay len cam bien (Cho {}s)...".format(timeout_sec))
    t0 = time.ticks_ms()
    p = fig.getImage()
    while p != FINGERPRINT_OK:
        if time.ticks_diff(time.ticks_ms(), t0) >= timeout_ms:
            print(">> [HET GIO]: Da HUY dang ky!")
            SaveResult = 0
            return 0
        time.sleep_ms(30)
        p = fig.getImage()

    print("   [+] Da chup anh 1! Dang tao mau...")
    p = fig.image2Tz(1)
    if p != FINGERPRINT_OK:
        print(">> [LOI]: Anh lan 1 bi mo! Ma loi:", hex(p))
        SaveResult = 0
        return 0

    # 3. Yeu cau nhac tay ra
    print("-> [HANH DONG]: NHAC NGON TAY RA...")
    t0 = time.ticks_ms()
    p = fig.getImage()
    while p != FINGERPRINT_NOFINGER:
        if time.ticks_diff(time.ticks_ms(), t0) > 2500:
            break
        time.sleep_ms(30)
        p = fig.getImage()

    # 4. Cho cham lai LAN 2
    print("-> [BUOC 2/2]: Dat lai DUNG NGON TAY DO mot lan nua (Cho {}s)...".format(timeout_sec))
    t0 = time.ticks_ms()
    p = fig.getImage()
    while p != FINGERPRINT_OK:
        if time.ticks_diff(time.ticks_ms(), t0) >= timeout_ms:
            print(">> [HET GIO]: Da HUY dang ky!")
            SaveResult = 0
            return 0
        time.sleep_ms(30)
        p = fig.getImage()

    print("   [+] Da chup anh 2! Dang kiem tra...")
    p = fig.image2Tz(2)
    if p != FINGERPRINT_OK:
        print(">> [LOI]: Anh lan 2 khong dat! Ma loi:", hex(p))
        SaveResult = 0
        return 0

    # 5. Ghep model
    p = fig.createModel()
    if p != FINGERPRINT_OK:
        print(">> [THAT BAI]: 2 lan cham khong khop cung 1 ngon tay! Ma loi:", hex(p))
        SaveResult = 0
        return 0

    # 6. Luu vao o nho Flash
    p = fig.storeModel(id)
    if p != FINGERPRINT_OK:
        print(">> [LOI]: Khong the luu vao ID {}! Ma loi: {}".format(id, hex(p)))
        SaveResult = 0
        return 0

    print(">> [THANH CONG]: Da luu van tay vao ID {}!".format(id))
    print("=" * 45 + "\n")
    SaveResult = 1
    return 1


def searchFinger():
    p = fig.getImage()
    if p != FINGERPRINT_OK:
        return -1  # Khong co tay cham -> Thoat ngay lap tuc

    print(">> [AS608]: Phat hien ngon tay! Dang quet...")
    p = fig.image2Tz(1)
    if p != FINGERPRINT_OK:
        return -1

    p = fig.search()
    if p == FINGERPRINT_OK:
        fid = fig.return_FingerID()
        print(">> [XAC THUC DUNG]: Khop ID: {}".format(fid))
        return fid
    else:
        print(">> [TU CHOI]: Van tay LA, chua dang ky!")
        return 0


def checkFinger():
    """Ham phuc vu khoi lenh [doc cam bien van tay] tren Blockly"""
    global SaveResult
    result = searchFinger()
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