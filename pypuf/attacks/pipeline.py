"""
Pipeline for Basic Attacks on (XOR) Arbiter PUFS
"""

from ..io import random_inputs, ChallengeResponseSet
from ..simulation.delay import LTFArray
import torch
from torch.optim import Adam
from torch.nn import MSELoss
from sklearn.metrics import accuracy_score
from numpy.random import RandomState
from tqdm import tqdm as tqdm_normal
from tqdm.notebook import tqdm as tqdm_notebook
from .models.base_model import BasicModel
from numpy import array, ones

from typing import Optional


def create_test_and_train(input_size, train_size=10000, test_size=100, k=2, random_seed=1234, device='cpu'):
    '''
    Generate training and test data and convert to pytorch Tensors

    :param input_size:
    :param train_size:
    :param test_size:
    :param k:
    :param random_seed:
    :param device:
    :return:
    '''
    instance = LTFArray(ones(shape=(k, input_size)), transform='id')
    X_train = random_inputs(n=input_size, N=train_size, seed=random_seed)
    y_train = instance.eval(X_train)
    X_test = random_inputs(n=input_size, N=test_size, seed=random_seed)
    y_test = instance.eval(X_test)

    X_train = torch.FloatTensor(X_train).to(device)
    y_train = torch.FloatTensor(y_train).to(device)
    y_train = y_train.view(train_size, 1)
    X_test = torch.FloatTensor(X_test).to(device)
    y_test = torch.FloatTensor(y_test).to(device)

    return X_train, y_train, X_test, y_test


def train(model, X_train, y_train, criterion, optimizer, batch_size, epochs=10000, notebook=False):
    '''
    Train the model

    :param model:
    :param X_train:
    :param y_train:
    :param criterion:
    :param optimizer:
    :param batch_size:
    :param notebook: set to True if using a jupyter notebook for a better progress bar
    :return: losses
    '''
    if notebook:
        progress_bar = tqdm_notebook
    else:
        progress_bar = tqdm_normal

    losses = []

    for t in progress_bar(range(epochs)):
        j = batch_size
        for i in range(0, len(X_train), batch_size):
            y_pred = model(X_train[i:j])
            loss = criterion(y_pred, y_train[i:j])
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            i = j
    
        losses.append(loss.item())

    return losses

def pipeline(
    input_size: int = 64,
    k: int = 1,
    random_seed: int = 1234,
    device: Optional[str] = None,
    model: Optional[torch.nn.Module] = None,
    criterion: Optional[object] = None,
    optimizer: Optional[object] = None,
    batch_size: Optional[int] = None,
    notebook: bool = False):

    '''

    :param input_size:
    :param k:
    :param random_seed:
    :param device:
    :param model:
    :param criterion:
    :param optimizer:
    :param batch_size:
    :param notebook:
    :return:
    '''

    X_train, y_train, X_test, y_test = create_test_and_train(input_size=input_size, k=k, random_seed=random_seed, device=device)

    if device is None:
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    if model is None:
        model = BasicModel(input_size, k, device).to(device)

    if criterion is None:
        criterion = MSELoss()

    if optimizer is None:
        optimizer = Adam(model.parameters(), lr=0.00001)

    if batch_size is None:
        batch_size = len(X_train)

    losses = train(model=model, X_train=X_train, y_train=y_train, criterion=criterion, optimizer=optimizer, batch_size=batch_size, notebook=notebook)

    print(losses)

    predictions = []
    with torch.no_grad():
       for x in X_test:
            predictions.append(model.predict(x))
            
            
    print(accuracy_score(y_test.cpu().numpy(), predictions))