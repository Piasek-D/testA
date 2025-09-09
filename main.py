from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import time

# URL wyszukiwania
url = "https://www.azair.eu/azfin.php?searchtype=flexi&tp=0&isOneway=return&srcAirport=Polska+%5BSZY%5D+%28%2BWMI%2CWAW%2CGDN%2CBZG%2CLCJ%2CRDO%2CLUZ%2CPOZ%2CKRK%2CKTW%2CRZE%2CSZZ%2CWRO%29&srcap0=WMI&srcap1=WAW&srcap2=GDN&srcap3=BZG&srcap4=LCJ&srcap5=RDO&srcap7=LUZ&srcap9=POZ&srcap10=KRK&srcap11=KTW&srcap12=RZE&srcap13=SZZ&srcap14=WRO&srcFreeAirport=&srcTypedText=po&srcFreeTypedText=&srcMC=PL&dstAirport=Gdziekolwiek+%5BXXX%5D&anywhere=true&dstap0=LIN&dstap1=BGY&dstFreeAirport=&dstTypedText=xxx&dstFreeTypedText=&dstMC=&depmonth=202509&depdate=2025-09-07&aid=0&arrmonth=202606&arrdate=2026-06-28&minDaysStay=1&maxDaysStay=8&dep0=true&dep1=true&dep2=true&dep3=true&dep4=true&dep5=true&dep6=true&arr0=true&arr1=true&arr2=true&arr3=true&arr4=true&arr5=true&arr6=true&samedep=true&samearr=true&minHourStay=0%3A45&maxHourStay=23%3A20&minHourOutbound=0%3A00&maxHourOutbound=24%3A00&minHourInbound=0%3A00&maxHourInbound=24%3A00&autoprice=true&adults=1&children=0&infants=0&maxChng=1&currency=PLN&lang=pl&indexSubmit=Szukaj"

# konfiguracja Chrome
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

# ścieżka do ChromeDriver
service = Service("C:/Users/Darek/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe")

driver = webdriver.Chrome(service=service, options=options)
driver.get(url)

# czekaj, aż załadują się wyniki
try:
    WebDriverWait(driver, 30).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, "div.result")) > 0
    )
    time.sleep(7)  # dodatkowy czas na pełne wyrenderowanie wyników
except Exception as e:
    print("❌ Nie znaleziono wyników lub strona nie zdążyła się załadować:", e)

# pobierz HTML i zamknij przeglądarkę
html = driver.page_source
driver.quit()

# parsowanie przez BeautifulSoup
soup = BeautifulSoup(html, "html.parser")
results = soup.select("div.result")

if not results:
    print("Brak wyników do zapisania.")
    exit()

print(f"Znaleziono {len(results)} wyników\n")

# wyświetlamy pierwszą linię z wszystkimi kolumnami
first_row = list(results[0].stripped_strings)
print("Pierwszy wynik (wszystkie kolumny) z numeracją:")
for idx, val in enumerate(first_row):
    print(f"[{idx}] {val}", end=" | ")
print("\n")  # nowa linia po wyświetleniu wszystkich kolumn

# interaktywny wybór kolumn
wybrane = input("Podaj numery kolumn do zapisania, oddzielone przecinkami (np. 0,2,5,8): ")
wybrane_kolumny = [int(x.strip()) for x in wybrane.split(",") if x.strip().isdigit()]

# zapis do pliku TXT tylko wybranych kolumn
with open("loty_selenium.txt", "w", encoding="utf-8") as f:
    for r in results:
        all_text = list(r.stripped_strings)
        selected = [all_text[i] for i in wybrane_kolumny if i < len(all_text)]
        f.write(" | ".join(selected) + "\n")

print("\n✅ Zapisano wybrane kolumny do pliku loty_selenium.txt")

