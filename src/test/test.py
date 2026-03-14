import urllib.request
import json

# Fix 1: Close the quote. 
# Also added the 'Arrivals' or specific endpoint if needed, 
# but sticking to your URL for now.
url = "https://api.tfl.gov.uk/Line/dlr/Timetable/940GZZLUCGT"

try:
    hdr = {
        'Cache-Control': 'no-cache',
    }

    req = urllib.request.Request(url, headers=hdr)
    
    # In Python 3, urlopen defaults to GET, 
    # so the lambda override isn't strictly necessary.
    with urllib.request.urlopen(req) as response:
        status = response.getcode()
        print(f"Status Code: {status}")
        
        # Read and decode the bytes to a string, then load as JSON
        data = json.loads(response.read().decode('utf-8'))
        
        # Pretty print the first bit of the JSON so you can see it's valid
        print(json.dumps(data, indent=2)[:500] + "...")

except Exception as e:
    print(f"An error occurred: {e}")



import urllib.request
import json

# 1. Replace 'YOUR_API_KEY_HERE' with your actual key from the TfL portal
api_key = '009bf6ae289741bcbf53ff8502693b1c'
ids = 'dlr'  # Example line ID; replace with desired line IDs
# base_url = f"https://api.tfl.gov.uk/Line/{ids}/Arrivals"
base_url = "https://api.tfl.gov.uk/Line/dlr/Timetable/940GZZLUCGT/to/940GZZDLstd"

url = f"{base_url}?app_key={api_key}"

try:
    hdr = {
        'Cache-Control': 'no-cache',
        'User-Agent': 'Mozilla/5.0' 

    }

    req = urllib.request.Request(url, headers=hdr)
    
    with urllib.request.urlopen(req) as response:
        print(f"Status: {response.getcode()}")
        data = json.loads(response.read().decode('utf-8'))
        
        # This will print the name of the station to confirm it worked
        print(f"Connected to: {data['stations'][0]['name']}")

except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.reason}")
    if e.code == 403:
        print("Hint: Check if your API key is active or if the endpoint requires registration.")
except Exception as e:
    print(f"Other Error: {e}")



# Switch to the Arrivals endpoint for the same station (Canning Town DLR)
ids = 'dlr'  # Example line ID; replace with desired line IDs
stopPointId = '940GZZLUCGT'  # Canning Town DLR stop point ID
destinationPointId = '940GZZLUBNK'  # Bank
direction = 'all'

url = f"https://api.tfl.gov.uk/StopPoint/940GZZLUCGT/Arrivals?app_key={api_key}"
# # url = f"https://api.tfl.gov.uk/Line/{ids}/Disruption?app_key={api_key}"
# url = f"https://api.tfl.gov.uk/Line/{ids}/Arrivals/{stopPointId}?direction={direction}&destinationStationId={destinationPointId}&app_key={api_key}"

try:
    # Adding a User-Agent is a "best practice" to avoid 403s from firewalls
    hdr = {
        'Cache-Control': 'no-cache',
        'User-Agent': 'Mozilla/5.0' 
    }
    req = urllib.request.Request(url, headers=hdr)
    
    with urllib.request.urlopen(req) as response:
        print(f"Status: {response.getcode()} - Success!")
        data = json.loads(response.read().decode('utf-8'))
        
    print(data)
        # Arrivals returns a list of trains
        # for arrival in data[:5]: # Show first 5
        #     dest = arrival.get('destinationName')
        #     mins = arrival.get('timeToStation') // 60
            # print(f"Train to {dest} arriving in {mins} mins")

except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.reason}")
except Exception as e:
    print(f"Error: {e}")