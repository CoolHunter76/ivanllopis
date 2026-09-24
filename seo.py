import json
import os
from html import escape

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

from portal_updates import load_portal_updates, published_update_ids

ORIGIN = "https://ivanllopis.net"
LANGUAGES = ("es", "ca", "gl", "oc", "eu", "en", "fr", "uk", "it", "tr", "ru", "zh-Hans", "ja")
IMAGE = f"{ORIGIN}/static/images/ivan-hero-transparent.webp"
TEXT = {
    "es": (
        "Portfolio profesional de Ivan Llopis sobre ingenieria de software, cloud, Azure, .NET, Python e inteligencia artificial.",
        "Aficiones, intereses y actividades personales de Ivan Llopis.",
    ),
    "gl": (
        "Portfolio profesional de Ivan Llopis sobre enxeñaría de software, cloud e IA.",
        "Afeccións e intereses de Ivan Llopis.",
    ),
    "oc": (
        "Portfolio professionau de Ivan Llopis sus enginharia de logiciau, cloud e IA.",
        "Aficions e interèssi de Ivan Llopis.",
    ),
    "ru": (
        "Профессиональное портфолио о разработке, облачных технологиях и ИИ.",
        "Увлечения и интересы.",
    ),
    "zh-Hans": ("软件工程、云技术与人工智能专业作品集。", "个人爱好与兴趣。"),
    "ja": ("ソフトウェア、クラウド、AIに関するプロフェッショナルポートフォリオ。", "趣味と関心。"),
    "ca": (
        "Portafolis professional d'Ivan Llopis sobre enginyeria de programari, cloud, Azure, .NET, Python i intel.ligencia artificial.",
        "Aficions, interessos i activitats personals d'Ivan Llopis.",
    ),
    "eu": (
        "Ivan Llopisen portfolio profesionala: software ingeniaritza, hodeia, Azure, .NET, Python eta adimen artifiziala.",
        "Ivan Llopisen zaletasunak, interesak eta jarduera pertsonalak.",
    ),
    "en": (
        "Ivan Llopis professional portfolio about software engineering, cloud, Azure, .NET, Python and artificial intelligence.",
        "Discover Ivan Llopis hobbies, interests and personal activities.",
    ),
    "fr": (
        "Portfolio professionnel d'Ivan Llopis sur le genie logiciel, le cloud, Azure, .NET, Python et l'intelligence artificielle.",
        "Loisirs, centres d'interet et activites personnelles d'Ivan Llopis.",
    ),
    "uk": (
        "Професійне портфоліо Ivan Llopis: програмна інженерія, хмара, Azure, .NET, Python і штучний інтелект.",
        "Захоплення, інтереси та особисті заняття Ivan Llopis.",
    ),
    "it": (
        "Portfolio professionale di Ivan Llopis su ingegneria del software, cloud, Azure, .NET, Python e intelligenza artificiale.",
        "Hobby, interessi e attivita personali di Ivan Llopis.",
    ),
    "tr": (
        "Ivan Llopis'in yazilim muhendisligi, bulut, Azure, .NET, Python ve yapay zeka odakli profesyonel portfoyu.",
        "Ivan Llopis'in hobileri, ilgi alanlari ve kisisel etkinlikleri.",
    ),
}
router = APIRouter(include_in_schema=False)


def is_staging(request):
    return (
        os.getenv("APP_ENV", "production").lower() == "staging"
        or request.url.hostname == "staging.ivanllopis.net"
    )


def page_info(path):
    parts = [part for part in path.split("/") if part]
    lang = parts[0] if parts and parts[0] in LANGUAGES else "es"
    page = parts[1] if len(parts) > 1 else ""
    suffix = "/" + "/".join(parts[1:]) if len(parts) > 1 else ""
    hobbies = page == "hobbies"
    gamer = suffix == "/hobbies/gamer"
    updates = page == "updates"
    update_id = parts[2] if updates and len(parts) > 2 else None
    talent = suffix == "/talento-cercano"
    update = None
    if update_id:
        update = next(
            (item for item in load_portal_updates(lang)["items"] if item["id"] == update_id),
            None,
        )
    if gamer:
        title = "GAMER | IvanLlopis.net"
        description = (
            "Universo gamer personal de Ivan Llopis: galería de imágenes, vídeos y recuerdos de videojuegos."
            if lang == "es"
            else "Ivan Llopis gaming world: a gallery for images, videos and gaming memories."
        )
    elif talent:
        title = (
            "Talento Cercano | IvanLlopis.net"
            if lang == "es"
            else "Talent Close to Home | IvanLlopis.net"
        )
        description = (
            "Personas, espacios y proyectos cercanos que Ivan Llopis quiere ayudar a impulsar."
            if lang == "es"
            else "People, places and projects close to Ivan Llopis and worth discovering."
        )
    elif update:
        title = f"{update['title']} | IvanLlopis.net"
        description = update["summary"]
    elif updates:
        title = "Evolución de IvanLlopis.net" if lang == "es" else "IvanLlopis.net | Updates"
        description = (
            "Historial de evolución, cambios publicados y próximas señales de IvanLlopis.net."
            if lang == "es"
            else "IvanLlopis.net evolution archive, released changes and next signals."
        )
    else:
        title = (
            "Aficiones de Ivan Llopis"
            if hobbies and lang == "es"
            else ("Ivan Llopis | Hobbies" if hobbies else "Ivan Llopis | Software Engineer Lead")
        )
        description = TEXT[lang][1 if hobbies else 0]
    return lang, suffix, title, description, update


