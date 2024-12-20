
import random
import csv
from math import ceil

# Define constants for error handling
skip_tokens = ('गे', 'दे', 'ले', 'गा','जाए','जा', 'ला', 'ले', 'पा', 'खा', 'चाहिए', 'समाजवादी', 'विधानसभा', 
               'थालिपीठे', 'मराठवाड़ा', 'अन्यथा', 'खुफिया', 'अनसुना', 'इन्होंने')
exceptions = (('है', 'हैं'), ('था', 'थे', 'थी', 'थीं'), ('हुआ', 'हुई', 'हुए', 'हुईं'))
conjugated_adj = ('लंबा', 'ऊंचा', 'धीमा', 'महंगा', 'गीला', 'भूरा', 'मोटा', 'हल्का', 'पुराना',
                  'ताज़ा', 'बुरा', 'फिस्लाहा', 'कड़वा', 'चौड़ा', 'चौड़ा', 'सुखा', 'नमा', 'खट्टा', 
                  'पतला', 'लम्बा', 'अच्छा', 'हरा', 'थोड़ा', 'बड़ा', 'बूढा', 'कड़वा', 'निचा', 
                  'चमकीला', 'मीठा', 'पीला', 'भोला', 'गाढ़ा', 'खुरदुरा', 'ठंडा', 'गंदा', 'तीता', 
                  'सस्ता', 'छोटा', 'नया', 'गीरा', 'सूखा', 'गहरा', 'सीधा', 'खारा', 'दुबला', 
                  'चिपचिपा', 'नीला','तीखा','डरावना','सुनहरा','इकलौता','तीखा','समूचा','पुरा',
                  'अनूठा', 'सुरीला','ख़रीदा','संकरा','रूखा','अंधा','बहरा','बौना','ठिगना','पैना',
                  'घना','डरावना','अनूठा','झूठा','इकट्ठा','भरा','अधूरा', 'नुकीला','उबला','ढीला',
                  'पक्का', 'पहला', 'दूसरा','तीसरा','चौथा','पांचवा','छठा','पचवा','सातवा','आठवा',
                  'नौवा', 'दसवा')
adj_endings = ('ा', 'े', 'ी')
vb_endings = ('ा', 'े', 'ी', 'ीं')
endings1 = ('या', 'ए', 'ई', 'ईं',)
endings2 = ('या', 'ये', 'यी', 'यीं')

# Function definitions
def random_except(options, choice):
    remaining = list(options)
    remaining.remove(choice)
    return random.choice(remaining)

def endswith_any(word, endings):
    for ending in endings:
        if word.endswith(ending):
            return ending
    return None

def insert_single_error(sentence):
    words = sentence.split()
    erroneous_sentences = []

    for i, token in enumerate(words):
        original_token = token

        # Skip tokens
        if token in skip_tokens:
            continue

        # Handle exceptions
        elif any(token in ex for ex in exceptions):
            matching_exception = next(ex for ex in exceptions if token in ex)
            modified_token = random_except(matching_exception, token)
            erroneous_sentences.append(' '.join(words[:i] + [modified_token] + words[i+1:]))
        
        # Handle adjective endings
        elif len(token) > 4 and token[-1] in adj_endings and token[:-1] in conjugated_adj:
            modified_token = token[:-1] + random_except(adj_endings, token[-1])
            erroneous_sentences.append(' '.join(words[:i] + [modified_token] + words[i+1:]))

        # Handle verb endings
        elif len(token) > 3 and any(token.endswith(ending) for ending in vb_endings):
            ending = endswith_any(token, vb_endings)
            if ending:
                modified_token = token[:-len(ending)] + random_except(vb_endings, ending)
                erroneous_sentences.append(' '.join(words[:i] + [modified_token] + words[i+1:]))

        # # Handle other random character errors
        # elif len(token) > 3:
        #     pos = random.randint(1, len(token) - 2)
        #     modified_token = token[:pos] + token[pos + 1:]
        #     erroneous_sentences.append(' '.join(words[:i] + [modified_token] + words[i+1:]))

    return erroneous_sentences

def process_sentences(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile:
        data = infile.read()

    sentences = data.split('.')  # Split sentences by '.'
    output_rows = []

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        erroneous_variants = insert_single_error(sentence)

        for variant in erroneous_variants:
            output_rows.append([variant, sentence])

    # Save results to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["hi_err", "hi_corr"])  # Header
        writer.writerows(output_rows)

    print(f"Processed {len(sentences)} sentences. Results saved to {output_file}.")

# Main execution
if __name__ == "__main__":
    input_file = "hindi.input.txt"  # Input text file with Hindi sentences
    output_file = "output.csv"  # Output CSV file
    process_sentences(input_file, output_file)
