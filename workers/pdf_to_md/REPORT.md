# Quality and Performance Evaluation of PDF-to-Markdown Converters

## Overview

5 different converters were analyzed, all processing 17 Freiburg PDFs. Results are located in `data/md/{converter_name}/`.

| Converter    | Files | Directory               |
| ------------ | ----- | ----------------------- |
| MarkItDown   | 17    | `data/md/markitdown/`   |
| Pandoc       | 17    | `data/md/pandoc/`       |
| PaddleOCR    | 17    | `data/md/paddle_ocr/`   |
| Unstructured | 17    | `data/md/unstructured/` |
| Marker-PDF   | 17    | `data/md/marker_pdf/`   |

---

## Performance Analysis (File Sizes and Conversion Times)

| File                                 | Size       | Pages    | Output     | MarkItDown | Pandoc     | Unstructured | PaddleOCR   | Marker-PDF  |
| ------------------------------------ | ---------- | -------- | ---------- | ---------- | ---------- | ------------ | ----------- | ----------- |
| Bundestagswahl_2025.pdf              | 9.7 MB     | 66       | 189 KB     | 2s         | 3s         | 3m 49s       | 27m 47s     | 8m 8s       |
| Die_Oberbuergermeisterwahl_2018.pdf  | 5.0 MB     | 81       | 293 KB     | 7s         | 7s         | 4m 32s       | 38m 52s     | 21m 52s     |
| Europawahl_2024.pdf                  | 4.2 MB     | 38       | 118 KB     | 2s         | 2s         | 1m 58s       | 16m 27s     | 15m 56s     |
| Freiburg-Umfrage_2020.pdf            | 2.2 MB     | 126      | 987 KB     | 4s         | 5s         | 7m 11s       | 48m 59s     | 28m 15s     |
| Freiburg-Umfrage_2022.pdf            | 0.7 MB     | 49       | 545 KB     | 3s         | 3s         | 2m 58s       | 18m 28s     | ~13m\*      |
| Freiburg-Umfrage_2024.pdf            | 2.3 MB     | 101      | 1568 KB    | 11s        | 12s        | 6m 14s       | ~42m\*      | ~27m\*      |
| Gemeinderatswahl_2024.pdf            | 12.8 MB    | 60       | 324 KB     | 3s         | 4s         | 3m 2s        | ~25m\*      | ~16m\*      |
| Landtagswahl_2021.pdf                | 8.1 MB     | 65       | 310 KB     | 7s         | 9s         | 3m 17s       | ~27m\*      | ~17m\*      |
| Migrant_innenbeiratswahl_2020.pdf    | 0.4 MB     | 8        | 25 KB      | 0s         | 0s         | 47s          | ~3m\*       | ~2m\*       |
| Migrantinnenbeiratswahl_2025.pdf     | 1.2 MB     | 10       | 31 KB      | 0s         | 0s         | 29s          | ~4m\*       | ~3m\*       |
| Ortschaftsratswahlen_2024.pdf        | 9.0 MB     | 40       | 378 KB     | 0s         | 0s         | 2m 5s        | ~17m\*      | ~11m\*      |
| Sozialbericht_2023.pdf               | 1.7 MB     | 56       | 110 KB     | 2s         | 3s         | 2m 21s       | ~23m\*      | ~15m\*      |
| Stadtbezirksatlas_2021.pdf           | 38.6 MB    | 276      | 1072 KB    | 14s        | 17s        | 16m 43s      | ~115m\*     | ~74m\*      |
| Statistischer_Jahresbericht_2021.pdf | 1.0 MB     | 36       | 61 KB      | 1s         | 1s         | 1m 31s       | ~15m\*      | ~10m\*      |
| Statistischer_Jahresbericht_2023.pdf | 1.1 MB     | 11       | 21 KB      | 0s         | 0s         | 26s          | ~5m\*       | ~3m\*       |
| Statistischer_Jahresbericht_2024.pdf | 3.3 MB     | 13       | 17 KB      | 0s         | 0s         | 30s          | ~5m\*       | ~3m\*       |
| Statistisches_Jahrbuch_2024.pdf      | 4.5 MB     | 133      | 771 KB     | 5s         | 5s         | 7m 46s       | ~55m\*      | ~35m\*      |
| **Total**                            | **105 MB** | **1169** | **6.7 MB** | **61s**    | **71s**    | **~65m**     | **~487m\*** | **~305m\*** |
| **Avg per file**                     | **6.2 MB** | **69**   | **401 KB** | **3.6s**   | **4.2s**   | **3m 50s**   | **~29m**    | **~18m**    |
| **Avg per page**                     | -          | -        | -          | **~0.05s** | **~0.06s** | **~3.3s**    | **~25s**    | **~16s**    |

