"""81 il için statik sayfa üretir. Veriyi birtohum.github.io'daki kendi sitelerimden okur, kendisi veri toplamaz.
Çıktı: site/index.html, site/il/<ad>/index.html, site/veri/iller.json, site/veri/iller.csv
    python araclar/uret.py
"""
from __future__ import annotations

import csv
import html
import json
import math
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parent.parent
SITE = KOK / "site"
TABAN = "https://birtohum.github.io"
ADRES = TABAN + "/il-kimligi"
e = html.escape


def al(yol):
    r = urllib.request.Request(f"{TABAN}/{yol}", headers={"User-Agent": "il-kimligi (github.com/birtohum/il-kimligi)"})
    return json.load(urllib.request.urlopen(r, timeout=120))


def sayi(x, b=0):
    s = f"{abs(x):,.{b}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("−" if x < 0 else "") + s


def ek(s, e_):
    """Türkçe ek: ek('Sivas','da') -> Sivas'ta, ek('Rize','nin') -> Rize'nin"""
    k = s.replace("I", "ı").replace("İ", "i").lower()
    sesli = next((h for h in reversed(k) if h in "aıoueiöü"), "e")
    kalin, son = sesli in "aıou", k[-1]
    biter = son in "aıoueiöü"
    sert = son in "fstkçşhp"
    if e_ == "da":
        return f"{s}'{'t' if sert else 'd'}{'a' if kalin else 'e'}"
    if e_ == "dan":
        return f"{s}'{'t' if sert else 'd'}{'an' if kalin else 'en'}"
    if e_ == "nin":
        u = {"a": "ı", "ı": "ı", "e": "i", "i": "i", "o": "u", "u": "u", "ö": "ü", "ü": "ü"}[sesli]
        return f"{s}'{'n' if biter else ''}{u}n"
    raise ValueError(e_)


def slug(s):
    for a, b in zip("ıİşŞğĞüÜöÖçÇ", "iisSgGuUoOcC"):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def gunes(doy, lat, lon):
    """NOAA denklemleri; gün doğumu ve batımı (UTC+3, dakika). doy: 0 = 1 Ocak"""
    g = 2 * math.pi / 365 * doy
    eq = 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g) - 0.014615 * math.cos(2 * g) - 0.040849 * math.sin(2 * g))
    d = 0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g) - 0.006758 * math.cos(2 * g) + 0.000907 * math.sin(2 * g) - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g)
    r = math.radians
    c = math.cos(r(90.833)) / (math.cos(r(lat)) * math.cos(d)) - math.tan(r(lat)) * math.tan(d)
    ha = math.degrees(math.acos(max(-1, min(1, c))))
    return 720 - 4 * (lon + ha) - eq + 180, 720 - 4 * (lon - ha) - eq + 180


def saat(m):
    m = round(m)
    return f"{m // 60:02d}:{m % 60:02d}"


def guzel(s):
    """YILMAZ -> Yılmaz"""
    s = s.strip()
    return s[0] + s[1:].replace("I", "ı").replace("İ", "i").lower()


