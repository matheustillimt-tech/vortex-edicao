#!/usr/bin/env node
// Captura de tela pra usar nos motions (print e gravação), num Chrome próprio e isolado (Chrome for Testing).
// NÃO usa o seu navegador nem as suas contas: só páginas públicas. Página logada: grave você mesmo (OBS) ou tire print.
//
// Uso:
//   node capturar.mjs print  <url> <saida.png> [--largura 1440] [--altura 900] [--esconder "seletor,seletor"]
//   node capturar.mjs gravar <roteiro.json> <saida.mp4>
//
// roteiro.json:
// { "url": "https://...", "largura": 1440, "altura": 900, "esconder": ["header .avatar"],
//   "passos": [ {"espera": 1.5}, {"rola": 600}, {"passa": "texto ou seletor"}, {"clica": "Pricing"},
//               {"digita": ["input[name=q]", "texto"]}, {"espera": 2} ] }
//   "passa"/"clica" aceitam seletor CSS ou TEXTO visível. O cursor é desenhado na página (a gravação mostra o mouse).
import puppeteer from "puppeteer-core";
import { readFileSync, existsSync, readdirSync, unlinkSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { homedir } from "node:os";
import { join } from "node:path";

function chrome() {
  const base = join(homedir(), ".cache/puppeteer/chrome");
  for (const v of existsSync(base) ? readdirSync(base).sort().reverse() : []) {
    const p = join(base, v, "chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing");
    if (existsSync(p)) return p;
  }
  throw new Error("Chrome for Testing não encontrado em ~/.cache/puppeteer (rode: npx @puppeteer/browsers install chrome@stable)");
}

const CURSOR = `(() => { if (document.getElementById("__cur")) return;
  const c = document.createElement("div"); c.id = "__cur";
  c.innerHTML = '<svg width="28" height="28" viewBox="0 0 24 24"><path d="M4 2l16 9.5-7 1.5-3.5 6.5z" fill="#fff" stroke="#000" stroke-width="1.4" stroke-linejoin="round"/></svg>';
  Object.assign(c.style, {position:"fixed",left:"0",top:"0",zIndex:2147483647,pointerEvents:"none",transition:"transform .45s cubic-bezier(.3,.7,.2,1)",filter:"drop-shadow(0 2px 4px rgba(0,0,0,.4))"});
  document.body.appendChild(c);
  const r = document.createElement("div"); r.id = "__rip";
  Object.assign(r.style, {position:"fixed",width:"44px",height:"44px",margin:"-22px 0 0 -22px",borderRadius:"50%",border:"3px solid #fff",boxShadow:"0 0 0 2px rgba(0,0,0,.35)",opacity:"0",zIndex:2147483646,pointerEvents:"none",transition:"opacity .5s, transform .5s",transform:"scale(.3)"});
  document.body.appendChild(r);
  window.__move = (x, y) => { c.style.transform = "translate(" + x + "px," + y + "px)"; };
  window.__click = (x, y) => { r.style.left = x + "px"; r.style.top = y + "px"; r.style.transition = "none"; r.style.opacity = "1"; r.style.transform = "scale(.3)";
    requestAnimationFrame(() => { r.style.transition = "opacity .55s, transform .55s"; r.style.opacity = "0"; r.style.transform = "scale(1.6)"; }); };
})()`;

async function alvo(page, q) {
  try { const el = await page.$(q); if (el) return el; } catch {}
  const [el] = await page.$$(`xpath/.//*[normalize-space(text())=${JSON.stringify(q)}] | .//*[contains(normalize-space(.),${JSON.stringify(q)}) and not(*[contains(normalize-space(.),${JSON.stringify(q)})])]`);
  if (!el) throw new Error("não achei na página: " + q);
  return el;
}

async function centro(el) {
  await el.scrollIntoView();
  const b = await el.boundingBox();
  return [b.x + b.width / 2, b.y + b.height / 2];
}

async function esconde(page, seletores) {
  // banner de cookies: some da imagem SEM aceitar nada (nenhum clique em consentimento)
  await page.evaluate(() => {
    for (const el of document.querySelectorAll("body *")) {
      const cs = getComputedStyle(el);
      if ((cs.position === "fixed" || cs.position === "sticky") && /cookie|consent|privacidade|privacy/i.test(el.innerText || "") && el.innerText.length < 1500)
        el.style.setProperty("display", "none", "important");
    }
    for (const el of document.querySelectorAll('[id*="cookie" i],[class*="cookie" i],[id*="consent" i],[class*="consent" i],#onetrust-consent-sdk'))
      el.style.setProperty("display", "none", "important");
  });
  // dado pessoal / sensível: desfoca
  if (seletores?.length) await page.addStyleTag({ content: seletores.join(",") + "{filter:blur(12px)!important}" });
}

const [modo, a1, a2, ...resto] = process.argv.slice(2);
const opt = (k, d) => { const i = resto.indexOf("--" + k); return i >= 0 ? resto[i + 1] : d; };
const browser = await puppeteer.launch({ executablePath: chrome(), headless: true, args: ["--lang=pt-BR", "--hide-scrollbars"] });
const page = await browser.newPage();
try {
  if (modo === "print") {
    const W = +opt("largura", 1440), H = +opt("altura", 900);
    await page.setViewport({ width: W, height: H, deviceScaleFactor: 2 });
    await page.goto(a1, { waitUntil: "networkidle2", timeout: 60000 });
    await esconde(page, opt("esconder", "") ? opt("esconder").split(",") : []);
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: a2 });
    console.log("print:", a2);
  } else if (modo === "gravar") {
    const R = JSON.parse(readFileSync(a1, "utf8"));
    const W = R.largura || 1440, H = R.altura || 900;
    await page.setViewport({ width: W, height: H, deviceScaleFactor: 1 });
    await page.goto(R.url, { waitUntil: "networkidle2", timeout: 60000 });
    await esconde(page, R.esconder);
    await page.evaluate(CURSOR);
    let pos = [W * 0.5, H * 0.6];
    await page.evaluate((x, y) => window.__move(x, y), ...pos);
    const bruto = a2.replace(/\.[a-z0-9]+$/i, "") + "_bruto.webm";
    const rec = await page.screencast({ path: bruto });
    for (const p of R.passos || []) {
      if (p.espera) await new Promise(r => setTimeout(r, p.espera * 1000));
      if (p.rola) { await page.mouse.wheel({ deltaY: p.rola }); await new Promise(r => setTimeout(r, 700)); }
      if (p.passa || p.clica) {
        const el = await alvo(page, p.passa || p.clica);
        pos = await centro(el);
        await page.evaluate((x, y) => window.__move(x, y), ...pos);
        await new Promise(r => setTimeout(r, 650));
        await page.mouse.move(...pos);
        if (p.clica) { await page.evaluate((x, y) => window.__click(x, y), ...pos); await page.mouse.click(...pos); await new Promise(r => setTimeout(r, 900)); await page.evaluate(CURSOR); }
      }
      if (p.digita) { const [sel, txt] = p.digita; await (await alvo(page, sel)).click(); await page.keyboard.type(txt, { delay: 70 }); }
    }
    await new Promise(r => setTimeout(r, 800));
    await rec.stop();
    // o HyperFrames precisa de fps constante e duração no cabeçalho: converte pra MP4 30 fps
    execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-i", bruto, "-vf", "fps=30,scale=trunc(iw/2)*2:trunc(ih/2)*2", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", "-movflags", "+faststart", a2]);
    unlinkSync(bruto);
    console.log("gravação:", a2);
  } else {
    console.log("uso: capturar.mjs print <url> <saida.png> | gravar <roteiro.json> <saida.mp4>");
  }
} finally {
  await browser.close();
}
