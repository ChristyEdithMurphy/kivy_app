# -*- coding: utf-8 -*-


# system libraries
import re
import os
# import sys
import shutil
# import uuid
import sqlite3

# kivy and kivymd
import asynckivy
from kivy.clock import Clock
# from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemSupportingText, MDListItemTertiaryText

# custom libraries
from custom_libs import utils, db

# externally stored classes
from class_libs.Money import Money

# data
from data import global_vars, items


class DashScreen(MDScreen):

	def on_enter(self):
		
		Clock.schedule_once(lambda x: asynckivy.start(self.show_sold_items_list("sold_products_list")))


	async def show_sold_items_list(self, ct_list):

		APP_PATH = global_vars.APP_PATH
		APP_USER = global_vars.USER_ID

		# clean list
		self.ids[ct_list].clear_widgets()
		# create db or connect & create a cursor
		conn = sqlite3.connect(os.path.join(APP_PATH, "dbs/main_whm.db"))
		# conn = sqlite3.connect(os.path.join(APP_PATH, "test_db_00.db"))
		c = conn.cursor()

		# get list of unique items
		c.execute("SELECT DISTINCT item_name FROM stock_items WHERE whm_uuid=:whm_uuid",
			{"whm_uuid": APP_USER}
		)
		unique_item_names = [row[0] for row in c.fetchall()]


		total_items_value = Money.mint(float(0))
		total_litrage = float(0)

		total_beer_value = Money.mint(float(0))
		total_beer_litrage = float(0)

		total_SAD_value = Money.mint(float(0))
		total_SAD_litrage = float(0)

		total_NAD_value = Money.mint(float(0))
		total_NAD_litrage = float(0)

		total_WATER_value = Money.mint(float(0))
		total_WATER_litrage = float(0)

		# and now we shall get sum for each items qty, amount
		for unique_item_name in unique_item_names:

			await asynckivy.sleep(0)

			# grab records from db
			c.execute("SELECT SUM(item_stock_qty), SUM(item_total_value) FROM stock_items WHERE item_name=:item_name AND whm_uuid=:whm_uuid",
				{
					"item_name": unique_item_name,
					"whm_uuid": APP_USER
				}
			)
			# Fetch the results
			results = c.fetchall()

			# Process the results
			total_item_qty = results[0][0]
			total_item_qty_formatted = f"{total_item_qty:,.2f}".replace(",", " ")
			total_item_amount = Money.mint(float(results[0][1]))
			item_price = Money.mint(float(items.ITEMS_DICT[unique_item_name][0]))
			item_litrage = float(items.ITEMS_DICT[unique_item_name][2])
			total_item_litrage = item_litrage * total_item_qty
			total_item_litrage_formatted = f"{total_item_litrage:,.2f}".replace(",", " ")

			total_items_value += total_item_amount
			total_litrage += total_item_litrage

			if unique_item_name in items.BEER_DICT.keys():
				total_beer_value += total_item_amount
				total_beer_litrage += total_item_litrage

			if unique_item_name in items.SAD_DICT.keys():
				total_SAD_value += total_item_amount
				total_SAD_litrage += total_item_litrage

			if unique_item_name in items.NAD_DICT.keys():
				total_NAD_value += total_item_amount
				total_NAD_litrage += total_item_litrage

			if unique_item_name in items.WATER_DICT.keys():
				total_WATER_value += total_item_amount
				total_WATER_litrage += total_item_litrage


			self.ids[ct_list].add_widget(
				MDListItem(
					MDListItemHeadlineText(
						text=unique_item_name
					),
					MDListItemSupportingText(
						text=f"{item_litrage} л.  x  {total_item_qty_formatted} шт.  =  {total_item_litrage_formatted} л.",
					),
					MDListItemTertiaryText(
						text=f"{item_price}  |  {total_item_amount}",
					),
				)
			)

		self.ids.lbl_total_items_value.text = f"ИТОГО : {str(total_items_value)}"
		total_litrage_raw = f"{total_litrage:,.2f}".replace(",", " ")
		self.ids.lbl_total_litrage.text = f"{total_litrage_raw} л."

		self.ids.lbl_total_beer_value.text = f"ПИВО : {str(total_beer_value)}"
		total_beer_litrage_raw = f"{total_beer_litrage:,.2f}".replace(",", " ")
		self.ids.lbl_total_beer_litrage.text = f"{total_beer_litrage_raw} л."

		self.ids.lbl_total_SAD_value.text = f"К.А.Н. : {str(total_SAD_value)}"
		total_SAD_litrage_raw = f"{total_SAD_litrage:,.2f}".replace(",", " ")
		self.ids.lbl_total_SAD_litrage.text = f"{total_SAD_litrage_raw} л."

		self.ids.lbl_total_NAD_value.text = f"Б.Н. : {str(total_NAD_value)}"
		total_NAD_litrage_raw = f"{total_NAD_litrage:,.2f}".replace(",", " ")
		self.ids.lbl_total_NAD_litrage.text = f"{total_NAD_litrage_raw} л."

		self.ids.lbl_total_WAATER_value.text = f"ВОДА : {str(total_WATER_value)}"
		total_WATER_litrage_raw = f"{total_WATER_litrage:,.2f}".replace(",", " ")
		self.ids.lbl_total_WATER_litrage.text = f"{total_WATER_litrage_raw} л."

		conn.commit()
		conn.close()