def topla():
    alti = {x["plaka"]: x for x in al("alti-ipucu/veri/iller.json")["iller"]}
    goc = al("goc-haritasi/veri/goc.json")
    soy = al("soyadin-nereli/veri/soyadlari.json")
    nufus = al("soyadin-nereli/veri/nufus2025.json")
    hava = al("kac-sigara/veri/veri.json")
    gece = al("turkiye-geceleri/veri/veri.json")
    dep = al("turkiye-sallandi/veri/ozet.json")
    sok = {int(x["p"]): x for x in al("sokak-adlari/veri/ozet.json")["iller"]}
    harita = al("goc-haritasi/veri/harita.json")
    hy = {x["plaka"]: x for x in hava["yillik"]}
    gy = {int(x["plaka"]): x for x in gece["iller"]}
    yillar = goc["yillar"]
    iller = []
    for i in range(81):
        p = i + 1
        a = alti[p]
        giden = gelen = 0
        for y in yillar:
            m = goc["akim"][str(y)]
            giden += sum(m[i * 81 + j] for j in range(81))
            gelen += sum(m[j * 81 + i] for j in range(81))
        ort = sum(goc["nufus"][str(y)][i] for y in yillar) / len(yillar)
        net = gelen - giden
        h = hy.get(p)
        s = sok[p]
        g = gy[p]
        kk = s["kadin"] + s["erkek"]
        d21, b21 = gunes(354, a["en"], a["boy"])
        d6, b6 = gunes(171, a["en"], a["boy"])
        d = dep["iller"][str(p)]
        iller.append({
            "p": p, "ad": a["ad"], "slug": slug(a["ad"]), "bolge": a["ipucu"].get("bolge", ""),
            "nufus": nufus[i], "giden": giden, "gelen": gelen, "net": net, "net_binde": round(net / ort / len(yillar) * 1000, 2),
            "pm": h["ortalama"] if h and h.get("siralamada") else None, "pm_gun": h["who_ustu_gun"] if h else None,
            "deprem": d["son365"], "deprem_max": a["ipucu"]["deprem"]["en_buyuk"],
            "yangin": a["ipucu"]["yangin"]["n"], "yangin_orman": a["ipucu"]["yangin"]["orman"], "yangin_yil": a["ipucu"]["yangin"]["yil"],
            "isik_artis": round((g["isik"][-1] / g["isik"][0] - 1) * 100) if g["isik"][0] else None,
            "sokak": s["sokak"], "numara_oran": round(s["numara"] / s["sokak"] * 100, 1) if s["sokak"] else None,
            "kadin": s["kadin"], "erkek": s["erkek"], "kadin_oran": round(s["kadin"] / kk * 100, 1) if kk >= 200 else None,
            "kisiler": s["kisiler"][:3], "kadinlar": s["kadinlar"][:3],
            "soy_ilk": guzel(soy["iller"][i][0][0]), "soy_ozel": guzel(soy["ozel"][i][0]) if soy["ozel"][i] else None,
            "gun21a": saat(d21), "bat21a": saat(b21), "gun21h": saat(d6), "bat21h": saat(b6), "gun21a_dk": round(d21),
            "d": next(x["d"] for x in harita["iller"] if x["kod"] == p),
        })
    return iller, harita, hava["guncelleme"][:10], dep["guncelleme"][:10]


# metrik: anahtar, başlık, biçim, yüksek uçta ifade, düşük uçta ifade, kaynak site
METRIK = [
 ("nufus", "Nüfus", lambda v: sayi(v), "nüfusu en kalabalık", "nüfusu en az", None),
 ("net_binde", "Net göç", lambda v: f"{'+' if v > 0 else ''}{sayi(v, 1)}‰", "en çok göç alan", "en çok göç veren", "goc-haritasi"),
 ("pm", "Hava kirliliği", lambda v: f"{sayi(v, 1)} µg/m³", "havası en kirli", "havası en temiz", "kac-sigara"),
 ("deprem", "Deprem, son 365 gün", lambda v: sayi(v), "en çok deprem kaydedilen", "en az deprem kaydedilen", "turkiye-sallandi"),
 ("yangin", "Uydunun gördüğü yangın, 2025", lambda v: sayi(v), "uydunun en çok yangın gördüğü", "uydunun en az yangın gördüğü", "orman-yanginlari-uzaydan"),
 ("isik_artis", "Gece ışığı artışı, 2012–2024", lambda v: f"{'+' if v > 0 else ''}%{sayi(v)}", "geceleri en hızlı aydınlanan", "gece ışığı en az artan", "turkiye-geceleri"),
 ("kadin_oran", "Kadın adlı sokak oranı", lambda v: f"%{sayi(v, 1)}", "sokaklarında kadın adı en sık geçen", "sokaklarında kadın adı en nadir geçen", "sokak-adlari"),
 ("numara_oran", "Yalnız numaralı sokak", lambda v: f"%{sayi(v)}", "sokakları en çok numarayla anılan", "sokakları en çok adıyla anılan", "sokak-adlari"),
]
ACIK = {"nufus": "2025, TÜİK", "net_binde": "2008–2025 yıllık ortalama, her 1.000 kişide. TÜİK", "pm": "Son bir yılın ince toz ortalaması. Bakanlık istasyonları",
        "deprem": "EMSC, AFAD, Kandilli. Küçük depremleri istasyon sıklığı da etkiler", "yangin": "NASA FIRMS sıcak noktaları", "isik_artis": "VIIRS uydu görüntüleri",
        "kadin_oran": "Açıkça bir kişiyi anan sokaklarda; en az 200 sokaklı iller. OpenStreetMap", "numara_oran": "Adı olmayan sokaklar. OpenStreetMap"}


