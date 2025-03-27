import os
import requests
from duckduckgo_search import DDGS

# Napravi folder za slike
os.makedirs("sponge", exist_ok=True)

# Pretraži slike
with DDGS() as ddgs:
    results = ddgs.images(
        keywords="sponge foam",
        region="wt-wt",
        safesearch="off",
        size="Medium",
        color="color",
        type_image="photo",
        max_results=100
    )

    # Preuzmi slike
    for i, result in enumerate(results):
        try:
            img_url = result["image"]
            response = requests.get(img_url, stream=True, timeout=2)
            if response.status_code == 200:
                with open(f"sponge/aa_{i+1}.jpg", "wb") as f:
                    f.write(response.content)
                print(f"Preuzeto {i+1}/100")
        except Exception as e:
            print(f"Greška pri preuzimanju {img_url}: {str(e)}")
