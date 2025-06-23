# ✉️ AI-Powered Cover Letter Generator

A command-line tool that generates tailored cover letters using your resume, job descriptions, and preferred tone. Built with Anthropic's Claude LLM and LangGraph for stateful generation workflows.

## 🚀 Features

- 🔁 **State Machine Logic** – Built with LangGraph to manage multi-step workflows such as resume parsing, job description ingestion, tone setting, generation, validation, and export.
- 🤖 **Claude LLM Integration** – Uses `claude-3-opus-20240229` for high-quality, context-aware writing.
- ⚙️ **Customizable Inputs** – Specify resume, job description, and desired tone via command-line arguments.
- 🧠 **Structured State Tracking** – Manages each stage of generation using Python's `TypedDict` for clean, explicit data modeling.
- 💡 **Easily Extendable** – Add validation steps, tone presets, or web frontends as needed.

## 🧰 Tech Stack

- Python 3.10+
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [Anthropic API](https://docs.anthropic.com/)
- `argparse`, `os`, `json`, `typing`

## 📦 Installation

```bash
git clone https://github.com/yourusername/cover-letter-generator.git
cd cover-letter-generator
pip install -r requirements.txt
