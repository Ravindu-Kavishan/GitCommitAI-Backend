import requests
import json

diff="""
diff --git a/example.py b/example.py
index 1234567..89abcde 100644
--- a/example.py
+++ b/example.py
@@ -1,6 +1,8 @@
 def greet(name):
     print(f"Hello, {name}!")
+    print("Welcome to the Python world!")
 
 def add(a, b):
     return a + b
 
 def subtract(a, b):
-    return a - b
+    if b == 0:
+        return "Cannot subtract by zero"
     return a - b
+
 def multiply(a, b):
+    return a * b
"""

instructions1 = "Given the following git diff,generate only a single line commit message, covering all the changes:"
instructions2 = "Given the following git diff,generate only a commit message as multiple simple few points, covering all the changes:"

prompt=f"{instructions2}\n{diff}"

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    # "Authorization": "Bearer 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",
    "Authorization": "Bearer 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",
    "Content-Type": "application/json",
    "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
    "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
  },
  data=json.dumps({
    "model": "meta-llama/llama-3.3-70b-instruct",
    "messages": [
      {
        "role": "user",
        "content": prompt
      }
    ],
    
  })
)

# print(response)
content = response.json()['choices'][0]['message']['content']

print(content)