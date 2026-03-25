🎵 SpotyShell
Remote Task Execution via Spotify Metadata.

SpotyShell is an asynchronous Python-based engine designed to bridge media interactions with system-level automation. It monitors incoming Spotify links and maps their metadata to pre-defined shell commands.

💻 Technical Architecture
Core Framework
Python 3.11+: Leveraging asyncio for non-blocking event loops.

Telegram Bot API: Primary Command-and-Control (C2) interface.

Subprocess Management: Utilizes Python's subprocess module to execute binaries and capture real-time execution logs.

[!IMPORTANT]
Resource Optimization: This engine is architected with a minimal-footprint approach, ensuring stability in environments with limited RAM (e.g., 512MB) and CPU overhead.

🛠️ Internal Logic & Workflow
Intercept: The engine listens for specific URL patterns (Spotify shares) sent via the C2 interface.

Validate: Metadata is parsed and validated to ensure the request is authorized.

Execute: The system triggers internal shell routines based on the input mapping.

Bash
# Example Execution Flow
[Input]  -> Spotify URL
[Action] -> Metadata Parsing -> Logic Mapping
[Output] -> Shell Script Execution -> Telegram Feedback
🚀 System Integration
Process Persistence
We use PM2 for daemonization to ensure 24/7 persistence, automated logging, and crash recovery.

[!TIP]
Network Resilience: The system is integrated with nmcli to handle automated priority switching between saved WiFi profiles without manual intervention.
