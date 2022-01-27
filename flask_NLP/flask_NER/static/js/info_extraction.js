window.hltr = null; // what is the different between using var hltr and window.hltr
window.mapTag = {}; // for TextHighlighter: window.mapTag[time-stamp] = tag
window.mapTag_color = {}; //window.mapTag_color[tag] = color
window.selectedTag = ''; // map timestamp to tag
window.tag_id = 0;
window.tags = [];
window.epicker = document.querySelector('.color-picker');
window.display_page = null;
localStorage.label_from_model = false;
let modal_createTag = document.getElementById('div_dl_createtag');

// helper functions
function getBrightness(color) {
  return true;
}
function getRandomColor() {
  var letters = '0123456789ABCDEF';
  var color = '#';
  for (var i = 0; i < 6; i++) color += letters[Math.floor(Math.random() * 16)];
  return color;
}
function rgbToHex(rgb) {
  var hex = Number(rgb).toString(16);
  if (hex.length < 2) hex = '0' + hex;
  return hex;
}
function fullColorHex(s) {
  //(10,10,20)
  try {
    var s1 = s.indexOf('('),
      s2 = s.indexOf(')');
    var a = s.substring(s1 + 1, s2).split(',');
    return '#' + rgbToHex(a[0]) + rgbToHex(a[1]) + rgbToHex(a[2]);
  } catch {
    return '#000000';
  }
}
var ColorPicker = (function () {
  var COLORS = [];
  function ColorPicker(el) {
    epicker = this;
    epicker.color = COLORS[0];
    epicker.selected = null;
    COLORS.forEach(function (color) {
      window.tag_id += 1;
      if (epicker.color === color) {
        var div = $(
          '<span style="background-color:' +
            color +
            '" class="dropdown-selected selected">'
        ).append(
          $('<p style="margin:0px;">').text('unknown'),
          $('<i class="del" data-id="' + window.tag_id + '">')
        );
        epicker.selected = div;
        div.appendTo(el);
      } else {
        var div = $(
          '<span style="background-color:' +
            color +
            '" class="dropdown-selected">'
        )
          .append(
            $('<p style="margin:0px;">').text('unknown'),
            $('<i class="del" data-id="' + window.tag_id + '">')
          )
          .appendTo(el);
      }
      div.click(function () {
        if (color !== epicker.color) {
          epicker.color = color;
          if (epicker.selected) epicker.selected.removeClass('selected');
          epicker.selected = div;
          epicker.selected.addClass('selected');
          if (typeof epicker.callback === 'function')
            epicker.callback.call(epicker, color);
        }
      });
    });
  }
  ColorPicker.prototype.onColorChange = function (callback) {
    this.callback = callback;
  };
  return ColorPicker;
})();

function hl_removeitem(t) {
  try {
    var h = window.hltr.getHighlights();
    h.forEach(function (e) {
      if (e.getAttribute('data-timestamp') == t) {
        window.hltr.removeHighlight(e);
        try {
          delete window.mapTag[t];
          $('.content-label tr#' + t).remove();
        } catch {}
        return;
      }
    });
  } catch {}
}
function get_current_page() {
  var pages = document.getElementsByClassName('pagination__item');
  for (var i = 0; i < pages.length; i++) {
    page = pages[i];
    if (page.style.display == 'block') {
      window.display_page = page;
    }
  }
}
function removeTag(tag) {
  for (const [time, tag_name] of Object.entries(window.mapTag)) {
    if (tag == tag_name) {
      hl_removeitem(time);
      delete window.mapTag_color[tag];
    }
  }
  if (window.selectedTag == tag) {
    window.selectedTag = '';
  }
}
function createTag(tag_name, color) {
  var brighterColor = getBrightness(color) ? '#eeeeee' : '#111111'; // get color for word according to background color
  if (tag_name == '') alert('Tag value cannot be empty!');
  else if (window.tags.includes(tag_name)) alert('Duplicated tag value!');
  else {
    window.tags.push(tag_name);
    window.tag_id += 1;
    window.mapTag_color[tag_name] = color;

    var div_dont_know = $(
      '<i class="del"  data-id="' +
        window.tag_id +
        '" style="color:' +
        brighterColor +
        '">'
    );

    var div = $(
      '<span style="background-color:' + color + '" class="dropdown-selected">'
    )
      .append(
        $('<p style="margin:0px;color:' + brighterColor + '">').text(tag_name),
        div_dont_know
      )
      .appendTo($('.color-picker')); // add new tags in the tags lists
    div.click(function () {
      if (color !== epicker.color) {
        window.selectedTag = tag_name;
        epicker.color = color;
        if (epicker.selected) epicker.selected.removeClass('selected');
        epicker.selected = div;
        epicker.selected.addClass('selected');
        if (typeof epicker.callback === 'function') {
          // dont understand that part much
          epicker.callback.call(epicker, color);
        }
      }
    });
    div_dont_know.click(function () {
      var idx = window.tags.indexOf(tag_name);
      if (idx > -1) window.tags.splice(idx, 1);
      removeTag(tag_name);
      div.remove();
    });
    div.trigger('click');
  }
}