def siralar(iller):
    S = {}
    for k, *_ in METRIK:
        v = sorted((x[k] for x in iller if x.get(k) is not None), reverse=True)
        S[k] = v
    return S


def sira(S, k, x):
    if x.get(k) is None:
        return None
    return S[k].index(x[k]) + 1


def serit(S, k, x):
    """81 ilin değer sırasını gösteren şerit: her çizgi bir il, parlayan bu il."""
    v, r = S[k], sira(S, k, x)
    if r is None:
        return ""
    n = len(v)
    W = 300
    cizgi = "".join(f'<rect x="{i / n * W:.1f}" y="4" width="{max(1.2, W / n - 1.2):.1f}" height="14"/>' for i in range(n) if i != r - 1)
    return f'<svg class="serit" viewBox="0 0 {W} 22" aria-hidden="true"><g>{cizgi}</g><rect class="bu" x="{(r - 1) / n * W:.1f}" y="0" width="{max(3, W / n):.1f}" height="22"/></svg>'


def uclar(iller, S, x):
    """Bu ili en çok öne çıkaran özellikler."""
    t = []
    for k, _, _, yuk, dus, _ in METRIK:
        r = sira(S, k, x)
        if r is None:
            continue
        n = len(S[k])
        if r <= n - r + 1:
            t.append((r, yuk, r, k))
        else:
            t.append((n - r + 1, dus, n - r + 1, k))
    t.sort(key=lambda a: (a[0], [m[0] for m in METRIK].index(a[3]) == 0))
    out = []
    for _, ifade, r, k in t:
        if k == "nufus" and r > 1:
            continue
        out.append(f"Türkiye'nin {ifade} ili" if r == 1 else f"{ifade[0].replace('i', 'İ').upper()}{ifade[1:]} {r}. il")
    return out[:3]


