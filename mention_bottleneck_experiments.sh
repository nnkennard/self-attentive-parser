DATA_HOME=$1
source sap_ve/bin/activate

mkdir $DATA_HOME"/processed/conll/predconst/"
for subset in 'test' 'train' 'dev'
do
  for seg_len in 'SEGMENTED_384' 'SEGMENTED_512'
  do
    input_file=$DATA_HOME"/processed/conll/classic/"$subset"_"$seg_len".jsonl"
    output_file=$DATA_HOME"/processed/conll/predconst/"$subset"_"$seg_len".jsonl"
    python create_predconst_file.py $input_file $output_file
  done
done

mkdir $DATA_HOME"/processed/preco/predconst/"
for subset in 'train' 'dev' 'test'
do
  for seg_len in 'SEGMENTED_384' 'SEGMENTED_512'
  do
    input_file=$DATA_HOME"/processed/preco/classic/"$subset"_"$seg_len".jsonl"
    output_file=$DATA_HOME"/processed/preco/predconst/"$subset"_"$seg_len".jsonl"
    python create_predconst_file.py $input_file $output_file
  done
done
