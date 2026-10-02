import os, subprocess, time

CHROME_PATH = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
OUTPUT_DIR = os.path.abspath('docs/screenshots')
os.makedirs(OUTPUT_DIR, exist_ok=True)

stations = [
    'KL-PER-01', 'KL-PER-02', 'KL-PAM-01', 'KL-MUV-01', 'KL-CHA-01', 'KL-ACH-01',
    'AS-BRA-01', 'AS-BRA-02', 'AS-KOP-01', 'AS-DHA-01', 'AS-JIA-01'
]

targets = [
    ('landing-dark.png', 'http://localhost:3000/?theme=dark', 1440, 900),
    ('alerts-dark.png', 'http://localhost:3000/alerts?theme=dark', 1440, 900),
]

for st_id in stations:
    filename = f'live-monitor-{st_id}-dark.png'
    url = f'http://localhost:3000/live?station={st_id}&theme=dark'
    targets.append((filename, url, 1440, 900))

print("Starting screenshot capture of 11 station Live Monitors + Landing + Alerts...")
for filename, url, w, h in targets:
    out_file = os.path.join(OUTPUT_DIR, filename)
    cmd = [
        CHROME_PATH,
        '--headless',
        '--disable-gpu',
        '--virtual-time-budget=4000',
        f'--window-size={w},{h}',
        f'--screenshot={out_file}',
        url
    ]
    try:
        subprocess.run(cmd, check=True, timeout=20)
        size = os.path.getsize(out_file) if os.path.exists(out_file) else 0
        print(f'  [OK] {filename} ({size // 1024} KB)')
    except Exception as e:
        print(f'  [FAIL] {filename}: {e}')

print("\nScreenshot capture complete.")
