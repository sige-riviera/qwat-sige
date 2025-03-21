# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFile,
    QgsProcessingOutputVectorLayer,
    QgsProcessingException,
    QgsVectorLayer,
    QgsProject
)
import os
import processing

class ShapefileListFromFolder(QgsProcessingAlgorithm):
    FOLDER_PATH = 'FOLDER_PATH'  # Input folder containing shapefiles
    OUTPUT = 'OUTPUT'  # List of layer objects
    FALLBACK_ENCODING = 'ISO-8859-1'  # Fallback default encoding if not set (e.g. for Happy Survey)
    ENCODING_PRIORITY_ORDER = ['ENCODING', 'CPG_ENCODING', 'LDID_ENCODING']

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ShapefileListFromFolder()

    def name(self):
        return 'shapefile_list_from_folder'

    def displayName(self):
        return self.tr("Lister toutes les couches shapefile d'un dossier")

    def group(self):
        return self.tr('Script pour modèle Import relevés')

    def groupId(self):
        return 'exportImportScripts'

    def shortHelpString(self):
        return self.tr("Cet algorithme génère une liste d'objets couche à partir des shapefiles dans un dossier spécifié pour import_survey_data.model3.")
    
    def getEncodingHelper(self, encoding_dict):
        # Loop encoding priority order
        for key in self.ENCODING_PRIORITY_ORDER:
            value = encoding_dict.get(key)
            # Check that value is not None neither en empty string
            if value not in (None, ''):
                return value
        
        # If no valid value is found, returns NULL
        return None

    def initAlgorithm(self, config=None):
        # Input parameter: folder path using QgsProcessingParameterFile in Folder mode
        self.addParameter(
            QgsProcessingParameterFile(
                self.FOLDER_PATH,
                self.tr('Dossier contenant les shapefiles'),
                behavior=QgsProcessingParameterFile.Folder
            )
        )

        # Output parameter: list of layer objects
        self.addOutput(
            QgsProcessingOutputVectorLayer(
                self.OUTPUT,
                self.tr('Liste des couches shapefile')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Retrieve the folder path from the parameters
        folder_path = self.parameterAsString(parameters, self.FOLDER_PATH, context)

        # Force path cleaning and formatting
        folder_path = os.path.normpath(os.path.expandvars(folder_path.strip()))
        
        # Debugging comments
        #feedback.pushInfo(f"Paramètres: {parameters}")
        #feedback.pushInfo(f"Chemin brut reçu : {repr(folder_path)}")
        #feedback.pushInfo(f"Chemin normalisé : {folder_path}")

        # Check if the folder exists
        if not folder_path or not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            raise QgsProcessingException(self.tr("Le dossier spécifié n'existe pas ou n'est pas un dossier valide."))

        # List of layer objects
        layers = []

        # Traverse the folder to find all .shp files
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.shp'):
                    shapefile_path = os.path.join(root, file)
                    processing_params = {
                        'INPUT': shapefile_path
                    }
                    encoding_outputs = processing.run('native:shpencodinginfo', processing_params) # Use native QGIS processing to get shapefile encoding information from file and not from QgsLayer
                    encoding = self.getEncodingHelper(encoding_outputs)
                    
                    try:
                        # Load the shapefile layer into QGIS
                        layer = QgsVectorLayer(shapefile_path, file, 'ogr')
                        
                        # Check and apply encoding if needed
                        if encoding is None:
                            layer.dataProvider().setEncoding(self.FALLBACK_ENCODING)
                            feedback.pushWarning(f"Le shapefile {file} n'a pas d'information d'encodage. L'encodage suivant a été appliqué : {layer.dataProvider().encoding()}")
                        
                        if layer.isValid():
                            # Add the layer to the project
                            QgsProject.instance().addMapLayer(layer, False)  # Add the layer to the project without making it visible
                            layers.append(layer)
                            QgsProject.instance().removeMapLayer(layer)  # Remove the layer from the project
                        else:
                            # Warn that the layer is invalid
                            feedback.pushWarning(f"Couche invalide: {shapefile_path}")
                    except Exception as e:
                        feedback.pushWarning(f"Erreur lors du chargement de {shapefile_path}: {str(e)}")

        # If no layers are found, generate a warning message
        if not layers:
            feedback.pushWarning("Aucun shapefile valide dans le dossier.")

        # Return the list of layer objects, or an empty layer if none are valid
        return {self.OUTPUT: layers}
 