def seo_head(request):
    lang, suffix, title, description, update = page_info(request.url.path)
    canonical = f"{ORIGIN}/{lang}{suffix}"
    robots = "noindex, nofollow, noarchive" if is_staging(request) else "index, follow"
    alternates = "\n".join(
        f'<link rel="alternate" hreflang="{code}" href="{ORIGIN}/{code}{suffix}">'
        for code in LANGUAGES
    )
    alternates += f'\n<link rel="alternate" hreflang="x-default" href="{ORIGIN}/es{suffix}">'
    if suffix == "/updates":
        alternates += f'\n<link rel="alternate" type="application/atom+xml" title="IvanLlopis.net Updates" href="{ORIGIN}/{lang}/updates.atom">'
    graph = [
        {
            "@type": "WebSite",
            "@id": f"{ORIGIN}/#website",
            "url": f"{ORIGIN}/",
            "name": "IvanLlopis.net",
            "inLanguage": list(LANGUAGES),
        },
        {
            "@type": "Person",
            "@id": f"{ORIGIN}/#person",
            "name": "Ivan Llopis",
            "url": f"{ORIGIN}/",
            "image": IMAGE,
            "jobTitle": "Software Engineer Lead",
        },
    ]
    if update:
        graph.append(
            {
                "@type": "Article" if update["status"] != "next" else "WebPage",
                "headline": update["title"],
                "description": update["summary"],
                "url": canonical,
                "inLanguage": lang,
                **({"datePublished": update["date"]} if update.get("date") else {}),
                "author": {"@id": f"{ORIGIN}/#person"},
            }
        )
    data = {
        "@context": "https://schema.org",
        "@graph": graph,
    }
    return "\n".join(
        [
            "<!-- SEO managed by seo.py -->",
            f"<title>{escape(title)}</title>",
            f'<meta name="description" content="{escape(description, quote=True)}">',
            f'<meta name="robots" content="{robots}">',
            f'<link rel="canonical" href="{canonical}">',
            alternates,
            '<meta property="og:type" content="article">'
            if update
            else '<meta property="og:type" content="website">',
            '<meta property="og:site_name" content="IvanLlopis.net">',
            f'<meta property="og:title" content="{escape(title, quote=True)}">',
            f'<meta property="og:description" content="{escape(description, quote=True)}">',
            f'<meta property="og:url" content="{canonical}">',
            f'<meta property="og:image" content="{IMAGE}">',
            '<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{escape(title, quote=True)}">',
            f'<meta name="twitter:description" content="{escape(description, quote=True)}">',
            f'<meta name="twitter:image" content="{IMAGE}">',
            f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>',
        ]
    )


class SeoMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if is_staging(request):
            response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        if response.status_code != 200 or "text/html" not in response.headers.get(
            "content-type", ""
        ):
            return response
        body = b"".join([chunk async for chunk in response.body_iterator])
        html = body.decode("utf-8")
        lower = html.lower()
        start = lower.find("<title")
        if start != -1:
            end = lower.find("</title>", start)
            if end != -1:
                html = html[:start] + html[end + 8 :]
        head_end = html.lower().find("</head>")
        if head_end != -1:
            html = html[:head_end] + seo_head(request) + "\n" + html[head_end:]
        headers = dict(response.headers)
        headers.pop("content-length", None)
        return Response(
            html, status_code=response.status_code, headers=headers, media_type="text/html"
        )


@router.get("/robots.txt")
def robots(request: Request):
    text = (
        "User-agent: *\nDisallow: /\n"
        if is_staging(request)
        else f"User-agent: *\nAllow: /\n\nSitemap: {ORIGIN}/sitemap.xml\n"
    )
    return PlainTextResponse(text)


@router.get("/sitemap.xml")
def sitemap():
    urls = "\n".join(
        f"  <url><loc>{ORIGIN}/{lang}{suffix}</loc></url>"
        for lang in LANGUAGES
        for suffix in (
            "",
            "/technologies",
            "/projects",
            "/work-life",
            "/request-cv",
            "/privacy",
            "/hobbies",
            "/hobbies/gamer",
            "/updates",
            "/talento-cercano",
        )
    )
    update_urls = "\n".join(
        f"  <url><loc>{ORIGIN}/{lang}/updates/{update_id}</loc></url>"
        for lang in LANGUAGES
        for update_id in published_update_ids()
    )
    urls = f"{urls}\n{update_urls}"
    xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n'
    return Response(xml, media_type="application/xml")


def configure_seo(app):
    app.add_middleware(SeoMiddleware)
    app.include_router(router)
