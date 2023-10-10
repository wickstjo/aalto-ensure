# ---------- Producer --------------
dataset = h5py.File('../dataset_creator/runs/draft_v1.hdf5', 'r')
activity = dataset['is_active']
sensors = dataset['sensors']
metadata = json.loads(dataset['metadata'][()])
n_frames = metadata["n_frames"]
sensor_data_iters = {key: iter(sensors[key]) for key in sensors.keys()}
queue = Queue()

for frame in range(n_frames):
  for sensor_name, data_iter in sensor_data_iters.items():
    active = activity[sensor_name][frame]
    if active:
      # Sensor has data for this frame only if it is marked as active
      sensor_data = data_iter.__next__()
      queue.put(sensor_data) # Data is in bytes

# ---------- Consumer --------------
yolo = Model(yolo_model_name)
response_queue = Queue()
while not queue.empty():
  data = queue.get() # Data is in bytes
  img = Image.open(io.BytesIO(data))
  results = yolo.forward(asarray(img))
  response_queue.put(results)