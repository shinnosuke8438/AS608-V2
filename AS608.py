import time
from machine import UART

# Cac goi lenh chuan AS608
cmd_verify_passwoard = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x07\x13\x00\x00\x00\x00\x00\x1B'
cmd_get_image        = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x03\x01\x00\x05'
cmd_image2Tz         = b'\xEF\x01\xFF\xFF\xFF\xFF'
cmd_save_image2Tz    = b'\x01\x00\x04\x02'
cmd_createModel      = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x03\x05\x00\x09'
cmd_storeModel       = b'\xEF\x01\xFF\xFF\xFF\xFF'
cmd_save_storeModel  = b'\x01\x00\x06\x06\x01\x00'
cmd_match            = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x03\x03\x00\x07'
cmd_search           = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x08\x04\x01\x00\x00\x00\x7F\x00\x8D'
cmd_search_master    = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x08\x04\x01\x00\x00\x00\x01\x00\x0F'
cmd_deleteModel      = b'\xEF\x01\xFF\xFF\xFF\xFF'
cmd_save_deleteModel = b'\x01\x00\x07\x0c\x00'
cmd_empty_database   = b'\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x03\x0D\x00\x11'


class FINGER_PRINT:
    def __init__(self):
        # Khoi tao UART tren dung chan phan cung da kiem chung (P15: TX, P14: RX)
        self.uart = UART(2, baudrate=57600, tx=23, rx=19, timeout=200)
        self.fingerID = -1

    def _flush_input(self):
        """Xoa sach dem UART de tranh lech goi tin"""
        while self.uart.any():
            self.uart.read()

    def _wait_and_read(self, length, timeout_ms=100):
        """Cho va doc du so luong byte yeu cau mot cach an toan"""
        t0 = time.ticks_ms()
        while self.uart.any() < length:
            if time.ticks_diff(time.ticks_ms(), t0) > timeout_ms:
                break
            time.sleep_ms(2)
        return self.uart.read(length)

    def data_return(self, length):
        res = self._wait_and_read(length, timeout_ms=80)
        try:
            if res and len(res) >= length:
                return res[length - 3]
            return 0xFF
        except Exception:
            return 0xFF

    def data_match_return(self, length):
        res = self._wait_and_read(length, timeout_ms=80)
        try:
            if res and len(res) >= length:
                return res[length - 5]
            return 0xFF
        except Exception:
            return 0xFF

    def data_search_return(self, length):
        # Xu ly ket qua tim kiem Flash
        res = self._wait_and_read(length, timeout_ms=100)
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
        return self.data_return(12)

    def getImage(self):
        self._flush_input()
        self.uart.write(cmd_get_image)
        res = self.data_return(12)
        if res == 0x02 or res == 0xFF:
            self.fingerID = -1
        return res

    def image2Tz(self, slot=1):
        sum_image2Tz = cmd_save_image2Tz + bytearray([slot, 0, slot + 0x7])
        self._flush_input()
        self.uart.write(cmd_image2Tz)
        self.uart.write(sum_image2Tz)
        time.sleep_ms(30)  # TOI UU: Giam tu 1 giay xuong 30ms
        return self.data_return(12)

    def createModel(self):
        self._flush_input()
        self.uart.write(cmd_createModel)
        time.sleep_ms(30)
        return self.data_return(12)

    def storeModel(self, id):
        sum_storeModel = cmd_save_storeModel + bytearray([id, 0, id + 0x0E])
        self._flush_input()
        self.uart.write(cmd_storeModel)
        self.uart.write(sum_storeModel)
        time.sleep_ms(50)  # TOI UU: Giam tu 1 giay xuong 50ms
        return self.data_return(12)

    def match(self):
        self._flush_input()
        self.uart.write(cmd_match)
        time.sleep_ms(30)
        return self.data_match_return(14)

    def search(self):
        self._flush_input()
        self.uart.write(cmd_search)
        time.sleep_ms(50)  # TOI UU: Giam tu 2 giay xuong 50ms
        return self.data_search_return(16)

    def search_master(self):
        self._flush_input()
        self.uart.write(cmd_search_master)
        time.sleep_ms(30)
        return self.data_search_return(16)

    def deleteModel(self, id):
        sum_deleteModel = cmd_save_deleteModel + bytearray([id, 0, 1, 0, id + 0x15])
        self._flush_input()
        self.uart.write(cmd_deleteModel)
        self.uart.write(sum_deleteModel)
        time.sleep_ms(30)
        return self.data_return(12)

    def emptyDatabase(self):
        self._flush_input()
        self.uart.write(cmd_empty_database)
        time.sleep_ms(30)
        return self.data_return(12)

    def return_FingerID(self):
        return self.fingerID


fig = FINGER_PRINT()