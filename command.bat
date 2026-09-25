@REM git clone https://github.com/VinUni-AI20k/K4-L3B-RAG-Pipeline.git
cd K4-L3B-RAG-Pipeline
py -m venv .venv
call .venv/scripts/activate
py -m pip install --upgrade pip setuptools wheel
py -m pip install -r requirements.txt
py -m playwright install chromium
copy .env.example .env