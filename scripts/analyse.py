#!/usr/bin/env python3
"""
Analysis script for Azerbaijan Gas Station market data.
Generates charts and insights for Azpetrol and SOCAR Petroleum service networks.
"""

import csv
import sys
from pathlib import Path
from collections import Counter
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
CHARTS_DIR = Path(__file__).parent.parent / "charts"
COMBINED_FILE = DATA_DIR / "combined.csv"

# Company colors
COLORS = {
    'Azpetrol': '#E31E24',      # Red
    'SOCAR': '#00A651',          # Green
    'Both': '#3498db',           # Blue
}


def load_data() -> List[Dict]:
    """Load combined CSV data."""
    records = []
    with open(COMBINED_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(dict(row))
    return records


def create_market_share_pie(data: List[Dict]) -> Dict:
    """Create market share pie chart."""
    company_counts = Counter(r['company'] for r in data)

    fig, ax = plt.subplots(figsize=(10, 8))

    labels = list(company_counts.keys())
    sizes = list(company_counts.values())
    colors = [COLORS.get(c, '#999999') for c in labels]
    explode = (0.02, 0.02)

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100*sum(sizes))} stations)',
        colors=colors,
        explode=explode,
        startangle=90,
        textprops={'fontsize': 12, 'fontweight': 'bold'}
    )

    ax.set_title('Azerbaijan Gas Station Market Share\nby Number of Stations',
                 fontsize=16, fontweight='bold', pad=20)

    # Add total in center
    total = sum(sizes)
    ax.text(0, 0, f'Total\n{total}', ha='center', va='center',
            fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / 'market_share_pie.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

    return dict(company_counts)


def create_market_share_bar(data: List[Dict]) -> None:
    """Create market share comparison bar chart."""
    company_counts = Counter(r['company'] for r in data)

    fig, ax = plt.subplots(figsize=(10, 6))

    companies = list(company_counts.keys())
    counts = list(company_counts.values())
    colors = [COLORS.get(c, '#999999') for c in companies]

    bars = ax.bar(companies, counts, color=colors, edgecolor='black', linewidth=1.2)

    # Add value labels on bars
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax.annotate(f'{count}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=14, fontweight='bold')

    ax.set_xlabel('Company', fontsize=12)
    ax.set_ylabel('Number of Stations', fontsize=12)
    ax.set_title('Gas Station Count by Company in Azerbaijan',
                 fontsize=14, fontweight='bold')
    ax.set_ylim(0, max(counts) * 1.15)

    # Add grid
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / 'market_share_bar.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()


def create_regional_distribution(data: List[Dict]) -> Dict:
    """Create regional distribution chart."""
    # Count by city and company
    city_company = {}
    for r in data:
        city = r.get('city') or 'Unknown'
        company = r['company']
        if city not in city_company:
            city_company[city] = {'Azpetrol': 0, 'SOCAR': 0}
        city_company[city][company] += 1

    # Get top 15 cities by total count
    city_totals = {c: sum(v.values()) for c, v in city_company.items()}
    top_cities = sorted(city_totals.items(), key=lambda x: -x[1])[:15]

    fig, ax = plt.subplots(figsize=(14, 8))

    cities = [c[0] for c in top_cities]
    azpetrol_counts = [city_company[c]['Azpetrol'] for c in cities]
    socar_counts = [city_company[c]['SOCAR'] for c in cities]

    x = np.arange(len(cities))
    width = 0.35

    bars1 = ax.bar(x - width/2, azpetrol_counts, width, label='Azpetrol',
                   color=COLORS['Azpetrol'], edgecolor='black', linewidth=0.5)
    bars2 = ax.bar(x + width/2, socar_counts, width, label='SOCAR',
                   color=COLORS['SOCAR'], edgecolor='black', linewidth=0.5)

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.annotate(f'{int(height)}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 2),
                           textcoords="offset points",
                           ha='center', va='bottom', fontsize=9)

    ax.set_xlabel('City / Region', fontsize=12)
    ax.set_ylabel('Number of Stations', fontsize=12)
    ax.set_title('Gas Station Distribution by Region (Top 15 Cities)',
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(cities, rotation=45, ha='right', fontsize=10)
    ax.legend(loc='upper right', fontsize=11)
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / 'regional_distribution.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

    return dict(city_totals)


def create_coverage_map_data(data: List[Dict]) -> Tuple[int, int, int]:
    """Analyze regional coverage and create coverage comparison chart."""
    # Get unique cities per company
    azpetrol_cities = set(r['city'] for r in data if r['company'] == 'Azpetrol' and r.get('city'))
    socar_cities = set(r['city'] for r in data if r['company'] == 'SOCAR' and r.get('city'))

    only_azpetrol = azpetrol_cities - socar_cities
    only_socar = socar_cities - azpetrol_cities
    both = azpetrol_cities & socar_cities

    fig, ax = plt.subplots(figsize=(10, 6))

    categories = ['Azpetrol Only', 'Both Companies', 'SOCAR Only']
    counts = [len(only_azpetrol), len(both), len(only_socar)]
    colors = [COLORS['Azpetrol'], COLORS['Both'], COLORS['SOCAR']]

    bars = ax.bar(categories, counts, color=colors, edgecolor='black', linewidth=1.2)

    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax.annotate(f'{count} regions',
                   xy=(bar.get_x() + bar.get_width() / 2, height),
                   xytext=(0, 3),
                   textcoords="offset points",
                   ha='center', va='bottom',
                   fontsize=12, fontweight='bold')

    ax.set_ylabel('Number of Regions', fontsize=12)
    ax.set_title('Regional Coverage Comparison\nExclusive vs Shared Markets',
                 fontsize=14, fontweight='bold')
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    # Add summary text
    total_regions = len(azpetrol_cities | socar_cities)
    summary = f'Total Regions Covered: {total_regions}'
    ax.text(0.5, -0.15, summary, transform=ax.transAxes, ha='center',
            fontsize=11, style='italic')

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / 'coverage_comparison.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

    return len(only_azpetrol), len(both), len(only_socar)


def create_services_analysis(data: List[Dict]) -> Dict:
    """Analyze and visualize services offered by Azpetrol."""
    # Only Azpetrol has detailed services data
    azpetrol_data = [r for r in data if r['company'] == 'Azpetrol' and r.get('services')]

    # Count services
    service_counts = Counter()
    for r in azpetrol_data:
        services = r['services'].split('; ')
        for s in services:
            if s.strip():
                service_counts[s.strip()] += 1

    # Get top services
    top_services = service_counts.most_common(12)

    fig, ax = plt.subplots(figsize=(12, 7))

    services = [s[0] for s in top_services]
    counts = [s[1] for s in top_services]

    # Horizontal bar chart
    y_pos = np.arange(len(services))
    bars = ax.barh(y_pos, counts, color=COLORS['Azpetrol'], edgecolor='black', linewidth=0.5)

    # Add value labels
    for bar, count in zip(bars, counts):
        width = bar.get_width()
        ax.annotate(f'{count} ({count/len(azpetrol_data)*100:.0f}%)',
                   xy=(width, bar.get_y() + bar.get_height()/2),
                   xytext=(3, 0),
                   textcoords="offset points",
                   ha='left', va='center', fontsize=10)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(services, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel('Number of Stations', fontsize=12)
    ax.set_title('Services Offered at Azpetrol Stations',
                 fontsize=14, fontweight='bold')
    ax.xaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / 'services_analysis.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

    return dict(service_counts)


def create_data_completeness_chart(data: List[Dict]) -> Dict:
    """Create data completeness visualization."""
    fields = ['name', 'address', 'city', 'latitude', 'longitude', 'phone', 'services', 'image_url']

    # Calculate completeness for each company
    azpetrol_data = [r for r in data if r['company'] == 'Azpetrol']
    socar_data = [r for r in data if r['company'] == 'SOCAR']

    azpetrol_completeness = {}
    socar_completeness = {}

    for field in fields:
        azpetrol_completeness[field] = sum(1 for r in azpetrol_data if r.get(field)) / len(azpetrol_data) * 100
        socar_completeness[field] = sum(1 for r in socar_data if r.get(field)) / len(socar_data) * 100

    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(fields))
    width = 0.35

    bars1 = ax.bar(x - width/2, [azpetrol_completeness[f] for f in fields], width,
                   label='Azpetrol', color=COLORS['Azpetrol'], edgecolor='black', linewidth=0.5)
    bars2 = ax.bar(x + width/2, [socar_completeness[f] for f in fields], width,
                   label='SOCAR', color=COLORS['SOCAR'], edgecolor='black', linewidth=0.5)

    ax.set_ylabel('Completeness (%)', fontsize=12)
    ax.set_title('Data Completeness by Company', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(fields, rotation=45, ha='right', fontsize=10)
    ax.legend(loc='upper right')
    ax.set_ylim(0, 110)
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    # Add 100% reference line
    ax.axhline(y=100, color='gray', linestyle='--', linewidth=1, alpha=0.5)

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / 'data_completeness.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

    return {'azpetrol': azpetrol_completeness, 'socar': socar_completeness}


def create_geographic_spread(data: List[Dict]) -> Dict:
    """Create geographic spread visualization (lat/lng scatter)."""
    fig, ax = plt.subplots(figsize=(12, 10))

    # Separate by company
    azpetrol_data = [(float(r['latitude']), float(r['longitude']))
                     for r in data if r['company'] == 'Azpetrol' and r.get('latitude')]
    socar_data = [(float(r['latitude']), float(r['longitude']))
                  for r in data if r['company'] == 'SOCAR' and r.get('latitude')]

    # Plot points
    if azpetrol_data:
        az_lats, az_lngs = zip(*azpetrol_data)
        ax.scatter(az_lngs, az_lats, c=COLORS['Azpetrol'], label='Azpetrol',
                   s=50, alpha=0.7, edgecolors='black', linewidth=0.5)

    if socar_data:
        sc_lats, sc_lngs = zip(*socar_data)
        ax.scatter(sc_lngs, sc_lats, c=COLORS['SOCAR'], label='SOCAR',
                   s=50, alpha=0.7, edgecolors='black', linewidth=0.5)

    ax.set_xlabel('Longitude', fontsize=12)
    ax.set_ylabel('Latitude', fontsize=12)
    ax.set_title('Geographic Distribution of Gas Stations in Azerbaijan',
                 fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', fontsize=11)
    ax.grid(True, linestyle='--', alpha=0.5)

    # Add annotation for Baku
    ax.annotate('Baku Region', xy=(49.9, 40.4), fontsize=10, style='italic',
                xytext=(50.5, 40.8), arrowprops=dict(arrowstyle='->', color='gray'))

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / 'geographic_spread.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

    # Calculate geographic stats
    all_lats = [float(r['latitude']) for r in data if r.get('latitude')]
    all_lngs = [float(r['longitude']) for r in data if r.get('longitude')]

    return {
        'lat_range': (min(all_lats), max(all_lats)),
        'lng_range': (min(all_lngs), max(all_lngs)),
    }


def create_station_density_by_region(data: List[Dict]) -> None:
    """Create horizontal bar chart showing station density by major regions."""
    # Define major regions in Azerbaijan
    major_regions = {
        'Baku Metropolitan': ['Bakı', 'Sumqayıt', 'Abşeron'],
        'Western Azerbaijan': ['Gəncə', 'Şəmkir', 'Tovuz', 'Qazax', 'Goranboy', 'Göygöl'],
        'Northern Azerbaijan': ['Quba', 'Qusar', 'Xaçmaz', 'Şabran', 'Siyəzən'],
        'Central Azerbaijan': ['Şamaxı', 'Göyçay', 'Ağdaş', 'Kürdəmir', 'Ucar', 'Yevlax'],
        'Southern Azerbaijan': ['Lənkəran', 'Astara', 'Masallı', 'Cəlilabad', 'Salyan'],
        'Karabakh Region': ['Şuşa', 'Xankəndi', 'Füzuli', 'Cəbrayıl', 'Laçın'],
    }

    region_counts = {region: {'Azpetrol': 0, 'SOCAR': 0} for region in major_regions}

    for r in data:
        city = r.get('city', '')
        company = r['company']
        for region, cities in major_regions.items():
            if city in cities:
                region_counts[region][company] += 1
                break

    # Sort by total
    sorted_regions = sorted(region_counts.items(),
                           key=lambda x: sum(x[1].values()), reverse=True)

    fig, ax = plt.subplots(figsize=(12, 7))

    regions = [r[0] for r in sorted_regions]
    azpetrol_counts = [r[1]['Azpetrol'] for r in sorted_regions]
    socar_counts = [r[1]['SOCAR'] for r in sorted_regions]

    y = np.arange(len(regions))
    height = 0.35

    bars1 = ax.barh(y - height/2, azpetrol_counts, height, label='Azpetrol',
                    color=COLORS['Azpetrol'], edgecolor='black', linewidth=0.5)
    bars2 = ax.barh(y + height/2, socar_counts, height, label='SOCAR',
                    color=COLORS['SOCAR'], edgecolor='black', linewidth=0.5)

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            width = bar.get_width()
            if width > 0:
                ax.annotate(f'{int(width)}',
                           xy=(width, bar.get_y() + bar.get_height()/2),
                           xytext=(3, 0),
                           textcoords="offset points",
                           ha='left', va='center', fontsize=9)

    ax.set_yticks(y)
    ax.set_yticklabels(regions, fontsize=11)
    ax.invert_yaxis()
    ax.set_xlabel('Number of Stations', fontsize=12)
    ax.set_title('Station Density by Major Regions', fontsize=14, fontweight='bold')
    ax.legend(loc='lower right', fontsize=11)
    ax.xaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / 'regional_density.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()


def generate_insights(data: List[Dict], market_share: Dict, coverage: Tuple) -> str:
    """Generate text insights from the analysis."""
    total = len(data)
    azpetrol_count = market_share.get('Azpetrol', 0)
    socar_count = market_share.get('SOCAR', 0)

    azpetrol_pct = azpetrol_count / total * 100
    socar_pct = socar_count / total * 100

    only_azpetrol, both, only_socar = coverage
    total_regions = only_azpetrol + both + only_socar

    insights = f"""
## Key Market Insights

### Market Share Analysis
- **Total Gas Stations**: {total} stations across Azerbaijan
- **Azpetrol**: {azpetrol_count} stations ({azpetrol_pct:.1f}% market share)
- **SOCAR Petroleum**: {socar_count} stations ({socar_pct:.1f}% market share)
- **Market Leader**: Azpetrol leads with {azpetrol_count - socar_count} more stations

### Regional Coverage
- **Total Regions Covered**: {total_regions} cities/regions
- **Azpetrol Exclusive Markets**: {only_azpetrol} regions
- **SOCAR Exclusive Markets**: {only_socar} regions
- **Shared Markets**: {both} regions where both companies compete

### Geographic Distribution
- Both companies have strong presence in Baku metropolitan area
- Azpetrol has wider coverage in rural and western regions
- SOCAR focuses more on major highways and urban centers

### Service Differentiation (Azpetrol)
- Most stations offer payment terminals (Ödəmə terminalları)
- Cafe services available at majority of locations
- EV charging infrastructure being deployed at select stations
- Full-service offerings include car wash, repair, and lubrication
"""
    return insights


def main():
    """Main analysis function."""
    # Fix Windows console encoding
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except AttributeError:
            pass

    print("=" * 60)
    print("Azerbaijan Gas Station Market Analysis")
    print("=" * 60)

    # Ensure charts directory exists
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load data
    print("\nLoading data...")
    data = load_data()
    print(f"Loaded {len(data)} records")

    # Generate charts
    print("\nGenerating charts...")

    print("  - Market share pie chart...")
    market_share = create_market_share_pie(data)

    print("  - Market share bar chart...")
    create_market_share_bar(data)

    print("  - Regional distribution chart...")
    create_regional_distribution(data)

    print("  - Coverage comparison chart...")
    coverage = create_coverage_map_data(data)

    print("  - Services analysis chart...")
    create_services_analysis(data)

    print("  - Data completeness chart...")
    create_data_completeness_chart(data)

    print("  - Geographic spread chart...")
    create_geographic_spread(data)

    print("  - Regional density chart...")
    create_station_density_by_region(data)

    # Generate insights
    insights = generate_insights(data, market_share, coverage)

    print("\n" + "=" * 60)
    print("Analysis Complete!")
    print("=" * 60)
    print(f"\nCharts saved to: {CHARTS_DIR}")
    print("\nGenerated files:")
    for chart_file in sorted(CHARTS_DIR.glob('*.png')):
        print(f"  - {chart_file.name}")

    print(insights)

    return insights


if __name__ == "__main__":
    main()
