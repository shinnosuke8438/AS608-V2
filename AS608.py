import time
from machine import UART

# Cac goi lenh chuan AS608
cmd_verify_passwoard = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x07\x13\x00\x00\x00\x00\x00\x1B'
cmd_get_image        = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x03\x01\x00\x05'
cmd_image2Tz         = b'\xEF\x01\xFF\xFF\xFF\xFF'
cmd_save_image2Tz    = b'\x01\x00\x04\x02'
cmd_createModel      = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x03\x05\x00\x09'
cmd_storeModel       = b'\xEF\x01\xFF\xFF\xFF\xFF'
cmd_save_storeModel  = b'\x01\x00\x06\x06\x01'
cmd_match            = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x03\x03\x00\x07'
cmd_search           = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x08\x04\x01\x00\x00\x00\x7F\x00\x8D'
cmd_search_master    = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x08\x04\x01\x00\x00\x00\x01\x00\x0F'
cmd_deleteModel      = b'\xEF\x01\xFF\xFF\xFF\xFF'
cmd_save_deleteModel = b'\x01\x00\x07\x0C'
cmd_empty_database   = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x03\x0D\x00\x11'


class FINGER_PRINT:
    def __init__(self):
        # Khoi tao UART tren chan P15 (TX - GPIO 23), P14 (RX - GPIO 19)
        self.uart = UART(2, baudrate=57600, tx=23, rx=19, timeout=50)
        self.fingerID = -1

    def _flush_input(self):
        """Xoa sach dem UART de tranh lech goi tin"""
        while self.uart.any():
            self.uart.read()

    def _wait_and_read(self, length, timeout_ms=500):
        """Cho va doc du so luong byte, thoat ngay khi nhan du"""
        t0 = time.ticks_ms()
        while self.uart.any() < length:
            if time.ticks_diff(time.ticks_ms(), t0) > timeout_ms:
                return None  # Thoat ngay khi timeout, tranh bi treo them boi uart.read()
            time.sleep_ms(2)
        return self.uart.read(length)

    def data_return(self, length, timeout_ms=500):
        res = self._wait_and_read(length, timeout_ms=timeout_ms)
        try:
            if res and len(res) >= length:
                return res[length - 3]
            return 0xFF
        except Exception:
            return 0xFF

    def data_match_return(self, length, timeout_ms=500):
        res = self._wait_and_read(length, timeout_ms=timeout_ms)
        try:
            if res and len(res) >= length:
                return res[length - 5]
            return 0xFF
        except Exception:
            return 0xFF

    def data_search_return(self, length, timeout_ms=600):
        res = self._wait_and_read(length, timeout_ms=timeout_ms)
        try:
            if res and len(res) >= length:
                confirm_code = res[length - 7]
                if confirm_code == 0x00:
                    # Ghep 2 byte PageID (Index 10 va 11)
                    self.fingerID = (res[length - 6] << 8) | res[length - 5]
                elif confirm_code == 0x09:
                    self.fingerID = 0  # Van tay la
                else:
                    self.fingerID = -1
                return confirm_code
            else:
                self.fingerID = -1
                return 0xFF
        except Exception:
            self.fingerID = -1
            return 0xFF

    def verifyPassword(self):
        self._flush_input()
        self.uart.write(cmd_verify_passwoard)
        return self.data_return(12, timeout_ms=300)

    def getImage(self):
        self._flush_input()
        self.uart.write(cmd_get_image)
        # Quet anh van tay khi dat tay len mat kinh can 150ms - 350ms
        res = self.data_return(12, timeout_ms=450)
        if res == 0x02 or res == 0xFF:
            self.fingerID = -1
        return res

    def image2Tz(self, slot=1):
        chk = (0x01 + 0x04 + 0x02 + slot) & 0xFFFF
        sum_image2Tz = cmd_save_image2Tz + bytearray([slot, (chk >> 8) & 0xFF, chk & 0xFF])
        self._flush_input()
        self.uart.write(cmd_image2Tz + sum_image2Tz)
        return self.data_return(12, timeout_ms=500)

    def createModel(self):
        self._flush_input()
        self.uart.write(cmd_createModel)
        return self.data_return(12, timeout_ms=500)

    def storeModel(self, id):
        id_high = (id >> 8) & 0xFF
        id_low = id & 0xFF
        chk = (0x01 + 0x06 + 0x06 + 0x01 + id_high + id_low) & 0xFFFF
        sum_storeModel = cmd_save_storeModel + bytearray([id_high, id_low, (chk >> 8) & 0xFF, chk & 0xFF])
        self._flush_input()
        self.uart.write(cmd_storeModel + sum_storeModel)
        return self.data_return(12, timeout_ms=500)

    def match(self):
        self._flush_input()
        self.uart.write(cmd_match)
        return self.data_match_return(14, timeout_ms=500)

    def search(self):
        self._flush_input()
        self.uart.write(cmd_search)
        return self.data_search_return(16, timeout_ms=600)

    def search_master(self):
        self._flush_input()
        self.uart.write(cmd_search_master)
        return self.data_search_return(16, timeout_ms=600)

    def deleteModel(self, id):
        id_high = (id >> 8) & 0xFF
        id_low = id & 0xFF
        chk = (0x01 + 0x07 + 0x0C + id_high + id_low + 0x00 + 0x01) & 0xFFFF
        sum_deleteModel = cmd_save_deleteModel + bytearray([id_high, id_low, 0x00, 0x01, (chk >> 8) & 0xFF, chk & 0xFF])
        self._flush_input()
        self.uart.write(cmd_deleteModel + sum_deleteModel)
        return self.data_return(12, timeout_ms=500)

    def emptyDatabase(self):
        self._flush_input()
        self.uart.write(cmd_empty_database)
        return self.data_return(12, timeout_ms=600)

    def return_FingerID(self):
        return self.fingerID


fig = FINGER_PRINT()