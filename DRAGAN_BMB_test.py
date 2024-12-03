import csv
import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.meteor_score import meteor_score
from nltk.tokenize import word_tokenize
from bert_score import score
import logging

logging.getLogger("transformers.modeling_utils").setLevel(logging.ERROR)

# download once to initalize
# nltk.download('punkt')
# nltk.download('punkt_tab')
# nltk.download('wordnet')

# Define input and output file paths
input_file_path = './ANSWERS/answers_100_nosamples.csv'
output_file_path = './ANALYSIS/evaluation_scores_100_4o_nosamples.csv'

# Function to calculate BLEU score
def calculate_bleu(reference, sample):
    smoothing_fn = SmoothingFunction().method1
    reference_tokens = reference.split()  # Tokenize reference
    sample_tokens = sample.split()  # Tokenize sample
    return sentence_bleu([reference_tokens], sample_tokens, smoothing_function=smoothing_fn)

# Function to calculate METEOR score
def calculate_meteor(reference, sample):
    # Tokenize the reference and sample
    reference_tokens = word_tokenize(reference)
    sample_tokens = word_tokenize(sample)
    # Compute METEOR score
    return meteor_score([reference_tokens], sample_tokens)

# Function to calculate BERTScore
def calculate_bertscore(reference, sample):
    # Compute BERTScore using pretrained BERT model
    P, R, F1 = score([sample], [reference], lang="en", verbose=False)
    return float(F1[0])  # Return F1 score as a single float

# Process input file and create output file
with open(input_file_path, 'r', encoding='utf-8') as infile, open(output_file_path, 'w', encoding='utf-8', newline='') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = ['Index', 'Question', 'Reference', 'Candidate', 'BLEU', 'METEOR', 'BERTScore']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        index = row.get('Index', '')
        question = row.get('Question', '')[:10]  # First 10 characters of Question
        reference = row.get('Reference', '')  # Use full Reference for evaluation
        sample = row.get('Candidate', '')  # Use full Sample for evaluation

        # Calculate BLEU, METEOR, and BERTScore
        bleu_score = calculate_bleu(reference, sample)
        meteor = calculate_meteor(reference, sample)
        bertscore = calculate_bertscore(reference, sample)

        # Write results to output file
        writer.writerow({
            'Index': index,
            'Question': question,
            'Reference': reference[:10],  # Truncated for display in output
            'Candidate': sample[:10],  # Truncated for display in output
            'BLEU': round(bleu_score, 4),
            'METEOR': round(meteor, 4),
            'BERTScore': round(bertscore, 4)
        })

# Output file path
print(f"Results written to {output_file_path}")
