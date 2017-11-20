# Keep It!

Archive your Maya files. Simply.

To save and keep a version:

    import keepit
    keepit.keep()

* Add a message and archive processes in the archive folder will be run.
* Add no message (just hit enter) and maya will save as is. No archive will happen.

This command above can be used stand alone or to replace ctrl-s to save the scene. No message, no archive.

To view previous version and recover:

    import keepit
    keepit.look()

* Right click a thumbnail and load scene, to temporarally load the file. Then saveas, to save over your original file if you wish.
* Right click a thumb and revert scene. This will replace the file with the old version. Be careful with this.
