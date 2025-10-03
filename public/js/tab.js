function new_tab(element, is_enter, goto_link = true) {
  const a = element.getElementsByClassName("selected")[0];
  if (!a) return;

  let name;
  if (element.id == "content") {
    name = a.textContent.replace("/", "");
  } else {
    name = a.textContent.split(" ");
    name.shift();
    name = name.join(" ");
  }

  const page = {
    link: a.href,
    name: name,
  };

  tabs = JSON.parse(Cookies.get("tabs"));

  check = tabs.find((t) => t.link == page.link);
  if (check) {
    if (goto_link) window.location.href = page.link;
    return;
  }

  tabs = is_enter ? tabs.filter((p) => p.link !== window.location.href) : tabs;
  tabs.push(page);
  Cookies.set("tabs", JSON.stringify(tabs));

  if (goto_link) window.location.href = page.link;
}

function del_tab(event) {
  const element = document.getElementById("tabs");
  let a;
  if (!event) {
    a = element.getElementsByClassName("selected")[0].firstElementChild;
  } else {
    a = event.target.previousElementSibling;
  }

  const page = {
    link: a.href,
    name: a.innerText,
  };

  tabs = JSON.parse(Cookies.get("tabs"));
  const new_tabs = tabs.filter((p) => p.link !== page.link);
  tabs = new_tabs.length > 0 ? new_tabs : tabs;
  Cookies.set("tabs", JSON.stringify(tabs));

  if (!event || page.link == window.location.href) {
    window.location.href = tabs[tabs.length - 1].link;
  } else {
    render_tabs();
  }
}

function next_tab() {
  const element = document.getElementById("tabs");
  const a = element.getElementsByClassName("selected")[0];

  const previous_element = a.previousElementSibling;
  const next_element = a.nextElementSibling;
  let url = "";

  if (!previous_element) {
    url = next_element.firstElementChild.href;
  } else if (!next_element) {
    url = previous_element.firstElementChild.href;
  } else {
    url =
      next_element.firstElementChild.href == document.referrer
        ? previous_element.firstElementChild.href
        : next_element.firstElementChild.href;
  }

  window.location.href = url;
}

function render_tabs() {
  new_tab(document.getElementById("files"), false, false);

  const tabs = JSON.parse(Cookies.get("tabs"));
  const tabs_container = document.getElementById("tabs");
  tabs_container.replaceChildren();

  tabs.forEach((tab) => {
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.href = tab.link;
    a.textContent = tab.name;

    const location = window.location.href.endsWith("/")
      ? window.location.href
      : window.location.href + "/";
    const link = tab.link.endsWith("/") ? tab.link : tab.link + "/";
    if (location == tab.link) {
      li.classList.add("selected");
    }

    const button = document.createElement("button");
    button.classList.add("closetab");
    button.textContent = "x";
    button.addEventListener("click", del_tab);

    tabs_container.appendChild(li);
    li.appendChild(a);
    li.appendChild(button);
  });
}
