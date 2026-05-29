const statusEl = document.getElementById("status");
const cookieCountEl = document.getElementById("cookieCount");
const streamsEl = document.getElementById("streams");
const streamLabel = document.getElementById("streamLabel");
const streamUrl = document.getElementById("streamUrl");

document.querySelectorAll("[data-url]").forEach((button) => {
  button.addEventListener("click", () => openUrl(button.dataset.url));
});

document.getElementById("refresh").addEventListener("click", refreshCookieCount);
document.getElementById("clear").addEventListener("click", clearDatCookies);
document.getElementById("saveStream").addEventListener("click", saveShortcut);

refreshCookieCount();
renderShortcuts();

function send(type, payload = {}) {
  return chrome.runtime.sendMessage({ type, ...payload });
}

async function openUrl(url) {
  await send("open-url", { url });
  statusEl.textContent = "Opened " + url;
}

async function refreshCookieCount() {
  const result = await send("count-dat-cookies");
  cookieCountEl.textContent = result.count;
  statusEl.textContent = "Local DAT cookie count refreshed";
}

async function clearDatCookies() {
  const confirmed = confirm("Clear local DAT cookies in this browser profile?");
  if (!confirmed) {
    return;
  }
  const result = await send("clear-dat-cookies");
  cookieCountEl.textContent = "0";
  statusEl.textContent = `Removed ${result.removed} local DAT cookies`;
}

async function saveShortcut() {
  const label = streamLabel.value.trim();
  const url = streamUrl.value.trim();
  if (!label || !url.startsWith("https://")) {
    statusEl.textContent = "Enter a label and https URL";
    return;
  }

  const { streams = [] } = await chrome.storage.local.get(["streams"]);
  streams.push({ label, url });
  await chrome.storage.local.set({ streams });
  streamLabel.value = "";
  streamUrl.value = "";
  statusEl.textContent = "Shortcut saved";
  renderShortcuts();
}

async function renderShortcuts() {
  const { streams = [] } = await chrome.storage.local.get(["streams"]);
  streamsEl.replaceChildren();

  for (const [index, stream] of streams.entries()) {
    const row = document.createElement("div");
    row.className = "shortcut";

    const label = document.createElement("span");
    label.textContent = stream.label;
    label.title = stream.url;

    const open = document.createElement("button");
    open.textContent = "Open";
    open.addEventListener("click", () => openUrl(stream.url));

    const remove = document.createElement("button");
    remove.textContent = "Remove";
    remove.addEventListener("click", async () => {
      streams.splice(index, 1);
      await chrome.storage.local.set({ streams });
      renderShortcuts();
    });

    row.append(label, open, remove);
    streamsEl.append(row);
  }
}
