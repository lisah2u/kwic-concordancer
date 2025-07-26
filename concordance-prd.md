We are building a **classroom-friendly, linguist-powered concordancer** with a clean UX — and room for cool NLP enhancements down the road. 

✅ Start simple (exact match + static corpora)  prototype on macbook
✅ **NEW**: Add file viewing and in-file search capabilities with streamlined workflow
✅ **UX Enhancement**: Simplified single-workflow interface (Select → View → Search)
✅ Expand NLP depth: spaCy, lemmatization, regex, and BPE viz after basic functionality is good.
✅ Migrate to modern, scalable tech (FastAPI + Tailwind + Netlify/Vercel)
✅ Stay UX-first — and pedagogy-focused

---

## 🏗️ Technical Architecture (v1.2 Enhanced)

### 🧠 Backend (Python + FastAPI)

* **Load corpora**: static `.txt` files → tokenized per line. Located in the samples directory.
* **Search endpoint**: `/search?corpus=X&query=Y` (KWIC concordance)
* **File viewing endpoint**: `/view/{corpus}` (full file content with metadata)
* **In-file search endpoint**: `/search-in-file/{corpus}?query=X&case_sensitive=bool`
* **Output formats**: 
  - KWIC hits → `{ left: [...], match: [...], right: [...] }`
  - File content → `{ filename, content, line_count, word_count, char_count }`
  - In-file search → `{ query, results: [{ line_number, content, matches }] }`
* **Lemmatization placeholder**: add a `spacy_model` import + `Doc` prep, even if unused at first
* **Typed functions** + **pytest unit tests** (22 tests covering all endpoints)

### 🧰 Libraries

* `fastapi` (with static file serving)
* `spacy` (start with `en_core_web_sm`)
* `pydantic` (request/response models)
* `pytest` (comprehensive testing)
* `httpx` (test client)
* `uvicorn` (ASGI server)
* Optional for later: `tokenizers` (HuggingFace BPE/WordPiece)

### 🖥️ Frontend (Static Files via FastAPI Static Mount)

* **Tailwind CSS** for layout + highlighting
* **Streamlined Workflow**: 
  - **Step 1**: Select corpus from dropdown
  - **Step 2**: View file content with metadata
  - **Step 3**: Search within file (replaces file view)
  - **Clear**: Return to file view from search results
* **Vanilla JS** for:
  - Single-workflow state management
  - Fetching file content and search results
  - File viewer with line numbers and syntax highlighting
  - In-file search with result highlighting
  - Real-time file metadata display (lines, words, characters)
  - Dynamic UI showing/hiding based on current step
* **Responsive Design**: Mobile-friendly interface with clean, intuitive UX
* Optional enhancement: tooltips with `title` attribute to show token details (lemma, POS, BPE)

---

## ✅ Completed Features (v1.2)

### 📄 File Viewing & Analysis
* **Complete File Display**: View full corpus files with monospace formatting and line numbers
* **File Metadata**: Real-time statistics (line count, word count, character count)
* **Scrollable Interface**: Clean presentation with max-height scrolling for large files
* **Professional Styling**: Code editor-style presentation with proper syntax highlighting

### 🔍 In-File Search Capabilities
* **Full-Text Search**: Search for terms within specific corpus files
* **Case Sensitivity Control**: Toggle between case-sensitive and case-insensitive search
* **KWIC Format Results**: Traditional three-column concordance display (left context | match | right context)
* **Proper Text Justification**: Left context right-aligned, match centered, right context left-aligned
* **Configurable Context**: 5-word context window around search terms
* **Search Statistics**: Total lines matched and total match count display
* **Regex-Safe**: Properly escaped search terms prevent regex injection

### 🎨 Enhanced User Interface
* **Streamlined Workflow**: Intuitive single-path navigation (Select → View → Search)
* **Progressive Disclosure**: UI elements appear as needed, reducing cognitive load
* **Responsive Design**: Works seamlessly on desktop and mobile devices
* **State Management**: Smart enabling/disabling of buttons based on current step
* **Error Handling**: User-friendly error messages and validation
* **Accessibility**: Keyboard navigation and screen reader friendly

### 🧪 Comprehensive Testing
* **22 Test Cases**: Full coverage of all endpoints and functionality
* **Integration Tests**: End-to-end testing of file viewing and search
* **Edge Case Handling**: Validation of error conditions and boundary cases
* **Temporary File Testing**: Safe test isolation with cleanup

---

## 🧪 Future Enhancements Roadmap

### 🔍 Search Enhancements (v1.5+)

* ✅ Exact match (v1)
* ✅ Case toggle (v1.2 - implemented in file search)
* 🔄 Case toggle for KWIC search (pending)
* 🔠 Whole word match (with `\b` regex logic)
* 🧬 Regex (user toggle)
* 🧠 Lemmatized search (`Doc` + lemma lookup via spaCy)

```python
# Example: Lemmatized match
if lemma_match:
    query_lemma = nlp(query)[0].lemma_
    if query_lemma in [token.lemma_ for token in doc]:
        # include in results
```

---

### 🧠 NLP Attributes (v2)

* Add option to display part-of-speech tags (POS)
* Add `Doc.to_json()` dump per line — store POS, lemma, tag, etc.
* Frontend toggle: show POS/lemma as subscript or tooltip

---

### 🔍 Tokenization Visualization (v2.5)

* Use HuggingFace's `tokenizers` library for BPE
* In the result table, color or box subword tokens (esp. for multi-token words)

```js
// Pseudocode JS idea for frontend
renderMatchToken(token) {
  if (token.is_subword) {
    return <span class="text-purple-500">{token.text}</span>
  } else {
    return <span>{token.text}</span>
  }
}
```

---

### 🌐 Deployment & Hosting

* **Vercel/Netlify**: host static frontend
* **Backend**: Deploy FastAPI as separate service (e.g., `Fly.io`, `Render`, or `Railway`)
* Use CORS-friendly setup from FastAPI → frontend fetches from `/api/search`




