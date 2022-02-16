#! /bin/bash
find ./ -name 'assertion_*.txt' -delete

echo "Compiling the assertions...!!!"
bison -d dbdetector.y
flex dbdetector.l

echo "Checking if necessary files exist or not...!!!"
FILE1=./dbdetector.tab.c
FILE2=./lex.yy.c
# test -f ./dbdetector.tab.c && echo "$FILE1 exists."
# test -f ./lex.yy.c && echo "$FILE2 exists."

if [[ -f "$FILE1" && -f "$FILE2" ]]; then
    echo "All necessary files exist...!!!"
    g++ dbdetector.tab.c lex.yy.c -lfl -o dbdetector
    ./dbdetector assertions
fi


if [ ! -f "$FILE1" ]; then
	echo "$FILE1 doesnot exist...!!!"
fi

if [ ! -f "$FILE2" ]; then
	echo "$FILE2 doesnot exist...!!!"
fi

echo "\n\t Please provide <p4filename.p4>:"
read p4_file_name

echo "\n\t Please provide <dot file name>:"
read dot_file_name

echo "\n\t Please provide <json file name>:"
read json_file_name

echo "\n\t Please provide <control block name(eg: \"MyIngress\")>:"
read ctrl_blk_name

echo "\n\t Please provide <user metadata variable name>:"
read meta_name

echo "\n\t Please provide header file name (eg: header.p4 \"Please include path as well if required.\"):"
read header_file

path=`pwd`
path="${path}/.."
path=`find ${path} -name ${p4_file_name}`
path=`dirname ${path}`
echo $path
cd ${path}
python p4_augmenter.py $p4_file_name $dot_file_name $json_file_name $ctrl_blk_name $meta_name

python assertion_augmenter.py ${p4_file_name%".p4"}"_augmented.p4" $ctrl_blk_name $meta_name $header_file

find ./ -name '*.pkl' -delete