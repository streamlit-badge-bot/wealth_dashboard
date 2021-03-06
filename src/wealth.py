import json

import pandas as pd

from utils import today


class WealthManager:
    def __init__(self):
        self.fund_dict = {}

    def new_fund(self, fund_name, remarks, platform, initial_investment=0.0, maturity=None):
        if fund_name in self.fund_dict.keys():
            raise KeyError('This fund name have already been used')

        new_fund = Funds(fund_name, remarks, platform, initial_investment, maturity)
        self.fund_dict[fund_name] = new_fund


    def fund_update_cur_val(self, fund_name, cur_value):
        self.fund_dict[fund_name].update_cur_val(cur_value)

    def fund_transact(self, fund_name, amount, transact_date, prev_value=None, transact_remark=None, sold=False):
        self.fund_dict[fund_name].transact(amount, transact_date, prev_value, transact_remark, sold)

    def fund_edit_info(self, fund_name, remarks, platform, maturity=None):
        self.fund_dict[fund_name].edit_info(remarks, platform, maturity)

    def export_data(self):
        output_dict = {fund_name: fund_obj.save_data()
                       for fund_name, fund_obj in self.fund_dict.items()}

        output_json = json.dumps(output_dict)

        return output_json

    def import_data(self, data_dict):

        for fund_name, fund_data_dict in data_dict.items():
            fund = Funds(fund_name, import_data=True)
            fund.load_data(fund_data_dict)
            self.fund_dict[fund_name] = fund

    def get_funds_name_list(self, exclude_sold=False):
        funds_name_list = list(self.fund_dict.keys())
        if exclude_sold:
            funds_name_list = [fund_name for fund_name in funds_name_list if not self.fund_dict[fund_name].sold]
        return funds_name_list

    def get_fund_cur_val(self, fund_name):
        return self.fund_dict[fund_name].cur_val

    def get_fund_total_investment(self, fund_name):
        return self.fund_dict[fund_name].total_investment

    def get_fund_platform(self, fund_name):
        return self.fund_dict[fund_name].platform

    def get_fund_profit(self, fund_name):
        investment = self.get_fund_total_investment(fund_name)
        cur_val = self.get_fund_cur_val(fund_name)
        return cur_val - investment

    def get_fund_maturity(self, fund_name):
        return self.fund_dict[fund_name].maturity

    def get_fund_remarks(self, fund_name):
        return self.fund_dict[fund_name].remarks

    def get_fund_history_df(self, fund_name):
        history = self.fund_dict[fund_name].history

        date_list = []
        val_list = []
        for date, val in history.items():
            date_list.append(date)
            val_list.append(val)

        output_df = {'Date': date_list,
                     'Valuation': val_list}

        output_df = pd.DataFrame(output_df)
        output_df['Date']= pd.to_datetime(output_df['Date'])
        output_df = output_df.set_index('Date')

        return output_df

    def get_fund_transaction_df(self, fund_name):
        transaction = self.fund_dict[fund_name].transaction
        transaction_remark = self.fund_dict[fund_name].transaction_remark

        date_list = []
        amt_list = []
        remark_list = []
        for date, amt in transaction.items():
            date_list.append(date)
            amt_list.append(amt)
            try:
                remark_list.append(transaction_remark[date])
            except KeyError:
                remark_list.append('')

        output_df = {'Date': date_list,
                     'Amount': amt_list,
                     'Remarks': remark_list}

        output_df = pd.DataFrame(output_df)
        output_df['Date']= pd.to_datetime(output_df['Date'])
        output_df = output_df.set_index('Date')

        return output_df


class Funds:
    def __init__(self, name, remarks=None, platform=None, initial_investment=None, maturity=None, import_data=False):
        self.name = name
        self.remarks = remarks
        self.platform = platform
        self.total_investment = initial_investment
        self.cur_val = initial_investment
        self.sold = False

        if maturity is not None:
            maturity = str(maturity)
        self.maturity = maturity

        if import_data:
            self.transaction = {}
            self.transaction_remark = {}
            self.history = {}
        else:
            self.transaction = {today(): initial_investment}
            self.transaction_remark = {today(): 'Funds Created'}
            self.history = {today(): initial_investment}

    def update_cur_val(self, cur_value):
        self.history[today()] = cur_value
        self.cur_val = cur_value

    def transact(self, amount, transact_date, prev_value=None, transact_remark=None, sold=False):
        if prev_value is None:
            prev_value = self.cur_val

        if transact_date is not None:
            transact_date = str(transact_date)

        if sold:
            self.sold = True
            self.transaction[transact_date] = -prev_value
            self.history[transact_date] = 0
            if transact_remark is None:
                transact_remark = '[Sold]'
            else:
                transact_remark = f'[Sold] {transact_remark}'
        else:
            cur_value = prev_value + amount
            self.transaction[transact_date] = amount
            self.history[transact_date] = cur_value
            self.total_investment += amount
            self.cur_val = cur_value

        self.transaction_remark[transact_date] = transact_remark

    def edit_info(self, remarks, platform, maturity):
        self.remarks = remarks
        self.platform = platform
        if maturity is not None:
            maturity = str(maturity)
        self.maturity = maturity

    def save_data(self):
        output_dict = {'name': self.name,
                       'remarks': self.remarks,
                       'platform': self.platform,
                       'total_investment': self.total_investment,
                       'cur_val': self.cur_val,
                       'maturity': self.maturity,
                       'transaction': self.transaction,
                       'history': self.history,
                       'sold': self.sold}
        return output_dict

    def load_data(self, fund_data_dict):
        self.remarks = fund_data_dict['remarks']
        self.platform = fund_data_dict['platform']
        self.total_investment = fund_data_dict['total_investment']
        self.cur_val = fund_data_dict['cur_val']
        self.maturity = fund_data_dict['maturity']
        self.transaction = fund_data_dict['transaction']
        self.history = fund_data_dict['history']
        if 'sold' in fund_data_dict.keys():
            self.sold = fund_data_dict['sold']