CSS = """
:root{--asfalt:#20242a;--asfalt2:#2a2f36;--yazi:#f3f4f6;--soluk:#a8afb9;--cizgi:#3a4048;--sari:#ffd21f;--mavi:#0a3d91;--plaka:#fff}
*{box-sizing:border-box}
body{margin:0;background:var(--asfalt);color:var(--yazi);font:16px/1.55 "Barlow",system-ui,sans-serif}
a{color:var(--sari)}
.sar{max-width:1040px;margin:0 auto;padding:0 16px}
.yol{height:6px;background:repeating-linear-gradient(90deg,var(--sari) 0 46px,transparent 46px 78px);margin:18px 0}
.ust{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:16px 0 0;font:600 .9rem "Barlow",sans-serif;color:var(--soluk)}
.ust a{color:var(--soluk);text-decoration:none}
.plaka{display:inline-flex;align-items:stretch;background:var(--plaka);color:#111;border:3px solid #111;border-radius:10px;overflow:hidden;font-family:"Saira Condensed","Oswald",sans-serif;font-weight:800;line-height:1;box-shadow:0 10px 30px -14px #000}
.plaka i{display:flex;align-items:flex-end;justify-content:center;background:var(--mavi);color:#fff;font-style:normal;font-size:.26em;padding:0 .38em .35em;min-width:1.3em;letter-spacing:.02em}
.plaka b{display:flex;align-items:center;gap:.28em;padding:.13em .3em .1em;font-weight:800;letter-spacing:.015em;white-space:nowrap;text-transform:uppercase}
.bas{padding:18px 0 4px}
.bas .plaka{font-size:min(104px,calc(86vw/(var(--n)*.5 + 2.5)))}
.bas h1{font:800 clamp(1.5rem,3.6vw,2.4rem)/1.15 "Saira Condensed","Barlow",sans-serif;margin:20px 0 6px;max-width:30ch}
.oz{list-style:none;padding:0;margin:0;display:flex;flex-wrap:wrap;gap:8px}
.oz li{background:var(--sari);color:#111;font-weight:600;padding:5px 12px;border-radius:4px;font-size:.95rem}
.kapsam{display:grid;grid-template-columns:1.25fr 1fr;gap:18px;margin-top:16px}
.harita svg{width:100%;height:auto;display:block}
.harita path{fill:#333941;stroke:var(--asfalt);stroke-width:.6}
.harita path.bu{fill:var(--sari)}
.ozet3{display:grid;gap:10px;align-content:start}
.kutu{background:var(--asfalt2);border:1px solid var(--cizgi);border-radius:8px;padding:12px 14px}
.kutu small{display:block;color:var(--soluk);font-size:.82rem}
.kutu b{font:800 1.5rem/1.15 "Saira Condensed",sans-serif}
.kart{list-style:none;padding:0;margin:26px 0 0}
.kart li{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,.8fr) minmax(0,1.5fr);gap:6px 18px;align-items:center;padding:14px 0;border-top:1px solid var(--cizgi)}
.kart h3{margin:0;font:600 1.02rem "Barlow",sans-serif}
.kart h3 a{color:inherit;text-decoration-color:var(--cizgi)}
.kart small{color:var(--soluk);font-size:.8rem;display:block}
.kart .deger{font:800 clamp(1.5rem,3vw,2.1rem)/1 "Saira Condensed",sans-serif;color:var(--sari);white-space:nowrap}
.sira-yazi{font-size:.82rem;color:var(--soluk)}
.serit{width:100%;height:auto;display:block}
.serit g{fill:#4a515b}.serit .bu{fill:var(--sari)}
h2{font:800 clamp(1.4rem,3vw,2rem) "Saira Condensed",sans-serif;margin:34px 0 10px}
.alt{color:var(--soluk);font-size:.9rem}
.komsu{display:flex;justify-content:space-between;gap:12px;margin:30px 0}
.komsu .plaka{font-size:min(26px,calc(40vw/(var(--n)*.5 + 2.5)))}
.komsu a{text-decoration:none}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin-top:14px}
.grid a{text-decoration:none;display:block}
.grid .plaka{font-size:min(28px,calc(172px/(var(--n)*.5 + 2.5)));width:100%;height:46px;align-items:stretch}
.grid .plaka b{flex:1}
.grid .plaka:hover,.grid a:focus-visible .plaka{outline:3px solid var(--sari);outline-offset:2px}
.ara{font:600 1.1rem "Barlow",sans-serif;width:100%;max-width:420px;min-height:50px;padding:0 16px;border-radius:8px;border:2px solid var(--cizgi);background:var(--asfalt2);color:var(--yazi)}
.en{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.en div{background:var(--asfalt2);border:1px solid var(--cizgi);border-radius:8px;padding:14px 16px}
.en h3{margin:0 0 8px;font:600 1rem "Barlow",sans-serif;color:var(--soluk)}
.en ol{margin:0;padding:0;list-style:none}
.en li{display:flex;justify-content:space-between;gap:10px;padding:3px 0}
.en li b{color:var(--sari);font-family:"Saira Condensed",sans-serif;font-size:1.15rem}
.dugme{font:700 1rem "Barlow",sans-serif;background:var(--sari);color:#111;border:0;border-radius:8px;padding:12px 18px;cursor:pointer;min-height:44px}
footer{padding:30px 0 40px;color:var(--soluk);font-size:.86rem;border-top:1px solid var(--cizgi);margin-top:30px}
footer a{color:var(--soluk)}
@media (max-width:720px){.kapsam{grid-template-columns:1fr}.kart li{grid-template-columns:1fr auto}.kart .seritk{grid-column:1/-1}.grid{grid-template-columns:repeat(auto-fill,minmax(160px,1fr))}.grid .plaka{font-size:min(22px,calc(136px/(var(--n)*.5 + 2.5)))}}
"""
FONT = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Saira+Condensed:wght@700;800&family=Barlow:wght@400;500;600;700&display=swap" rel="stylesheet">'
SAYAC = '<script data-goatcounter="https://birtohum.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>'


