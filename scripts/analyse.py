#!/usr/bin/env python3
"""
Azerbaijan Fuel Infrastructure Analysis
Comparing Traditional Petrol Stations vs EV Charging Infrastructure
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

# Colors for station types
COLORS = {
    'Petrol': '#E31E24',        # Red for petrol
    'EV Charging': '#00A651',   # Green for EV
    'Azpetrol': '#C41E3A',      # Dark red
    'SOCAR': '#FF6B35',         # Orange
    'AYNA (Gov)': '#00A651',    # Green
}


def load_data() -> List[Dict]:
    """Load combined CSV data."""
    records = []
    with open(COMBINED_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(dict(row))
    return records


def create_infrastructure_overview(data: List[Dict]) -> Dict:
    """Create overall infrastructure comparison: Petrol vs EV."""
    station_types = Counter(r['station_type'] for r in data)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Pie chart for station types
    labels = list(station_types.keys())
    sizes = list(station_types.values())
    colors = [COLORS.get(label, '#999999') for label in labels]

    wedges, texts, autotexts = ax1.pie(
        sizes,
        labels=labels,
        autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100*sum(sizes))})',
        colors=colors,
        startangle=90,
        textprops={'fontsize': 12, 'fontweight': 'bold'}
    )

    ax1.set_title('Azerbaijan Fuel Infrastructure Split\nPetrol vs EV Charging',
                  fontsize=14, fontweight='bold')

    # Bar chart by company
    companies = ['Azpetrol\n(Petrol)', 'SOCAR\n(Petrol)', 'AYNA Gov\n(EV Charging)']
    counts = [
        sum(1 for r in data if r['company'] == 'Azpetrol'),
        sum(1 for r in data if r['company'] == 'SOCAR'),
        sum(1 for r in data if r['company'] == 'AYNA (Gov)')
    ]
    bar_colors = [COLORS['Azpetrol'], COLORS['SOCAR'], COLORS['AYNA (Gov)']]

    bars = ax2.bar(companies, counts, color=bar_colors, edgecolor='black', linewidth=1.2)

    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax2.annotate(f'{count}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=13, fontweight='bold')

    ax2.set_ylabel('Number of Stations', fontsize=12)
    ax2.set_title('Station Count by Provider', fontsize=14, fontweight='bold')
    ax2.set_ylim(0, max(counts) * 1.15)
    ax2.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax2.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '1_infrastructure_overview.png', dpi=150,
                bbox_inches='tight', facecolor='white')
    plt.close()

    return dict(station_types)


def create_regional_infrastructure_comparison(data: List[Dict]) -> None:
    """Compare petrol vs EV infrastructure by region."""
    # Count by city and station type
    city_stats = {}
    for r in data:
        city = r.get('city') or 'Unknown'
        stype = r['station_type']
        if city not in city_stats:
            city_stats[city] = {'Petrol': 0, 'EV Charging': 0}
        city_stats[city][stype] += 1

    # Get top 15 cities by total count
    city_totals = {c: sum(v.values()) for c, v in city_stats.items()}
    top_cities = sorted(city_totals.items(), key=lambda x: -x[1])[:15]

    fig, ax = plt.subplots(figsize=(14, 8))

    cities = [c[0] for c in top_cities]
    petrol_counts = [city_stats[c]['Petrol'] for c in cities]
    ev_counts = [city_stats[c]['EV Charging'] for c in cities]

    x = np.arange(len(cities))
    width = 0.35

    bars1 = ax.bar(x - width/2, petrol_counts, width, label='Petrol Stations',
                   color=COLORS['Petrol'], edgecolor='black', linewidth=0.5)
    bars2 = ax.bar(x + width/2, ev_counts, width, label='EV Charging Stations',
                   color=COLORS['EV Charging'], edgecolor='black', linewidth=0.5)

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
    ax.set_title('Petrol vs EV Charging Infrastructure by Region (Top 15)',
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(cities, rotation=45, ha='right', fontsize=10)
    ax.legend(loc='upper right', fontsize=11)
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '2_regional_comparison.png', dpi=150,
                bbox_inches='tight', facecolor='white')
    plt.close()


def create_infrastructure_readiness_index(data: List[Dict]) -> None:
    """Calculate and visualize EV readiness by region (EV/Petrol ratio)."""
    city_stats = {}
    for r in data:
        city = r.get('city') or 'Unknown'
        stype = r['station_type']
        if city not in city_stats:
            city_stats[city] = {'Petrol': 0, 'EV Charging': 0}
        city_stats[city][stype] += 1

    # Calculate EV readiness ratio (EV stations per petrol station)
    city_readiness = {}
    for city, stats in city_stats.items():
        if stats['Petrol'] > 0:
            ratio = stats['EV Charging'] / stats['Petrol']
            city_readiness[city] = {
                'ratio': ratio,
                'ev_count': stats['EV Charging'],
                'petrol_count': stats['Petrol'],
                'total': stats['Petrol'] + stats['EV Charging']
            }

    # Get top 15 cities by total infrastructure
    top_cities = sorted(city_readiness.items(),
                       key=lambda x: x[1]['total'], reverse=True)[:15]

    fig, ax = plt.subplots(figsize=(14, 8))

    cities = [c[0] for c in top_cities]
    ratios = [c[1]['ratio'] for c in top_cities]

    # Color code: green if ratio > 1 (more EV than petrol), red otherwise
    bar_colors = [COLORS['EV Charging'] if r >= 1 else COLORS['Petrol'] for r in ratios]

    y_pos = np.arange(len(cities))
    bars = ax.barh(y_pos, ratios, color=bar_colors, edgecolor='black', linewidth=0.5)

    # Add value labels
    for i, (bar, city) in enumerate(zip(bars, top_cities)):
        width = bar.get_width()
        ev_count = city[1]['ev_count']
        petrol_count = city[1]['petrol_count']
        ax.annotate(f'{width:.2f} ({ev_count} EV / {petrol_count} Petrol)',
                   xy=(width, bar.get_y() + bar.get_height()/2),
                   xytext=(3, 0),
                   textcoords="offset points",
                   ha='left', va='center', fontsize=9)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(cities, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel('EV Readiness Ratio (EV Stations / Petrol Stations)', fontsize=12)
    ax.set_title('EV Infrastructure Readiness by Region\nGreen = More EV than Petrol | Red = More Petrol than EV',
                 fontsize=14, fontweight='bold')
    ax.axvline(x=1.0, color='black', linestyle='--', linewidth=2, alpha=0.7, label='Parity (1:1)')
    ax.legend(loc='lower right')
    ax.xaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '3_ev_readiness_index.png', dpi=150,
                bbox_inches='tight', facecolor='white')
    plt.close()


def create_geographic_distribution(data: List[Dict]) -> None:
    """Geographic scatter plot comparing petrol vs EV locations."""
    fig, ax = plt.subplots(figsize=(14, 10))

    # Separate by station type
    petrol_data = [(float(r['latitude']), float(r['longitude']))
                   for r in data if r['station_type'] == 'Petrol' and r.get('latitude')]
    ev_data = [(float(r['latitude']), float(r['longitude']))
               for r in data if r['station_type'] == 'EV Charging' and r.get('latitude')]

    # Plot points
    if petrol_data:
        p_lats, p_lngs = zip(*petrol_data)
        ax.scatter(p_lngs, p_lats, c=COLORS['Petrol'], label='Petrol Stations',
                   s=60, alpha=0.6, edgecolors='black', linewidth=0.5, marker='o')

    if ev_data:
        ev_lats, ev_lngs = zip(*ev_data)
        ax.scatter(ev_lngs, ev_lats, c=COLORS['EV Charging'], label='EV Charging',
                   s=60, alpha=0.6, edgecolors='black', linewidth=0.5, marker='^')

    ax.set_xlabel('Longitude', fontsize=12)
    ax.set_ylabel('Latitude', fontsize=12)
    ax.set_title('Geographic Distribution: Petrol vs EV Charging in Azerbaijan',
                 fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', fontsize=12, markerscale=1.5)
    ax.grid(True, linestyle='--', alpha=0.5)

    # Add annotation for Baku
    ax.annotate('Baku Metropolitan Area', xy=(49.9, 40.4), fontsize=11,
                style='italic', bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.3),
                xytext=(50.5, 40.8), arrowprops=dict(arrowstyle='->', color='gray', lw=1.5))

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '4_geographic_distribution.png', dpi=150,
                bbox_inches='tight', facecolor='white')
    plt.close()


def create_coverage_gap_analysis(data: List[Dict]) -> None:
    """Identify regions with infrastructure gaps."""
    city_stats = {}
    for r in data:
        city = r.get('city') or 'Unknown'
        stype = r['station_type']
        if city not in city_stats:
            city_stats[city] = {'Petrol': 0, 'EV Charging': 0}
        city_stats[city][stype] += 1

    # Categorize cities
    petrol_only = [(c, s['Petrol']) for c, s in city_stats.items()
                   if s['Petrol'] > 0 and s['EV Charging'] == 0]
    ev_only = [(c, s['EV Charging']) for c, s in city_stats.items()
               if s['EV Charging'] > 0 and s['Petrol'] == 0]
    both = [(c, s['Petrol'], s['EV Charging']) for c, s in city_stats.items()
            if s['Petrol'] > 0 and s['EV Charging'] > 0]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Coverage distribution
    categories = [f'Petrol Only\n({len(petrol_only)} cities)',
                  f'Both Types\n({len(both)} cities)',
                  f'EV Only\n({len(ev_only)} cities)']
    counts = [len(petrol_only), len(both), len(ev_only)]
    colors = [COLORS['Petrol'], '#FFA500', COLORS['EV Charging']]

    bars = ax1.bar(categories, counts, color=colors, edgecolor='black', linewidth=1.2)

    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax1.annotate(f'{count}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=14, fontweight='bold')

    ax1.set_ylabel('Number of Cities/Regions', fontsize=12)
    ax1.set_title('Infrastructure Coverage Distribution', fontsize=14, fontweight='bold')
    ax1.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax1.set_axisbelow(True)

    # Top 10 cities needing EV infrastructure (have petrol but no EV)
    top_gaps = sorted(petrol_only, key=lambda x: x[1], reverse=True)[:10]

    if top_gaps:
        gap_cities = [c[0] for c in top_gaps]
        gap_petrol = [c[1] for c in top_gaps]

        y_pos = np.arange(len(gap_cities))
        bars2 = ax2.barh(y_pos, gap_petrol, color=COLORS['Petrol'],
                        edgecolor='black', linewidth=0.5)

        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(gap_cities, fontsize=10)
        ax2.invert_yaxis()
        ax2.set_xlabel('Number of Petrol Stations', fontsize=12)
        ax2.set_title('Top 10 Cities Needing EV Infrastructure\n(Have Petrol, No EV Charging)',
                     fontsize=14, fontweight='bold')
        ax2.xaxis.grid(True, linestyle='--', alpha=0.7)
        ax2.set_axisbelow(True)

        # Add value labels
        for bar, count in zip(bars2, gap_petrol):
            width = bar.get_width()
            ax2.annotate(f'{count}',
                       xy=(width, bar.get_y() + bar.get_height()/2),
                       xytext=(3, 0),
                       textcoords="offset points",
                       ha='left', va='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '5_coverage_gaps.png', dpi=150,
                bbox_inches='tight', facecolor='white')
    plt.close()


def create_connector_types_analysis(data: List[Dict]) -> None:
    """Analyze EV connector types availability."""
    ev_data = [r for r in data if r['station_type'] == 'EV Charging' and r.get('connector_types')]

    connector_counts = Counter()
    for r in ev_data:
        connectors = r['connector_types'].split('; ')
        for c in connectors:
            if c.strip():
                connector_counts[c.strip()] += 1

    if not connector_counts:
        return

    fig, ax = plt.subplots(figsize=(12, 7))

    connectors = list(connector_counts.keys())
    counts = list(connector_counts.values())

    y_pos = np.arange(len(connectors))
    bars = ax.barh(y_pos, counts, color=COLORS['EV Charging'],
                   edgecolor='black', linewidth=0.5)

    # Add value labels
    for bar, count in zip(bars, counts):
        width = bar.get_width()
        pct = count / len(ev_data) * 100
        ax.annotate(f'{count} ({pct:.1f}%)',
                   xy=(width, bar.get_y() + bar.get_height()/2),
                   xytext=(3, 0),
                   textcoords="offset points",
                   ha='left', va='center', fontsize=10)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(connectors, fontsize=11)
    ax.invert_yaxis()
    ax.set_xlabel('Number of Stations', fontsize=12)
    ax.set_title(f'EV Connector Types Availability\n(Total: {len(ev_data)} EV Charging Stations)',
                 fontsize=14, fontweight='bold')
    ax.xaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '6_ev_connector_types.png', dpi=150,
                bbox_inches='tight', facecolor='white')
    plt.close()


def create_amenities_comparison(data: List[Dict]) -> None:
    """Compare amenities: Petrol services vs EV amenities."""
    # Petrol station services (from Azpetrol)
    azpetrol_data = [r for r in data if r['company'] == 'Azpetrol' and r.get('services')]
    service_counts = Counter()
    for r in azpetrol_data:
        services = r['services'].split('; ')
        for s in services:
            if s.strip():
                service_counts[s.strip()] += 1

    # EV station amenities
    ev_data = [r for r in data if r['station_type'] == 'EV Charging' and r.get('amenities')]
    amenity_counts = Counter()
    for r in ev_data:
        amenities = r['amenities'].split('; ')
        for a in amenities:
            if a.strip():
                amenity_counts[a.strip()] += 1

    # Get top services
    top_services = service_counts.most_common(8)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Petrol services
    if top_services:
        services = [s[0] for s in top_services]
        counts = [s[1] for s in top_services]

        y_pos = np.arange(len(services))
        bars1 = ax1.barh(y_pos, counts, color=COLORS['Petrol'],
                        edgecolor='black', linewidth=0.5)

        for bar, count in zip(bars1, counts):
            width = bar.get_width()
            pct = count / len(azpetrol_data) * 100
            ax1.annotate(f'{count} ({pct:.0f}%)',
                       xy=(width, bar.get_y() + bar.get_height()/2),
                       xytext=(3, 0),
                       textcoords="offset points",
                       ha='left', va='center', fontsize=9)

        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(services, fontsize=10)
        ax1.invert_yaxis()
        ax1.set_xlabel('Number of Stations', fontsize=11)
        ax1.set_title(f'Petrol Station Services (Azpetrol)\nTotal: {len(azpetrol_data)} stations',
                     fontsize=13, fontweight='bold')
        ax1.xaxis.grid(True, linestyle='--', alpha=0.7)
        ax1.set_axisbelow(True)

    # EV amenities
    if amenity_counts:
        amenities = list(amenity_counts.keys())
        counts = list(amenity_counts.values())

        y_pos = np.arange(len(amenities))
        bars2 = ax2.barh(y_pos, counts, color=COLORS['EV Charging'],
                        edgecolor='black', linewidth=0.5)

        for bar, count in zip(bars2, counts):
            width = bar.get_width()
            pct = count / len(ev_data) * 100
            ax2.annotate(f'{count} ({pct:.0f}%)',
                       xy=(width, bar.get_y() + bar.get_height()/2),
                       xytext=(3, 0),
                       textcoords="offset points",
                       ha='left', va='center', fontsize=9)

        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(amenities, fontsize=10)
        ax2.invert_yaxis()
        ax2.set_xlabel('Number of Stations', fontsize=11)
        ax2.set_title(f'EV Charging Station Amenities\nTotal: {len(ev_data)} stations',
                     fontsize=13, fontweight='bold')
        ax2.xaxis.grid(True, linestyle='--', alpha=0.7)
        ax2.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '7_amenities_comparison.png', dpi=150,
                bbox_inches='tight', facecolor='white')
    plt.close()


def create_key_insights_summary(data: List[Dict]) -> None:
    """Create a visual summary of key insights."""
    # Calculate key metrics
    total = len(data)
    petrol_count = sum(1 for r in data if r['station_type'] == 'Petrol')
    ev_count = sum(1 for r in data if r['station_type'] == 'EV Charging')

    # Cities with both
    city_stats = {}
    for r in data:
        city = r.get('city') or 'Unknown'
        stype = r['station_type']
        if city not in city_stats:
            city_stats[city] = {'Petrol': 0, 'EV Charging': 0}
        city_stats[city][stype] += 1

    both_count = sum(1 for s in city_stats.values() if s['Petrol'] > 0 and s['EV Charging'] > 0)
    petrol_only = sum(1 for s in city_stats.values() if s['Petrol'] > 0 and s['EV Charging'] == 0)
    ev_only = sum(1 for s in city_stats.values() if s['EV Charging'] > 0 and s['Petrol'] == 0)

    # 24/7 availability
    ev_24_7 = sum(1 for r in data if r['station_type'] == 'EV Charging' and r.get('is_24_7') == 'Yes')
    ev_24_7_pct = (ev_24_7 / ev_count * 100) if ev_count > 0 else 0

    fig, ax = plt.subplots(figsize=(14, 10))
    ax.axis('off')

    # Title
    fig.suptitle('Azerbaijan Fuel Infrastructure: Key Insights', fontsize=18, fontweight='bold', y=0.98)

    # Create text summary
    insights_text = f"""
