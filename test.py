# Import Required
import json
from typing import List
# Load FAQs
faqFile = open("faq.json")
FAQs = json.load(faqFile)
# Check results


def autocomplete_faqs(searchTerm: str) -> List[str]:
    searchTermElements = searchTerm.split()
    results = []
    for s in searchTermElements:
        for q in FAQs:
            if s.lower() in q.lower():
                if q not in results:
                    results.append(q)
    return results[:10]


# Term to search for
searchTerm = "mean"
# Search
searchResults = autocomplete_faqs(searchTerm)
# Print Results
print("Search Term: {}".format(searchTerm))
print("Results: {}".format(searchResults))
