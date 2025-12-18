#!/usr/bin/env python3
"""
EV Charging Stations Scraper for Azerbaijan
============================================

This script scrapes electric vehicle charging station data from the
Azerbaijan government's Electronic Data Management system (edm.ayna.gov.az).

Data Source:
    - API: https://edm.ayna.gov.az/getFilteredChargePointsInBoundingBox
    - Format: JSON
    - Coverage: All of Azerbaijan

Output:
    - File: data/ev_charging.csv
    - Fields: company, name, address, city, latitude, longitude,
              status, power_kw, connector_types, station_type, image_url, source_url

Author: Generated for gas_station_analyse project
Date: 2025-12-18
"""

import requests
import csv
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Fix for Windows console encoding issues
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


class EVChargingStationScraper:
    """Scraper for EV charging stations from edm.ayna.gov.az"""

    def __init__(self):
        self.api_url = "https://edm.ayna.gov.az/getFilteredChargePointsInBoundingBox"
        # Bounding box covering all of Azerbaijan
        self.params = {
            'bottomLeftPointLatitude': '38.143299488708834',
            'bottomLeftPointLongitude': '45.22755474768201',
            'topRightPointLatitude': '41.93070887845769',
            'topRightPointLongitude': '50.62244125692294',
            'lng': 'az'  # Azerbaijani language
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://edm.ayna.gov.az/'
        }
        self.stations: List[Dict[str, Any]] = []

    def fetch_data(self) -> Dict[str, Any]:
        """Fetch charging station data from the API"""
        print("Fetching EV charging station data from edm.ayna.gov.az...")

        try:
            response = requests.get(
                self.api_url,
                params=self.params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            print(f"✓ Successfully fetched data")
            print(f"  Response size: {len(response.content):,} bytes")

            return data

        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching data: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"✗ Error parsing JSON: {e}")
            raise

    def extract_city_from_address(self, address: str) -> str:
        """Extract city/region from address using Azerbaijani patterns"""
        if not address:
            return ""

        # Extract city from addresses like "Sultan Əliyev 1, Haftoni, Lənkəran, Azərbaycan"
        # Usually the third or second-to-last component is the city
        parts = [p.strip() for p in address.split(',') if p.strip()]

        # Filter out country name and common non-city parts
        filtered = [p for p in parts if p not in ['Azərbaycan', 'Azerbaijan'] and not re.match(r'^AZ\d+$', p)]

        # Common Azerbaijani city/region patterns
        patterns = [
            r'([A-ZƏŞÇÖÜĞİ][a-zəşçöüğı]+)\s+şəhəri',  # City name
            r'([A-ZƏŞÇÖÜĞİ][a-zəşçöüğı]+)\s+rayonu',   # District name
        ]

        # Try patterns on all parts
        for part in filtered:
            for pattern in patterns:
                match = re.search(pattern, part)
                if match:
                    return match.group(1)

        # If we have filtered parts, likely the last one is the city
        if filtered:
            # Check if last part looks like a city name (not a street address)
            last_part = filtered[-1]
            if not any(char.isdigit() for char in last_part):
                return last_part

        # Fallback to second-to-last comma-separated part or first word
        if len(parts) >= 2:
            return parts[-2] if not any(char.isdigit() for char in parts[-2]) else parts[0].split()[0]

        return parts[0].split()[0] if parts else ""

    def parse_station_data(self, data: Dict[str, Any]) -> None:
        """Parse the JSON response and extract station information"""
        print("\nParsing station data...")

        # Access the charge_points array from result
        result = data.get('result', {})
        charge_points = result.get('charge_points', [])

        if not charge_points:
            print("⚠ No charge points found in response")
            print(f"  Response keys: {list(data.keys())}")
            if result:
                print(f"  Result keys: {list(result.keys())}")
            return

        print(f"  Found {len(charge_points)} charge points in API response")

        seen_stations = set()  # For deduplication

        for point in charge_points:
            try:
                # Extract basic information
                station_id = str(point.get('_id', ''))
                name = point.get('name', '').strip()
                address = point.get('address', '').strip()
                phone = point.get('phone', '').strip()

                # GPS coordinates from GeoJSON geometry (format: [longitude, latitude])
                geometry = point.get('geometry', {})
                coordinates = geometry.get('coordinates', [])

                if len(coordinates) >= 2:
                    longitude = coordinates[0]  # First is longitude
                    latitude = coordinates[1]   # Second is latitude
                else:
                    longitude = None
                    latitude = None

                # Skip if missing critical data
                if not all([name, latitude, longitude]):
                    continue

                # Deduplication key
                dedup_key = f"{name}_{latitude}_{longitude}"
                if dedup_key in seen_stations:
                    continue
                seen_stations.add(dedup_key)

                # Extract city from address
                city = self.extract_city_from_address(address)

                # Connector types from types array
                types_list = point.get('types', [])
                connector_types = []
                for conn_type in types_list:
                    if isinstance(conn_type, dict):
                        type_name = conn_type.get('name', '')
                        if type_name:
                            connector_types.append(type_name)
                connector_types_str = '; '.join(connector_types)

                # Amenities
                has_cafe = point.get('cafe', False)
                has_wc = point.get('wc', False)
                amenities = []
                if has_cafe:
                    amenities.append('Cafe')
                if has_wc:
                    amenities.append('WC')
                amenities_str = '; '.join(amenities)

                # Quantity and tariffs
                quantity = point.get('quantity', '0')
                tariffs = point.get('tariffs', '0')

                # Working hours (24/7 if all days are active with 0-1440 minutes)
                working_hours = point.get('working_hours', [])
                is_24_7 = all(
                    day.get('active', False) and
                    day.get('start', -1) == 0 and
                    day.get('end', -1) == 1440
                    for day in working_hours
                ) if working_hours else False

                # Create station record
                station = {
                    'company': 'AYNA (Gov)',  # Government network
                    'name': name,
                    'address': address,
                    'city': city,
                    'latitude': float(latitude),
                    'longitude': float(longitude),
                    'phone': phone,
                    'connector_types': connector_types_str,
                    'amenities': amenities_str,
                    'quantity': quantity,
                    'tariffs': tariffs,
                    'is_24_7': 'Yes' if is_24_7 else 'No',
                    'station_id': station_id,
                    'source_url': 'https://edm.ayna.gov.az/',
                    'scraped_at': datetime.now().isoformat()
                }

                self.stations.append(station)

            except Exception as e:
                print(f"⚠ Error parsing station {point.get('name', 'unknown')}: {e}")
                continue

        print(f"✓ Parsed {len(self.stations)} unique EV charging stations")

    def save_to_csv(self, output_file: str) -> None:
        """Save the scraped data to a CSV file"""
        if not self.stations:
            print("⚠ No stations to save")
            return

        # Ensure output directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"\nSaving data to {output_file}...")

        # Define CSV columns
        fieldnames = [
            'company',
            'name',
            'address',
            'city',
            'latitude',
            'longitude',
            'phone',
            'connector_types',
            'amenities',
            'quantity',
            'tariffs',
            'is_24_7',
            'station_id',
            'source_url',
            'scraped_at'
        ]

        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.stations)

            print(f"✓ Successfully saved {len(self.stations)} stations to {output_file}")

            # Print summary statistics
            self.print_summary()

        except Exception as e:
            print(f"✗ Error saving to CSV: {e}")
            raise

    def print_summary(self) -> None:
        """Print summary statistics of the scraped data"""
        print("\n" + "="*50)
        print("EV CHARGING STATIONS SCRAPING SUMMARY")
        print("="*50)

        print(f"\nTotal Stations: {len(self.stations)}")

        # Count by company/operator
        companies = {}
        for station in self.stations:
            company = station['company']
            companies[company] = companies.get(company, 0) + 1

        print(f"\nStations by Operator:")
        for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True):
            print(f"  {company}: {count}")

        # Count by city
        cities = {}
        for station in self.stations:
            city = station['city'] or 'Unknown'
            cities[city] = cities.get(city, 0) + 1

        print(f"\nTop 10 Cities by Station Count:")
        for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {city}: {count}")

        # Count by 24/7 availability
        available_24_7 = sum(1 for s in self.stations if s.get('is_24_7') == 'Yes')
        print(f"\n24/7 Availability:")
        print(f"  24/7 Stations: {available_24_7}/{len(self.stations)} ({available_24_7/len(self.stations)*100:.1f}%)")

        # Data completeness
        print(f"\nData Completeness:")
        for field in ['address', 'city', 'phone', 'connector_types', 'amenities']:
            complete = sum(1 for s in self.stations if s.get(field))
            percentage = (complete / len(self.stations) * 100) if self.stations else 0
            print(f"  {field}: {complete}/{len(self.stations)} ({percentage:.1f}%)")

        print("="*50 + "\n")

    def run(self, output_file: str = 'data/ev_charging.csv') -> None:
        """Main method to run the complete scraping process"""
        print("Starting EV Charging Stations Scraper")
        print("="*50)

        try:
            # Fetch data from API
            data = self.fetch_data()

            # Parse the data
            self.parse_station_data(data)

            # Save to CSV
            self.save_to_csv(output_file)

            print("\n✓ Scraping completed successfully!")

        except Exception as e:
            print(f"\n✗ Scraping failed: {e}")
            raise


def main():
    """Entry point for the script"""
    scraper = EVChargingStationScraper()
    scraper.run()


if __name__ == "__main__":
    main()