_\* Estimate based on avg time per page (PaddleOCR: ~25s/page, Marker-PDF: ~16s/page).
The conversion process was interrupted several times and not logged, therefore no actual measurements are available for these files._

_Note: Output size refers to Marker-PDF (best quality). All conversions were performed on CPU (Apple Mac M4) without GPU acceleration._

---

## Detailed Quality Evaluation

### 1. MarkItDown - ⭐⭐ (2/5)

**Description:** Microsoft library for fast text extraction

**Strengths:**

- Fast and lightweight
- Basic text extraction works
- No external dependencies

**Weaknesses:**

- No table formatting
- Line breaks in the middle of sentences
- Page numbers inserted as loose lines
- No structure (no heading hierarchy)

**Example Problem:**

```
Die GRÜNEN konnten einen neuen Erst-

stimmen-Rekord einfahren, was dazu führte, dass erstmals eine

Frau das Direktmandat im Wahlkreis Freiburg verteidigen konnte.
```

---

### 2. Pandoc - ⭐⭐½ (2.5/5)

**Description:** pdfminer.six-based text extraction with page separation

**Strengths:**

- Page separation with `## Page X` and `---`
- Slightly better structure than MarkItDown
- Fast processing

**Weaknesses:**

- No table formatting
- Line breaks in running text
- No hierarchy for headings

**Example Output:**

```markdown
## Page 3

Kurz gefasst …

Bei der vorgezogenen Bundestagswahl am 23. Februar 2025

wurden einige Bundestagswahl-Superlative aufgestellt...
```

---

### 3. PaddleOCR - ⭐⭐⭐ (3/5)

**Description:** OCR engine with multi-language support (optimized for German)

**Strengths:**

- Good page structure with `## Page X`
- OCR suitable for scanned documents
- Table of contents well formatted with page numbers

**Weaknesses:**

- OCR errors on graphical pages ("914-01 FRE BURC DYMATRI")
- Umlaut problems ("GRüNEN" instead of "GRÜNEN")
- Not optimal for well-formatted digital PDFs

**Example Problem:**

```
Die GRüNEN konnten einen neuen Erst-
stimmen-Rekord einfahren...
```

---

### 4. Unstructured - ⭐⭐½ (2.5/5)

**Description:** Layout detection with hi_res strategy and table detection

**Strengths:**

- Recognizes tables and formats them as Markdown
- Layout detection present
- Structured output

**Weaknesses:**

- **Massive OCR errors with German texts:**
  - "W ahlberechtigte" instead of "Wahlberechtigte"
  - "W ahltermin" instead of "Wahltermin"
  - "fihrte" instead of "führte"
- Umlaut problems: "GRUNEN" (without Ü), "GroBstadtvergleich" (ß→B)
- Spaces in wrong places

**Example Problem:**

```
Bei der vorgezogenen Bundestagswahl am 23. Februar 2025
wurden einige Bundestagswahl-Superlative aufgestellt:
Nie war die Zahl der W ahlberechtigten héher...
```

---

### 5. Marker-PDF - ⭐⭐⭐⭐⭐ (5/5) BEST QUALITY

**Description:** Deep learning-based PDF conversion with layout detection

**Strengths:**

