# AI Email Assistant (Proof of Concept)

## 🧠 Product Overview

A conversational AI-powered tool that generates **personalized marketing emails** from a contact list (JSON file) using pre-defined HTML templates. It uses:

- **Apollo API** for contact enrichment
- **Gemini Flash** for template selection and content generation
- **Gemini Vision** for optional image generation

Emails are generated on a **per-contact basis**, personalized using enrichment data, and rendered with a preview for the user. No database or persistence is required; the app is designed as a **stateless, Replit-deployable PoC** with optional expansion into a React frontend later.

---

## 🎯 Key Features

### Core Functionality

- Upload or load a contact list from a local JSON file
- Enrich each contact via Apollo
- Use Gemini Flash to:
  - Select the best-fit pre-generated HTML template
  - Generate subject line, preheader, body, CTA, and optional image prompt
  - Inject generated content into the selected HTML template
- Render a live preview of the final HTML email
- Show chat-style interaction log and internal agent reasoning (e.g., template selected, enrichment results)

### Constraints

- Stateless: session is ephemeral (no DB or persistent storage)
- Local JSON file for contact list
- Static HTML templates stored locally (pre-generated with example copy)
- Text + image generation via Gemini APIs

---

## 🧰 Tech Stack

### Frontend (optional)

- **Streamlit** (preferred for PoC, supports Replit)
  - `st.chat_message()` for conversation UI
  - `st.expander()` for agent thinking/debug views
  - `st.file_uploader()` for JSON file upload
  - `st.markdown()` or `st.components.v1.html()` for email preview

### Backend / Core Logic

- **Python 3.10+**
- **Gemini Flash API** (text)
- **Gemini Image API** (optional visuals)
- **Apollo API** for enrichment
- **HTML parsing/editing**: BeautifulSoup4 (to replace content in HTML templates)

### File Structure

```
ai-email-assistant/
├── app.py                   # Streamlit frontend + orchestration
├── data/
│   └── contacts.json        # Example input contact list
├── templates/
│   ├── bold_cta.html        # Static HTML templates
│   ├── simple_split.html
│   └── testimonial_layout.html
├── utils/
│   ├── apollo.py            # Enrichment logic
│   ├── gemini.py            # Text + image generation helpers
│   └── html_utils.py        # Template replacement logic
```

---

## 📄 Contact JSON Schema

```json
[
  {
    "email": "jennifer.lee@target.com",
    "first_name": "Jennifer",
    "job_title": "",
    "company": "Target",
    "industry": "Retail",
    "location": ""
  },
  ...
]
```

---

## 🔁 Step-by-Step Workflow

### 1. Load Contact List

- Accept JSON file upload via Streamlit or use a default local file
- Parse into Python dict list

### 2. Enrich Contact Data (Apollo)

- For each contact, check for missing fields (e.g., job_title, location)
- Call Apollo enrichment API (batch or per-contact)
- Inject enriched values back into contact object

### 3. Call Gemini Flash

- Input:
  - Enriched contact info
  - Summary of campaign purpose
  - All available templates (with short descriptions)
- Output:
  - Chosen template (file name or template ID)
  - Subject line
  - Preheader
  - Headline, body, CTA text
  - Optional: image prompt

### 4. Inject into Template

- Load selected HTML file from `/templates`
- Replace example content using tag matching or regex:
  - Replace `<h1>` or `<!-- HEADLINE -->` with headline
  - Replace `<!-- BODY -->` with Gemini-generated body text
  - Replace CTA and link
  - Optionally replace `<img src=...>` if image generated

### 5. Display Preview

- Render in `st.components.v1.html()` or markdown
- Allow user to:
  - Download as HTML
  - Copy raw HTML
  - Regenerate for contact
  - View "agent log" (template chosen, Gemini prompt, Apollo data used)

---

## ✅ Stretch Goals

- Image generation via Gemini Vision using body context
- Regenerate content using a different template
- Preview for multiple contacts (e.g., top 3 enriched contacts)
- Export all emails to ZIP

---

## 🛠️ Deployment Plan

- Target Replit deployment (Streamlit is supported out of the box)
- Requirements:
  - `streamlit`
  - `openai` or `google-generativeai`
  - `beautifulsoup4`
  - `requests`
- Use environment variables for API keys (Apollo, Gemini)
- Optional: switch to FastAPI if integrating with a React frontend later

---

## 🚀 Next Steps

1. Scaffold file structure and sample JSON/template files
2. Set up Gemini + Apollo key access + simple utils
3. Build Streamlit UI step-by-step
4. Test on Replit with a few contacts and templates
5. Polish the agent reasoning log and preview interface

---

Let me know if you'd like a prompt framework or code scaffolding next.
