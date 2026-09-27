import httpx
from bs4 import BeautifulSoup
import json
import os


URL = "https://aaplesarkar.mahaonline.gov.in/en/CommonForm/ViewAllServices"


def scrape_master_services():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/140.0 Safari/537.36"
        )
    }

    response = httpx.get(
        URL,
        headers=headers,
        verify=False,
        follow_redirects=True,
        timeout=30,
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    tables = soup.find_all("table")

    if not tables:
        raise RuntimeError("No tables found on ViewAllServices")

    # Table 0 = English
    table = tables[0]

    rows = table.find_all("tr")

    services = []

    for row in rows[1:]:
        cells = row.find_all(["td", "th"])

        values = [
            cell.get_text(" ", strip=True)
            for cell in cells
        ]

        # Expected:
        # Sr No, Department, Sub Department, Service,
        # Time Limit, Designated Officer,
        # First Appellate Officer, Second Appellate Officer,
        # Available on portal

        if len(values) < 9:
            continue

        service = {
            "sr_no": values[0],
            "department": values[1],
            "sub_department": values[2],
            "service_name": values[3],
            "time_limit_days": values[4],
            "designated_officer": values[5],
            "first_appellate_officer": values[6],
            "second_appellate_officer": values[7],
            "available_on_portal": values[8],
        }

        services.append(service)

    return services


if __name__ == "__main__":
    services = scrape_master_services()

    print(f"Found {len(services)} services")

    print("\nFirst 10 services:\n")

    for service in services[:10]:
        print(service)

    os.makedirs("data", exist_ok=True)

    with open(
        "data/all_services.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            services,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("\nSaved to data/all_services.json")