function auto_scroll(item) {
  console.log(item);
  item.scrollIntoView();
}

$(document).ready(function () {
  var removeBtn = document.getElementById('hl_remove'),
    hl_acceptBtn = document.getElementById('hl_accept'),
    hl_rejectBtn = document.getElementById('hl_reject'),
    hl_learn = document.getElementById('hl_learn'),
    createTag_btn = document.getElementById('createTag_btn'),
    modal_createTag = document.getElementById('div_dl_createtag'),
    original_file_ = document.getElementById('original_file'),
    report_id_ = document.getElementById('report_id'),
    hl_undo = document.getElementById('hl_undo'),
    new_page_loaded = document.getElementById('new_page_loaded');
  original_file = original_file_.textContent.replace('\n', '');
  original_file = original_file.trim();

  report_id = report_id_.textContent.replace('\n', '');
  report_id = report_id.trim();
  get_current_page();

  // var sandbox = window.display_page;
  var sandbox = document.getElementById('document_content');
  var colors = new ColorPicker(document.querySelector('.color-picker'));
  window.hltr = new TextHighlighter(sandbox, {
    onBeforeHighlight: function (range) {
      if (window.selectedTag == '') {
        // alert('Please choose the tag before annotating');
        return false;
      } else {
        return true;
      }
    },
    onAfterHighlight: function (range, highlights) {
      highlights.map(function (h) {
        var time = h.getAttribute('data-timestamp');
        window.mapTag[time] = window.selectedTag;
        $(
          '<tr onclick = "auto_scroll(hl_' +
            time +
            ')" id =' +
            time +
            '><td>' +
            h.innerHTML +
            '</td><td>' +
            window.selectedTag +
            '</td></tr>'
        ).appendTo($('.content-label'));
      });
      //range.extractContents();
      return true;
    },
    onRemoveHighlight: function (hl) {
      return true;
    },
  });
  var serialized = '';

  new_page_loaded.addEventListener('click', function () {
    if (localStorage.label_from_model == 'true') {
      $('#loadMe').modal('show');
      get_current_page();
      load_original_info_extraction_label(window.display_page);
    }
  });

  colors.onColorChange(function (color) {
    window.hltr.setColor(color);
  });
  removeBtn.addEventListener('click', function () {
    window.hltr.removeHighlights();
    $('.content-label tr').remove();
    window.mapTag = {};
    localStorage.label_from_model = false;
  });
  hl_learn.addEventListener('click', function () {
    $('#loadMe').modal('show');
    // localStorage.label_from_model = true;
    // get_current_page();
    load_original_info_extraction_label();
  });
  createTag_btn.addEventListener('click', function (e) {
    e.preventDefault();
    var tag_name = $('#hl_text').val();
    var color = $('#hl_color').val();
    modal_createTag.style.display = 'none';
    $('#hl_text').val('');
    $('#hl_color').val(getRandomColor());
    createTag(tag_name, color);
  });
  hl_undo.addEventListener('click', function (e) {
    function getMax(arr) {
      if (!arr) return null;
      var maxV = arr[0];
      for (a of arr) {
        if (a > maxV) maxV = a;
      }
      return maxV;
    }
    var t = getMax(Object.keys(window.mapTag));
    if (t) {
      hl_removeitem(t);
    }
    localStorage.label_from_model = false;
  });

  function load_original_info_extraction_label() {
    $.post('/get_original_info_extraction', {
      type: 'post',
      url: '/get_original_info_extraction',
      contentType: 'application/json;charset=UTF-8',
      dataType: 'json',
      data: JSON.stringify({ file_dir: original_file, report_id: report_id }),
    }).done(function (q) {
      if (q.status == false) {
        hl_find_generate_JSON(q.data['res']);
        first_save_info_extraction();
        // alert('Finish extracting important paragraphs');
        $('#loadMe').modal('hide');
      } else {
        hl_loadfrom(q.data['res']);
        // alert('Original information extraction version is found!');
        $('#loadMe').modal('hide');
      }
    });
  }
  function load_latest_info_extraction_version(report_id) {
    $.post('/get_latest_info_extraction', {
      type: 'post',
      url: '/get_latest_info_extraction',
      contentType: 'application/json;charset=UTF-8',
      dataType: 'json',
      data: JSON.stringify({ report_id: report_id }),
    }).done(function (q) {
      window.hltr.removeHighlights();
      if (q.status) {
        // if that document has latest info_extraction version
        hl_loadfrom(q.data['res']);
        alert('Latest information extraction version is found!');
      } else {
        alert('The original version is loaded');
      }
    });
  }

  function confirm_hl(action, original_file, report_id) {
    serialized = window.hltr.serializeHighlights();
    var d = JSON.parse(serialized); // get all highlights in JSON object
    var out = [];
    for (var i = 0; i < d.length; i++) {
      var temp = document.createElement('div');
      temp.innerHTML = d[i][0];
      var time = temp.firstElementChild.getAttribute('data-timestamp');
      var color_origin = temp.firstElementChild.getAttribute('style');
      color_origin = color_origin
        .replace('background-color:', '')
        .replace(';', '');
      if (!color_origin.includes('#'))
        color_origin = fullColorHex(color_origin);
      var res = {
        content: d[i][1],
        path: d[i][2],
        offset: d[i][3],
        length: d[i][4],
        timestamp: time,
        tag: window.mapTag[time], // map tag with timestamp
        color: color_origin,
      };
      out.push(res);
    }
    $.post('/confirm_info_extraction', {
      type: 'post',
      url: '/confirm_info_extraction',
      contentType: 'application/json;charset=UTF-8',
      dataType: 'json',
      data: JSON.stringify({
        res: out,
        action: action,
        original_file: original_file,
        report_id: report_id,
      }),
    });
  }

  function decodeHtmlCharCodes(str) {
    return str.replace(/(&#(\d+);)/g, function (match, capture, charCode) {
      return String.fromCharCode(charCode);
    });
  }

  // d = [{'content': 'South America', 'tag': 'LOC', 'color': '#2DC477'}, {'content': 'United States', 'tag': 'GPE', 'color': '#AC10D6'}];
  function hl_find_generate_JSON(d) {
    window.selectedTag = ''; // map timestamp to tag

    $('.content-label tr').remove();

    contentSet = [];
    objectSet = [];
    d.forEach(createSetObject);
    function createSetObject(object) {
      // console.log(object.content);
      object.content = decodeHtmlCharCodes(object.content);
      if (object.content.length > 10) {
        if (!contentSet.includes(object.content)) {
          contentSet.push(object.content);
          objectSet.push(object);
        }
      }
    }

    objectSet.sort((a, b) =>
      a.content.length < b.content.length
        ? 1
        : a.content.length > b.content.length
        ? -1
        : 0
    );
    for (var i = 0; i < objectSet.length; i++) {
      for (var j = 0; j < i; j++) {
        if (objectSet[j].content.includes(objectSet[i].content)) {
          markDuplicatedEachEntity(objectSet[i]);
          objectSet.splice(i, 1);
          break;
        }
      }
    }

    objectSet.forEach(markEachEntity);
    function markEachEntity(object) {
      try {
        if (!window.tags.includes(object.tag) && object.tag != '') {
          createTag(object.tag, object.color);
        } else {
          object.color = window.mapTag_color[object.tag];
        }
        window.selectedTag = object.tag;

        window.hltr.setColor(object.color);
        // console.log('finding ...' + object.content);
        window.hltr.find(object.content, true);
        // console.log('--done--');
      } catch (e) {}
    }
    function markDuplicatedEachEntity(object) {
      try {
        if (!window.tags.includes(object.tag) && object.tag != '') {
          createTag(object.tag, object.color);
        } else {
          object.color = window.mapTag_color[object.tag];
        }
        window.selectedTag = object.tag;

        window.hltr.setColor(object.color);
        // console.log(object.content);
        window.hltr.find(object.content, true);
      } catch (e) {}
    }
  }
  var func = () => {};

  /*d = [{"timestamp":"1624010980537", "content":'amet', "path":"1", "offset":22, "length":4, "color":"#ffff7b", "tag":"label1"}, ];*/
  function hl_loadfrom(d) {
    arr = [];
    window.tag_id = 0;
    window.tags = [];
    window.mapTag = {}; // for TextHighlighter
    window.selectedTag = ''; // map timestamp to tag
    $('.color-picker').empty();
    $('.content-label tr').remove();
    $.each(d, function (k, v) {
      //highlight step
      var s = [
        '<span class="highlighted" id = "hl_' +
          v.timestamp +
          '" data-timestamp="' +
          v.timestamp +
          '" onclick="hl_removeitem(' +
          v.timestamp +
          ')" style="background-color: ' +
          v.color +
          ';" data-highlighted="true"></span>',
        v.content,
        v.path,
        v.offset,
        v.length,
      ];
      arr.push(s);
      window.mapTag[v.timestamp] = v.tag;
      window.selectedTag = v.tag;
      // create tags
      if (!window.tags.includes(v.tag) && v.tag) {
        createTag(v.tag, v.color);
      }

      // update table word tags
      var div_table = $(
        '<tr id =' +
          v.timestamp +
          ' onclick = "auto_scroll(hl_' +
          v.timestamp +
          ')"><td>' +
          v.content +
          '</td><td>' +
          v.tag +
          '</td></tr>'
      ).appendTo($('.content-label'));
    });
    var s = JSON.stringify(arr);
    window.hltr.removeHighlights();
    window.hltr.deserializeHighlights(s);
  }
  function first_save_info_extraction() {
    serialized = window.hltr.serializeHighlights();
    var d = JSON.parse(serialized); // get all highlights in JSON object
    var out = [];
    for (var i = 0; i < d.length; i++) {
      // Array(5)
      // 0: "<span class=\"highlighted\" data-timestamp=\"1636008148149\" onclick=\"hl_removeitem('1636008148149')\" style=\"background-color: rgb(255, 128, 128);\" data-highlighted=\"true\"></span>"
      // 1: "CHAN"
      // 2: "12:0:1"
      // 3: 17
      // 4: 4
      var temp = document.createElement('div');
      temp.innerHTML = d[i][0];
      var time = temp.firstElementChild.getAttribute('data-timestamp');
      var color_origin = temp.firstElementChild.getAttribute('style');
      color_origin = color_origin
        .replace('background-color:', '')
        .replace(';', '');
      if (!color_origin.includes('#'))
        color_origin = fullColorHex(color_origin);
      var res = {
        content: d[i][1],
        path: d[i][2],
        offset: d[i][3],
        length: d[i][4],
        timestamp: time,
        tag: window.mapTag[time], // map tag with timestamp
        color: color_origin,
      };
      out.push(res);
    }
    $.post('/confirm_info_extraction', {
      type: 'post',
      url: '/confirm_info_extraction',
      contentType: 'application/json;charset=UTF-8',
      dataType: 'json',
      data: JSON.stringify({
        res: out,
        action: 'accept',
        original_file: original_file,
        report_id: report_id,
        category: 3,
        type: 'original_info_extraction',
      }),
    });
  }

  function confirm_info_extract() {
    serialized = window.hltr.serializeHighlights();
    var d = JSON.parse(serialized); // get all highlights in JSON object
    var out = [];
    for (var i = 0; i < d.length; i++) {
      // Array(5)
      // 0: "<span class=\"highlighted\" data-timestamp=\"1636008148149\" onclick=\"hl_removeitem('1636008148149')\" style=\"background-color: rgb(255, 128, 128);\" data-highlighted=\"true\"></span>"
      // 1: "CHAN"
      // 2: "12:0:1"
      // 3: 17
      // 4: 4
      var temp = document.createElement('div');
      temp.innerHTML = d[i][0];
      var time = temp.firstElementChild.getAttribute('data-timestamp');
      var color_origin = temp.firstElementChild.getAttribute('style');
      color_origin = color_origin
        .replace('background-color:', '')
        .replace(';', '');
      if (!color_origin.includes('#'))
        color_origin = fullColorHex(color_origin);
      var res = {
        content: d[i][1],
        path: d[i][2],
        offset: d[i][3],
        length: d[i][4],
        timestamp: time,
        tag: window.mapTag[time], // map tag with timestamp
        color: color_origin,
      };
      out.push(res);
    }
    $.post('/confirm_info_extraction', {
      type: 'post',
      url: '/confirm_info_extraction',
      contentType: 'application/json;charset=UTF-8',
      dataType: 'json',
      data: JSON.stringify({
        res: out,
        action: 'accept',
        original_file: original_file,
        report_id: report_id,
        category: 4,
        type: 'latest_info_extraction',
      }),
    }).done(function (q) {
      alert('Your annotation has been successfully accepted!');
    });
  }
  hl_acceptBtn.addEventListener('click', confirm_info_extract);
  hl_rejectBtn.addEventListener('click', function () {
    load_latest_info_extraction_version(report_id);
  });
});
