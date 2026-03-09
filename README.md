# AI Trading Agent App

This project is a Streamlit web app that analyzes a stock watchlist and provides simple BUY / SELL / HOLD recommendations.

## Do I need to download files locally?

Yes, if you want to run it on your own computer, you need a local copy of this project folder.

If using Git:

```bash
git clone <your-repo-url>
cd my-todo-app
```

If using ZIP download:

1. Download the project ZIP.
2. Extract it.
3. Open terminal in the extracted `my-todo-app` folder.

## Quick Start

1. Open a terminal **inside this folder**.
2. Verify `run.sh` exists:

   ```bash
   ls
   ```

   You should see `run.sh`, `web.py`, and `requirements.txt`.

3. Install packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Start with one command:

   ```bash
   bash run.sh
   ```

5. Open your browser at:

   - Local machine: `http://localhost:8501`
   - Remote/dev container: use the forwarded URL for port `8501`.

## Fix: `bash run.sh` says "No such file or directory"

This almost always means your terminal is not in the project folder.

Try:

```bash
cd /full/path/to/my-todo-app
ls
bash ./run.sh
```

If `run.sh` still does not appear in `ls`, you are in the wrong directory.

## Alternative start command (without `run.sh`)

```bash
streamlit run web.py
```

## If the page still looks blank

- Make sure you click **Run AI Scan**.
- Confirm your symbols are comma-separated (example: `AAPL,MSFT,NVDA`).
- If market data is blocked by network policy, the app shows an error message instead of results.

## What you should see

After clicking **Run AI Scan**, the app shows:

- Stock Name
- Symbol
- Signal (BUY / SELL / HOLD)
- Price
- Analysis
- Reason
- Alerts section

## Downloadable bundle

You can generate one ZIP file with all app files:

```bash
bash export_bundle.sh
```

This creates:

- `ai-trading-agent-bundle.zip`

You can then share or download that ZIP file.

