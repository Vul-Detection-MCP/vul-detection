# Count tool calls from a ARGV-supplied log file
# Pattern: "Tool call: %TOOL_NAME%"
import os
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: script.py <logfile>")
        return
    log_file = sys.argv[1]
    os.system(f"""grep -o "Tool call: [^\\\" ]*" {log_file} | sed "s/Tool call: //" | sort | uniq -c | sort -nr""")

if __name__ == '__main__':
    main()
