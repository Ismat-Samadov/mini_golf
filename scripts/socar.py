#!/usr/bin/env python3
"""
Web scraper for SOCAR Petroleum gas stations in Azerbaijan.
Extracts location coordinates, addresses, and other information from Google MyMaps KML data.
Source: https://socar-petroleum.az/az/pages/xidmet-sebekesi
"""

import csv
import io
import re
import sys
import zipfile
import warnings
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from xml.etree import ElementTree as ET

import requests


BASE_URL = "https://socar-petroleum.az"
SERVICE_NETWORK_URL = f"{BASE_URL}/az/pages/xidmet-sebekesi"
OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_FILE = OUTPUT_DIR / "socar.csv"

# Google MyMaps IDs embedded in the page
MYMAPS_IDS = [
    "1Au5MBLgL005lFBKHyXzjWDCLfe0lw18",
    "1IMv82ZQskLKV5TUj38JUHWXa1jHEbfU"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
}

# Suppress SSL warnings for the SOCAR site
warnings.filterwarnings('ignore', message='Unverified HTTPS request')


def fetch_kmz(map_id: str) -> Optional[bytes]:
    """Fetch KMZ file from Google MyMaps."""
    kml_url = f"https://www.google.com/maps/d/kml?mid={map_id}"
    print(f"  Fetching: {kml_url}")

    try:
        response = requests.get(kml_url, headers=HEADERS, timeout=30, verify=True)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"  Error fetching KMZ: {e}")
        return None


def extract_kml_from_kmz(kmz_content: bytes) -> Optional[str]:
    """Extract KML content from KMZ (ZIP) file."""
    try:
        with zipfile.ZipFile(io.BytesIO(kmz_content)) as z:
            if 'doc.kml' in z.namelist():
                return z.read('doc.kml').decode('utf-8')
    except (zipfile.BadZipFile, KeyError) as e:
        print(f"  Error extracting KML: {e}")
    return None


def parse_kml_stations(kml_content: str) -> List[Dict]:
    """Parse station data from KML content."""
    stations = []

    # KML namespace
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}

    try:
        root = ET.fromstring(kml_content)
    except ET.ParseError as e:
        print(f"  XML parse error: {e}")
        return stations

    # Find all Placemarks
    for placemark in root.findall('.//kml:Placemark', ns):
        station = {}

        # Get name
        name_elem = placemark.find('kml:name', ns)
        if name_elem is not None and name_elem.text:
            station['name'] = name_elem.text.strip()

        # Get coordinates from Point
        coords_elem = placemark.find('.//kml:coordinates', ns)
        if coords_elem is not None and coords_elem.text:
            coords_text = coords_elem.text.strip()
            # Format: lng,lat,elevation
            parts = coords_text.split(',')
            if len(parts) >= 2:
                try:
                    station['longitude'] = float(parts[0].strip())
                    station['latitude'] = float(parts[1].strip())
                except ValueError:
                    pass

        # Get ExtendedData
        for data_elem in placemark.findall('.//kml:Data', ns):
            data_name = data_elem.get('name', '')
            value_elem = data_elem.find('kml:value', ns)

            if value_elem is not None and value_elem.text:
                value = value_elem.text.strip()

                if data_name == 'GPS COORDINATES':
                    # Parse "lat, lng" format for verification
                    station['gps_coordinates'] = value
                elif data_name == 'ADDRESS':
                    station['address'] = value
                elif data_name == 'gx_media_links':
                    station['image_url'] = value

        # Get description for fallback data
        desc_elem = placemark.find('kml:description', ns)
        if desc_elem is not None and desc_elem.text:
            description = desc_elem.text.strip()

            # Extract address if not already set
            if 'address' not in station:
                addr_match = re.search(r'ADDRESS:\s*([^<]+)', description, re.IGNORECASE)
                if addr_match:
                    station['address'] = addr_match.group(1).strip()

            # Extract GPS coordinates if not already set
            if 'gps_coordinates' not in station:
                gps_match = re.search(r'GPS COORDINATES:\s*([\d.,\s]+)', description, re.IGNORECASE)
                if gps_match:
                    station['gps_coordinates'] = gps_match.group(1).strip()

        # Only add if we have a name and coordinates
        if station.get('name') and station.get('latitude') and station.get('longitude'):
            stations.append(station)

    return stations


