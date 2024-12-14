import random
import sys
from difflib import SequenceMatcher
from math import ceil
import csv

'अंग्रेजा', 'पड़ते', 'बनीं',

skip_tokens = ('गे', 'दे', 'ले', 'गा','जाए','जा', 'ला', 'ले', 'पा', 'खा', 'चाहिए', 'समाजवादी', 'विधानसभा', 'थालिपीठे', 'मराठवाड़ा', 'अन्यथा', 'खुफिया', 'अनसुना', 'इन्होंने')
exceptions = (('है', 'हैं'), ('था', 'थे', 'थी', 'थीं'), ('हुआ', 'हुई', 'हुए', 'हुईं'))
conjugated_adj = ('लंबा', 'ऊंचा', 'धीमा', 'महंगा', 'गीला', 'भूरा', 'मोटा', 'हल्का', 'पुराना',
                  'ताज़ा', 'बुरा', 'फिस्लाहा', 'कड़वा', 'चौड़ा', 'चौड़ा', 'सुखा', 'नमा', 'खट्टा', 'पतला', 'लम्बा', 'अच्छा', 'हरा', 'थोड़ा',
                  'बड़ा', 'बूढा', 'कड़वा', 'निचा', 'चमकीला', 'मीठा', 'पीला', 'भोला', 'गाढ़ा', 'खुरदुरा', 'ठंडा', 'गंदा', 'तीता', 'सस्ता',
                  'छोटा', 'नया', 'गीरा', 'सूखा', 'गहरा', 'सीधा', 'खारा', 'दुबला', 'चिपचिपा',
                  'नीला','तीखा','डरावना','सुनहरा','इकलौता','तीखा','समूचा','पुरा','अनूठा', 'सुरीला',
                  'ख़रीदा','संकरा','रूखा','अंधा','बहरा','बौना','ठिगना','पैना','घना','डरावना',
                  'अनूठा','झूठा','इकट्ठा','भरा','अधूरा', 'नुकीला','उबला','ढीला','पक्का',
                  'पहला', 'दूसरा','तीसरा','चौथा','पांचवा','छठा','पचवा','सातवा','आठवा',
                  'नौवा', 'दसवा' ,
                  )

adj = ('ा', 'े', 'ी')
vb = ('ा', 'े', 'ी', 'ीं')

endings1 = ('या', 'ए', 'ई', 'ईं',)
endings2 = ('या', 'ये', 'यी', 'यीं')



def convert_to_edits(err, cor):
    return f'{err}\n{cor}\n'


def convert_to_wdiff(err, cor):
    result = []
    err_toks, cor_toks = err.split(), cor.split()
    matcher = SequenceMatcher(None, err_toks, cor_toks)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        err_part = ' '.join(err_toks[i1:i2])
        cor_part = ' '.join(cor_toks[j1:j2])
        if tag == 'replace':
            result.append("[-{}-] {{+{}+}}".format(err_part, cor_part))
        elif tag == 'insert':
            result.append("{{+{}+}}".format(cor_part))
        elif tag == 'delete':
            result.append("[-{}-]".format(err_part))
        else:
            result.append(err_part)
    return ' '.join(result)


def sentence_wise(file):
    sentence = []
    for line in file:
        line = line.strip()
        if line == '</s>':
            yield sentence
            sentence = []
        elif line == '<s>':
            pass
        else:
            sentence.append(line)
    yield sentence


def pos_tag(sentence):
    actual_words = []
    tags = []
    tags_better = []
    for word in sentence:
        components = word.split('\t')
        if len(components) < 3:
            continue  # Or handle the error appropriately
        actual_words.append(components[0])
        tags.append(components[2])
        tags_better.append(components)
    return zip(actual_words, tags, tags_better)


def random_except(options, choice):
    remaining = list(options)
    remaining.remove(choice)
    return random.choice(remaining)


def endswith_any(word, endings):
    for ending in endings:
        if word.endswith(ending):
            return ending


