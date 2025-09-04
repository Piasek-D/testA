from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import uvicorn
import os

BASE = "https://biletyczarterowe.r.pl"

app = FastAPI()

# Szablony będą trzymane w katalogu tymczasowym
os.makedirs("templates", exist_ok=True)

# Utwórz prosty index.html jeśli nie istnieje
if not os.path.exists("templates/index.html"):
    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Loty</title>
</head>
<body>
  <h1>Wyszukiwarka lotów</h1>
  <form method="get">
    <input type="text" name="q" placeholder="from=KRK&to=RHO">
    <button type="submit">Szukaj</button>
  </form>

  <table border="1">
    <tr><th>Data</th><th>Trasa</th><th>Cena</th><th>Link</th></tr>
    {% for f in flights %}
    <tr>
      <td>{{ f.date or "-" }}</td>
      <td>{{ f.departure or "" }} → {{ f.arrival or "" }}</td>
      <td>{{ f.price or "-" }} {{ f.currency or "" }}</td>
      <td>{% if f.link %}<a href="{{ f.link }}" target="_blank">otwórz</a>{% else %}-{% endif %}</td>
    </tr>
    {% endfor %}
  </table>
</body>
</html>""")

templates = Jinja2Templates(directory="templates")

async def scrape_search_results(q: str):
    url = f"{BASE}/szukaj?{q}" if not q.startswith("http") else q
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_load_state('networkidle')
        content = await page.content()
        await browser.close()

    soup = BeautifulSoup(content, "html.parser")
    offers = soup.select("div.offer-item")  # trzeba dopasować do DOM strony

    results = []
    for node in offers:
        date = node.select_one(".offer-date")
        route = node.select_one(".offer-route")
        price = node.select_one(".offer-price")
        link_tag = node.select_one("a")
        link = urljoin(BASE, link_tag["href"]) if link_tag and link_tag.get("href") else None

        results.append({
            "departure": None,
            "arrival": None,
            "date": date.get_text(strip=True) if date else None,
            "price": price.get_text(strip=True) if price else None,
            "currency": "PLN",
            "link": link,
            "extras": {"route": route.get_text(strip=True) if route else None}
        })
    return results

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, q: str = Query(None)):
    flights = []
    if q:
        flights = await scrape_search_results(q)
        flights = sorted(flights, key=lambda x: x.get("date") or "")
    return templates.TemplateResponse("index.html", {"request": request, "flights": flights})

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
