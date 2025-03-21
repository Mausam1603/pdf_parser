import fitz  # PyMuPDF
import re
import logging

logging.basicConfig(level=logging.INFO)

def extract_tasks_from_pdf(pdf_path: str) -> dict:
    doc = fitz.open(pdf_path)
    tasks = []
    seen_task_numbers = set()

    task_pattern = re.compile(r"(Task\s+(\d{1,2}\.\d{1,2}))", re.IGNORECASE)
    field_patterns = {
        "personnel_required": re.compile(r"Personnel\s+required\s+to\s+perform\s+work:\s*(.*)", re.IGNORECASE),
        "energy_isolation": re.compile(r"Energy\s+Isolation:\s*(.*)", re.IGNORECASE),
        "time_required": re.compile(r"Time\s+Required:\s*(.*)", re.IGNORECASE),
        "consumables": re.compile(r"Consumables:\s*(.*)", re.IGNORECASE),
        "tools_required": re.compile(r"Tools\s+Required:\s*(.*)", re.IGNORECASE),
        "summary": re.compile(r"Summary:\s*(.*)", re.IGNORECASE),
    }

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text = page.get_text()

        task_splits = task_pattern.split(text)

        if len(task_splits) < 3:
            logging.info(f"[SKIP] No tasks found on page {page_num + 1}")
            continue

        for i in range(1, len(task_splits), 3):
            task_number_full = task_splits[i].strip()  # E.g. Task 1.01
            task_number_match = re.search(r"(\d{1,2}\.\d{1,2})", task_number_full)

            if not task_number_match:
                logging.warning(f"[SKIP] No valid task number found in: '{task_number_full}'")
                continue

            task_number = task_number_match.group(1)

            if task_number in seen_task_numbers:
                logging.info(f"[DUPLICATE] Skipping duplicate task {task_number}")
                continue
            seen_task_numbers.add(task_number)

            task_title_and_details = task_splits[i + 2].strip()

            first_line_end = task_title_and_details.find("\n")
            task_title = (
                task_title_and_details[:first_line_end].strip()
                if first_line_end != -1
                else task_title_and_details
            )

            details_text = task_title_and_details[first_line_end:].strip() if first_line_end != -1 else ""

            details = {}
            for field, pattern in field_patterns.items():
                match = pattern.search(details_text)
                details[field] = match.group(1).strip() if match else ""

            task_obj = {
                "task_number": task_number,
                "task_title": task_title,
                "details": details
            }

            tasks.append(task_obj)
            logging.info(f"[EXTRACTED] Task {task_number} - {task_title}")

    return {"tasks": tasks}
