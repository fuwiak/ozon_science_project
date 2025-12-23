#!/usr/bin/env python3
"""
Skrypt do testowania zdalnego API po wdrożeniu na Railway
"""
import requests
import json
import os
import sys
from typing import Dict, Any, Optional

API_URL = os.getenv("RAILWAY_URL", "https://your-app-name.railway.app")

def test_endpoint(name: str, url: str, method: str = "GET", data: Optional[Dict] = None, timeout: int = 10):
    """Testuje endpoint i wyświetla wynik"""
    print(f"\n{'='*60}")
    print(f"🧪 {name}")
    print(f"📍 {method} {url}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=timeout)
        elif method == "DELETE":
            response = requests.delete(url, timeout=timeout)
        else:
            print(f"❌ Nieobsługiwana metoda: {method}")
            return False
        
        response.raise_for_status()
esult = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"\n✅ Status: {response.status_code} | Czas: {response.elapsed.total_seconds():.2f}s")
        return True
    exceprequests.exceptions.Timeout:
        print(f"❌ Timeout po {timeout}s")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Błąd: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Status: {e.respo            print(f"   S try:
                print(f"   Response: {e.response.text[:200]}")
            except:
                pass
        return False

def main():
    global API_URL
    
    if len(sys.argv) > 1:
        API_URL = sys.argv[1]
    
    if API_URL == "https://your-app-name.railway.app":
        print("⚠️  UWAGA: Ustaw URL swojego backendu!")
        print("   Przykład: python test_remote.py https://your-app.railway.app")
        print("   Lub: export RAILWAY_URL=https://your-app.railway.app")
        print()
        API_URL = input("Wprowadź URL du (lub naciśnij Enter aby kontynuować z domyślnym): ").strip()
        if not API_URL:
            API_URL = "https://your-app-name.railway.app"
    
    print("🚀 Testowanie zdalnego API")
    print(f"🌐 URL: {API_URL}\n")
    
    results = []
    
    # Podstawowe testy
    results.append(("Health Chect_endpoint("Health Check", f"{API_URL}/health")))
    results.append(("Status", test_endpoint("Status", f"{API_URL}/api/status")))
    
    # Produkty
    results.append(("Lista produktów", test_endpoint("Lista produktów", f"{API_URL}/api/products?page=1&page_size=5")))
    results.append(("Kategorie"test_endpoint("Kategorie", f"{API_URL}/api/products/categories/list")))
    results.append(("Marki", test_endpoint("Marki", f"{API_URL}/api/products/brands/list")))
    
    # Analityka
    results.append(("Top produkty", test_endpoint("Top produkty", f"{API_URL}/api/analytics/demand/top?limit=5")))
    results.append(("Metryki cenowe", test_endpoint("Metryki cenowe", f"{API_URL}/api/analytics/pricing-metrics?min_days_out_of_stock=15")))
    results.append(("Produkty bez stanu", test_endpoint("Produkty bez stanu", f"{API_URL}/api/analytics/stock/out-of-stock?min_days=15")))
    
    # Cache
    results.append(("Statystyka cache", test_endpoint("Statystyka cache", f"{API_URL}/api/cache/stats")))
    
    # Podsumowanie
    print("\n" + "="*60)
    print("📊 Podsumowanie testów")
    print("="*60)
    
    passed = sum(1 for _, result in ults if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\n✅ Przeszło: {passed}/{total}")
    print("="*60)

if __name__ == "__main__":
    main()
