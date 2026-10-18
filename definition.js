Blockly.Blocks['yolobit_fingerprint_create'] = {
  init: function() {
    this.jsonInit({
      "type": "yolobit_fingerprint_create",
      "message0": Blockly.Msg.YOLOBIT_FINGERPRINT_CREATE_MESSAGE0,
      "args0": [
        {
          "type": "input_value",
          "name": "ID"
        }
      ],
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#ffa64d",
      "tooltip": Blockly.Msg.YOLOBIT_FINGERPRINT_CREATE_TOOLTIP,
      "helpUrl": Blockly.Msg.YOLOBIT_FINGERPRINT_CREATE_HELPURL
    });
  }
};

Blockly.Blocks['yolobit_fingerprint_result'] = {
  init: function() {
    this.jsonInit({
      "type": "yolobit_fingerprint_result",
      "message0": Blockly.Msg.YOLOBIT_FINGERPRINT_RESULT_MESSAGE0,
      "output": null,
      "colour": "#ffa64d",
      "tooltip": Blockly.Msg.YOLOBIT_FINGERPRINT_RESULT_TOOLTIP,
      "helpUrl": Blockly.Msg.YOLOBIT_FINGERPRINT_RESULT_HELPURL
    });
  }
};


Blockly.Blocks['yolobit_fingerprint_verify'] = {
  init: function() {
    this.jsonInit({
      "type": "yolobit_fingerprint_verify",
      "message0": Blockly.Msg.YOLOBIT_FINGERPRINT_VERIFY_MESSAGE0,
      "output": null,
      "colour": "#ffa64d",
      "tooltip": Blockly.Msg.YOLOBIT_FINGERPRINT_VERIFY_TOOLTIP,
      "helpUrl": Blockly.Msg.YOLOBIT_FINGERPRINT_VERIFY_HELPURL
    });
  }
};

Blockly.Blocks['yolobit_fingerprint_check'] = {
  init: function() {
    this.jsonInit({
      "type": "yolobit_fingerprint_check",
      "message0": Blockly.Msg.YOLOBIT_FINGERPRINT_CHECK_MESSAGE0,
      "args0": [
        {
          "type": "input_value",
          "name": "ID"
        }
      ],
      "output": null,
      "colour": "#ffa64d",
      "tooltip": Blockly.Msg.YOLOBIT_FINGERPRINT_CHECK_TOOLTIP,
      "helpUrl": Blockly.Msg.YOLOBIT_FINGERPRINT_CHECK_HELPURL
    });
  }
};

Blockly.Blocks['yolobit_fingerprint_delete'] = {
  init: function() {
    this.jsonInit({
      "type": "yolobit_fingerprint_delete",
      "message0": Blockly.Msg.YOLOBIT_FINGERPRINT_DELETE_MESSAGE0,
      "args0": [
        {
          "type": "input_value",
          "name": "ID"
        }
      ],
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#ffa64d",
      "tooltip": Blockly.Msg.YOLOBIT_FINGERPRINT_DELETE_TOOLTIP,
      "helpUrl": Blockly.Msg.YOLOBIT_FINGERPRINT_DELETE_HELPURL
    });
  }
};

Blockly.Blocks['yolobit_fingerprint_clear'] = {
  init: function() {
    this.jsonInit({
      "type": "yolobit_fingerprint_clear",
      "message0": Blockly.Msg.YOLOBIT_FINGERPRINT_CLEAR_MESSAGE0,
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#ffa64d",
      "tooltip": Blockly.Msg.YOLOBIT_FINGERPRINT_CLEAR_TOOLTIP,
      "helpUrl": Blockly.Msg.YOLOBIT_FINGERPRINT_CLEAR_HELPURL
    });
  }
};

// Any imports need to be reserved words
Blockly.Python.addReservedWords('fingerprint');

Blockly.Python['yolobit_fingerprint_create'] = function(block) {
  Blockly.Python.definitions_['import_fingerprint'] = 'from fingerprint import *';
  var value_id = Blockly.Python.valueToCode(block, 'ID', Blockly.Python.ORDER_ATOMIC);
  var code = 'getFingerprintEnroll(' + value_id + ')\n';
  return code;
};

Blockly.Python['yolobit_fingerprint_result'] = function(block) {
  Blockly.Python.definitions_['import_fingerprint'] = 'from fingerprint import *';
  var code = 'getLastSaveResult()';
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.Python['yolobit_fingerprint_verify'] = function(block) {
  Blockly.Python.definitions_['import_fingerprint'] = 'from fingerprint import *';
  var code = 'checkFinger()';
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.Python['yolobit_fingerprint_check'] = function(block) {
  Blockly.Python.definitions_['import_fingerprint'] = 'from fingerprint import *';
  var value_id = Blockly.Python.valueToCode(block, 'ID', Blockly.Python.ORDER_ATOMIC);
  var code = 'checkID(' + value_id + ')';
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.Python['yolobit_fingerprint_delete'] = function(block) {
  Blockly.Python.definitions_['import_fingerprint'] = 'from fingerprint import *';
  var value_id = Blockly.Python.valueToCode(block, 'ID', Blockly.Python.ORDER_ATOMIC);
  var code = 'fig.deleteModel(' + value_id + ')\n';
  return code;
};

Blockly.Python['yolobit_fingerprint_clear'] = function(block) {
  Blockly.Python.definitions_['import_fingerprint'] = 'from fingerprint import *';
  var code = 'fig.emptyDatabase()\n';
  return code;
};

// --- KHỐI IN MENU HƯỚNG DẪN ---
Blockly.Blocks['yolobit_fingerprint_print_menu'] = {
  init: function() {
    this.jsonInit({
      "type": "yolobit_fingerprint_print_menu",
      "message0": "hiển thị bảng hướng dẫn sử dụng",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#ffa64d",
      "tooltip": "In menu hướng dẫn thao tác ra cửa sổ lệnh"
    });
  }
};

Blockly.Python['yolobit_fingerprint_print_menu'] = function(block) {
  Blockly.Python.definitions_['import_fingerprint'] = 'from fingerprint import *';
  return 'print_menu()\n';
};

// --- KHỐI ĐỌC TỔNG SỐ VÂN TAY ---
Blockly.Blocks['yolobit_fingerprint_get_count'] = {
  init: function() {
    this.jsonInit({
      "type": "yolobit_fingerprint_get_count",
      "message0": "đọc tổng số vân tay hiện có",
      "output": null,
      "colour": "#ffa64d",
      "tooltip": "Trả về tổng số vân tay đang được lưu trong cảm biến"
    });
  }
};

Blockly.Python['yolobit_fingerprint_get_count'] = function(block) {
  Blockly.Python.definitions_['import_fingerprint'] = 'from fingerprint import *';
  return ['getTotalFingerprints()', Blockly.Python.ORDER_NONE];
};