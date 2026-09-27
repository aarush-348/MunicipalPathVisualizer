import httpx

base = "https://aaplesarkar.mahaonline.gov.in"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://aaplesarkar.mahaonline.gov.in/en/CommonForm/ViewAllServices",
    "X-Requested-With": "XMLHttpRequest",
}

with httpx.Client(
    headers=headers,
    verify=False,
    follow_redirects=True,
    timeout=20
) as client:

    # First establish a session on the actual page
    page = client.get(
        base + "/en/CommonForm/ViewAllServices"
    )

    print("PAGE:", page.status_code)

    # Now make the AJAX request
    response = client.get(
        base + "/en/Forms/GetServiceMasterDataforSeva",
        params={"term": "Income"}
    )

    print("API STATUS:", response.status_code)
    print("API URL:", response.url)
    print("CONTENT TYPE:", response.headers.get("content-type"))
    print()
    print(response.text[:5000])
