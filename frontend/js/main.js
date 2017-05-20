function xhrGet(url, callback) {
  var xhr = new XMLHttpRequest();
  xhr.onreadystatechange = function() { 
    if (xhr.readyState == 4 && xhr.status == 200)
      callback(xhr.responseText);
  }
  xhr.open("GET", url, true);
  xhr.send(null);
};

var url = 'https://ydo07btybj.execute-api.eu-west-1.amazonaws.com/dev/ramblings/';

xhrGet(url, function(response) {
  var data = JSON.parse(response);
  var itemsDiv = document.getElementById('items')
  for(var i=0; i < data.length; i++) {
    var item = '<div class="item">' + data[i]['text'] + '</div>';
    itemsDiv.innerHTML = itemsDiv.innerHTML + item;
  }
});
