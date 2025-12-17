#!/usr/bin/env python3
"""
Web scraper for Azpetrol gas stations in Azerbaijan.
Extracts location coordinates, addresses, and service information.
Source: https://www.azpetrol.com/service-network
"""

import csv
import json
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.azpetrol.com"
SERVICE_NETWORK_URL = f"{BASE_URL}/service-network"
OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_FILE = OUTPUT_DIR / "azpetrol.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}


def fetch_page(url: str) -> str:
    """Fetch HTML content from URL."""
    print(f"Fetching: {url}")
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.text


def parse_full_station_data(html: str) -> List[Dict]:
    """Parse station data from RSC payload with escaped JSON."""
    stations = []

    # The data uses escaped quotes: \\"id\\"
    # In Python regex, we need to match a literal backslash (\) followed by a quote (")
    # To match literal backslash in regex: \\\\ (4 backslashes in raw string = 2 literal backslashes)
    # But the HTML has single backslash before quote: \"
    # So we need: \\" which in regex raw string is: \\\\"

    # Actually, the HTML shows: \\"lat\\":\\"40.38916\\"
    # In Python string, this is represented as: \\"
    # To match this in regex: \\\\\" matches a backslash followed by a quote

    # Pattern to find station data with lat/lng coordinates
    # Using raw string to handle escapes properly
    station_pattern = r'\\"id\\":(\d+),\\"attributes\\":\{\\"title\\":\\"([^"\\]+)\\"(?:,\\"address\\":\\"([^"\\]*)\\")?(?:,\\"phone\\":\\"([^"\\]*)\\")?(?:,\\"lat\\":\\"([\d.]+)\\")?(?:,\\"lng\\":\\"([\d.]+)\\")?'

    matches = re.findall(station_pattern, html)

    # Track unique stations by ID
    seen_ids = set()

    for match in matches:
        station_id, title, address, phone, lat, lng = match

        # Skip if we don't have coordinates
        if not lat or not lng:
            continue

        # Skip duplicates
        if station_id in seen_ids:
            continue
        seen_ids.add(station_id)

        station = {
            'id': int(station_id),
            'name': title,
            'address': address if address else '',
            'phone': phone if phone else '',
            'latitude': float(lat),
            'longitude': float(lng),
        }

        stations.append(station)

    # Extract services for each station
    stations = extract_services_for_stations(html, stations)

    # Extract image URLs
    stations = extract_images_for_stations(html, stations)

    return stations


def extract_services_for_stations(html: str, stations: List[Dict]) -> List[Dict]:
    """Extract services/categories for each station."""

    # Find all category definitions (they have color attributes)
    category_pattern = r'\\"id\\":(\d+),\\"attributes\\":\{\\"title\\":\\"([^"\\]+)\\",\\"color\\":\\"#[A-Fa-f0-9]+\\"'
    all_categories = {}
    for cat_id, cat_title in re.findall(category_pattern, html):
        all_categories[int(cat_id)] = cat_title

    # For each station, find the corresponding categories
    # Station data is followed by network_categories block
    for station in stations:
        station_id = station['id']

        # Find the station block and extract categories that follow
        # Pattern to find station and its categories
        block_pattern = rf'\\"id\\":{station_id},\\"attributes\\":\{{\\"title\\":\\"[^"\\]+\\".*?\\"network_categories\\":\{{\\"data\\":\[(.*?)\]\}}\}}'
        block_match = re.search(block_pattern, html, re.DOTALL)

        if block_match:
            categories_data = block_match.group(1)
            # Extract category titles from this block
            cat_matches = re.findall(r'\\"title\\":\\"([^"\\]+)\\"', categories_data)
            if cat_matches:
                # Filter out non-service items
                services = [c for c in cat_matches if c not in [station['name']]]
                services = sorted(list(set(services)))
                if services:
                    station['services'] = '; '.join(services)

    return stations


def extract_images_for_stations(html: str, stations: List[Dict]) -> List[Dict]:
    """Extract image URLs for stations."""

    for station in stations:
        station_id = station['id']

        # Find the image URL for this station
        # Pattern: "id":277,"attributes":{...,"image":{"data":{"id":85,"attributes":{"url":"/uploads/image_xxx.jpg"
        pattern = rf'\\"id\\":{station_id},\\"attributes\\":\{{\\"title\\".*?\\"url\\":\\"(/uploads/[^"\\]+)\\"'
        match = re.search(pattern, html, re.DOTALL)

        if match:
            image_path = match.group(1)
            station['image_url'] = f"https://qnela1.azpetrol.com{image_path}"

    return stations


def extract_all_categories(html: str) -> Dict[int, str]:
    """Extract all unique service categories."""
    categories = {}

    # Find all category definitions with color (service categories have colors)
    cat_pattern = r'\\"id\\":(\d+),\\"attributes\\":\{\\"title\\":\\"([^"\\]+)\\",\\"color\\":\\"#[A-Fa-f0-9]+\\"'

    for cat_id, cat_title in re.findall(cat_pattern, html):
        categories[int(cat_id)] = cat_title

    return categories


