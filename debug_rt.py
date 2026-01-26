import requests
from bs4 import BeautifulSoup

url = "https://www.rottentomatoes.com/critic/aa-dowd/movies"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

print("=== DEBUG RT PROFILE ===")
rows = soup.select('tr')
print(f"Total rows found: {len(rows)}")

for i, row in enumerate(rows[:20]):
    print(f"\nRow {i}:")
    # Print data-qa attributes
    attrs = row.attrs
    if 'data-qa' in attrs:
        print(f"  data-qa: {attrs['data-qa']}")
    print(f"  Snippet: {str(row)[:200]}...")

# Also check for links inside rows
links = soup.select('tr a[href*="/m/"]')
print(f"\nMovie links in rows: {len(links)}")
if links:
    print(f"  First movie link: {links[0].text.strip()} ({links[0]['href']})")
    parent_tr = links[0].find_parent('tr')
    if parent_tr:
        print(f"  Parent TR attrs: {parent_tr.attrs}")
