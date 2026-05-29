const DAT_HOSTS = ["one.dat.com", "power.dat.com", "login.dat.com"];

chrome.runtime.onInstalled.addListener(async () => {
  const existing = await chrome.storage.local.get(["streams"]);
  if (!existing.streams) {
    await chrome.storage.local.set({
      streams: [
        { label: "DAT One", url: "https://one.dat.com" },
        { label: "DAT Power", url: "https://power.dat.com" }
      ]
    });
  }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type === "open-url") {
    chrome.tabs.create({ url: message.url });
    sendResponse({ ok: true });
    return true;
  }

  if (message?.type === "count-dat-cookies") {
    countDatCookies().then(sendResponse);
    return true;
  }

  if (message?.type === "clear-dat-cookies") {
    clearDatCookies().then(sendResponse);
    return true;
  }

  return false;
});

async function countDatCookies() {
  const cookies = await getDatCookies();
  return { ok: true, count: cookies.length };
}

async function clearDatCookies() {
  const cookies = await getDatCookies();
  await Promise.all(cookies.map(removeCookie));
  return { ok: true, removed: cookies.length };
}

async function getDatCookies() {
  const groups = await Promise.all(
    DAT_HOSTS.map((domain) => chrome.cookies.getAll({ domain }))
  );
  const seen = new Set();
  const merged = [];

  for (const cookie of groups.flat()) {
    const key = `${cookie.storeId}:${cookie.domain}:${cookie.path}:${cookie.name}`;
    if (!seen.has(key)) {
      seen.add(key);
      merged.push(cookie);
    }
  }

  return merged;
}

function removeCookie(cookie) {
  const domain = cookie.domain.startsWith(".") ? cookie.domain.slice(1) : cookie.domain;
  const scheme = cookie.secure ? "https" : "http";
  const url = `${scheme}://${domain}${cookie.path}`;
  return chrome.cookies.remove({
    url,
    name: cookie.name,
    storeId: cookie.storeId
  });
}
