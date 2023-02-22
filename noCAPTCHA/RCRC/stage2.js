  var geetest_canvas_fullbg = document.getElementsByClassName(
    "geetest_canvas_fullbg geetest_fade geetest_absolute"
  );
  var geetest_canvas_slice = document.getElementsByClassName(
    "geetest_canvas_slice geetest_absolute"
  );
  if (geetest_canvas_fullbg.length > 0 && geetest_canvas_slice.length > 0) {
  geetest_canvas_slice[0].style.display = "none";
  geetest_canvas_slice[0].style.opacity = "0";
  geetest_canvas_fullbg[0].style.display = "none";
  geetest_canvas_fullbg[0].style.opacity = "0";
  }

