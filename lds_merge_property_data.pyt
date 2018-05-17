################################################################################
#
# lds_merge_property_data.pyt
#
# Copyright 2013 Crown copyright (c)
# Land Information New Zealand and the New Zealand Government.
# All rights reserved
#
# This program is released under the terms of the new BSD license. See the 
# LICENSE file for more information.
#
################################################################################
# ArcGIS 10.1 Python ArcTool tool to merge property and ownership FileGDBs
# exported from LDS and to create relationships between feature classes/tables.
################################################################################

import sys
import os.path
import arcpy
import shutil
import collections
from optparse import OptionParser

__author__ = 'Jeremy Palmer'
__date__ = 'January 2013'
__copyright__ = '2013 Crown copyright (c)'
__version__ = '1.0.3'

Options = collections.namedtuple('Options', 'source_dir, output_file_gdb, overwrite_file_gdb, create_relationships')

layers = {
    'primary_parcels'            : 'NZ Primary Parcels',
    'primary_land_parcels'       : 'NZ Primary Land Parcels',
    'primary_road_parcels'       : 'NZ Primary Road Parcels',
    'primary_hydro_parcels'      : 'NZ Primary Hydro Parcels',
    'non_primary_parcels'        : 'NZ Non-Primary Parcels',
    'strata_parcels'             : 'NZ Strata Parcels',
    'non_primary_linear_parcels' : 'NZ Non-Primary Linear Parcels',
    'parcels'                    : 'NZ Parcels',
    'linear_parcels'             : 'NZ Linear Parcels',
    'parcel_statutory_actions'   : 'NZ Parcel Statutory Actions List',
    'title_estates'              : 'NZ Property Title Estates List',
    'titles'                     : 'NZ Property Titles List',
    'title_owners'               : 'NZ Property Titles Owners List',
    'survey_affected_parcels'    : 'NZ Survey Affected Parcels List',
    'title_parcel_association'   : 'NZ Title Parcel Association List',
    'survey_plans'               : 'NZ Survey Plans',
    'title_memorials'            : 'NZ Title Memorials List Including Mortgages Leases Easements',
    'title_memorials_additional_text' : 'NZ Title Memorials Additional Text List',
}

parcel_layers = [
    'primary_parcels',
    'primary_land_parcels',
    'primary_road_parcels',
    'primary_hydro_parcels',
    'non_primary_parcels',
    'strata_parcels',
    'non_primary_linear_parcels',
    'parcels',
    'linear_parcels',
]

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [MergePropertyDatasets, CreateRelationships]


