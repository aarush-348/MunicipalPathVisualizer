import httpx

url = "https://aaplesarkar.mahaonline.gov.in/en/Forms/GetServiceMasterDataforSeva"

r = httpx.get(
    url,
    verify=False,
    follow_redirects=True,
    timeout=20
)

print("STATUS:", r.status_code)
print("CONTENT TYPE:", r.headers.get("content-type"))
print(r.text[:10000])

import re

scripts = soup.find_all("script", src=True)

print("\n=== Relevant JS files ===")

for script in scripts:
    src = script["src"]

    if src.startswith("/"):
        src = "https://aaplesarkar.mahaonline.gov.in" + src

    if "Form" in src or "common" in src.lower() or "ajax" in src.lower():
        print(src)