def insert_errors(pos_tags):
    err = []
    cor = []
    edit_types = []  # New list to store edit types

    for token, tag, _ in pos_tags:
        try:
            if token in skip_tokens or len(token) < 2:
                err.append(token)
                edit_types.append("NO_ERR")  # No edit applied
            elif tag == 'PSP' and token[-1] in adj and token[-2] in ('क', 'ल'):
                err.append(token[:-1] + random_except(adj, token[-1]))
                edit_types.append("PSP")
            elif list(filter(lambda ex: token in ex, exceptions)):
                exs = list(filter(lambda ex: token in ex, exceptions))
                err.append(random_except(exs[0], token))
                edit_types.append("EXCEPTION")
            elif len(token) > 4 and token[-1] in adj and token[-4:-1] == 'वाल':
                err.append(token[:-1] + random_except(adj, token[-1]))
                edit_types.append("ADJ_CONJ")
            elif tag in ('JJ', 'QO') and token[-1] in adj and (token[:-1] + adj[0]) in conjugated_adj:
                err.append(token[:-1] + random_except(adj, token[-1]))
                edit_types.append("CONJ_ADJ")
            elif tag == 'PRP' and token[-1] in adj and (token[-2] in ('र', 'क') or token.startswith('अप')):
                err.append(token[:-1] + random_except(adj, token[-1]))
                edit_types.append("PRP")
            elif tag == 'VAUX':
                if len(token) == 2 and token[-1] in vb[-2:]:
                    err.append(token[0] + random.choice(endings1[:2]))
                    edit_types.append("VAUX_SHORT")
                elif endswith_any(token, endings1):
                    ending = endswith_any(token, endings1)
                    substitute = random_except(endings1, ending)
                    err.append(token.strip(ending) + substitute)
                    edit_types.append("VAUX")
                else:
                    err.append(token)
                    edit_types.append("NO_ERR")
            else:
                err.append(token)
                edit_types.append("NO_ERR")
            cor.append(token)
        except IndexError as e:
            print(token, tag, e, file=sys.stderr)
    return ' '.join(err), ' '.join(cor), ', '.join(edit_types)



def select_edits(err, cor, edit_types, selection_ratio=1):
    mismatch = []
    err, cor = err.split(), cor.split()
    mm = []
    for i, (er, co) in enumerate(zip(err, cor)):
        if er != co:
            mm.append((er, co))
            mismatch.append(i)
    num_edits = ceil(len(mismatch) * selection_ratio)
    for i in sorted(random.sample(mismatch, num_edits)):
        cor_cpy = cor[:]
        cor_cpy[i] = err[i]
        yield ' '.join(cor), ' '.join(cor_cpy)


def main(args):
    print("is it running?")
    output_rows = []
    print(args.input_file[:10])
    with open(args.input_file) as input_file:
        for sentence in sentence_wise(input_file):
            sentence_tagged = pos_tag(sentence)
            
            inserted_errors = insert_errors(sentence_tagged)
            
            if args.single is not None:
                inserted_errors = select_edits(*inserted_errors, args.single)
            else:
                inserted_errors = [inserted_errors]

            for cor, err, edit_types in inserted_errors:
                # for edit_type in edit_types:  # Add rows for each edit type
                output_rows.append([err, cor, edit_type])
                if args.edits:
                    print(convert_to_edits(err, cor))
                else:
                    print(convert_to_wdiff(err, cor))
    # Write to CSV
    with open("train.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["hi_err", "hi_corr", "error"])  # Header row
        writer.writerows(output_rows)  # Data rows
    print("Training data saved to training_data.csv")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Insert Errors into a sentence file')
    parser.add_argument('input_file', default='hindi.output', nargs='?', help='input filename')
    parser.add_argument('--single', nargs='?', const=0.6, type=int, help='format')
    parser.add_argument('--edits', action='store_true', help='format')
    parser_args = parser.parse_args()

    random.seed(1234)

    main(parser_args)
