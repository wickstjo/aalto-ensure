# MAKE SERVICE DIRECTORY ARGUMENT MANDATORY 
if [[ -z $1 ]]
then
  echo "ERROR: DEFINE THE NUMBER OF TOPIC PARTITIONS";
  exit 1;
fi

python3 app/kafka_init.py -n $1