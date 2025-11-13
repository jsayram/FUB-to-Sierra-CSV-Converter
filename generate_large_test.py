#!/usr/bin/env python3
"""Generate a large FUB CSV file with 5,100 rows for testing."""

import csv
import random
from pathlib import Path

# Template data
first_names = ["John", "Maria", "Robert", "Jennifer", "Michael", "Emily", "David", "Lisa", "James", "Patricia",
               "Christopher", "Linda", "Mark", "Barbara", "Daniel", "Nancy", "Kevin", "Karen", "Steven", "Betty",
               "Edward", "Dorothy", "Ronald", "Sarah", "Joseph", "Margaret", "Thomas", "Jessica", "Charles", "Michelle",
               "Matthew", "Ashley", "Amanda", "Joshua", "Melissa", "Donna", "Brian", "Kimberly", "Jeffrey", "Ryan",
               "Deborah", "Jason", "Stephanie", "Justin", "Nicole", "Angela", "Brandon", "Katherine", "Gary", "Rachel",
               "Emma", "Aaron", "Tyler", "Brittany", "Zachary", "Samantha", "Alexander", "Danielle", "Kyle", "Megan",
               "Adam", "Lauren", "Jacob", "Amber", "Jonathan", "Crystal", "Craig", "Heather", "Travis", "Monica",
               "Jeremy", "Diana", "Austin", "Courtney", "Sean", "Jordan", "Vanessa", "Eric", "Cynthia",
               "Gregory", "Shannon", "Dennis", "Randy", "Janet", "Frank", "Carolyn", "Scott", "Rebecca",
               "Andrew", "Laura", "Albert", "Sharon", "Willie", "Terry", "Kathleen", "Lawrence", "Amy"]

last_names = ["Smith", "Garcia", "Johnson", "Lee", "Williams", "Brown", "Jones", "Martinez", "Anderson", "Taylor",
              "Thomas", "Moore", "Jackson", "White", "Harris", "Martin", "Thompson", "Robinson", "Clark", "Rodriguez",
              "Lewis", "Walker", "Hall", "Allen", "Young", "Hernandez", "King", "Wright", "Lopez", "Hill",
              "Scott", "Green", "Adams", "Baker", "Gonzalez", "Nelson", "Carter", "Mitchell", "Perez", "Roberts",
              "Turner", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins", "Stewart", "Sanchez", "Morris",
              "Rogers", "Reed", "Cook", "Morgan", "Bell", "Murphy", "Bailey", "Rivera", "Cooper", "Richardson",
              "Cox", "Howard", "Ward", "Torres", "Peterson", "Gray", "Ramirez", "James", "Watson", "Brooks",
              "Kelly", "Sanders", "Price", "Bennett", "Wood", "Barnes", "Ross", "Henderson", "Coleman", "Jenkins",
              "Perry", "Powell", "Long", "Patterson", "Hughes", "Flores", "Washington", "Butler", "Simmons", "Foster"]

cities = ["Austin", "San Antonio", "Dallas", "Houston", "Fort Worth", "Arlington", "Plano", "Irving", "Frisco",
          "McKinney", "Richardson", "Garland", "Grand Prairie", "Mesquite", "Carrollton", "Lewisville", "Allen",
          "Flower Mound", "Denton", "Wylie", "Rockwall", "Rowlett", "The Colony", "Little Elm", "Prosper", "Celina"]

sources = ["Zillow", "Realtor.com", "Facebook", "Google", "Trulia", "Website", "Referral", "Open House", "Cold Call"]

agents = ["Sarah Johnson", "Mike Chen", "Jane Doe", "Tom Wilson", "Amy Rodriguez"]

tags_pool = ["Hot Lead", "First Time Buyer", "Investor", "Relocating", "Cash Buyer", "Pre-Approved", "Luxury",
             "VA Loan", "FHA", "Seller", "Buyer", "Warm Lead", "Corporate", "Military", "Upgrade", "Downsizing"]

