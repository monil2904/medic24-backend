import re

def parse_lab_report(raw_text: str) -> list[dict]:
    # Regex patterns for Indian lab formats
    # Example format: Hemoglobin  14.5  g/dL  13.0-17.0
    results = []
    
    # A robust regex capturing Test Name, Value, Unit, Reference Range, and optional Flag
    pattern = re.compile(
        r"([A-Za-z\s\(\)]+?)\s+(\d+\.?\d*)\s+([A-Za-z/%]+)\s+([\d\.\-]+)\s*(HIGH|LOW|NORMAL|CRITICAL)?", 
        re.IGNORECASE
    )
    
    matches = pattern.findall(raw_text)
    for match in matches:
        test_name = match[0].strip()
        # Filter out common false positive header lines
        if not test_name or test_name.lower() in ["test", "result", "unit", "reference"]:
            continue
            
        value_str = match[1]
        unit = match[2].strip()
        ref_range = match[3].strip()
        flag = match[4].strip().upper() if len(match) > 4 and match[4] else "NORMAL"
        
        try:
            val = float(value_str)
        except ValueError:
            continue
            
        # Basic flag inference if actual flag wasn't explicitly present
        if not flag or flag == "NORMAL":
            if '-' in ref_range:
                parts = ref_range.split('-')
                if len(parts) == 2:
                    try:
                        low = float(parts[0])
                        high = float(parts[1])
                        if val < low:
                            flag = "LOW"
                        elif val > high:
                            flag = "HIGH"
                        else:
                            flag = "NORMAL"
                    except ValueError:
                        flag = "NORMAL"
            else:
                flag = "NORMAL"

        results.append({
            "test": test_name,
            "value": val,
            "unit": unit,
            "range": ref_range,
            "flag": flag
        })
        
    return results
