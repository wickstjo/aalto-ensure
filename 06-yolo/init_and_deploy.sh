# MAKE SERVICE DIRECTORY ARGUMENT MANDATORY
if [[ -z $1 ]]
then
  echo "ERROR: DEFINE THE NUMBER OF TOPIC PARTITIONS";
  exit 1;
fi

# INITIALIZE KAFKA TOPICS & WAIT FOR ABIT
python3 app/kafka_init.py -n $1

sleep 5
echo "KAFKA WAS OK, DELOYING PODS..."
sleep 1

# THEN DEPLOY FRESH PODS
kubectl apply -f yolo_depl.yaml