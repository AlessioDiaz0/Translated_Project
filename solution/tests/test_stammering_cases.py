"""Quick test for stammering detection cases."""
import requests

BASE_URL = "http://localhost:8000"

test_cases = [
    {"source": "Vorrei comprare un biglietto", "translated": "I would like to buy a ticket", "expected": False, "line": 1},
    {"source": "Amo la musica", "translated": "I love music", "expected": False, "line": 2},
    {"source": "Dove si trova la stazione?", "translated": "Where is the station station station station?", "expected": True, "line": 3},
    {"source": "Sono molto molto molto molto felice", "translated": "I am very happy", "expected": False, "line": 4},
    {"source": "Posso aiutarti?", "translated": "Can I help you??", "expected": False, "line": 5},
    {"source": "Sono affamato", "translated": "I'm hungry", "expected": False, "line": 6},
    {"source": "Sono così stanco", "translated": "I'm sooo tired", "expected": False, "line": 7},
    {"source": "ciao", "translated": "bye bye", "expected": False, "line": 8},
    {"source": "ciao ciao ciao ciao", "translated": "bye bye bye bye", "expected": False, "line": 9},
    {"source": "ciao ciao", "translated": "bye bye bye bye bye bye bye bye bye bye bye", "expected": True, "line": 10},
    {"source": "Questo è veramente l'ultimo test", "translated": "This is really the is really the is really the is really the last test", "expected": True, "line": 11},
    {"source": "Mi piace moooooooolto il cibo italiano", "translated": "I like Italian food soooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo", "expected": True, "line": 12},
]

passed = 0
failed = 0

for test in test_cases:
    response = requests.get(
        f"{BASE_URL}/stammering",
        params={
            "source_sentence": test["source"],
            "translated_sentence": test["translated"]
        }
    )
    
    if response.status_code == 200:
        result = response.json()["has_stammer"]
        status = "✅ PASS" if result == test["expected"] else "❌ FAIL"
        
        if result == test["expected"]:
            passed += 1
        else:
            failed += 1
        
        print(f"Line {test['line']}: {status} - Got {result}, Expected {test['expected']}")
    else:
        print(f"Line {test['line']}: ERROR - Status {response.status_code}")
        failed += 1

print(f"\n{'='*50}")
print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print(f"{'='*50}")
