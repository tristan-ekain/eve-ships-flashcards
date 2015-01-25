# EVE Ship Flashcards

EVE Online has more than 300 different ship types. Learning the names and basic information about most of them is thus no small achievement. To make this easier, learning tools like flashcards can be used. Flashcards have helped many people in school and university, for things like vocabulary or math equations, and should prove equally useful for learning EVE's ships.

There are many flashcard applications for various operating systems and devices. [Anki][anki] is one such application, and is the target of this project.

This project contains scripts for the various steps involved in creating a set of flashcards:
* Extracting ship information from CCP's [static data export][ccp-sde], and writing it in a file.
* Transform this data into a format that can be imported into Anki.

The following sections explain how to use the scripts to build a ship card deck yourself. If you just want to use a pre-built card deck, check the section "Import a Card Deck" on how to import it.

In the following sections it is expected that you already have [Anki][anki] installed and that you know how to use it.


## Requisites

### Install Software

Install the following software:

* Python 3.x (tested with Python 3.4.2; later versions will most probably work; earlier versions might now)
* [Anki][anki]: you should already have this installed ;-)

### Download Files

* This project. Check out with Git, or download as ZIP file and extract somewhere. The location of the sources on your hard drive will be referred to as **workspace** from now on.
* The SDE dump in sqlite format. CCP provides it in MS SQL format only, but other players convert them into various format. An sqlite conversion can be found e.g. here: [https://www.fuzzwork.co.uk/dump/](https://www.fuzzwork.co.uk/dump/)
* The images: from [CCP's site][ccp-sde] download the **Renders** ZIP file. This file contains high-resolution images for all of EVE's items.


## Setup local workspace

* Extract the SDE dump, and copy the sqlite database into the *data* subdirectory of your workspace. The file must be called **eve.sqlite**.
* Extract the *Renders* ZIP file. Copy all the images into the *data/Renders* subdirectory of your workspace.  
These images are quite big (512x512 pixels). You can resize them down to 256x256 pixels to make the resulting Anki file smaller.

After these steps, your workspace should look like this:
<pre>
/
+ data
  + eve.sqlite
  + Renders
    + ...
    + 582.png
    + 583.png
    + ...
+ ...
</pre>


## Extract Ships from SDE

In your workspace directory, run the script **extract_ships_from_sde.py**. The script takes no parameters, and does not print anything on the console (except when errors occur).

The script reads the information from the sqlite database, and writes it into the file **ships.csv** in the directory **output** (which is automatically created).

The data in this file is required for the next step. However, you can edit it first if you want, or put it into Google Spreadsheets or Excel (where you can export it later for the next step).


## Create Files for Anki

This step requires the data extracted by the previous step. You can either take the file **ships.csv** directly as it was created, or you can edit it first. You can add or remove lines, add columns or change the order of columns, as long as the following is still true:

* The first line in the file contains the row names.
* All column of the original **ships.csv** are still present (with their original names).

If not already there, put the file **ships.csv** into the **output** directory. Then run the script **create_anki_data.py** from the workspace directory. It takes no parameters, and does not print anything on the console (except when errors occur).

The script does two things:

* It creates a CSV file that Anki can import, and saves it under **output/anki/anki.csv**.
* It copies all ship images from **data/Render** to **output/anki/collection.media**. The images of other item types are not copied.


## Import Data into Anki

Open Anki and open the profile in which you want to create the cards, or create a new one.

Next import the file **anki/Template.apkg** from your workspace, either by

* selecting *File -> Import...*, then opening the template file, or
* just double-clicking the file.

This will add two things to your Anki profile:

* The definition for the note type we're using for the ship flash cards. It is called "Ship", and you can find it under **Tools -> Manage Note Types...**. Go there, and delete all other note types.
* One dummy card which only exists to hold the "Ship" note type definition. You should go and delete it now. To do that, click **Browse**, then in the new window select "Whole Collection" in the list on the left side. This will show you all cards. Pick the one called "\__Dummy__", and delete it.

Now you have to copy the images to the folder where Anki expects them during the import. Where that folder is depends on your operating system:

* On Windows, its the **Anki** subfolder in your **Documents** folder.
* On other operating systems, it should be either **~/Anki** or **~/Documents/Anki**.

In this folder, go to the subfolder for your profile. There you should find a folder called **collection.media**; if it doesn't exist, create it. Into this folder copy all the image files from **output/anki/collection.media**.

The next step is importing the ships into Anki. Click **Import File** and select **output/anki/anki.csv**. This will open the import dialog. In this dialog, apply the following settings:

* Set "Type" to "Ship".
* Set "Deck" to the deck into which you want to import the cards. The default setting is fine.
* In the dropdown box, select "Update existing notes when first field matches". When you don't have any cards yet, this doesn't matter, but if you already have some, this will cause Anki to update your cards with the new data from the CSV file.
* Select "Allow HTML in fields". Otherwise the images won't get imported.
* Under "Field Mapping", assign the columns from the CSV file to the corresponding columns in Anki. Make sure that every field in Anki gets a column mapped to. Also, the "Category Tag" column from the CSV needs to be mapped the "Tags" field.

After all settings are correct, press **Import**. This will import the card and open a new dialog, in which you can check what happened (new cards added, existing cards updated...).

Now all cards are imported, and you can check the result. Click **Browse**, then select "Whole Collection" on the left. You should now see a list of cards; one card per ship. Click a card, and check its fields have been correctly filled. If yes, you're done; if not, delete all cards and try again.

If you want to update your cards at a later time, just run these steps again.

The following steps are optional, but advisable: export all cards, and import them into the separate profile with which you learn.

* Click **File -> Export...**
* As "Export format" select "Anki Deck Package".
* In the "Include" dropdown box select the deck that contains the ship cards.
* Deselect "Include scheduling Information"
* Select "Include Media"
* Click **Export...** and select where to save the exported data.

You now have a card deck. What to do with it is explained in the next section.

## Import a Card Deck

If you have built a card deck yourself (following the previous sections"), or if you have downloaded a pre-build one, then you can import that into the Anki profile that you are using for learning. So open Anki, and go to that profile (or create it if you don't have one already).

Click **Import File**, then select the card deck (file name ends with ".apkg"). This does several things:

* Cards that don't already exist in your profile are created with the data from the card deck file.
* Cards that already exist in your profile are updated with the data from the card deck file.

That means that if you later get an updated card deck file, just follow these steps again. The learning progress data is not modified by the import, so updating is safe to do.


## Legal Notes

This project is released under the Apache 2.0 license (see [LICENSE](LICENSE)).  
All EVE Online related materials are property of CCP hf.

[anki]: http://ankisrs.net/
[ccp-sde]: https://developers.eveonline.com/resource/static-data-export "CCP's Static Data Export"
[ccp-iec]: https://developers.eveonline.com/resource/image-export-collection "CCP's Image Export Collection"
