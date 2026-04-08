import os
import json
import sys
from pathlib import Path

def check_file_exists(base_path, pattern):
    """Check if a file matching pattern exists in base_path"""
    path = Path(base_path)
    if not path.exists():
        return False, f"Directory {base_path} does not exist"

    matches = list(path.glob(pattern))
    if matches:
        return True, f"Found: {matches[0]}"
    return False, f"No file matching '{pattern}' found in {base_path}"

def check_file_contains(file_path, search_term, description=""):
    """Check if file contains specific content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_term in content or search_term.lower() in content.lower():
                return True, f"Found '{search_term}' in file"
            return False, f"'{search_term}' not found in file"
    except Exception as e:
        return False, f"Error reading file: {str(e)}"

def grade_eval_1(outputs_dir):
    """Grade meeting preparation eval"""
    results = []
    english_dir = Path(outputs_dir) / "English"

    # Check 1: Meeting file exists
    meeting_dir = english_dir / "meeting"
    passed, evidence = check_file_exists(meeting_dir, "*.md")
    results.append({
        "text": "Creates a meeting preparation file in English/meeting/ folder with date and topic in filename",
        "passed": passed,
        "evidence": evidence
    })

    if passed:
        meeting_file = list(meeting_dir.glob("*.md"))[0]

        # Check 2: Speaking script section
        passed, evidence = check_file_contains(meeting_file, "Speaking Script")
        results.append({
            "text": "Meeting file contains a complete speaking script section with conversational English",
            "passed": passed,
            "evidence": evidence
        })

        # Check 3: Learning notes
        passed, evidence = check_file_contains(meeting_file, "Learning Notes")
        results.append({
            "text": "Meeting file has a Learning Notes section with vocabulary and expressions",
            "passed": passed,
            "evidence": evidence
        })

        # Check 6: Covers all content
        with open(meeting_file, 'r', encoding='utf-8') as f:
            content = f.read()
            has_foundation = any(term in content.lower() for term in ["foundation", "infrastructure", "architecture"])
            has_prompt = "prompt engineering" in content.lower()
            has_testing = "user testing" in content.lower() or "testing" in content.lower()
            has_accuracy = "accuracy" in content.lower() and ("82" in content or "65" in content)
            has_response_time = "response time" in content.lower() and "40" in content

            all_covered = has_foundation and has_prompt and has_testing and has_accuracy and has_response_time
            missing = []
            if not has_foundation: missing.append("foundation/infrastructure")
            if not has_prompt: missing.append("prompt engineering")
            if not has_testing: missing.append("user testing")
            if not has_accuracy: missing.append("accuracy metric")
            if not has_response_time: missing.append("response time metric")

            evidence = "All points covered" if all_covered else f"Missing: {', '.join(missing)}"
            results.append({
                "text": "Speaking script covers all required points: foundation architecture, prompt engineering, user testing plan, and both KPI metrics",
                "passed": all_covered,
                "evidence": evidence
            })
    else:
        # Add placeholders for remaining checks
        for desc in [
            "Meeting file contains a complete speaking script section with conversational English",
            "Meeting file has a Learning Notes section with vocabulary and expressions",
            "Speaking script covers all required points"
        ]:
            results.append({"text": desc, "passed": False, "evidence": "Meeting file not found"})

    # Check 4: vocabulary.md exists
    vocab_file = english_dir / "vocabulary.md"
    passed = vocab_file.exists()
    results.append({
        "text": "Creates or updates vocabulary.md with new technical/meeting terms",
        "passed": passed,
        "evidence": f"vocabulary.md {'found' if passed else 'not found'}"
    })

    # Check 5: expressions.md exists
    expr_file = english_dir / "expressions.md"
    passed = expr_file.exists()
    results.append({
        "text": "Creates or updates expressions.md with meeting expression patterns",
        "passed": passed,
        "evidence": f"expressions.md {'found' if passed else 'not found'}"
    })

    return results

def grade_eval_2(outputs_dir):
    """Grade tech vocabulary extraction eval"""
    results = []
    english_dir = Path(outputs_dir) / "English"

    # Check 1: Daily log exists
    daily_dir = english_dir / "daily"
    passed, evidence = check_file_exists(daily_dir, "*.md")
    results.append({
        "text": "Creates a daily log file in English/daily/ with today's date",
        "passed": passed,
        "evidence": evidence
    })

    if passed:
        daily_file = list(daily_dir.glob("*.md"))[0]

        # Check 2: Explains incremental rollout
        with open(daily_file, 'r', encoding='utf-8') as f:
            content = f.read()
            has_chinese = any(char >= '\u4e00' and char <= '\u9fff' for char in content)
            has_incremental = "incremental" in content.lower() and "rollout" in content.lower()
            passed = has_chinese and has_incremental
            results.append({
                "text": "Provides clear explanation of 'incremental rollout' in Chinese",
                "passed": passed,
                "evidence": "Has Chinese explanation" if passed else "Missing Chinese explanation or key terms"
            })

        # Check 3: Vocabulary table
        passed = "pronunciation" in content.lower() and "meaning" in content.lower()
        results.append({
            "text": "Daily log has a vocabulary table with key terms including pronunciations and meanings",
            "passed": passed,
            "evidence": "Vocabulary table found with required columns" if passed else "Missing vocabulary table structure"
        })

        # Check 4: Sentence patterns
        passed, evidence = check_file_contains(daily_file, "pattern")
        results.append({
            "text": "Identifies and documents reusable sentence patterns",
            "passed": passed,
            "evidence": evidence
        })
    else:
        for desc in [
            "Provides clear explanation of 'incremental rollout' in Chinese",
            "Daily log has a vocabulary table with key terms including pronunciations and meanings",
            "Identifies and documents reusable sentence patterns"
        ]:
            results.append({"text": desc, "passed": False, "evidence": "Daily log not found"})

    # Check 5: vocabulary.md
    vocab_file = english_dir / "vocabulary.md"
    passed = vocab_file.exists()
    results.append({
        "text": "Updates vocabulary.md with the new technical terms under appropriate category",
        "passed": passed,
        "evidence": f"vocabulary.md {'found' if passed else 'not found'}"
    })

    # Check 6: expressions.md
    expr_file = english_dir / "expressions.md"
    passed = expr_file.exists()
    results.append({
        "text": "Updates expressions.md with the extracted sentence patterns",
        "passed": passed,
        "evidence": f"expressions.md {'found' if passed else 'not found'}"
    })

    return results

def grade_eval_3(outputs_dir):
    """Grade email translation eval"""
    results = []
    english_dir = Path(outputs_dir) / "English"

    # Check 1: Provides translation
    # Look for either daily log or direct output file
    daily_dir = english_dir / "daily"
    has_daily, daily_evidence = check_file_exists(daily_dir, "*.md")

    translation_found = False
    translation_file = None

    if has_daily:
        daily_file = list(daily_dir.glob("*.md"))[0]
        with open(daily_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "api" in content.lower() and ("integration test" in content.lower() or "regression test" in content.lower()):
                translation_found = True
                translation_file = daily_file

    results.append({
        "text": "Provides accurate English translation suitable for professional email to PM",
        "passed": translation_found,
        "evidence": "Translation found in daily log" if translation_found else "Translation not found in expected location"
    })

    # Check 2: Daily log exists
    results.append({
        "text": "Creates a daily log file in English/daily/ with the translation and learning materials",
        "passed": has_daily,
        "evidence": daily_evidence
    })

    if translation_file:
        with open(translation_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check 3: Technical vocabulary
        has_vocab_table = "word" in content.lower() and "pronunciation" in content.lower() and "meaning" in content.lower()
        has_tech_terms = sum([
            "integration" in content.lower(),
            "root cause" in content.lower(),
            "schema" in content.lower(),
            "parsing" in content.lower(),
            "regression" in content.lower()
        ]) >= 3

        passed = has_vocab_table and has_tech_terms
        results.append({
            "text": "Daily log includes vocabulary table with technical terms",
            "passed": passed,
            "evidence": "Vocabulary table with technical terms found" if passed else "Missing vocabulary table or key terms"
        })

        # Check 4: Key sentences section
        passed = "key sentence" in content.lower() or "sentence" in content.lower()
        results.append({
            "text": "Daily log has key sentences section analyzing useful expressions",
            "passed": passed,
            "evidence": "Key sentences section found" if passed else "Key sentences section missing"
        })

        # Check 5: Patterns
        passed = "pattern" in content.lower()
        results.append({
            "text": "Daily log includes useful patterns table for technical communication",
            "passed": passed,
            "evidence": "Patterns section found" if passed else "Patterns section missing"
        })
    else:
        for desc in [
            "Daily log includes vocabulary table with technical terms",
            "Daily log has key sentences section analyzing useful expressions",
            "Daily log includes useful patterns table for technical communication"
        ]:
            results.append({"text": desc, "passed": False, "evidence": "Daily log not found"})

    # Check 6: vocabulary.md
    vocab_file = english_dir / "vocabulary.md"
    passed = vocab_file.exists()
    results.append({
        "text": "Updates vocabulary.md with testing/technical terms",
        "passed": passed,
        "evidence": f"vocabulary.md {'found' if passed else 'not found'}"
    })

    # Check 7: expressions.md
    expr_file = english_dir / "expressions.md"
    passed = expr_file.exists()
    results.append({
        "text": "Updates expressions.md with email/technical communication patterns",
        "passed": passed,
        "evidence": f"expressions.md {'found' if passed else 'not found'}"
    })

    return results

def main():
    if len(sys.argv) < 3:
        print("Usage: python grade.py <eval_number> <outputs_dir>")
        sys.exit(1)

    eval_num = int(sys.argv[1])
    outputs_dir = sys.argv[2]

    if eval_num == 1:
        results = grade_eval_1(outputs_dir)
    elif eval_num == 2:
        results = grade_eval_2(outputs_dir)
    elif eval_num == 3:
        results = grade_eval_3(outputs_dir)
    else:
        print(f"Unknown eval number: {eval_num}")
        sys.exit(1)

    # Calculate pass rate
    total = len(results)
    passed = sum(1 for r in results if r["passed"])

    output = {
        "expectations": results,
        "pass_rate": passed / total if total > 0 else 0,
        "total_assertions": total,
        "passed_assertions": passed
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
