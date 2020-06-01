import sys
import benepar
import re
import sys
from tqdm import tqdm

import conll_lib


def conllify_parse(parse):
  parse_lines = str(parse).replace("\n", " ")
  curr_seg = ""
  segments = []
  pos_list = []
  tokens = []

  WORD_PATTERN = "(\([^\s\(\)]+[ ]+[^\s\(\)]+\))" # Matches (RB And)

  segment_parts = [part.strip()
                   for part in re.split(WORD_PATTERN, parse_lines)]
  
  while segment_parts:
    new_seg = segment_parts.pop(0)
    if re.match(WORD_PATTERN, new_seg):
      pos, token = new_seg[1:-1].split() # This starts and ends with ()
      pos_list.append(pos)
      tokens.append(token)
      curr_seg += "*"
      while segment_parts and segment_parts[0].startswith(")"):
        # Closing parens go on previous token
        curr_seg += ")"
        segment_parts[0] = segment_parts[0][1:] # Re-add the rest
      segments.append(re.sub("\s+", "", curr_seg))
      curr_seg = ""
    else:
      curr_seg += new_seg

  return pos_list, segments


def add_predconst(input_file, parser):
  assert input_file.endswith(".txt")
  output_file = input_file.replace(".txt", ".miniconll")

  listified_dataset = conll_lib.listify_conll_dataset(input_file)
  new_dataset = []
  for document in tqdm(listified_dataset):
    new_document = []
    for sentence in document:
      new_sentence = []
      if len(sentence) == 1:
        if sentence[0][0].startswith("#"):
          new_document.append(sentence)
          continue
        else:
          # There are some empty sentences in PreCo
          new_sentence.append(sentence[0][:10] + [sentence[0][-1], "_POS", "_PARSE"])
          
      else:
        tokens = [fields[3] for fields in sentence]
        if ' ' in tokens:
          pos_list, parse_list = ["_POS"] * len(tokens), ["_PARSE"] * len(tokens)
        else:
          parse = parser.parse(tokens)
          pos_list, parse_list = conllify_parse(parse)
        for old_fields, pred_pos, pred_parse in zip(sentence, pos_list, parse_list):
          new_sentence.append(old_fields[:10] + [old_fields[-1], pred_pos, pred_parse])
        
        assert len(pos_list) == len(parse_list) == len(sentence)
      new_document.append(new_sentence)
    new_dataset.append(new_document)

  conll_lib.write_listified_dataset_to_file(new_dataset, output_file)
         
      

def main():
  input_conll_file = sys.argv[1]
  benepar.download('benepar_en2')
  parser = benepar.Parser("benepar_en2")
  add_predconst(input_conll_file, parser)
  


if __name__ == "__main__":
  main()
