#!/bin/env python3

from tableauhyperapi import HyperProcess, Telemetry, Connection, CreateMode, NOT_NULLABLE, NULLABLE, SqlType, \
        TableDefinition, Inserter, escape_name, escape_string_literal, HyperException, TableName

from os import path
import json
import os
import time


HYPER_LOG_FILE = 'hyperd.log'


MATCH_SELECT = lambda o: 'v' in o and 'SELECT' in o['v']['query-trunc']

custom_settings = {
    'log_timing' : '1',
    'log_adaptive_optimization': '1'
}

table_defs = {
    'Lineitem': TableDefinition(
        table_name='Lineitem',
        columns=[
            TableDefinition.Column('l_orderkey',        SqlType.int(), NOT_NULLABLE),
            TableDefinition.Column('l_partkey',         SqlType.int(), NOT_NULLABLE),
            TableDefinition.Column('l_suppkey',         SqlType.int(), NOT_NULLABLE),
            TableDefinition.Column('l_linenumber',      SqlType.int(), NOT_NULLABLE),
            TableDefinition.Column('l_quantity',        SqlType.numeric(10,2), NOT_NULLABLE),
            TableDefinition.Column('l_extendedprice',   SqlType.numeric(10,2), NOT_NULLABLE),
            TableDefinition.Column('l_discount',        SqlType.numeric(10,2), NOT_NULLABLE),
            TableDefinition.Column('l_tax',             SqlType.numeric(10,2), NOT_NULLABLE),
            TableDefinition.Column('l_returnflag',      SqlType.char(1), NOT_NULLABLE),
            TableDefinition.Column('l_linestatus',      SqlType.char(1), NOT_NULLABLE),
            TableDefinition.Column('l_shipdate',        SqlType.date(), NOT_NULLABLE),
            TableDefinition.Column('l_commitdate',      SqlType.date(), NOT_NULLABLE),
            TableDefinition.Column('l_receiptdate',     SqlType.date(), NOT_NULLABLE),
            TableDefinition.Column('l_shipinstruct',    SqlType.char(25), NOT_NULLABLE),
            TableDefinition.Column('l_shipmode',        SqlType.char(10), NOT_NULLABLE),
            TableDefinition.Column('l_comment',         SqlType.char(44), NOT_NULLABLE),
        ]
    ),
    'Orders': TableDefinition(
        table_name='Orders',
        columns = [
            TableDefinition.Column('o_orderkey',        SqlType.int(), NOT_NULLABLE),
            TableDefinition.Column('o_custkey',         SqlType.int(), NOT_NULLABLE),
            TableDefinition.Column('o_orderstatus',     SqlType.char(1), NOT_NULLABLE),
            TableDefinition.Column('o_totalprice',      SqlType.numeric(10,2), NOT_NULLABLE),
            TableDefinition.Column('o_orderdate',       SqlType.date(), NOT_NULLABLE),
            TableDefinition.Column('o_orderpriority',   SqlType.char(15), NOT_NULLABLE),
            TableDefinition.Column('o_clerk',           SqlType.char(15), NOT_NULLABLE),
            TableDefinition.Column('o_shippriority',    SqlType.int(), NOT_NULLABLE),
            TableDefinition.Column('o_comment',         SqlType.char(80), NOT_NULLABLE),
        ]
    ),
    'Customer': TableDefinition(
        table_name='Customer',
        columns = [
            TableDefinition.Column('c_custkey',         SqlType.int(), NOT_NULLABLE),
            TableDefinition.Column('c_name',            SqlType.char(25), NOT_NULLABLE),
            TableDefinition.Column('c_address',         SqlType.char(40), NOT_NULLABLE),
            TableDefinition.Column('c_nationkey',       SqlType.int(), NOT_NULLABLE),
            TableDefinition.Column('c_phone',           SqlType.char(15), NOT_NULLABLE),
            TableDefinition.Column('c_acctbal',         SqlType.numeric(10,2), NOT_NULLABLE),
            TableDefinition.Column('c_mktsegment',      SqlType.char(10), NOT_NULLABLE),
            TableDefinition.Column('c_comment',         SqlType.char(117), NOT_NULLABLE),
        ]
    ),
    'Part': TableDefinition(
        table_name='Part',
        columns=[
            TableDefinition.Column('p_partkey',         SqlType.int(), NOT_NULLABLE),
            TableDefinition.Column('p_name',            SqlType.char(55), NOT_NULLABLE),
            TableDefinition.Column('p_mfgr',            SqlType.char(25), NOT_NULLABLE),
            TableDefinition.Column('p_brand',           SqlType.char(10), NOT_NULLABLE),
            TableDefinition.Column('p_type',            SqlType.char(25), NOT_NULLABLE),
            TableDefinition.Column('p_size',            SqlType.int(), NOT_NULLABLE),
            TableDefinition.Column('p_container',       SqlType.char(10), NOT_NULLABLE),
            TableDefinition.Column('p_retailprice',     SqlType.numeric(10,2), NOT_NULLABLE),
            TableDefinition.Column('p_comment',         SqlType.char(23), NOT_NULLABLE),
        ]
    ),
}

def init():
    if os.path.isfile(HYPER_LOG_FILE):
        os.remove(HYPER_LOG_FILE)

def load_table(connection :Connection, table_name :str, filename :str):
    table_def = table_defs[table_name]
    connection.catalog.create_table(table_def)
    connection.execute_command(f'COPY {table_def.table_name} FROM \'{filename}\' WITH DELIMITER \'|\' CSV')

def dispose_table(connection :Connection, table_name :str):
    table_def = table_defs[table_name]
    connection.execute_command(f'DELETE FROM {table_def.table_name}')
    connection.execute_command(f'DROP TABLE {table_def.table_name}')

def benchmark_query(connection :Connection, query :str, tables :list):
    for table_name, filename in tables:
        load_table(connection, table_name, filename)
    begin = time.time_ns()
    with connection.execute_query(query) as result:
        pass
    end = time.time_ns()
    for table_name, _ in tables:
        dispose_table(connection, table_name)
    return end - begin

def extract_results():
    j = list()
    with open(HYPER_LOG_FILE, 'r') as log:
        for line in log:
            j.append(json.loads(line))
    return j

def match_result(result :object, attribute_values :dict, matcher :list=list()):
    for attr, val in attribute_values.items():
        if attr not in result or result[attr] != val:
            return False
    for m in matcher:
        if not m(result):
            return False
    return True

def filter_results(results :list, attribute_values :dict, matcher :list=list()):
    matches = list()
    for r in results:
        if match_result(r, attribute_values, matcher):
            matches.append(r)
    return matches

if __name__ == '__main__':
    with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU, parameters=custom_settings) as hyper:
        with Connection(endpoint=hyper.endpoint, database='benchmark.hyper', create_mode=CreateMode.CREATE_AND_REPLACE) as connection:
            with connection.execute_query('SHOW ALL') as result:
                for row in result:
                    print(f'{row[0]:60} {row[1]:20} {row[2]}')