def plaka(x, tam=True):
    ad = x["ad"].replace("i", "i")
    ust = ad.replace("i", "İ").replace("ı", "I").upper()
    return f'<span class="plaka" style="--n:{len(ust)}"><i>TR</i><b><span>{x["p"]:02d}</span><span>{e(ust)}</span></b></span>'


def harita_svg(iller, H, x):
    yol = "".join(f'<path class="bu" d="{i["d"]}"/>' if i is x else f'<path d="{i["d"]}"/>' for i in sorted(iller, key=lambda i: i is x))
    return f'<svg viewBox="0 0 {H["w"]} {H["h"]}" role="img" aria-label="Türkiye haritasında {e(x["ad"])}">{yol}</svg>'


def il_sayfa(x, iller, H, S, tarih):
    uc = uclar(iller, S, x)
    satir = ""
    for k, bas, bic, _, _, kay in METRIK:
        r = sira(S, k, x)
        if r is None:
            satir += f'<li><div><h3>{bas}</h3><small>Yeterli veri yok</small></div><div class="deger">—</div><div></div></li>'
            continue
        h3 = f'<a href="{TABAN}/{kay}/">{bas}</a>' if kay else bas
        satir += (f'<li><div><h3>{h3}</h3><small>{ACIK[k]}</small></div><div class="deger">{bic(x[k])}</div>'
                  f'<div class="seritk">{serit(S, k, x)}<span class="sira-yazi">{len(S[k])} il içinde, en yüksekten {r}.</span></div></li>')
    kisiler = ", ".join(f"{e(a)} ({n})" for a, n in x["kisiler"]) or "—"
    kadinlar = ", ".join(f"{e(a)} ({n})" for a, n in x["kadinlar"]) or "kayıt yok"
    nb = ek(x["ad"], "nin")
    da = ek(x["ad"], "da")
    aciklama = f"{x['ad']} il kimliği: nüfus {sayi(x['nufus'])}, net göç, hava kirliliği, deprem, yangın, sokak adları ve soyadları. {uc[0] if uc else ''}."
    i = x["p"] - 1
    on, so = iller[(i - 1) % 81], iller[(i + 1) % 81]
    baslik = f"{uc[0]}." if uc else f"{x['ad']} sayılarla."
    return f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(x['ad'])} ({x['p']:02d}): il kimliği, göç, hava, deprem, sokak adları</title><meta name="description" content="{e(aciklama)}">
