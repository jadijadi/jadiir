function command() {
  const setter = document.getElementById("setter");
  const writer = document.getElementById("writer");
  const input = setter.value.substring(1).split(" ");
  const command = input[0];
  input.shift();
  const args = input.join("").replace(" ", "").split("=");

  if (
    typeof commands != "undefined" &&
    typeof commands[command] === "function"
  ) {
    commands[command](command);
  }

  switch (command) {
    case "help":
      window.location.href = "/readme";
      break;

    case "set":
      const success = set(args);
      setter.value = JSON.stringify(success);
      break;

    case "q":
      window.location.href = "https://search.ononoki.org";
      break;

    default:
      setter.value = JSON.stringify({
        type: "error",
        message: "command not found",
      });
  }
}

function set(args) {
  const error = {
    type: "error",
    message: "invalid param",
  };

  const success = {
    type: "success",
    message: "command executed",
  };

  let param = args[0];
  let value = args[1];

  if (value == "true" || value == "false") {
    value = value == "true" ? true : false;
  } else {
    return error;
  }

  let config = JSON.parse(Cookies.get("config"));
  config[param] = value;
  Cookies.set("config", JSON.stringify(config));

  exec_config();
  return success;
}
