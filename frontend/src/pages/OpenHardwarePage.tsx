import React from 'react';
import { Cpu, Layers, ShieldCheck, Download, Code, FileText } from 'lucide-react';

export const OpenHardwarePage: React.FC = () => {
  const bomItems = [
    { category: "Microcontroller", name: "ESP32 Wi-Fi + BT DevKit V1", qty: 1, cost: "₹350", source: "Robu.in" },
    { category: "Water Level Sensor", name: "JSN-SR04T Waterproof Ultrasonic", qty: 1, cost: "₹650", source: "Amazon India" },
    { category: "Rain Sensor", name: "Tipping Bucket Rain Gauge (0.2794mm)", qty: 1, cost: "₹1,200", source: "Robu.in" },
    { category: "Solar Module", name: "6V 5W Monocrystalline Panel", qty: 1, cost: "₹450", source: "Amazon India" },
    { category: "Battery Pack", name: "18650 3.7V 3400mAh LiFePO4 Cells", qty: 2, cost: "₹440", source: "Industrial Store" },
    { category: "Charge Controller", name: "TP4056 + MPPT CN3791 Solar Module", qty: 1, cost: "₹180", source: "Robu.in" },
    { category: "Enclosure", name: "IP65 Weatherproof ABS Box (200x120mm)", qty: 1, cost: "₹320", source: "Local Store" },
    { category: "Mounting & Hardware", name: "Galvanized 2-inch Pole Brackets & Wires", qty: 1, cost: "₹400", source: "Local Store" }
  ];

  return (
    <div className="space-y-8 pb-12">
      
      {/* Page Header */}
      <div className="border-b border-survey-border dark:border-night-border pb-3">
        <span className="font-mono text-xs text-survey-teal dark:text-night-teal uppercase tracking-wider block">FOSSEE OPEN HARDWARE NATIONAL MAKE-A-THON 2026</span>
        <h1 className="font-serif text-3xl font-bold text-survey-ink dark:text-night-text">Open Hardware Blueprint & ESP32 Firmware</h1>
        <p className="font-sans text-xs text-survey-slate dark:text-night-slate">Complete hardware schematics, C++ Arduino sketch, and Bill of Materials for physical node deployment.</p>
      </div>

      {/* Hardware Blueprint Banner */}
      <div className="rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <span className="font-mono text-xs text-survey-teal dark:text-night-teal uppercase block">NODE COST PER UNIT</span>
          <div className="font-mono text-3xl font-bold text-survey-ink dark:text-night-text mt-1">₹3,990 INR</div>
          <span className="font-sans text-xs text-survey-slate dark:text-night-slate">~$48 USD estimated total hardware BOM</span>
        </div>
        <div>
          <span className="font-mono text-xs text-survey-teal dark:text-night-teal uppercase block">POWER AUTONOMY</span>
          <div className="font-mono text-3xl font-bold text-survey-ink dark:text-night-text mt-1">14 Days</div>
          <span className="font-sans text-xs text-survey-slate dark:text-night-slate">6V 5W Solar + Dual 18650 LiFePO4 battery</span>
        </div>
        <div>
          <span className="font-mono text-xs text-survey-teal dark:text-night-teal uppercase block">OPEN LICENCE</span>
          <div className="font-mono text-3xl font-bold text-survey-ink dark:text-night-text mt-1">MIT Licence</div>
          <span className="font-sans text-xs text-survey-slate dark:text-night-slate">100% Open Source code & CAD blueprints</span>
        </div>
      </div>

      {/* Section 1: Vector Wiring Schematic */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="font-serif text-xl font-bold text-survey-ink dark:text-night-text">Hardware Wiring Schematic</h2>
          <span className="font-mono text-xs text-amber-600 dark:text-amber-400 font-semibold uppercase">PLANNED BLUEPRINT • NOT BUILT THIS ROUND</span>
        </div>

        <div className="rounded border border-survey-border dark:border-night-border bg-night-bg p-4 flex justify-center">
          <img
            src="/firmware-stub/wiring_diagram.svg"
            alt="ESP32 Wiring Schematic"
            className="w-full max-w-4xl h-auto rounded"
            onError={(e) => {
              // Fallback to inline SVG text if image tag path fails
              (e.target as HTMLElement).style.display = 'none';
            }}
          />
        </div>
      </section>

      {/* Section 2: Bill of Materials (BOM) Table */}
      <section className="space-y-3">
        <h2 className="font-serif text-xl font-bold text-survey-ink dark:text-night-text">Bill of Materials (BOM Table)</h2>
        
        <div className="overflow-x-auto rounded border border-survey-border dark:border-night-border bg-survey-card dark:bg-night-card">
          <table className="w-full text-left border-collapse font-sans text-xs">
            <thead>
              <tr className="border-b border-survey-border dark:border-night-border bg-survey-paper dark:bg-night-bg font-mono text-[11px] text-survey-teal dark:text-night-teal uppercase">
                <th className="p-3">Category</th>
                <th className="p-3">Item Description</th>
                <th className="p-3">Qty</th>
                <th className="p-3">Cost (INR)</th>
                <th className="p-3">Source</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-survey-border/40 dark:divide-night-border/40">
              {bomItems.map((item, idx) => (
                <tr key={idx} className="hover:bg-survey-paper/50 dark:hover:bg-night-bg/50">
                  <td className="p-3 font-mono font-medium text-survey-teal dark:text-night-teal">{item.category}</td>
                  <td className="p-3 font-semibold text-survey-ink dark:text-night-text">{item.name}</td>
                  <td className="p-3 font-mono">{item.qty}</td>
                  <td className="p-3 font-mono font-bold text-survey-ink dark:text-night-text">{item.cost}</td>
                  <td className="p-3 text-survey-slate dark:text-night-slate">{item.source}</td>
                </tr>
              ))}
              <tr className="bg-survey-paper dark:bg-night-bg font-mono font-bold">
                <td colSpan={3} className="p-3 text-survey-ink dark:text-night-text uppercase">Total Estimated Cost Per Node</td>
                <td colSpan={2} className="p-3 text-emerald-700 dark:text-emerald-400 text-sm">₹3,990 INR (~ $48 USD)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* Section 3: ESP32 C++ Arduino Sketch Preview */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="font-serif text-xl font-bold text-survey-ink dark:text-night-text">ESP32 Arduino Firmware Sketch (`node_firmware.ino`)</h2>
          <span className="font-mono text-xs text-survey-teal dark:text-night-teal">HTTP POST JSON / Wi-Fi</span>
        </div>

        <div className="rounded border border-survey-border dark:border-night-border bg-[#0C141B] p-4 text-emerald-400 font-mono text-xs overflow-x-auto">
          <pre className="whitespace-pre">{`/*
 * FloodSense ESP32 Autonomous Monitoring Station Firmware
 * PLANNED HARDWARE BLUEPRINT — NOT BUILT IN THIS ROUND (SOFTWARE SIMULATION ONLY)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* API_SERVER_URL = "http://floodsense.local/api/readings";
const char* NODE_ID = "KL-PER-01";

void loop() {
    float water_level_cm = measureWaterLevelCm();
    float rainfall_mm_hr = measureRainfall();
    float battery_pct = measureBattery();

    StaticJsonDocument<256> doc;
    doc["node_id"] = NODE_ID;
    doc["water_level_cm"] = water_level_cm;
    doc["rainfall_mm_hr"] = rainfall_mm_hr;
    doc["battery_pct"] = battery_pct;

    String requestBody;
    serializeJson(doc, requestBody);

    HTTPClient http;
    http.begin(API_SERVER_URL);
    http.addHeader("Content-Type", "application/json");
    int httpCode = http.POST(requestBody);
    http.end();
}`}</pre>
        </div>
      </section>

    </div>
  );
};
