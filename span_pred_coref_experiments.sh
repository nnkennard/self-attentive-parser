DATA_HOME=$1
source sap_ve/bin/activate

for dataset in  'preco' #'conll'
do
  for subset in 'test' 'train' 'dev'
  do
    input_file=$DATA_HOME"/original/"$dataset"/"$subset".txt"
    echo $input_file
    python add_predconst.py $input_file
  done
done

