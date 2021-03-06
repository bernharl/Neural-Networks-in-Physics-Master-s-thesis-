import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
import numpy as np

torch.manual_seed(1)
device = "cuda:1"


class SineData(torch.utils.data.Dataset):
    def __init__(self):
        tmp = torch.load("train_dataset.pt")
        self.y = torch.from_numpy(tmp[1][:, :, np.newaxis]).float().to(device)
        self.x = torch.from_numpy(tmp[0][:, :, np.newaxis]).float().to(device)

        tmp = torch.load("test_dataset.pt")
        self.y_test = torch.from_numpy(tmp[1][:, :, np.newaxis]).float().to(device)
        self.x_test = torch.from_numpy(tmp[0][:, :, np.newaxis]).float().to(device)

        tmp = torch.load("oos.pt")
        self.y_oos = (
            torch.from_numpy(tmp[1][np.newaxis, :, np.newaxis]).float().to(device)
        )
        self.x_oos = (
            torch.from_numpy(tmp[0][np.newaxis, :, np.newaxis]).float().to(device)
        )
        # print(self.x_test.shape, self.x_oos.shape)
        # print(self.y_test.shape, self.y_oos.shape)
        # print(tmp.shape)
        # exit()


class Model(nn.Module):
    def __init__(self, hidden=10, layers=1, dropout=0):
        super(Model, self).__init__()
        self.lstm = nn.LSTM(
            input_size=1, hidden_size=hidden, num_layers=layers, batch_first=True
        )
        self.dropout = nn.Dropout(dropout)
        self.output = nn.Linear(hidden, 1)
        

    def forward(self, x):
        #print(x.shape)
        #exit()
        output, (h_n, c_n) = self.lstm(x)
        return self.output(self.dropout(output))

if __name__=="__main__":
    data = SineData()
    model = Model(51, 2, 0.1).to(device)
    optimizer = torch.optim.LBFGS(model.parameters(), lr=0.01)
    #optimizer = torch.optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
    loss_func = nn.MSELoss()
    model.train()
    # print(data.y.shape)
    # exit()
    for i in range(150):

        def closure():
            optimizer.zero_grad()
            # print(x)
            # exit()
            y_pred = model.forward(data.x)
            # print(y_pred.shape)
            # exit()
            loss = loss_func(data.y, y_pred)
            print(f"Epoch {i}: {loss.item()}")
            loss.backward()
            return loss
        loss = closure()
        #optimizer.step()
        optimizer.step(closure)

    # Split
    batch = 15
    with torch.no_grad():
        y_pred = model(data.x).detach()[batch].flatten().cpu()
        y_pred_test = model(data.x_test).detach()[batch].flatten().cpu()
    plt.plot(
        data.x.detach()[batch].flatten().cpu(), data.y.detach()[batch].flatten().cpu(), label="true"
    )
    plt.plot(data.x.detach()[batch].flatten().cpu(), y_pred, label="pred")

    plt.plot(
        data.x_test.detach()[batch].flatten().cpu(),
        data.y_test.detach()[batch].flatten().cpu(),
        label="true test",
    )
    plt.plot(data.x_test.detach()[batch].flatten().cpu(), y_pred_test, label="pred test")

    plt.legend()
    plt.savefig("split.png")
    plt.close()


    # Combined
    x_comb = torch.cat([data.x, data.x_test], 1)
    y_comb = torch.cat([data.y, data.y_test], 1)
    with torch.no_grad():
        y_pred = model(x_comb).detach()[batch].flatten().cpu()
    plt.plot(
        x_comb.detach()[batch].flatten().cpu(), y_comb.detach()[batch].flatten().cpu(), label="true"
    )
    plt.plot(x_comb.detach()[batch].flatten().cpu(), y_pred, label="pred")


    plt.legend()
    plt.savefig("combined.png")
    plt.close()

    # OOS:
    with torch.no_grad():
        y_pred_oos = model(data.x_oos).detach()[0].flatten().cpu()
    plt.plot(
        data.x_oos.detach()[0].flatten().cpu(),
        data.y_oos.detach()[0].flatten().cpu(),
        label="true",
    )
    plt.plot(data.x_oos.detach()[0].flatten().cpu(), y_pred_oos, label="pred")

    plt.legend()
    plt.savefig("oos.png")
    plt.close()
