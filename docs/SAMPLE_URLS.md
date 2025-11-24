# Sample Earnings Call Transcript URLs for Testing QuickBrief AI

## How to Use:
1. Copy any URL below
2. Open http://localhost:5001 in your browser
3. Paste the URL in the input box
4. Click "Analyze" button
5. Wait 20-40 seconds for AI analysis
6. View your results!

## Recent Earnings Call Transcripts:

### 🚀 Technology Giants:

**NVIDIA (NVDA):**
https://www.fool.com/earnings/call-transcripts/2025/11/19/nvidia-nvda-q3-2026-earnings-call-transcript/

**Apple (AAPL):**
https://www.fool.com/earnings/call-transcripts/2025/10/31/apple-q4-2025-earnings-call-transcript/

**Alphabet (GOOG):**
https://www.fool.com/earnings/call-transcripts/2025/10/30/alphabet-goog-q3-2025-earnings-call-transcript/

**Microsoft (MSFT):**
https://www.fool.com/earnings/call-transcripts/2025/10/29/microsoft-msft-q1-2026-earnings-call-transcript/

**Amazon (AMZN):**
https://www.fool.com/earnings/call-transcripts/2025/10/31/amazon-amzn-q3-2025-earnings-call-transcript/

**Meta Platforms (META):**
https://www.fool.com/earnings/call-transcripts/2025/10/29/meta-platforms-meta-q3-2025-earnings-call-transcript/

### 🏢 Business Services:

**Maximus (MMS):**
https://www.fool.com/earnings/call-transcripts/2025/11/20/maximus-mms-q4-2025-earnings-call-transcript/

### 🍔 Food & Beverage:

**Jack in the Box (JACK):**
https://www.fool.com/earnings/call-transcripts/2025/11/20/jack-in-the-box-jack-q4-2025-earnings-transcript/

**J&J Snack Foods (JJSF):**
https://www.fool.com/earnings/call-transcripts/2025/11/17/jj-snack-foods-jjsf-q4-2025-earnings-transcript/

### 🚢 Maritime & Logistics:

**Navios Maritime (NMM):**
https://www.fool.com/earnings/call-transcripts/2025/11/18/navios-nmm-earnings-call-transcript/

---

## Quick Test URL (Recommended):
Start with this one to test the application:

https://www.fool.com/earnings/call-transcripts/2025/11/19/nvidia-nvda-q3-2026-earnings-call-transcript/

---

## Tips:
- Each analysis takes 20-40 seconds
- Make sure your internet connection is stable
- The application works best with full transcript URLs (not listing pages)
- You can find more transcripts at: https://www.fool.com/earnings/call-transcripts/

---

## ⚠️ Common Error: "npm run dev"

### Error Message:
```
npm error code ENOENT
npm error syscall open
npm error path D:\QuickBrief AI\package.json
npm error errno -4058
npm error enoent Could not read package.json
```

### Why This Happens:
**QuickBrief AI is a Python/Flask application, NOT a Node.js/npm project!**

- ❌ **Don't use:** `npm run dev`
- ✅ **Use instead:** `python app.py`

### Correct Commands:

```bash
# To run the application:
python app.py

# To run tests:
python run_all_tests.py

# To install dependencies:
pip install -r requirements.txt
```

### Explanation:
- **npm** is for Node.js/JavaScript projects
- **pip** is for Python projects
- This project uses **Python + Flask**, not Node.js
- There is no `package.json` file because we don't need npm

### Quick Reference:

| Task | Wrong Command | Correct Command |
|------|---------------|-----------------|
| Run app | `npm run dev` ❌ | `python app.py` ✅ |
| Install | `npm install` ❌ | `pip install -r requirements.txt` ✅ |
| Test | `npm test` ❌ | `python run_all_tests.py` ✅ |
