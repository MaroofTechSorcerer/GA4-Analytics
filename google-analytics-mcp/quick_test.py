#!/usr/bin/env python3
"""
Quick test script for GA4 MCP Server
Run this to test the tools directly
"""

import sys
import os
sys.path.append('.')

# Import the MCP server functions
from ga4_mcp_server import list_dimension_categories, list_metric_categories, get_ga4_data

def test_tools():
    print("🧪 Testing GA4 MCP Server Tools...\n")
    
    try:
        # Test 1: List dimension categories
        print("1️⃣ Testing: List dimension categories")
        result = list_dimension_categories()
        print(f"✅ Found {len(result)} dimension categories")
        print(f"Categories: {list(result.keys())}\n")
        
        # Test 2: List metric categories  
        print("2️⃣ Testing: List metric categories")
        result = list_metric_categories()
        print(f"✅ Found {len(result)} metric categories")
        print(f"Categories: {list(result.keys())}\n")
        
        # Test 3: Get some GA4 data
        print("3️⃣ Testing: Get GA4 data (last 7 days)")
        result = get_ga4_data(
            dimensions=["date"],
            metrics=["totalUsers", "newUsers"],
            date_range_start="7daysAgo",
            date_range_end="yesterday"
        )
        print(f" Successfully retrieved GA4 data!")
        print(f"Data points: {len(result) if result else 0}\n")
        
        print("🎉 All tests passed! Your MCP server is working correctly.")
        print("💡 You can now use it with Cursor or Claude.")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_tools() 