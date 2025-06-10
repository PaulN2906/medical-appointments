"""
Test async pentru race condition
"""
import asyncio
import aiohttp
import json
import sys

BASE_URL = "http://127.0.0.1:8000/api"
CONCURRENT_REQUESTS = 20

# Hardcoded pentru simplitate - obtinute din setup_test_data.py
DOCTOR_ID = 4  # actualizat dupa rulare setup
SCHEDULE_ID = 54  # actualizat dupa rulare setup

class AsyncTester:
    async def login_user(self, session, username, password):
        """Login si obtinere token"""
        login_data = {
            'username': username,
            'password': password
        }
        
        try:
            async with session.post(f"{BASE_URL}/auth/users/login/", json=login_data) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('token'), data.get('patient_id')
                else:
                    text = await resp.text()
                    print(f"❌ Login failed for {username}: {resp.status} - {text}")
                    return None, None
        except Exception as e:
            print(f"❌ Login error for {username}: {e}")
            return None, None
    
    async def make_appointment(self, session, token, patient_id, request_id):
        """Incercare programare"""
        headers = {'Authorization': f'Token {token}'}
        appointment_data = {
            'doctor': DOCTOR_ID,
            'patient': patient_id,
            'schedule': SCHEDULE_ID,
            'notes': f'Race condition test appointment #{request_id}'
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/appointments/appointments/", 
                json=appointment_data, 
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                response_text = await resp.text()
                
                return {
                    'success': resp.status == 201,
                    'status': resp.status,
                    'response': response_text,
                    'patient_id': patient_id,
                    'request_id': request_id
                }
        except Exception as e:
            return {
                'success': False,
                'status': 'error',
                'response': str(e),
                'patient_id': patient_id,
                'request_id': request_id
            }
    
    async def run_test(self):
        """Rulare test de concurenta"""
        print(f"🚀 Starting race condition test with {CONCURRENT_REQUESTS} concurrent requests...")
        print(f"   Doctor ID: {DOCTOR_ID}")
        print(f"   Schedule ID: {SCHEDULE_ID}")
        
        async with aiohttp.ClientSession() as session:
            # 1. Login pentru toti pacientii
            print("🔐 Logging in patients...")
            login_tasks = []
            for i in range(CONCURRENT_REQUESTS):
                task = self.login_user(session, f'test_patient_{i}', 'TestPassword123!')
                login_tasks.append(task)
            
            login_results = await asyncio.gather(*login_tasks)
            
            # Filtreaza rezultatele valide
            valid_logins = [(token, patient_id, i) for i, (token, patient_id) in enumerate(login_results) if token and patient_id]
            
            print(f"✅ {len(valid_logins)} patients logged in successfully")
            
            if len(valid_logins) < CONCURRENT_REQUESTS:
                print(f"⚠️ Only {len(valid_logins)}/{CONCURRENT_REQUESTS} patients logged in successfully")
            
            if len(valid_logins) == 0:
                print("❌ No patients could log in. Check your setup!")
                return [], 0
            
            # 2. Fa appointment-uri simultane
            print(f"⏱️ Making {len(valid_logins)} concurrent appointment requests...")
            start_time = asyncio.get_event_loop().time()
            
            appointment_tasks = []
            for token, patient_id, request_id in valid_logins:
                task = self.make_appointment(session, token, patient_id, request_id)
                appointment_tasks.append(task)
            
            results = await asyncio.gather(*appointment_tasks)
            
            end_time = asyncio.get_event_loop().time()
            duration = end_time - start_time
            
            return results, duration
    
    def analyze_results(self, results, duration):
        """Analiza rezultate test"""
        print(f"\n📊 Test Results:")
        print(f"   Duration: {duration:.2f} seconds")
        print(f"   Total requests: {len(results)}")
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        print(f"   Successful: {len(successful)}")
        print(f"   Failed: {len(failed)}")
        
        # Afiseaza primele cateva rezultate successful
        if successful:
            print(f"\n✅ Successful appointments:")
            for result in successful[:3]:  # Primele 3
                print(f"   Request #{result['request_id']}: Patient {result['patient_id']}")
            if len(successful) > 3:
                print(f"   ... and {len(successful) - 3} more")
        
        # Analizeaza motivele esecului
        if failed:
            print(f"\n❌ Failed appointments:")
            error_reasons = {}
            for result in failed:
                try:
                    if isinstance(result['response'], str) and result['response'].startswith('{'):
                        response_data = json.loads(result['response'])
                        error = response_data.get('error', 'Unknown error')
                    else:
                        error = str(result['response'])[:100]  # Primele 100 caractere
                except:
                    error = str(result['response'])[:100]
                
                error_reasons[error] = error_reasons.get(error, 0) + 1
            
            for error, count in error_reasons.items():
                print(f"   {error}: {count} times")
        
        # Verdict
        print(f"\n🎯 VERDICT:")
        if len(successful) == 1:
            print(f"   ✅ SUCCESS: Race condition is properly handled!")
            print(f"   ✅ Only 1 appointment was created as expected")
            print(f"   ✅ {len(failed)} requests were correctly rejected")
        elif len(successful) > 1:
            print(f"   ❌ FAILURE: Race condition detected!")
            print(f"   ❌ {len(successful)} appointments were created for the same time slot")
            print(f"   ❌ This should be only 1!")
        else:
            print(f"   ⚠️ UNEXPECTED: No appointments were created")
            print(f"   ⚠️ This might indicate a different issue")
        
        return len(successful) == 1

async def main():
    if len(sys.argv) > 1:
        global DOCTOR_ID, SCHEDULE_ID
        try:
            DOCTOR_ID = int(sys.argv[1])
            SCHEDULE_ID = int(sys.argv[2])
        except:
            print("Usage: python test_race_async.py [doctor_id] [schedule_id]")
            return False
    
    tester = AsyncTester()
    
    try:
        results, duration = await tester.run_test()
        success = tester.analyze_results(results, duration)
        return success
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Async Race Condition Test for Appointment Booking")
    print("=" * 55)
    
    success = asyncio.run(main())
    
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test revealed issues that need to be fixed!")
