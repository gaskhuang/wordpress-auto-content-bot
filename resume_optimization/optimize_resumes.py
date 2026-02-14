import json
import re
from collections import Counter
import csv

def optimize_resumes(input_path, output_path):
    print(f"正在讀取檔案: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. 識別全局重複的行 (UI 雜訊)
    all_lines = []
    for item in data:
        full_text = item.get('full_text', '')
        if full_text:
            all_lines.extend(full_text.split('\n'))
    
    line_counts = Counter(all_lines)
    # 如果某行在超過 80% 的履歷中出現，則視為 UI 雜訊
    threshold = len(data) * 0.8
    common_noise = {line for line, count in line_counts.items() if count >= threshold and line.strip()}

    # 2. 處理每一份履歷
    optimized_data = []
    for item in data:
        full_text = item.get('full_text', '')
        
        # 移除噪音行
        lines = full_text.split('\n')
        cleaned_lines = [line for line in lines if line not in common_noise]
        
        # 重新組合文字
        cleaned_text = '\n'.join(cleaned_lines).strip()
        
        # 嘗試從文字中提取姓名 (如果原欄位為空)
        name = item.get('name', '')
        if not name or name == "N/A" or name == "":
            match = re.search(r'([^\s\d\w]{2,4})\s+\d+歲\s+(男|女)', cleaned_text)
            if match:
                name = match.group(1)
        
        # 移除連續的換行符號以進一步瘦身
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)

        # 建立優化後的物件
        optimized_item = {
            "serial_number": item.get("serial_number"),
            "name": name,
            "url": item.get("url"),
            "scraped_at": item.get("scraped_at"),
            "summary_text": cleaned_text
        }
        optimized_data.append(optimized_item)

    # 3. 儲存 JSON 結果
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(optimized_data, f, ensure_ascii=False, indent=2)

    # 4. 轉換為 CSV
    csv_path = output_path.replace('.json', '.csv')
    if optimized_data:
        keys = optimized_data[0].keys()
        with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(optimized_data)

    print(f"優化完成。原始筆數: {len(data)}")
    print(f"JSON 產出路徑: {output_path}")
    print(f"CSV 產出路徑: {csv_path}")

if __name__ == "__main__":
    input_file = "/Users/gask/.gemini/antigravity/scratch/resume_optimization/resumes_251-260.json"
    output_file = "/Users/gask/Downloads/resumes_data_251-260_optime.json"
    optimize_resumes(input_file, output_file)
