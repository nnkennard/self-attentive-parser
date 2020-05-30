import re
import benepar
import json
import nltk
from tqdm import tqdm
import sys

def flatten(nonflat):
  return sum(nonflat, [])

def remap_spans(spans, token_start, token_end, subtoken_offset):

  new_spans = []
  for start, end in spans:
    new_start = subtoken_offset[token_start[start]] + token_start[start]
    new_end = subtoken_offset[token_end[end]] + token_end[end]
    new_spans.append([new_start, new_end])
  return new_spans

CONSTITUENT_PATTERN = "([\(\)]+)"

def convert_example(example_line, parser):
  original_obj = json.loads(example_line)
  token_start, token_end = original_obj["bpe_maps"]
  subtoken_offsets = original_obj["subtoken_offsets"]
  sentence_offset = 0
  spans = []
  for sentence in original_obj["token_sentences"]:
    parse = parser.parse(sentence)
    parse_lines = str(parse).replace("\n", " ")
    curr_seg = ""
    segments = []
    pos_list = []
    tokens = []

    WORD_PATTERN = "(\([^\s\(\)]+\s[^\s\(\)]+\))" # Matches (RB And)

    segment_parts = re.split(WORD_PATTERN, parse_lines)
    print("\n".join(segment_parts))
    while segment_parts:
      new_seg = segment_parts.pop(0)
      if re.match(WORD_PATTERN, new_seg):
        pos, token = new_seg[1:-1].split() # This starts and ends with ()
        pos_list.append(pos)
        tokens.append(token)
        curr_seg += "*"
        while segment_parts and re.match("^[\)]+$", segment_parts[0].strip()):
          # Closing parens go on previous line
          curr_seg += segment_parts.pop(0)
        segments.append(curr_seg)
        curr_seg = ""
      else:
        curr_seg += new_seg

    assert len(tokens) == len(pos_list) == len(segments)
    print("\n".join(re.sub("\s+", "", i) for i in segments))
  
    parse.pretty_print()

    exit()
    for subtree in parse.subtrees():
      subsequence = str(subtree.flatten())[:-1].split()[1:]
      for start in range(len(sentence)):
        maybe_exclusive_end = start + len(subsequence)
        if sentence[start:maybe_exclusive_end] == subsequence:
          spans.append((sentence_offset + start,
                        sentence_offset + maybe_exclusive_end - 1))
    sentence_offset += len(sentence)

  assert not original_obj.get("injected_mentions", []) # Either it was [] or undefined, now def []
  original_obj["injected_mentions"] = remap_spans(list(set(spans)), token_start, token_end, subtoken_offsets)
  return json.dumps(original_obj)

def main():
  input_file, output_file = sys.argv[1:3]
  benepar.download('benepar_en2')
  parser = benepar.Parser("benepar_en2")

  converted_examples = []
  with open(input_file, 'r') as f:
    input_examples = f.readlines()
    for line in tqdm(input_examples):
      converted_examples.append(convert_example(line, parser))
  with open(output_file, 'w') as g:
    g.write("\n".join(converted_examples))


if __name__ == "__main__":
  main()
