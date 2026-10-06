"""Builds data/leads_labeled.csv.

All leads are SYNTHETIC (written by hand for this project, fake names, example.com emails).
Labels follow the rubric in the README and come from a single annotator, so the hot/warm
boundary is subjective. Edit this file to add your own cases, then re-run it.
"""
import csv
import pathlib

HOT = [
    "Hi, I want to buy a 3BHK in Whitefield, budget up to 1.4 Cr, loan pre-approved by HDFC. Can I visit this Saturday?",
    "Please call me today. I liked the Sarjapur 2BHK listing and want to book it before the price revision. Token amount ready.",
    "We are relocating to Bengaluru next month for work and need a 2BHK to rent near Manyata. Budget 40k. Can we see two options this weekend?",
    "Interested in plot no. 214 in your Devanahalli layout. Ready to pay 20% down payment this week, please share the agreement draft.",
    "Selling my current flat and have a buyer. Need a 3BHK in HSR within 45 days, 1.8 Cr max. Please arrange visits.",
    "Saw your ad for the Hebbal 2BHK. Can I come tomorrow at 11 am? I have the documents and a cheque ready.",
    "Looking to invest 90 lakh in a ready-to-move apartment in Electronic City, need possession in 3 weeks. Who can meet me?",
    "Hello, my bank sanctioned the home loan yesterday (75L). Which of your Yelahanka 2BHKs are available for immediate registration?",
    "I'm free all weekend to see the Koramangala 3BHK. We've finalised the budget (2.2 Cr) and want to close this month.",
    "Please send the payment details for the Kanakapura Road villa. My family has decided and we want to book now.",
    "Need a 1BHK for rent in Indiranagar from 1st of next month, budget 25k, can pay 2 months deposit. Call me after 6 pm.",
    "My lease ends in 3 weeks, need a 2BHK near Bellandur ORR, up to 45k. Can someone show me flats tomorrow?",
    "We are a couple buying our first home. Budget 85L, loan eligibility letter in hand. Want to visit the Thanisandra project on Sunday.",
    "Hi, referred by Mr. Rao who bought from you. I want the same tower, 10th floor or above, 2BHK. Ready to book this week.",
    "Want to buy a commercial office space of 1200 sqft in Whitefield for my startup, budget 1.1 Cr, need to finalise in 30 days. Please call.",
]
WARM = [
    "What is the price range for 2BHKs in your Hennur project? Is it RERA registered?",
    "We are thinking of buying a flat sometime this year in North Bengaluru. Can you send brochures for your ongoing projects?",
    "Interested in the Sarjapur villa. What are the payment plans and when is the possession date?",
    "Looking at 3BHKs around 1.5 Cr. Still comparing a few builders. Can you share floor plans and amenities?",
    "Does your Whitefield project allow pets and what is the maintenance charge per sqft?",
    "Could you share the location and carpet area of the 2BHK listed on your website? Will decide after checking.",
    "My husband and I might buy in 4-5 months. What are your upcoming launches?",
    "Is there a tie-up with any bank for home loans? Considering a purchase in Yelahanka.",
    "How far is the Devanahalli plot from the airport and what is the per sqft rate?",
    "Please send details about 1BHK rental options near Marathahalli. Not in a hurry, moving in a couple of months.",
    "I saw your Instagram post about the Hebbal apartments. How many units are left in the 2BHK category?",
    "Looking for investment options under 60L. Do you have anything with good rental yield?",
    "Can you explain the difference between your Gold and Platinum 3BHK variants? We want to shortlist before visiting.",
    "My parents want a ground-floor flat. Do any of your projects have one? Budget flexible, nothing finalised.",
    "Interested in resale properties in HSR Layout. Do you handle those and what is your commission?",
]
COLD = [
    "Just browsing, nothing planned. Might look at houses after a couple of years.",
    "Hi, are you hiring? I'm a fresher looking for a sales executive role in real estate.",
    "We offer SEO and digital marketing services for real-estate firms. Can we schedule a demo?",
    "I already bought a flat last year. Looking for an interior designer, do you have recommendations?",
    "test test please ignore",
    "Is this the number for the electricity board? I need to report a power cut.",
    "I'm doing a college project on housing trends in Bengaluru. Can you share your sales data?",
    "Congratulations! You've won a free cruise. Click the link to claim your prize now.",
    "Not looking to buy. Just wanted to know what your office timings are.",
    "Selling lead lists of verified home buyers, 10k contacts for 5000 rupees. Interested?",
    "Can you fix my leaking bathroom tap? Please send a plumber.",
    "My friend might buy something in 2-3 years, I'm just collecting information for him, no rush at all.",
    "Please remove my number from your mailing list. Not interested.",
    "Looking for a PG for a single student in Jaipur. Do you have anything there?",
    "What's the weather like in Bengaluru today?",
]

rows = []
n = 0
for label, msgs in (("hot", HOT), ("warm", WARM), ("cold", COLD)):
    for m in msgs:
        n += 1
        rows.append({
            "lead_id": f"T{n:03d}",
            "name": f"Test Lead {n}",
            "email": f"lead{n}@example.com",
            "source": "website",
            "message": m,
            "true_intent": label,
        })

# Interleave classes so a partial run is not biased toward one label.
rows.sort(key=lambda r: (int(r["lead_id"][1:]) % 15, r["true_intent"]))

out = pathlib.Path(__file__).with_name("leads_labeled.csv")
with out.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"wrote {len(rows)} leads -> {out}")
