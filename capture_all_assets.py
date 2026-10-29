"""
Comprehensive screenshot capture script for Intelligent Hostel Complaint Management System.
Uses Selenium with headless Chrome to capture all screens, states, modals, and functions
into the assets/ directory.
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

def create_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1680,1050')
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1680, 1050)
    return driver

def capture_all():
    print("📸 Starting comprehensive screenshot capture into assets/ ...")
    driver = create_driver()

    try:
        # ─────────────────────────────────────────────────────────────────────
        # 1. Login Page
        # ─────────────────────────────────────────────────────────────────────
        print("1. Capturing Login Page...")
        driver.get("http://localhost:5173/login")
        time.sleep(1.5)
        driver.save_screenshot(os.path.join(ASSETS_DIR, "01_login_page.png"))

        # ─────────────────────────────────────────────────────────────────────
        # 2. Registration Page
        # ─────────────────────────────────────────────────────────────────────
        print("2. Capturing Registration Page...")
        driver.get("http://localhost:5173/signup")
        time.sleep(1.5)
        driver.save_screenshot(os.path.join(ASSETS_DIR, "02_registration_page.png"))

        # ─────────────────────────────────────────────────────────────────────
        # 3. Warden Command Center (Log in as Warden)
        # ─────────────────────────────────────────────────────────────────────
        print("3. Logging in as Warden & Capturing Command Center...")
        driver.get("http://localhost:5173/login")
        time.sleep(1.2)
        warden_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Chief Warden') or contains(text(), 'Warden')]")
        driver.execute_script("arguments[0].click();", warden_btn)
        time.sleep(0.5)
        submit_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        driver.execute_script("arguments[0].click();", submit_btn)
        time.sleep(2.5)
        driver.save_screenshot(os.path.join(ASSETS_DIR, "03_warden_command_center.png"))

        # ─────────────────────────────────────────────────────────────────────
        # 4. Warden Local LLM Settings Modal
        # ─────────────────────────────────────────────────────────────────────
        print("4. Capturing Warden Local LLM Settings Modal...")
        try:
            settings_btn = driver.find_element(By.XPATH, "//button[@title='AI Engine Settings' or @title='Local LLM Engine Settings']")
            driver.execute_script("arguments[0].click();", settings_btn)
            time.sleep(1.2)
            driver.save_screenshot(os.path.join(ASSETS_DIR, "04_warden_local_llm_settings_modal.png"))
            close_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Close') or contains(text(), 'Done') or contains(text(), '✕')]")
            if close_buttons:
                driver.execute_script("arguments[0].click();", close_buttons[0])
            time.sleep(1.0)
        except Exception as e:
            print("Modal 4 note:", e)

        # ─────────────────────────────────────────────────────────────────────
        # 5. Warden Complaint Telemetry Modal
        # ─────────────────────────────────────────────────────────────────────
        print("5. Capturing Warden Complaint Detail & Notes Modal...")
        try:
            detail_btns = driver.find_elements(By.XPATH, "//button[@title='Manage Ticket & Notes' or @title='View Details & Add Notes']")
            if detail_btns:
                driver.execute_script("arguments[0].click();", detail_btns[0])
                time.sleep(1.5)
                driver.save_screenshot(os.path.join(ASSETS_DIR, "05_warden_complaint_telemetry_modal.png"))
                driver.save_screenshot(os.path.join(ASSETS_DIR, "13_warden_media_evidence_telemetry.png"))
                print("✅ Saved 13_warden_media_evidence_telemetry.png")
                close_modal = driver.find_elements(By.XPATH, "//button[contains(text(), 'Close') or contains(text(), '✕')]")
                if close_modal:
                    driver.execute_script("arguments[0].click();", close_modal[0])
                time.sleep(1.0)
        except Exception as e:
            print("Modal 5 note:", e)

        # ─────────────────────────────────────────────────────────────────────
        # 6. Log in as Student & Capture Grievance Portal
        # ─────────────────────────────────────────────────────────────────────
        print("6. Logging in as Student & Capturing Student Portal...")
        driver.get("http://localhost:5173/login")
        time.sleep(1.2)
        student_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Resident Student') or contains(text(), 'Student')]")
        driver.execute_script("arguments[0].click();", student_btn)
        time.sleep(0.5)
        submit_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        driver.execute_script("arguments[0].click();", submit_btn)
        time.sleep(2.5)
        driver.save_screenshot(os.path.join(ASSETS_DIR, "06_student_grievance_portal.png"))

        # ─────────────────────────────────────────────────────────────────────
        # 7. Student Live AI Priority Triage Preview in action
        # ─────────────────────────────────────────────────────────────────────
        print("7. Testing Live AI Priority Preview...")
        try:
            inputs = driver.find_elements(By.TAG_NAME, "input")
            text_inputs = [inp for inp in inputs if inp.get_attribute("type") == "text"]
            if text_inputs:
                text_inputs[0].send_keys("Severe water leak into bathroom light fixture with continuous sparking")
                if len(text_inputs) > 1:
                    text_inputs[1].send_keys("304")
            
            textareas = driver.find_elements(By.TAG_NAME, "textarea")
            if textareas:
                textareas[0].send_keys("The washroom ceiling is leaking water directly onto the open switchbox and sparks are flying. Immediate electrocution risk for students!")
            
            # Wait for debounced live AI priority preview to execute and render
            time.sleep(2.5)
            driver.save_screenshot(os.path.join(ASSETS_DIR, "07_student_live_ai_triage_preview.png"))
            driver.save_screenshot(os.path.join(ASSETS_DIR, "12_student_media_evidence_upload.png"))
            print("✅ Saved 12_student_media_evidence_upload.png")
        except Exception as e:
            print("Preview note:", e)

        # ─────────────────────────────────────────────────────────────────────
        # 8. Student "Track My Complaints" Timeline Tracker
        # ─────────────────────────────────────────────────────────────────────
        print("8. Capturing Student Complaints Timeline Tracker with Media Evidence...")
        try:
            track_tab = driver.find_element(By.XPATH, "//button[contains(text(), 'My Complaints') or contains(text(), 'Track')]")
            driver.execute_script("arguments[0].click();", track_tab)
            time.sleep(1.5)
        except Exception as e:
            print("Track tab note:", e)

        # ─────────────────────────────────────────────────────────────────────
        # 9. Account & Resident Profile Page
        # ─────────────────────────────────────────────────────────────────────
        print("9. Capturing Account Profile Page...")
        driver.get("http://localhost:5173/account")
        time.sleep(2.0)
        driver.save_screenshot(os.path.join(ASSETS_DIR, "09_account_profile_page.png"))

        # ─────────────────────────────────────────────────────────────────────
        # 10. FastAPI Interactive Swagger Documentation
        # ─────────────────────────────────────────────────────────────────────
        print("10. Capturing FastAPI Interactive Docs...")
        driver.get("http://localhost:3000/docs")
        time.sleep(2.5)
        driver.save_screenshot(os.path.join(ASSETS_DIR, "10_fastapi_swagger_api_docs.png"))

        print("\n✨ All screenshots captured successfully in assets/ directory!")

    finally:
        driver.quit()

if __name__ == "__main__":
    capture_all()
