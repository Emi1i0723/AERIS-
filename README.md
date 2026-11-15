# AERIS · AER-Mon

**Local physiological telemetry, experimental anomaly analysis, and a browser dashboard for space-crew monitoring.**

AERIS (America, Europe, RISe) is TEAM AERIS's NASA Space Apps Challenge 2026 prototype. Its monitoring concept, AER-Mon, connects ESP32 devices to a Raspberry Pi through a local MQTT broker. The server stores measurements in SQLite and serves a dashboard with recent readings, historical trends, and technical indicators from **Ermon**, the experimental anomaly-analysis module.

The project explores how accessible sensors and onboard computing could support monitoring when ground support or internet connectivity is limited. Its longer-term vision includes individualized digital twins and preventive guidance. The current implementation provides telemetry ingestion, historical storage, statistical analysis, and visualization.

> **Prototype scope:** AERIS is not a clinically validated medical device. Ermon identifies changes in recorded signals and data availability; its outputs are not diagnoses or treatment instructions. No clinical certification, NASA endorsement, or standards-compliance assessment is established by this repository.

## Contents

- [Project purpose](#project-purpose)
- [Architecture and data flow](#architecture-and-data-flow)
- [Repository structure](#repository-structure)
- [Hardware and software](#hardware-and-software)
- [Telemetry and storage](#telemetry-and-storage)
- [How Ermon works](#how-ermon-works)
- [Dashboard](#dashboard)
- [REST API](#rest-api)
- [Running the prototype](#running-the-prototype)
- [Verification and limitations](#verification-and-limitations)
- [Roadmap](#roadmap)
- [AI assistance disclosure](#ai-assistance-disclosure)
- [Research context and references](#research-context-and-references)
- [Team](#team)
- [Contributing and licensing](#contributing-and-licensing)

## Project purpose

NASA's Human Research Program describes five hazards of human spaceflight, including distance from Earth and altered gravity environments. These provide context for AERIS's interest in local monitoring and reduced dependence on remote support. See [NASA: Five Hazards of Human Spaceflight](https://www.nasa.gov/hrp/hazards/).

The prototype combines affordable, commercially available hardware with a local software stack. Its demonstration pairs a physical sensor device with a controllable simulator, allowing the team to show changing signals without deliberately creating dangerous physiological conditions in a volunteer.

The same design could be explored for education and monitoring research in disconnected terrestrial settings, including rural communities in Mexico and Latin America. Suitability for clinical use, mission deployment, cost savings, energy consumption, and medical-risk reduction have not been established by this implementation.

## Architecture and data flow

```text
ESP32 #1: physical sensors ───────┐
          astronauta1           │
                               ├── Local Wi-Fi / MQTT ── Mosquitto
ESP32 #2: signal simulator ─────┘                              │
          astronauta2                                        ▼
                                                     mqtt/receptor.py
                                                            │
                                                            ▼
                                                   SQLite: mediciones
                                                       │         │
                                                       │         ▼
                                                       │       Ermon
                                                       │         │
                                                       ▼         ▼
                                                     Flask REST API
                                                            │
                                                            ▼
                                                 Browser dashboard
                                                 (reported: iPad)
```

1. Devices publish JSON measurements under `nasa/astronautas/`.
2. `mqtt/receptor.py` subscribes to `nasa/astronautas/#`, validates the payload, adds the server's UTC reception timestamp, and inserts a row into SQLite.
3. `api/servidor.py` serves the dashboard and measurement endpoints. Requests to the Ermon endpoint run the analysis against stored measurements.
4. The browser requests both profiles every three seconds and renders received values, trends, and Ermon messages.

The runtime data path uses local services and does not call a cloud AI service. Ermon runs when requested; this source tree does not contain a background alert-publishing service or a server-to-ESP32 MQTT alarm loop.

The optional **Python generator** is a separate source of simulated telemetry. It publishes under **both** astronaut identifiers and is not the firmware for ESP32 #2.

## Repository structure

Paths below are relative to the repository root. The local folder name `bueno` is not part of the application architecture.

```text
.
├── api/
│   ├── servidor.py                # Flask dashboard and REST routes
│   └── templates/
│       └── index.html             # HTML, CSS, JavaScript, embedded image
├── database/
│   └── crear_bd.py                # Creates astronautas.db and mediciones
├── ermon/
│   ├── lector_datos.py            # Read-only SQLite queries
│   ├── analizador.py              # Rolling per-variable Z-score analysis
│   ├── modelo_ml.py               # Mahalanobis model: training and inference
│   ├── modelo_ermon.npz           # Saved mean, inverse covariance, threshold
│   └── alertas.py                 # Data freshness, quality, and analysis states
├── mqtt/
│   ├── receptor.py                # Active ingestion and persistence script
│   └── generador.py               # Optional two-profile software simulator
├── mqtt_respaldo_20261115_011711/
│   ├── receptor.py                # Historical backup, not the active receiver
│   └── generador.py               # Historical backup generator
├── logs/                         # Local runtime directory; empty in reviewed copy
└── Technical_Report.md           # Team's implementation and demonstration report
```

`database/astronautas.db` is generated locally and was not included in the reviewed copy. ESP32 firmware, wiring diagrams, Mosquitto configuration, systemd unit files, dependency lockfiles, and license files are not present. The server code can therefore be reviewed here, but the complete physical deployment cannot be reproduced from this tree alone.

## Hardware and software

The team reports the following demonstration hardware; device firmware is outside this source snapshot.

| Component | Role |
| --- | --- |
| ESP32 #1 / `astronauta1` | Sends measurements from physical sensors |
| MAX30102 | Optical pulse and SpO₂ estimation |
| DS18B20 | Temperature sensing; not a validated core-body temperature measurement |
| MPU6050 | Acceleration measurements and motion-related telemetry |
| ESP32 #2 / `astronauta2` | Controllable simulated signals for the demonstration |
| Raspberry Pi | Local MQTT broker, receiver, SQLite database, API, and Ermon |
| Browser / iPad | Dashboard client on the same local network |

The included server uses **Python, Paho MQTT, SQLite, Flask, and NumPy**. The technical report identifies **Mosquitto** as the broker and **Gunicorn** as the deployed application server. The dashboard uses browser JavaScript and canvas charts; no frontend build step is included.

TFT and buzzer features described in the earlier project overview cannot be verified without the ESP32 firmware. They are not part of the server-side behavior documented here.

## Telemetry and storage

Example payload for topic `nasa/astronautas/astronauta1`:

```json
{
  "astronauta_id": "astronauta1",
  "frecuencia_cardiaca": 78,
  "spo2": 98,
  "temperatura": 33.4,
  "ax": 0.02,
  "ay": -0.04,
  "az": 1.01,
  "aceleracion_g": 1.01
}
```

| Field | Meaning and receiver validation |
| --- | --- |
| `astronauta_id` | Non-empty string identifying the source profile |
| `frecuencia_cardiaca` | Heart rate in bpm; integer from 0 to 250 |
| `spo2` | Oxygen saturation estimate in percent; integer from 0 to 100 |
| `temperatura` | Temperature in °C; finite numeric value |
| `ax`, `ay`, `az` | Acceleration axes, displayed as g; finite numeric values |
| `aceleracion_g` | Acceleration magnitude in g; finite, nonnegative numeric value |

All eight fields are required. These are input-validation rules, not clinical normal ranges. The receiver does not calculate acceleration magnitude, verify sensor calibration, or enforce that the topic matches the payload identifier.

The `mediciones` table stores these fields plus an auto-incrementing `id` and `fecha_recepcion`. The timestamp represents **server reception**, not a device sampling timestamp. The receiver accepts identifiers beyond the two dashboard profiles, while Ermon restricts analysis to `astronauta1` and `astronauta2`.

The software generator publishes one sample per profile in each loop, followed by a three-second pause. It generates heart rate from 60–110 bpm, SpO₂ from 94–100%, temperature from 20–38 °C, and random acceleration axes. These are software test ranges. It has no built-in emergency-scenario selector.

## How Ermon works

### Recent-sample statistical analysis

For each astronaut, `analizador.py` reads up to **30 recent rows** and evaluates heart rate, SpO₂, temperature, and acceleration magnitude independently. Each variable needs at least **10 valid values**.

The latest valid value is compared with the mean and population standard deviation of the preceding valid values:

```text
z = (latest value − reference mean) / reference standard deviation
```

An absolute Z-score of **2.5 or higher** produces `desviacion_detectada`. A change from a constant reference produces `variacion_sin_referencia`; insufficient history produces `datos_insuficientes`.

This is a moving statistical reference for each profile, not a physiological simulation or a clinically calibrated personal baseline. Sustained changes can enter the rolling reference over time.

### Experimental multivariable model

`modelo_ml.py` uses **heart rate, SpO₂, and acceleration magnitude**. Temperature is not a model input. Training estimates a mean vector and regularized covariance matrix, then sets a threshold at the **99th percentile of training-set Mahalanobis distances**. A new sample above that threshold returns `anomalia_ml`; otherwise it returns `patron_compatible`.

The saved `.npz` contains one model shared by both profiles. The report and code comments describe its initial training data as synthetic; the training dataset and an independent validation dataset are not supplied. The model file itself does not establish training provenance or accuracy.

Running `python ermon/modelo_ml.py` trains on up to 100 current database rows for `astronauta1`, requires at least 20 valid rows, and **overwrites the saved model**. It is not necessary for normal startup. The script's final prediction uses a training sample and is not an independent evaluation.

### Combined technical status

`alertas.py` combines statistical results with checks for missing data, invalid values, and measurements older than **30 seconds**. Model anomalies are informational because model validation is pending.

| `estado_general` | Meaning |
| --- | --- |
| `sin_datos` | No measurements for the profile |
| `atencion` | At least one attention-level condition, such as stale data or a statistical deviation |
| `informativo` | Informational conditions only, including limited history or an experimental model anomaly |
| `sin_alertas` | No conditions added to the alert list |

Model availability is also returned separately in `modelo_ml`. A missing model can produce `modelo_no_disponible` without raising the overall status. `sin_alertas` therefore does not establish that all analysis components are available, nor that a person is healthy. Stale readings can still be analyzed, with their age reported alongside the result.

## Dashboard

The Flask-served dashboard provides:

- Selection between the two astronaut profiles, with both refreshed every three seconds.
- Latest heart rate, SpO₂, temperature, acceleration magnitude, and axes.
- Historical charts and browser CSV export from the currently buffered history.
- Ermon status, model classification, and explanatory technical messages.
- Missing/stale-reading indicators after the 30-second freshness window.

The browser initially requests up to 300 historical rows per profile, then appends new readings obtained by polling. Its in-memory history is limited to 300 records and the last ten minutes; CSV export is not a complete database export. Polling can miss intermediate samples in this buffer even when SQLite stores them.

Both profiles obtain live values from the API. The active JavaScript does not generate replacement measurements. Scenario and pause controls are hidden and disabled; posture is explicitly not calculated. The animated heart follows the received bpm value and is **not an ECG waveform**. Some initial HTML labels retain demonstration text, which the runtime renderer replaces.

## REST API

All listed routes use `GET`.

| Endpoint | Behavior |
| --- | --- |
| `/` | Renders the dashboard |
| `/api/estado` | Returns a static application status response; does not test MQTT, database health, or sensor availability |
| `/api/astronautas` | Lists distinct identifiers already stored in SQLite |
| `/api/astronautas/<astronauta_id>/ultimo` | Returns the newest row by insertion ID; HTTP 404 when no row exists |
| `/api/astronautas/<astronauta_id>/historico?limite=50` | Returns the latest requested rows in chronological insertion order |
| `/api/ermon/<astronauta_id>` | Evaluates freshness, data quality, statistical deviations, and the saved model |

The history limit defaults to `50` and accepts integers from `1` to `1000`; invalid limits return HTTP 400. An empty history returns an empty `mediciones` list. Ermon accepts only the two supported identifiers and returns HTTP 400 for others. Database errors return HTTP 500 in the measurement endpoints.

No API authentication or authorization is implemented in the supplied Flask code.

## Running the prototype

These instructions are derived from the reviewed source. They are a manual startup guide, not a reproduction of the team's unavailable service configuration or a newly verified Raspberry Pi deployment.

### 1. Match the expected project location

The current code expects **`/home/pi/nasa_space_apps`** on a Linux Raspberry Pi:

- API and MQTT scripts use `Path.home() / "nasa_space_apps"`.
- Ermon uses absolute paths under `/home/pi/nasa_space_apps`.
- The database initializer creates its database beside `database/crear_bd.py`.

To run the source without changing paths, place the repository contents there and run as user `pi`. A different account or checkout directory requires coordinated path changes; renaming the GitHub repository does not change these runtime assumptions.

### 2. Install dependencies

On Raspberry Pi OS / Debian, with Python 3 available:

```bash
sudo apt update
sudo apt install python3-venv mosquitto mosquitto-clients
cd /home/pi/nasa_space_apps
python3 -m venv .venv
source .venv/bin/activate
python -m pip install Flask numpy gunicorn "paho-mqtt==1.6.1"
python database/crear_bd.py
```

The Paho pin is a compatibility choice for the supplied legacy callback signatures and `mqtt.Client()` constructor, not a recovered deployment lockfile. Paho 2.0 introduced callback-version changes; see the [official migration guide](https://eclipse.dev/paho/files/paho.mqtt.python/html/migrations.html). Exact Flask, NumPy, and Gunicorn versions used in the demonstration were not recorded here.

### 3. Configure the local broker

The receiver connects to `localhost:1883` with username/password authentication. Mosquitto must be configured with matching credentials and a listener reachable from the ESP32 devices on the local network. Installing Mosquitto alone does not reproduce the team's broker settings; those files and the ESP32 configuration are not included.

**Publication issue in this snapshot:** MQTT credentials are embedded in the active receiver and historical backup scripts. Remove them from any public release and replace exposed credentials. The Python generator currently reads the `CONTRASENA` assignment from the receiver using Python's AST, so changing credential handling requires updating that integration too. No `.env` loader is currently implemented.

### 4. Start ingestion and the web application

Run the receiver in one terminal:

```bash
cd /home/pi/nasa_space_apps
source .venv/bin/activate
python mqtt/receptor.py
```

Run the application in a second terminal:

```bash
cd /home/pi/nasa_space_apps
source .venv/bin/activate
gunicorn --chdir api --bind 0.0.0.0:5000 servidor:app
```

Open `http://<raspberry-pi-local-ip>:5000/` in a browser on the same trusted network. This binding enables LAN access; the application has no access-control layer. For a local-only check, `python api/servidor.py` binds to `127.0.0.1:5000`, which is not directly accessible from an iPad.

The report names `nasa-api.service` and `nasa-receptor.service`, but their unit definitions are absent. The commands above start foreground processes and do not install those services.

### 5. Supply telemetry and check the API

Use the configured ESP32 devices, or run the optional software generator in a third terminal:

```bash
cd /home/pi/nasa_space_apps
source .venv/bin/activate
python mqtt/generador.py
```

For a software-only demo, stop physical publishers first: the generator uses the same two identifiers, and the database has no separate real/synthetic provenance field. Running both sources together mixes their rows.

```bash
curl http://127.0.0.1:5000/api/estado
curl http://127.0.0.1:5000/api/astronautas
curl http://127.0.0.1:5000/api/astronautas/astronauta1/ultimo
curl 'http://127.0.0.1:5000/api/astronautas/astronauta1/historico?limite=50'
curl http://127.0.0.1:5000/api/ermon/astronauta1
```

An empty database is expected before telemetry arrives. Allow enough samples for statistical analysis. Stopping a publisher for more than 30 seconds should produce a stale-data indication if it previously supplied measurements.

## Verification and limitations

### What this source review establishes

The reviewed files implement MQTT validation and persistence, the six listed Flask routes, dashboard API polling, statistical analysis, and Mahalanobis-based inference. All ten Python files passed a syntax parse. The supplied model loaded with `allow_pickle=False` and contains the expected mean, inverse covariance, and threshold parameters.

This review did not repeat physical acquisition, start the deployed Raspberry Pi services, or perform a new end-to-end runtime test. Flask was not installed in the review environment. Firmware, database history, service files, original test screenshots, and training data were not supplied.

### Demonstration results reported by the team

The Technical Report dated **November 15, 2026** records:

- Successful Flask route registration and HTTP 200 for the dashboard.
- Active `nasa-api.service` and `nasa-receptor.service` services.
- Dashboard access from Safari on an iPad, including both profiles, charts, and Ermon information.
- Missing-recent-data behavior while the physical `astronauta1` device was switched off.
- Incoming `astronauta2` measurements and historical trends from SQLite.
- A controlled simulator interval with an approximately 148 bpm peak and 87% minimum SpO₂ visible in history.

These are team-reported observations, not hardware results independently reproduced during this source review. As the report notes, the available screenshot was taken after values returned to their usual range; it does not prove that an active Ermon alert appeared during the anomaly interval. Those extreme values also cannot be generated by the included Python generator's normal ranges.

### Current boundaries

- No clinically validated inference, individual physiological digital twin, or treatment-guidance engine is included.
- No implemented radiation, SANS, inflammation, fall, posture, blood-pressure, or HRV inference is established by these files.
- No server-side return alarm publisher, ESP32 buffering implementation, CAN bus, SpaceWire, or DTN transport is included.
- The shared model has no supplied independent validation results, accuracy metrics, or reproducible training dataset.
- Stored data does not identify whether a row came from physical hardware or a simulator.
- Local operation does not imply encryption, anonymization, access control, or regulatory compliance.

## Roadmap

1. Publish firmware, wiring, broker configuration, service definitions, and tested dependency versions after removing credentials and private information.
2. Capture synchronized evidence of anomaly onset, active Ermon response, and recovery.
3. Separate physical and synthetic data provenance and preserve reproducible training/validation datasets.
4. Evaluate individual baselines and model behavior on representative data, including sustained changes and sensor artifacts.
5. Make paths and credentials configurable and add access controls appropriate to deployment.
6. Explore bidirectional device feedback, individualized digital twins, offline reference assistance, and additional sensors as separate, validated extensions.

## AI assistance disclosure

**OpenAI ChatGPT was used as an external development assistant.** According to the team's report, it supported drafting Python ingestion, database, API, and analysis code; integrating dashboard endpoints and refresh behavior; suggesting deployment and troubleshooting commands; and preparing documentation.

The team selected the architecture and hardware, configured devices and the Raspberry Pi, ran commands, reviewed suggestions, and observed the demonstration. ChatGPT did not independently operate the hardware or perform physical testing.

**Ermon is a separate component:** it runs the repository's statistical and experimental model logic locally. It does not call ChatGPT at runtime. This disclosure is a summary of documented assistance, not a line-by-line provenance audit.

## Research context and references

The original project documentation cites NASA, ESA, and CSA material as motivation and background research. These references should not be confused with training data: no agency dataset ingestion, agency-derived threshold calibration, or radiation-risk model appears in the reviewed code. The initial model is described as trained on synthetic telemetry.

The bibliography below preserves the team's original reference collection for further reading. Apart from the NASA hazards page referenced above, links and source-specific claims were not independently validated during this code review. Their inclusion does not establish endorsement or compliance.

### NASA

- [NASA Human Research Program (HRP) 5 Hazards of Human Spaceflight](https://www.nasa.gov/hrp/hazards/)
- [NASA Human Research Program (HRP) Overview](https://www.nasa.gov/hrp/)
- [NASA HRP Hazard 1: Space Radiation](https://www.nasa.gov/hrp/hazard-space-radiation/)
- [NASA HRP Hazard 2: Isolation and Confinement](https://www.nasa.gov/hrp/hazard-isolation-and-confinement/)
- [NASA HRP Hazard 3: Distance from Earth](https://www.nasa.gov/hrp/hazard-distance-from-earth/)
- [NASA HRP Hazard 4: Gravity Fields](https://www.nasa.gov/hrp/hazard-gravity-fields/)
- [NASA HRP Hazard 5: Hostile/Closed Environments](https://www.nasa.gov/hrp/hazard-hostile-closed-environments/)
- [A Clinical Decision Support System for Earth-independent Medical Operations](https://www.nasa.gov/centers-and-facilities/ames/ames-science/ames-space-biosciences/a-clinical-decision-support-system-for-earth-independent-medical-operations/)
- [NASA Spaceflight Human-System Standard: Volume 1: Crew Health](https://www.nasa.gov/wp-content/uploads/2023/03/nasa-std-3001-vol-1-rev-c-with-signature.pdf)
- [Human System Risk Management Plan, JSC-66705 Rev. A](https://ntrs.nasa.gov/citations/20205008887)
- [NASA Human Research Roadmap (HRR)](https://humanresearchroadmap.nasa.gov/)
- [Risks of human spaceflight](https://www.nasa.gov/hrp/risks/)
- [Risk of spaceflight associated neuro-ocular syndrome (SANS)](https://www.nasa.gov/reference/risk-of-spaceflight-associated-neuro-ocular-syndrome-sans/)
- [Risk of hypoxia](https://www.nasa.gov/reference/risk-of-hypoxia/)
- [Risk of reduced cardiorespiratory and musculoskeletal fitness](https://www.nasa.gov/reference/risk-of-reduced-cardiorespiratory-and-musculoskeletal-fitness/)

- [About OSDR & Biological and Physical Sciences Data Repository](https://science.nasa.gov/biological-physical/data/osdr/)
- [ROSES Open Science and Data Management Plan](https://science.nasa.gov/researchers/sara/faqs/osdmp/)

- [NASA's Repository Supports Research of Commercial Astronaut Health](https://science.nasa.gov/humans-in-space/nasas-repository-supports-research-of-commercial-astronaut-health/)
- [History and Mission of Physical Science Informatics](https://science.nasa.gov/physical-sciences-informatics-psi/history-of-physical-science-informatics/)
- [The NASA Task Book](https://taskbook.nasaprs.com/)

- [TREAT Astronauts Act](https://www.nasa.gov/hhp/treat-astronauts-act/)
- [NASA Human Health and Performance Directorate (HH&P) - Human System Risks Registry](https://www.nasa.gov/hhp/human-system-risks/)
- [The Human Body in Space](https://www.nasa.gov/humans-in-space/the-human-body-in-space/)
- [Biomedical Results of Apollo](https://history.nasa.gov/SP-368/s2ch3.htm)
- [NASA Space Cancer Risk Model: 2020 Operational Implementation](https://ntrs.nasa.gov/citations/20210013314)

### ESA (European Space Agency)
- [Exposome Signature: A multi-system view of human adaptation to spaceflight](https://www.esa.int/Science_Exploration/Human_and_Robotic_Exploration/epsilon/Exposome_Signature_A_multi_system_view_of_human_adaptation_to_spaceflight)
- [RelaxPro: Helping astronauts sleep and manage stress in space](https://www.esa.int/Science_Exploration/Human_and_Robotic_Exploration/epsilon/RelaxPro_Helping_astronauts_sleep_and_manage_stress_in_space)
- [EasyMotion-2: Using electrical stimulation to preserve astronaut muscles in space](https://www.esa.int/Science_Exploration/Human_and_Robotic_Exploration/epsilon/EasyMotion_2_Using_electrical_stimulation_to_preserve_astronaut_muscles_in_space)
- [New European exercise device begins testing with first rope-pulling workout in space](https://www.esa.int/Science_Exploration/Human_and_Robotic_Exploration/New_European_exercise_device_begins_testing_with_first_rope-pulling_workout_in_space)
- [Space for Everyone — Module 7: Space Business, Lesson 1: Technology on Earth](https://learn.esa.int/explore/space-everyone)

### CSA (Canadian Space Agency)
- [Little transistor records radiation levels (EVARM)](https://www.asc-csa.gc.ca/eng/iss/evarm.asp)
- [MOSFET radiation monitoring system and Matroshka-R](https://www.asc-csa.gc.ca/eng/astronauts/space-medicine/mosfet.asp)
- [Effects of space on the body](https://www.asc-csa.gc.ca/eng/astronauts/living-in-space/effects-of-space-on-the-body.asp)
- [Monitoring radiation for astronaut health](https://www.asc-csa.gc.ca/eng/news/articles/2026/2026-02-26-monitoring-radiation-astronaut-health.asp)
- [Chris Hadfield explains the Radi-N2 experiment (Video)](https://www.asc-csa.gc.ca/eng/multimedia/search/video/17883#transcript)

## Team

| TEAM AERIS member | Role |
| --- | --- |
| Manuel Mendoza Pino | Technical lead, documentation, and prototype design |
| Emilio Cervera Uicab | Team lead, documentation, and visuals |
| Ian Mendoza Ancona | 3D design and documentation |
| Jorge A. Gutiérrez Jacobo | ML and software design |
| Eduardo Domenzain Uh | Visuals lead and pitch |

## Contributing and licensing

Contributions can focus on reproducible setup, firmware documentation, data-quality checks, independent model evaluation, and clearer separation of implemented features from research goals. Include reproduction steps and synthetic examples when reporting an issue; do not attach personal telemetry or credentials.

Keep generated SQLite databases, logs, virtual environments, secret configuration, and private telemetry out of public releases. Historical backup files also require review because they contain embedded credentials. No `.gitignore` is supplied in this snapshot.

The earlier README states an intended licensing split of **MIT for code** and **CC BY 4.0 for documentation/content**. No corresponding license files are present in the reviewed tree. The team should provide the full license texts, attribution, and scope before presenting that licensing arrangement as complete. Open-science goals are part of the project vision; formal NASA SPD-41a, FAIR, or ISO/IEC 42001 compliance has not been verified here.
