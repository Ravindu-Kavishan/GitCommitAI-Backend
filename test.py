from google import genai

client = genai.Client(api_key="AIzaSyBcFZ_ulQ6o2tbmFKOazUAbB8-7zkRnj2A")

diff = """
diff --git a/src/app/components/Button.js b/src/app/components/Button.js
index abc1234..def5678 100644
--- a/src/app/components/Button.js
+++ b/src/app/components/Button.js
@@ -1,6 +1,7 @@
 import React from 'react';

 const Button = ({ label, onClick }) => {
-  return <button onClick={onClick}>{label}</button>;
+  return <button className="btn" onClick={onClick}>{label}</button>;
 };

 export default Button;
"""

def get_suggested_word(commit_msg):
    prompt = (
        "You are an AI assistant that helps a user to complete a manual commit message by suggesting the next word.\n"
        "Below is the already typed commit message:\n"
        f"{commit_msg}\n"
        "Below is the git differencerelated to the commit:\n"
        f"{diff}\n"
        "User only needs the next word nothing else, therefore only output the predicted word.\n"
        "If the commit message do not need any suggestions return done"
        "If the commit message is empty return a start word"
        "Stay within the given context of the given git difference"
        "Keep the commit message consice"
    )
    
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )
    return response.text.strip()

def interactive_commit_message():
    commit_msg = ""
    
    while True:
        # Ask the user to type part of the commit message
        print(f"Current commit message: '{commit_msg}'")
        user_input = input("Press space to complete the next word in the commit message (or type 'exit' to quit): ")
        
        # If user types 'exit', break the loop and stop suggesting words
        if user_input.lower() == "exit":
            print("Exiting. Final commit message:", commit_msg)
            break
        
        # Update commit message with user input
        commit_msg += " " + user_input.strip()

        # Get the next suggested word
        suggestion = get_suggested_word(commit_msg)

        # If the suggestion is 'done', break out of the loop (commit message complete)
        if suggestion.lower() == "done":
            print("Commit message complete:", commit_msg)
            break

        # Show the suggested next word
        print(f"Suggested next word: '{suggestion}'")
        
if __name__ == "__main__":
    interactive_commit_message()
