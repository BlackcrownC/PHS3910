import numpy as np
import matplotlib as plt
import pycromanager
from pycromanager import Core
import time
import os
import cv2
from typing import Any

import pylablib as pll
from pylablib.devices import Thorlabs
import pylablib
from pylablib.devices import Thorlabs
import thorlabs_tsi_sdk
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK, OPERATION_MODE, TLCameraError


class CameraController:
    def __init__(self):
        self.camera: Any = None
        self.sdk: Any = None
        self.img_ext = "tiff"
        self.vid_ext = "avi"

    def init_values(self):
        self.camera.exposure_time_us = 30000  # Exemple de temps d'exposition de 25 ms (tester sur Thorlab)
        self.camera.black_level = 5
        self.camera.gain = 0
        self.camera.frames_per_trigger_zero_for_unlimited = 1  # Mode de capture continue : 0 ; Mode de capture ponctuel : 1

    def __enter__(self):
        try:
            pll.par["devices/dlls/thorlabs_tlcam"] = "path/to/dlls"
            print(Thorlabs.list_cameras_tlcam())
            # Initialiser le SDK
            self.sdk = TLCameraSDK()
            print("SDK initialisé avec succès.")

            # Découvrir les caméras disponibles
            available_cameras = self.sdk.discover_available_cameras()
            print(f"Caméras disponibles : {available_cameras}")
            if not available_cameras:
                print("Aucune caméra trouvée. Vérifiez la connexion.")
                self.camera.dispose()
                exit()
            self.camera = self.sdk.open_camera(available_cameras[0])
            print(f"Caméra connectée avec succès : {available_cameras[0]}")
            self.init_values()
            return self
        except TLCameraError as e:
            print(f"Erreur SDK : {e}")
        finally:
            # Nettoyer le SDK correctement
            if 'sdk' in locals():
                self.sdk.dispose()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.camera.disarm()
        self.camera.dispose()
        # Nettoyer le SDK correctement
        if 'sdk' in locals():
            self.sdk.dispose()

    def capture(self, output_path: str = "test"):
        self.camera.arm(2)  # Préparez la caméra avec 2 tampons
        print("Caméra armée et prête pour capturer des images.")

        # Commencer à capturer des images
        self.camera.issue_software_trigger()
        time.sleep(2)
        print("Capture d'images en cours...")
        frame = self.camera.get_pending_frame_or_null()

        if frame is not None:
            print(f"Image capturée avec succès : {frame.frame_count}")
            image = frame.image_buffer  # Assurez-vous que cet attribut est correct
            cv2.imshow('Image Capturee', image)  # Affichez l'image
            cv2.waitKey(0)  # Attendez une touche pour fermer la fenêtre

            # Enregistrer l'image en format TIFF
            cv2.imwrite(f"{output_path}.{self.img_ext}", image)
            print(f"Image enregistrée sous : {output_path}")
        else:
            print("Aucune image capturée.")

        # Désarmer et fermer la caméra après utilisation
        self.camera.disarm()
        print("Caméra désarmée et fermée.")

    def record_video(self, nombre_image_par_seconde: int = 10, record_time: float = 1.0, output_path: str = "test"):
        self.camera.arm(2)  # Préparez la caméra avec 2 tampons
        print("Caméra armée et prête pour capturer des images.")

        # Définir les dimensions de la vidéo
        frame_width = self.camera.image_width_pixels
        frame_height = self.camera.image_height_pixels
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(f"{output_path}.{self.vid_ext}", fourcc, nombre_image_par_seconde,
                              (frame_width, frame_height), isColor=False)

        for picture_number in range(int(nombre_image_par_seconde * record_time)):
            self.camera.issue_software_trigger()
            # Commencer à capturer des imagesc
            time.sleep(1/nombre_image_par_seconde)
            print("Capture d'images en cours...")
            frame = self.camera.get_pending_frame_or_null()

            if frame is not None:
                print(f"Image capturée avec succès : {frame.frame_count}")
                # cv2.imshow('Image Capturee', image)  # Affichez l'image
                # cv2.waitKey(0)  # Attendez une touche pour fermer la fenêtre

                # Enregistrer l'image en format video
                image = np.array(frame.image_buffer, dtype=np.uint8).reshape((frame_height, frame_width))
                out.write(image)
            else:
                print("Unable to acquire image, program exiting...")

        # Désarmer et fermer la caméra après utilisation
        self.camera.disarm()
        print("Caméra désarmée et fermée.")

    def get_image(self, filename: str = "test", is_video: bool = False):
        if is_video:
            image = cv2.VideoCapture(f"{filename}.{self.vid_ext}")
            return image
        image = cv2.imreadmulti(f"{filename}.{self.img_ext}", flags=cv2.IMREAD_LOAD_GDAL)[1]
        image = np.float32(np.array(image))
        return image


with CameraController() as camera_controller:
    # camera_controller.capture()
    camera_controller.record_video(10, 10, "test")
