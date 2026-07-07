# INGEK - Universal Fleet Control

An intelligent, next-generation aviation ground station designed to revolutionize international flight safety. INGEK acts as a real-time "Digital Twin," cloning vital aircraft telemetry from the sky directly to ground control to prevent catastrophic failures before they happen.

## 🚀 The Global Aviation Crisis & Problem
Traditional aircraft communications (like ACARS and SATCOM) operate on severely limited bandwidth channels, failing to stream comprehensive telemetry data continuously. When an inflight crisis occurs—such as pitot tube icing or sudden engine overheating—ground control teams are left functionally "blind," leading to critical delays in deploying tactical emergency support.

## 💡 The INGEK Solution
INGEK shatters this information gap by securely streaming and visualizing complex aircraft parameter matrices every 3 seconds. 
* **Real-time Digital Twin Cloning:** Continuously tracks and clones flight organ vital signs.
* **Dual-Mode Engine Flexibility:** Seamlessly switches between live streaming data and high-precision historical data retrieval for deep telemetry analysis.

## 🛠️ Advanced Tech Stack & AMD Compute Justification
To process millions of incoming data streams instantaneously without lagging, INGEK leverages massive hardware and AI acceleration:
* **AMD Compute Resources:** Developed and deployed utilizing high-performance AMD GPU architectures.
* **Fireworks AI Platform:** Drives ultra-fast, low-latency LLM inference pipelines.
* **Llama 3.1 8B Instruct:** Instantly dissects telemetry failure packages during critical anomalies and automatically generates enterprise-grade Emergency Action Protocols for ground crews.
* **Frontend Dashboard:** Built with Python and Streamlit for dynamic, real-time data visualization.

## 📦 Getting Started (Local Development)

### 1. Prerequisites
Ensure you have Python 3.10+ installed and access to your Fireworks AI API credentials.

### 2. Installation
Clone the repository and install the dependencies:
```bash
git clone https://github.com/arsyadpelajar01-coder/AMD-Cingkariak.git
cd AMD-Cingkariak
pip install -r requirements.txt
