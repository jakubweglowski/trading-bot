import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from LSTM import LSTM
from data_prepare import prepare_data_for_LSTM_training
from data_prepare import prepare_data_for_LSTM

class TimeSeriesDataset(Dataset):
    def __init__(self, X, y):
        self.X = X
        self.y = y

    def __len__(self):
        return len(self.X)

    def __getitem__(self, i):
        return self.X[i], self.y[i]


class LSTM_Exp:
    

    def __init__(self,input_size, hidden_size, num_stacked_layers,data,window,skip,split,
                 device='cpu',learning_rate=0.0001,num_epochs=20,batch_size=16):
        self.input_size=input_size
        self.hidden_size=hidden_size
        self.num_stacked_layers=num_stacked_layers
        self.device=device
        
        self.model=LSTM(input_size, hidden_size, num_stacked_layers,device).to(self.device)
        
        self.learning_rate = learning_rate
        self.num_epochs = num_epochs
        self.loss_function = nn.MSELoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        self.window=window
        
        X_train,y_train,X_test,y_test,self.scaler=prepare_data_for_LSTM_training(data,window,skip,split)
        
        self.train_dataset = TimeSeriesDataset(X_train, y_train)
        self.test_dataset = TimeSeriesDataset(X_test, y_test)

        self.train_loader = DataLoader(self.train_dataset, batch_size=batch_size, shuffle=True)
        self.test_loader = DataLoader(self.test_dataset, batch_size=batch_size, shuffle=False)
        
    def train_one_epoch(self,epoch):
        self.model.train(True)
        print(f'Epoch: {epoch + 1}')
        running_loss = 0.0

        for batch_index, batch in enumerate(self.train_loader):
            x_batch, y_batch = batch[0].to(self.device), batch[1].to(self.device)

            output = self.model(x_batch)
            loss = self.loss_function(output, y_batch)
            running_loss += loss.item()

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            if batch_index % 100 == 99:  # print every 100 batches
                avg_loss_across_batches = running_loss / 100
                print('Batch {0}, Loss: {1:.3f}'.format(batch_index+1,
                                                    avg_loss_across_batches))
                running_loss = 0.0
        print()
       
    def validate_one_epoch(self,epoch):
        self.model.train(False)
        running_loss = 0.0

        for batch_index, batch in enumerate(self.test_loader):
            x_batch, y_batch = batch[0].to(self.device), batch[1].to(self.device)

            with torch.no_grad():
                output = self.model(x_batch)
                loss = self.loss_function(output, y_batch)
                running_loss += loss.item()

        avg_loss_across_batches = running_loss / len(self.test_loader)

        print('Val Loss: {0:.3f}'.format(avg_loss_across_batches))
        print('***************************************************')
        print() 
        
    def train(self):
        for epoch in range(self.num_epochs):
            self.train_one_epoch(epoch)
            self.validate_one_epoch(epoch)
        
        return self.model,self.scaler
    
    def test(self,X_test):
        X_test=np.array(X_test)
        srednie=np.mean(X_test,axis=1)
        X_test=X_test[:,:,0]
        X_test=np.concatenate((srednie, X_test), axis=1)
        X_test=self.scaler.transform(X_test)
        X_test=X_test.reshape(-1,self.window+1,1)
        X_test=X_test[:,1:,:]
        X_test=torch.Tensor(X_test)
        
        with torch.no_grad():
            predicted = self.model(X_test.to(self.device)).to(self.device).numpy()
            
        Y_test=np.concatenate((np.array(X_test)[:,:,0],predicted), axis=1)
        Y_test=self.scaler.inverse_transform(Y_test)
        return Y_test[:,-1]
    
    def signaling(self,X_test,granica):
        
        Y_pred=self.test(X_test)
        sygnaly=[]
     
        for i in range(len(Y_pred)):
            if Y_pred[i]>(1+granica)*X_test[i,-1]:
                sygnaly.append(1)
            elif Y_pred[i]<(1-granica)*X_test[i,-1]:
                sygnaly.append(-1)
            else:
                sygnaly.append(0)
                
        return sygnaly
    
    def Decision(self,data,granica,tytul=0):
        czas=data.index
        X=prepare_data_for_LSTM(data,self.window,skip=1)
        X=X.reshape(-1,self.window,1)
        
        sygnaly=self.signaling(X,granica)
        
        df=pd.DataFrame({tytul:sygnaly})
        df=df.set_index(czas[self.window-1:])
        
        return df

        
        