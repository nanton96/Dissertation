import utils.dataloaders as dataloaders
import numpy as np
from utils.arg_extractor import get_args
from utils.new_experiment_builder import ExperimentBuilder
from utils.new_models import EF,Encoder,Forecaster,ConvLSTM
import torch
from torch.utils.data import DataLoader
args, device = get_args()  # get arguments from command line
rng = np.random.RandomState(seed=args.seed)  
from collections import OrderedDict

torch.manual_seed(seed=args.seed)
args.toy = False
batch_size = args.batch_size

train_dataset = dataloaders.MilanDataLoader(_set = 'train',toy = args.toy,create_channel_axis=True)
valid_dataset = dataloaders.MilanDataLoader(_set = 'valid',toy = args.toy,create_channel_axis=True)
test_dataset  = dataloaders.MilanDataLoader(_set = 'test', toy = args.toy,create_channel_axis=True)

train_data = DataLoader(train_dataset,batch_size=args.batch_size,shuffle=True,num_workers=4,drop_last = True)
valid_data = DataLoader(valid_dataset,batch_size=args.batch_size,shuffle=True,num_workers=4,drop_last = True)
test_data = DataLoader(test_dataset,batch_size=args.batch_size,shuffle=True,num_workers=4,drop_last = True)


seq_input = 12
seq_output = 6
seq_length = 18
###### Define encoder #####
encoder_architecture = [
    [ #in_channels, out_channels, kernel_size, stride, padding
        OrderedDict({'conv1_leaky_1': [1, 8, 4, 2, 1]}),
        OrderedDict({'conv2_leaky_1': [64, 192, 4, 2, 1]}),
        OrderedDict({'conv3_leaky_1': [192, 192, 3, 2, 1]}),
    ],

    [
        ConvLSTM(input_channel=8, num_filter=64, b_h_w=(batch_size, 50, 50),
                 kernel_size=3, stride=1, padding=1,device=device,seq_len=seq_input),
        ConvLSTM(input_channel=192, num_filter=192, b_h_w=(batch_size, 25, 25),
                 kernel_size=3, stride=1, padding=1,device=device,seq_len=seq_input),
        ConvLSTM(input_channel=192, num_filter=192, b_h_w=(batch_size, 13, 13),
                 kernel_size=3, stride=1, padding=1,device=device,seq_len=seq_input),
    ]
]
encoder = Encoder(encoder_architecture[0],encoder_architecture[1]).to(device)
###### Define decoder #####
forecaster_architecture = [
    [
        OrderedDict({'deconv1_leaky_1': [192, 192, 3, 2, 1]}),
        OrderedDict({'deconv2_leaky_1': [192, 64, 4, 2, 1]}),
        OrderedDict({
            'deconv3_leaky_1': [64, 8, 4, 2, 1],
            'conv3_leaky_2': [8, 8, 3, 1, 1],
            'conv3_3': [8, 1, 1, 1, 0]
        }),
    ],

    [
        ConvLSTM(input_channel=192, num_filter=192, b_h_w=(batch_size, 13, 13),
                 kernel_size=3, stride=1, padding=1,device=device,seq_len=seq_output),
        ConvLSTM(input_channel=192, num_filter=192, b_h_w=(batch_size, 25, 25),
                 kernel_size=3, stride=1, padding=1,device=device,seq_len=seq_output),
        ConvLSTM(input_channel=64, num_filter=64, b_h_w=(batch_size, 50, 50),
                 kernel_size=3, stride=1, padding=1,device=device,seq_len=seq_output),
    ]
]
forecaster=Forecaster(forecaster_architecture[0],forecaster_architecture[1],seq_output).to(device)

model = EF(encoder,forecaster)
experiment = ExperimentBuilder(network_model=model,seq_start = seq_input,seq_length = seq_length,
                                    experiment_name=args.experiment_name,
                                    num_epochs=args.num_epochs,
                                    lr =args.learning_rate, weight_decay_coefficient=args.weight_decay_coefficient,
                                    continue_from_epoch=args.continue_from_epoch,
                                    device=device,
                                    train_data=train_data, val_data=valid_data,
                                    test_data=test_data)  # build an experiment object
experiment_metrics, test_metrics = experiment.run_experiment()