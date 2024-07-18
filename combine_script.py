import sys

# 커맨드 라인 인자로 serial 값을 받음
if len(sys.argv) < 2:
    print("Error: No serial number provided.")
    sys.exit(1)

serial_data = sys.argv[1]
print(serial_data)

with open("serial_config.py", "r", encoding="utf-8") as serial_file:
    serial_content = serial_file.read()

with open("auto40_build_2.py", "r", encoding="utf-8") as main_file:
    main_data = main_file.read()

combined_data = serial_content + "\n" + main_data

# 파일 이름에 serial_data 값을 포함시킴
output_filename = f"auto40_{serial_data}.py"

with open(output_filename, "w", encoding="utf-8") as combined_file:
    combined_file.write(combined_data)