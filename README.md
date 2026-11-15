# 🚀 AERIS (AER-Mon): Autonomous Edge Physiological Monitoring & Experimental Digital Twin Ecosystem

[![CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Code License: MIT](https://img.shields.io/badge/Code_License-MIT-green.svg)](https://opensource.org/licenses/MIT)
![Project Status](https://img.shields.io/badge/Status-In_Development_%2F_Prototype-blue.svg)
![Open Science](https://img.shields.io/badge/NASA_TOPS-SPD--41a_Compliant-orange.svg)

**AERIS** (**A**merica, **E**urope, **RIS**e — operating through its core module **AER-Mon**) is an edge-based astronaut health monitoring system that combines low-cost wearable biometric sensors and a personalized experimental **Digital Twin** to track physiological conditions in real time. Built for **Earth-Independent Medical Operations (EIMO)**, it detects physiological deviations, triggers multi-sensory early warnings, and provides non-diagnostic, step-by-step preventive guidance to safeguard astronauts during deep-space missions.

> **⚠️ Regulatory & Clinical Disclaimer (Non-Diagnostic System):** In strict alignment with NASA standards (**NASA-STD-3001** and ExMC guidelines), AERIS/AER-Mon is **NOT** an automated medical doctor and does not issue definitive clinical diagnoses. It operates strictly as a **Preventive Monitoring, Anomaly Detection, and Step-by-Step Action Guidance System**, preserving 100% of final authority with the human crew. This functional prototype developed for the NASA Space Apps Challenge 2026 has not yet been certified by a clinical organization.

---

## 📋 Table of Contents
1. [About the Project & NASA Space Apps Challenge Alignment](#1-about-the-project--nasa-space-apps-challenge-alignment)
2. [Project Information & Technical Deep Dive](#2-project-information--technical-deep-dive)
3. [Key Features & 3-Layer Modular Architecture](#3-key-features--3-layer-modular-architecture)
4. [Engineering Status & Transparency Note](#4-engineering-status--transparency-note)
5. [Repository Structure](#5-repository-structure)
6. [Installation & Usage](#6-installation--usage)
7. [Super Intelligence (SI) Tools Disclosure](#7-super-intelligence-si-tools-disclosure)
8. [Data Used (NASA and Agencies References)](#8-data-used-nasa-and-agencies-references)
9. [Team (TEAM AERIS)](#9-team-team-aeris)
10. [How to Contribute](#10-how-to-contribute)
11. [License](#11-license)

---

## 1. About the Project & NASA Space Apps Challenge Alignment

### 🛰️ What did you develop?
**TEAM AERIS** developed **AER-Mon** (AERIS Monitoring), an integrated hardware-software ecosystem running 100% locally (*Zero Cloud Dependency*). It consists of:
1. **AERIS Smart device Prototype (Edge Hardware Node):** An ESP32-based wearable node integrating optical, thermal, and kinematic sensors (`MAX30102`, `DS18B20`, `MPU6050`) with an onboard TFT screen and acoustic buzzer for immediate crew feedback.
2. **Central Habitat Server & Experimental Digital Twin (Raspberry Pi Node):** A unified local server running an MQTT broker (`Mosquitto`), a normalized `SQLite` database, and an individualized Digital Twin engine that compares real-time telemetry against personalized baseline profiles rather than generic population averages.

### 🎯 How does it address the challenge?
The 2026 Challenge poses a critical scenario: *"Imagine you are halfway to Mars. Suddenly, your fellow crewmate feels a sharp pain in the chest and collapses... Remember that astronauts are not necessarily medical doctors. Your tool should explain how to take each measurement, why it matters, and what to do when a value does not look normal."*

**AERIS** directly resolves this scenario by:
- **Automating Multi-Parameter Capture:** Continuously acquiring heart rate, $\text{SpO}_2$, peripheral skin temperature, and 3-axis acceleration without requiring a second crewmember to operate complex instruments.
- **Individualized Anomaly Detection:** Evaluating live telemetry alongside simulated emergency trends (e.g., hypoxia, tachycardia, fall/collapse kinematics) tailored to each astronaut's baseline.
- **Actionable Guidance for Non-Doctors:** Alerting the Crew Medical Officer (CMO)—who typically has only ~40 hours of basic medical training—via visual and acoustic cues, explaining how to verify sensor placement, why the physiological metric matters, and which official NASA/ESA/CSA stabilization countermeasure to follow.

### 🌍 Why is it important?
In Low Earth Orbit (ISS), astronauts rely on a real-time "umbilical cord" with Flight Surgeons in Houston. On a 3-year (~1,195-day) mission to Mars spanning 140 million miles, light-speed physics breaks that cord, creating communication delays of **20 to 24 minutes each way (up to 48 minutes round-trip)** plus solar wind blackouts. Moving from ground-dependent care to **Earth-Independent Medical Operations (EIMO)** requires onboard systems that close the perception-to-action loop in milliseconds. NASA studies (*LuCCI / Doc-in-a-Box* and *AMOS*) demonstrate that onboard clinical decision support reduces overall mission medical risk by **more than 34%**.

---

## 2. Project Information & Technical Deep Dive

### ⚙️ What does your project do, and how does it work?
AERIS bridges physical biometric capture and synthetic scenario modeling through a **Hybrid Demonstration Strategy**:
1. **Physical Telemetry Stream:** The `ESP32` reads biometric and kinematic signals, packages them into standardized JSON payloads, and publishes them over a local Wi-Fi network via the `MQTT` protocol.
2. **Local Broker & Persistence:** A single `Raspberry Pi` acts as the central mission computer, receiving MQTT topics via `Mosquitto`, normalizing payloads, and storing historical time-series data in a local `SQLite` database.
3. **Experimental Digital Twin & Bi-Directional Alerting:** The system evaluates incoming telemetry and synthetic emergency scenarios against individualized thresholds calibrated using Tri-Agency research:
   - **NASA HRP (5 Hazards / RIDGE):** Models cardiovascular deconditioning ("spherical heart"), fluid shifts associated with **SANS** (affecting ~20% of astronauts clinically), and the universal **600 mSv** career radiation limit.
   - **CSA Radiation Physics:** Incorporates the **30% ISS neutron radiation contribution** documented by the Canadian Space Agency (*EVARM, Radi-N2, CANS*) into vascular and systemic risk thresholds.
   - **ESA Life Sciences:** Accounts for **Low-Grade Inflammation (LGI)** (*Exposome Signature*) via peripheral temperature monitoring and circadian/autonomic stress (*RelaxPro*).
4. **Closed-Loop Alarm:** When an anomaly is detected, the Raspberry Pi updates the monitoring interface and publishes an alert back to the `ESP32` MQTT alarm topic, triggering the astronaut's TFT display and a 30-second acoustic buzzer cycle.

### 💡 What benefits does it have?
- **100% Local Autonomy (Zero Cloud):** Operates entirely inside the spacecraft's local network without internet dependency.
- **Individual Biological Variability:** Inspired by NASA JSC nutritional biochemistry research (Dr. Scott Smith & Dr. Sara Zwart on SANS genetic variability) and ESA life sciences, AERIS adapts to the individual astronaut rather than relying on rigid, one-size-fits-all clinical tables.
- **Reduced Crew Cognitive Load:** Automates 3 of the 4 primary routine medical checks (temperature, pulse/oximetry, and kinematic state, with expandable oscillometric blood pressure design), preventing checkup omissions caused by crew fatigue.

### 🌱 What is the intended impact?
1. **Deep Space Exploration (Artemis & Mars):** Safeguards astronaut lives (helping protect mission investments valued at ~$117M USD per astronaut training/mission cycle) during EVA preparation and intra-vehicular habitat monitoring.
2. **Earth Technology Transfer (ESA "AirScore" Commercial Model):** Following the European Space Agency's space business viability framework, AERIS avoids high aerospace CapEx traps (*OrbitalView*) and scales as a zero-launch-CapEx edge analytics platform (*AirScore*). Millions of people in **rural communities in Mexico and Latin America**, underground mines, offshore oil rigs, and disaster zones experience their own "Martian isolation" without specialist doctors or stable internet. Just as CSA's *EVARM* space sensors now serve over 1,000 terrestrial cancer clinics, AERIS brings autonomous triage and preventive guidance to disconnected rural clinics.
3. **International Open Science Milestone from Mexico (NASA SPD-41a):** AERIS implements NASA's **TOPS (Transform to Open Science)** workflow (*Open from Inception*) with a formal Open Science and Data Management Plan (OSDMP) based on **FAIR principles** (Open Data, Open Code, Open Results).

### 🛠️ What tools did you use? (Hardware & Software: WHY, HOW, and Specifications)

| Component / Tool | Specification | WHY we chose it | HOW it is used in AERIS |
| :--- | :--- | :--- | :--- |
| **ESP32 Dev Module** | Dual-core 32-bit MCU, 240 MHz, integrated Wi-Fi | Ultra-low power, high reliability, and native wireless telemetry at a fraction of commercial wearable costs. | Samples sensors, renders local states on the TFT display, drives the acoustic buzzer, and publishes/subscribes to MQTT topics. |
| **MAX30102** | Pulse Oximeter & Heart Rate Sensor (I2C, Red/IR LEDs) | Non-invasive optical photoplethysmography (PPG) for continuous cardiovascular tracking. | Estimates Heart Rate (BPM) and oxygen saturation ($\text{SpO}_2$) to detect hypoxia or cardiovascular stress. |
| **DS18B20** | 1-Wire Digital Thermometer ($\pm 0.5^\circ\text{C}$ accuracy) | High accuracy in the physiological range ($30^\circ\text{C}$–$42^\circ\text{C}$) and robust digital signal integrity. | Tracks peripheral skin temperature to detect early febrile peaks linked to ESA's Low-Grade Inflammation (LGI). |
| **MPU6050** | 6-Axis MEMS Accelerometer & Gyroscope (I2C) | Essential for correlating physiological spikes with physical exertion or sudden collapse. | Captures $X, Y, Z$ acceleration and derived magnitude to identify falls, immobility, or nocturnal agitation. |
| **TFT Display & Buzzer** | SPI Color Screen + Active Piezo Buzzer | Astronauts suffering from SANS visual blurring cannot read dense manuals during an emergency. | Provides high-contrast visual status cues and multi-beep acoustic alerts with automatic 30-second timeout. |
| **Raspberry Pi** | Single-Board Computer (Linux OS, local Wi-Fi hub) | Compact, low-wattage edge server capable of running message brokers, databases, and Digital Twin logic offline. | Hosts the `Mosquitto` MQTT broker, `SQLite` database, `receptor.py`/`generador.py` scripts, and the **AER-Mon** interface. |
| **Python 3 & SQLite** | Python (`paho-mqtt`, `sqlite3`), Serverless SQL Engine | Open-source, lightweight, zero-configuration persistence compliant with NASA FAIR reproducibility standards. | Normalizes real and simulated telemetry streams, stores longitudinal astronaut records, and triggers threshold alerts. |

### 🎨 How is your project creative?
- **Personalized Digital Twin over Static Alarms:** Clones an individual volunteer's baseline biometrics to simulate how *their* specific physiology would respond to Martian anomalies.
- **Hybrid Live + Synthetic Demonstration:** Combines live biometric telemetry from a real human volunteer wearing the ESP32 node with a real-time emergency injector (`generador.py`) to safely demonstrate life-threatening spaceflight scenarios (e.g., acute hypoxia or cardiovascular collapse) on stage.
- **UNAM-Inspired Cost Engineering:** Inspired by clinical validation studies at the **National Autonomous University of Mexico (UNAM)** on wrist oscillometric micro-cuffs, our architecture strips away expensive consumer smartwatch screens and cloud bloatware, reducing hardware node costs from **~$500 USD to ~$50 USD**.

### ⚡ What factors did your team consider? (Energy, Accessibility, Cost, Ethics)
- **Cost (~90% Reduction):** Built entirely with COTS (Commercial Off-The-Shelf) microelectronics (~$50 USD node) and open-source software, enabling effortless replication by schools, researchers, and rural clinics worldwide.
- **Energy Efficiency:** Edge-optimized C++ firmware and lightweight MQTT binary/JSON payloads minimize radio transmission overhead on the wearable and CPU draw on the Raspberry Pi.
- **Accessibility & Human Factors:** Designed specifically for non-medical crewmembers or operators experiencing **SANS-induced visual impairment**, prioritizing high-contrast visual states and distinct acoustic buzzer patterns.
- **Legal & Ethical Governance:** Built with *Privacy-by-Design* synthetic anonymization and aligned with **ISO/IEC 42001** (AI Management Systems) and **NASA-STD-3001**, strictly separating preventive guidance from unauthorized automated diagnosis.

---

## 3. Key Features & 3-Layer Modular Architecture

- **Layer 1 — Biometric & Kinematic Acquisition (`ESP32`):** Continuous sampling of estimated Heart Rate, $\text{SpO}_2$, peripheral temperature, and 3-axis acceleration ($X, Y, Z$ + vector magnitude), transmitted via periodic JSON MQTT payloads.
- **Layer 2 — Hardware-Agnostic Transport & Persistence (`Mosquitto` + `SQLite`):** Decoupled message normalization designed to scale seamlessly from local Wi-Fi/MQTT testbeds to certified spacecraft **CAN bus / SpaceWire (ESA)** networks and deep-space **DTN / Bundle Protocol (NASA)**.
- **Layer 3 — Experimental Digital Twin & Bi-Directional Alerting (`AER-Mon`):** Real-time comparison against individualized baseline profiles, synthetic emergency simulation, and immediate MQTT feedback alarms back to the astronaut's wrist device.

---

## 4. Engineering Status & Transparency Note

In commitment to scientific integrity and engineering transparency before the NASA Space Apps jury, we document the exact verification state of our prototype as of **November 15, 2026**:

- **✅ Verified in Current Audit:**
  - `ESP32` firmware acquiring telemetry (`MAX30102`, `MPU6050`, `DS18B20`), displaying status on TFT, and subscribing to the MQTT alarm topic with buzzer activation (~30s auto-shutoff).
  - Active `Mosquitto` MQTT broker running on the unified `Raspberry Pi`.
  - Functional telemetry ingestion (`receptor.py`) and synthetic scenario generator (`generador.py`) scripts.
- **🔄 In Final Integration for Delivery:**
  - Consolidation of the `SQLite` persistence schema, Experimental Digital Twin evaluator, alert publisher service, and visual monitor interface onto the single unified Raspberry Pi node for end-to-end live testing.
- **🔭 Future Roadmap (Outside Current Verified Prototype Scope):**
  - Local RAG assistant (*"Brag"* with offline medical manuals), 80/20 Random Forest predictive model validation, hardware oscillometric blood pressure & true R-R HRV capture, direct radiation dosimetry hardware, and 30-second local flash store-and-forward buffering on the ESP32 during Wi-Fi drops.
---

## 6 TEAM AERIS 
This is the official 5 integrants of team AERIS
- Manuel Mendoza Pino Tech Leader, documentation and prototype design
- Emilio Cervera Uicab Team Leader, documentation and visuals
- Ian Mendoza Ancona 3D designer and documentation
- Jorge Guitérrez Jacobo ML expert and software designer 
- Eduardo Domenzain Uh Visuals Leader and Pitch
---
## DATA USED (NASA AND AGENCIES REFERENCES)

### NASA

#### HRP (Human Research Program & EIMO Clinical Standards)
- NASA Human Research Program (HRP) 5 Hazards of Human Spaceflight -- https://www.nasa.gov/hrp/hazards/
- NASA Human Research Program (HRP) Overview -- https://www.nasa.gov/hrp/
- NASA HRP Hazard 1: Space Radiation -- https://www.nasa.gov/hrp/hazard-space-radiation/
- NASA HRP Hazard 2: Isolation and Confinement -- https://www.nasa.gov/hrp/hazard-isolation-and-confinement/
- NASA HRP Hazard 3: Distance from Earth -- https://www.nasa.gov/hrp/hazard-distance-from-earth/
- NASA HRP Hazard 4: Gravity Fields -- https://www.nasa.gov/hrp/hazard-gravity-fields/
- NASA HRP Hazard 5: Hostile/Closed Environments -- https://www.nasa.gov/hrp/hazard-hostile-closed-environments/
- A Clinical Decision Support System for Earth-independent Medical Operations -- https://www.nasa.gov/centers-and-facilities/ames/ames-science/ames-space-biosciences/a-clinical-decision-support-system-for-earth-independent-medical-operations/
- NASA Spaceflight Human-System Standard: Volume 1: Crew Health -- https://www.nasa.gov/wp-content/uploads/2023/03/nasa-std-3001-vol-1-rev-c-with-signature.pdf
- Human System Risk Management Plan, JSC-66705 Rev. A -- https://ntrs.nasa.gov/citations/20205008887
- NASA Human Research Roadmap (HRR) -- https://humanresearchroadmap.nasa.gov/
- Risks of human spaceflight -- https://www.nasa.gov/hrp/risks/
- Risk of spaceflight associated neuro-ocular syndrome (SANS) -- https://www.nasa.gov/reference/risk-of-spaceflight-associated-neuro-ocular-syndrome-sans/
- Risk of hypoxia -- https://www.nasa.gov/reference/risk-of-hypoxia/
- Risk of reduced cardiorespiratory and musculoskeletal fitness -- https://www.nasa.gov/reference/risk-of-reduced-cardiorespiratory-and-musculoskeletal-fitness/

#### OSDR (Open Science Data Repository & Open Science Plan)
- About OSDR & Biological and Physical Sciences Data Repository -- https://science.nasa.gov/biological-physical/data/osdr/
- ROSES Open Science and Data Management Plan -- https://science.nasa.gov/researchers/sara/faqs/osdmp/

#### LSDA (Life Sciences Data Archive / Commercial & Physical Sciences Repositories)
- NASA's Repository Supports Research of Commercial Astronaut Health -- https://science.nasa.gov/humans-in-space/nasas-repository-supports-research-of-commercial-astronaut-health/?utm_source=
- History and Mission of Physical Science Informatics -- https://science.nasa.gov/physical-sciences-informatics-psi/history-of-physical-science-informatics/
- The NASA Task Book -- https://taskbook.nasaprs.com/

#### LSAH (Lifetime Surveillance of Astronaut Health / Longitudinal & Biomedical Records)
- TREAT Astronauts Act -- https://www.nasa.gov/hhp/treat-astronauts-act/
- NASA Human Health and Performance Directorate (HH&P) - Human System Risks Registry -- https://www.nasa.gov/hhp/human-system-risks/
- The Human Body in Space -- https://www.nasa.gov/humans-in-space/the-human-body-in-space/
- Biomedical Results of Apollo -- https://history.nasa.gov/SP-368/s2ch3.htm
- NASA Space Cancer Risk Model: 2020 Operational Implementation -- https://ntrs.nasa.gov/citations/20210013314

---

### ESA (European Space Agency)
- Exposome Signature: A multi-system view of human adaptation to spaceflight -- https://www.esa.int/Science_Exploration/Human_and_Robotic_Exploration/epsilon/Exposome_Signature_A_multi_system_view_of_human_adaptation_to_spaceflight
- RelaxPro: Helping astronauts sleep and manage stress in space -- https://www.esa.int/Science_Exploration/Human_and_Robotic_Exploration/epsilon/RelaxPro_Helping_astronauts_sleep_and_manage_stress_in_space
- EasyMotion-2: Using electrical stimulation to preserve astronaut muscles in space -- https://www.esa.int/Science_Exploration/Human_and_Robotic_Exploration/epsilon/EasyMotion_2_Using_electrical_stimulation_to_preserve_astronaut_muscles_in_space
- New European exercise device begins testing with first rope-pulling workout in space -- https://www.esa.int/Science_Exploration/Human_and_Robotic_Exploration/New_European_exercise_device_begins_testing_with_first_rope-pulling_workout_in_space
- Space for Everyone — Module 7: Space Business, Lesson 1: Technology on Earth -- https://learn.esa.int/explore/space-everyone

---

### CSA (Canadian Space Agency)
- Little transistor records radiation levels (EVARM) -- https://www.asc-csa.gc.ca/eng/iss/evarm.asp
- MOSFET radiation monitoring system and Matroshka-R -- https://www.asc-csa.gc.ca/eng/astronauts/space-medicine/mosfet.asp
- Effects of space on the body -- https://www.asc-csa.gc.ca/eng/astronauts/living-in-space/effects-of-space-on-the-body.asp
- Monitoring radiation for astronaut health -- https://www.asc-csa.gc.ca/eng/news/articles/2026/2026-02-26-monitoring-radiation-astronaut-health.asp
- Chris Hadfield explains the Radi-N2 experiment (Video) -- https://www.asc-csa.gc.ca/eng/multimedia/search/video/17883#transcript



---

## 5. Repository Structure

```text
AERIS/
├── docs/                       # Master research documentation (V4), OSDMP, and manuals
├── assets/                     # Infographics, architecture diagrams, and SI-watermarked media
├── src/                        # Source code and executable scripts
│   ├── firmware_esp32/         # Arduino/C++ firmware for sensors, TFT, buzzer & MQTT
│   ├── server_rpi/             # Python MQTT receptor.py, generador.py, SQLite & Digital Twin
│   └── notebooks/              # Reproducible Jupyter Notebooks (Open Code - MIT License)
├── CODE_OF_CONDUCT.md          # Community standards (NASA Open Science compliant)
├── CONTRIBUTING.md             # Guidelines for open collaboration
├── CITATION.cff                # One-click scientific citation metadata
├── README.md                   # General project overview and NASA Space Apps documentation
└── LICENSE                     # Full legal text of the CC BY 4.0 & MIT Dual Licensing

---

**Note.**Because lack of time We decided to simplified our repository structure in only one file with code, a link to our
landing page and our Social Media. In order to keep this structure and have a clear way to keep developing AERIS.


