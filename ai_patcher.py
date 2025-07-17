# ai_patcher.py
import ollama

def get_full_patch(full_code, message):
    prompt = f"""
You are a secure code expert.

This file has one or more security vulnerabilities.
Here is the original code:\n{full_code}

Known issue: {message}

Please rewrite the ENTIRE file with all vulnerabilities fixed.
Respond with just the fixed code and a brief explanation.
"""
    response = ollama.chat(
        model="deepseek-coder",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['message']['content']
