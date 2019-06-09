import utils.dataloaders as dataloaders
import numpy as np
from utils.arg_extractor import get_args
from utils.experiment_builder import ExperimentBuilder
from utils.models import ConvLSTMModel
import torch
args, device = get_args()  # get arguments from command line
rng = np.random.RandomState(seed=args.seed)  

torch.manual_seed(seed=args.seed)
args.toy = True
train_data = dataloaders.MilanDataLoader(_set = 'train',toy = args.toy)
valid_data = dataloaders.MilanDataLoader(_set = 'valid',toy = args.toy)
test_data  = dataloaders.MilanDataLoader(_set = 'test', toy = args.toy)
example_x, example_y = train_data.__getitem__(1)
seq_start = example_x.shape[0]
seq_length = seq_start + example_y.shape[0]
model = ConvLSTMModel(input_size = args.image_height, seq_start = args.seq_start, seq_length = args.seq_length, batch_size = args.batch_size)
experiment = ExperimentBuilder(network_model=model,
                                    experiment_name=args.experiment_name,
                                    num_epochs=args.num_epochs,
                                    weight_decay_coefficient=args.weight_decay_coefficient,
                                    continue_from_epoch=args.continue_from_epoch,
                                    device=device,
                                    train_data=train_data, val_data=valid_data,
                                    test_data=test_data)  # build an experiment object
experiment_metrics, test_metrics = experiment.run_experiment()