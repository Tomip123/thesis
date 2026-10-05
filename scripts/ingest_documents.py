#!/usr/bin/env python3
import logging
import os
import re
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

from docling_core.types.doc import ImageRefMode
from docling.backend.docling_parse_v4_backend import DoclingParseV4DocumentBackend
from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

log = logging.getLogger(__name__)

_ROOT = Path(__file__).resolve().parents[1]

def build_converter() -> DocumentConverter:
    pipeline_options = PdfPipelineOptions()
    
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    
    if hasattr(pipeline_options, "ocr"):
        pipeline_options.ocr.enabled = True
        pipeline_options.ocr.force_ocr = True
        pipeline_options.ocr.engine = "auto"
    
    if hasattr(pipeline_options, "tables"):
        pipeline_options.tables.mode = "accurate"

    if hasattr(pipeline_options, "enrichment"):
        pipeline_options.enrichment.enable_code = True
        pipeline_options.enrichment.enable_formula = True

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
                backend=DoclingParseV4DocumentBackend,
            )
        }
    )

def safe_filename_from_url(url: str) -> str:
    clean = re.sub(r'https?://', '', url)
    clean = re.sub(r'[^a-zA-Z0-9]', '_', clean).strip('_')
    return clean[:100]

def _process_item(item_source: str, output_dir_str: str, is_pdf: bool):
    try:
        source_name = Path(item_source).name if is_pdf else item_source
        output_dir = Path(output_dir_str)
        output_dir.mkdir(parents=True, exist_ok=True)

        if is_pdf:
            md_path = output_dir / f"{Path(item_source).stem}.md"
        else:
            md_path = output_dir / f"{safe_filename_from_url(item_source)}.md"

        if md_path.exists():
            return {"source": source_name, "status": "SKIPPED", "md": str(md_path)}

        converter = build_converter()
        
        res = converter.convert(item_source, raises_on_error=False)

        if res.status in (ConversionStatus.SUCCESS, ConversionStatus.PARTIAL_SUCCESS):
            res.document.save_as_markdown(md_path, image_mode=ImageRefMode.PLACEHOLDER)
            return {
                "source": source_name,
                "status": res.status.name,
                "md": str(md_path),
                "errors": [e.error_message for e in getattr(res, "errors", [])],
            }
        else:
            return {"source": source_name, "status": "FAILED", "error": "Conversion status unsuccessful"}

    except Exception as e:
        return {"source": item_source, "status": "FAILED", "error": str(e)}

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    root_dir = _ROOT / "data"
    
    tasks = []
    
    for subdir in root_dir.rglob("*"):
        if not subdir.is_dir() or subdir.name == "md":
            continue
            
        md_output_dir = subdir / "md"
        
        for pdf_file in subdir.glob("*.pdf"):
            tasks.append((str(pdf_file), str(md_output_dir), True))
            
        url_file = subdir / "url.txt"
        if url_file.exists():
            with open(url_file, "r", encoding="utf-8") as f:
                for line in f:
                    url = line.strip()
                    if url and not url.startswith("#"):
                        tasks.append((url, str(md_output_dir), False))

    if not tasks:
        log.info("No PDFs or url.txt files found.")
        return

    log.info("Found %d items to process.", len(tasks))
    max_workers = min(os.cpu_count() or 1, len(tasks))
    
    converted, partial, failed, skipped = 0, 0, 0, 0

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_process_item, src, out, is_pdf): src for src, out, is_pdf in tasks}
        
        for i, future in enumerate(as_completed(futures), start=1):
            result = future.result()
            prefix = f"[{i}/{len(tasks)}]"
            status = result["status"]
            source = result["source"]

            if status == "SUCCESS":
                converted += 1
                log.info("%s Processed: %s", prefix, source)
            elif status == "PARTIAL_SUCCESS":
                partial += 1
                log.warning("%s Partially Processed: %s", prefix, source)
            elif status == "SKIPPED":
                skipped += 1
                log.info("%s Skipped (exists): %s", prefix, source)
            else:
                failed += 1
                log.error("%s Failed: %s | Reason: %s", prefix, source, result.get("error"))

    log.info(
        "\nSummary: %d converted, %d partially converted, %d failed, %d skipped.",
        converted, partial, failed, skipped
    )

if __name__ == "__main__":
    main()