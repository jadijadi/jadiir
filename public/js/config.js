function exec_config() {
  const config = JSON.parse(Cookies.get("config"));

  Object.keys(config).map((key) => {
    const value = config[key];
    switch (key) {
      case "mouse":
        const html = document.getRootNode().documentElement;
        html.style = value ? "" : "cursor:none;pointer-events:none;";
        break;

      default:
    }
  });
}
