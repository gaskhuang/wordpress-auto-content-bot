import json
import os
import re

def split_json_to_txt(input_path, output_dir, chunk_size=20):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 根據 serial_number 排序
    data.sort(key=lambda x: x.get('serial_number', 0))
    
    total = len(data)
    for i in range(0, total, chunk_size):
        chunk = data[i:i + chunk_size]
        start_sn = chunk[0].get('serial_number', i + 1)
        end_sn = chunk[-1].get('serial_number', i + len(chunk))
        
        filename = f"{start_sn}-{end_sn}.txt"
        file_path = os.path.join(output_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f_out:
            for item in chunk:
                sn = item.get('serial_number', 'N/A')
                summary = item.get('summary_text', '')
                
                # 參考 optimize_resumes.py 的姓名提取邏輯
                name = item.get('name', '')
                if not name or name == "N/A" or name == "":
                    # 匹配 2-4 個非空白字符，後接歲數與性別
                    match = re.search(r'([^\s\d\w]{2,4})\s+\d+歲\s+(男|女)', summary)
                    if match:
                        name = match.group(1).strip()
                
                f_out.write(f"--- Serial Number: {sn} ---\n")
                if name and name.strip():
                    f_out.write(f"姓名: {name}\n")
                f_out.write(f"{summary}\n")
                f_out.write("\n" + "="*50 + "\n\n")
        
        print(f"Generated: {filename}")

if __name__ == "__main__":
    input_file = "/Users/gask/Downloads/resumes_data_251-260_optime.json"
    output_folder = "/Users/gask/Downloads/split_resumes"
    split_json_to_txt(input_file, output_folder)
