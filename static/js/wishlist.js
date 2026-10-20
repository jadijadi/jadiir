// Gift wish list: reads a Google Sheet (published as CSV) and renders it as cards.
//
// Usage in a page: <div id="wishlist" data-csv="CSV URL" data-currency="$"></div>
//
// Sheet columns (header row, any order, case-insensitive; only `name` is required):
//   name, price, link, link2, image, description, priority, status, category
//   priority: high / medium / low (or 1 / 2 / 3)
//   status:   empty / "available" = wanted, "reserved" = someone is buying it,
//             "purchased" = already bought (greyed out), "received" = got it
(function () {
  const root = document.getElementById("wishlist");
  if (!root) return;

  const csvUrl = (root.dataset.csv || "").trim();
  const currency = root.dataset.currency || "$";

  function parseCSV(text) {
    const rows = [];
    let row = [];
    let field = "";
    let inQuotes = false;
    for (let i = 0; i < text.length; i++) {
      const c = text[i];
      if (inQuotes) {
        if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
        else if (c === '"') inQuotes = false;
        else field += c;
      } else if (c === '"') {
        inQuotes = true;
      } else if (c === ",") {
        row.push(field); field = "";
      } else if (c === "\n" || c === "\r") {
        if (c === "\r" && text[i + 1] === "\n") i++;
        row.push(field); rows.push(row); row = []; field = "";
      } else {
        field += c;
      }
    }
    if (field !== "" || row.length) { row.push(field); rows.push(row); }
    return rows;
  }

  function toItems(rows) {
    if (!rows.length) return [];
    const header = rows[0].map((h) => h.trim().toLowerCase());
    return rows.slice(1)
      .map((r, index) => {
        const item = { index };
        header.forEach((h, i) => { item[h] = (r[i] || "").trim(); });
        return item;
      })
      .filter((item) => item.name);
  }

  function safeUrl(value) {
    if (!value) return null;
    try {
      const url = new URL(value);
      return url.protocol === "http:" || url.protocol === "https:" ? url.href : null;
    } catch (e) {
      return null;
    }
  }

  function priorityRank(value) {
    const v = (value || "").toLowerCase();
    if (v === "high" || v === "1") return 1;
    if (v === "low" || v === "3") return 3;
    return 2;
  }

  function statusOf(value) {
    const v = (value || "").toLowerCase();
    if (v === "received" || v === "got" || v === "done") return "received";
    if (v === "reserved") return "reserved";
    if (v === "purchased" || v === "bought") return "purchased";
    return "wanted";
  }

  function formatPrice(value) {
    if (!value) return "";
    const plain = value.replace(/,/g, "");
    if (/^\d+(\.\d+)?$/.test(plain)) {
      return currency + Number(plain).toLocaleString("en-US", { maximumFractionDigits: 2 });
    }
    return value;
  }

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }

  function linkButton(href) {
    const a = el("a", "wl-link", new URL(href).hostname.replace(/^www\./, ""));
    a.href = href;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    return a;
  }

  function card(item) {
    const status = statusOf(item.status);
    const article = el("article", "wl-card wl-" + status);

    const image = safeUrl(item.image);
    if (image) {
      const img = el("img", "wl-image");
      img.src = image;
      img.alt = item.name;
      img.loading = "lazy";
      img.referrerPolicy = "no-referrer";
      img.onerror = () => img.remove();
      article.appendChild(img);
    }

    const body = el("div", "wl-body");
    const badges = el("div", "wl-badges");
    if (status === "reserved") badges.appendChild(el("span", "wl-badge wl-badge-reserved", "Reserved"));
    if (status === "purchased") badges.appendChild(el("span", "wl-badge wl-badge-purchased", "Purchased"));
    if (status === "received") badges.appendChild(el("span", "wl-badge", "Received, thank you!"));
    if (status === "wanted" && priorityRank(item.priority) === 1) {
      badges.appendChild(el("span", "wl-badge wl-badge-top", "Most wanted"));
    }
    if (item.category) badges.appendChild(el("span", "wl-badge", item.category));
    if (badges.childNodes.length) body.appendChild(badges);

    const title = el("h3", "wl-name", item.name);
    body.appendChild(title);

    const price = formatPrice(item.price);
    if (price) body.appendChild(el("div", "wl-price", price));
    if (item.description) body.appendChild(el("p", "wl-description", item.description));

    const links = [item.link, item.link2].map(safeUrl).filter(Boolean);
    if (links.length) {
      const row = el("div", "wl-links");
      links.forEach((href) => row.appendChild(linkButton(href)));
      body.appendChild(row);
    }

    article.appendChild(body);
    return article;
  }

  function grid(items) {
    const div = el("div", "wl-grid");
    items.forEach((item) => div.appendChild(card(item)));
    return div;
  }

  function render(items) {
    const order = { wanted: 0, reserved: 1, purchased: 2 };
    const active = items
      .filter((item) => statusOf(item.status) !== "received")
      .sort((a, b) =>
        order[statusOf(a.status)] - order[statusOf(b.status)] ||
        priorityRank(a.priority) - priorityRank(b.priority) ||
        a.index - b.index);
    const received = items.filter((item) => statusOf(item.status) === "received");

    root.replaceChildren();
    if (!active.length) root.appendChild(el("p", "wl-message", "The list is empty right now. Check back later!"));
    else root.appendChild(grid(active));

    if (received.length) {
      const details = el("details", "wl-received");
      details.appendChild(el("summary", null, "Already received (" + received.length + ")"));
      details.appendChild(grid(received));
      root.appendChild(details);
    }
  }

  function message(text) {
    root.replaceChildren(el("p", "wl-message", text));
  }

  if (!csvUrl) {
    message("No sheet is connected yet.");
    return;
  }

  fetch(csvUrl, { cache: "no-store" })
    .then((response) => {
      if (!response.ok) throw new Error("HTTP " + response.status);
      return response.text();
    })
    .then((text) => render(toItems(parseCSV(text))))
    .catch((error) => {
      console.error("wishlist:", error);
      message("Sorry, I couldn't load the list right now. Please try again later.");
    });
})();
