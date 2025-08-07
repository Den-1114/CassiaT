# CassiaT

**CassiaT** is a modular, Python-based project for automating intelligent agents and running automated workflows. Designed with flexibility and experimentation in mind, it supports agent-based operations powered by configurable environments.

## ✨ Features

- Clean, extensible architecture
- Config-driven execution (`configs/`)
- Agent behavior modularity
- Integrated testing utilities
- Ideal foundation for automation or AI experiments

## 🚀 Getting Started

Clone the repository:

```bash
git clone https://github.com/Den-1114/CassiaT.git
cd CassiaT
```

### 📦 Prerequisites

- Python **3.13+**
- `pip` (Python package installer)

Install dependencies in **editable mode**:

```bash
pip install -e .
```

### 🔐 Environment Variables

1. Navigate to the `configs/` directory.
2. Rename `.env.example` to `.env`.
3. Replace the value of `OPENAI_API_KEY` with your actual API key.

### ▶️ Run the App

```bash
python main.py
```

## 🗂 Project Structure

```
CassiaT/
├── agent/           # Core agent logic
├── configs/         # Configuration and .env files
├── main.py          # Main entry point
├── testing.py       # Testing utilities
├── requirements.txt # Python dependencies
├── pyproject.toml   # Project metadata
```

## 🪪 License

CassiaT is licensed under the [MIT License](LICENSE).
