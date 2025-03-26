import json
import pandas as pd

# Open and load the JSON report 
with open('C:\\Users\\Ait\\Desktop\\ZAP-Report.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Prepare a list to store each alert's data as a row
rows = []

# Iterate over each site in the JSON report
for site in data.get('site', []):
    site_name = site.get('@name')
    # Iterate over each alert within the site
    for alert in site.get('alerts', []):
        row = {
            'site': site_name,                      # Affected URL or site name
            'alert': alert.get('alert'),            # Vulnerability type
            'riskcode': alert.get('riskcode'),      # Severity proxy (riskcode)
            'confidence': alert.get('confidence'),
            'riskdesc': alert.get('riskdesc'),
            'count': alert.get('count'),
            'vulnerability_detected': 1             # Mark as vulnerability (1)
        }
        rows.append(row)

# Create a DataFrame from the rows
df = pd.DataFrame(rows)

# Rename columns: 'alert' to 'vulnerability_type' and 'site' to 'url'
df.rename(columns={'alert': 'vulnerability_type', 'site': 'url'}, inplace=True)

# Save the updated DataFrame to CSV
df.to_csv('C:\\Users\\Ait\\Desktop\\ZAP-Report.csv', index=False)

print("CSV file created with renamed columns: ZAP-Report.csv")
