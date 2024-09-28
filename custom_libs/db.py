# -*- coding: utf-8 -*-


import os
import sys
import shutil
import sqlite3

# data
from data import global_vars

# path
APP_PATH = global_vars.APP_PATH


def check_create_dbs() -> None:

	# CREATE / CONNECT DB & CREATE CUSROR
	conn = sqlite3.connect(os.path.join(APP_PATH, "dbs/main_whm.db"))
	c = conn.cursor()


	# CREATE A TABLE
	with conn:
		c.execute("""CREATE TABLE if not exists wh_cart(
			dt text,
			item_art text,
			item_name text,
			item_price text,
			cart_item_qty text,
			item_total_value text,
			whm_uuid text,
			item_comment text)
		""")


	with conn:
		c.execute("""CREATE TABLE if not exists wh_cart_return(
			dt text,
			item_art text,
			item_name text,
			item_price text,
			cart_item_qty text,
			item_total_value text,
			whm_uuid text,
			item_comment text)
		""")


	with conn:
		c.execute("""CREATE TABLE if not exists stock_items(
			dt text,
			item_art text,
			item_name text,
			item_price text,
			item_stock_qty text,
			item_total_value text,
			whm_uuid text)
		""")


	with conn:
		c.execute("""CREATE TABLE if not exists warehouse_transactions(
			dt text,
			transaction_uuid text,
			item_art text,
			item_name text,
			item_qty text,
			type text,
			comment text,
			whm_id text,
			agent_uuid text)
		""")


	with conn:
		c.execute("""CREATE TABLE if not exists reports_history(
			dt text,
			whm_uuid text)
		""")


	# COMMIT CHANGES & CLOSE
	conn.commit()
	conn.close()

	return



def clear_cart(table_names):
	# create db or connect & create a cursor
	conn = sqlite3.connect(os.path.join(APP_PATH, "dbs/main_whm.db"))
	c = conn.cursor()

	for table_name in table_names:
		c.execute(f"DELETE FROM {table_name}")

	# commit changes & close connection
	conn.commit()
	conn.close()

	return