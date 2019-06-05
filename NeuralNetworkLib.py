import numpy as np
import math
import random
import copy

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def dsigmoid(y):
    return y * (1 - y)

def mutate_one(value, rate):
    r = random.random()
    if (r < rate):
        new_value = np.random.normal(0, 0.20)
        return new_value
    else:
        return value

class NeuralNetwork():
    # This is sloppy and it's only here to allow me to make a copy of a nn for the genetic algo
    def __init__(self, a, b=None, c=None):
        # basically, if one thing is passed to the function it will treat it like another nn and copy its parameters
        if (b == None):
            self.input_nodes = a.input_nodes
            self.hidden_nodes = a.hidden_nodes
            self.output_nodes = a.output_nodes

            self.weights_ih = a.weights_ih
            self.weights_ho = a.weights_ho

            self.bias_h = a.bias_h
            self.bias_o = a.bias_o

        # Otherwise it will create a new one with a, b, and c being the number of input, hidden, and output nodes respectively
        else:
            self.input_nodes = a
            self.hidden_nodes = b
            self.output_nodes = c

            self.weights_ih = np.random.rand(self.hidden_nodes, self.input_nodes)
            self.weights_ho = np.random.rand(self.output_nodes, self.hidden_nodes)
            self.weights_ih = (self.weights_ih * 2) - 1
            self.weights_ho = (self.weights_ho * 2) - 1

            self.bias_h = np.random.rand(self.hidden_nodes)
            self.bias_o = np.random.rand(self.output_nodes)
            self.bias_h = (self.bias_h * 2) - 1
            self.bias_o = (self.bias_o * 2) - 1  
            self.learning_rate = 0.05

    # Takes a np array as input and returns a np array of guesses
    def feedforward(self, inputs):

        # Generate hidden 1d matrix
        hidden = self.weights_ih.dot(inputs)
        hidden = hidden + self.bias_h
        # Turn my sigmoid activation function into a vectorized function that can be called on all element of a matrix
        sigmoid_vec = np.vectorize(sigmoid)
        hidden = sigmoid_vec(hidden)

        # Generate output 1d matrix
        output = self.weights_ho.dot(hidden)
        output = output + self.bias_o
        output = sigmoid_vec(output)

        return output

    # BackProp using a np array as input and a np array as target
    def train(self, inputs, targets):
        # Generate hidden 1d matrix
        hiddens = self.weights_ih.dot(inputs)
        hiddens = hiddens + self.bias_h
        # Turn my sigmoid activation function into a vectorized function that can be called on all element of a matrix
        sigmoid_vec = np.vectorize(sigmoid)
        hiddens = sigmoid_vec(hiddens)

        # Generate output 1d matrix
        outputs = self.weights_ho.dot(hiddens)
        outputs = outputs + self.bias_o
        outputs = sigmoid_vec(outputs)

        # calc error, Target - outputs
        output_errors = targets - outputs

        dsigmoid_vec = np.vectorize(dsigmoid)

        output_gradient = np.matmul(dsigmoid_vec(outputs),(output_errors)) * self.learning_rate
        weights_ho_deltas = output_gradient * np.transpose(hiddens)

        self.weights_ho = self.weights_ho + weights_ho_deltas
        self.bias_o = self.bias_o + output_gradient

        # calc hidden layer errors 
        hidden_errors = (np.transpose(self.weights_ho)).dot(output_errors)

        hidden_gradient = np.matmul(dsigmoid_vec(hiddens),(hidden_errors)) * self.learning_rate
        weights_ih_deltas = hidden_gradient * np.transpose(inputs)

        self.weights_ih = self.weights_ih + weights_ih_deltas
        self.bias_h = self.bias_h + hidden_gradient

    def copy(self):
        return NeuralNetwork(self)

    # When called, call the mutate_one function on every value in the weights and bias' matrices
    def mutate(self, mut_rate):
        mutate_all = np.vectorize(mutate_one)
        self.weights_ih = mutate_all(self.weights_ih, mut_rate)
        self.weights_ho = mutate_all(self.weights_ho, mut_rate)
        self.bias_h = mutate_all(self.bias_h, mut_rate)
        self.bias_o = mutate_all(self.bias_o, mut_rate)


if __name__ == "__main__":
    nn = NeuralNetwork(2,10,1)

    training_data = [
    {
        'input' : [0,0],
        'target' : [0],
    },
    {
        'input' : [1,0],
        'target' : [1],
    },
    {
        'input' : [0,1],
        'target' : [1],
    },
    {
        'input' : [1,1],
        'target' : [0],
    }]

    for i in range(50000):
        data = random.choice(training_data)
        nn.train(data.get('input'), data.get('target'))

    print(nn.feedforward([0,0]))
    print(nn.feedforward([1,0]))
    print(nn.feedforward([0,1]))
    print(nn.feedforward([1,1]))