class MergePropertyDatasets(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "LDS merge property datasets"
        self.description = "Merges Property and ownership FileGDB 10.0 " + \
            "databases that are  downloaded from LDS."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        
        param0 = arcpy.Parameter(
            displayName="LDS unzipped datasets directory containing FileGDBs",
            name = "source_dir",
            datatype = "Folder",
            parameterType = "Required",
            direction = "Input"
        )
        
        param1 = arcpy.Parameter(
            displayName = "Destination FileGDB",
            name = "output_file_gdb",
            datatype = "Workspace",
            parameterType = "Required",
            direction = "Input"
        )
    
        return [param0, param1]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        options = Options(
            source_dir = parameters[0].valueAsText,
            output_file_gdb = parameters[1].valueAsText,
            overwrite_file_gdb = False,
            create_relationships = False
        )
        run_merge(options)
        return

class CreateRelationships(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "LDS relationships builder for property datasets"
        self.description = "Creates relationships between LDS Property and Ownership layers " + \
            " and tables. Requires an existing FileGDB which contain all layers and tables"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        
        param0 = arcpy.Parameter(
            displayName = "LDS Property and Ownership FileGDB",
            name = "source_file_gdb",
            datatype = "Workspace",
            parameterType = "Required",
            direction = "Input"
        )
        param0.value = None
        return [param0]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        if arcpy.ProductInfo() == "ArcView":
            return False
        else:
            return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        options = Options(
            source_dir = None,
            output_file_gdb = parameters[0].valueAsText,
            create_relationships = True,
            overwrite_file_gdb = False,
        )
        create_relationships(options)
        return

def dir_slug(layer_title):
    return layer_title.replace(' ', '-').lower()[0:75]


def layer_path(source_file_gdb_dir, layer_title):
    dir_slug_name = dir_slug(layer_title)
    #Handle inconsistency in the way LDS names memorials layer
    if(layer_title=="NZ Title Memorials List Including Mortgages Leases Easements"):
        filegdb_item = filegdb_entity("NZ_Title_Memorials_List__including_Mortgages__Leases__Easements_")
    else:
        filegdb_item = filegdb_entity(layer_title)
 
    dataset_dir = dir_slug_name
    filegdb_dir = dir_slug_name + '.gdb'
    path = os.path.join(source_file_gdb_dir, dir_slug_name, filegdb_dir, filegdb_item)
    return path

def filegdb_entity(name):
    return name.replace(' ', '_').replace('-', '_')[0:160]

def add_parcel_relationships(output_file_gdb, parcel_layer):
    parcel_name = filegdb_entity(layers[parcel_layer])
    parcel_path = output_path = os.path.join(output_file_gdb, parcel_name)
    if not arcpy.Exists(parcel_path):
        return

    survey_plans_name = filegdb_entity(layers['survey_plans'])
    survey_plans_path = output_path = os.path.join(output_file_gdb, survey_plans_name)
    survey_affected_parcels_name = filegdb_entity(layers['survey_affected_parcels'])
    survey_affected_parcels_path = output_path = os.path.join(output_file_gdb, survey_affected_parcels_name)
    relationship = os.path.join(output_file_gdb, "surveys_affected_" + parcel_layer)
    if arcpy.Exists(survey_plans_path) and arcpy.Exists(survey_affected_parcels_path) and not arcpy.Exists(relationship):
        arcpy.AddMessage("Creating " + parcel_layer + " to surveys relationship")
        arcpy.TableToRelationshipClass_management(
            parcel_path,
            survey_plans_path,
            relationship,
            "SIMPLE",
            survey_plans_name,
            parcel_name,
            "NONE",
            "MANY_TO_MANY",
            survey_affected_parcels_path,
            "par_id;sur_wrk_id",
            "id",
            "par_id",
            "id",
            "sur_wrk_id"
        )
        
    parcel_statutory_actions_name = filegdb_entity(layers['parcel_statutory_actions'])
    parcel_statutory_actions_path = output_path = os.path.join(output_file_gdb, parcel_statutory_actions_name)
    relationship = os.path.join(output_file_gdb,  parcel_layer + "_has_stat_actions")
    if arcpy.Exists(parcel_statutory_actions_path)  and not arcpy.Exists(relationship):
        arcpy.AddMessage("Creating " + parcel_layer + " to statutory action relationship")
        arcpy.CreateRelationshipClass_management(
            parcel_path,
            parcel_statutory_actions_path,
            relationship,
            "SIMPLE",
            parcel_statutory_actions_name,
            parcel_name,
            "NONE",
            "ONE_TO_MANY",
            "NONE",
            "id",
            "par_id",
            "",
            ""
        )
    
    titles_name = filegdb_entity(layers['titles'])
    titles_path = output_path = os.path.join(output_file_gdb, titles_name)
    title_parcel_association_name = filegdb_entity(layers['title_parcel_association'])
    title_parcel_association_path = output_path = os.path.join(output_file_gdb, title_parcel_association_name)
    relationship = os.path.join(output_file_gdb, parcel_layer + "_has_titles")
    if arcpy.Exists(titles_path) and arcpy.Exists(title_parcel_association_path) and not arcpy.Exists(relationship):
        arcpy.AddMessage("Creating " + parcel_layer + " to titles relationship")
        arcpy.TableToRelationshipClass_management(
            parcel_path,
            titles_path,
            relationship,
            "SIMPLE",
            titles_name,
            parcel_name,
            "NONE",
            "MANY_TO_MANY",
            title_parcel_association_path,
            "par_id;title_no",
            "id",
            "par_id",
            "title_no",
            "title_no"
        )
    return

def add_title_relationships(output_file_gdb):
    titles_name = filegdb_entity(layers['titles'])
    titles_path = output_path = os.path.join(output_file_gdb, titles_name)
    title_estates_name = filegdb_entity(layers['title_estates'])
    title_estates_path = output_path = os.path.join(output_file_gdb, title_estates_name)
    title_owners_name = filegdb_entity(layers['title_owners'])
    title_owners_path = output_path = os.path.join(output_file_gdb, title_owners_name)
    title_memorials_name = filegdb_entity("NZ_Title_Memorials_List__including_Mortgages__Leases__Easements_")
    title_memorials_path = output_path = os.path.join(output_file_gdb, title_memorials_name)
    title_memorials_additional_text_name = filegdb_entity(layers['title_memorials_additional_text'])
    title_memorials_additional_text_path = output_path = os.path.join(output_file_gdb, title_memorials_additional_text_name)
    relationship = os.path.join(output_file_gdb, "titles_has_estates")
    if arcpy.Exists(titles_path) and arcpy.Exists(title_estates_path) and not arcpy.Exists(relationship):
        arcpy.AddMessage("Creating title to titles estates relationship")
        arcpy.CreateRelationshipClass_management(
            titles_path,
            title_estates_path,
            relationship,
            "SIMPLE",
            title_estates_name,
            titles_name,
            "NONE",
            "ONE_TO_MANY",
            "NONE",
            "title_no",
            "title_no",
            "",
            ""
        )
        
    relationship = os.path.join(output_file_gdb, "title_estates_has_owners")
    if arcpy.Exists(title_estates_path) and arcpy.Exists(title_owners_path)  and not arcpy.Exists(relationship):
        arcpy.AddMessage("Creating title estates to titles owners relationship")
        arcpy.CreateRelationshipClass_management(
            title_estates_path,
            title_owners_path,
            relationship,
            "SIMPLE",
            title_owners_name,
            title_estates_name,
            "NONE",
            "ONE_TO_MANY",
            "NONE",
            "id",
            "tte_id",
            "",
            ""
        )
    
    relationship = os.path.join(output_file_gdb, "title_has_memorials")
    if arcpy.Exists(titles_path) and arcpy.Exists(title_memorials_path)  and not arcpy.Exists(relationship):
        arcpy.AddMessage("Creating title to title memorials relationship")
        arcpy.CreateRelationshipClass_management(
            titles_path,
            title_memorials_path,
            relationship,
            "SIMPLE",
            title_memorials_name,
            titles_name,
            "NONE",
            "ONE_TO_MANY",
            "NONE",
            "title_no",
            "title_no",
            "",
            ""
        )

    relationship = os.path.join(output_file_gdb, "title_memorials_has_additional_text")
    if arcpy.Exists(title_memorials_path) and arcpy.Exists(title_memorials_additional_text_path) and not arcpy.Exists(relationship):
        arcpy.AddMessage("Creating title memorials to additional text relationship")
        arcpy.CreateRelationshipClass_management(
            title_memorials_path,
            title_memorials_additional_text_path,
            relationship,
            "SIMPLE",
            title_memorials_additional_text_name,
            title_memorials_name,
            "NONE",
            "ONE_TO_MANY",
            "NONE",
            "id",
            "ttm_id",
            "",
            ""
        )
    return


def run_merge(options):
    file_path, extension = os.path.splitext(options.output_file_gdb)
    if extension != '.gdb':
        print "Path: " + output_file_gdb + " is not a valid FileGDB directory"
        exit(1)
    
    if not arcpy.Exists(options.output_file_gdb) or (options.overwrite_file_gdb and arcpy.Exists(options.output_file_gdb)):
        name = os.path.split(options.output_file_gdb)[-1]
        path = os.path.split(options.output_file_gdb)[0]
        if arcpy.Exists(options.output_file_gdb):
            shutil.rmtree(options.output_file_gdb)
        arcpy.AddMessage("Creating FileGDB " + options.output_file_gdb)
        arcpy.CreateFileGDB_management(path, name)
    
    for layer in layers:
        source_path = layer_path(options.source_dir, layers[layer])
        name = os.path.split(source_path)[-1]            

        if arcpy.Exists(source_path):
            output_path = os.path.join(options.output_file_gdb, name)
            if arcpy.Exists(output_path):
                arcpy.AddMessage(name + " content already exists in output FileGDB and will not be merged")
                continue
            arcpy.AddMessage("Importing " + name)
            arcpy.Copy_management(source_path, output_path)
        else:
            arcpy.AddMessage("Skipping " + name + " as the database was not found")

def create_relationships(options):
    if options.create_relationships:
        if arcpy.ProductInfo() == "ArcView":
            arcpy.AddWarning("Building relationships requires a higher licence than ArcView")
            return False
        for parcel_layer in parcel_layers:
            add_parcel_relationships(options.output_file_gdb, parcel_layer)
        add_title_relationships(options.output_file_gdb)
    return True

def main():
    usage = "usage: %prog [options] source_lds_dir destination_file_gdb"
    parser = OptionParser(usage=usage)
    parser.add_option(
        "-o",
        "--overwrite",
        action="store_true",
        dest="overwrite",
        default=False,
        help="overwrite destination FileGDB"
    )
    parser.add_option(
        "-r",
        "--relationships",
        action="store_true",
        dest="create_relationships",
        default=False,
        help="creates relationships between features class and tables"
    )
    (cmd_opt, args) = parser.parse_args()
    
    if len(args) != 2:
        parser.error("Please specific destination FileGDB path")
    
    source_dir      = args[0]
    output_file_gdb = args[1]
    
    options = Options(
        source_dir = args[0],
        output_file_gdb = args[1],
        overwrite_file_gdb = cmd_opt.overwrite,
        create_relationships = cmd_opt.create_relationships
    )
    run_merge(options)
    create_relationships(options)

if __name__ == "__main__":
    main()