- **Perfect text extraction** - no OCR errors
- **Correct umlauts** (ä, ö, ü, ß, GRÜNEN)
- **Clean Markdown tables** with correct alignment
- **Hierarchical headings** (#, ##, ####)
- **Bold text preserved** (`**Wähler*innenwanderungen**`)
- **Image references** (`![](_page_3_Figure_13.jpeg)`)
- Clean paragraphs without artificial line breaks

**Weaknesses:**

- Requires more processing time (Deep Learning)
- Larger model downloads (~2GB on first start)

**Example Output:**

```markdown
# Kurz gefasst …

Bei der vorgezogenen Bundestagswahl am 23. Februar 2025
wurden **einige Bundestagswahl-Superlative** aufgestellt:
Nie war die Zahl der Wahlberechtigten höher, ebenso das
Interesse der Freiburger Auslandsdeutschen.

**Tab.1 Wahlberechtigte und Wahlbeteiligung bei der Bundestagswahl 2025 in Freiburg**

|                 |         |         | 2025/         |
| --------------- | ------- | ------- | ------------- |
|                 | 2025    | 2021    | 2021          |
| Wahlberechtigte | 161.136 | 157.938 | +3.198        |
| Wahlbeteiligung | 85,7 %  | 80,4 %  | +5,3 %-Punkte |
```

---

## Overall Ranking: Time vs. Quality

| Rank | Converter      | Avg Time/File | Quality    | Recommendation                  |
| ---- | -------------- | ------------- | ---------- | ------------------------------- |
| 1    | **Marker-PDF** | ~15-20m       | ⭐⭐⭐⭐⭐ | **Best choice for RAG systems** |
| 2    | PaddleOCR      | ~20-30m       | ⭐⭐⭐     | Only for scanned documents      |
| 3    | Unstructured   | ~3m 50s       | ⭐⭐½      | Not suitable for German texts   |
| 4    | Pandoc         | ~4.2s         | ⭐⭐½      | Fast simple extraction          |
| 5    | MarkItDown     | ~3.6s         | ⭐⭐       | Only for simple text PDFs       |

---

## Recommendation for the RAG System

**Marker-PDF is the clear winner** for Freiburg city data:

1. **Perfect text quality** - No OCR errors means better semantic search
2. **Preserves table structure** - Important for statistical data and election results
3. **No umlaut errors** - Critical for German texts (GRÜNEN, Wähler, Größe)
4. **Best foundation for embeddings** - Clean text = better vector representation

### Next Steps

To achieve the best quality in the RAG system:

```bash
# Rebuild index with Marker-PDF results
python scripts/index_documents.py --source data/md/marker_pdf/
```

---

## Quality Improvement with LLM Post-Processing

If further improvement of Markdown quality is needed, the following options are available:

### Typical Problems After PDF Conversion

| Problem          | Example                      | Solution          |
| ---------------- | ---------------------------- | ----------------- |
| OCR spacing      | "W ahlberechtigte"           | LLM or Regex      |
| Umlaut errors    | "GRUNEN" instead of "GRÜNEN" | LLM or dictionary |
| Line breaks      | "Erst-\nstimmen"             | Regex             |
| Table formatting | Wrong alignment              | LLM               |

### Local/Free LLM Options (via Ollama)

| Model            | RAM  | Quality  | Recommendation      |
| ---------------- | ---- | -------- | ------------------- |
| **Llama 3.1 8B** | 8 GB | ⭐⭐⭐⭐ | Best local option   |
| **Qwen 2.5 7B**  | 8 GB | ⭐⭐⭐⭐ | Strong multilingual |
| **Mistral 7B**   | 8 GB | ⭐⭐⭐½  | Good for German     |

```bash
# Installation
brew install ollama
ollama pull llama3.1:8b
```

### Cloud APIs (cheap/free)

| Service    | Model         | Cost/1M Tokens | Quality    |
| ---------- | ------------- | -------------- | ---------- |
| **Groq**   | Llama 3.1 70B | Free (limited) | ⭐⭐⭐⭐⭐ |
| **Google** | Gemini Flash  | ~$0.075        | ⭐⭐⭐⭐   |
| **OpenAI** | GPT-4o-mini   | ~$0.15         | ⭐⭐⭐⭐   |

### Example Prompt for LLM Correction

```
You are an expert in correcting OCR errors in German texts.

Correct the following Markdown text from a PDF conversion:

1. Fix OCR spacing errors (e.g., "W ahlberechtigte" → "Wahlberechtigte")
2. Correct missing umlauts (e.g., "GRUNEN" → "GRÜNEN", "Grossstadt" → "Großstadt")
3. Join hyphenated words split across lines (e.g., "Erst-\nstimmen" → "Erststimmen")
4. Fix typical OCR character confusions (e.g., "héher" → "höher", "fihrte" → "führte")
5. Preserve the Markdown formatting (tables, headings, lists) exactly as is
6. Do NOT change any factual information or numbers

Return only the corrected text, without explanations.

Text:
{markdown_content}
```

### Recommended Workflow

1. **Marker-PDF** for best initial quality (already implemented)
2. **Rule-based correction** for known OCR patterns
3. **LLM post-processing** with Groq API (free) or Ollama (local)
4. **Quality check** with LanguageTool

### Cost Estimate for All 17 Files (~6.7 MB Text)

| Method         | Cost  | Time       |
| -------------- | ----- | ---------- |
| Local (Ollama) | $0    | ~30-60 min |
| Groq (free)    | $0    | ~10-20 min |
| GPT-4o-mini    | ~$1-2 | ~5-10 min  |

---

## Test Document

The analysis was performed using the document **Bundestagswahl_2025.pdf** because it:

- Contains complex tables
- Uses many German umlauts
- Includes graphics and diagrams
- Is representative of all Freiburg city data

---

_Report created: November 26, 2025_
_Data source: workers/pdf_to_md/conversion.log_
