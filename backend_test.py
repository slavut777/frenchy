import requests
import sys
import time
from datetime import datetime

class FrenchVocabularyAPITester:
    def __init__(self, base_url="https://f251dfc8-0ec4-4a3b-bdd3-bc7912b97d0c.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                return success, response.json() if response.text else {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test(
            "Root API Endpoint",
            "GET",
            "api/",
            200
        )

    def test_get_all_words(self):
        """Test getting all words"""
        return self.run_test(
            "Get All Words",
            "GET",
            "api/words",
            200
        )

    def test_get_flashcards(self):
        """Test getting flashcards"""
        return self.run_test(
            "Get Flashcards",
            "GET",
            "api/flashcards",
            200
        )

    def test_update_word_progress(self, word_id, known=True):
        """Test updating word progress"""
        return self.run_test(
            f"Update Word Progress (known={known})",
            "POST",
            f"api/flashcards/{word_id}/update",
            200,
            params={"known": known}
        )

    def test_get_stats(self):
        """Test getting user stats"""
        return self.run_test(
            "Get User Stats",
            "GET",
            "api/stats",
            200
        )

def main():
    # Setup
    tester = FrenchVocabularyAPITester()
    
    # Test root endpoint
    tester.test_root_endpoint()
    
    # Test getting all words
    success, words_response = tester.test_get_all_words()
    if not success:
        print("❌ Failed to get words, stopping tests")
        return 1
    
    # Test getting flashcards
    success, flashcards_response = tester.test_get_flashcards()
    if not success:
        print("❌ Failed to get flashcards, stopping tests")
        return 1
    
    # Test updating word progress if we have flashcards
    if success and flashcards_response and len(flashcards_response) > 0:
        word_id = flashcards_response[0]["id"]
        
        # Test marking a word as known
        success, _ = tester.test_update_word_progress(word_id, True)
        if not success:
            print("❌ Failed to update word progress (known=True)")
        
        # Test marking a word as not known
        success, _ = tester.test_update_word_progress(word_id, False)
        if not success:
            print("❌ Failed to update word progress (known=False)")
    
    # Test getting stats
    success, stats_response = tester.test_get_stats()
    if not success:
        print("❌ Failed to get stats")
    else:
        print(f"\n📊 Stats: {stats_response}")
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())