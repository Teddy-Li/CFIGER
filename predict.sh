echo "Prediction for $1 started!"
date
python -u predict.py --slice_id $1 --gpu_id $2
date
echo "Done!"