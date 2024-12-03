import os
import logging
import dotenv
import importlib
import csv
from chatbot_api.src.agents.dragan_rag_agent import dragan_rag_agent_executor

FILE_QUESTIONS = "./QUESTIONS/questions_100.txt"        # input file with questions for DRAGAN
FILE_ANSWERS = "./ANSWERS/answers_100_nosamples.csv"    # output .csv file with DRAGAN generated responses

# Custom logging filter to suppress specific messages
class SuppressConnectionErrors(logging.Filter):
    def filter(self, record):
        # Suppress messages containing "Failed to write data to connection"
        return "Failed to write data to connection" not in record.getMessage()

# Configure logging to use the custom filter
logging.basicConfig(
    level=logging.INFO,  # Adjust the logging level as necessary
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger()
logger.addFilter(SuppressConnectionErrors())

def process_questions_from_file(input_file, output_file):
    """Reads questions from a file, processes them, and writes answers to a CSV."""
    if not os.path.exists(input_file):
        print(f"Error: The file '{input_file}' does not exist.")
        return
    
    try:
        with open(input_file, "r") as f:
            questions = [line.strip() for line in f.readlines() if line.strip()]
        
        results = []
        for idx, question in enumerate(questions, start=1):
            try:
                response = dragan_rag_agent_executor.invoke({"input": question})
                answer = response.get('output', 'No response received.')
                results.append((idx, question, answer, answer))
                print(f"Processed question {idx}: {question}")
            except Exception as e:
                print(f"Error processing question {idx}: {e}")
                results.append((idx, question, "Error during processing"))
        
        # Write results to a CSV file
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Index", "Question", "Reference", "Candidate"])
            writer.writerows(results)
        
        print(f"Results written to '{output_file}'.")
    except Exception as e:
        print(f"Error: {e}")

def main():
    # Load environment variables from .env
    dotenv.load_dotenv()

    print("Welcome to the DRAGAN Chat Interface!")
    print("You can ask questions, type 'run tests' to process a question file, or type 'quit' to exit.")

    while True:
        # Get user input
        user_input = input("Ask a question: ")
        
        # Exit the loop if the user types 'quit'
        if user_input.lower() == 'quit':
            print("Thank you for using DRAGAN!")
            break
        
        # Run tests from file
        if user_input.lower() == 'run tests':
            input_file = FILE_QUESTIONS
            output_file = FILE_ANSWERS
            process_questions_from_file(input_file, output_file)
            continue

        # Send the question to the dragan_rag_agent_executor
        try:
            response = dragan_rag_agent_executor.invoke({"input": user_input})
            print("DRAGAN: " + response.get('output', 'No response received.'))
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
