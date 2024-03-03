from mlforecast import MLForecast
import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from window_ops.rolling import rolling_mean, rolling_max, rolling_min
import optuna
import matplotlib.pyplot as plt
import holidays
import logging
from sklearn.metrics import mean_absolute_error
import os

current_directory = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(current_directory, 'data')

class Predictive:
    def __init__(self):

        logger_filename = os.path.join(current_directory, 'logs', 'predictive.log')
        logging.basicConfig(filename=logger_filename, level=logging.DEBUG,
                            format="%(asctime)s | %(levelname)s | %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")

        self.N_TRIALS = 30
        self.HORIZON = 30
        self.MODEL = "LGBMRegressor"
        self.static_features = ['is_holiday']
        self.data_file = os.path.join(data_path, 'dados-gerais.csv')
        self.dataset = self.get_data(self.data_file)
        self.max_date = self.dataset['ds'].max()
        self.train, self.valid = self.get_train_test()
        self.valid_horizon = self.valid['ds'].nunique()
        self.best_params = self.optimize()



    def get_train_test(self):
        two_months_ago = self.max_date - pd.DateOffset(months=2)
        train = self.dataset[self.dataset['ds'] <= two_months_ago]
        test = self.dataset[self.dataset['ds'] > two_months_ago]
        return train, test

    def wmape(self, y_true, y_pred):
        return np.abs(y_true - y_pred).sum() / np.abs(y_true).sum()
    
    def create_instances(self, model, lag):
        return MLForecast(
            models=model,
            freq='D',
            lags=[1,7,lag],
            date_features=['dayofweek', 'month'],
            lag_transforms={
                1: [(rolling_mean, 7), (rolling_max, 7), (rolling_min, 7)],
            },
            num_threads=6
        )
    
    def models_(self, params):
        return [
            # XGBRegressor(
            #     n_estimators=500,
            #     learning_rate=params['learning_rate'],
            #     max_depth=params['max_depth'],
            #     min_child_weight=params['min_child_weight'],
            #     subsample=params['subsample'],
            #     colsample_bytree=params['colsample_bytree'],
            #     random_state=42
            # ),
            LGBMRegressor(
                n_estimators=500,
                learning_rate=params['learning_rate'],
                num_leaves=params['num_leaves'],
                min_data_in_leaf=params['min_data_in_leaf'],
                bagging_fraction=params['bagging_fraction'],
                colsample_bytree=params['colsample_bytree'],
                bagging_freq=1,
                random_state=42,
                verbose=-1)
        ]

    def get_data(self, path):
        br_holidays = holidays.country_holidays('BR')
        data = pd.read_csv(path)
        data = data.rename(columns= {'date': 'ds', 'case_cnt': 'y', 'ra': 'unique_id'})
        data['ds'] = pd.to_datetime(data['ds'])
        data = data.sort_values(by=['unique_id', 'ds']).groupby('unique_id').apply(lambda x: x.fillna(method='ffill'))
        data['is_holiday'] = data['ds'].dt.date.apply(lambda x: 1 if x in br_holidays else 0)

        return data

    def objective(self, trial):
        learning_rate = trial.suggest_loguniform('learning_rate', 1e-3, 1e-1)
        lags = trial.suggest_int('lags', 14, 56, step=7)# step means we only try multiples of 7 starting from 14
        colsample_bytree = trial.suggest_uniform('colsample_bytree', 0.1, 1.0)

        # LightGBM
        num_leaves = trial.suggest_int('num_leaves', 2, 256)
        min_data_in_leaf = trial.suggest_int('min_data_in_leaf', 1, 100)
        bagging_fraction = trial.suggest_uniform('bagging_fraction', 0.1,1.0)

        # XGBoost
        min_child_weight = trial.suggest_int('min_child_weight', 1, 10)
        subsample = trial.suggest_uniform('subsample', 0.1, 1.0)
        max_depth = trial.suggest_int('max_depth', 3, 10)

        models = self.models_({
            'learning_rate': learning_rate,
            'num_leaves': num_leaves,
            'min_data_in_leaf': min_data_in_leaf,
            'bagging_fraction': bagging_fraction,
            'colsample_bytree': colsample_bytree,
            'min_child_weight': min_child_weight,
            'subsample': subsample,
            'max_depth': max_depth
        })
    
        forecast = self.train_forecast(models, lags)

        error = mean_absolute_error(forecast['y'], forecast[self.MODEL])

        return error

    def optimize(self):
        study = optuna.create_study(direction='minimize')
        study.optimize(self.objective, n_trials=self.N_TRIALS)
        return study.best_params

    def train_forecast(self, models, lags):
        instances = self.create_instances(models, lags)
        instances.fit(self.train, id_col='unique_id', target_col='y', time_col='ds', static_features=self.static_features)
        forecast = instances.predict(h=self.valid_horizon)
        forecast = forecast.merge(self.valid[['unique_id', 'ds', 'y']], on=['unique_id', 'ds'], how='left')
        forecast['y'] = forecast['y'].fillna(0)
        return forecast
    
    def metrics(self, forecast):
        mape = self.wmape(forecast['y'], forecast[self.MODEL])
        mae = mean_absolute_error(forecast['y'], forecast[self.MODEL])
        return mape, mae

    def save_csv(self, forecast, model_name):
        file_to_save = os.path.join(data_path, 'pred_results', f'forecast_{model_name}.csv')
        forecast.to_csv(file_to_save, index=False)        
    
    def train_for_metrics(self):
        forecast = self.train_forecast(self.models_(self.best_params), self.best_params['lags'])
        mape, mae = self.metrics(forecast)

        logging.info(f"Model: {self.MODEL} | MAPE: {mape} | MAE: {mae}")
        self.save_csv(forecast, self.MODEL)
    
    def predict(self):
        model = self.models_(self.best_params)
        instances = self.create_instances(model, self.best_params['lags'])
        instances.fit(self.dataset, id_col='unique_id', target_col='y', time_col='ds', static_features=self.static_features)
        forecast = instances.predict(h=self.HORIZON)
        self.save_csv(forecast, f'full_{self.MODEL}')
        
        
    def contamination(self, horizon):
        response = {'horizon': horizon}
        return response