def extract_regions(html: str) -> List[str]:
    """Extract all regions from the HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    regions = []

    # Find region buttons in the dropdown (within regions_list class)
    region_list = soup.select('[class*="regions_list"] button')
    for btn in region_list:
        text = btn.get_text(strip=True)
        if text and text not in ['Bütün regionlar']:
            regions.append(text)

    return list(set(regions))


def extract_city_from_address(address: str) -> Optional[str]:
    """Extract city/region from address string."""
    if not address:
        return None

    # Patterns for Azerbaijani addresses
    address_lower = address.lower()

    # Common city/region patterns
    patterns = [
        (r'^([A-Za-zƏəÜüÖöŞşÇçĞğIıİi]+)\s+şəhəri', re.IGNORECASE),
        (r'^([A-Za-zƏəÜüÖöŞşÇçĞğIıİi]+)\s+rayonu', re.IGNORECASE),
        (r'^([A-Za-zƏəÜüÖöŞşÇçĞğIıİi]+)\s+şəh\.', re.IGNORECASE),
    ]

    for pattern, flags in patterns:
        match = re.search(pattern, address, flags)
        if match:
            return match.group(1)

    # Fallback: first meaningful part
    parts = address.split(',')
    if parts:
        first_part = parts[0].strip()
        # Remove common suffixes
        for suffix in [' şəhəri', ' rayonu', ' şəh.', ' ray.']:
            if suffix in first_part.lower():
                idx = first_part.lower().find(suffix)
                return first_part[:idx].strip()

        # Just return first word if nothing else works
        words = first_part.split()
        if words:
            return words[0]

    return None


def normalize_station_data(stations: List[Dict]) -> List[Dict]:
    """Normalize and enhance station data."""
    for station in stations:
        # Add city extraction
        if 'address' in station and 'city' not in station:
            city = extract_city_from_address(station['address'])
            if city:
                station['city'] = city

    return stations


def scrape_azpetrol() -> List[Dict]:
    """Main scraping function."""
    print("=" * 60)
    print("Azpetrol Gas Station Scraper")
    print("=" * 60)

    # Fetch main page
    try:
        html = fetch_page(SERVICE_NETWORK_URL)
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
        return []

    print(f"\nPage size: {len(html):,} bytes")
    print("\nParsing station data from React Server Components payload...")

    # Extract stations
    stations = parse_full_station_data(html)
    print(f"Found {len(stations)} stations with coordinates")

    # Normalize data
    stations = normalize_station_data(stations)

    # Get statistics
    categories = extract_all_categories(html)
    print(f"Found {len(categories)} service categories")

    regions = extract_regions(html)
    print(f"Found {len(regions)} regions in dropdown")

    return stations


def save_to_csv(stations: List[Dict], output_file: Path) -> None:
    """Save station data to CSV file."""
    if not stations:
        print("No stations to save!")
        return

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Define column order with important fields first
    priority_fields = ['id', 'name', 'address', 'city', 'latitude', 'longitude', 'phone', 'services', 'image_url']

    # Collect all fields
    all_fields = set()
    for station in stations:
        all_fields.update(station.keys())

    # Order fields
    ordered_fields = [f for f in priority_fields if f in all_fields]
    ordered_fields.extend(sorted(f for f in all_fields if f not in priority_fields))

    # Add metadata
    ordered_fields.extend(['source_url', 'scraped_at'])

    print(f"\nSaving to: {output_file}")

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=ordered_fields, extrasaction='ignore')
        writer.writeheader()

        scraped_at = datetime.now().isoformat()
        for station in stations:
            station['source_url'] = SERVICE_NETWORK_URL
            station['scraped_at'] = scraped_at
            writer.writerow(station)

    print(f"Successfully saved {len(stations)} stations")

    # Print sample
    print("\nSample data (first 5 stations):")
    for i, station in enumerate(stations[:5], 1):
        name = station.get('name', 'Unknown')
        lat = station.get('latitude', 'N/A')
        lng = station.get('longitude', 'N/A')
        city = station.get('city', 'N/A')
        print(f"  {i}. {name} ({city}) - Coords: ({lat}, {lng})")

    # Print statistics
    print("\n" + "-" * 40)
    print("Statistics:")
    print(f"  Total stations: {len(stations)}")

    # Count stations with all data
    with_services = sum(1 for s in stations if s.get('services'))
    with_images = sum(1 for s in stations if s.get('image_url'))
    with_phones = sum(1 for s in stations if s.get('phone'))

    print(f"  With services: {with_services}")
    print(f"  With images: {with_images}")
    print(f"  With phones: {with_phones}")

    # Count by city
    cities = {}
    for s in stations:
        city = s.get('city', 'Unknown')
        cities[city] = cities.get(city, 0) + 1

    print(f"  Cities/Regions: {len(cities)}")
    print("  Top 5 locations:")
    for city, count in sorted(cities.items(), key=lambda x: -x[1])[:5]:
        print(f"    - {city}: {count} stations")


def main():
    """Main entry point."""
    # Fix Windows console encoding for Azerbaijani characters
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except AttributeError:
            pass  # Python < 3.7

    try:
        stations = scrape_azpetrol()

        if not stations:
            print("\nNo stations found. The website structure may have changed.")
            print("Please check the page source manually or update the scraper.")
            sys.exit(1)

        save_to_csv(stations, OUTPUT_FILE)

        print("\n" + "=" * 60)
        print("Scraping completed successfully!")
        print(f"Output file: {OUTPUT_FILE}")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during scraping: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
