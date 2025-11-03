#!/bin/bash
# Test script for Step 4: Data Generation (Final JSON for frontend)

echo "========================================"
echo "Step 4 Test: Final Data Generation"
echo "========================================"

# Check if final data file exists
FINAL_FILE="../data/processed/wordcloud_data.json"

if [ ! -f "$FINAL_FILE" ]; then
    echo "❌ FAIL: Final data file not found at $FINAL_FILE"
    exit 1
fi

echo "✓ Final data file exists"

# Validate JSON structure using Python
python3 << 'EOF'
import json
import sys

try:
    with open('../data/processed/wordcloud_data.json', 'r') as f:
        data = json.load(f)

    # Check structure
    assert 'metadata' in data, "Missing 'metadata'"
    assert 'words' in data, "Missing 'words'"

    metadata = data['metadata']
    words = data['words']

    # Check metadata
    required_fields = ['conference', 'years', 'total_papers', 'total_keywords', 'categories']
    for field in required_fields:
        assert field in metadata, f"Missing metadata field: {field}"

    print(f"✓ Metadata structure valid")
    print(f"  - Conference: {metadata['conference']}")
    print(f"  - Years: {metadata['years']}")
    print(f"  - Total papers: {metadata['total_papers']}")
    print(f"  - Total keywords: {metadata['total_keywords']}")

    # Check words structure
    assert isinstance(words, list), "Words must be a list"
    assert len(words) > 0, "Words list is empty"

    print(f"✓ Words structure valid ({len(words)} words)")

    # Validate word objects
    for i, word in enumerate(words[:5]):  # Check first 5
        assert 'text' in word, f"Word {i} missing 'text'"
        assert 'value' in word, f"Word {i} missing 'value'"
        assert 'years' in word, f"Word {i} missing 'years'"
        assert isinstance(word['text'], str), f"Word {i} text not string"
        assert isinstance(word['value'], int), f"Word {i} value not int"
        assert isinstance(word['years'], dict), f"Word {i} years not dict"

    print(f"✓ Word objects valid")

    # Check year breakdowns exist
    year_breakdown_count = 0
    for word in words:
        if word['years']:
            year_breakdown_count += 1

    print(f"✓ Year breakdowns: {year_breakdown_count}/{len(words)} words have year data")

    if year_breakdown_count == 0:
        print("⚠ WARNING: No year breakdowns found!")
        sys.exit(1)

    # Show top 5 keywords
    print(f"\n✓ Top 5 keywords:")
    for i, word in enumerate(words[:5], 1):
        print(f"  {i}. '{word['text']}': {word['value']} occurrences")
        year_counts = ', '.join([f"{y}:{c}" for y, c in word['years'].items()])
        print(f"     Years: {year_counts}")

    print("\n✓ Step 4: All tests passed!")

except AssertionError as e:
    print(f"❌ FAIL: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ FAIL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

EOF

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✓✓✓ Step 4 TEST PASSED ✓✓✓"
    echo "========================================"
    echo "The word cloud data is ready for frontend!"
    echo ""
    echo "Next steps:"
    echo "  1. Start local server: python3 -m http.server 8000"
    echo "  2. Open browser: http://localhost:8000"
    echo "  3. Test the word cloud and filters!"
else
    echo ""
    echo "========================================"
    echo "❌❌❌ Step 4 TEST FAILED ❌❌❌"
    echo "========================================"
    exit 1
fi