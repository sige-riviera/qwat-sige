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
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterExpression,
                       QgsProcessingParameterString,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFile,
                       QgsExpression,
                       QgsVectorFileWriter,
                       QgsWkbTypes)
from qgis import processing
import os
import shutil  # For copying files


class ExportShapefileToFolderAlgorithm(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    FOLDER = 'FOLDER'
    PREFIX = 'PREFIX'
    SUFFIX = 'SUFFIX'
    USE_PREFIX = 'USE_PREFIX'
    OVERWRITE = 'OVERWRITE'  # New checkbox for overwriting
    OUTPUT = 'OUTPUT'
    QML_SOURCE = 'QML_SOURCE'  # New parameter for the .qml file

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ExportShapefileToFolderAlgorithm()

    def name(self):
        return 'export_shapefile_to_folder'

    def displayName(self):
        return self.tr('Export en shapefile dans un dossier')

    def group(self):
        return self.tr('Script pour modèle Import relevés')

    def groupId(self):
        return 'exportImportScripts'

    def shortHelpString(self):
        return self.tr("Exporte la couche en entrée vers une couche au format shapefile dans un dossier spécifié, avec un préfixe optionnel, et y ajoute le fichier de style QML. Permet d'écraser le fichier de destination si spécifié.")

    def initAlgorithm(self, config=None):
        # Input parameter for the vector layer
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Couche en entrée'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        # Parameter for the destination folder
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.FOLDER,
                self.tr('Dossier de destination')  # Interface to select a folder
            )
        )

        # Prefix as an expression
        self.addParameter(
            QgsProcessingParameterExpression(
                self.PREFIX,
                self.tr('Préfixe du nom du shapefile (Format: AAAAMMDD_)')
            )
        )

        # Suffix as a string
        self.addParameter(
            QgsProcessingParameterString(
                self.SUFFIX,
                self.tr('Nom du shapefile (sans extension)'),
                defaultValue='output'  # Default value for the suffix
            )
        )

        # Checkbox to enable or disable the prefix
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.USE_PREFIX,
                self.tr('Utiliser le préfixe dans le nom du fichier?'),
                defaultValue=True  # Default value to enable the prefix
            )
        )

        # Checkbox for overwriting
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OVERWRITE,
                self.tr('Ecraser le fichier de sortie s\'il existe?'),
                defaultValue=False  # Default value to disable overwriting
            )
        )

        # Parameter for the source QML file
        self.addParameter(
            QgsProcessingParameterFile(
                self.QML_SOURCE,
                self.tr('Chemin du fichier QML source à copier'),
                extension='qml'  # Limit files to .qml
            )
        )

        # Output parameter for the final layer
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Couche en sortie')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Get the input layer source
        source = self.parameterAsSource(parameters, self.INPUT, context)
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        # Get the folder path selected by the user
        folder_path = self.parameterAsString(parameters, self.FOLDER, context)
        if not folder_path:
            raise QgsProcessingException("Un dossier de destination doit être défini.")

        # Check if the user wants to use the prefix
        use_prefix = self.parameterAsBoolean(parameters, self.USE_PREFIX, context)

        # If the user chose to use the prefix, evaluate the expression
        prefix = ''
        if use_prefix:
            prefix_expr = self.parameterAsExpression(parameters, self.PREFIX, context)
            expression = QgsExpression(prefix_expr)

            # Check if the expression is valid
            if expression.hasParserError():
                raise QgsProcessingException(f"L'expression pour le préfixe est invalide: {expression.parserErrorString()}")

            # Evaluate the expression to get the prefix
            prefix = expression.evaluate()
            if expression.hasEvalError():
                raise QgsProcessingException(f"Erreur dans l'évaluation de l'expression pour le préfixe: {expression.evalErrorString()}")

            # Ensure the expression result is a non-empty string
            if not prefix or not isinstance(prefix, str):
                raise QgsProcessingException("L'expression du préfixe doit évaluer une chaîne de caractéres non vide.")

        # Get the suffix specified by the user
        suffix = self.parameterAsString(parameters, self.SUFFIX, context)
        
        # Construct the full path for the shapefile
        output_path = os.path.join(folder_path, f"{prefix}{'_' if use_prefix else ''}{suffix}.shp")

        # Check if the file already exists
        overwrite = self.parameterAsBoolean(parameters, self.OVERWRITE, context)
        if os.path.exists(output_path) and not overwrite:
            feedback.reportError(f"Le fichier '{output_path}' existe déjà, et l'écrasement du fichier est désactivé. Operation annulée.")
            return {}  # Do not execute the script if the file exists and overwriting is disabled

        # If the file exists and overwriting is allowed, delete it before creating a new file
        if os.path.exists(output_path) and overwrite:
            os.remove(output_path)
            feedback.pushInfo(f"Le fichier existant '{output_path}' a été supprimé.")

        # Determine if the source layer is in 3D (contains Z coordinates)
        geometry_type = source.wkbType()
        if QgsWkbTypes.hasZ(geometry_type):
            output_geometry_type = QgsWkbTypes.Point25D  # For point geometries with Z
        else:
            output_geometry_type = QgsWkbTypes.Point  # Stay in 2D if no Z

        # Create the shapefile specifying the geometry type (Point or Point25D)
        writer = QgsVectorFileWriter(output_path, 'UTF-8', source.fields(), output_geometry_type, source.sourceCrs(), 'ESRI Shapefile')

        if writer.hasError() != QgsVectorFileWriter.NoError:
            raise QgsProcessingException("Erreur lors de la création du shapefile: {}".format(writer.errorMessage()))

        # Write the features to the shapefile
        for feature in source.getFeatures():
            writer.addFeature(feature)

        del writer  # Close the writer

        # Copy the source QML file to the destination folder and rename it
        qml_source_path = self.parameterAsString(parameters, self.QML_SOURCE, context)
        if qml_source_path and os.path.isfile(qml_source_path):
            # Rename the QML file with the same name as the shapefile
            qml_destination_path = os.path.join(folder_path, f"{prefix}{'_' if use_prefix else ''}{suffix}.qml")
            shutil.copy(qml_source_path, qml_destination_path)  # Copy the QML file
            feedback.pushInfo(f"Le fichier QML a été copié dans: {qml_destination_path}")
        else:
            feedback.pushInfo("Le QML est invalide ou n'existe pas.")

        # Inform the user about the output file
        feedback.pushInfo("Le shapefile a été exporté vers: {}".format(output_path))

        # Return the output path as a result
        return {self.OUTPUT: output_path}
