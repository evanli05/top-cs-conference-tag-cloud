#!/bin/bash
# Test Script for Step 2: Data Fetching

echo "=================================="
echo "Step 2: Data Fetching Test"
echo "=================================="
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."

echo "1. Checking if raw data file exists..."
if [ -f "data/raw/kdd_papers.json" ]; then
    echo "   ✓ File exists: data/raw/kdd_papers.json"
    SIZE=$(ls -lh data/raw/kdd_papers.json | awk '{print $5}')
    echo "   ✓ File size: $SIZE"
else
    echo "   ✗ File not found!"
    exit 1
fi

echo ""
echo "2. Running Python validation tests..."
python3 << 'PYTHON_EOF'
import json
import sys

try:
    with open('data/raw/kdd_papers.json', 'r') as f:
        data = json.load(f)
    
    # Quick validation
    total = len(data['papers'])
    years = data['metadata']['years']
    
    print(f"   ✓ Total papers: {total}")
    print(f"   ✓ Years covered: {years}")
    
    # Check each year has data
    year_counts = {}
    for paper in data['papers']:
        year = paper.get('year')
        year_counts[year] = year_counts.get(year, 0) + 1
    
    all_years_present = all(year in year_counts for year in years)
    
    if all_years_present and total >= 2000:
        print("   ✓ Data validation PASSED")
        sys.exit(0)
    else:
        print("   ✗ Data validation FAILED")
        sys.exit(1)
        
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)
PYTHON_EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "✓ Step 2 Tests PASSED"
    echo "=================================="
else
    echo ""
    echo "=================================="
    echo "✗ Step 2 Tests FAILED"
    echo "=================================="
    exit 1
fi
