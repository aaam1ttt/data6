#!/usr/bin/env python3

import os
import re
import ast
import tokenize
from io import StringIO

def remove_comments_from_python_code(code):
    """Remove comments from Python code while preserving strings and functional syntax"""
    try:
        result_lines = []
        lines = code.split('\n')
        
        for line in lines:
            # Check if line contains a # symbol
            if '#' not in line:
                result_lines.append(line)
                continue
            
            # Use tokenize to properly handle strings vs comments
            try:
                tokens = list(tokenize.generate_tokens(StringIO(line + '\n').readline))
                clean_line = ""
                last_end = 0
                
                for token in tokens:
                    if token.type == tokenize.COMMENT:
                        # Add everything up to the comment
                        clean_line += line[last_end:token.start[1]]
                        # Skip the comment
                        break
                    elif token.type in (tokenize.STRING, tokenize.FSTRING_START, tokenize.FSTRING_MIDDLE, tokenize.FSTRING_END):
                        # Keep strings intact
                        clean_line += line[last_end:token.end[1]]
                        last_end = token.end[1]
                    elif token.type == tokenize.NEWLINE or token.type == tokenize.NL:
                        clean_line += line[last_end:]
                        break
                    else:
                        last_end = token.end[1]
                
                if not clean_line and last_end < len(line):
                    clean_line = line[last_end:]
                
                # Remove trailing whitespace but keep the line structure
                clean_line = clean_line.rstrip()
                result_lines.append(clean_line)
                
            except tokenize.TokenError:
                # If tokenization fails, use simple approach but be careful with strings
                in_string = False
                string_char = None
                i = 0
                clean_line = ""
                
                while i < len(line):
                    char = line[i]
                    if not in_string and char in ['"', "'"]:
                        in_string = True
                        string_char = char
                        clean_line += char
                    elif in_string and char == string_char and (i == 0 or line[i-1] != '\\'):
                        in_string = False
                        string_char = None
                        clean_line += char
                    elif not in_string and char == '#':
                        break
                    else:
                        clean_line += char
                    i += 1
                
                clean_line = clean_line.rstrip()
                result_lines.append(clean_line)
        
        return '\n'.join(result_lines)
    
    except Exception as e:
        print(f"Error processing code: {e}")
        return code

def process_python_file(file_path):
    """Process a single Python file to remove comments"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_code = f.read()
        
        clean_code = remove_comments_from_python_code(original_code)
        
        # Verify the cleaned code is still valid Python
        try:
            ast.parse(clean_code)
        except SyntaxError as e:
            print(f"Warning: Syntax error in cleaned code for {file_path}: {e}")
            print("Skipping this file to avoid breaking the code")
            return False
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(clean_code)
        
        print(f"Processed: {file_path}")
        return True
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Remove comments from all Python files in the project"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    python_files = []
    for root, dirs, files in os.walk(project_root):
        # Skip venv and .git directories
        dirs[:] = [d for d in dirs if d not in ['venv', '.git', '__pycache__']]
        
        for file in files:
            if file.endswith('.py') and file != 'remove_comments.py':
                python_files.append(os.path.join(root, file))
    
    print(f"Found {len(python_files)} Python files to process")
    
    processed = 0
    for file_path in python_files:
        if process_python_file(file_path):
            processed += 1
    
    print(f"Successfully processed {processed} out of {len(python_files)} files")

if __name__ == '__main__':
    main()