# Molnbyte och regelverkens täckning i IaaS-avtal: en empirisk analys av hur standardvillkor tar upp dataförordningen, GDPR och NIS2

## Snabbstart

```bash
pip install -r requirements.txt
python scripts/build_reviews_db.py
streamlit run app.py
```

## 1. Konvertera dokumenten till Markdown

```bash
pip install -r requirements-ingest.txt
python scripts/ingest_documents.py
```

## 2. Slå samman varje leverantörs dokument

```bash
python scripts/combine_markdown.py
```

## 3. Rensa dokumenten

```bash
python scripts/run_cleaning.py All
```

## 4. Generera kodboken

```bash
python scripts/generate_objectives.py --regulation "EU Data Act" --list
python scripts/generate_objectives.py --regulation "EU Data Act" \
    --articles "Article 13" "Article 23" "Article 25" "Article 26" "Article 27" "Article 28" \
               "Article 29" "Article 30" "Article 31" "Article 32" "Article 34" \
    --draft output/objective_drafts/eu_data_act_clean.json
```

## 5. Granska kodboken

```bash
streamlit run app.py
```

## 6. Godkänn kodboken

```bash
python scripts/approve_objectives.py output/objective_drafts/eu_data_act_clean.json
```

## 7. Koda varje leverantör mot varje objektiv

```bash
python scripts/run_audit.py --regulation GDPR --estimate-only
python scripts/run_audit.py --regulation GDPR --providers all --objectives all \
    --draft output/audit_drafts/gdpr_audit.json
```

## 8. Granska kodningen

```bash
streamlit run app.py
```

## 9. Godkänn kodningen

```bash
python scripts/approve_audit.py output/audit_drafts/gdpr_audit.json
```

## 10. Bygg databasen

```bash
python scripts/build_reviews_db.py
```
