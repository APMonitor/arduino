close all; clear all; clc

addpath('apm')

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Configuration
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% number of terms
ny = 2; % output coefficients
nu = 1; % input coefficients
% number of inputs
ni = 1;
% number of outputs
no = 1;
% load data and parse into columns
data = load('data_step_test.csv');
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% generate time-series model
sysd = apm_id(data,ni,nu,ny);

% plt.figure(1)
% plt.subplot(2,1,1)
% plt.plot(data[:,0],ypred,'r-',LineWidth=2)
% plt.plot(data[:,0],data[:,2],'b--',LineWidth=2)
% plt.legend(['Predicted','Measured'],loc='best')
% plt.ylabel('Temp (K)')
% 
% plt.subplot(2,1,2)
% plt.plot(data[:,0],data[:,1],'k-',LineWidth=2)
% plt.legend(['Heater'],loc='best')
% plt.ylabel('Heater')
% plt.show()
