#!/usr/bin/env python3
"""
Combines Azpetrol, SOCAR Petroleum gas station data, and EV charging station data
into a single unified dataset for comprehensive fuel infrastructure analysis.
"""

import csv
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

DATA_DIR = Path(__file__).parent.parent / "data"
AZPETROL_FILE = DATA_DIR / "azpetrol.csv"
SOCAR_FILE = DATA_DIR / "socar.csv"
EV_CHARGING_FILE = DATA_DIR / "ev_charging.csv"
OUTPUT_FILE = DATA_DIR / "combined.csv"


def read_csv(file_path: Path) -> List[Dict]:
    """Read CSV file and return list of dictionaries."""
    records = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(dict(row))
    except FileNotFoundError:
        print(f"Warning: File not found: {file_path}")
    return records


def normalize_record(record: Dict, company: str, station_type: str = 'Petrol') -> Dict:
    """Normalize a record to common schema.

    Args:
        record: Raw record from CSV
        company: Company name (Azpetrol, SOCAR, or AYNA (Gov))
        station_type: Type of station ('Petrol' or 'EV Charging')
    """
    normalized = {
        'station_type': station_type,
        'company': company,
        'name': record.get('name', ''),
        'address': record.get('address', ''),
        'city': record.get('city', ''),
        'latitude': record.get('latitude', ''),
        'longitude': record.get('longitude', ''),
        'phone': record.get('phone', ''),
        'services': record.get('services', ''),  # Petrol stations
        'connector_types': record.get('connector_types', ''),  # EV stations
        'amenities': record.get('amenities', ''),  # EV stations
        'is_24_7': record.get('is_24_7', ''),  # EV stations
        'image_url': record.get('image_url', ''),
        'source_url': record.get('source_url', ''),
    }

    # Add Azpetrol-specific fields
    if 'id' in record:
        normalized['station_id'] = record['id']
    elif 'station_id' in record:
        normalized['station_id'] = record['station_id']

    # Add SOCAR-specific fields
    if 'gps_coordinates' in record:
        normalized['gps_coordinates'] = record['gps_coordinates']

    return normalized


def combine_datasets() -> List[Dict]:
    """Load and combine all three datasets (Azpetrol, SOCAR, and EV charging)."""
    combined = []

    # Load Azpetrol data (Petrol stations)
    print(f"Loading Azpetrol data from: {AZPETROL_FILE}")
    azpetrol_records = read_csv(AZPETROL_FILE)
    print(f"  Found {len(azpetrol_records)} petrol stations")

    for record in azpetrol_records:
        normalized = normalize_record(record, 'Azpetrol', station_type='Petrol')
        combined.append(normalized)

    # Load SOCAR data (Petrol stations)
    print(f"\nLoading SOCAR data from: {SOCAR_FILE}")
    socar_records = read_csv(SOCAR_FILE)
    print(f"  Found {len(socar_records)} petrol stations")

    for record in socar_records:
        normalized = normalize_record(record, 'SOCAR', station_type='Petrol')
        combined.append(normalized)

    # Load EV Charging data
    print(f"\nLoading EV Charging data from: {EV_CHARGING_FILE}")
    ev_records = read_csv(EV_CHARGING_FILE)
    print(f"  Found {len(ev_records)} EV charging stations")

    for record in ev_records:
        normalized = normalize_record(record, 'AYNA (Gov)', station_type='EV Charging')
        combined.append(normalized)

    return combined


def save_combined_csv(records: List[Dict], output_file: Path) -> None:
    """Save combined records to CSV."""
    if not records:
        print("No records to save!")
        return

    # Define column order
    columns = [
        'station_type',
        'company',
        'name',
        'address',
        'city',
        'latitude',
        'longitude',
        'phone',
        'services',
        'connector_types',
        'amenities',
        'is_24_7',
        'station_id',
        'gps_coordinates',
        'image_url',
        'source_url',
        'combined_at'
    ]

    print(f"\nSaving combined data to: {output_file}")

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()

        combined_at = datetime.now().isoformat()
        for record in records:
            record['combined_at'] = combined_at
            writer.writerow(record)

    print(f"Successfully saved {len(records)} records")


def print_summary(records: List[Dict]) -> None:
    """Print summary statistics."""
    print("\n" + "=" * 60)
    print("COMBINED FUEL INFRASTRUCTURE DATASET SUMMARY")
    print("=" * 60)

    # Count by station type
    type_counts = {}
    for r in records:
        stype = r.get('station_type', 'Unknown')
        type_counts[stype] = type_counts.get(stype, 0) + 1

    print("\nRecords by Station Type:")
    for stype, count in sorted(type_counts.items()):
        pct = (count / len(records)) * 100 if records else 0
        print(f"  - {stype}: {count} stations ({pct:.1f}%)")
    print(f"  - TOTAL: {len(records)} stations")

    # Count by company
    company_counts = {}
    for r in records:
        company = r.get('company', 'Unknown')
        company_counts[company] = company_counts.get(company, 0) + 1

    print("\nRecords by Company:")
    for company, count in sorted(company_counts.items()):
        stype = next((r.get('station_type') for r in records if r.get('company') == company), '')
        print(f"  - {company} ({stype}): {count} stations")

    # Count by city
    city_counts = {}
    for r in records:
        city = r.get('city', 'Unknown') or 'Unknown'
        city_counts[city] = city_counts.get(city, 0) + 1

    print(f"\nUnique cities/regions: {len(city_counts)}")
    print("Top 10 locations:")
    for city, count in sorted(city_counts.items(), key=lambda x: -x[1])[:10]:
        # Count petrol vs EV in this city
        petrol_count = sum(1 for r in records if (r.get('city') or 'Unknown') == city and r.get('station_type') == 'Petrol')
        ev_count = sum(1 for r in records if (r.get('city') or 'Unknown') == city and r.get('station_type') == 'EV Charging')
        print(f"  - {city}: {count} total (Petrol: {petrol_count}, EV: {ev_count})")

    # Data completeness
    print("\nData Completeness:")
    fields = ['name', 'address', 'city', 'latitude', 'longitude', 'phone']
    for field in fields:
        count = sum(1 for r in records if r.get(field))
        pct = (count / len(records)) * 100 if records else 0
        print(f"  - {field}: {count}/{len(records)} ({pct:.1f}%)")


def main():
    """Main entry point."""
    # Fix Windows console encoding
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except AttributeError:
            pass

    print("=" * 60)
    print("Fuel Infrastructure Data Combiner")
    print("=" * 60)

    # Combine datasets
    combined = combine_datasets()

    if not combined:
        print("\nNo data to combine. Make sure to run the scrapers first:")
        print("  python scripts/azpetrol.py")
        print("  python scripts/socar.py")
        print("  python scripts/ev_charging.py")
        sys.exit(1)

    # Save combined CSV
    save_combined_csv(combined, OUTPUT_FILE)

    # Print summary
    print_summary(combined)

    print("\n" + "=" * 60)
    print("Combination completed successfully!")
    print(f"Output file: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
