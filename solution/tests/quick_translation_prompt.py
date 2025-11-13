import requests


# ============================================================================
# CUSTOMIZE YOUR REQUEST HERE
# ============================================================================
request_data = {
    "source_language": "it",
    "target_language": "en", 
    "query_sentence": "Come si dice questo in inglese?"
}
# ============================================================================


BASE_URL = "http://localhost:8000"


def send_translation_request(data):
    """Send a translation request and display the prompt."""
    print("\n" + "=" * 70)
    print("  Translation Request")
    print("=" * 70)
    print(f"\n  Source Language:  {data['source_language']}")
    print(f"  Target Language:  {data['target_language']}")
    print(f"  Query Sentence:   {data['query_sentence']}")
    print("\n" + "-" * 70)
    
    try:
        response = requests.get(
            f"{BASE_URL}/prompt",
            params=data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            prompt = result.get("prompt", "")
            
            print("\n✅ SUCCESS - Generated Prompt:\n")
            print(prompt)
            print("\n" + "=" * 70 + "\n")
            
        else:
            print(f"\n❌ ERROR - Status {response.status_code}")
            print(f"Response: {response.text}\n")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR - Cannot connect to server")
        print("Make sure the server is running:")
        print("  cd solution/")
        print("  docker-compose up\n")
        
    except Exception as e:
        print(f"\n❌ ERROR - {str(e)}\n")


if __name__ == "__main__":
    send_translation_request(request_data)
