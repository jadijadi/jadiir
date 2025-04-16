function writeit(from, event) {
  const w = document.getElementById("writer");
  let value;
  try {
    value = JSON.parse(from.value);
  } catch (e) {
    value = from.value;
  }

  if (value.type) {
    const color = value.type == "error" ? "#C62828" : "#689F38";

    w.innerHTML = `<span style="color:${color};">${value.message.replaceAll(" ", "&nbsp")}</span>`;
  } else if (value.startsWith(":")) {
    w.innerHTML = value.replaceAll(" ", "&nbsp");
  } else {
    value = "";
  }
}

function moveIt(count, event) {
  let keycode = event.keyCode || event.which;

  cursor.style.display = count == 0 ? "none" : "block";

  left = parseInt(cursor.style.left);
  cursor_width = "3px";

  if (keycode == 37 && left >= 0 - (count - 1) * 13) {
    cursor.style.left = left - 13 + "px";
  } else if (keycode == 39 && left + 13 <= 0) {
    cursor.style.left = left + 13 + "px";
  } else {
    cursor_width = "13px";
  }

  cursor.style.width = cursor_width;
}
