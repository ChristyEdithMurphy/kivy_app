# -*- coding: utf-8 -*-


# data
from data import users
from data import global_vars

# system libraries
import os
# import sys
# import shutil
# import re
# import random
# import string
from pathlib import Path

# kivy and kivymd
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import (
    ScreenManager,
    Screen,
    NoTransition, SwapTransition
)

from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)

from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
# from kivymd.uix.boxlayout import MDBoxLayout
# from kivy.uix.boxlayout import BoxLayout

from kivy.clock import Clock

from kivy.utils import platform

if platform == 'android':
    from android import api_version, mActivity
    from android.permissions import request_permissions, check_permission, Permission
    # Application path
    global_vars.APP_PATH = os.path.dirname(os.path.abspath(__file__))
    global_vars.EXTERNAL_STORAGE_PATH = "/sdcard/Download/Argus"

else:
    # Application path
    global_vars.APP_PATH = Path().absolute()
    global_vars.EXTERNAL_STORAGE_PATH = "./Argus"

# custom libraries
from custom_libs import utils, db

# externally stored classes
from class_libs.DashScreen import DashScreen
from class_libs.IncomeItemsScreen import IncomeItemsScreen
from class_libs.OutgoingItemsScreen import OutgoingItemsScreen
from class_libs.QRScannerScreen import QRScannerScreen



class WindowManager(ScreenManager):
    '''A window manager to manage switching between sceens.'''

# declare the screens
class LoginScreen(MDScreen):
    pass



class ArgusApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if platform == 'android':
            self.permissions = [
                Permission.ACCESS_COARSE_LOCATION,
                Permission.ACCESS_FINE_LOCATION,
                Permission.CAMERA,
                Permission.INTERNET,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ]



    def build(self):
        ''' Initializes the Application and returns the root widget'''
        
        # customize theme
        current_theme_style = utils.theme_style()

        self.theme_cls.theme_style = current_theme_style
        self.theme_cls.primary_palette = "Darkslategray"
        self.theme_cls.accent_palette = 'Red'
        self.theme_cls.accent_hue = '400'
        self.title = "BEERS"
        
        # load kv files
        self.load_all_kv_files()
        
        # set screen manager
        self.wm = WindowManager(transition=NoTransition())
        
        self.screens = [
            LoginScreen(name='login'),
            DashScreen(name='dash'),
            IncomeItemsScreen(name='incoming_items_screen'),
            OutgoingItemsScreen(name='outgoing_items_screen'),
            QRScannerScreen(name='qr_scanner_screen'),
            # SearchFilters(name='person_search_filters_page'),
            # TakePicture(name='take_picture_page'),
            # StartBot(name='start_bot_page'),
            # SearchResults(name='person_search_results_page'),
            # SelectFaceImg(name='select_face_image_page'),
            # FaceGalery(name='face_galery_page'),
            # AddVisa(name='add_visa_screen'),
            # AddIDDoc(name='add_id_doc_screen'),
            # PersonalDocs(name='personal_docs_page'),
            # Visas(name='visas_page'),
            # Contacts(name='contacts_page'),
            # Emails(name='emails_page'),
            # ACs(name='acs_page'),
            # ProfileScreen(name='profile'),
            # UploadScreen(name='upload')
        ]
        self.wm.add_widget(self.screens[0])
        
        return self.wm


    # LOAD KV SCREENS
    def load_all_kv_files(self):
        Builder.load_file('screens/login_screen.kv')
        Builder.load_file('screens/dash_screen.kv')
        Builder.load_file('screens/incoming_items_screen.kv')
        Builder.load_file('screens/outgoing_items_screen.kv')
        Builder.load_file('screens/qr_scanner_screen.kv')
        # Builder.load_file('screens/person_search_filters_page.kv')
        # Builder.load_file('screens/take_picture.kv')
        # Builder.load_file('screens/start_bot.kv')
        # Builder.load_file('screens/person_search_results_page.kv')
        # Builder.load_file('screens/select_face_image_page.kv')
        # Builder.load_file('screens/face_galery_page.kv')
        # Builder.load_file('screens/add_visa_screen.kv')
        # Builder.load_file('screens/add_id_doc_screen.kv')
        # Builder.load_file('screens/personal_docs_screen.kv')
        # Builder.load_file('screens/visas_screen.kv')
        # Builder.load_file('screens/contacts_screen.kv')
        # Builder.load_file('screens/emails_screen.kv')
        # Builder.load_file('screens/acs_screen.kv')
        # Builder.load_file('screens/profile_screen.kv')
        # Builder.load_file('screens/upload_screen.kv')


    # STYLING
    def switch_theme_style(self):
        self.theme_cls.theme_style = (
            "Light" if self.theme_cls.theme_style == "Dark" else "Dark"
        )
        self.root.md_bg_color = self.theme_cls.surfaceColor


    def on_start(self):
        def on_start(*args):
            self.root.md_bg_color = self.theme_cls.surfaceColor

        Clock.schedule_once(on_start)



    # NOTIFICATIONS
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



    # GOTOs
    PREVIOUS_SCREEN_LVL_0 = None
    PREVIOUS_SCREEN_LVL_1 = None
    PREVIOUS_SCREEN_LVL_2 = None
    PREVIOUS_SCREEN_LVL_3 = None
    PREVIOUS_SCREEN_LVL_4 = None
    PREVIOUS_SCREEN_LVL_5 = None
    PREVIOUS_SCREEN_LVL_6 = None


    def goto_dash_after_login(self):
        key_pass = self.wm.get_screen("login").ids.agent_key_id.text

        if str(key_pass) not in users.USERS_DICT.values():
            return self.notification("Erreur", "Mot de passe est incorrect")

        if str(key_pass) in users.USERS_DICT.values():
            global_vars.USER_ID = [key for key, value in users.USERS_DICT.items() if value == key_pass][0]
            self.wm.switch_to(self.screens[1])
            self.PREVIOUS_SCREEN_LVL_0 = 1
            self.wm.remove_widget(self.wm.get_screen('login'))
            # print(self.wm.screen_names)
            utils.check_or_make_dir("dbs")
            utils.simple_check_or_make_dir(global_vars.EXTERNAL_STORAGE_PATH)
            db.check_create_dbs()


    # def goto_take_picure(self):
    #     self.wm.switch_to(self.screens[3])
    #     self.PREVIOUS_SCREEN_LVL_1 = 2
    #     # self.wm.remove_widget(self.wm.get_screen('dash'))
    #     # self.notification("Path:", str(global_vars.APP_PATH))
    #     # Builder.unbind_widget(self.wm.get_screen('dash'))
    #     # Builder.unload_file('screens/dash_screen.kv')
    #     # print(self.wm.screen_names)

    def goto_receive_items(self):
        self.wm.switch_to(self.screens[2])
        self.PREVIOUS_SCREEN_LVL_1 = 1


    def goto_release_items(self):
        self.wm.switch_to(self.screens[3])
        self.PREVIOUS_SCREEN_LVL_1 = 1


    def goto_qr_scanner(self):
        self.wm.switch_to(self.screens[4])
        self.PREVIOUS_SCREEN_LVL_1 = 1


    # def goto_search_filters(self):
    #     self.wm.switch_to(self.screens[2])
    #     self.PREVIOUS_SCREEN_LVL_1 = 2
    #     # self.wm.remove_widget(self.wm.get_screen('dash'))
    #     # self.notification("Path:", str(global_vars.APP_PATH))
    #     # Builder.unbind_widget(self.wm.get_screen('dash'))
    #     # Builder.unload_file('screens/dash_screen.kv')
    #     # print(self.wm.screen_names)


    # def goto_search_results(self):
    #     self.wm.switch_to(self.screens[3])
    #     self.PREVIOUS_SCREEN_LVL_2 = 3
    #     # self.wm.remove_widget(self.wm.get_screen('person_search_filters_page'))
    #     # print(self.wm.screen_names)


    # def goto_select_face_image_page(self):
    #     self.wm.switch_to(self.screens[4])
    #     self.PREVIOUS_SCREEN_LVL_3 = 4
    #     # self.wm.remove_widget(self.wm.get_screen('person_search_results_page'))


    # def goto_face_galery_page(self):
    #     self.wm.switch_to(self.screens[5])
    #     self.PREVIOUS_SCREEN_LVL_4 = 5
    #     # self.wm.remove_widget(self.wm.get_screen('person_search_results_page'))


    # def goto_add_visa(self):
    #     self.wm.switch_to(self.screens[6])
    #     self.PREVIOUS_SCREEN_LVL_5 = 6
    #     # self.wm.remove_widget(self.wm.get_screen('person_search_results_page'))


    # # def goto_add_id_doc(self):
    # #     self.wm.switch_to(self.screens[6])
    # #     self.PREVIOUS_SCREEN_LVL_5 = 6
    # #     # self.wm.remove_widget(self.wm.get_screen('person_search_results_page'))


    # # def goto_personal_docs(self):
    # #     self.wm.switch_to(self.screens[7])
    # #     self.PREVIOUS_SCREEN_LVL_6 = 7
    # #     # self.wm.remove_widget(self.wm.get_screen('person_search_results_page'))



    # # GOBACKS
    def goback_screen_0_from_camera(self):
        self.wm.switch_to(self.screens[self.PREVIOUS_SCREEN_LVL_0])
        self.wm.remove_widget(self.wm.get_screen('qr_scanner_screen'))
        # print(self.wm.screen_names)

    def goback_screen_0(self):
        self.wm.switch_to(self.screens[self.PREVIOUS_SCREEN_LVL_0])
        # self.wm.remove_widget(self.wm.get_screen('take_picture_page'))
        # print(self.wm.screen_names)

    # def goback_screen_1(self):
    #     self.wm.switch_to(self.screens[self.PREVIOUS_SCREEN_LVL_1])
    #     # print(self.wm.screen_names)

    # def goback_screen_2(self):
    #     self.wm.switch_to(self.screens[self.PREVIOUS_SCREEN_LVL_2])
    #     # print(self.wm.screen_names)

    # def goback_screen_3(self):
    #     self.wm.switch_to(self.screens[self.PREVIOUS_SCREEN_LVL_3])
    #     # print(self.wm.screen_names)

    # def goback_screen_4(self):
    #     self.wm.switch_to(self.screens[self.PREVIOUS_SCREEN_LVL_4])
    #     # print(self.wm.screen_names)

    # def goback_screen_5(self):
    #     self.wm.switch_to(self.screens[self.PREVIOUS_SCREEN_LVL_5])
    #     # print(self.wm.screen_names)



ArgusApp().run()
