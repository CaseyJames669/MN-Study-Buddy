import json
import random
import re

class SprinklerExamBuddy:
    def __init__(self, data_files):
        self.data = {}
        self.load_data(data_files)
        self.current_file = None  # Track the current file for follow-up questions.
        self.last_question = None
        self.greet()



    def load_data(self, data_files):
        for file in data_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            entry = json.loads(line)
                            # Basic validation
                            if not all(k in entry for k in ("input", "output", "source", "quoted text")):
                                print(f"Warning: Skipping invalid entry in {file}: {line.strip()}")
                                continue

                            # Use a single key combining filename and question.  Make it lowercase.
                            key = (file + ":" + entry['input']).lower()
                            self.data[key] = entry
                        except json.JSONDecodeError as e:
                            print(f"JSONDecodeError in {file}: {e} - Line: {line.strip()}")
            except FileNotFoundError:
                print(f"Error: File not found: {file}")
            except Exception as e:
                print(f"Error loading file {file}: {e}")

        if not self.data:
            raise ValueError("No valid data loaded.  Check your JSONL files.")
        print(f"Loaded {len(self.data)} question/answer pairs.")


    def greet(self):
        print("\nHowdy! I'm your study buddy for the Minnesota Journeyman Sprinkler Fitter exam.  I'm loaded up with info from the 2020 MSFC and those NFPA standards. Ask me anything, but remember, I cite my sources! Type 'help' for a list of commands, or 'quit' to exit.")

    def ask_question(self, topic=None):
        if topic:
            # Filter questions by topic (filename)
            topic = topic.lower()
            relevant_questions = [
                (q, data) for q, data in self.data.items() if q.startswith(topic + ":")
            ]
            if not relevant_questions:
                print(f"Sorry, I don't have any questions on '{topic}'.  Try 'list topics' to see available topics.")
                return None, None

            question_key, data = random.choice(relevant_questions)
            self.current_file = question_key.split(":")[0]  # Extract filename

        else:  # Random question
             question_key, data = random.choice(list(self.data.items()))
             self.current_file = question_key.split(":")[0]


        print("\nQuestion:", data['input'])
        self.last_question = question_key #store for answer, follow up
        return question_key, data


    def show_answer(self, question_key):
        if question_key:
            data = self.data[question_key]
            print("\nAnswer:", data['output'])
            print("Source:", data['source'])
            print("Quoted Text:", data['quoted text'])
        else:
            print("Ask a question first.")

    def follow_up(self):
        if self.last_question:
            self.show_answer(self.last_question)
        else:
            print("Ask a question first, and I can show you the answer and source.")

    def list_topics(self):
        topics = sorted(list(set(q.split(":")[0] for q in self.data.keys())))
        print("\nAvailable Topics (Files):")
        for topic in topics:
            print(f"  - {topic}")

    def run(self):
        question_key = None
        data = None

        while True:
            command = input("\nYour command (or question): ").strip().lower()

            if command == 'quit':
                break
            elif command == 'help':
                print("\nAvailable Commands:")
                print("  ask [topic]   - Ask a random question, optionally from a specific topic (file).")
                print("  answer        - Show the answer and source for the last question.")
                print("  follow up     - Same as 'answer'.")
                print("  list topics   - List available topics (files).")
                print("  help          - Show this help message.")
                print("  quit          - Exit the study buddy.")
                print("  [question]    - Ask a specific question (I will try to find a match or related info).")
            elif command.startswith('ask'):
                parts = command.split(" ", 1)
                topic = parts[1] if len(parts) > 1 else None
                question_key, data = self.ask_question(topic)
            elif command == 'answer' or command == 'follow up':
                 self.follow_up()
            elif command == 'list topics':
                self.list_topics()
            else:
                # Attempt to find a matching question
                matched_key = self.find_question(command)
                if matched_key:
                    self.show_answer(matched_key)

                else: #if no match, return random
                    print("I couldn't find that, here is a random one")
                    question_key, data = self.ask_question()

    def find_question(self, question_text):
        """Finds a question in the data that matches the input text (case-insensitive)."""
        question_text = question_text.lower()
        for key in self.data:
            if question_text in key:
                return key
        return None


# --- Main Program Execution ---
if __name__ == "__main__":
    # Get all .jsonl files in the current directory.  This is MUCH better than hardcoding.
    import glob
    data_files = glob.glob("*.jsonl")
    data_files = [file for file in data_files if "index" not in file] #removes the index file

    if not data_files:
        print("No .jsonl data files found in the current directory.  Exiting.")
        exit()

    try:
        buddy = SprinklerExamBuddy(data_files)
        buddy.run()
    except ValueError as e:
        print(f"Error: {e}")