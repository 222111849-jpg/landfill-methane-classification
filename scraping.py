from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re
import random
import os

# **Konfigurasi WebDriver**
options = Options()
options.headless = False  # False biar bisa lihat prosesnya
options.set_preference("general.useragent.override", 
   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

driver = webdriver.Firefox(options=options)

# **Baca file CSV berisi daftar landfill**
df = pd.read_csv("DataLandfill.csv", sep=",", quotechar='"')
facilities = df["NamaFasilitas"].tolist()

# **Kata kunci utama untuk pencarian di Google Maps**
keywords = ["sampah", "garbage", "limbah", "daur", "akhir", "sementara", "UPST"]
name_keywords = ["TPA", "TPST", "Sampah"]
desc_keywords = ["pemerintah"]

# **Path hasil scraping**
save_path = "hasil_pencarian_fasilitas.csv"
batch_size = 5  # Simpan data setiap 200 iterasi
results = []

# **Cek apakah file hasil sudah ada, agar bisa lanjut dari terakhir**
if os.path.exists(save_path):
    existing_data = pd.read_csv(save_path)
    start_idx = len(existing_data)
    results = existing_data.to_dict(orient="records")
    print(f"📌 Melanjutkan dari indeks {start_idx}")
else:
    start_idx = 0

# **Mulai scraping**
for idx, facility in enumerate(facilities[start_idx:], start=start_idx):
    search_query = facility.replace(" ", "+")
    url = f"https://www.google.com/maps/search/{search_query}/"
    time.sleep(random.uniform(5, 10))
    driver.set_page_load_timeout(30)
    driver.get(url)

    try:
        wait = WebDriverWait(driver, 10)
        time.sleep(5)

        # **Scroll untuk load lebih banyak hasil**
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # **Ambil hasil pencarian**
        place_list = driver.find_elements(By.CLASS_NAME, "Nv2PK")

        selected_result = None
        place_name, address, facility_type, facility_label = "Not Found", "Not Found", "Not Found", "Not Found"

        if place_list:
            print(f"\n🔍 Hasil ditemukan untuk '{facility}':")

            for idx, place in enumerate(place_list):
                try:
                    name = place.find_element(By.CLASS_NAME, "qBF1Pd").text  # Nama tempat
                    desc_elements = place.find_elements(By.CLASS_NAME, "W4Efsd")
                    desc = "No Label"
                    if desc_elements:
                        for div in desc_elements:
                            spans = div.find_elements(By.XPATH, "./span")
                            if spans:
                                desc = spans[0].text
                                break  # Ambil yang pertama ditemukan
                    
                    print(f"   {idx+1}. {name} | {desc}")  

                    # **Cek apakah sesuai kata kunci**
                    if any(re.search(rf"\b{kw}\b", name, re.IGNORECASE) for kw in keywords) or \
                       any(re.search(rf"\b{kw}\b", desc, re.IGNORECASE) for kw in keywords):
                        selected_result = place
                        place_name = name
                        break  
                    elif any(re.search(rf"\b{nk}\b", name, re.IGNORECASE) for nk in name_keywords) and \
                         any(re.search(rf"\b{dk}\b", desc, re.IGNORECASE) for dk in desc_keywords):
                        selected_result = place
                        place_name = name
                        break  

                except Exception as e:
                    print(f"   ❌ Error ambil data: {str(e)}")

            if selected_result:
                selected_result.click()
                time.sleep(10)  # Tunggu halaman detail terbuka
                
                facility_label = desc
                try:
                    address = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "Io6YTe"))
                    ).text
                except:
                    address = "Not Found"
                facility_type = next((kw for kw in keywords if kw.lower() in address.lower()), "Other")
                current_url = driver.current_url
            else:
                current_url = driver.current_url

        else:
            # **Jika langsung ke halaman detail**
            print(f"   🔹 Langsung ke halaman detail untuk '{facility}'")
            place_name = wait.until(EC.presence_of_element_located((By.XPATH, "//h1[contains(@class, 'DUwDvf')]"))).text
            address = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'Io6YTe')]"))).text
            
            try:
                facility_label = driver.find_element(By.CLASS_NAME, "DkEaL").text
            except:
                facility_label = "Not Found"

            facility_type = next((kw for kw in keywords if kw.lower() in address.lower()), "Other")
            current_url = driver.current_url

        # **Ambil koordinat dari URL**
        match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', current_url)
        latitude, longitude = match.groups() if match else ("Not Found", "Not Found")
        
        print(f"✅ '{facility}' → {place_name}, {address}, ({latitude}, {longitude}), {facility_type}, Label: {facility_label}")
        results.append({
            "search": facility, 
            "found_place": place_name, 
            "address": address, 
            "latitude": latitude, 
            "longitude": longitude,
            "facility_type": facility_type,
            "facility_label": facility_label
        })
    
    except Exception as e:
        print(f"❌ Tidak ada hasil untuk '{facility}' atau error: {str(e)}")
        results.append({
            "search": facility, 
            "found_place": "Not Found", 
            "address": "Not Found", 
            "latitude": "Not Found", 
            "longitude": "Not Found",
            "facility_type": "Not Found",
            "facility_label": "Not Found"
        })

    # **Simpan hasil setiap 200 iterasi**
    if (idx + 1) % batch_size == 0:
        df_results = pd.DataFrame(results)
        df_results.to_csv(save_path, index=False)
        print(f"💾 Data disimpan (total {idx+1} records)")

# **Simpan data terakhir sebelum keluar**
df_results = pd.DataFrame(results)
df_results.to_csv(save_path, index=False)

time.sleep(10)
driver.quit()

print("\n🚀 Scraping selesai! Cek file 'hasil_pencarian_fasilitas.csv'.")