<meta property="og:title" content="{x['p']:02d} {e(x['ad'])}: {e(baslik)}"><meta property="og:description" content="{e(aciklama)}"><meta property="og:image" content="{ADRES}/og/{x['slug']}.png"><meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{ADRES}/il/{x['slug']}/"><link rel="icon" href="../../favicon.svg">{FONT}<link rel="stylesheet" href="../../stil.css"></head><body><div class="sar">
<div class="ust"><a href="../../">← 81 plaka</a><span>{e(x['bolge'])}</span></div>
<header class="bas">{plaka(x)}<h1>{e(baslik)}</h1><ul class="oz">{''.join(f'<li>{e(u)}</li>' for u in uc[1:])}</ul></header>
<div class="yol" aria-hidden="true"></div>
<div class="kapsam"><div class="harita" id="harita" data-p="{x['p']}" style="aspect-ratio:{H['w']}/{H['h']}"></div><div class="ozet3">
<div class="kutu"><small>En yaygın soyadı</small><b>{e(x['soy_ilk'])}</b></div>
<div class="kutu"><small><a href="{TABAN}/soyadin-nereli/">İlin kendine özgü soyadı</a></small><b>{e(x['soy_ozel'] or '—')}</b></div>
<div class="kutu"><small><a href="{TABAN}/gunes-kacta-doguyor/">21 Aralık'ta güneş</a></small><b>{x['gun21a']} – {x['bat21a']}</b><small>21 Haziran'da {x['gun21h']} – {x['bat21h']}</small></div>
</div></div>
<ul class="kart">{satir}</ul>
<h2>{e(nb)} sokakları kimin adını taşıyor?</h2>
<p>En çok: {kisiler}.<br>Kadınlar: {kadinlar}.</p><p class="alt">{sayi(x['sokak'])} sokak sayıldı. <a href="{TABAN}/sokak-adlari/">Yöntem ve sınırlar</a>.</p>
<p><button class="dugme" id="paylas" data-m="{x['p']:02d} {e(x['ad'])}: {e(baslik)}">Paylaş</button> <a href="{TABAN}/dogdugum-gun/">{e(da)} doğduğun gün hava nasıldı?</a></p>
<nav class="komsu" aria-label="Komşu plakalar"><a href="../{on['slug']}/">{plaka(on)}</a><a href="../{so['slug']}/">{plaka(so)}</a></nav>
<footer>Sayılar kendi sitelerimden derlendi, {e(tarih)} tarihli. Her satırın başlığı kaynağa gider. Sıralamalar verinin kapsamına bağlıdır; hava için ölçüm yeterli olmayan iller sıralanmaz. Kod ve veri: <a href="https://github.com/birtohum/il-kimligi">github.com/birtohum/il-kimligi</a> · <a href="{TABAN}/">birtohum</a></footer>
</div><script>fetch("../../veri/harita.json").then(r=>r.json()).then(H=>{{const k=document.getElementById("harita"),p=+k.dataset.p;const y=H.iller.slice().sort((a,b)=>(a.kod===p)-(b.kod===p)).map(i=>`<path ${{i.kod===p?'class="bu"':""}} d="${{i.d}}"/>`).join("");k.innerHTML=`<svg viewBox="0 0 ${{H.w}} ${{H.h}}" role="img" aria-label="Türkiye haritasında il konumu">${{y}}</svg>`}});document.getElementById("paylas").onclick=async function(){{const m=this.dataset.m,u=location.href;try{{if(navigator.share)await navigator.share({{text:m,url:u}});else{{await navigator.clipboard.writeText(m+" "+u);this.textContent="Kopyalandı"}}}}catch(_){{}}}};</script>{SAYAC}</body></html>"""


def ana(iller, S, tarih):
    grid = "".join(f'<a href="il/{x["slug"]}/" data-ad="{e(x["ad"].replace("I", "ı").replace("İ", "i").lower())}">{plaka(x)}</a>' for x in iller)
    en = ""
    for k, bas, bic, yuk, dus, _ in METRIK[1:]:
        for ifade, ters in ((yuk, False), (dus, True)):
            t = sorted((x for x in iller if x.get(k) is not None), key=lambda x: x[k], reverse=not ters)[:5]
            sat = "".join(f'<li><a href="il/{x["slug"]}/">{e(x["ad"])}</a><b>{bic(x[k])}</b></li>' for x in t)
            en += f"<div><h3>Türkiye'nin {ifade} illeri</h3><ol>{sat}</ol></div>"
    return f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>İlin Kimliği: 81 plaka, 81 il</title><meta name="description" content="Plakana dokun: ilinin nüfusu, göçü, havası, depremi, yangını, sokak adları ve soyadları tek sayfada; 81 il içinde kaçıncı olduğuyla.">
<meta property="og:title" content="81 plaka. Seninki hangisi?"><meta property="og:description" content="İlinin göçü, havası, depremi, sokak adları ve soyadları tek sayfada; 81 il içinde kaçıncı?"><meta property="og:image" content="{ADRES}/og/ana.png"><meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{ADRES}/"><link rel="icon" href="favicon.svg">{FONT}<link rel="stylesheet" href="stil.css"></head><body><div class="sar">
<header class="bas" style="padding-top:36px"><h1 style="font-size:clamp(3rem,9vw,6rem);line-height:.95;margin:0">81 plaka. <span style="color:var(--sari)">Seninki hangisi?</span></h1>
<p style="font-size:1.15rem;color:var(--soluk);max-width:58ch">İlinin nüfusu, göçü, havası, depremi, yangını, sokak adları ve soyadları tek sayfada; 81 il içinde kaçıncı olduğuyla.</p>
<label for="ara" style="position:absolute;left:-9999px">İl ara</label><input class="ara" id="ara" placeholder="İl ya da plaka yaz" autocomplete="off"></header>
<div class="yol" aria-hidden="true"></div>
<div class="grid" id="grid">{grid}</div>
<h2>En'ler</h2><div class="en">{en}</div>
<footer>Sayılar kendi sitelerimden derlendi (TÜİK, Bakanlık istasyonları, EMSC/AFAD/Kandilli, NASA FIRMS, VIIRS, OpenStreetMap), {e(tarih)} tarihli. <a href="veri/iller.csv">Bütün tablo (CSV)</a>. Kod: <a href="https://github.com/birtohum/il-kimligi">github.com/birtohum/il-kimligi</a> · <a href="{TABAN}/">birtohum</a></footer>
</div><script>const g=[...document.querySelectorAll("#grid a")];document.getElementById("ara").oninput=e=>{{const q=e.target.value.trim().replace(/I/g,"ı").replace(/İ/g,"i").toLowerCase();g.forEach((a,i)=>{{const p=String(i+1).padStart(2,"0");a.hidden=q&&!(a.dataset.ad.includes(q)||p.startsWith(q))}})}};</script>{SAYAC}</body></html>"""


