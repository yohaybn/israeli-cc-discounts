import json
import os
import urllib.request
import urllib.parse

def get_region(lat, lon):
    """Classify coordinates into regional buckets across Israel based on latitude."""
    if lat < 30.0:
        return "eilat_arava"
    elif lat < 31.3:
        return "south"
    elif lat < 32.5:
        return "center"
    else:
        return "north"

def fetch_and_split_israel_businesses():
    # Output directory (docs/data for GitHub Pages site root)
    output_dir = os.path.join("docs", "data", "businesses")
    os.makedirs(output_dir, exist_ok=True)

    overpass_query = """
    [out:json][timeout:240];
    area["ISO3166-1"="IL"][admin_level=2]->.searchArea;
    (
      node["shop"](area.searchArea);
      way["shop"](area.searchArea);
      
      node["amenity"~"restaurant|cafe|fast_food|pub|bar|food_court|ice_cream|pharmacy|bank|atm|fuel"](area.searchArea);
      way["amenity"~"restaurant|cafe|fast_food|pub|bar|food_court|ice_cream|pharmacy|bank|atm|fuel"](area.searchArea);
      
      node["craft"](area.searchArea);
      way["craft"](area.searchArea);
    );
    out center;
    """
    
    url = "https://overpass-api.de/api/interpreter"
    data = urllib.parse.urlencode({'data': overpass_query}).encode('utf-8')
    
    req = urllib.request.Request(
        url, 
        data=data, 
        headers={'User-Agent': 'IsraelBusinessFetcher/2.0 (GitHubActions)'}
    )
    
    print("Fetching data from Overpass API...")
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error downloading data: {e}")
        return

    elements = result.get('elements', [])
    print(f"Retrieved {len(elements)} raw elements.")

    regions_data = {
        "north": [],
        "center": [],
        "south": [],
        "eilat_arava": []
    }

    processed_count = 0

    for item in elements:
        lat = item.get('lat') or item.get('center', {}).get('lat')
        lon = item.get('lon') or item.get('center', {}).get('lon')
        
        tags = item.get('tags', {})
        name = tags.get('name') or tags.get('name:he') or tags.get('name:en')
        category = tags.get('shop') or tags.get('amenity') or tags.get('craft')
        
        if lat and lon and name and category:
            business = {
                "id": item['id'],
                "name": name,
                "type": category,
                "lat": round(lat, 6),
                "lon": round(lon, 6)
            }
            
            region = get_region(lat, lon)
            regions_data[region].append(business)
            processed_count += 1

    print(f"Processed {processed_count} businesses in total.")

    # Save to docs/data/businesses/
    for region_name, businesses in regions_data.items():
        filepath = os.path.join(output_dir, f"businesses_{region_name}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(businesses, f, ensure_ascii=False, separators=(',', ':'))
        print(f"Saved {filepath} with {len(businesses)} businesses.")

if __name__ == "__main__":
    fetch_and_split_israel_businesses()