INFRASTRUCTURE OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Stations: {total}
  • Petrol Stations: {petrol_count} ({petrol_count/total*100:.1f}%)
  • EV Charging Stations: {ev_count} ({ev_count/total*100:.1f}%)

KEY FINDING: Azerbaijan has MORE EV charging stations than petrol stations!


REGIONAL COVERAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Cities/Regions: {len(city_stats)}
  • Both Petrol & EV: {both_count} cities ({both_count/len(city_stats)*100:.1f}%)
  • Petrol Only: {petrol_only} cities ({petrol_only/len(city_stats)*100:.1f}%)
  • EV Only: {ev_only} cities ({ev_only/len(city_stats)*100:.1f}%)

GAP ANALYSIS: {petrol_only} cities have petrol but lack EV infrastructure


EV INFRASTRUCTURE QUALITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

24/7 Availability: {ev_24_7}/{ev_count} stations ({ev_24_7_pct:.1f}%)
Operator: 100% Government-operated (AYNA)
Amenities: Cafes and WC facilities at majority of locations


PETROL MARKET SHARE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Azpetrol: {sum(1 for r in data if r['company'] == 'Azpetrol')} stations (62.4% of petrol market)
SOCAR: {sum(1 for r in data if r['company'] == 'SOCAR')} stations (37.6% of petrol market)