def main():
    iller, H, t1, t2 = topla()
    tarih = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    S = siralar(iller)
    SITE.mkdir(exist_ok=True)
    (SITE / "stil.css").write_text(CSS, encoding="utf-8")
    (SITE / "favicon.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 20"><rect width="32" height="20" rx="3" fill="#fff" stroke="#111"/><rect width="7" height="20" rx="2" fill="#0a3d91"/></svg>', encoding="utf-8")
    (SITE / "index.html").write_text(ana(iller, S, tarih), encoding="utf-8")
    for x in iller:
        k = SITE / "il" / x["slug"]
        k.mkdir(parents=True, exist_ok=True)
        (k / "index.html").write_text(il_sayfa(x, iller, H, S, tarih), encoding="utf-8")
    (SITE / "veri").mkdir(exist_ok=True)
    temiz = [{k: v for k, v in x.items() if k != "d"} for x in iller]
    (SITE / "veri" / "harita.json").write_text(json.dumps({"w": H["w"], "h": H["h"], "iller": [{"kod": i["kod"], "d": i["d"]} for i in H["iller"]]}, separators=(",", ":")), encoding="utf-8")
    (SITE / "veri" / "iller.json").write_text(json.dumps(temiz, ensure_ascii=False, indent=0), encoding="utf-8")
    al_ = ["p", "ad", "nufus", "giden", "gelen", "net", "net_binde", "pm", "deprem", "deprem_max", "yangin", "yangin_orman", "isik_artis", "sokak", "numara_oran", "kadin", "erkek", "kadin_oran", "soy_ilk", "soy_ozel", "gun21a", "bat21a", "gun21h", "bat21h"]
    with open(SITE / "veri" / "iller.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=al_, extrasaction="ignore")
        w.writeheader()
        w.writerows(temiz)
    (SITE / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                      + f"<url><loc>{ADRES}/</loc></url>" + "".join(f"<url><loc>{ADRES}/il/{x['slug']}/</loc></url>" for x in iller) + "</urlset>", encoding="utf-8")
    for p in (52, 34, 6, 4):
        x = iller[p - 1]
        print(x["ad"], uclar(iller, S, x), x["net_binde"], x["pm"], x["kadin_oran"], x["isik_artis"], x["soy_ozel"], x["gun21a"])


if __name__ == "__main__":
    main()
