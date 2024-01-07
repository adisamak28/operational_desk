""" 
Name    : views.py
Version : 1.0
Version History :
#############################################################################################################
Version     Date                  Description                                              Modified By
1.0         18-September-2022     Initial Version Release                                  Aditya S
2.0         28-November-2022      Production version with more features                    Aditya S
3.0         13-January-2023       Release of account based search across all products      Aditya S
#############################################################################################################
"""


from django.http import HttpResponseRedirect, HttpResponse
from django.db import connections
import datetime
import pandas as pd
import psycopg2 as pspg
import pandas.io.sql as sqlio
import requests
import json
import numbers
import boto3
import time
import csv
import re
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
str_pkg_name = "old_data_service"
from operationaldesk_automation.secrets import *
import logging
logger = logging.getLogger(__name__)
from old_data_reqapi.controller import old_data_controller




class OldDataService:
    def _init_(self, peb_card_number, amount, bank_ref_number, pan_id, account_no, product_identifier, page_no):
        self.peb_card_number = peb_card_number
        self.amount = amount
        self.bank_ref_number = bank_ref_number
        self.pan_id = pan_id
        self.account_no = account_no
        self.product_identifier = product_identifier
        self.page_no = page_no
        
    
    # Create your views here.
    def operational_data(self, peb_card_number, amount, bank_ref_number, pan_id, account_no, product_identifier, page_no):
        card_no = peb_card_number
        amt = amount
        bank_ref_no = bank_ref_number
        pan_data = pan_id
        account_number = account_no
        product_name = product_identifier
        page_number = page_no
        try:
            with connections['redshift_info'].cursor() as cur:
                if (pan_data and re.search("^[a-zA-Z]{3}[pchabgjlftjPCHABGJLFT][a-zA-Z][0-9]{4}[a-zA-Z]$", pan_data)):
                    final_response = self.pan_id_based_search(pan_data)
                    return final_response
                elif (account_number and product_name and page_number):
                    final_response = self.account_num_based_search(account_number, product_name, page_number)
                    return final_response
                elif (card_no and not(bank_ref_no or amt) and card_no.isalnum()):  #card_no entered
                    query = f"select peb_transaction_id , peb_card_number,  amount , transaction_ref_num , bank_ref_num , peb_transaction_status , peb_transaction_date, peb_merchant_id, peb_submerchant_id from prod_gateway_db.peb_transaction_info where peb_card_number = '{card_no}'" 
                elif (card_no and amt and not(bank_ref_no) and card_no.isalnum() and isinstance(float(amt), (int, float))): # Card no and amount entered 
                    query = f"select peb_transaction_id , peb_card_number,  amount , transaction_ref_num , bank_ref_num , peb_transaction_status , peb_transaction_date, peb_merchant_id, peb_submerchant_id from prod_gateway_db.peb_transaction_info where peb_card_number = '{card_no}' and amount = '{amt}'"
                elif (bank_ref_no and not(card_no or amt) and bank_ref_no.isalnum()): #bank ref no is entered
                    query = f"select peb_transaction_id , peb_card_number,  amount , transaction_ref_num , bank_ref_num , peb_transaction_status , peb_transaction_date, peb_merchant_id, peb_submerchant_id from prod_gateway_db.peb_transaction_info where bank_ref_num = '{bank_ref_no}'"
                elif (bank_ref_no and amt and not(card_no) and bank_ref_no.isnumeric() and isinstance(float(amt), (int, float)) ): #bank ref no and amount entered
                    query = f"select peb_transaction_id , peb_card_number, amount , transaction_ref_num , bank_ref_num , peb_transaction_status , peb_transaction_date, peb_merchant_id, peb_submerchant_id from prod_gateway_db.peb_transaction_info where bank_ref_num = '{bank_ref_no}' and amount = '{amt}'"
                elif (card_no and bank_ref_no and amt and card_no.isalnum() and isinstance(float(amt), (int, float)) and bank_ref_no.isalnum()): # card no, bank_ref_no, amount entered
                    query = f"select peb_transaction_id , peb_card_number,  amount , transaction_ref_num , bank_ref_num , peb_transaction_status , peb_transaction_date, peb_merchant_id, peb_submerchant_id from prod_gateway_db.peb_transaction_info where peb_card_number = '{card_no}' and bank_ref_num = '{bank_ref_no}' and amount = '{amt}'"

                elif (card_no and bank_ref_no and not(amt) and card_no.isalnum() and bank_ref_no.isalnum() ): # Card no and bank_ref_no entered
                    query = f"select peb_transaction_id , peb_card_number,  amount , transaction_ref_num , bank_ref_num , peb_transaction_status , peb_transaction_date, peb_merchant_id, peb_submerchant_id from prod_gateway_db.peb_transaction_info where peb_card_number = '{card_no}' and bank_ref_num = '{bank_ref_no}'"
                else:
                    return {'success' : False, 'message': 'input parameters invalid'}
        
                cur.execute(query)
                columns = [column[0] for column in cur.description]
                final_response = []
                for row in cur.fetchall():
                    d=(dict(zip(columns, row)))
                    d['peb_transaction_date'] =  d['peb_transaction_date'].strftime('%Y-%m-%d')
                    final_response.append(d)
                logger.error("card transaction response", final_response)
                return final_response
        except Exception as error:
            return {'success' : False, 'error' : str(error)}   
         



    def pan_id_based_search(self, pan_data):
        try:
            client = boto3.client('redshift-data', aws_access_key_id = aws_access_key_id, aws_secret_access_key = aws_secret_access_key, region_name=region_name)
            response_query = client.execute_statement(
                ClusterIdentifier= 'prod-redshift-edap', Database= 'prodredshiftdb', DbUser= 'aml_user_redshift', Sql= f"select merchant_id, business_name, pan_id from prod_easebuzz_db.eb_profile_businessinfo_audit epb where epb.pan_id like '%{pan_data}%'" )
            time.sleep(1)
            get_result = client.get_statement_result(Id= response_query["Id"], NextToken = "")
            time.sleep(1)
            if not(get_result['Records']):
                response_query = client.execute_statement(
                        ClusterIdentifier='prod-redshift-edap', Database= 'prodredshiftdb', DbUser= 'aml_user_redshift', Sql = f"select id, name, pan_number from edueasebuzzpy_db.institute i where i.pan_number like '%{pan_data}%'")   
                time.sleep(1)
                get_result = client.get_statement_result( Id= response_query["Id"], NextToken = "")
            if not(get_result['Records']):
                return {'success' : False, 'message': 'Data not Found'}
            else:
                d = get_result['Records']
                logger.error("get resultset", d)
                final_result =[]
                for x in d:
                    result = {}
                    result['merchant_id'] = x[0]['longValue']
                    result['merchant_name'] = x[1]['stringValue']
                    result['Pan_id'] = x[2]['stringValue']
                    print("final result", result)
                    final_result.append(result)
                logger.error("show pan final result", final_result)
                return final_result  
        except Exception as error:
            logger.exception("raised exception")
            return {'success' : False, 'error' : str(error)}   


    def account_num_based_search(self, account_number, product_name, page_number):
        try:
            with connections['redshift_info'].cursor() as cur:
                merchant_details = []
                recordlength = ""
                if product_name =='WIRE':
                    record_count_query = f"select count(*) from public.vms_ledger vl where vl.remitter_account_number = '{account_number}' or vl.beneficiary_account_number = '{account_number}'"
                    cur.execute(record_count_query)
                    records = cur.fetchall()
                    query1 = f"select merchant_id as wire_merchant_id, uuid, unique_transaction_reference, remitter_account_number, beneficiary_account_number, remitter_full_name, beneficiary_full_name from public.vms_ledger vl where vl.remitter_account_number = '{account_number}' or vl.beneficiary_account_number = '{account_number}' order by id asc LIMIT 10 OFFSET '{page_number}'"
                    cur.execute(query1)
                    columns = [column[0] for column in cur.description]
                    recordlength = records[0][0]
                    for row in cur.fetchall():
                        d=(dict(zip(columns, row)))
                        d['product'] = "Wire"
                        merchant_details.append(d)
                if product_name =='PG':
                    record_count_query = f"select count(*) from prod_gateway_db.peb_submerchant_info pi2 where account_number = '{account_number}'"
                    cur.execute(record_count_query)
                    records = cur.fetchall()
                    query2 = f"select merchant_id, submerchant_id ,name as merchant_name, account_number from prod_gateway_db.peb_submerchant_info pi2 where account_number = '{account_number}' order by id asc limit 10 OFFSET '{page_number}'"
                    cur.execute(query2)
                    columns = [column[0] for column in cur.description]
                    recordlength = records[0][0]
                    for row in cur.fetchall():
                        d=(dict(zip(columns, row)))
                        d['product'] = "PG"
                        merchant_details.append(d)
                if product_name =='INSTACOLLECT':
                    record_count_query = f"select count(*) from prod_easebuzz_instacollect.smart_collect_smartcollectledger scs where remitter_account_number = '{account_number}' or beneficiary_account_number ='{account_number}'"
                    cur.execute(record_count_query)
                    records = cur.fetchall()
                    query3 = f"select merchant_id as wire_merchant_id , uuid , unique_transaction_reference , remitter_account_number , beneficiary_account_number, remitter_full_name , beneficiary_full_name  from prod_easebuzz_instacollect.smart_collect_smartcollectledger scs where remitter_account_number = '{account_number}' or beneficiary_account_number ='{account_number}' order by id asc LIMIT 10 OFFSET '{page_number}'"
                    cur.execute(query3)
                    columns = [column[0] for column in cur.description]
                    recordlength = records[0][0]
                    for row in cur.fetchall():
                        d=(dict(zip(columns, row)))
                        d['product'] = "INSTACOLLECT"
                        merchant_details.append(d)
                if merchant_details:
                    return {"merchant_details": merchant_details, "count": recordlength}
                else:
                    return {'success' : False, 'message' : 'Not found any details for given account number'}
            
        except Exception as error:
            return {'success' : False, 'error' : str(error)}






    ####################################################################################################################################################

    def call_operational_data(self, data):  #main function which calls the old data function
        try:
            peb_card_number = data.get("peb_card_number")
            amount = data.get("amount")
            bank_ref_number = data.get("bank_ref_number")
            pan_id = data.get("pan_id")
            account_no = data.get("account_no")
            product_identifier = data.get("product_identifier")
            page_no = data.get("page_no")
            card_data = self.operational_data(peb_card_number, amount, bank_ref_number, pan_id, account_no, product_identifier, page_no)
            card_data_api_response = {"success": True, "data": card_data}             
            return card_data_api_response
        except Exception as error:
            return {'success': False, 'error' : str(error)} 
  


