# 🎯 Agentic Canvas - Industrial AI Innovation Framework

A consolidated Flask application showcasing **5 industrial AI agent demonstrations** through a unified "Agentic Canvas" interface.

## 🌟 Features

### Demo 1: Carbon Compass (T3 Cognitive Agent)
- Real-time emissions monitoring and optimization
- Reinforcement learning for carbon reduction
- Counterfactual scenario analysis
- **Capabilities**: CG.RS, CG.DC, LA.RL, GS.MO

### Demo 2: GridMind AI (T4 Multi-Agent System)
- 5-agent coordination for renewable energy plant
- Weather, demand, storage, trading, and maintenance agents
- Consensus protocols and distributed coordination
- **Capabilities**: IC.DS, IC.CF, IC.CS, LA.MM

### Demo 3: Safety Guardian (T2 Procedural Agent)
- Refinery safety monitoring and conflict detection
- Real-time gas sensor analysis
- Permit-to-work management
- **Capabilities**: PK.OB, CG.PS, IC.HL, GS.SF

### Demo 4: Mobility Maestro (T3 Cognitive Agent)
- EV charging network optimization
- Multi-criteria site evaluation
- Financial modeling and ROI analysis
- **Capabilities**: CG.PS, CG.DC, AE.TL, LA.SL

### Demo 5: Engineer's Copilot (T2 Generative Agent)
- R&D research assistant for TCAP Mumbai
- Formulation recommendations
- Test protocol generation
- Bilingual support (English/Hindi)
- **Capabilities**: PK.KB, CG.RS, AE.CX, IC.NL

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip
- virtualenv (recommended)

### Installation

```bash
# 1. Clone repository
git clone 
cd agentic-canvas

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 5. Initialize database
python scripts/init_db.py

# 6. Seed with demo data
python scripts/seed_db.py

# 7. Run application
python run.py
```

### Access the Application

Open your browser and navigate to:
```
http://localhost:5002
```

**Default Login Credentials:**
- Username: `demo`
- Password: `demo`

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at http://localhost:5000
```

## 📊 Architecture

```
agentic-canvas/
├── app/
│   ├── agents/          # AI agent implementations
│   ├── blueprints/      # Flask routes
│   ├── core/            # Core services
│   ├── models/          # Database models
│   ├── static/          # CSS, JS, images
│   └── templates/       # HTML templates
├── data/                # SQLite database
├── logs/                # Application logs
├── scripts/             # Utility scripts
└── run.py              # Application entry point
```

## 🛠️ Technology Stack

- **Backend**: Flask 3.0, SQLAlchemy
- **Frontend**: Bootstrap 5, Chart.js
- **Real-time**: Socket.IO
- **AI/ML**: OpenAI GPT-4, Custom agents
- **Database**: SQLite (development), PostgreSQL (production-ready)

## 📖 Usage

### Demo Navigation
1. Log in with provided credentials
2. Select a demo from the home page
3. Each demo has its own dashboard with:
   - Real-time metrics
   - AI agent controls
   - Data visualizations
   - Action history

### API Endpoints
Each demo exposes REST APIs:
- `/demo1/api/*` - Carbon Compass
- `/demo2/api/*` - GridMind AI
- `/demo3/api/*` - Safety Guardian
- `/demo4/api/*` - Mobility Maestro
- `/demo5/api/*` - Engineer's Copilot

## 🔧 Configuration

Edit `app/config.py` to customize:
- Database settings
- OpenAI API configuration
- Demo-specific parameters
- Simulation intervals

## 🙏 Credits

**Framework**: AI Agent Capabilities Periodic Table (AIA CPT) by Digital Twin Consortium 
**Version**: 1.0.0

---

**Ready to demonstrate the future of Industrial AI! 🚀**