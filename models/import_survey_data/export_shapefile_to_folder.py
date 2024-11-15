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
import shutil  # Pour le copier-coller de fichiers


class ExportShapefileToFolderAlgorithm(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    FOLDER = 'FOLDER'
    PREFIX = 'PREFIX'
    SUFFIX = 'SUFFIX'
    USE_PREFIX = 'USE_PREFIX'
    OVERWRITE = 'OVERWRITE'  # Nouvelle case à cocher pour l'écrasement
    OUTPUT = 'OUTPUT'
    QML_SOURCE = 'QML_SOURCE'  # Nouveau paramètre pour le fichier .qml

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ExportShapefileToFolderAlgorithm()

    def name(self):
        return 'exportshapefiletofolder'

    def displayName(self):
        return self.tr('Export to Shapefile in Folder')

    def group(self):
        return self.tr('Export scripts')

    def groupId(self):
        return 'exportscripts'

    def shortHelpString(self):
        return self.tr("Exports the input layer to a shapefile format in a specified folder with an optional prefix, and copies a QML style file. Allows overwriting if specified.")

    def initAlgorithm(self, config=None):
        # Paramètre d'entrée pour la couche vecteur
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        # Paramètre pour le dossier de destination
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.FOLDER,
                self.tr('Destination folder')  # Interface permettant de sélectionner un dossier
            )
        )

        # Préfixe en tant qu'expression
        self.addParameter(
            QgsProcessingParameterExpression(
                self.PREFIX,
                self.tr('Shapefile prefix expression (Format: AAAAMMDD_)')
            )
        )

        # Suffixe en tant que chaîne de caractères
        self.addParameter(
            QgsProcessingParameterString(
                self.SUFFIX,
                self.tr('Shapefile suffix (without extension)'),
                defaultValue='output'  # Valeur par défaut pour le suffixe
            )
        )

        # Case à cocher pour activer ou non le préfixe
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.USE_PREFIX,
                self.tr('Use prefix in the filename?'),
                defaultValue=True  # Valeur par défaut pour activer le préfixe
            )
        )

        # Case à cocher pour l'écrasement
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OVERWRITE,
                self.tr('Overwrite file if it exists?'),
                defaultValue=False  # Par défaut, ne pas écraser
            )
        )

        # Paramètre pour le fichier QML source
        self.addParameter(
            QgsProcessingParameterFile(
                self.QML_SOURCE,
                self.tr('Source QML file'),
                extension='qml'  # Limite les fichiers aux .qml
            )
        )

        # Paramètre de sortie pour la couche finale
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Obtenir la source de la couche d'entrée
        source = self.parameterAsSource(parameters, self.INPUT, context)
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        # Obtenir le chemin du dossier choisi par l'utilisateur
        folder_path = self.parameterAsString(parameters, self.FOLDER, context)
        if not folder_path:
            raise QgsProcessingException("Output folder path is required.")

        # Vérifiez si l'utilisateur souhaite utiliser le préfixe
        use_prefix = self.parameterAsBoolean(parameters, self.USE_PREFIX, context)

        # Si l'utilisateur a choisi d'utiliser le préfixe, évaluer l'expression
        prefix = ''
        if use_prefix:
            prefix_expr = self.parameterAsExpression(parameters, self.PREFIX, context)
            expression = QgsExpression(prefix_expr)

            # Vérifiez que l'expression est valide
            if expression.hasParserError():
                raise QgsProcessingException(f"Invalid prefix expression: {expression.parserErrorString()}")

            # Évaluez l'expression pour obtenir le préfixe
            prefix = expression.evaluate()
            if expression.hasEvalError():
                raise QgsProcessingException(f"Error evaluating prefix expression: {expression.evalErrorString()}")

            # Vérifiez que le résultat de l'expression est une chaîne non vide
            if not prefix or not isinstance(prefix, str):
                raise QgsProcessingException("Prefix expression must evaluate to a non-empty string.")

        # Obtenir le suffixe spécifié par l'utilisateur
        suffix = self.parameterAsString(parameters, self.SUFFIX, context)
        
        # Construire le chemin complet du fichier shapefile
        output_path = os.path.join(folder_path, f"{prefix}{'_' if use_prefix else ''}{suffix}.shp")

        # Vérifier si le fichier existe déjà
        overwrite = self.parameterAsBoolean(parameters, self.OVERWRITE, context)
        if os.path.exists(output_path) and not overwrite:
            feedback.reportError(f"Le fichier '{output_path}' existe déjà et l'option d'écrasement n'est pas activée. Opération annulée.")
            return {}  # Ne pas exécuter le script si le fichier existe et écrasement désactivé

        # Si le fichier existe et que l'écrasement est autorisé, le supprimer avant de créer un nouveau fichier
        if os.path.exists(output_path) and overwrite:
            os.remove(output_path)
            feedback.pushInfo(f"Existing file '{output_path}' has been removed.")

        # Déterminer si la couche source est en 3D (contient des coordonnées Z)
        geometry_type = source.wkbType()
        if QgsWkbTypes.hasZ(geometry_type):
            output_geometry_type = QgsWkbTypes.Point25D  # Pour géométries de points avec Z
        else:
            output_geometry_type = QgsWkbTypes.Point  # Reste en 2D si pas de Z

        # Créer le fichier shapefile en spécifiant le type de géométrie (Point ou Point25D)
        writer = QgsVectorFileWriter(output_path, 'UTF-8', source.fields(), output_geometry_type, source.sourceCrs(), 'ESRI Shapefile')

        if writer.hasError() != QgsVectorFileWriter.NoError:
            raise QgsProcessingException("Error when creating shapefile: {}".format(writer.errorMessage()))

        # Écrire les entités (features) dans le shapefile
        for feature in source.getFeatures():
            writer.addFeature(feature)

        del writer  # Fermer le writer

        # Copier le fichier QML source dans le dossier de destination et le renommer
        qml_source_path = self.parameterAsString(parameters, self.QML_SOURCE, context)
        if qml_source_path and os.path.isfile(qml_source_path):
            # Renommer le fichier QML avec le même nom que le shapefile
            qml_destination_path = os.path.join(folder_path, f"{prefix}{'_' if use_prefix else ''}{suffix}.qml")
            shutil.copy(qml_source_path, qml_destination_path)  # Copier le fichier QML
            feedback.pushInfo(f"QML file copied to: {qml_destination_path}")
        else:
            feedback.pushInfo("No valid QML file provided or the file does not exist.")

        # Informer l'utilisateur du fichier de sortie
        feedback.pushInfo("Shapefile exported to: {}".format(output_path))

        # Retourner le chemin de sortie comme paramètre de sortie
        return {self.OUTPUT: output_path}
