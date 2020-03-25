import benepar
import json
import nltk
import sys

def convert_example(example_line, parser):
  original_obj = json.loads(example_line)
  sentence_offset = 0
  spans = []
  for sentence in original_obj["sentences"]:
    parse = parser.parse(sentence)
    for subtree in parse.subtrees():
      subsequence = str(subtree.flatten())[:-1].split()[1:]
      for start in range(len(sentence)):
        maybe_exclusive_end = start + len(subsequence)
        if sentence[start:maybe_exclusive_end] == subsequence:
          spans.append((sentence_offset + start,
                        sentence_offset + maybe_exclusive_end - 1))
    sentence_offset += len(sentence)
  assert not original_obj.get("injected_mentions", []) # Either it was [] or undefined, now def []
  original_obj["injected_mentions"] = list(set(spans))
  return json.dumps(original_obj)

def main():
  input_file, output_file = sys.argv[1:3]
  benepar.download('benepar_en2')
  parser = benepar.Parser("benepar_en2")

  converted_examples = []
  with open(input_file, 'r') as f:
    for i, line in enumerate(f):
      print(i)
      converted_examples.append(convert_example(line, parser))
  with open(output_file, 'w') as g:
    g.write("\n".join(converted_examples))

  pass


if __name__ == "__main__":
  main()
