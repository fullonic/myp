// MAPPING SERVICE

$(document).ready(function() {

  $('#form-map').on('submit', function(event) {
    event.preventDefault();

    var progressDiv = document.getElementById("progress");
    progressDiv.classList.remove("d-none");

    var download_file = document.getElementById("download_file");



    var mappingSubmit = document.getElementById("submitBtn");
    $("#mappingSubmit").attr('disabled', true).text("Uploading...").html(
      `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...`
    );

    var formData = new FormData($('#form-map')[0]);

    $.ajax({
      xhr: function() {
        var xhr = new window.XMLHttpRequest();
        xhr.upload.addEventListener('progress', function(e) {

          if (e.lengthComputable) {

            var percent = Math.round((e.loaded / e.total) * 100);

            $('#progressBar').attr('aria-valuenow', percent).css('width', percent + '%').text(percent + '%');
            $('#loading').text(percent + '%');
            console.log(percent);
            if (percent === 100) {
              $("#mappingSubmit").text("Generating map files....");
              mappingSubmit.classList.add("btn-danger");
            };

          }
        });
        return xhr;
      },
      type: 'POST',
      url: "/mapping",
      data: formData,
      processData: false,
      contentType: false,
      success: function() {
        nFiles();
        $("#mappingSubmit").attr('disabled', true).text("Upload Complete!");
        mappingSubmit.classList.remove("btn-danger");
        mappingSubmit.classList.add("btn-success");
        alert('File uploaded!');
        download_file.classList.remove("d-none");
      }
    });

  });

});

// MAP BY GPX

$(document).ready(function() {

  $('#form-track').on('submit', function(event) {
    event.preventDefault();

    var progressDiv = document.getElementById("progress");
    progressDiv.classList.remove("d-none");


    var submitBtnGPX = document.getElementById("submitBtnGPX");
    $("#submitBtnGPX").attr('disabled', true).text("Uploading...").html(
      `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...`
    );

    var formData = new FormData($('#form-track')[0]);

    $.ajax({
      xhr: function() {
        var xhr = new window.XMLHttpRequest();
        xhr.upload.addEventListener('progress', function(e) {

          if (e.lengthComputable) {

            var percent = Math.round((e.loaded / e.total) * 100);

            $('#progressBar').attr('aria-valuenow', percent).css('width', percent + '%').text(percent + '%');
            $('#loading').text(percent + '%');
            console.log(percent);
            if (percent === 100) {
              $("#submitBtnGPX").text("Generating map files....");
              submitBtnGPX.classList.add("btn-danger");
            };

          }
        });
        return xhr;
      },
      type: 'POST',
      url: "/map_by_track",
      data: formData,
      processData: false,
      contentType: false,
      success: function() {
        nFiles();
        $("#submitBtnGPX").attr('disabled', true).text("Upload Complete!");
        submitBtnGPX.classList.remove("btn-danger");
        submitBtnGPX.classList.add("btn-success");
        // GET URL FOR DOWNLOAD FILE
        getFile();
        alert('File uploaded!');
        var btn = document.getElementById('download_file');
        btn.classList.remove("d-none");
      }
    });

  });
});


function nFiles() {
  var label = document.getElementsByTagName("label");
  $("").css("content", "files");
};


function getFile() {
  var project_name = document.getElementById("project_name").value;

  $.ajax({
    type: 'POST',
    url: "/get_file/" + project_name + "/",
    data: project_name,
    processData: false,
    contentType: false,
    success: function(msg) {
      var btn = document.getElementById('download_file');
      var url_ = "/get_file/" + msg["url"] + "/";
      console.log(url_);
      btn.href = url_
    }
  });
}



$(document).ready(function() {

  $('#form-mapping').on('submit', function(event) {
    event.preventDefault();

    var progressDiv = document.getElementById("progress");
    progressDiv.classList.remove("d-none");

    var map = document.getElementById("showMap");



    var submitButton = document.getElementById("submitBtn");
    $("#submitBtn").attr('disabled', true).text("Uploading...").html(
      `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...`
    );

    var formData = new FormData($('#form-mapping')[0]);

    $.ajax({
      xhr: function() {
        var xhr = new window.XMLHttpRequest();
        xhr.upload.addEventListener('progress', function(e) {

          if (e.lengthComputable) {

            var percent = Math.round((e.loaded / e.total) * 100);

            $('#progressBar').attr('aria-valuenow', percent).css('width', percent + '%').text(percent + '%');
            $('#loading').text(percent + '%');
            console.log(percent);
            if (percent === 100) {
              $("#submitBtn").text("Generating map files....");
              submitButton.classList.add("btn-danger");
            };

          }
        });
        return xhr;
      },
      type: 'POST',
      url: "/create_map",
      data: formData,
      processData: false,
      contentType: false,
      success: function() {
        nFiles();
        $("#submitBtn").attr('disabled', true).text("Upload Complete!");
        submitButton.classList.remove("btn-danger");
        submitButton.classList.add("btn-success");
        alert('File uploaded!');
        map.classList.remove("d-none");
      }
    });

  });

});