def extract_city_from_address(address: str) -> Optional[str]:
    """Extract city/region from address string."""
    if not address:
        return None

    # Common patterns in Azerbaijani addresses
    patterns = [
        r'^([A-Za-zƏəÜüÖöŞşÇçĞğIıİi]+)\s+(?:şəhəri|ş-ri|şəh\.)',
        r'^([A-Za-zƏəÜüÖöŞşÇçĞğIıİi]+)\s+(?:rayonu|r-nu|ray\.)',
        r'([A-Za-zƏəÜüÖöŞşÇçĞğIıİi]+)\s+şoss?esi',  # e.g., "Bakı Salyan şossesi"
    ]

    for pattern in patterns:
        match = re.search(pattern, address, re.IGNORECASE)
        if match:
            return match.group(1)

    # Check for specific keywords
    if 'Bakı' in address or 'Baki' in address:
        return 'Bakı'

    # Fallback: first word
    words = address.split()
    if words:
        first_word = words[0].rstrip(',')
        if len(first_word) > 2:
            return first_word

    return None


def normalize_station_data(stations: List[Dict]) -> List[Dict]:
    """Normalize and deduplicate station data."""
    # Deduplicate by name
    seen_names = set()
    unique_stations = []

    for station in stations:
        name = station.get('name', '')
        if name and name not in seen_names:
            seen_names.add(name)

            # Extract city from address
            if 'address' in station and 'city' not in station:
                city = extract_city_from_address(station['address'])
                if city:
                    station['city'] = city

            unique_stations.append(station)

    # Sort by station number
    def get_station_number(s):
        match = re.search(r'(\d+)', s.get('name', ''))
        return int(match.group(1)) if match else 999

    unique_stations.sort(key=get_station_number)

    return unique_stations


def scrape_socar() -> List[Dict]:
    """Main scraping function."""
    print("=" * 60)
    print("SOCAR Petroleum Gas Station Scraper")
    print("=" * 60)

    all_stations = []

    print(f"\nFetching data from {len(MYMAPS_IDS)} Google MyMaps...")

    for i, map_id in enumerate(MYMAPS_IDS, 1):
        print(f"\nMap {i}: {map_id}")

        # Fetch KMZ
        kmz_content = fetch_kmz(map_id)
        if not kmz_content:
            continue

        # Extract KML
        kml_content = extract_kml_from_kmz(kmz_content)
        if not kml_content:
            continue

        # Parse stations
        stations = parse_kml_stations(kml_content)
        print(f"  Found {len(stations)} stations")

        all_stations.extend(stations)

    # Normalize and deduplicate
    print(f"\nTotal raw stations: {len(all_stations)}")
    normalized = normalize_station_data(all_stations)
    print(f"After deduplication: {len(normalized)} unique stations")

    return normalized


def save_to_csv(stations: List[Dict], output_file: Path) -> None:
    """Save station data to CSV file."""
    if not stations:
        print("No stations to save!")
        return

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Define column order
    priority_fields = ['name', 'address', 'city', 'latitude', 'longitude', 'gps_coordinates', 'image_url']

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

    # Count with all data
    with_address = sum(1 for s in stations if s.get('address'))
    with_images = sum(1 for s in stations if s.get('image_url'))

    print(f"  With address: {with_address}")
    print(f"  With images: {with_images}")

    # Count by city
    cities = {}
    for s in stations:
        city = s.get('city', 'Unknown')
        cities[city] = cities.get(city, 0) + 1

    print(f"  Cities/Regions: {len(cities)}")
    print("  Top locations:")
    for city, count in sorted(cities.items(), key=lambda x: -x[1])[:5]:
        print(f"    - {city}: {count} stations")


def main():
    """Main entry point."""
    # Fix Windows console encoding
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except AttributeError:
            pass

    try:
        stations = scrape_socar()

        if not stations:
            print("\nNo stations found.")
            print("The Google MyMaps may have been updated or removed.")
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
