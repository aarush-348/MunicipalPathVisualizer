"""
Configuration settings for Aaple Sarkar portal data extraction.
"""
from dataclasses import dataclass
from typing import Dict

@dataclass
class ScraperConfig:
    # Base portal URLs
    BASE_URL: str = "https://aaplesarkar.mahaonline.gov.in"
    NOTIFIED_SERVICES_URL_EN: str = "https://aaplesarkar.mahaonline.gov.in/en/CommonForm/ViewAllServices"
    NOTIFIED_SERVICES_URL_MR: str = "https://aaplesarkar.mahaonline.gov.in/mr/CommonForm/ViewAllServices"
    CERT_DOCS_URL_TEMPLATE: str = "https://aaplesarkar.mahaonline.gov.in/{lang}/Login/Certificate_Documents?ServiceId={service_id}"
    SUBDEPT_API_URL: str = "https://aaplesarkar.mahaonline.gov.in/Controllers/TrackApplicationStatus/Select_SubDept"
    SERVICES_BY_DEPT_API_URL: str = "https://aaplesarkar.mahaonline.gov.in/Controllers/TrackApplicationStatus/Service_SelectedDept"
    MAITRI_MOVED_SERVICES_URL: str = "https://aaplesarkar.mahaonline.gov.in/en/Login/GetMaitriMovedServices"
    AUTOCOMPLETE_API_URL: str = "https://aaplesarkar.mahaonline.gov.in/en/Forms/GetServiceMasterDataforSeva"

    # Scraping limits & etiquette
    REQUEST_DELAY_SECONDS: float = 0.5  # Polite delay between requests
    TIMEOUT_SECONDS: float = 20.0
    MAX_RETRIES: int = 3
    SAMPLE_LIMIT: int = 20  # For Phase 2 test scrape

    # Request headers
    HEADERS: Dict[str, str] = None

    def __post_init__(self):
        if self.HEADERS is None:
            self.HEADERS = {
                "User-Agent": "MunicipalBureaucracyPathVisualizer/1.0 (+https://github.com/aarush-348/MunicipalPathVisualizer; Civic Research Bot)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9,mr;q=0.8",
                "X-Requested-With": "XMLHttpRequest"
            }
