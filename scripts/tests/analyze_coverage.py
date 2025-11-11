#!/usr/bin/env python3
"""
Analyze paper and abstract coverage for all conferences
"""
import json
import os
from collections import defaultdict

def analyze_conference_file(file_path):
    """Analyze a single conference JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Handle different JSON structures
    if isinstance(data, dict) and 'papers' in data:
        papers = data['papers']
        metadata = data.get('metadata', {})
    elif isinstance(data, list):
        papers = data
        metadata = {}
    else:
        papers = []
        metadata = {}

    total_papers = len(papers)
    papers_with_abstracts = sum(1 for p in papers if p.get('abstract'))

    # Year breakdown
    by_year = defaultdict(lambda: {'total': 0, 'with_abstract': 0})
    for paper in papers:
        year = paper.get('year')
        by_year[year]['total'] += 1
        if paper.get('abstract'):
            by_year[year]['with_abstract'] += 1

    return {
        'total_papers': total_papers,
        'papers_with_abstracts': papers_with_abstracts,
        'abstract_coverage': (papers_with_abstracts / total_papers * 100) if total_papers > 0 else 0,
        'by_year': dict(sorted(by_year.items()))
    }

def main():
    # Go up three levels: scripts/tests/ -> scripts/ -> project_root/
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    data_dir = os.path.join(project_root, 'data', 'raw')

    conferences = {
        'KDD': 'kdd_papers.json',
        'ICLR': 'iclr_papers.json',
        'AAAI': 'aaai_papers.json',
        'NeurIPS': 'neurips_papers.json',
        'CVPR': 'cvpr_papers.json',
        'IJCAI': 'ijcai_papers.json'
    }

    results = {}
    total_all = 0
    total_with_abstracts = 0

    for conf_name, file_name in conferences.items():
        file_path = os.path.join(data_dir, file_name)
        if os.path.exists(file_path):
            print(f"\n{'='*60}")
            print(f"Conference: {conf_name}")
            print('='*60)

            stats = analyze_conference_file(file_path)
            results[conf_name] = stats

            total_all += stats['total_papers']
            total_with_abstracts += stats['papers_with_abstracts']

            print(f"Total Papers: {stats['total_papers']:,}")
            print(f"Papers with Abstracts: {stats['papers_with_abstracts']:,}")
            print(f"Abstract Coverage: {stats['abstract_coverage']:.1f}%")
            print(f"\nYear-by-Year Breakdown:")
            print(f"{'Year':<8} {'Papers':<10} {'Abstracts':<12} {'Coverage':<10}")
            print('-' * 45)

            for year, data in stats['by_year'].items():
                coverage = (data['with_abstract'] / data['total'] * 100) if data['total'] > 0 else 0
                print(f"{year:<8} {data['total']:<10} {data['with_abstract']:<12} {coverage:.1f}%")
        else:
            print(f"\n[SKIP] {conf_name}: File not found")

    print(f"\n{'='*60}")
    print(f"OVERALL STATISTICS")
    print('='*60)
    print(f"Total Conferences: {len(results)}")
    print(f"Total Papers: {total_all:,}")
    print(f"Papers with Abstracts: {total_with_abstracts:,}")
    print(f"Overall Coverage: {(total_with_abstracts / total_all * 100) if total_all > 0 else 0:.1f}%")

    # Save results to JSON for README generation
    output_file = os.path.join(data_dir, 'coverage_stats.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'conferences': results,
            'overall': {
                'total_papers': total_all,
                'papers_with_abstracts': total_with_abstracts,
                'coverage': (total_with_abstracts / total_all * 100) if total_all > 0 else 0
            }
        }, f, indent=2)

    print(f"\nCoverage statistics saved to: {output_file}")

if __name__ == '__main__':
    main()
