# -*- coding: utf-8 -*-


# system libraries
import re
import os
# import sys
# import shutil
import sqlite3
import uuid
from datetime import datetime

# kivy and kivymd
import asynckivy
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemSupportingText, MDListItemTertiaryText, MDListItemTrailingIcon

# custom libraries
from custom_libs import utils, db

# externally stored classes
from class_libs.Money import Money

# data
from data import global_vars, menus, items

# path
APP_PATH = global_vars.APP_PATH


class IncomeItemsScreen(MDScreen):

    def on_enter(self):
        Clock.schedule_once(lambda x: asynckivy.start(self.show_items_in_wh_cart()))



    # NOTIFICATION
    def notification(self, msg_type, message):
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text=msg_type,
                halign="left",
            ),
            MDDialogSupportingText(
                text=message,
                halign="left",
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Закрыть"),
                    style="text",
                    on_release=self.close_dialog
                ),
                spacing="10dp",
            ),
            size_hint=(0.9, None)
        )
        self.dialog.open()

    def close_dialog(self, obj):
        self.dialog.dismiss()



    # CANCEL OPERATION
    def cancel_receiving_items(self):
        db.clear_cart(["wh_cart"])
        self.ids.stock_addr.text = ""
        self.ids.received_item.text = ""
        self.ids.received_item_qty.text = ""
        self.ids.received_item_comment.text = ""
        self.ids.wh_cart_items.clear_widgets()

        self.app = MDApp.get_running_app()
        return self.app.goback_screen_0()



    # MENUs
    def open_items_sources_menu(self):
        matching = menus.ITEMS_SOURCES_DICT.keys()
        menu_items = [
            {
                "text": i,
                "on_release": lambda x=i: self.set_id_item(x),
            } for i in matching]
        self.menu = MDDropdownMenu(
            caller=self.ids.stock_addr,
            items=menu_items,
            position="bottom",
            width_mult=1
        )
        self.menu.open()

    def set_id_item(self, text_item):
        self.ids.stock_addr.text = text_item
        self.menu.dismiss()
        self.ids.received_item.focus = True



    def open_items_menu(self):
        matching = items.ITEMS_DICT.keys()
        menu_items = [
            {
                "text": i,
                "on_release": lambda x=i: self.set_item(x),
            } for i in matching]
        self.menu = MDDropdownMenu(
            caller=self.ids.received_item,
            items=menu_items,
            position="bottom",
            width_mult=1
        )
        self.menu.open()

    def set_item(self, text_item):
        self.ids.received_item.text = text_item
        self.menu.dismiss()
        self.ids.received_item_qty.focus = True



    def open_on_text_items_menu(self):
        try:
            self.menu.dismiss()
        except:
            pass

        text = self.ids.received_item.text

        if len(text) in range(3,7):
            matching = [s for s in items.ITEMS_DICT.keys() if text.upper() in s.upper()]
            menu_items = [
                {
                    "text": i,
                    "on_release": lambda x=i: self.set_item(x),
                } for i in matching]
            self.menu = MDDropdownMenu(
                caller=self.ids.received_item,
                items=menu_items,
                position="bottom",
                width_mult=1
            )
            self.menu.open()



    def on_enter_check_item(self):
        try:
            self.menu.dismiss()
        except:
            pass

        item_name = self.ids.received_item.text

        if item_name not in items.ITEMS_DICT.keys():
            # self.item_price = None
            self.ids.received_item.text = ""
            self.ids.received_item.focus = True
            return self.notification("Ошибка", "Неверно указано название товара или такого товара нет.")

        self.ids.received_item_qty.focus = True
        # self.item_price = ITEMS_LIST[item_name][0]



    def qty_corrector(self):

        qty_txt = self.ids.received_item_qty.text

        qty = utils.match_qty(qty_txt)

        if qty == False:
            self.ids.received_item_qty.focus = True
            return self.notification("Ошибка", "Неверно указано количество.")

        if qty != False:
            self.ids.received_item_qty.text = qty
            self.ids.received_item_comment.focus = True



    def on_comment_validate(self):

        self.ids.received_item_comment.text = self.text_corrector(self.ids.received_item_comment.text)

        cheked = self.check_textfields_values()

        if cheked == True:
            self.add_items_to_wh_cart()
            # self.show_items_in_wh_cart()
            Clock.schedule_once(lambda x: asynckivy.start(self.show_items_in_wh_cart()))



    def text_corrector(self, txt_raw):
        txt = txt_raw.upper()
        t_0 = re.sub(r"\W+", " ", txt)
        t_1 = re.sub(r"\s+", " ", t_0)
        t_2 = re.sub(r"^\s+", "", t_1)
        t_3 = re.sub(r"\s+$", "", t_2)
        return t_3



    def check_textfields_values(self):

        # GET DATA
        text_fields = [
            self.ids.stock_addr.text,
            self.ids.received_item.text,
            self.ids.received_item_qty.text,
            self.ids.received_item_comment.text
        ]
        
        # item source
        items_source = text_fields[0]
        if items_source not in menus.ITEMS_SOURCES_DICT.keys():
            return self.notification("Ошибка", "Неверно указан источник товара.\nВыберите источник из выпадающего списка.")

        # item name
        item_name = text_fields[1]
        if item_name not in items.ITEMS_DICT.keys():
            return self.notification("Ошибка", "Неверно указано название товара или такого товара нет.\nВыберите товар из выпадающего списка.")

        # item qty
        item_qty = utils.match_qty(text_fields[2])
        if item_qty == False:
            return self.notification("Ошибка", "Неверно указано количество.")

        if item_qty == 0:
            return self.notification("Ошибка", "Количество не может быть равным 0")

        self.ids.received_item_qty.text = item_qty

        # comment to item
        item_comment = self.text_corrector(text_fields[3])
        self.ids.received_item_comment.text = item_comment

        return True



    def add_items_to_wh_cart(self):

        # GET DATA
        item_name = self.ids.received_item.text
        item_qty = self.ids.received_item_qty.text
        item_comment = self.ids.received_item_comment.text

        item_art = items.ITEMS_DICT[item_name][1]
        item_price = items.ITEMS_DICT[item_name][0]

        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

        APP_USER = global_vars.USER_ID

        # create db or connect & create a cursor
        conn = sqlite3.connect(os.path.join(APP_PATH, "dbs/main_whm.db"))
        c = conn.cursor()

        c.execute("SELECT cart_item_qty FROM wh_cart WHERE whm_uuid=:whm_uuid and item_art=:item_art",
            {
                "whm_uuid": APP_USER,
                "item_art": item_art
            }
        )
        existing_item_qty_raw = c.fetchall()

        if len(existing_item_qty_raw) == 0:

            item_total_value = str(float(item_price) * float(item_qty))
            # add a record
            c.execute("INSERT INTO wh_cart VALUES (:dt, :item_art, :item_name, :item_price, :cart_item_qty, :item_total_value, :whm_uuid, :item_comment)",
                {
                    "dt": formatted_time,
                    "item_art": item_art,
                    "item_name": item_name,
                    "item_price": item_price,
                    "cart_item_qty": item_qty,
                    "item_total_value": item_total_value,
                    "whm_uuid": APP_USER,
                    "item_comment": item_comment
                }
            )

        else:
            existing_item_qty = existing_item_qty_raw[0][0]
            qty_sum = int(existing_item_qty) + int(item_qty)
            new_total_value = str(float(item_price) * float(qty_sum))

            c.execute("UPDATE wh_cart SET dt = ?, cart_item_qty = ?, item_total_value = ?, whm_uuid = ?, item_comment = ? WHERE whm_uuid =? and item_art = ?",
                (formatted_time, qty_sum, new_total_value, APP_USER, item_comment, APP_USER, item_art)
            )

        # commit changes & close connection
        conn.commit()
        conn.close()

        self.ids.received_item.text = ""
        self.ids.received_item_qty.text = ""
        self.ids.received_item_comment.text = ""



    async def show_items_in_wh_cart(self):

        APP_USER = global_vars.USER_ID

        ct_list = "wh_cart_items"
        self.ids[ct_list].clear_widgets()

        # create db or connect & create a cursor
        conn = sqlite3.connect(os.path.join(APP_PATH, "dbs/main_whm.db"))
        c = conn.cursor()
        # grab records from db
        c.execute("SELECT * FROM wh_cart WHERE whm_uuid=:whm_uuid ORDER BY item_name DESC", {"whm_uuid": APP_USER})
        records = c.fetchall()

        for record in records:

            unique_item_name = record[2]
            item_art = record[1]
            item_litrage = float(items.ITEMS_DICT[unique_item_name][2])
            total_item_qty = int(record[4])
            total_item_qty_formatted = f"{total_item_qty:,.2f}".replace(",", " ")
            total_item_litrage = item_litrage * total_item_qty
            total_item_litrage_formatted = f"{total_item_litrage:,.2f}".replace(",", " ")
            item_price = Money.mint(float(record[3]))
            total_item_amount = Money.mint(float(record[5]))


            self.ids[ct_list].add_widget(
                MDListItem(
                    MDListItemHeadlineText(
                        id="headliner",
                        text=unique_item_name,
                    ),
                    MDListItemSupportingText(
                        text=f"{item_litrage} л.  x  {total_item_qty_formatted} шт.  =  {total_item_litrage_formatted} л.",
                    ),
                    MDListItemTertiaryText(
                        text=f"{item_price}  |  {total_item_amount}",
                    ),
                    id=unique_item_name,
                    on_press=lambda x: self.remove_item_notification(x.id)
                )
            )

        # commit changes & close connection
        conn.commit()
        conn.close()



    ART_ID_TO_REMOVE = None


    def remove_item_notification(self, item_id):
        self.ART_ID_TO_REMOVE = item_id
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text=item_id,
                halign="left",
            ),
            MDDialogSupportingText(
                text="Удалить товар из списка?",
                halign="left",
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Отмена"),
                    style="text",
                    on_release=self.close_dialog
                ),
                MDButton(
                    MDButtonText(text="Удалить"),
                    style="text",
                    on_press=self.remove_item_from_wh_cart,
                    on_release=self.close_dialog
                ),
                spacing="10dp",
            ),
            size_hint=(0.9, None)
        )
        self.dialog.open()



    def remove_item_from_wh_cart(self, *args):

        APP_USER = global_vars.USER_ID
        item_art = self.ART_ID_TO_REMOVE

        conn = sqlite3.connect(os.path.join(APP_PATH, "dbs/main_whm.db"))
        c = conn.cursor()
        c.execute("DELETE from wh_cart WHERE whm_uuid=:whm_uuid and item_name=:item_name", {"whm_uuid": APP_USER, "item_name": item_art})
        conn.commit()
        conn.close()

        # self.show_items_in_wh_cart("wh_cart_items")
        Clock.schedule_once(lambda x: asynckivy.start(self.show_items_in_wh_cart()))
        self.ART_ID_TO_REMOVE = None




    def submit_new_items_manually(self):

        APP_USER = global_vars.USER_ID

        # get variables
        items_source = self.ids.stock_addr.text

        if items_source not in menus.ITEMS_SOURCES_DICT.keys():
            return self.notification("Ошибка", "Неверно указан источник товара.\nВыберите источник из выпадающего списка.")

        source = menus.ITEMS_SOURCES_DICT[items_source]


        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

        # Generate a new transaction UUID
        new_uuid = uuid.uuid4()
        corrected_uuid = str(re.sub("-", "", str(new_uuid)))
        transaction_id = f"wh_{corrected_uuid}"

        # create db or connect & create a cursor
        conn = sqlite3.connect(os.path.join(APP_PATH, "dbs/main_whm.db"))
        c = conn.cursor()

        # get records from wh_cart
        c.execute("SELECT * FROM wh_cart WHERE whm_uuid=:whm_uuid", {"whm_uuid": APP_USER})
        records = c.fetchall()

        if len(records) == 0:
            return self.notification("Ошибка", "Ни один товар не добавлен в корзину.\nВыберите товар из выпадающего списка и нажмите Enter, далее укажите количество, снова нажмите Enter, при необходимости напишите коментарий к товару, и нажмите Enter.")

        for record in records:

            # prepare variables
            item_art = record[1]
            item_name = record[2]
            item_price = record[3]
            item_qty = record[4]
            item_comment = record[7]

            # get stock data
            c.execute("SELECT item_stock_qty FROM stock_items WHERE whm_uuid=:whm_uuid and item_art=:item_art", {"whm_uuid": APP_USER, "item_art": item_art})
            existing_item_qty_raw = c.fetchall()

            if len(existing_item_qty_raw) == 0:

                item_total_value = str(float(item_price) * float(item_qty))
                # add a record
                c.execute("INSERT INTO stock_items VALUES (:dt, :item_art, :item_name, :item_price, :item_stock_qty, :item_total_value, :whm_uuid)",
                    {
                        "dt": formatted_time,
                        "item_art": item_art,
                        "item_name": item_name,
                        "item_price": item_price,
                        "item_stock_qty": item_qty,
                        "item_total_value": item_total_value,
                        "whm_uuid": APP_USER
                    }
                )

            else:
                existing_item_qty = existing_item_qty_raw[0][0]
                qty_sum = int(existing_item_qty) + int(item_qty)
                new_total_value = str(float(item_price) * float(qty_sum))

                c.execute("UPDATE stock_items SET dt = ?, item_name = ?, item_price = ?, item_stock_qty = ?, item_total_value = ?, whm_uuid = ? WHERE whm_uuid =? and item_art = ?",
                    (formatted_time, item_name, item_price, qty_sum, new_total_value, APP_USER, APP_USER, item_art)
                )

            # warehouse transactions
            c.execute("INSERT INTO warehouse_transactions VALUES (:dt, :transaction_uuid, :item_art, :item_name, :item_qty, :type, :comment, :whm_id, :agent_uuid)",
                {
                    "dt": formatted_time,
                    "transaction_uuid": transaction_id,
                    "item_art": item_art,
                    "item_name": item_name,
                    "item_qty": item_qty,
                    "type": source,
                    "comment": item_comment,
                    "whm_id": APP_USER,
                    "agent_uuid": ""
                }
            )

        # commit changes & close connection
        conn.commit()
        conn.close()

        # clear inputs
        self.cancel_receiving_items() # it cleans everything
        return