LINZ Data Service Esri ArcGIS Support Tools
===========================================

To best support Esri users, LINZ provides a set of tools to merge layers and tables into one database, as well as to create relationships within this merged database. 

These tools support the following layers and tables:

* [NZ Primary Parcels](http://data.linz.govt.nz/layer/772-nz-primary-parcels/)
* [NZ Primary Land Parcels](http://data.linz.govt.nz/layer/823-nz-primary-land-parcels/)
* [NZ Primary Road Parcels](http://data.linz.govt.nz/layer/796-nz-primary-road-parcels/)
* [NZ Primary Hydro Parcels](http://data.linz.govt.nz/layer/771-nz-primary-hydro-parcels/)
* [NZ Non-Primary Parcels](http://data.linz.govt.nz/layer/782-nz-non-primary-parcels/)
* [NZ Strata Parcels](http://data.linz.govt.nz/layer/780-nz-strata-parcels/)
* [NZ Non-Primary Linear Parcels](http://data.linz.govt.nz/layer/783-nz-non-primary-linear-parcels/)
* [NZ Parcels](http://data.linz.govt.nz/layer/1571-nz-parcels)
* [NZ Linear Parcels](http://data.linz.govt.nz/layer/1570-nz-linear-parcels)

* [NZ Property Titles List](http://data.linz.govt.nz/table/1567-nz-property-titles-list)
* [NZ Property Title Estates List](http://data.linz.govt.nz/table/1566-nz-property-title-estates-list)
* [NZ Property Titles Owners List](http://data.linz.govt.nz/table/1564-nz-property-titles-owners-list)
* [NZ Title Parcel Association List](http://data.linz.govt.nz/table/1569-nz-title-parcel-association-list)
* [NZ Parcel Statutory Actions List](http://data.linz.govt.nz/table/1565-nz-parcel-statutory-actions-list)
* [NZ Survey Affected Parcels List](http://data.linz.govt.nz/table/1568-nz-survey-affected-parcels-list)

# lds_merge_property_data.pyt

This python code is both a command line script and a ArcGIS 10.1 Python ArcTool.

## Command line usage (ArcGIS 10.0 or higher)

The command line script can be can be used in ArcGIS 10.X. It has the following options:

```
Usage: lds_merge_property_data.pyt [options] source_lds_dir destination_file_gdb


Options:
  -h, --help           show this help message and exit
  -o, --overwrite      overwrite destination FileGDB
  -r, --relationships  creates relationships between features class and tables
```

If you are using ArcGIS 10.1 an example windows command line to merge a directory of single FileGDB and build relationships would be:

```
C:\Python27\ArcGIS10.1\python.exe lds_merge_property_data.pyt -r C:\Temp\working\data C:\Temp\working\lds_property.gdb
```

This will create the lds_property.gdb database and create relationships between all relevant features classes and tables that have been imported.

## ArcToolbox Usage (ArcGIS 10.1 or higher)

The ArcGIS Python ArcTool can only be used in ArcGIS 10.1 or higher and provides two tools which can be run within ArcMap or ArcCatalog:

### LDS merge property datasets tool

Takes a directory of unzipped LDS FileGDB layers or tables (one FileGDB for each). This tool will then import each layer and table it finds and imports them into a single destination FileGDB. 

### LDS relationships builder for property datasets tool

Build relationships between Parcels, Survey Plans Layers and associated [tables](http://data.linz.govt.nz/#/tables/category/property-ownership-boundaries). Note: building relationships requires a higher licence than ArcView

# Help

For more information please see http://www.linz.govt.nz/about-linz/linz-data-service/help/advanced-user-guides/building-relationships-for-esri-file-geodatabase
