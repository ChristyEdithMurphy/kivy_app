# -*- coding: utf-8 -*-


# system libraries
import re
import os
import time

# kivy and kivymd
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import (
	MDDialog,
	MDDialogIcon,
	MDDialogHeadlineText,
	MDDialogSupportingText,
	MDDialogButtonContainer,
	MDDialogContentContainer,
)
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.camera import Camera
from kivy.graphics import Rotate, PushMatrix, PopMatrix, Rectangle
from kivy.graphics.texture import Texture

from os.path import exists, join

# custom libraries
from custom_libs import utils, db

# data
from data import global_vars

# path
APP_PATH = global_vars.APP_PATH
EXTERNAL_STORAGE_PATH = global_vars.EXTERNAL_STORAGE_PATH

import cv2
import numpy as np

from kivy.clock import Clock
import asynckivy

# from pyzbar.pyzbar import ZBarSymbol
# from pyzbar.pyzbar import decode, ZBarSymbol



class QRScannerScreen(MDScreen):

	CAM = None


	def on_enter(self):
		self.CAM = None
		self.turn_camera_on()



	def turn_camera_on(self):
		self.CAM = Camera(
			# size_hint=(1, 1),
			size=(1080, 1080),
			resolution=(1080, 1080),
			# texture_size=(960,960),
			# pos_hint={"center_x": .5, "center_y": 0.5},
			play=True,
			# allow_stretch=True,
			# keep_ratio=True,
			# fit_mode="cover"
		)
		with self.CAM.canvas.before:
			PushMatrix()
			Rotate(angle=-90, origin=self.center)

		with self.CAM.canvas.after:
			PopMatrix()

		# self.CAM.texture_size = (960, 960)

		self.ids.camera_layout.clear_widgets()
		self.ids.camera_layout.add_widget(
			self.CAM
		)

		# Clock.schedule_interval(self.update, 1.0 / 30.0) # 30 fps



	# def update(self, dt):

	# 	detector = cv2.QRCodeDetector()

	# 	texture = self.CAM.texture

	# 	if texture:
	# 		pixels = texture.pixels
	# 		frame = np.frombuffer(pixels, np.uint8).reshape(texture.height, texture.width, 4)
	# 		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	# 		data, bbox, _ = detector.detectAndDecode(gray)
	# 		if data:
	# 			self.stop_camera()
	# 			self.notification("QR content:", data)


	# def take_picture_etc(self):
	# 	Clock.schedule_once(lambda x: asynckivy.start(self.take_pic()))


	# async def take_pic(self):
	# 	EXTERNAL_STORAGE_PATH = "/sdcard/Download/Argus"
	# 	# EXTERNAL_STORAGE_PATH = "./"
	# 	utils.simple_check_or_make_dir(EXTERNAL_STORAGE_PATH)
	# 	await asynckivy.sleep(0)

	# 	timestr = time.strftime("%Y%m%d_%H%M%S")
	# 	image_path = os.path.join(EXTERNAL_STORAGE_PATH, f"IMG_{timestr}.png")

	# 	# Using kivy export
	# 	if self.CAM != None:
	# 		self.CAM.export_to_png(image_path)

	# 		await asynckivy.sleep(0.2)
	# 		return self.stop_camera()



	def save_pic_via_cv(self):
		Clock.schedule_once(lambda x: asynckivy.start(self.take_and_save_pic_via_cv()))


	async def take_and_save_pic_via_cv(self):

		detector = cv2.QRCodeDetector()
		await asynckivy.sleep(0)

		timestr = time.strftime("%Y%m%d_%H%M%S")
		image_path = os.path.join(EXTERNAL_STORAGE_PATH, f"IMG_{timestr}.png")

		texture = self.CAM.texture

		if texture:
			pixels = texture.pixels
			frame = np.frombuffer(pixels, np.uint8).reshape(texture.height, texture.width, 4)
			# frame = np.frombuffer(pixels, np.uint8).reshape(texture.height, texture.width, -1)
			# Grayscale, flip the image horizontally (mirror image)
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			flipped_img = cv2.flip(gray, 0)
			rotated_img = cv2.rotate(flipped_img, cv2.ROTATE_90_CLOCKWISE)

			# IMPROVE QUALITY OPTION 1
			# Remove shadows
			dilated_img = cv2.dilate(rotated_img, np.ones((7, 7), np.uint8))
			bg_img = cv2.medianBlur(dilated_img, 21)
			diff_img = 255 - cv2.absdiff(rotated_img, bg_img)
			norm_img = cv2.normalize(diff_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)

			# Threshold using Otsu's
			# work_img = cv2.threshold(norm_img, 0, 255, cv2.THRESH_OTSU)[1]
			work_img = cv2.threshold(norm_img, 127, 255, cv2.THRESH_OTSU)[1]

			# # IMPROVE QUALITY OPTION 2
			# thresh = cv2.adaptiveThreshold(rotated_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
			# kernel = np.array([[0, -1, 0],
			# 					[-1, 5, -1],
			# 					[0, -1, 0]])
			# sharpened = cv2.filter2D(thresh, -1, kernel)

			# data = decode(work_img, symbols=[ZBarSymbol.QRCODE])
			# data = decode(work_img)
			data, bbox, _ = detector.detectAndDecode(rotated_img)
			if data:
				# print(data)
				# byte_string = data[0].data
				# string = byte_string.decode('utf-8')
				# # self.stop_camera()
				Clock.schedule_once(lambda x: asynckivy.start(self.notification("QR content:", data)))

			# write image
			cv2.imwrite(image_path, rotated_img)
			await asynckivy.sleep(0.3)
			return self.stop_camera()



	def stop_camera(self):
		# Clock.unschedule(self.take_pic)
		Clock.unschedule(self.take_and_save_pic_via_cv)
		self.CAM.play = False
		self.CAM.stopped = True
		time.sleep(1)
		# self.CAM._camera._device.release()
		self.CAM = None
		self.ids.camera_layout.clear_widgets()
		self.exit()



	def exit(self):
		self.app = MDApp.get_running_app()
		return self.app.goback_screen_0_from_camera()



	# NOTIFICATIONS
	async def notification(self, msg_type, message):
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
				MDButtonText(text="Отмена"),
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