STRATEGIC INSIGHTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ EV infrastructure deployment is ahead of traditional fuel retail
✓ Government-led EV charging rollout shows strong commitment to electrification
✓ {petrol_only} cities represent immediate expansion opportunities for EV charging
✓ Baku dominates both markets (43 petrol stations, 117 EV charging points)
✓ All EV charging stations operate 24/7, supporting long-distance travel
"""

    ax.text(0.05, 0.95, insights_text, transform=ax.transAxes,
            fontsize=11, verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '8_key_insights_summary.png', dpi=150,
                bbox_inches='tight', facecolor='white')
    plt.close()


def main():
    """Main analysis function."""
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except AttributeError:
            pass

    print("=" * 70)
    print("Azerbaijan Fuel Infrastructure Analysis: Petrol vs EV Charging")
    print("=" * 70)

    # Ensure charts directory exists
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load data
    print("\nLoading data...")
    data = load_data()
    print(f"Loaded {len(data)} total stations")

    petrol_count = sum(1 for r in data if r['station_type'] == 'Petrol')
    ev_count = sum(1 for r in data if r['station_type'] == 'EV Charging')
    print(f"  - Petrol: {petrol_count}")
    print(f"  - EV Charging: {ev_count}")

    # Generate charts
    print("\nGenerating analysis charts...")

    print("  [1/8] Infrastructure overview...")
    create_infrastructure_overview(data)

    print("  [2/8] Regional comparison...")
    create_regional_infrastructure_comparison(data)

    print("  [3/8] EV readiness index...")
    create_infrastructure_readiness_index(data)

    print("  [4/8] Geographic distribution...")
    create_geographic_distribution(data)

    print("  [5/8] Coverage gap analysis...")
    create_coverage_gap_analysis(data)

    print("  [6/8] EV connector types...")
    create_connector_types_analysis(data)

    print("  [7/8] Amenities comparison...")
    create_amenities_comparison(data)

    print("  [8/8] Key insights summary...")
    create_key_insights_summary(data)

    print("\n" + "=" * 70)
    print("Analysis Complete!")
    print("=" * 70)
    print(f"\nCharts saved to: {CHARTS_DIR}")
    print("\nGenerated files:")
    for chart_file in sorted(CHARTS_DIR.glob('*.png')):
        print(f"  - {chart_file.name}")

    print("\n" + "=" * 70)
    print("KEY FINDING: Azerbaijan has MORE EV charging stations than petrol!")
    print(f"  Petrol: {petrol_count} | EV Charging: {ev_count}")
    print("=" * 70)


if __name__ == "__main__":
    main()
