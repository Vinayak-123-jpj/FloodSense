# FloodSense ESP32 Autonomous Node — Bill of Materials (BOM)

## FOSSEE Open Hardware National Make-A-Thon 2026 Specification
> **Status:** Planned Open-Hardware Blueprint (Software-Only Virtual Sensor Layer Built for 2026 Round)

The hardware architecture is designed to be affordable, solar-autonomous, weather-proof (IP65), and easy to deploy across rural river catchments in India.

---

### Component Breakdown & Pricing (in INR ₹)

| Component Category | Item Description | Model / Spec | Qty | Unit Cost (₹) | Total Cost (₹) | Supplier / Source |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **Microcontroller** | ESP32 Wi-Fi + BT Module | ESP32-WROOM-32 DevKit V1 | 1 | ₹350 | ₹350 | Robu.in / ElectronicsComp |
| **Water Level Sensor** | Waterproof Ultrasonic Distance Sensor | JSN-SR04T-V3.0 (20cm - 600cm range) | 1 | ₹650 | ₹650 | Robu.in / Amazon India |
| **Rain Sensor** | Tipping Bucket Rain Gauge | 0.2794mm per tip resolution | 1 | ₹1,200 | ₹1,200 | Robu.in / Centronic |
| **Solar Panel** | Monocrystalline Solar Module | 6V 5W Anodized Frame | 1 | ₹450 | ₹450 | Amazon India / Robu.in |
| **Battery Cell** | High-Cap Lithium Iron Phosphate | 18650 3.7V 3400mAh LiFePO4 | 2 | ₹220 | ₹440 | Industrial Energy Store |
| **Charge Controller** | Solar Battery Charger Module | TP4056 with CN3791 MPPT Solar Controller | 1 | ₹180 | ₹180 | Robu.in |
| **Enclosure** | Weatherproof Junction Box | IP65 ABS Sealed Box (200x120x75mm) | 1 | ₹320 | ₹320 | Local Hardware Store |
| **Mounting Hardware** | Stainless Steel Clamp & Pole Mounting | Galvanized 2-inch Pole Brackets | 1 | ₹250 | ₹250 | Local Hardware Store |
| **Wiring & Passive** | Jumper Wires, Resistors, PCB | 1:1 Divider Resistors & PCB | 1 set | ₹150 | ₹150 | Robu.in |
| **TOTAL ESTIMATED COST PER NODE** | | | | | **₹3,990 INR** | *(~ $48 USD)* |

---

### Key Operational Characteristics
- **Power Autonomy**: Built-in solar charging supports continuous operation during prolonged overcast monsoon periods for up to **14 consecutive days** without sunlight.
- **Ruggedness**: JSN-SR04T transducer sealed against high humidity, splashes, and debris.
- **Sampling Frequency**: Transmits telemetry every **10 seconds** during active monsoon alerts and drops to **5 minutes** during normal dry conditions to conserve power.
