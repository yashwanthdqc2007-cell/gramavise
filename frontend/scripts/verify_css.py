import urllib.request
import re
import sys

routes = ["/", "/onboarding", "/schemes", "/history"]

try:
    for route in routes:
        url = f"http://localhost:3000{route}"
        print(f"\n--- Verifying route {route} ({url}) ---")
        res = urllib.request.urlopen(url)
        print(f"Page Status: {res.status}")
        html = res.read().decode("utf-8")
        
        css_matches = re.findall(r'href=["\'](/_next/static/css/[^"\']+)["\']', html)
        print(f"Found {len(css_matches)} CSS links in HTML: {css_matches}")
        assert len(css_matches) > 0, f"No CSS link found on {route}"
        
        for css_url in css_matches:
            full_url = "http://localhost:3000" + css_url
            css_res = urllib.request.urlopen(full_url)
            content_type = css_res.headers.get("Content-Type")
            body = css_res.read().decode("utf-8")
            print(f"  CSS URL: {css_url}")
            print(f"  HTTP Status: {css_res.status}")
            print(f"  Content-Type: {content_type}")
            print(f"  CSS Size: {len(body)} bytes")
            
            assert css_res.status == 200, f"CSS must return 200 OK on {route}"
            assert "text/css" in content_type, f"Content-Type must be text/css on {route}"
            assert len(body) > 1000, f"CSS body must contain compiled rules on {route}"
            print("  [PASS] Verified 200 OK, text/css, and active stylesheet.")

    print("\n>>> ALL ROUTES VERIFIED WITH WORKING CSS! <<<")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
