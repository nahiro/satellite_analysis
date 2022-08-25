#!/usr/bin/env python
import os
import sys
import re
import numpy as np
import pandas as pd
from itertools import combinations
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score,mean_squared_error
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
PARAMS = ['Sb','Sg','Sr','Se1','Se2','Se3','Sn1','Sn2','Ss1','Ss2',
          'Nb','Ng','Nr','Ne1','Ne2','Ne3','Nn1','Nn2','Ns1','Ns2',
          'NDVI','GNDVI','RGI','NRGI']
OBJECTS = ['BLB','Blast','Borer','Rat','Hopper','Drought']
CRITERIAS = ['RMSE_test','R2_test','AIC_test','RMSE_train','R2_train','AIC_train','BIC_train']
EPSILON = 1.0e-6

# Default values
OUT_FNAM = 'sentinel2_score_fit.csv'
X_PARAM = ['Nb','Ng','Nr','Ne1','Ne2','Ne3','Nn1','Nn2','Ns1','Ns2','NDVI','GNDVI','NRGI']
Y_PARAM = ['BLB']
VMAX = 5.0
NX_MIN = 1
NX_MAX = 2
NCHECK_MIN = 1
NMODEL_MAX = 3
CRITERIA = 'RMSE_test'
N_CROSS = 5
Y_THRESHOLD = ['BLB:0.2','Blast:0.2','Borer:0.2','Rat:0.2','Hopper:0.2','Drought:0.2']
Y_MAX = ['BLB:9.0','Blast:9.0','Drought:9.0']
Y_INT = ['BLB:2.0','Blast:2.0','Borer:0.2','Rat:0.2','Hopper:0.2','Drought:2.0']
Y_FACTOR = ['BLB:BLB:1.0','Blast:Blast:1.0','Borer:Borer:1.0','Rat:Rat:1.0','Hopper:Hopper:1.0','Drought:Drought:1.0']
FIGNAM = 'sentinel2_score_fit.pdf'

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-i','--inp_list',default=None,help='Input file list (%(default)s)')
parser.add_argument('-I','--inp_fnam',default=None,action='append',help='Input file name (%(default)s)')
parser.add_argument('-O','--out_fnam',default=OUT_FNAM,help='Output file name (%(default)s)')
parser.add_argument('-x','--x_param',default=None,action='append',help='Candidate explanatory variable ({})'.format(X_PARAM))
parser.add_argument('-y','--y_param',default=None,action='append',help='Objective variable ({})'.format(Y_PARAM))
parser.add_argument('--y_threshold',default=None,action='append',help='Threshold for limiting non-optimized objective variables ({})'.format(Y_THRESHOLD))
parser.add_argument('--y_max',default=None,action='append',help='Max score ({})'.format(Y_MAX))
parser.add_argument('--y_int',default=None,action='append',help='Score step for mean value fitting ({})'.format(Y_INT))
parser.add_argument('--y_factor',default=None,action='append',help='Conversion factor to objective variable equivalent ({})'.format(Y_FACTOR))
parser.add_argument('-V','--vmax',default=VMAX,type=float,help='Max variance inflation factor (%(default)s)')
parser.add_argument('-n','--nx_min',default=NX_MIN,type=int,help='Min number of explanatory variable in a formula (%(default)s)')
parser.add_argument('-N','--nx_max',default=NX_MAX,type=int,help='Max number of explanatory variable in a formula (%(default)s)')
parser.add_argument('-m','--ncheck_min',default=NCHECK_MIN,type=int,help='Min number of explanatory variables for multico. check (%(default)s)')
parser.add_argument('-M','--nmodel_max',default=NMODEL_MAX,type=int,help='Max number of formula (%(default)s)')
parser.add_argument('-C','--criteria',default=CRITERIA,help='Selection criteria (%(default)s)')
parser.add_argument('-c','--n_cross',default=N_CROSS,type=int,help='Number of cross validation (%(default)s)')
parser.add_argument('-a','--amin',default=None,type=float,help='Min age in day (%(default)s)')
parser.add_argument('-A','--amax',default=None,type=float,help='Max age in day (%(default)s)')
parser.add_argument('-F','--fignam',default=FIGNAM,help='Output figure name for debug (%(default)s)')
parser.add_argument('--mean_fitting',default=False,action='store_true',help='Mean value fitting (%(default)s)')
parser.add_argument('-d','--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
parser.add_argument('-b','--batch',default=False,action='store_true',help='Batch mode (%(default)s)')
args = parser.parse_args()
if args.inp_list is None and args.inp_fnam is None:
    raise ValueError('Error, args.inp_list={}, args.inp_fnam={}'.format(args.inp_list,args.inp_fnam))
if not args.criteria in CRITERIAS:
    raise ValueError('Error, unsupported criteria >>> {}'.format(args.criteria))
if args.mean_fitting and args.criteria in ['RMSE_test','R2_test','AIC_test']:
    raise ValueError('Error, {} is not calculated for mean value fitting. Choose another selection criteria.'.format(args.criteria))
if args.x_param is None:
    args.x_param = X_PARAM
for param in args.x_param:
    if not param in PARAMS:
        raise ValueError('Error, unknown explanatory variable for x_param >>> {}'.format(param))
if args.y_param is None:
    args.y_param = Y_PARAM
for param in args.y_param:
    if not param in OBJECTS:
        raise ValueError('Error, unknown objective variable for y_param >>> {}'.format(param))
if args.y_threshold is None:
    args.y_threshold = Y_THRESHOLD
y_threshold = {}
for s in args.y_threshold:
    m = re.search('\s*(\S+)\s*:\s*(\S+)\s*',s)
    if not m:
        raise ValueError('Error, invalid threshold >>> {}'.format(s))
    param = m.group(1)
    value = float(m.group(2))
    if not param in OBJECTS:
        raise ValueError('Error, unknown objective variable for y_threshold ({}) >>> {}'.format(param,s))
    if not np.isnan(value):
        y_threshold[param] = value
if args.y_max is None:
    args.y_max = Y_MAX
y_max = {}
for s in args.y_max:
    m = re.search('\s*(\S+)\s*:\s*(\S+)\s*',s)
    if not m:
        raise ValueError('Error, invalid max score >>> {}'.format(s))
    param = m.group(1)
    value = float(m.group(2))
    if not param in OBJECTS:
        raise ValueError('Error, unknown objective variable for y_max ({}) >>> {}'.format(param,s))
    y_max[param] = value
if args.y_int is None:
    args.y_int = Y_INT
y_int = {}
for s in args.y_int:
    m = re.search('\s*(\S+)\s*:\s*(\S+)\s*',s)
    if not m:
        raise ValueError('Error, invalid score step >>> {}'.format(s))
    param = m.group(1)
    value = float(m.group(2))
    if not param in OBJECTS:
        raise ValueError('Error, unknown objective variable for y_int ({}) >>> {}'.format(param,s))
    y_int[param] = value
if args.y_factor is None:
    args.y_factor = Y_FACTOR
y_factor = {}
for y_param in args.y_param:
    y_factor[y_param] = {}
for s in args.y_factor:
    m = re.search('\s*(\S+)\s*:\s*(\S+)\s*:\s*(\S+)\s*',s)
    if not m:
        raise ValueError('Error, invalid factor >>> {}'.format(s))
    y_param = m.group(1)
    param = m.group(2)
    value = float(m.group(3))
    if not y_param in OBJECTS:
        raise ValueError('Error, unknown objective variable for y_factor ({}) >>> {}'.format(y_param,s))
    if not param in OBJECTS:
        raise ValueError('Error, unknown objective variable for y_factor ({}) >>> {}'.format(param,s))
    if y_param in args.y_param:
        if not np.isnan(value) and (param != y_param):
            y_factor[y_param][param] = value

def llf(y_true,y_pred):
    n = len(y_pred)
    m = len(y_true)
    if m != n:
        raise ValueError('Error, len(y_pred)={}, len(y_true)={}'.format(n,m))
    error = y_true-y_pred
    v = np.var(error)
    return -n/2.0*np.log(2.0*np.pi*v)-np.dot(error.T,error)/(2.0*v)

def aic(y_true,y_pred,npar):
    return -2.0*llf(y_true,y_pred)+2.0*npar

def bic(y_true,y_pred,npar):
    n = len(y_pred)
    m = len(y_true)
    if m != n:
        raise ValueError('Error, len(y_pred)={}, len(y_true)={}'.format(n,m))
    return -2.0*llf(y_true,y_pred)+np.log(n)*npar

# Read data
if args.inp_list is not None:
    fnams = []
    with open(args.inp_list,'r') as fp:
        for line in fp:
            fnam = line.strip()
            if (len(fnam) < 1) or (fnam[0] == '#'):
                continue
            fnams.append(fnam)
else:
    fnams = args.inp_fnam
X = {}
Y = {}
P = {}
p_param = []
if args.amin is not None or args.amax is not None:
    p_param.append('Age')
for param in OBJECTS:
    if param in y_threshold:
        p_param.append(param)
for y_param in args.y_param:
    for param in y_factor[y_param]:
        if not param in p_param:
            p_param.append(param)
for param in args.x_param:
    X[param] = []
for param in args.y_param:
    Y[param] = []
for param in p_param:
    P[param] = []
for fnam in fnams:
    df = pd.read_csv(fnam,comment='#')
    df.columns = df.columns.str.strip()
    for param in args.x_param:
        if not param in df.columns:
            raise ValueError('Error in finding column for {} >>> {}'.format(param,fnam))
        X[param].extend(list(df[param]))
    for param in args.y_param:
        if not param in df.columns:
            raise ValueError('Error in finding column for {} >>> {}'.format(param,fnam))
        Y[param].extend(list(df[param]))
    for param in p_param:
        if not param in df.columns:
            raise ValueError('Error in finding column for {} >>> {}'.format(param,fnam))
        P[param].extend(list(df[param]))
X = pd.DataFrame(X)
Y = pd.DataFrame(Y)
P = pd.DataFrame(P)
for param in X.columns:
    X[param] = X[param].astype(float)
for param in Y.columns:
    Y[param] = Y[param].astype(float)
for param in P.columns:
    P[param] = P[param].astype(float)

# Add equivalent values to objective variables
for y_param in args.y_param:
    for param in y_factor[y_param]:
        Y[y_param] += P[param]*y_factor[y_param][param]

# Select data
param = 'Age'
if param in p_param:
    cnd2 = np.isnan(P[param].values)
    if np.all(cnd2):
        sys.stderr.write('Warning, no data available for {}.\n'.format(param))
    else:
        cnd = np.full((len(X),),False)
        if args.amin is not None:
            cnd |= (P[param] < args.amin).values
        if args.amax is not None:
            cnd |= (P[param] > args.amax).values
        if cnd.sum() > 0:
            X = X.iloc[~cnd]
            Y = Y.iloc[~cnd]
            P = P.iloc[~cnd]
X_inp = X.copy()
Y_inp = Y.copy()
P_inp = P.copy()

# Make formulas
if args.debug:
    if not args.batch:
        plt.interactive(True)
    fig = plt.figure(1,facecolor='w',figsize=(5,5))
    plt.subplots_adjust(top=0.9,bottom=0.12,left=0.18,right=0.95)
    pdf = PdfPages(args.fignam)
with open(args.out_fnam,'w') as fp:
    fp.write('{:>13s},'.format('Y'))
    for v in CRITERIAS:
        fp.write('{:>13s},'.format(v))
    fp.write('{:>13s},{:>2s}'.format('P','N'))
    for n in range(args.nx_max+1):
        fp.write(',{:>13s},{:>13s},{:>13s},{:>13s},{:>13s}'.format('P{}_param'.format(n),'P{}_value'.format(n),'P{}_error'.format(n),'P{}_p'.format(n),'P{}_t'.format(n)))
    fp.write('\n')
for y_param in args.y_param:
    cnd = np.isnan(Y_inp[y_param].values)
    if np.all(cnd):
        raise ValueError('Error, no data available for {}. Remove {} from objective variable.'.format(y_param,y_param))
    for param in args.x_param:
        cnd2 = np.isnan(X_inp[param].values)
        if np.all(cnd2):
            raise ValueError('Error, no data available for {}. Remove {} from explanatory variable.'.format(param,param))
        cnd |= cnd2
    for param in y_threshold:
        if param in [y_param]:
            continue
        else:
            cnd2 = (P_inp[param] > y_threshold[param]).values
            if np.all(cnd2):
                raise ValueError('Error, no {} left in threshold determination. Change the threshold of {}.'.format(param,param))
            cnd |= cnd2
    if cnd.sum() > 0:
        X_all = X_inp.iloc[~cnd].copy()
        Y_all = Y_inp.iloc[~cnd].copy()
        P_all = P_inp.iloc[~cnd].copy()
    else:
        X_all = X_inp.copy()
        Y_all = Y_inp.copy()
        P_all = P_inp.copy()
    Y = Y_all[y_param]
    if args.mean_fitting:
        X_score = {}
        Y_score = {}
        for param in args.x_param:
            X_score[param] = []
        Y_score[y_param] = []
        cnd1 = np.full((len(Y),),True)
        smax = 1.0
        if y_param in y_max:
            sint = y_int[y_param]/y_max[y_param]
        else:
            sint = y_int[y_param]
        for score in np.arange(smax,0,-sint):
            s_next = score-sint
            s = 0.5*(score+s_next)
            if np.abs(s) < EPSILON:
                s = 0.0
            cnd2 = (Y > s)
            cnd = (cnd1 & cnd2)
            if cnd.sum() > 0:
                X_cnd = X_all[cnd].mean()
                Y_cnd = Y[cnd].mean()
                for param in args.x_param:
                    X_score[param].append(X_cnd[param])
                Y_score[y_param].append(Y_cnd)
            cnd1[cnd2] = False
        cnd = cnd1
        if cnd.sum() > 0:
            X_cnd = X_all[cnd].mean()
            Y_cnd = Y[cnd].mean()
            for param in args.x_param:
                X_score[param].append(X_cnd[param])
            Y_score[y_param].append(Y_cnd)
        X_score = pd.DataFrame(X_score)
        Y_score = pd.DataFrame(Y_score)
    if args.debug:
        for param in args.x_param:
            if y_param in y_max:
                fact = y_max[y_param]
                y_label = 'Observed {} Score'.format(y_param)
            else:
                fact = 100.0
                y_label = 'Observed {} Intensity (%)'.format(y_param)
            fig.clear()
            ax1 = plt.subplot(111)
            ax1.minorticks_on()
            ax1.plot(X_all[param],Y*fact,'bo')
            ax1.plot(X_inp[param],Y_inp[y_param]*fact,'k.')
            if args.mean_fitting:
                ax1.plot(X_score[param],Y_score[y_param]*fact,'mo',ms=10)
            xmin = X_inp[param].min()
            ymin = Y_inp[y_param].min()*fact
            xmax = X_inp[param].max()
            ymax = Y_inp[y_param].max()*fact
            xdif = xmax-xmin
            ydif = ymax-ymin
            xfit = np.linspace(xmin,xmax,100)
            if args.mean_fitting:
                yfit = np.polyval(np.polyfit(X_score[param],Y_score[y_param]*fact,1),xfit)
            else:
                yfit = np.polyval(np.polyfit(X_all[param],Y*fact,1),xfit)
            ax1.plot(xfit,yfit,'r-')
            ax1.set_xlim(xmin-0.1*xdif,xmax+0.1*xdif)
            ax1.set_ylim(ymin-0.1*ydif,ymax+0.1*ydif)
            ax1.set_xlabel(param)
            ax1.set_ylabel(y_label)
            ax1.xaxis.set_tick_params(pad=7)
            ax1.yaxis.set_label_coords(-0.14,0.5)
            plt.savefig(pdf,format='pdf')
            if not args.batch:
                plt.draw()
                plt.pause(0.1)
    model_xs = []
    model_rmse_train = []
    model_r2_train = []
    model_aic_train = []
    model_bic_train = []
    model_fs = []
    coef_ps = []
    coef_ts = []
    coef_values = []
    coef_errors = []
    model_rmse_test = []
    model_r2_test = []
    model_aic_test = []
    for n in range(args.nx_min,args.nx_max+1):
        for c in combinations(args.x_param,n):
            x_list = list(c)
            if len(x_list) > args.ncheck_min:
                flag = False
                for indx in range(len(x_list)):
                    vif = variance_inflation_factor(X_all[x_list].values,indx)
                    if vif > args.vmax:
                        flag = True
                        break
                if flag:
                    continue # Eliminate multicollinearity
                r_list = []
                for x in x_list:
                    r_list.append(np.corrcoef(X_all[x],Y)[0,1])
                x_list = [c[indx] for indx in np.argsort(r_list)[::-1]]
            if args.mean_fitting:
                X = sm.add_constant(X_score[x_list]) # adding a constant
                x_all = list(X.columns)
                if len(X) <= len(x_all):
                    raise ValueError('Error, not enough data available >>> {}'.format(len(X_all)))
                model = sm.OLS(Y_score[y_param],X).fit()
            else:
                X = sm.add_constant(X_all[x_list]) # adding a constant
                x_all = list(X.columns)
                if len(X) <= len(x_all):
                    raise ValueError('Error, not enough data available >>> {}'.format(len(X_all)))
                model = sm.OLS(Y,X).fit()
            model_xs.append(x_all)
            model_rmse_train.append(np.sqrt(model.mse_resid)) # adjusted for df_resid
            model_r2_train.append(model.rsquared_adj)
            model_aic_train.append(model.aic)
            model_bic_train.append(model.bic)
            model_fs.append(model.f_pvalue)
            coef_ps.append(model.pvalues)
            coef_ts.append(model.tvalues)
            coef_values.append(model.params)
            if args.mean_fitting:
                cov = model.cov_params()
                errors = {}
                for param in x_all:
                    errors[param] = np.sqrt(cov.loc[param,param])
                coef_errors.append(errors)
                model_rmse_test.append(np.nan)
                model_r2_test.append(np.nan)
                model_aic_test.append(np.nan)
            else:
                rmses = []
                r2s = []
                aics = []
                values = {}
                errors = {}
                for param in x_all:
                    values[param] = []
                kf = KFold(n_splits=args.n_cross,random_state=None,shuffle=False)
                for train_index,test_index in kf.split(X):
                    X_train,X_test = X.iloc[train_index],X.iloc[test_index]
                    Y_train,Y_test = Y.iloc[train_index],Y.iloc[test_index]
                    model = sm.OLS(Y_train,X_train).fit()
                    Y_pred = model.predict(X_test)
                    rmses.append(mean_squared_error(Y_test,Y_pred,squared=False))
                    r2s.append(r2_score(Y_test,Y_pred))
                    aics.append(aic(Y_test,Y_pred,0))
                    for param in x_all:
                        values[param].append(model.params[param])
                for param in x_all:
                    errors[param] = np.std(values[param])
                coef_errors.append(errors)
                model_rmse_test.append(np.mean(rmses))
                model_r2_test.append(np.mean(r2s))
                model_aic_test.append(np.mean(aics))

    # Sort formulas
    if args.criteria == 'RMSE_test':
        model_indx = np.argsort(model_rmse_test)
    elif args.criteria == 'R2_test':
        model_indx = np.argsort(model_r2_test)[::-1]
    elif args.criteria == 'AIC_test':
        model_indx = np.argsort(model_aic_test)
    elif args.criteria == 'RMSE_train':
        model_indx = np.argsort(model_rmse_train)
    elif args.criteria == 'R2_train':
        model_indx = np.argsort(model_r2_train)[::-1]
    elif args.criteria == 'AIC_train':
        model_indx = np.argsort(model_aic_train)
    elif args.criteria == 'BIC_train':
        model_indx = np.argsort(model_bic_train)
    else:
        raise ValueError('Error, unsupported criteria >>> {}'.format(args.criteria))

    # Output results
    with open(args.out_fnam,'a') as fp:
        y_number = 1
        for indx in model_indx[:args.nmodel_max]:
            fp.write('{:>13s},'.format(y_param))
            fp.write('{:13.6e},{:13.6e},{:13.6e},{:13.6e},{:13.6e},{:13.6e},{:13.6e},{:13.6e},{:2d}'.format(model_rmse_test[indx],model_r2_test[indx],model_aic_test[indx],
                                                                                                            model_rmse_train[indx],model_r2_train[indx],
                                                                                                            model_aic_train[indx],model_bic_train[indx],
                                                                                                            model_fs[indx],len(model_xs[indx])-1))
            for param in model_xs[indx]:
                fp.write(',{:>13s},{:13.6e},{:13.6e},{:13.6e},{:13.6e}'.format(param,coef_values[indx][param],coef_errors[indx][param],coef_ps[indx][param],coef_ts[indx][param]))
            for n in range(len(model_xs[indx]),args.nx_max+1):
                fp.write(',{:>13s},{:13.6e},{:13.6e},{:13.6e},{:13.6e}'.format('None',np.nan,np.nan,np.nan,np.nan))
            fp.write('\n')
            if args.debug:
                x_list = []
                Y_pred = 0.0
                for param in model_xs[indx]:
                    param_low = param.lower()
                    if param_low == 'none':
                        continue
                    elif param_low == 'const':
                        Y_pred += coef_values[indx][param]
                    else:
                        x_list.append(param)
                        Y_pred += coef_values[indx][param]*X_all[param].values
                title = 'Model #{} ({})'.format(y_number,','.join(x_list))
                fig.clear()
                ax1 = plt.subplot(111)
                ax1.minorticks_on()
                if y_param in y_max:
                    xtmp = Y*y_max[y_param]
                    ytmp = Y_pred*y_max[y_param]
                    ax1.plot(xtmp,ytmp,'bo')
                    xmin = min(Y.min(),Y_pred.min())*y_max[y_param]
                    xmax = max(Y.max(),Y_pred.max())*y_max[y_param]
                    xdif = xmax-xmin
                    xfit = np.linspace(xmin,xmax,100)
                    yfit = np.polyval(np.polyfit(xtmp,ytmp,1),xfit)
                    ax1.plot(xfit,yfit,'r-')
                    ax1.plot(xfit,xfit,'k:')
                    x_label = 'Observed {} Score'.format(y_param)
                    y_label = 'Pred {} Score'.format(y_param)
                else:
                    xtmp = Y*100.0
                    ytmp = Y_pred*100.0
                    ax1.plot(xtmp,ytmp,'bo')
                    xmin = min(Y.min(),Y_pred.min())*100.0
                    xmax = max(Y.max(),Y_pred.max())*100.0
                    xdif = xmax-xmin
                    xfit = np.linspace(xmin,xmax,100)
                    yfit = np.polyval(np.polyfit(xtmp,ytmp,1),xfit)
                    ax1.plot(xfit,yfit,'r-')
                    ax1.plot(xfit,xfit,'k:')
                    x_label = 'Observed {} Intensity (%)'.format(y_param)
                    y_label = 'Pred {} Intensity (%)'.format(y_param)
                ax1.set_xlim(xmin-0.1*xdif,xmax+0.1*xdif)
                ax1.set_ylim(xmin-0.1*xdif,xmax+0.1*xdif)
                ax1.set_title(title)
                ax1.set_xlabel(x_label)
                ax1.set_ylabel(y_label)
                ax1.xaxis.set_tick_params(pad=7)
                ax1.yaxis.set_label_coords(-0.14,0.5)
                plt.savefig(pdf,format='pdf')
                if not args.batch:
                    plt.draw()
                    plt.pause(0.1)
            y_number += 1
if args.debug:
    pdf.close()
