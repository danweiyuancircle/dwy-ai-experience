#!/usr/bin/env node

const https = require("https");
const crypto = require("crypto");

function he(e) {
  let t = [],
    r = e.split("");
  for (var i = 0; i < r.length; i++) {
    0 != i && t.push(" ");
    let e = r[i].charCodeAt().toString(2);
    t.push(e);
  }
  return t.join("");
}

function fe(e) {
  let t = e.toString(),
    r = [[], [], [], []];
  for (var i = 0; i < t.length; i++) {
    let e = he(t[i]);
    (r[0] += e.slice(2, 3)),
      (r[1] += e.slice(3, 4)),
      (r[2] += e.slice(4, 5)),
      (r[3] += e.slice(5));
  }
  let a = [];
  for (i = 0; i < r.length; i++) {
    let e = parseInt(r[i], 2).toString(16);
    2 == e.length && (e = "0" + e),
      1 == e.length && (e = "00" + e),
      0 == e.length && (e = "000"),
      (a[i] = e);
  }
  let n = crypto.createHash("md5").update(t).digest("hex");
  return (
    n.slice(0, 3) +
    a[0] +
    n.slice(6, 11) +
    a[1] +
    n.slice(14, 19) +
    a[2] +
    n.slice(22, 27) +
    a[3] +
    n.slice(30)
  );
}

function aesDecrypt(encryptedB64, key) {
  const now = new Date();
  if (!key) {
    const dateStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
    key = crypto.createHash("md5").update(dateStr).digest("hex").substring(8, 24);
  }
  const keyBuf = Buffer.from(key, "utf-8");
  const decipher = crypto.createDecipheriv("aes-128-cbc", keyBuf, keyBuf);
  let decrypted = decipher.update(encryptedB64, "base64", "utf-8");
  decrypted += decipher.final("utf-8");
  return decrypted;
}

function httpGet(url) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { "User-Agent": "Mozilla/5.0", Referer: "https://www.olevod.com/" } }, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => resolve({ status: res.statusCode, body: data }));
    }).on("error", reject);
  });
}

async function fetchVodDetail(vodId) {
  const ts = Math.floor(Date.now() / 1000);
  const _vv = fe(ts);
  const url = `https://api.olelive.com/v1/pub/vod/detail/${vodId}/true?_vv=${_vv}`;
  const { status, body } = await httpGet(url);
  if (status !== 200) throw new Error(`API returned status ${status}: ${body}`);
  const json = JSON.parse(body);
  if (json.code !== 0) throw new Error(`API error: ${JSON.stringify(json)}`);
  let data = json.data;
  if (typeof data === "string") {
    try {
      data = JSON.parse(aesDecrypt(data));
    } catch {
      throw new Error("Failed to decrypt API response");
    }
  }
  return data;
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log("用法: node olevod-extract.js <视频URL或ID> [集数范围]");
    console.log("");
    console.log("示例:");
    console.log("  node olevod-extract.js https://www.olevod.com/player/vod/2-81723-20.html");
    console.log("  node olevod-extract.js 81723");
    console.log("  node olevod-extract.js 81723 1-5");
    console.log("  node olevod-extract.js 81723 3");
    process.exit(0);
  }

  let vodId;
  const input = args[0];
  const urlMatch = input.match(/\/(\d+)-(\d+)-(\d+)\.html/);
  if (urlMatch) {
    vodId = urlMatch[2];
  } else if (/^\d+$/.test(input)) {
    vodId = input;
  } else {
    console.error("无法解析视频ID，请输入URL或纯数字ID");
    process.exit(1);
  }

  let rangeStart = 1,
    rangeEnd = Infinity;
  if (args[1]) {
    if (args[1].includes("-")) {
      const [s, e] = args[1].split("-").map(Number);
      rangeStart = s;
      rangeEnd = e;
    } else {
      rangeStart = rangeEnd = parseInt(args[1]);
    }
  }

  const detail = await fetchVodDetail(vodId);
  const urls = detail.urls || [];

  const episodes = urls.filter((ep) => ep.index >= rangeStart && ep.index <= rangeEnd);
  if (episodes.length === 0) {
    console.error(`指定范围 ${rangeStart}-${rangeEnd} 内没有可下载的集数`);
    process.exit(1);
  }

  for (const ep of episodes) {
    console.log(`${ep.index}\t${ep.title}\t${ep.url}`);
  }
}

main().catch((e) => {
  console.error("错误:", e.message);
  process.exit(1);
});
