#! /bin/sh

rm zip/UNZIP_ME_FOR_TFS_HISCORES_UPDATER.zip
zip -r zip/UNZIP_ME_FOR_TFS_HISCORES_UPDATER.zip . -x "./.git*" "./log/*.*" "./*.csv" "./*.sh" "./*.pyc" "./zip/*"
cp zip/UNZIP_ME_FOR_TFS_HISCORES_UPDATER.zip ~/share
echo "Now upload this .zip to the GDrive: ~/share/UNZIP_ME_FOR_TFS_HISCORES_UPDATER.zip."

