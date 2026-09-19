import urllib.request
import urllib.parse
import json
import http.cookiejar

# Absolute gateway endpoint targeting your core service routing layout
BASE_API_URL = "http://localhost:1979/semanticturkey/it.uniroma2.art.semanticturkey/st-core-services/"

def create_authenticated_project(project_name, base_uri, admin_email="admin@venic.org", admin_pass="admin"):
    # 1. Initialize an automatic Cookie Jar handler to manage our session lifetime
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    urllib.request.install_opener(opener)

    # --- STEP 1: AUTHENTICATE / LOGIN PASS ---
    login_endpoint = BASE_API_URL + "Auth/login"
    login_payload = {
        "email": admin_email,
        "password": admin_pass
    }
    login_data = urllib.parse.urlencode(login_payload).encode('utf-8')
    
    # Identify your tracking profile to the server via standard user agent keys
    headers = {'User-Agent': 'MyaamiaOntolexPipeline/1.6'}
    login_req = urllib.request.Request(login_endpoint, data=login_data, headers=headers, method="POST")

    print(f"🔑 Authenticating user credentials with Semantic Turkey container...")
    try:
        with urllib.request.urlopen(login_req, timeout=10) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            if res_data.get("stype") == "exception":
                print(f"❌ Server rejected credentials: {res_data.get('msg')}")
                return
            print("   🔒 Session token generated and stored in local cookie jar.")
    except Exception as auth_err:
        print(f"❌ Handshake processing failed during authentication phase: {auth_err}")
        return

    # --- STEP 2: CREATE ONTOLEX ENVIRONMENT PASS ---
    create_endpoint = BASE_API_URL + "Projects/createProject"
    create_payload = {
        "consumer": "SYSTEM",
        "projectName": project_name,
        "baseURI": base_uri,
        "model": "http://uniroma2.it",
        "lexicalizationModel": "http://uniroma2.it-Lemon",
        "historyEnabled": "true",
        "validationEnabled": "false",
        "uriGeneratorFactoryID": "http://uniroma2.it"
    }
    
    create_data = urllib.parse.urlencode(create_payload).encode('utf-8')
    create_req = urllib.request.Request(create_endpoint, data=create_data, headers=headers, method="POST")

    print(f"🚀 Transmitting OntoLex configuration payload to creation endpoint...")
    try:
        with urllib.request.urlopen(create_req, timeout=15) as create_response:
            result = create_response.read().decode('utf-8')
            print("🎯 Server Response Data Struct:")
            print(json.dumps(json.loads(result), indent=2))
            print(f"\n✅ Project '{project_name}' configured natively inside your backend repository!")
    except Exception as e:
        print(f"❌ Failed to instantiate data project workspace shell block: {e}")

if __name__ == "__main__":
    # If you modified your default administrator setup, change the credentials here
    create_authenticated_project(
        project_name="MyaamiaLexicon", 
        base_uri="http://example.org",
        admin_email="admin@venic.org", 
        admin_pass="admin"
    )
