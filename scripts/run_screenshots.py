import os, subprocess, time

CHROME_PATH = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
OUTPUT_DIR = os.path.abspath('docs/screenshots')
os.makedirs(OUTPUT_DIR, exist_ok=True)

targets = [
    ('replay-10pct.png', 'http://localhost:3000/replay?pct=10', 1440, 900),
    ('replay-50pct.png', 'http://localhost:3000/replay?pct=50', 1440, 900),
    ('replay-75pct.png', 'http://localhost:3000/replay?pct=75', 1440, 900),
    ('replay-98pct.png', 'http://localhost:3000/replay?pct=98', 1440, 900),
    ('landing-1440-light.png', 'http://localhost:3000/?theme=light', 1440, 900),
    ('landing-1440-dark.png', 'http://localhost:3000/?theme=dark', 1440, 900),
    ('landing-375-light.png', 'http://localhost:3000/?theme=light', 375, 812),
    ('landing-375-dark.png', 'http://localhost:3000/?theme=dark', 375, 812),
    ('monitor-1440-light.png', 'http://localhost:3000/live?theme=light', 1440, 900),
    ('monitor-1440-dark.png', 'http://localhost:3000/live?theme=dark', 1440, 900),
    ('monitor-375-light.png', 'http://localhost:3000/live?theme=light', 375, 812),
    ('monitor-375-dark.png', 'http://localhost:3000/live?theme=dark', 375, 812),
    ('monitor-source-real.png', 'http://localhost:3000/live?source=REAL&theme=light', 1440, 900),
    ('monitor-source-simulated.png', 'http://localhost:3000/live?source=SIMULATED&theme=light', 1440, 900),
    ('model-1440-light.png', 'http://localhost:3000/model?theme=light', 1440, 1000),
    ('model-1440-dark.png', 'http://localhost:3000/model?theme=dark', 1440, 1000),
    ('model-375-light.png', 'http://localhost:3000/model?theme=light', 375, 812),
    ('model-375-dark.png', 'http://localhost:3000/model?theme=dark', 375, 812),
    ('alerts-1440-light.png', 'http://localhost:3000/alerts?theme=light', 1440, 900),
    ('alerts-1440-dark.png', 'http://localhost:3000/alerts?theme=dark', 1440, 900),
    ('alerts-375-light.png', 'http://localhost:3000/alerts?theme=light', 375, 812),
    ('alerts-375-dark.png', 'http://localhost:3000/alerts?theme=dark', 375, 812)
]

for filename, url, w, h in targets:
    out_file = os.path.join(OUTPUT_DIR, filename)
    cmd = [
        CHROME_PATH,
        '--headless',
        '--disable-gpu',
        '--virtual-time-budget=3000',
        f'--window-size={w},{h}',
        f'--screenshot={out_file}',
        url
    ]
    print(f'Capturing {filename}...')
    try:
        subprocess.run(cmd, check=True, timeout=20)
        size = os.path.getsize(out_file) if os.path.exists(out_file) else 0
        print(f'  [OK] {filename} ({size // 1024} KB)')
    except Exception as e:
        print(f'  [FAIL] Failed {filename}: {e}')