phone_formats = [
    lambda n: f"{n[0:3]}-{n[3:6]}-{n[6:10]}",
    lambda n: f"({n[0:3]}) {n[3:6]}-{n[6:10]}",
    lambda n: f"{n[0:3]}.{n[3:6]}.{n[6:10]}",
    lambda n: f"+1 ({n[0:3]}) {n[3:6]}-{n[6:10]}",
    lambda n: f"1-{n[0:3]}-{n[3:6]}-{n[6:10]}",
    lambda n: n,
]

def random_phone():
    """Generate a random 10-digit phone number in various formats."""
    digits = f"{random.randint(200, 999)}{random.randint(200, 999)}{random.randint(1000, 9999)}"
    if random.random() < 0.1:  # 10% chance of empty
        return ""
    return random.choice(phone_formats)(digits)

def random_tags():
    """Generate random tags."""
    if random.random() < 0.05:  # 5% chance of empty
        return ""
    num_tags = random.randint(1, 4)
    tags = random.sample(tags_pool, num_tags)
    delimiter = random.choice(["; ", ", ", " | "])
    return delimiter.join(tags)

def random_email(first, last, suffix=""):
    """Generate email from name."""
    if not first or not last or random.random() < 0.02:  # 2% chance of empty
        return ""
    domains = ["gmail.com", "yahoo.com", "email.com", "outlook.com", "mail.com", "hotmail.com"]
    formats = [
        f"{first.lower()}.{last.lower()}{suffix}@{random.choice(domains)}",
        f"{first.lower()}{last.lower()}{suffix}@{random.choice(domains)}",
        f"{first[0].lower()}.{last.lower()}{suffix}@{random.choice(domains)}",
        f"{first.lower()}{random.randint(1, 99)}@{random.choice(domains)}",
    ]
    return random.choice(formats)

def generate_row(index):
    """Generate a single row of FUB data."""
    first = random.choice(first_names)
    last = random.choice(last_names)
    city = random.choice(cities)
    
    # Occasionally skip first or last name
    if random.random() < 0.02:
        first = ""
    if random.random() < 0.01:
        last = ""
    
    row = {
        "First Name": first,
        "Last Name": last,
        "Email": random_email(first, last) if first and last else "",
        "Secondary Email": random_email(first, last, "2") if random.random() > 0.7 else "",
        "Phone": random_phone(),
        "Secondary Phone": random_phone() if random.random() > 0.6 else "",
        "Source": random.choice(sources),
        "Assigned To": random.choice(agents),
        "Street": f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Maple', 'Pine', 'Elm', 'Cedar'])} {random.choice(['St', 'Ave', 'Rd', 'Dr', 'Ln', 'Blvd'])}",
        "City": city,
        "State": "TX",
        "Zip": f"{random.randint(75000, 78999)}",
        "Tags": random_tags(),
        "Notes": f"Contact #{index}. Interested in {city} area. " + random.choice([
            "Budget flexible.",
            "Ready to move quickly.",
            "Just looking currently.",
            "Very motivated buyer.",
            "Needs to sell first.",
            "Pre-approved and ready.",
        ]) if random.random() > 0.3 else "",
        "Search Criteria": f"{random.randint(2, 5)} bed {random.randint(1, 4)} bath in {city}" if random.random() > 0.2 else "",
    }
    return row

# Generate the CSV
output_path = Path(__file__).parent / "csv_input" / "fub_export_large.csv"
output_path.parent.mkdir(exist_ok=True)

headers = ["First Name", "Last Name", "Email", "Secondary Email", "Phone", "Secondary Phone",
           "Source", "Assigned To", "Street", "City", "State", "Zip", "Tags", "Notes", "Search Criteria"]

print("Generating 5,100 rows of test data...")

with open(output_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    
    for i in range(1, 5101):
        writer.writerow(generate_row(i))
        if i % 500 == 0:
            print(f"  Generated {i} rows...")

print(f"\n✓ Created {output_path}")
print(f"  Total rows: 5,100")
print("\nNow run: python src/fub_to_sierra.py")
