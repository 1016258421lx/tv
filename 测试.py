# -*- coding: utf-8 -*-
"""
MissAV_TuT.py

由 MissAV_TuT.js 的实际逻辑改写为 FongMi/CatVod/WebHTV Python Spider。
目标运行环境：WebHTV/FongMi 的 Chaquopy Python Spider。

注意：
1. 这是 Python Spider，不是普通 requests 爬虫。
2. 站点配置使用 type=3，api 指向本文件，例如 ./MissAV_TuT.py。
3. 本文件保留原 JS 的主要站点探测、分类、搜索、详情、HLS、请求头、封面
   以及 JavTrailers 辅助逻辑；Widget.http / Widget.html 已改为 requests + bs4。
"""

import re
import time
from urllib.parse import quote, urljoin, urlparse, unquote

import requests
from bs4 import BeautifulSoup

try:
    from base.spider import Spider as BaseSpider
except Exception:
    class BaseSpider:
        pass


class Spider(BaseSpider):
    USER_AGENT = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 "
        "Mobile/15E148 Safari/604.1"
    )

    SITE_CANDIDATES = [
        "https://missav.fans",
        "https://missav.media",
        "https://missav.ai",
        "https://missav.ws",
        "https://missav.live",
    ]

    ACTRESS_ENDPOINTS = [('瀬户环奈', 'dm179/cn/actresses/%E7%80%AC%E6%88%B8%E7%92%B0%E5%A5%88'), ('逢泽みゆ', 'dm179/cn/actresses/%E9%80%A2%E6%B2%A2%E3%81%BF%E3%82%86'), ('河北彩花', 'dm179/cn/actresses/%E6%B2%B3%E5%8C%97%E5%BD%A9%E8%8A%B1'), ('松本一香', 'dm179/cn/actresses/%E6%9D%BE%E6%9C%AC%E4%B8%80%E9%A6%99'), ('美园和花', 'dm179/cn/actresses/%E7%BE%8E%E5%9B%AD%E5%92%8C%E8%8A%B1'), ('北冈果林', 'dm179/cn/actresses/%E5%8C%97%E5%B2%A1%E6%9E%9C%E6%9E%97'), ('柏木こなつ', 'dm179/cn/actresses/%E6%9F%8F%E6%9C%A8%E3%81%93%E3%81%AA%E3%81%A4'), ('浅野こころ', 'dm179/cn/actresses/%E6%B5%85%E9%87%8E%E3%81%93%E3%81%93%E3%82%8D'), ('北野未奈', 'dm179/cn/actresses/%E5%8C%97%E9%87%8E%E6%9C%AA%E5%A5%88'), ('清原みゆう', 'dm179/cn/actresses/%E6%B8%85%E5%8E%9F%E3%81%BF%E3%82%86%E3%81%86'), ('沙月惠奈', 'dm179/cn/actresses/%E6%B2%99%E6%9C%88%E6%83%A0%E5%A5%88'), ('miru', 'dm179/cn/actresses/miru'), ('七森莉莉', 'dm179/cn/actresses/%E4%B8%83%E6%A3%AE%E8%8E%89%E8%8E%89'), ('七濑爱丽丝', 'dm179/cn/actresses/%E4%B8%83%E6%BF%91%E7%88%B1%E4%B8%BD%E4%B8%9D'), ('鹫尾芽衣', 'dm179/cn/actresses/%E9%B9%AB%E5%B0%BE%E8%8A%BD%E8%A1%A3'), ('博多彩叶', 'dm179/cn/actresses/%E5%8D%9A%E5%A4%9A%E5%BD%A9%E5%8F%B6'), ('石川澪', 'dm179/cn/actresses/%E7%9F%B3%E5%B7%9D%E6%BE%AA'), ('白上咲花', 'dm179/cn/actresses/%E7%99%BD%E4%B8%8A%E5%92%B2%E8%8A%B1'), ('田野忧', 'dm179/cn/actresses/%E7%94%B0%E9%87%8E%E5%BF%A7'), ('未步なな', 'dm179/cn/actresses/%E6%9C%AA%E6%AD%A5%E3%81%AA%E3%81%AA'), ('村上悠华', 'dm179/cn/actresses/%E6%9D%91%E4%B8%8A%E6%82%A0%E5%8D%8E'), ('三田真铃', 'dm179/cn/actresses/%E4%B8%89%E7%94%B0%E7%9C%9F%E9%93%83'), ('八挂うみ', 'dm179/cn/actresses/%E5%85%AB%E6%8E%9B%E3%81%86%E3%81%BF'), ('初美なのか', 'dm179/cn/actresses/%E5%88%9D%E7%BE%8E%E3%81%AA%E3%81%AE%E3%81%8B'), ('宫下玲奈', 'dm179/cn/actresses/%E5%AE%AE%E4%B8%8B%E7%8E%B2%E5%A5%88'), ('新有菜', 'dm58/actresses/%E6%A9%8B%E6%9C%AC%E6%9C%89%E8%8F%9C%20%28%E6%96%B0%E6%9C%89%E8%8F%9C%29'), ('新木希空', 'dm179/cn/actresses/%E6%96%B0%E6%9C%A8%E5%B8%8C%E7%A9%BA'), ('明里つむぎ', 'dm179/cn/actresses/%E6%98%8E%E9%87%8C%E3%81%A4%E3%82%80%E3%81%8E'), ('小野六花', 'dm179/cn/actresses/%E5%B0%8F%E9%87%8E%E5%85%AD%E8%8A%B1'), ('宇都宫紫苑', 'dm179/cn/actresses/%E5%AE%87%E9%83%BD%E5%AE%AE%E7%B4%AB%E8%8B%91'), ('小宵こなん', 'dm179/cn/actresses/%E5%B0%8F%E5%AE%B5%E3%81%93%E3%81%AA%E3%82%93'), ('本庄鈴', 'dm179/cn/actresses/%E6%9C%AC%E5%BA%84%E9%88%B4'), ('桃乃木かな', 'dm179/cn/actresses/%E6%A1%83%E4%B9%83%E6%9C%A8%E3%81%8B%E3%81%AA'), ('桜空もも', 'dm179/cn/actresses/%E6%A1%9C%E7%A9%BA%E3%82%82%E3%82%82'), ('楓ふうあ', 'dm179/cn/actresses/%E6%A1%AB%E3%81%B5%E3%81%86%E3%81%82'), ('楓カレン', 'dm179/cn/actresses/%E6%A5%93%E3%82%AB%E3%83%AC%E3%83%B3'), ('涼森れむ', 'dm179/cn/actresses/%E6%B6%BC%E6%A3%AE%E3%82%8C%E3%82%80'), ('瀧本雫葉', 'dm179/cn/actresses/%E7%80%A7%E6%9C%AC%E9%9B%AB%E8%91%89'), ('田中レモン', 'dm179/cn/actresses/%E7%94%B0%E4%B8%AD%E3%83%AC%E3%83%A2%E3%83%B3'), ('相沢みなみ', 'dm179/cn/actresses/%E7%9B%B8%E6%B2%A2%E3%81%BF%E3%81%AA%E3%81%BF'), ('神木麗', 'dm179/cn/actresses/%E7%A5%9E%E6%9C%A8%E9%BA%97'), ('美ノ嶋めぐり', 'dm179/cn/actresses/%E7%BE%8E%E3%83%8E%E5%B6%8B%E3%82%81%E3%81%90%E3%82%8A'), ('野々浦暖', 'dm179/cn/actresses/%E9%87%8E%E3%80%85%E6%B5%A6%E6%9A%96'), ('青空ひかり', 'dm179/cn/actresses/%E9%9D%92%E7%A9%BA%E3%81%B2%E3%81%8B%E3%82%8A'), ('三上悠亚', 'dm179/cn/actresses/%E4%B8%89%E4%B8%8A%E6%82%A0%E4%BA%9A'), ('榊原萌', 'dm179/cn/actresses/%E6%A6%8A%E5%8E%9F%E8%90%8C'), ('彩月七绪', 'dm179/cn/actresses/%E5%BD%A9%E6%9C%88%E4%B8%83%E7%BB%AA'), ('神宫寺奈绪', 'dm179/cn/actresses/%E7%A5%9E%E5%AE%AB%E5%AF%BA%E5%A5%88%E7%BB%AA'), ('有村のぞみ', 'dm179/cn/actresses/%E6%9C%89%E6%9D%91%E3%81%AE%E3%81%9E%E3%81%BF')]
    GENRES_ENDPOINTS = [('高清', 'dm96/cn/genres/%E9%AB%98%E6%B8%85'), ('独家', 'dm139/cn/genres/%E7%8B%AC%E5%AE%B6'), ('中出', 'dm130/cn/genres/%E4%B8%AD%E5%87%BA'), ('单体作品', 'dm122/cn/genres/%E5%8D%95%E4%BD%93%E4%BD%9C%E5%93%81'), ('巨乳', 'dm120/cn/genres/%E5%B7%A8%E4%B9%B3'), ('人妻', 'dm77/cn/genres/%E4%BA%BA%E5%A6%BB'), ('熟女', 'dm118/cn/genres/%E7%86%9F%E5%A5%B3'), ('素人', 'dm123/cn/genres/%E7%B4%A0%E4%BA%BA'), ('美少女', 'dm437/cn/genres/%E7%BE%8E%E5%B0%91%E5%A5%B3'), ('口交', 'dm1301/cn/genres/%E5%8F%A3%E4%BA%A4'), ('多人运动', 'dm321/cn/genres/%E5%A4%9A%E4%BA%BA%E8%BF%90%E5%8A%A8'), ('薄格', 'dm76/cn/genres/%E8%96%84%E6%A0%BC'), ('骑乘', 'dm486/cn/genres/%E9%AA%91%E4%B9%98'), ('痴女', 'dm313/cn/genres/%E7%97%B4%E5%A5%B3'), ('4小时以上', 'dm738/cn/genres/4%E5%B0%8F%E6%97%B6%E4%BB%A5%E4%B8%8A'), ('女高中生', 'dm4448/cn/genres/%E5%A5%B3%E9%AB%98%E4%B8%AD%E7%94%9F'), ('潮吹', 'dm161/cn/genres/%E6%BD%AE%E5%90%B9'), ('苗条', 'dm757/cn/genres/%E8%8B%97%E6%9D%A1'), ('自拍', 'dm978/cn/genres/%E8%87%AA%E6%8B%8D'), ('合集', 'dm784/cn/genres/%E5%90%88%E9%9B%86'), ('乳交', 'dm594/cn/genres/%E4%B9%B3%E4%BA%A4'), ('恋物癖', 'dm117/cn/genres/%E6%81%8B%E7%89%A9%E7%99%96'), ('美乳', 'dm215/cn/genres/%E7%BE%8E%E4%B9%B3'), ('NTR', 'dm736/cn/genres/NTR'), ('企划', 'dm341/cn/genres/%E4%BC%81%E5%88%92'), ('乱伦', 'dm56/cn/genres/%E4%B9%B1%E4%BC%A6'), ('搭讪', 'dm292/cn/genres/%E6%90%AD%E8%AE%AA'), ('颜射', 'dm319/cn/genres/%E9%A2%9C%E5%B0%84'), ('淫乱', 'dm903/cn/genres/%E6%B7%AB%E4%B9%B1'), ('偷拍', 'dm516/cn/genres/%E5%81%B7%E6%8B%8D'), ('剧情', 'dm98/cn/genres/%E5%89%A7%E6%83%85'), ('自慰', 'dm7606/cn/genres/%E8%87%AA%E6%85%B0'), ('4K', 'dm55/cn/genres/4K'), ('手淫', 'dm94/cn/genres/%E6%89%8B%E6%B7%AB'), ('姐姐', 'dm793/cn/genres/%E5%A7%90%E5%A7%90'), ('羞辱', 'dm161/cn/genres/%E7%BE%9E%E8%BE%B1')]
    MAKERS_ENDPOINTS = [("Moody's", 'dm825/cn/makers/Moody%27s'), ('Prestige', 'dm825/cn/makers/Prestige'), ('Madonna', 'dm825/cn/makers/Madonna'), ('S1', 'dm825/cn/makers/S1'), ('SOD', 'dm825/cn/makers/SOD'), ('IdeaPocket', 'dm825/cn/makers/IdeaPocket'), ('Attackers', 'dm825/cn/makers/Attackers'), ('Glory Quest', 'dm825/cn/makers/Glory%20Quest'), ('ビッグモーカル', 'dm825/cn/makers/%E3%83%93%E3%83%83%E3%82%B0%E3%83%A2%E3%83%BC%E3%82%AB%E3%83%AB'), ('NATURAL HIGH', 'dm825/cn/makers/NATURAL%20HIGH'), ('Wanz Factory', 'dm825/cn/makers/Wanz%20Factory'), ('Takara Visual', 'dm825/cn/makers/Takara%20Visual'), ('Fc2', 'dm825/cn/makers/Fc2'), ('Premium', 'dm825/cn/makers/Premium'), ('Fitch', 'dm825/cn/makers/Fitch'), ('VENUS', 'dm825/cn/makers/VENUS'), ("DEEP'S", 'dm825/cn/makers/DEEP%27S'), ('本中', 'dm825/cn/makers/%E6%9C%AC%E4%B8%AD'), ('Hunter', 'dm825/cn/makers/Hunter'), ('溜池ゴロー', 'dm825/cn/makers/%E6%BA%9C%E6%B1%A0%E3%82%B4%E3%83%AD%E3%83%BC'), ('TMA', 'dm825/cn/makers/TMA'), ('センタービレッジ', 'dm825/cn/makers/%E3%82%BB%E3%83%B3%E3%82%BF%E3%83%BC%E3%83%93%E3%83%AC%E3%83%83%E3%82%B8'), ('Das', 'dm825/cn/makers/Das'), ('Waap Entertainment', 'dm825/cn/makers/Waap%20Entertainment'), ('Crystal-Eizou', 'dm825/cn/makers/Crystal-Eizou'), ('kawaii', 'dm825/cn/makers/kawaii'), ('ゴーゴーズ', 'dm825/cn/makers/%E3%82%B4%E3%83%BC%E3%82%B4%E3%83%BC%E3%82%BA'), ('プラネットプラス', 'dm825/cn/makers/%E3%83%97%E3%83%A9%E3%83%8D%E3%83%83%E3%83%88%E3%83%97%E3%83%A9%E3%82%B9'), ('OPPAI', 'dm825/cn/makers/OPPAI'), ('STAR PARADISE', 'dm825/cn/makers/STAR%20PARADISE'), ('E-BODY', 'dm825/cn/makers/E-BODY'), ('セレブの友', 'dm825/cn/makers/%E3%82%BB%E3%83%AC%E3%83%96%E3%81%AE%E5%8F%8B'), ('ドグマ', 'dm825/cn/makers/%E3%83%89%E3%82%B0%E3%83%9E'), ('Alice Japan', 'dm825/cn/makers/Alice%20Japan'), ('KM Produce', 'dm825/cn/makers/KM%20Produce'), ('桃太郎映像出版', 'dm825/cn/makers/%E6%A1%83%E5%A4%AA%E9%83%8E%E6%98%A0%E5%83%8F%E5%87%BA%E7%89%88')]

    def __init__(self):
        self.extend = ""
        self.base_url = "https://missav.fans"
        self.resolved_site = ""
        self.session = requests.Session()
        self.people_avatar_cache = {}
        self.video_url_cache = {}
        self.image_cache = {}
        self.jav_cache = {}
        self._site_checked = False
        self.headers = {
            "User-Agent": self.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-TW,zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://missav.fans/",
            "Connection": "keep-alive",
        }

    # ------------------------------------------------------------------
    # 生命周期
    # ------------------------------------------------------------------
    def init(self, extend=""):
        self.extend = extend or ""
        # 允许通过 ext 直接指定站点，例如 https://missav.ws
        if isinstance(self.extend, dict):
            ext_url = self.extend.get("url") or self.extend.get("base_url") or ""
        else:
            ext_url = str(self.extend).strip()
        if ext_url.startswith("http://") or ext_url.startswith("https://"):
            self.base_url = ext_url.rstrip("/")
            self.resolved_site = self.base_url
            self.headers["Referer"] = self.base_url + "/"

    def destroy(self):
        try:
            self.session.close()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # HTTP / HTML
    # ------------------------------------------------------------------
    def _get(self, url, headers=None, timeout=12):
        h = dict(self.headers)
        if headers:
            h.update(headers)
        last = None
        for attempt in range(3):
            try:
                r = self.session.get(url, headers=h, timeout=timeout, allow_redirects=True)
                r.encoding = r.apparent_encoding or r.encoding
                return r
            except Exception as e:
                last = e
                if attempt < 2:
                    time.sleep(0.25 * (attempt + 1))
        raise last

    def _head(self, url, headers=None, timeout=2):
        h = dict(self.headers)
        if headers:
            h.update(headers)
        try:
            return self.session.head(url, headers=h, timeout=timeout, allow_redirects=True)
        except Exception:
            return None

    @staticmethod
    def _soup(html):
        return BeautifulSoup(html or "", "html.parser")

    @staticmethod
    def _text(value):
        return re.sub(r"\s+", " ", str(value or "")).strip()

    @staticmethod
    def _status(title, subtitle=""):
        return {"vod_id": "", "vod_name": title, "vod_remarks": subtitle}

    def _is_cf(self, html):
        raw = str(html or "")
        if not raw.strip():
            return False
        lower = raw.lower()
        has_cards = (
            "text-secondary" in lower or "thumbnail" in lower or
            "videodetails" in lower or "surrit" in lower
        )
        if has_cards and len(raw) > 12000:
            return False
        challenge_title = re.search(
            r"<title[^>]*>\s*(just a moment|attention required|please wait)",
            raw, re.I,
        )
        human = any(x in lower for x in (
            "verify you are human",
            "performing security verification",
            "checking your browser before accessing",
            "cf-browser-verification",
        ))
        return bool(challenge_title or (human and len(raw) < 20000))

    def _looks_like_site(self, html):
        if not html or self._is_cf(html):
            return False
        raw = str(html)
        return any(x in raw.lower() for x in (
            "text-secondary", "thumbnail", "fourhoi", "surrit"
        ))

    def _ensure_site(self):
        if self.resolved_site:
            return self.resolved_site
        for host in self.SITE_CANDIDATES:
            try:
                url = host + "/dm539/cn/new"
                r = self._get(url, headers={"Referer": host + "/"}, timeout=8)
                if self._looks_like_site(r.text):
                    self.base_url = host
                    self.resolved_site = host
                    self.headers["Referer"] = host + "/"
                    return host
            except Exception:
                continue
        self.resolved_site = self.base_url
        self.headers["Referer"] = self.base_url + "/"
        return self.base_url

    def _resolve(self, path):
        if not path:
            return ""
        path = str(path).strip()
        if path.startswith("http://") or path.startswith("https://"):
            # 保留 MissAV 镜像切换能力
            return re.sub(r"^https?://missav\.[a-z0-9.-]+", self.base_url, path, flags=re.I)
        return self.base_url.rstrip("/") + "/" + path.lstrip("/")

    # ------------------------------------------------------------------
    # MissAV 列表/分类
    # ------------------------------------------------------------------
    def _extract_video_id(self, href):
        if not href:
            return ""
        clean = str(href).split("#", 1)[0].split("?", 1)[0]
        slug = clean.rstrip("/").split("/")[-1]
        return re.sub(r"-(uncensored-leak|chinese-subtitle)$", "", slug, flags=re.I).upper()

    def _card_elements(self, soup):
        cards = soup.select("div[class*='thumbnail']")
        if not cards:
            cards = soup.select("div.group, div[class*='-group']")
        return cards

    def _card_link(self, card):
        link = card.select_one("a[class*='text-secondary']")
        if not link:
            link = card.select_one("a[href*='/cn/'], a[href*='/en/'], a[href*='/ja/']")
        return link

    def _duration(self, card):
        el = card.select_one("[class*='bottom-1'][class*='right-1']")
        return self._text(el.get_text(" ", strip=True) if el else "")

    @staticmethod
    def _fourhoi(video_id):
        if not video_id:
            return []
        v = str(video_id).lower()
        return [
            f"https://fourhoi.mrstcdn.store/{v}/cover-t.jpg",
            f"https://fourhoi.mrstcdn.store/{v}/cover-n.jpg",
            f"https://fourhoi.com/{v}/cover-t.jpg",
        ]

    @staticmethod
    def _usable_image(url):
        raw = str(url or "").strip()
        if not raw or raw.startswith("data:"):
            return False
        if re.search(r"\.(mp4|webm|m3u8|ts)(?:\?|$)", raw, re.I):
            return False
        return bool(re.search(r"\.(jpg|jpeg|png|webp|gif)(?:\?|$)", raw, re.I) or
                    re.search(r"cover|poster|pl\.jpg|ps\.jpg|thumbnail", raw, re.I))

    def _card_image(self, card, video_id):
        for img in card.select("img"):
            for attr in ("data-src", "data-original", "data-lazy", "src"):
                value = img.get(attr, "")
                if self._usable_image(value):
                    return value.strip()
        fs = self._fourhoi(video_id)
        return fs[0] if fs else ""

    # ------------------------------------------------------------------
    # 番号 / 高清封面规则（按原 JS 保留）
    # ------------------------------------------------------------------
    MGSTAGE_COVER_RULES = {
        "ABF": "prestige", "ABW": "prestige", "ABP": "prestige", "CHN": "prestige",
        "JUFE": "prestige", "MAAN": "prestige", "PPT": "prestige", "390JAC": "jackson",
    }

    def _jav_parts(self, title):
        raw = str(title or "").upper()
        m = re.search(r"\b([A-Z0-9]+)-?(\d{2,5})\b", raw)
        if not m:
            return None
        prefix, number = m.group(1), m.group(2)
        number5 = number.zfill(5)
        prefix_map = {
            "WSA": "2",
            "FSDSS": "1", "FCDSS": "1", "FNS": "1", "FTHTD": "1",
            "FALENO": "1", "FGAN": "1", "FSNF": "1", "FLAV": "1",
            "ABP": "118", "CHN": "118",
            "STARS": "1", "STAR": "1", "START": "1", "SODS": "1",
            "REBD": "h_346", "REBDB": "h_346", "GSHRB": "h_346",
        }
        pre = prefix_map.get(prefix, "")
        return {
            "prefix": prefix, "prefixLower": prefix.lower(), "number": number,
            "number3": number.zfill(3), "number5": number5,
            "code": f"{pre}{prefix.lower()}{number5}",
            "plainCode": f"{prefix.lower()}{number5}",
        }

    def _cover_candidates(self, value):
        p = self._jav_parts(value)
        if not p:
            return [], []
        prefix = p["prefix"]
        if prefix in self.MGSTAGE_COVER_RULES:
            maker = self.MGSTAGE_COVER_RULES[prefix]
            base = f"https://image.mgstage.com/images/{maker}/{p['prefixLower']}/{int(p['number'])}"
            dvd = f"{p['prefixLower']}-{int(p['number'])}"
            return [f"{base}/pf_e_{dvd}.jpg", f"{base}/pf_o1_{dvd}.jpg"], \
                   [f"{base}/pb_e_{dvd}.jpg", f"{base}/pb_o1_{dvd}.jpg"]
        code = p["code"].lower()
        a = f"https://awsimgsrc.dmm.co.jp/pics_dig/digital/video/{code}"
        b = f"https://pics.dmm.co.jp/digital/video/{code}"
        return [f"{a}/{code}ps.jpg", f"{b}/{code}ps.jpg"], [f"{a}/{code}pl.jpg", f"{b}/{code}pl.jpg"]

    def _pick_image(self, candidates, fallback=""):
        for url in candidates:
            if url in self.image_cache:
                if self.image_cache[url]:
                    return url
                continue
            r = self._head(url, headers={
                "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
                "Referer": "https://missav.ai/",
            }, timeout=1.2)
            ok = bool(r is not None and 200 <= r.status_code < 400)
            self.image_cache[url] = ok
            if ok:
                return url
        return fallback

    def _covers(self, value):
        posters, backs = self._cover_candidates(value)
        special = {
            "ABF-354": "https://image.mgstage.com/images/prestige/abf/354/pb_e_abf-354.jpg"
        }.get(re.sub(r"[\s_-]+", "-", str(value or "").upper()))
        return posters, backs, special

    # ------------------------------------------------------------------
    # 列表解析
    # ------------------------------------------------------------------
    def _people_item(self, name, avatar="", href=""):
        title = self._text(name)
        if not title:
            return None
        pid = self._normalize_people_id(href) or "cn/actresses/" + quote(title)
        return {"id": pid, "title": title, "avatar": self._resolve(avatar) if avatar else "", "role": "主演"}

    def _normalize_people_id(self, value):
        if not value:
            return ""
        s = str(value).strip()
        s = s.replace(self.base_url, "")
        s = re.sub(r"^https?://[^/]+/", "", s)
        return s.lstrip("/").split("?", 1)[0].rstrip("/")

    def _parse_list(self, html, include_images=False, current_people=None, current_genre=None):
        if not html:
            return [self._status("加载失败", "分类页没有返回内容")]
        if self._is_cf(html):
            return [self._status("被 Cloudflare 拦截", "分类页未通过验证，请稍后重试")]
        soup = self._soup(html)
        results = []
        for card in self._card_elements(soup):
            link = self._card_link(card)
            href = link.get("href", "") if link else ""
            if not href:
                continue
            href = self._resolve(href)
            title = self._text(link.get_text(" ", strip=True))
            duration = self._duration(card)
            video_id = self._extract_video_id(href)
            posters, backs, special = self._covers(video_id)
            img = self._card_image(card, video_id)
            four = self._fourhoi(video_id)
            fallback = img or (four[0] if four else "")
            poster = posters[0] if posters else fallback
            backdrop = special or self._pick_image(backs, fallback)
            item = {
                "vod_id": href,
                "vod_name": title,
                "vod_pic": backdrop or poster,
                "vod_remarks": duration,
                "vod_content": f"时长: {duration}" + (f" | 番号: {video_id}" if video_id else ""),
                "type_name": "电影",
                "coverUrl": backdrop or poster,
                "detailPoster": poster,
                "link": href,
            }
            people = []
            if current_people:
                people.append(current_people)
            for a in card.select("a[href*='/actresses/'], a[href*='actresses']"):
                p = self._people_item(a.get_text(" ", strip=True), self._img_of(a), a.get("href", ""))
                if p and not any(x["id"] == p["id"] or x["title"].replace(" ", "").lower() == p["title"].replace(" ", "").lower() for x in people):
                    people.append(p)
            if people:
                item["peoples"] = people
            if current_genre:
                item["genreItems"] = [current_genre]
            if include_images:
                item.update({"posterPath": poster, "backdropPath": backdrop, "image": backdrop})
            results.append(item)
        return results or [self._status("没有找到相关视频", "该分类当前没有可解析的影片卡片")]

    @staticmethod
    def _img_of(element):
        img = element.select_one("img")
        return (img.get("data-src") or img.get("src") or "") if img else ""

    # ------------------------------------------------------------------
    # 分类
    # ------------------------------------------------------------------
    def _build_list_url(self, endpoint, page=1, sort_by="", filters=""):
        params = []
        if filters:
            params.append("filters=" + quote(str(filters), safe=""))
        if sort_by:
            params.append("sort=" + quote(str(sort_by), safe=""))
        if int(page or 1) > 1:
            params.append("page=" + str(page))
        return self._resolve(endpoint) + (("?" + "&".join(params)) if params else "")

    def _endpoint_for(self, tid, extend):
        direct = {"recent_updates": "dm539/cn/new", "chinese": "dm278/cn/chinese-subtitle", "release": "dm632/cn/release"}
        if tid in direct:
            return direct[tid]
        # 传入 filter 里的具体 endpoint
        if isinstance(extend, dict):
            for k in ("url", "endpoint", "actress", "genre", "maker", "category"):
                v = extend.get(k)
                if v and ("/" in str(v) or str(v).startswith("dm")):
                    return str(v)
        if isinstance(extend, str) and "/" in extend:
            return extend
        groups = {
            "subtitle": "dm278/cn/chinese-subtitle",
            "japan": "dm632/cn/release",
            "amateur": "dm36/cn/siro",
            "uncensored": "dm816/cn/uncensored-leak",
            "asia": "dm63/cn/madou",
        }
        return groups.get(tid, "dm632/cn/release")

    def _selected_endpoint(self, tid, extend):
        if not isinstance(extend, dict):
            return self._endpoint_for(tid, extend)
        for key in ("actress", "genre", "maker", "category", "endpoint", "url"):
            val = extend.get(key)
            if val:
                return val
        return self._endpoint_for(tid, extend)

    # ------------------------------------------------------------------
    # 首页
    # ------------------------------------------------------------------
    def homeContent(self, filter):
        # 完整保留原 MissAV_TuT.js 的“一级分类 + 细分类/排序”结构。
        # 原 JS 中每个一级分类的 endpoint 本身就是细分类入口，因此这里
        # 用 FongMi/TVBox 标准 filters 暴露出来，而不是只保留一级分类。
        classes = [
            {"type_id": "recent_updates", "type_name": "最近更新"},
            {"type_id": "subtitle", "type_name": "中文字幕"},
            {"type_id": "japan", "type_name": "日本AV"},
            {"type_id": "amateur", "type_name": "素人"},
            {"type_id": "uncensored", "type_name": "无码影片"},
            {"type_id": "asia", "type_name": "亚洲AV"},
            {"type_id": "actress", "type_name": "女优"},
            {"type_id": "genre", "type_name": "类型"},
            {"type_id": "maker", "type_name": "发行商"},
        ]

        sorts = [
            {"n": "发行日期", "v": "released_at"},
            {"n": "最近更新", "v": "published_at"},
            {"n": "收藏数", "v": "saved"},
            {"n": "今日浏览数", "v": "today_views"},
            {"n": "本周浏览数", "v": "weekly_views"},
            {"n": "本月浏览数", "v": "monthly_views"},
            {"n": "总浏览数", "v": "views"},
        ]

        def values(items):
            return [{"n": "全部", "v": ""}] + [{"n": n, "v": v} for n, v in items]

        filters = {
            # 中文字幕：原 JS 的 3 个细筛选 + 排序
            "subtitle": [
                {"key": "endpoint", "name": "内容", "init": "dm278/cn/chinese-subtitle", "value": values([
                    ("中文字幕", "dm278/cn/chinese-subtitle"),
                ])},
                {"key": "filters", "name": "筛选", "init": "", "value": values([
                    ("单人作品", "individual"),
                    ("多人作品", "multiple"),
                    ("中文字幕", "chinese-subtitle"),
                ])},
                {"key": "sort_by", "name": "排序", "init": "released_at", "value": sorts},
            ],
            # 日本AV：最新发布 / 本周热门 / 月度热门
            "japan": [
                {"key": "endpoint", "name": "分类", "init": "dm632/cn/release", "value": [
                    {"n": "最新发布", "v": "dm632/cn/release"},
                    {"n": "本周热门", "v": "dm170/cn/weekly-hot"},
                    {"n": "月度热门", "v": "dm266/cn/monthly-hot"},
                ]},
                {"key": "sort_by", "name": "排序", "init": "released_at", "value": sorts},
            ],
            # 素人
            "amateur": [
                {"key": "endpoint", "name": "分类", "init": "dm36/cn/siro", "value": [
                    {"n": "SIRO", "v": "dm36/cn/siro"},
                    {"n": "LUXU", "v": "dm34/cn/luxu"},
                    {"n": "GANA", "v": "dm32/cn/gana"},
                    {"n": "PRESTIGE PREMIUM", "v": "dm999/cn/maan"},
                    {"n": "S-CUTE", "v": "dm38/cn/scute"},
                    {"n": "ARA", "v": "dm34/cn/ara"},
                ]},
                {"key": "sort_by", "name": "排序", "init": "released_at", "value": sorts},
            ],
            # 无码影片
            "uncensored": [
                {"key": "endpoint", "name": "分类", "init": "dm816/cn/uncensored-leak", "value": [
                    {"n": "无码流出", "v": "dm816/cn/uncensored-leak"},
                    {"n": "FC2", "v": "dm473/cn/fc2"},
                    {"n": "HEYZO", "v": "dm1977446/cn/heyzo"},
                    {"n": "东京热", "v": "dm42/cn/tokyohot"},
                    {"n": "一本道", "v": "dm4364834/cn/1pondo"},
                    {"n": "Caribbeancom", "v": "dm7414012/cn/caribbeancom"},
                    {"n": "Caribbeancompr", "v": "dm83900/cn/caribbeancompr"},
                    {"n": "10musume", "v": "dm6341956/cn/10musume"},
                    {"n": "pacopacomama", "v": "dm2479243/cn/pacopacomama"},
                    {"n": "Gachinco", "v": "dm150/cn/gachinco"},
                    {"n": "XXX-AV", "v": "dm42/cn/xxxav"},
                    {"n": "人妻斩", "v": "dm37/cn/marriedslash"},
                    {"n": "顽皮4610", "v": "dm33/cn/naughty4610"},
                    {"n": "顽皮0930", "v": "dm37/cn/naughty0930"},
                ]},
                {"key": "sort_by", "name": "排序", "init": "released_at", "value": sorts},
            ],
            # 亚洲AV
            "asia": [
                {"key": "endpoint", "name": "分类", "init": "dm63/cn/madou", "value": [
                    {"n": "麻豆传媒", "v": "dm63/cn/madou"},
                    {"n": "TWAV", "v": "dm31/cn/twav"},
                    {"n": "Furuke", "v": "dm15/cn/furuke"},
                    {"n": "韩国直播", "v": "cn/klive"},
                    {"n": "中国直播", "v": "cn/clive"},
                ]},
                {"key": "sort_by", "name": "排序", "init": "released_at", "value": sorts},
            ],
            # 女优 / 类型 / 发行商：完整使用原 JS 中已有的长列表
            "actress": [
                {"key": "actress", "name": "女优", "init": "", "value": values(self.ACTRESS_ENDPOINTS)},
                {"key": "sort_by", "name": "排序", "init": "released_at", "value": sorts},
            ],
            "genre": [
                {"key": "genre", "name": "类型", "init": "", "value": values(self.GENRES_ENDPOINTS)},
                {"key": "sort_by", "name": "排序", "init": "released_at", "value": sorts},
            ],
            "maker": [
                {"key": "maker", "name": "发行商", "init": "", "value": values(self.MAKERS_ENDPOINTS)},
                {"key": "sort_by", "name": "排序", "init": "released_at", "value": sorts},
            ],
            "recent_updates": [
                {"key": "sort_by", "name": "排序", "init": "published_at", "value": sorts},
            ],
        }

        # 不管调用方是否显式传 filter，都把完整 filters 返回。
        # 某些 WebHTV/TVBox 前端只有收到 filters 才会显示“细分类”按钮。
        return {"class": classes, "filters": filters}

    def homeVideoContent(self):
        return self.categoryContent("recent_updates", "1", False, {})

    def categoryContent(self, tid, pg, filter, extend):
        self._ensure_site()
        page = int(pg or 1)
        ext = dict(extend) if isinstance(extend, dict) else {}
        # 不同版本的 WebHTV/TVBox 会把筛选项放到 filter 或 extend，
        # 两边都兼容，避免“细分类能显示但点了没有切换”。
        if isinstance(filter, dict):
            for k, v in filter.items():
                if v not in (None, ""):
                    ext[k] = v
        endpoint = self._selected_endpoint(tid, ext)
        # 女优/类型/发行商没有选择具体项目时，使用原 JS 的第一项作为默认入口；
        # 一旦 extend 有具体值，则直接进入对应页面。
        if tid == "actress" and not (isinstance(ext, dict) and (ext.get("actress") or ext.get("peopleId"))):
            endpoint = self.ACTRESS_ENDPOINTS[0][1]
        elif tid == "genre" and not (isinstance(ext, dict) and (ext.get("genre") or ext.get("genreId"))):
            endpoint = self.GENRES_ENDPOINTS[0][1]
        elif tid == "maker" and not (isinstance(ext, dict) and (ext.get("maker") or ext.get("endpoint") or ext.get("url"))):
            endpoint = self.MAKERS_ENDPOINTS[0][1]
        sort_by = "published_at" if tid == "recent_updates" else ""
        if isinstance(ext, dict):
            sort_by = ext.get("sort") or ext.get("sort_by") or sort_by
        url = self._build_list_url(endpoint, page, sort_by)
        try:
            r = self._get(url, timeout=15)
            current_people = None
            current_genre = None
            if isinstance(ext, dict):
                people_id = ext.get("actress") or ext.get("peopleId")
                genre_id = ext.get("genre") or ext.get("genreId")
                if people_id:
                    endpoint = str(people_id)
                    url = self._build_list_url(endpoint, page, sort_by)
                    r = self._get(url, timeout=15)
                    title = unquote(str(people_id).rstrip("/").split("/")[-1])
                    current_people = {"id": self._normalize_people_id(people_id), "title": title, "avatar": "", "role": "主演"}
                elif genre_id:
                    endpoint = str(genre_id)
                    url = self._build_list_url(endpoint, page, sort_by)
                    r = self._get(url, timeout=15)
                    title = unquote(str(genre_id).rstrip("/").split("/")[-1])
                    current_genre = {"id": self._normalize_people_id(genre_id), "title": title}
            return {"list": self._parse_list(r.text, current_people=current_people, current_genre=current_genre)}
        except Exception as e:
            return {"list": [self._status("加载失败", str(e))]}

    # ------------------------------------------------------------------
    # 搜索
    # ------------------------------------------------------------------
    def searchContent(self, key, quick=False, pg="1"):
        self._ensure_site()
        page = int(pg or 1)
        url = self._resolve("cn/search/" + quote(str(key or "")))
        if page > 1:
            url += "?page=" + str(page)
        try:
            r = self._get(url, timeout=15)
            return {"list": self._parse_list(r.text)}
        except Exception as e:
            return {"list": [self._status("搜索失败", str(e))]}

    # ------------------------------------------------------------------
    # 播放地址
    # ------------------------------------------------------------------
    @staticmethod
    def _valid_hls(body, status=None):
        if status and not 200 <= int(status) < 400:
            return False
        text = str(body or "")
        if "#EXTM3U" not in text:
            return False
        return any(x in text for x in ("#EXTINF", "#EXT-X-STREAM-INF", "#EXT-X-TARGETDURATION", "#EXT-X-MAP"))

    def _play_headers(self, referer):
        return {"Referer": referer or self.base_url + "/", "User-Agent": self.USER_AGENT, "Origin": self.base_url}

    def _probe_hls(self, url, referer, timeout=2):
        try:
            r = self._get(url, headers=self._play_headers(referer), timeout=timeout)
            return self._valid_hls(r.text, r.status_code)
        except Exception:
            return False

    @staticmethod
    def _unpack_packer(html):
        if not html:
            return ""
        out = []
        regex = re.compile(r"eval\s*\(\s*function\s*\(\s*p\s*,\s*a\s*,\s*c\s*,\s*k\s*,\s*e\s*,\s*d\s*\)[\s\S]+?\}\s*\(\s*'([\s\S]+?)'\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*'([\s\S]+?)'[\s\S]+?\)", re.I)
        for m in regex.finditer(html):
            try:
                p, a, c, k = m.group(1).replace("\\'", "'"), int(m.group(2)), int(m.group(3)), m.group(4).split("|")
                for idx in range(c - 1, -1, -1):
                    if idx < len(k) and k[idx]:
                        p = re.sub(r"\b" + re.escape(format(idx, "x")) + r"\b", k[idx], p)
                out.append(p)
            except Exception:
                pass
        return "\n".join(out)

    def _extract_video_url(self, html):
        if not html:
            return ""
        soup = self._soup(html)
        for script in soup.find_all("script"):
            content = script.string or script.get_text() or ""
            if "surrit" in content.lower() and ".m3u8" in content:
                ms = re.findall(r"https://surrit\.[^\"'\\\s]+/[a-f0-9\-]+/[^\"'\s]*\.m3u8", content, re.I)
                if ms:
                    return next((x.replace("\\/", "/") for x in ms if "1080p" in x.lower()), next((x.replace("\\/", "/") for x in ms if "720p" in x.lower()), ms[0].replace("\\/", "/")))
            if "eval(function" in content:
                unpacked = self._unpack_packer(content)
                ms = re.findall(r"https://surrit\.[^\"'\\\s]+/[a-f0-9\-]+/[^\"'\s]*\.m3u8", unpacked, re.I)
                if ms:
                    return ms[0].replace("\\/", "/")
                hu = re.search(r"https:\\?/\\?/(surrit\.[^\"'\\\s]+)/(\w{8}-\w{4}-\w{4}-\w{4}-\w{12})", content, re.I)
                if hu:
                    return f"https://{hu.group(1)}/{hu.group(2)}/playlist.m3u8"
                um = re.findall(r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}", content, re.I)
                if um:
                    return f"https://surrit.mrstcdn.store/{um[0]}/playlist.m3u8"
        raw = html.replace("\\/", "/")
        m = re.search(r"https://surrit\.[^\"'\\\s]+/[a-f0-9\-]+/[^\"'\s]*\.m3u8", raw, re.I)
        if m:
            return m.group(0)
        hu = re.search(r"https://(surrit\.[^/]+)/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})", raw, re.I)
        if hu:
            return f"https://{hu.group(1)}/{hu.group(2)}/playlist.m3u8"
        m = re.search(r"source\s*=\s*['\"]([^'\"]+)['\"]", raw, re.I)
        return m.group(1) if m else ""

    def _surrit_variants(self, master, base):
        out=[]; seen=set(); lines=master.splitlines()
        for i,line in enumerate(lines):
            if not line.strip().startswith("#EXT-X-STREAM-INF"):
                continue
            if i+1 >= len(lines): continue
            path=lines[i+1].strip()
            if not path or path.startswith("#"): continue
            url=urljoin(base.rstrip("/")+"/", path)
            if url in seen: continue
            seen.add(url)
            m=re.search(r"RESOLUTION=\d+x(\d+)",line,re.I)
            h=int(m.group(1)) if m else 0
            out.append((h, f"{h}P" if h else "AUTO", url))
        return sorted(out, reverse=True)

    def _surrit_resources(self, video_url, code, referer):
        m = re.search(r"https://(surrit\.[^/]+)/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})", video_url, re.I)
        if not m:
            return []
        base = f"https://{m.group(1)}/{m.group(2)}"
        headers = self._play_headers(referer)
        master = base + "/playlist.m3u8"
        results=[]; seen=set()
        try:
            r=self._get(master,headers=headers,timeout=5)
            if self._valid_hls(r.text,r.status_code):
                results.append({"name":f"{str(code).upper()} - 最高(AUTO)","url":master,"description":f"番号：{str(code).upper()} | MissAV master 自适应最高","parse":0,"header":headers})
                for h,name,url in self._surrit_variants(r.text,base):
                    if url in seen: continue
                    seen.add(url)
                    results.append({"name":f"{str(code).upper()} - {name}","url":url,"description":f"番号：{str(code).upper()} | MissAV {name}","parse":0,"header":headers})
        except Exception:
            pass
        for h,name,path in [(1080,"1080P",base+"/1080p/video.m3u8"),(720,"720P",base+"/720p/video.m3u8"),(480,"480P",base+"/480p/video.m3u8"),(360,"360P",base+"/360p/video.m3u8")]:
            if path in seen: continue
            ok=self._probe_hls(path,referer)
            if ok or h >= 720:
                results.append({"name":f"{str(code).upper()} - {name}","url":path,"description":f"番号：{str(code).upper()} | MissAV {name}","parse":0,"header":headers})
        return results

    def _find_detail_link(self, code):
        url = self._resolve("cn/search/" + quote(code))
        r = self._get(url, timeout=15)
        if self._is_cf(r.text):
            return ""
        soup = self._soup(r.text)
        target = re.sub(r"[\s_-]+", "", str(code).upper())
        for card in self._card_elements(soup):
            link=self._card_link(card)
            if not link: continue
            href=link.get("href","")
            vid=self._extract_video_id(href)
            if re.sub(r"[\s_-]+", "",vid)==target:
                return self._resolve(href)
        for card in self._card_elements(soup):
            link=self._card_link(card)
            if link and target in re.sub(r"[\s_-]+", "", link.get_text(" ",strip=True).upper()):
                return self._resolve(link.get("href",""))
        link=self._card_link(self._card_elements(soup)[0]) if self._card_elements(soup) else None
        return self._resolve(link.get("href","")) if link else ""

    def _extract_code(self, value):
        s=str(value or "").upper()
        s=re.sub(r"[._]", " ", s).replace("_","-")
        pats=[r"\b([A-Z]{2,12})[- ]?(\d{2,6})\b"]
        for p in pats:
            m=re.search(p,s)
            if m: return f"{m.group(1)}-{m.group(2)}"
        return s.strip()

    def playerContent(self, flag, id, vipFlags):
        try:
            self._ensure_site()
            code=self._extract_code(id)
            if not code or "://" in str(id) and ".m3u8" in str(id):
                if str(id).startswith("http"):
                    code=code or "MissAV"
            cached=self.video_url_cache.get(code.upper())
            video_url=cached.get("url") if cached else ""
            referer=cached.get("referer") if cached else self._resolve("cn/search/"+quote(code))
            direct_id = str(id or "")
            detail = self._resolve(direct_id) if direct_id.startswith(("http://", "https://")) and "/video/" in direct_id else ""
            if not video_url:
                if not detail:
                    detail=self._find_detail_link(code)
                if not detail:
                    return {"parse":0,"url":""}
                r=self._get(detail,timeout=15)
                if self._is_cf(r.text):
                    return {"parse":0,"url":""}
                video_url=self._extract_video_url(r.text)
                referer=detail
                if video_url:
                    self.video_url_cache[code.upper()]={"url":video_url,"referer":referer,"timestamp":time.time()}
            if not video_url:
                return {"parse":0,"url":""}
            m=re.search(r"https://surrit\.[^/]+/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}",video_url,re.I)
            if m:
                resources=self._surrit_resources(video_url,code,referer)
                if resources:
                    # 传统 Spider 一次只能返回一个主 URL；把多清晰度作为 url 成对数组。
                    pairs=[]
                    for x in resources:
                        pairs += [x["name"], x["url"]]
                    return {"parse":0,"url":{"values":[{"n":resources[i]["name"],"v":resources[i]["url"]} for i in range(len(resources))],"position":0},"header":self._play_headers(referer)}
            if self._probe_hls(video_url,referer):
                return {"parse":0,"url":video_url,"header":self._play_headers(referer),"format":"application/x-mpegURL"}
            # 即使探活失败也保留原地址，避免 HEAD/GET 被 CDN 拒绝导致完全丢源。
            return {"parse":0,"url":video_url,"header":self._play_headers(referer),"format":"application/x-mpegURL"}
        except Exception as e:
            return {"parse":0,"url":"","msg":str(e)}

    # ------------------------------------------------------------------
    # 详情
    # ------------------------------------------------------------------
    def _extract_dvd_id(self, soup, link):
        labels={"番号","品番","DVD ID"}
        for row in soup.select(".text-secondary"):
            spans=row.find_all("span")
            if not spans: continue
            label=self._text(spans[0].get_text()).replace("：",":").strip()
            if label in labels and len(spans)>1:
                val=self._text(spans[-1].get_text())
                if val: return re.sub(r"\s+","",val)
        slug=self._extract_video_id(link)
        return slug

    def _actor_genres(self, soup):
        actors=[]; people=[]; genres=[]; seen_a=set(); seen_g=set()
        meta=[]
        for m in soup.select("meta[property='og:video:actor'],meta[property='video:actor'],meta[name='video:actor']"):
            meta += [self._text(x) for x in m.get("content","").split(",") if self._text(x)]
        for row in soup.select("[class*='text-secondary']"):
            spans=row.find_all("span",recursive=True)
            label=self._text(spans[0].get_text() if spans else "").replace("：",":").lower().replace(" ","")
            if label in ("女优:","女優:","actress:","actresses:"):
                for a in row.select("a[href*='/actresses/'],a[href*='actresses']"):
                    name=self._text(a.get_text())
                    if not name: continue
                    match=next((x for x in meta if name.replace(" ","").lower() in x.replace(" ","").lower() or x.replace(" ","").lower() in name.replace(" ","").lower()),name)
                    key=match.replace(" ","").lower()
                    if key in seen_a: continue
                    seen_a.add(key)
                    avatar=self._img_of(a)
                    actor={"name":match,"avatar":self._resolve(avatar) if avatar else "","link":self._resolve(a.get("href",""))}
                    actors.append(actor)
                    people.append(self._people_item(match,avatar,a.get("href","")))
            if label in ("类型:","類型:","分类:","分類:","genre:","genres:","category:","categories:"):
                for a in row.select("a[href*='/genres/'],a[href*='chinese-subtitle']"):
                    name=self._text(a.get_text()); gid=self._normalize_people_id(a.get("href",""))
                    if name and gid and gid not in seen_g:
                        seen_g.add(gid); genres.append({"id":gid,"title":name})
        return actors,people,genres

    def _related(self, soup, current_link):
        out=[]; seen=set(); cur=self._extract_video_id(current_link).upper()
        for card in self._card_elements(soup):
            if card.find_parent(id="videodetails"): continue
            link=self._card_link(card)
            if not link: continue
            href=self._resolve(link.get("href","")); vid=self._extract_video_id(href).upper()
            if not href or vid==cur or href.lower() in seen: continue
            seen.add(href.lower())
            title=self._text(link.get_text(" ",strip=True)) or vid or "推荐影片"
            img=self._card_image(card,vid); posters,backs,special=self._covers(vid)
            poster=posters[0] if posters else img
            backdrop=special or (backs[0] if backs else poster)
            out.append({"vod_id":href,"vod_name":title,"vod_pic":backdrop or poster,"vod_remarks":self._duration(card),"link":href,"detailPoster":poster})
        return out

    # JavTrailers 辅助：严格番号匹配 + DMM/MGStage 剧照
    def _clean_dvd(self, value):
        return re.sub(r"\s+","",str(value or "")).replace("-UNCENSORED-LEAK","").replace("-CHINESE-SUBTITLE","").replace("_UNCENSORED_LEAK","").replace("_CHINESE_SUBTITLE","")

    def _dvd_compare(self, value):
        s=self._clean_dvd(value).upper(); m=re.search(r"([A-Z]+)[-_ ]*0*(\d+)",s)
        return f"{m.group(1)}{int(m.group(2))}" if m else re.sub(r"[^A-Z0-9]","",s)

    def _dmm_id(self,value):
        s=self._clean_dvd(value).lower(); m=re.match(r"^([a-z]+)[-_ ]*0*(\d+)$",s)
        return f"{m.group(1)}{int(m.group(2)):05d}" if m else re.sub(r"[^a-z0-9]","",s)

    def _dmm_gallery(self, content_id, count=10):
        return [f"https://pics.dmm.co.jp/digital/video/{content_id}/{content_id}jp-{i}.jpg" for i in range(1,count+1)] if content_id else []

    def _mg_gallery(self,dvd_id,count=10):
        s=self._clean_dvd(dvd_id).lower(); m=re.match(r"^([a-z]+)[-_ ]*0*(\d+)$",s)
        if not m:return []
        pre,num=m.group(1),str(int(m.group(2))); dvd=f"{pre}-{num}"
        return [f"https://image.mgstage.com/images/prestige/{pre}/{num}/cap_e_{i}_{dvd}.jpg" for i in range(1,count+1)]

    def _jav_trailer_url(self,title):
        p=self._jav_parts(title)
        if not p:return ""
        code=p["code"]; fallback=f"https://media.javtrailers.com/hlsvideo/freepv/{code[0]}/{code[:3]}/{code}/playlist.m3u8"
        mg={"ABF","ABW","JUFE","MAAN","PPT","SIRO","LUXU","GANA","ABP","CHN"}
        if p["prefix"] not in mg and "VR" not in p["prefix"]:
            return fallback
        ids=[]
        if p["prefix"] in mg: ids.append(f"118{p['prefixLower']}{p['number5']}")
        ids.append(code)
        for pid in dict.fromkeys(ids):
            try:
                r=self._get(f"https://javtrailers.com/video/{pid}",headers={"Referer":"https://javtrailers.com/"},timeout=2.5)
                ms=re.findall(r"https://media\.javtrailers\.com/[^\"'\\\s<]+?(?:\.m3u8|\.mp4)",r.text)
                if ms:return ms[0]
                ms=re.findall(r"https://sample\.mgstage\.com/[^\"'\\\s<]+?\.mp4",r.text)
                if ms:return ms[0]
                ms=re.findall(r"https://cc3001\.dmm\.co\.jp/[^\"'\\\s<]+?(?:\.m3u8|\.mp4)",r.text)
                if ms:return ms[0]
            except Exception: pass
        return "" if p["prefix"] in mg else fallback

    def _jav_gallery(self,dvd_id):
        content=self._dmm_id(dvd_id)
        if not content:return []
        # 先按 DMM 标准图生成；若站点实际是 MGStage，则使用 MGStage 规则。
        if self._jav_parts(dvd_id) and self._jav_parts(dvd_id)["prefix"] in {"ABF","ABW","JUFE","MAAN","PPT","SIRO","LUXU","GANA","ABP","CHN"}:
            return self._mg_gallery(dvd_id)
        return self._dmm_gallery(content)

    def detailContent(self, ids):
        link = ids[0] if isinstance(ids,(list,tuple)) and ids else ids
        if not link:return {"list":[]}
        try:
            self._ensure_site(); link=self._resolve(link)
            r=self._get(link,timeout=15)
            if self._is_cf(r.text):return {"list":[]}
            soup=self._soup(r.text)
            title=self._text((soup.select_one("meta[property='og:title']") or {}).get("content") if soup.select_one("meta[property='og:title']") else "") or self._text(soup.select_one("h1").get_text() if soup.select_one("h1") else "")
            actors,peoples,genres=self._actor_genres(soup)
            video_url=self._extract_video_url(r.text)
            dvd=self._extract_dvd_id(soup,link)
            posters,backs,special=self._covers(self._extract_video_id(link))
            missav_cover=""
            for sel in ["meta[property='og:image']","meta[name='twitter:image']","video[poster]","img[data-src]","img[src]"]:
                el=soup.select_one(sel)
                if el:
                    missav_cover=el.get("content") or el.get("poster") or el.get("data-src") or el.get("src") or ""
                    if missav_cover:break
            poster=posters[0] if posters else self._resolve(missav_cover)
            backdrop=special or (backs[0] if backs else self._resolve(missav_cover)) or poster
            related=self._related(soup,link)
            trailers=[]
            trailer=self._jav_trailer_url(title)
            if trailer:
                tc=backdrop or poster
                trailers=[{"url":trailer,"coverUrl":tc,"posterPath":tc,"backdropPath":tc,"image":tc,"thumbnail":tc}]
            galleries=self._jav_gallery(dvd)
            item={
                "vod_id":link,"vod_name":title,"vod_pic":poster or backdrop,"vod_year":"","vod_area":"","vod_actor":", ".join(x["name"] for x in actors),
                "vod_director":"","vod_content":"","vod_remarks":"","vod_play_from":"MissAV","vod_play_url":f"正片${link}",
                "header":self._play_headers(link),"posterPath":poster,"backdropPath":backdrop,"detailPoster":backdrop,
                "peoples":peoples,"genreItems":genres,"relatedItems":related,
            }
            if galleries:item["backdropPaths"]=galleries
            if trailers:item["trailers"]=trailers
            # 详情阶段已经提取到 m3u8 时，保留在缓存，playerContent 无需再次搜索
            if video_url:self.video_url_cache[self._extract_video_id(link).upper()]={"url":video_url,"referer":link,"timestamp":time.time()}
            return {"list":[item]}
        except Exception as e:
            return {"list":[self._status("请求错误",str(e))]}

    # ------------------------------------------------------------------
    # 可选：本地代理/测试
    # ------------------------------------------------------------------
    def localProxy(self, params):
        return [404, "text/plain; charset=utf-8", "Not Found", {"Cache-Control":"no-cache"}]
